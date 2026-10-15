/-
Formalia · 条目 #20261014-24
猜想：Class number problem for real quadratic fields
内容许可：Apache-2.0（与原作相同）
原作版权：Copyright 2025 The Formal Conjectures Authors，Apache License 2.0

改编自 google-deepmind/formal-conjectures 仓库的 FormalConjectures/Wikipedia/ClassNumberProblem.lean。
改动：去掉 `answer(sorry) ↔`、`@[category …]` 等属性与 `sorry`，theorem 的参数改写成 `∀`，
只登记命题本身，写成 `def`。
-/
module

public import Mathlib.Algebra.Field.Rat
public import Mathlib.Algebra.Group.Defs
public import Mathlib.Algebra.Group.Int.Defs
public import Mathlib.Algebra.Group.Irreducible.Defs
public import Mathlib.Algebra.GroupWithZero.Defs
public import Mathlib.Algebra.Polynomial.Basic
public import Mathlib.Algebra.Ring.Defs
public import Mathlib.Algebra.Ring.Hom.Defs
public import Mathlib.Algebra.Ring.Rat
public import Mathlib.Algebra.Squarefree.Basic
public import Mathlib.Analysis.Normed.Field.Basic
public import Mathlib.Analysis.Normed.Field.Lemmas
public import Mathlib.Analysis.Normed.Ring.Basic
public import Mathlib.Data.Finite.Defs
public import Mathlib.Data.FunLike.Basic
public import Mathlib.Data.Set.Defs
public import Mathlib.Logic.Basic
public import Mathlib.NumberTheory.NumberField.ClassNumber
public import Mathlib.RingTheory.AdjoinRoot

@[expose] public section

namespace Registry.ClassNumberProblemForRealQuadraticFields

namespace S20261014_24_aux

open Polynomial

def IsClassNumberOne (d : ℤ) : Prop :=
  ∃ (h₂ : Irreducible (X ^ 2 - C (d : ℚ))),
  have := Fact.mk h₂
  NumberField.classNumber (AdjoinRoot (X ^ 2 - C (d : ℚ))) = 1

end S20261014_24_aux

open S20261014_24_aux in
/-- 表述 #20261014-24。

There are infinitely many real quadratic fields `ℚ(√d)` with class number one,
where `d > 1` is a squarefree integer. -/
def S20261014_24 : Prop :=
  { d : ℤ | Squarefree d ∧ d > 1 ∧ IsClassNumberOne d }.Infinite

end Registry.ClassNumberProblemForRealQuadraticFields

end
