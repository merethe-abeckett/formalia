<!-- 请只保留适用的部分 -->

## 这个 PR 做什么

- [ ] 登记新表述：编号 `#________`，猜想 ________
- [ ] 记录证明声明：表述 `#________`
- [ ] 修正事实错误
- [ ] 其他（说明）：

## 新表述自查

- [ ] 文件是单个 `def … : Prop`，以 `module` 开头，声明在 `@[expose] public section` 内
- [ ] 无 `sorry`、`axiom`、`opaque`、`constant`、`native_decide`
- [ ] `.json` 里 `source`、`submitted_by`、`submitted_at` 已填；改编的附了原始链接
- [ ] 本地跑过 `scripts/run_checks.sh` 和 `python3 scripts/validate_meta.py`

## 提醒

本仓库不讨论表述是否等价于原猜想，PR 里请不要包含这类论证。
