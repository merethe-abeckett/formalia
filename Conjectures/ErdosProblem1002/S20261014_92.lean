/-
Formalia · 条目 #20261014-92
猜想：Erdős Problem 1002
内容许可：Apache-2.0（与原作相同）
原作版权：Copyright 2025 The Formal Conjectures Authors，Apache License 2.0

改编自 google-deepmind/formal-conjectures 仓库的 FormalConjectures/ErdosProblems/1002.lean。
改动：去掉 `answer(sorry) ↔`、`@[category …]` 等属性与 `sorry`，theorem 的参数改写成 `∀`，
只登记命题本身，写成 `def`。
-/
module

public import Mathlib.Data.Finset.Defs
public import Mathlib.Topology.Defs.Basic
public import Mathlib.Algebra.BigOperators.Group.Finset.Defs
public import Mathlib.Algebra.Group.Defs
public import Mathlib.Algebra.Order.Floor.Defs
public import Mathlib.Analysis.SpecialFunctions.Log.Basic
public import Mathlib.Data.ENNReal.Basic
public import Mathlib.Data.FunLike.Basic
public import Mathlib.Data.Nat.Basic
public import Mathlib.Data.Nat.Cast.Defs
public import Mathlib.Data.Real.Archimedean
public import Mathlib.Data.Real.Basic
public import Mathlib.Data.Set.Defs
public import Mathlib.MeasureTheory.Measure.Haar.OfBasis
public import Mathlib.MeasureTheory.Measure.MeasureSpaceDef
public import Mathlib.Order.Filter.AtTopBot.Defs
public import Mathlib.Order.Filter.Defs
public import Mathlib.Order.Interval.Finset.Defs
public import Mathlib.Order.Interval.Finset.Nat
public import Mathlib.Order.Interval.Set.Defs
public import Mathlib.Order.Monotone.Defs
public import Mathlib.Topology.Defs.Filter
public import Mathlib.Topology.MetricSpace.Pseudo.Defs
public import Mathlib.Topology.UniformSpace.Defs

@[expose] public section

namespace Registry.ErdosProblem1002

namespace S20261014_92_aux

open Real Set Filter Finset MeasureTheory Topology

def statement : Prop :=
  ∃ g : ℝ → ℝ, Monotone g ∧
        Tendsto g atBot (𝓝 0) ∧
        Tendsto g atTop (𝓝 1) ∧
        letI f :=  fun (α : ℝ) (n : ℕ) ↦
          (1 / log n) * ∑ k ∈ Icc (1 : ℕ) n, (1 / 2 - Int.fract (α * k))
        ∀ c : ℝ, Tendsto (fun (n : ℕ) ↦ (volume { α | α ∈ Ioo (0 : ℝ) 1 ∧ f α n ≤ c }).toReal)
          atTop (𝓝 (g c))

end S20261014_92_aux

open S20261014_92_aux in
/-- 表述 #20261014-92。

For any $0<\alpha<1$, let $f(\alpha,n)=\frac{1}{\log n}\sum_{1\leq k\leq n}(\tfrac{1}{2}-
\{ \alpha k\})$. Does $f(\alpha,n)$ have an asymptotic distribution function?

In other words, is there a non-decreasing function $g$ such that $g(-\infty)=0$, $g(\infty)=1$,
and $\lim_{n\to \infty}\lvert \{ \alpha\in (0,1): f(\alpha,n)\leq c\}\rvert=g(c)$? -/
def S20261014_92 : Prop :=
  statement

end Registry.ErdosProblem1002

end
