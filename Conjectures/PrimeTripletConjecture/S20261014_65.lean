/-
Formalia · 条目 #20261014-65
猜想：Prime Triplet Conjecture
内容许可：Apache-2.0（与原作相同）
原作版权：Copyright 2025 The Formal Conjectures Authors，Apache License 2.0

改编自 google-deepmind/formal-conjectures 仓库的 FormalConjectures/Wikipedia/PrimeTriplets.lean。
改动：去掉 `answer(sorry) ↔`、`@[category …]` 等属性与 `sorry`，theorem 的参数改写成 `∀`，
只登记命题本身，写成 `def`。
-/
module

public import Mathlib.Algebra.GroupWithZero.Nat
public import Mathlib.Algebra.Prime.Defs
public import Mathlib.Data.Finite.Defs
public import Mathlib.Data.Set.Defs

@[expose] public section

namespace Registry.PrimeTripletConjecture

/-- 表述 #20261014-65。

Are there infinitely many tuples of three consecutive primes $(p, q, r)$ such that $r - p = 6$? -/
def S20261014_65 : Prop :=
  {p : ℕ | Prime p ∧ (Prime (p + 2) ∨ Prime (p + 4)) ∧ Prime (p + 6)}.Infinite

end Registry.PrimeTripletConjecture

end
