/-
Formalia · 条目 #20261014-50
猜想：Inverse Galois problem
内容许可：Apache-2.0（与原作相同）
原作版权：Copyright 2025 The Formal Conjectures Authors，Apache License 2.0

改编自 google-deepmind/formal-conjectures 仓库的 FormalConjectures/Wikipedia/InverseGalois.lean。
改动：去掉 `answer(sorry) ↔`、`@[category …]` 等属性与 `sorry`，theorem 的参数改写成 `∀`，
只登记命题本身，写成 `def`。
-/
module

public import Mathlib.Algebra.Algebra.Defs
public import Mathlib.Algebra.Algebra.Equiv
public import Mathlib.Algebra.Field.Defs
public import Mathlib.Algebra.Field.Rat
public import Mathlib.Algebra.Group.Defs
public import Mathlib.Algebra.Group.Equiv.Defs
public import Mathlib.Data.Fintype.Defs
public import Mathlib.FieldTheory.Galois.Basic

@[expose] public section

namespace Registry.InverseGaloisProblem

namespace S20261014_50_aux

structure GaloisRealization.{u, v} (K : Type u) (G : Type v) [Field K] [Group G] where
  -- Every Galois extension of `K : Type u` injects into `AlgebraicClosure K : Type u`.
  -- We therefore lose no generality assuming `L : Type u`.
  L : Type u
  to_field : Field L
  to_algebra : Algebra K L
  to_isGalois : IsGalois K L
  iso : G ≃* (L ≃ₐ[K] L)

class IsRealizable (K G : Type*) [Field K] [Group G] where
  exists_realization : Nonempty (GaloisRealization K G)

end S20261014_50_aux

open S20261014_50_aux in
/-- 表述 #20261014-50。

The **Inverse Galois Problem**: every finite group is
isomorphic to the Galois group of a Galois extension of the
rationals. -/
def S20261014_50 : Prop :=
  ∀ {G : Type*} [Fintype G] [Group G], IsRealizable ℚ G

end Registry.InverseGaloisProblem

end
