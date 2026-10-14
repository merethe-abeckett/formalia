/-
Formalia · 条目 #20261014-07
猜想：勒穆瓦纳猜想
内容许可：Apache-2.0（与原作相同）
原作版权：Copyright 2025 The Formal Conjectures Authors，Apache License 2.0

改编自 google-deepmind/formal-conjectures 仓库的
FormalConjectures/Wikipedia/Lemoine.lean。改动：去掉 `answer(sorry) ↔`、
`@[category …]` 等属性与 `sorry`，只登记命题本身，写成 `def`。
-/
module

public import Mathlib.Data.Nat.Prime.Defs
public import Mathlib.Algebra.Ring.Parity

@[expose] public section

namespace Registry.Lemoine

/-- 表述 #20261014-07。

每个满足 `6 < n` 的奇数 `n` 都存在素数 `p, q` 使 `p + 2 * q = n`。 -/
def S20261014_07 : Prop :=
  ∀ n : ℕ, 6 < n → Odd n → ∃ p q : ℕ, Nat.Prime p ∧ Nat.Prime q ∧ p + 2 * q = n

end Registry.Lemoine

end
