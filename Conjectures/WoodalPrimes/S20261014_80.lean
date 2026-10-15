/-
Formalia · 条目 #20261014-80
猜想：WoodalPrimes
内容许可：Apache-2.0（与原作相同）
原作版权：Copyright 2025 The Formal Conjectures Authors，Apache License 2.0

改编自 google-deepmind/formal-conjectures 仓库的 FormalConjectures/Wikipedia/WoodalPrimes.lean。
改动：去掉 `answer(sorry) ↔`、`@[category …]` 等属性与 `sorry`，theorem 的参数改写成 `∀`，
只登记命题本身，写成 `def`。
-/
module

public import Mathlib.Algebra.Group.Defs
public import Mathlib.Algebra.Group.Nat.Defs
public import Mathlib.Data.Finite.Defs
public import Mathlib.Data.Nat.Prime.Defs
public import Mathlib.Data.Set.Defs

@[expose] public section

namespace Registry.WoodalPrimes

/-- 表述 #20261014-80。

There are infinitely many prime numbers of the form `k * 2 ^ k - 1` for `k > 1`. -/
def S20261014_80 : Prop :=
  {k : ℕ | 1 < k ∧ (k * 2 ^ k - 1).Prime}.Infinite

end Registry.WoodalPrimes

end
