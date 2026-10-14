/-
Formalia · 条目 #20261014-19
猜想：Brennan's Conjecture
内容许可：Apache-2.0（与原作相同）
原作版权：Copyright 2025 The Formal Conjectures Authors，Apache License 2.0

改编自 google-deepmind/formal-conjectures 仓库的 FormalConjectures/Wikipedia/Brennanconjecture.lean。
改动：去掉 `answer(sorry) ↔`、`@[category …]` 等属性与 `sorry`，theorem 的参数改写成 `∀`，
只登记命题本身，写成 `def`。
-/
module

public import Mathlib.Analysis.Analytic.Basic
public import Mathlib.Analysis.Calculus.Deriv.Basic
public import Mathlib.Analysis.InnerProductSpace.Defs
public import Mathlib.Analysis.Normed.Field.Basic
public import Mathlib.Analysis.Normed.Group.Defs
public import Mathlib.Analysis.Normed.Group.Real
public import Mathlib.Analysis.Normed.Module.Basic
public import Mathlib.Analysis.Normed.Ring.Basic
public import Mathlib.Analysis.RCLike.Basic
public import Mathlib.Analysis.SpecialFunctions.Log.Basic
public import Mathlib.Analysis.SpecialFunctions.Pow.Real
public import Mathlib.Analysis.SpecialFunctions.Trigonometric.Basic
public import Mathlib.Data.Complex.Basic
public import Mathlib.Data.Nat.Cast.Defs
public import Mathlib.Data.Real.Archimedean
public import Mathlib.Data.Real.Basic
public import Mathlib.Data.Set.Defs
public import Mathlib.Data.Set.Operations
public import Mathlib.MeasureTheory.Integral.Bochner.Basic
public import Mathlib.MeasureTheory.Measure.Haar.OfBasis
public import Mathlib.MeasureTheory.Measure.MeasureSpaceDef
public import Mathlib.MeasureTheory.Measure.Restrict
public import Mathlib.Order.ConditionallyCompleteLattice.Defs
public import Mathlib.Order.Interval.Set.Defs
public import Mathlib.Order.LiminfLimsup
public import Mathlib.Order.SetNotation
public import Mathlib.Topology.Bornology.Basic
public import Mathlib.Topology.Defs.Filter
public import Mathlib.Topology.MetricSpace.Pseudo.Defs
public import Mathlib.Topology.UniformSpace.Defs

@[expose] public section

namespace Registry.BrennanConjecture

namespace S20261014_19_aux

open Complex Filter MeasureTheory Set Topology

def unitDisk : Set ℂ := {z | ‖z‖ < 1}

structure IsUnivalentNormalized (f : ℂ → ℂ) : Prop where
  analyticOn : AnalyticOn ℂ f unitDisk
  injOn      : InjOn f unitDisk
  map_zero   : f 0 = 0
  deriv_zero : deriv f 0 = 1

noncomputable def integralMeansSpectrum (f : ℂ → ℂ) (τ : ℝ) : ℝ :=
  limsup
    (fun r => Real.log (∫ θ in Ioc (-Real.pi) Real.pi,
        ‖deriv f (r • exp (Complex.I * θ))‖ ^ τ) /
      |Real.log (1 - r)|)
    (𝓝[Iio 1] (1 : ℝ))

noncomputable def universalSpectrumBounded (τ : ℝ) : ℝ :=
  sSup {β | ∃ f : ℂ → ℂ, IsUnivalentNormalized f ∧
    Bornology.IsBounded (f '' unitDisk) ∧ β = integralMeansSpectrum f τ}

end S20261014_19_aux

open S20261014_19_aux in
/-- 表述 #20261014-19。

Brennan's conjecture, part 2: $B_b(-2) = 1$. -/
def S20261014_19 : Prop :=
  universalSpectrumBounded (-2) = 1

end Registry.BrennanConjecture

end
