/-
Formalia · 条目 #20261014-42
猜想：Convergence of the Flint Hills and Cookson Hills series
内容许可：Apache-2.0（与原作相同）
原作版权：Copyright 2025 The Formal Conjectures Authors，Apache License 2.0

改编自 google-deepmind/formal-conjectures 仓库的 FormalConjectures/Wikipedia/FlintCooksonHills.lean。
改动：去掉 `answer(sorry) ↔`、`@[category …]` 等属性与 `sorry`，theorem 的参数改写成 `∀`，
只登记命题本身，写成 `def`。
-/
module

public import Mathlib.Algebra.Group.Defs
public import Mathlib.Analysis.Complex.Trigonometric
public import Mathlib.Data.Real.Basic
public import Mathlib.Topology.Algebra.InfiniteSum.Defs
public import Mathlib.Topology.Algebra.InfiniteSum.SummationFilter
public import Mathlib.Topology.MetricSpace.Pseudo.Defs
public import Mathlib.Topology.UniformSpace.Defs

@[expose] public section

namespace Registry.ConvergenceOfTheFlintHillsAndCooksonHillsSeries

/-- 表述 #20261014-42。

The Flint Hills series summing $csc(n)^2 / n^3$ from $n=1$ to $\infty$ converges.
(Note that we 0-index the series below.) -/
def S20261014_42 : Prop :=
  Summable (fun n : ℕ =>
          1 / ((((n + 1) : ℝ)^3) * (Real.sin (n + 1)^2)))

end Registry.ConvergenceOfTheFlintHillsAndCooksonHillsSeries

end
