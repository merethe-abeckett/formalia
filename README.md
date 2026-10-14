# Lean 表述登记库

## 阅读前说明（一些作者自己的话）

> 我觉得我们可以建立一个仓库，人类社区贡献者只负责转写原猜想命题至证明语言（现阶段先做 Lean 4，以后不一定非得是 Lean 4，任何证明语言都可以），比如 Hodge 猜想可以转写成 Lean 4 的 #20261010 或 #20261004 等数字编号的表述，然后 LLM（人类也可以，当然）只负责提供能证明或证否这些命题的 Lean 代码，放在自己的仓库里，到这里登记一句“我证明了 #某编号”，由其他 AI 或人类贡献者跑 Lean 来独立验证。这样一来，数学家可以选择认可或者不认可这些原猜想的 Lean 4 表述是否等价于原猜想，且任何人和公司都可以快速发布并快速被核查。而对未来数学家可以干什么我其实也有回答，就是做数学的解释学，和生物分类学家看 iNat 来鉴定和分类类似，一个是认领这些证明，一个则是从这些证明语言（不管是 LLM 还是人类写的）里面挖掘东西。

> 我觉得中国应该大力支持 OpenAI 用中文在中国投稿数学成果，全中文投稿到中国 preprint 平台上加速审核。然后给足 credits，表示 GPT 伟大，别理人类数学协会，我们承认你们的成果。然后把数学分为数学和数学解释学，前者由 ChatGLM、DeepSeek、Qwen、Kimi 和一堆其他模型审稿，后者是传统的人类审稿确保人类理解，以后别的国家数学家只好学习中文来发掘研究数学解释学。

上面是愿景，下面是本仓库现阶段的规则。两者有一处要先说清：本仓库本身不审稿，也不认证。模型在这里只做巡查，查 Lean 层面的问题；Lean 内核和 CI 查证明对不对；“表述等不等价于原猜想”谁都不查，留给数学家线下讨论。至于模型审稿、人类做解释学，那是下一阶段在别处发生的事，本仓库只负责把编号、表述、声明列清楚，让那些事有据可依。

本仓库强烈建议用户用中文普通话和各地中文方言完成对贡献的说明部分的补全，包括来源备注、非正式复述、PR 和议题里的说明。Lean 代码、JSON 字段名和 Mathlib 名称保持原样。

---

一个中立的目录，收录数学猜想的 Lean 4 形式化表述，全部针对钉死版本的 Mathlib 编译检查。

登记库**只列出，不判断**。每个自然语言猜想有一个消歧义页，页下列出该猜想的各条 Lean 表述，每条有永久编号，例如 `#20261014-01`。某条表述是否等价于原猜想，由数学家线下讨论，登记库不作结论。登记库只记录事实：

- 表述的 Lean 代码，形式为 `def … : Prop`；
- 检查时所用的工具链和各依赖的精确版本；
- 表述依赖的定义链，以及每个常量所在的模块；
- 谁提交的、何时提交、来源何处；
- 自动检查结果（能否编译、无 sorry、无 native_decide、只用标准公理、独立复核通过）；
- 哪些证明、由谁、**声称**证明了它；
- 可选的外部链接，只列不评。

任何人、任何 AI 公司，只能声称“证明了某个具体编号的表述”，不能声称“证明了某个猜想”。

## 目录结构

```
Conjectures/
  Goldbach/
    conjecture.json          消歧义页：名称、自然语言表述、参考资料
    S20261014_01.lean        表述 #20261014-01（一个 `def … : Prop`）
    S20261014_01.json        它的元数据
    S20261014_02.lean        表述 #20261014-02
    S20261014_02.json
Guides/                      AI 生成的导读（Gemini），逐定义解释 Lean 代码，可被人工修改
Archive/                     已归档的条目（编号保留，不再编译）
RegistryTools/Check.lean     检查器：公理、sorry、native_decide、定义链
scripts/run_checks.sh        编译并运行检查器，输出 build/check/*.json
scripts/lean4checker.sh      用 lean4checker 独立复核每个表述模块
scripts/validate_meta.py     元数据与命名规则校验
scripts/build_site.py        生成维基风格静态网站到 _site/
scripts/gen_guides.py        调用 Gemini 生成导读，写入 Guides/
scripts/archive_entry.py     提删公示期满后归档条目
patrol/patrol.py             巡查：双模型审查 Lean 层面问题，自动开议题
docs/DELETION.md             提删流程、巡查规则、公示期、归档
docs/ZENODO.md               用 Zenodo 为发布版本申请 DOI
.github/workflows/ci.yml     每次推送和 PR 的锁定检查
.github/workflows/pages.yml  构建并发布网站到 GitHub Pages
.github/workflows/patrol.yml 每周巡查
.github/workflows/guides.yml 生成或更新导读
```

### 编号

编号为日期式 `YYYYMMDD-NN`，`NN` 是同一天提交的流水号。`#20261014-01` 对应文件 `S20261014_01.lean`，因为 Lean 标识符不能以数字开头，也不能含连字符。编号永不复用、永不改号。

### 表述文件的要求

- 文件以 `module` 开头，用 `public import` 引入 Mathlib 模块，声明放在 `@[expose] public section` 内。
- 每个文件恰好一个 `def <名称> : Prop := …`，名称与元数据中的 `declaration` 一致。允许在同一文件内写辅助定义，检查器会把它们列为“自定义定义”，让读者一眼看出该表述并非只依赖 Mathlib。
- 不得出现 `sorry`、`axiom`、`opaque`、`constant`、`native_decide`。

### 元数据字段（`S<编号>.json`）

| 字段 | 含义 |
| --- | --- |
| `id` | `YYYYMMDD-NN` |
| `conjecture` | 所属 `conjecture.json` 的 slug |
| `module`、`declaration` | Lean 模块名和 `def` 的完整限定名 |
| `submitted_by`、`submitted_at` | 提交者与日期 |
| `source` | `kind`（`original` 原创、`adapted` 改编、`verbatim` 照录）、`url`、`note` |
| `informal_restatement` | 提交者对 Lean 代码的自然语言复述，网站上标注为提交者自述 |
| `claimed_proofs` | `{claimant, date, url, note}` 列表；只记录声明，不表示认可 |
| `external_links` | `{label, url}` 列表；只放链接，不加评论 |

## 锁定机制（CI）

每次推送和 PR 都会运行：

1. 对钉死版本的 Mathlib（见 `lake-manifest.json` 和 `lean-toolchain`）`lake build` 全部表述。
2. `lake exe check`：对每个声明用 `collectAxioms` 记录公理，标出 `sorryAx`，标出 `native_decide` 生成的辅助公理，标出 `propext`、`Classical.choice`、`Quot.sound` 之外的任何公理，并列出表述直接使用的常量及其所在模块。
3. `lean4checker`：从对应版本构建，把每个表述模块在全新内核中重放一遍。
4. `validate_meta.py`：命名与元数据规则。

检查未通过就不能合并。对数学内容没有人工“批准”环节，只检查事实是否齐全。

## 登记一条表述

1. 选择或新建 `Conjectures/<猜想>/conjecture.json`。
2. 新增 `S<YYYYMMDD>_<NN>.lean` 和 `S<YYYYMMDD>_<NN>.json`。
3. 本地运行：`lake exe cache get && scripts/run_checks.sh && scripts/lean4checker.sh && python3 scripts/validate_meta.py`。
4. 提交 Pull Request。

要为已有表述记录一条证明声明，在它的 `claimed_proofs` 里加一项并附证明链接。登记库不托管证明，只指向证明。

## 提删、巡查、归档

见 `docs/DELETION.md`。简而言之：只有 Lean 层面的问题可以提删，等价性问题永远不能。每周一次巡查（`patrol/patrol.py`，两个独立模型，起步用 Qwen 和 Gemini）按固定规则开议题；提删公示 14 天；之后条目被**归档**到 `Archive/`，编号永久保留，不是删除。巡查需要仓库密钥 `QWEN_API_KEY` 和/或 `GEMINI_API_KEY`；只有一个密钥时进入单模型模式，只能开“巡查发现”，不能开提删公示。

## AI 导读

`scripts/gen_guides.py` 调用 Gemini，为每条表述生成一份导读，存在 `Guides/<猜想>/S<编号>.md`，网站上单独一栏展示。导读只做两件事：逐个解释表述用到的定义（把钉死版本 Mathlib 里的定义源码喂给模型，而不是让它凭记忆），以及把量词和条件翻译成自然语言。它不评价表述好坏，不与原猜想比较。导读是普通文件，任何人都可以提 PR 修正；页面上标注为 AI 生成、不代表登记库判断。

## 网站

`python3 scripts/build_site.py` 生成 `_site/`。Pages 工作流在每次推送到 `main` 时发布。需在仓库 **Settings → Pages → Source** 选择 GitHub Actions 一次。

## 版本与引用

工具链和依赖版本钉死在 `lean-toolchain` 和 `lake-manifest.json` 中，每个表述页面都会显示。升级版本时 CI 会重新检查全部表述，改动是历史中的普通提交。需要可引用的快照时，创建 GitHub Release 并用 Zenodo 归档，每个 Release 得到一个 DOI，见 `docs/ZENODO.md`。

## 许可

- 代码（检查器、脚本、工作流）：Apache-2.0，见 `LICENSE`。
- 条目内容（`Conjectures/**`）：CC-BY-4.0，见 `LICENSE-CONTENT`。改编自其他项目的表述在文件头和 `source` 中注明来源。
