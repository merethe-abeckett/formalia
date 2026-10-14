/-
Formalia · 条目 #20261014-03
猜想：考拉兹猜想
内容许可：Apache-2.0（与原作相同）
原作版权：Copyright 2025 The Formal Conjectures Authors，Apache License 2.0

改编自 google-deepmind/formal-conjectures 仓库的
FormalConjectures/Wikipedia/CollatzConjecture.lean。改动：去掉 `answer(sorry) ↔`、
`@[category …]` 等属性与 `sorry`，只登记命题本身，写成 `def`。
-/
module

public import Mathlib.Algebra.Group.Nat.Even
public import Mathlib.Algebra.Group.Nat.Even
public import Mathlib.Order.Iterate

@[expose] public section

namespace Registry.Collatz

/-- 表述 #20261014-03。

对每个正整数 `n`，存在 `m` 使得对 `n` 迭代 `m` 次 Collatz 映射后得到 `1`。Collatz 映射内联写出：偶数取 `n / 2`，奇数取 `3 * n + 1`。 -/
def S20261014_03 : Prop :=
  ∀ n : ℕ, 0 < n → ∃ m : ℕ, (fun k : ℕ => if Even k then k / 2 else 3 * k + 1)^[m] n = 1

end Registry.Collatz

end
