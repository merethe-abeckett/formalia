# 用 Zenodo 归档发布版本

1. 用 GitHub 账号登录 https://zenodo.org ，进入账户设置中的 **GitHub** 页。
2. 打开本仓库旁边的开关。
3. 创建一个 GitHub Release，例如 Mathlib 升版本或新增一批表述后发 `v2026.10`。
4. Zenodo 会归档该 Release 的压缩包并分配 DOI；第一次发布还会得到一个“概念 DOI”，永远指向最新版本。
5. 拿到概念 DOI 后把徽章放进 README。

可选：在仓库根目录加 `.zenodo.json`，填 `creators`、`title`、`description`、`license`（代码为 `Apache-2.0`，在 description 中注明条目内容为 CC-BY-4.0），存档元数据会自动填好。
