/-
Formalia · 条目 #20261014-32
猜想：Euclid Numbers conjecture
内容许可：Apache-2.0（与原作相同）
原作版权：Copyright 2025 The Formal Conjectures Authors，Apache License 2.0

改编自 google-deepmind/formal-conjectures 仓库的 FormalConjectures/Wikipedia/Euclid.lean。
改动：去掉 `answer(sorry) ↔`、`@[category …]` 等属性与 `sorry`，theorem 的参数改写成 `∀`，
只登记命题本身，写成 `def`。
-/
module

public import Mathlib.Algebra.BigOperators.Group.Finset.Defs
public import Mathlib.Algebra.Group.Nat.Defs
public import Mathlib.Data.Finite.Defs
public import Mathlib.Data.Finset.Range
public import Mathlib.Data.Nat.Nth
public import Mathlib.Data.Nat.Prime.Defs
public import Mathlib.Data.Set.Defs

@[expose] public section

namespace Registry.EuclidNumbersConjecture

namespace S20261014_32_aux

noncomputable def Euclid (n : ℕ) : ℕ := 1 + ∏ i ∈ Finset.range n, i.nth Nat.Prime

end S20261014_32_aux

open S20261014_32_aux in
/-- 表述 #20261014-32。

It is not known whether there is an infinite number of prime Euclid numbers. -/
def S20261014_32 : Prop :=
  {n | (Euclid n).Prime}.Infinite

end Registry.EuclidNumbersConjecture

end
