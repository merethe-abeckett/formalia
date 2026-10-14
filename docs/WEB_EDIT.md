# 网页编辑：工作原理与部署

谁都可以编辑，不需要注册，也不需要 GitHub 账号。本页说明它怎么工作，以及维护者要在 Cloudflare 和 GitHub 上做的一次性设置。

## 一条编辑走过的路

1. 访客在网站上点编辑按钮，填表单，通过 Cloudflare Turnstile 人机验证，提交。
2. 表单发给 `formalnaturalist.co.nz/api/submit`，这个地址由 Cloudflare Worker（`worker/src/index.js`）处理：
   - 校验人机验证、检查封禁名单、按匿名编号限流（默认每小时 6 次）；
   - 用 IP 算出匿名编号，比如 `匿名者 7f3a1c2e`，IPv6 按 /64 归并；
   - 把完整 IP、浏览器标识、国家写进私有 KV 日志 `log:<议题号>`，90 天后自动删除；
   - 用一个只能开议题的令牌在仓库里开一个议题，正文里是编辑数据。
3. 议题触发 `.github/workflows/edit.yml`：
   - **check 任务**：没有任何密钥、只读。运行 `scripts/apply_edit.py` 把编辑写进工作区，跑元数据校验；如果是新增表述，再编译 Lean、跑检查器和 lean4checker。
   - **commit 任务**：只在检查通过时运行，持有写权限但不编译 Lean。在最新的 main 上重新应用同一条编辑，比对结果，提交并推送，回复议题后关闭，再触发 CI、网站和导读。
   - **report 任务**：检查不通过时，把原因回复到议题并关闭。
4. 访客被带到 `/edit/status.html?issue=N`，页面通过 Worker 读取议题状态，所以在打不开 GitHub 的地方也能看到结果。

每条编辑都留下一个议题和一次提交。表述页和猜想页底部的“编辑历史”从 git 记录生成。回退一条编辑，就是对那次提交做 `git revert`。

## 能编辑什么

| 类型 | 能改的内容 | 不能改的内容 |
| --- | --- | --- |
| 声明证明 | 追加一条声明：声称方、日期、证明链接、备注 | 已有声明（删除走提删流程） |
| 编辑表述信息 | 来源链接、来源备注、非正式复述、外部链接 | Lean 代码、编号、提交者、提交日期 |
| 编辑猜想信息 | 中文名、自然语言表述、参考资料 | 英文名、目录名 |
| 新增表述 | 在已有猜想下或新猜想下新增一条表述 | — |

Lean 代码不能就地修改：编号永远指向同一段代码，否则一条“证明了 #N”的声明就会失去意义。要改代码，新增一条表述。

多人同时编辑同一字段时，后提交的人会收到“编辑冲突”，刷新后在最新内容上重做，和维基百科一样。

## 安全设计

Lean 在编译期可以执行任意代码，所以匿名提交的 Lean 代码有两道防线：

1. **受限子集**（`scripts/lean_policy.py`）。表述文件只能是固定模板：`module`、若干 `public import Mathlib…`、一个辅助定义命名空间、一个 `def S<编号> : Prop :=`。用户片段里禁止 `#` 命令、属性 `@[…]`、`elab`、`macro`、`syntax`、`run_cmd`、`initialize`、`set_option`、`unsafe`、`IO`、`Lean` 命名空间、字符串字面量、`sorry`、`native_decide` 等。CI 对仓库里所有表述文件强制执行这一规则，不只是网页提交。
2. **权限隔离**。所有编译 Lean 的任务都没有密钥、令牌只读；所有持有密钥或写权限的任务都不编译 Lean。Guides、Patrol、Pages 三个工作流也按这个原则拆成两个任务。

用户填写的文字从不插进工作流脚本，只经环境变量和文件传递。

## 一次性设置

以下都在网页上点，不需要命令行。顺序不能乱：后面的步骤要用前面得到的值。

### 1. GitHub：开议题用的令牌

1. 打开 https://github.com/settings/personal-access-tokens/new （Fine-grained token）。
2. Token name 填 `formalia-edit-gateway`，Expiration 选一年，并在日历里记一个续期提醒。
3. Repository access 选 **Only select repositories**，只勾 `formalia`。
4. Permissions → Repository permissions → **Issues** 选 **Read and write**。其他全部保持 No access。
5. 生成，复制 `github_pat_` 开头的令牌。这个值只出现一次。

这个令牌只能开议题和读议题，不能推代码，泄露了也改不了仓库内容。

### 2. Cloudflare：Turnstile 人机验证

1. Cloudflare 后台左侧 **Turnstile** → **Add widget**。
2. Widget name 填 `formalia`，Hostname 添加 `formalnaturalist.co.nz` 和 `www.formalnaturalist.co.nz`。
3. Widget Mode 选 **Managed**，创建。
4. 记下 **Site Key**（公开的）和 **Secret Key**（保密的）。

### 3. Cloudflare：KV 存储

1. 左侧 **Storage & Databases** → **KV** → **Create a namespace**，名字填 `formalia`。

### 4. Cloudflare：创建 Worker

1. 左侧 **Workers & Pages** → **Create** → **Create Worker**，名字填 `formalia-edit`，先部署默认的 Hello World。
2. 点 **Edit code**，删掉默认代码，把仓库里 `worker/src/index.js` 的全部内容粘贴进去，**Deploy**。
3. 回到 Worker 页面 → **Settings** → **Bindings** → **Add binding** → **KV namespace**，Variable name 填 `FORMALIA_KV`，选第 3 步建的 `formalia`。
4. **Settings** → **Variables and Secrets**，逐个添加：

   | 类型 | 名字 | 值 |
   | --- | --- | --- |
   | Text | `REPO` | `merethe-abeckett/formalia` |
   | Text | `ALLOWED_ORIGINS` | `https://formalnaturalist.co.nz,https://www.formalnaturalist.co.nz` |
   | Text | `TURNSTILE_SITEKEY` | 第 2 步的 Site Key |
   | Text | `RATE_LIMIT_PER_HOUR` | `6` |
   | Secret | `GITHUB_TOKEN` | 第 1 步的令牌 |
   | Secret | `TURNSTILE_SECRET` | 第 2 步的 Secret Key |
   | Secret | `ANON_SECRET` | 一串随机字符，至少 32 位。可以在 PowerShell 里运行 `[guid]::NewGuid().ToString() + [guid]::NewGuid().ToString()` 生成 |

   `ANON_SECRET` 设定后不要随便改：改了以后所有人的匿名编号都会变。

5. **Settings** → **Domains & Routes** → **Add** → **Route**：Zone 选 `formalnaturalist.co.nz`，Route 填 `formalnaturalist.co.nz/api/*`。再加一条 `www.formalnaturalist.co.nz/api/*`。

### 5. 灌水区（聊天室）

聊天室跑在同一个 Worker 里，用 Cloudflare 免费版的 Durable Objects（SQLite 存储）。

1. Worker → **Settings** → **Bindings** → **Add binding** → **Durable Object**，Variable name 填 `CHAT`，Class 选 `ChatRoom`。
2. **Variables and Secrets** 里加一个 Secret：`CHAT_ADMIN_TOKEN`，值是一串至少 16 位的随机字符。
3. 管理员模式：浏览器打开 `https://formalnaturalist.co.nz/chat/#admin=你的口令` 一次，口令存在这台电脑上，地址栏里会自动抹掉。之后每条消息旁边会出现“删”“封”两个按钮。“封”会暂停该 IP 7 天并删除他的全部消息。

用后台粘贴代码的方式部署时，如果添加 Durable Object 绑定的界面要求迁移（migration），以仓库里 `worker/wrangler.toml` 的 `[[migrations]]` 为准。

### 6. 验证

浏览器打开 https://formalnaturalist.co.nz/api/config ，应该看到 `{"sitekey":"0x…","repo":"merethe-abeckett/formalia"}`。然后在网站上随便找一条表述，点“声明证明了这条表述”，提交一条测试声明，几分钟内状态页应显示“已写入”。测试完可以用一条编辑把它删掉，或者在 GitHub 上回退那次提交。

## 日常管理

- **查某条编辑的 IP**：Cloudflare → KV → `formalia` → 搜 `log:<议题号>`。
- **封禁**：在 KV 里新增一个键，值随便写原因：
  - 单个地址：`ban:203.0.113.7`
  - IPv4 网段：`ban:203.0.113.0/24`
  - IPv6：`ban:2001:0db8:0001:0002::/64` 或 `/48`（按 Worker 展开后的格式，四位一组补零）
- **回退恶意编辑**：在 GitHub 上找到那次提交，`git revert`；或者在网站上再提交一条编辑改回去。
- **调整限流**：改 Worker 变量 `RATE_LIMIT_PER_HOUR`。
- **令牌到期**：重新生成 GitHub 令牌，更新 Worker 的 `GITHUB_TOKEN`。

## 本地测试

```
python3 tests/test_lean_policy.py      # Lean 规范对抗测试
bash tests/test_apply_edit.sh          # 编辑应用测试
node worker/test.mjs                   # Worker 测试（模拟 KV、Turnstile、GitHub）
```

CI 每次推送都会跑这三项。
