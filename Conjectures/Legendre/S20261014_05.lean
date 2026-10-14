/-
Formalia · 条目 #20261014-05
猜想：勒让德猜想
内容许可：Apache-2.0（与原作相同）
原作版权：Copyright 2025 The Formal Conjectures Authors，Apache License 2.0

改编自 google-deepmind/formal-conjectures 仓库的
FormalConjectures/Wikipedia/LegendreConjecture.lean。改动：去掉 `answer(sorry) ↔`、
`@[category …]` 等属性与 `sorry`，只登记命题本身，写成 `def`。
-/
module

public import Mathlib.Data.Nat.Prime.Defs
public import Mathlib.Order.Interval.Set.Defs

@[expose] public section

namespace Registry.Legendre

/-- 表述 #20261014-05。

对每个 `n ≥ 1`，开区间 `(n ^ 2, (n + 1) ^ 2)` 内存在素数。原作写成 `answer(sorry) ↔ …`，这里只登记右侧命题。 -/
def S20261014_05 : Prop :=
  ∀ n : ℕ, 1 ≤ n → ∃ p ∈ Set.Ioo (n ^ 2) ((n + 1) ^ 2), Nat.Prime p

end Registry.Legendre

end
