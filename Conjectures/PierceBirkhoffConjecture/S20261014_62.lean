/-
Formalia · 条目 #20261014-62
猜想：Pierce–Birkhoff conjecture
内容许可：Apache-2.0（与原作相同）
原作版权：Copyright 2025 The Formal Conjectures Authors，Apache License 2.0

改编自 google-deepmind/formal-conjectures 仓库的 FormalConjectures/Wikipedia/PierceBirkhoff.lean。
改动：去掉 `answer(sorry) ↔`、`@[category …]` 等属性与 `sorry`，theorem 的参数改写成 `∀`，
只登记命题本身，写成 `def`。
-/
module

public import Mathlib.Algebra.Polynomial.Basic
public import Mathlib.Algebra.Group.Defs
public import Mathlib.Algebra.Group.Finsupp
public import Mathlib.Algebra.Group.Nat.Defs
public import Mathlib.Algebra.GroupWithZero.Defs
public import Mathlib.Algebra.GroupWithZero.Nat
public import Mathlib.Algebra.MonoidAlgebra.Defs
public import Mathlib.Algebra.MvPolynomial.Basic
public import Mathlib.Algebra.MvPolynomial.Eval
public import Mathlib.Algebra.Ring.Defs
public import Mathlib.Algebra.Ring.Hom.Defs
public import Mathlib.Data.Finite.Defs
public import Mathlib.Data.Finset.Defs
public import Mathlib.Data.Finsupp.Defs
public import Mathlib.Data.FunLike.Basic
public import Mathlib.Data.Real.Archimedean
public import Mathlib.Data.Real.Basic
public import Mathlib.Data.Set.Defs
public import Mathlib.Data.SetLike.Basic
public import Mathlib.Order.SetNotation
public import Mathlib.Topology.Constructions
public import Mathlib.Topology.Defs.Basic
public import Mathlib.Topology.MetricSpace.Pseudo.Defs
public import Mathlib.Topology.UniformSpace.Defs

@[expose] public section

namespace Registry.PierceBirkhoffConjecture

namespace S20261014_62_aux

open scoped Polynomial

def IsSemiAlgebraic {n : ℕ} (S : Set (Fin n → ℝ)) : Prop :=
  ∃ (ι : Type) (p₀ p₁ : ι → Finset (MvPolynomial (Fin n) ℝ)), Finite ι ∧
    S = ⋃ i, {x | (∀ p ∈ p₀ i, MvPolynomial.eval x p = 0) ∧
      ∀ p ∈ p₁ i, MvPolynomial.eval x p > 0}

def IsPiecewiseMvPolynomial {n : ℕ} (f : (Fin n → ℝ) → ℝ) : Prop :=
  ∃ (ι : Type) (P : ι → Set (Fin n → ℝ))
    (g : ι → MvPolynomial (Fin n) ℝ),
    Finite ι ∧
    (∀ i, IsClosed (P i)) ∧
    (∀ i, IsSemiAlgebraic (P i)) ∧
    (⋃ i, P i) = Set.univ ∧
    ∀ᵉ (i : ι) (x ∈ P i), f x = MvPolynomial.eval x (g i)

end S20261014_62_aux

open S20261014_62_aux in
/-- 表述 #20261014-62。

The Pierce-Birkhoff conjecture states that for every real piecewise-polynomial function
`f : ℝⁿ → ℝ`, there exists a finite set of polynomials `gᵢⱼ ∈ ℝ[x₁, ..., xₙ]` such that
`f = supᵢ infⱼ(gᵢⱼ)`. -/
def S20261014_62 : Prop :=
  ∀ {n : ℕ} (f : (Fin n → ℝ) → ℝ)
      (hf : IsPiecewiseMvPolynomial f), ∃ (ι κ : Type) (g : ι → κ → MvPolynomial (Fin n) ℝ), Finite ι ∧ Finite κ ∧
        ∀ x, f x = ⨆ i, ⨅ j, MvPolynomial.eval x (g i j)

end Registry.PierceBirkhoffConjecture

end
