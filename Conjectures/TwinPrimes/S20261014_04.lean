/-
Formalia · 条目 #20261014-04
猜想：孪生素数猜想
内容许可：Apache-2.0（与原作相同）
原作版权：Copyright 2025 The Formal Conjectures Authors，Apache License 2.0

改编自 google-deepmind/formal-conjectures 仓库的
FormalConjectures/Wikipedia/TwinPrimes.lean。改动：去掉 `answer(sorry) ↔`、
`@[category …]` 等属性与 `sorry`，只登记命题本身，写成 `def`。
-/
module

public import Mathlib.Data.Nat.Prime.Defs
public import Mathlib.Data.Set.Finite.Basic

@[expose] public section

namespace Registry.TwinPrimes

/-- 表述 #20261014-04。

集合 `{p : ℕ | Nat.Prime p ∧ Nat.Prime (p + 2)}` 是无限集。原作写成 `answer(sorry) ↔ …`，这里只登记右侧命题。 -/
def S20261014_04 : Prop :=
  {p : ℕ | Nat.Prime p ∧ Nat.Prime (p + 2)}.Infinite

end Registry.TwinPrimes

end
