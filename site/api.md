Formalia 的全部内容都有机器可读的版本，不需要注册，也没有调用次数限制。它们是网站构建时生成的静态文件，和网页同步更新。

## 全部表述的索引

```
{{SITE}}/statements.json
```

列出每一条表述的编号、所属猜想、Lean 声明名、网页地址、单条数据地址、检查是否通过、是否已归档，以及证明和证否声明的数量。顶层还给出生成时的仓库提交、Lean 工具链和 Mathlib 版本。

## 单条表述

```
{{SITE}}/statements/<编号>.json
```

例如 `{{SITE}}/statements/20261014-01.json`。字段：

- `id`、`url`、`short_url`、`json_url`：编号、网页地址、永久短链接、本文件地址。
- `conjecture`：所属猜想的网址名、英文名、中文名和页面地址。
- `declaration`、`negation`、`module`：Lean 声明的完整名称、它的否命题、所在模块。证明声明要证明的就是 `declaration` 本身，证否声明要证明的是 `negation`。
- `lean`、`lean_path`：表述文件的完整源码，以及它在仓库里的路径。
- `toolchain`、`dependencies`：钉死的 Lean 工具链和各依赖的精确版本。
- `check`：检查器报告，包括用到的公理、是否含 sorry 或 native_decide、登记库内的自定义定义。没有运行检查器时为 null。
- `submitted_by`、`submitted_at`、`source`、`license`：提交者、日期、来源和许可。
- `informal_restatement`：提交者对 Lean 代码的自然语言复述，只代表提交者本人的理解。
- `claims`：证明和证否声明，包括声明编号、方向、声称方、登记时间和机器验证结果。
- `archived`：已归档时给出日期、原因和讨论地址，否则为 null。
- `citation`：纯文本和 BibTeX 两种引用格式。

字段只会增加，不会改名或删除。如果将来需要不兼容的改动，会换一个新的 `schema` 值，例如 `formalia.statement/2`。

## 短链接

```
{{SITE}}/s/<编号>/
```

只认编号，跳到这条表述的页面。猜想改名、换网址名都不会失效，适合印在论文、幻灯片和徽章里。

## 给 AI 助手

```
{{SITE}}/llms.txt
```

按 [llms.txt](https://llmstxt.org/) 约定写的一页英文说明：登记库是什么、不是什么，数据在哪里，以及全部猜想的列表。

## 引用

在论文、公告或证明说明里提到某条表述时，请引用它的编号，例如“Formalia statement #20261014-01”。编号永不复用，编号指向的 Lean 代码也永远不变。每个表述页的“引用”一节都有现成的纯文本和 BibTeX，和 JSON 里的 `citation` 字段相同。

## 更新动态

```
{{SITE}}/feed.xml
```

Atom 格式的订阅源，包含最近登记的表述、证明与证否声明、解读和归档。网页版在“最近更新”页。

## 许可

数据接口里的内容与网页相同，按各条目自己声明的许可发布，默认 CC-BY-4.0。代码以 Apache-2.0 发布。
