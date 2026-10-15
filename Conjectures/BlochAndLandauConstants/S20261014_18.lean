/-
Formalia · 条目 #20261014-18
猜想：Bloch and Landau constants
内容许可：Apache-2.0（与原作相同）
原作版权：Copyright 2025 The Formal Conjectures Authors，Apache License 2.0

改编自 google-deepmind/formal-conjectures 仓库的 FormalConjectures/Wikipedia/Bloch.lean。
改动：去掉 `answer(sorry) ↔`、`@[category …]` 等属性与 `sorry`，theorem 的参数改写成 `∀`，
只登记命题本身，写成 `def`。
-/
module

public import Mathlib.Order.Filter.Defs
public import Mathlib.Algebra.Group.Defs
public import Mathlib.Analysis.CStarAlgebra.Classes
public import Mathlib.Analysis.Calculus.Deriv.Basic
public import Mathlib.Analysis.Calculus.FDeriv.Defs
public import Mathlib.Analysis.Complex.Basic
public import Mathlib.Analysis.Normed.Field.Basic
public import Mathlib.Analysis.Normed.Ring.Basic
public import Mathlib.Analysis.SpecialFunctions.Gamma.Basic
public import Mathlib.Data.Complex.Basic
public import Mathlib.Data.Nat.Cast.Defs
public import Mathlib.Data.Real.Archimedean
public import Mathlib.Data.Real.Basic
public import Mathlib.Data.Real.Sqrt
public import Mathlib.Data.Set.Defs
public import Mathlib.Data.Set.Operations
public import Mathlib.Order.SetNotation
public import Mathlib.Topology.Defs.Basic
public import Mathlib.Topology.MetricSpace.Pseudo.Defs
public import Mathlib.Topology.UniformSpace.Defs

@[expose] public section

namespace Registry.BlochAndLandauConstants

namespace S20261014_18_aux

open scoped Topology ENNReal

open Metric Set Filter

noncomputable def blochConstant : ℝ :=
  sSup {B : ℝ | ∀ f : ℂ → ℂ, DifferentiableOn ℂ f (ball 0 1) → deriv f 0 = 1 →
    ∃ S, IsOpen S ∧ S ⊆ ball 0 1 ∧ ∃ x, f '' S = ball x B ∧ InjOn f S}

end S20261014_18_aux

open S20261014_18_aux in
/-- 表述 #20261014-18。

Ahlfors and Grunsky also conjectured in [AG37] that this upper bound is the precise value of the
Bloch constant. -/
def S20261014_18 : Prop :=
  blochConstant = Real.Gamma (1 / 3) * Real.Gamma (11 / 12) /
      (Real.Gamma (1 / 4) * Real.sqrt (1 + Real.sqrt 3))

end Registry.BlochAndLandauConstants

end
