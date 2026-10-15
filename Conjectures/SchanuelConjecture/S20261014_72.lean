/-
Formalia · 条目 #20261014-72
猜想：Schanuel's Conjecture
内容许可：Apache-2.0（与原作相同）
原作版权：Copyright 2025 The Formal Conjectures Authors，Apache License 2.0

改编自 google-deepmind/formal-conjectures 仓库的 FormalConjectures/Wikipedia/Schanuel.lean。
改动：去掉 `answer(sorry) ↔`、`@[category …]` 等属性与 `sorry`，theorem 的参数改写成 `∀`，
只登记命题本身，写成 `def`。
-/
module

public import Mathlib.Data.Real.Basic
public import Mathlib.Algebra.Algebra.Rat
public import Mathlib.Algebra.EuclideanDomain.Defs
public import Mathlib.Algebra.EuclideanDomain.Field
public import Mathlib.Algebra.Field.Rat
public import Mathlib.Algebra.Ring.Rat
public import Mathlib.Analysis.CStarAlgebra.Classes
public import Mathlib.Analysis.Complex.Basic
public import Mathlib.Analysis.Complex.Exponential
public import Mathlib.Analysis.Complex.Norm
public import Mathlib.Analysis.Normed.Field.Basic
public import Mathlib.Analysis.Normed.Field.Lemmas
public import Mathlib.Analysis.Normed.Group.Continuity
public import Mathlib.Analysis.Normed.Group.Defs
public import Mathlib.Analysis.Normed.Module.Basic
public import Mathlib.Analysis.Normed.Ring.Basic
public import Mathlib.Analysis.RCLike.Basic
public import Mathlib.Data.Complex.Basic
public import Mathlib.Data.Set.Defs
public import Mathlib.Data.Set.Operations
public import Mathlib.Data.SetLike.Basic
public import Mathlib.FieldTheory.IntermediateField.Adjoin.Defs
public import Mathlib.FieldTheory.IntermediateField.Basic
public import Mathlib.LinearAlgebra.LinearIndependent.Defs
public import Mathlib.RingTheory.AlgebraicIndependent.Basic
public import Mathlib.SetTheory.Cardinal.Defs
public import Mathlib.SetTheory.Cardinal.Order
public import Mathlib.Topology.MetricSpace.Pseudo.Defs
public import Mathlib.Topology.UniformSpace.Defs

@[expose] public section

namespace Registry.SchanuelConjecture

namespace S20261014_72_aux

open scoped Real Complex

open IntermediateField

def statement : Prop :=
  ∀ (n : ℕ) (z : Fin n → ℂ) (h : LinearIndependent ℚ z), n ≤ Algebra.trdeg ℚ (adjoin ℚ (Set.range z ∪ Set.range (cexp ∘ z)))

end S20261014_72_aux

open S20261014_72_aux in
/-- 表述 #20261014-72。

Given any set of $n$ complex numbers $\{z_1, ..., z_n\}$ that are linearly independent over
$\mathbb{Q}$, the field extension $\mathbb{Q}(z_1, ..., z_n, e^{z_1}, ..., e^{z_n})$
has transcendence degree at least $n$ over $\mathbb{Q}$. -/
def S20261014_72 : Prop :=
  statement

end Registry.SchanuelConjecture

end
