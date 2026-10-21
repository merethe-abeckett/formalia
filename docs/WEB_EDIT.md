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
| 声明证明或证否 | 追加一条声明：方向（证明/证否）、声称方（自称）、自填日期、证明来源、备注。机器验证通过才写入，并分配声明编号 `P<日期>-<序号>`、记录登记时间、存档证明代码 | 已有声明（删除走提删流程） |
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

服务器代码由 GitHub 自动部署到 Cloudflare。你只需要在 Cloudflare 拿三样东西，填进 GitHub，再点一次“运行”。不需要命令行，也不需要在 Cloudflare 里粘贴代码。

### 第一部分：开通灌水区（约 10 分钟）

**1. 在 Cloudflare 创建一个 API 令牌**

1. 登录 Cloudflare，点右上角头像 → **My Profile** → 左边 **API Tokens** → **Create Token**。
2. 找到模板 **Edit Cloudflare Workers**，点右边的 **Use template**。
3. **Account Resources** 选你的账号；**Zone Resources** 选 `Specific zone` → `formalnaturalist.co.nz`。
4. 拉到底点 **Continue to summary** → **Create Token**。
5. 复制显示出来的令牌。它只显示这一次。

**2. 复制 Account ID**

Cloudflare 左侧菜单点 **Workers & Pages**，页面右侧有 **Account ID**，点旁边的复制按钮。

**3. 创建 KV 存储**（已完成，ID 已写进 `worker/wrangler.toml`，换新的 KV 时才需要改）

1. 左侧菜单 **Storage & Databases** → **KV** → **Create a namespace**（有的界面叫 Create instance）。
2. 名字填 `formalia`，创建。
3. 列表里这一行有一串 32 位的 ID，复制下来。

**4. 填进 GitHub**

打开 formalia 仓库 → **Settings** → **Secrets and variables** → **Actions**。

在 **Secrets** 标签页，点 **New repository secret**，逐个添加：

| Name | Secret |
| --- | --- |
| `CLOUDFLARE_API_TOKEN` | 第 1 步的令牌 |
| `CLOUDFLARE_ACCOUNT_ID` | 第 2 步的 Account ID |
| `ANON_SECRET` | 随便打一串至少 32 个字符的乱码，例如在键盘上乱敲。填好后不要再改，改了所有人的匿名编号都会变 |
| `CHAT_ADMIN_TOKEN` | 再打一串至少 16 个字符的乱码，这是你的聊天室管理员口令，自己记下来 |

**5. 运行部署**

仓库顶部 **Actions** → 左边 **Deploy Worker** → **Run workflow** → **Run workflow**。等一两分钟变绿。

**6. 试一下**

打开 https://formalnaturalist.co.nz/chat/ ，能看到“欢迎来到灌水区”就成功了。

管理员模式：打开 `https://formalnaturalist.co.nz/chat/#admin=你的CHAT_ADMIN_TOKEN` 一次。口令会存在这台电脑的浏览器里，地址栏会自动抹掉。之后每条消息旁边会出现“删”和“封”两个按钮。“封”会暂停这个人的网络地址 7 天，并删除他的全部消息。

### 第二部分：开通网页编辑

只需要一个 GitHub 令牌。人机验证是可选的：不配就不验证，只靠限流（每个匿名编号每小时 6 次，全站每天 200 次，可在 `worker/wrangler.toml` 里调）。

**1. 生成令牌**（只能你本人在 GitHub 上操作，别人代替不了，也不要把令牌发给任何人）：打开 https://github.com/settings/personal-access-tokens/new 。

- Token name：`formalia-edit`
- Expiration：选一年
- Repository access：选 **Only select repositories**，再选 `formalia`
- Permissions → Repository permissions → **Issues**：选 **Read and write**，其余不动
- 点 **Generate token**，复制以 `github_pat_` 开头的那串字符

**2. 填进 GitHub**：仓库 Settings → Secrets and variables → Actions → **New repository secret**。Name 填 `EDIT_GITHUB_TOKEN`，Secret 粘贴刚才的令牌，点 Add secret。

**3. 运行一次 Deploy Worker**（Actions → Deploy Worker → Run workflow）。打开 https://formalnaturalist.co.nz/api/config ，看到 `"edit":true` 就开通了。

**表述页的“问 AI”**：在 DeepInfra 后台 API Keys 页面新建一个密钥，填为 Secret `DEEPINFRA_API_KEY`；想用 Gemini 兜底，再把 Gemini 密钥填为 Secret `GEMINI_API_KEY`。两个都填时先问 DeepInfra，出错再问 Gemini；只填一个就只用那一个。换模型时填 Variable `DEEPINFRA_MODEL`（默认 `Qwen/Qwen3.8-Flash`）或 `GEMINI_MODEL`（默认 `gemini-3.8-flash`），值只写模型名本身。填好后运行一次 Deploy Worker。

**以后想加人机验证**：Cloudflare 左侧 **Turnstile** → **Add widget**，Hostname 加 `formalnaturalist.co.nz` 和 `www.formalnaturalist.co.nz`，模式选 **Managed**。把 Secret Key 填为 Secret `TURNSTILE_SECRET`，Site Key 填为 Variable `TURNSTILE_SITEKEY`，再运行一次 Deploy Worker。

### 以后

`worker/` 里的代码有改动、合并到 main 后，GitHub 会自动重新部署，不用再手动运行。令牌到期时，更新 GitHub 里对应的 Secret，再运行一次 Deploy Worker。

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
