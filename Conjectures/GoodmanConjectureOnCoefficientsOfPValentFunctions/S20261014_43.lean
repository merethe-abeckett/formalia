/-
Formalia · 条目 #20261014-43
猜想：Goodman's conjecture on coefficients of $p$-valent functions
内容许可：Apache-2.0（与原作相同）
原作版权：Copyright 2025 The Formal Conjectures Authors，Apache License 2.0

改编自 google-deepmind/formal-conjectures 仓库的 FormalConjectures/Wikipedia/GoodmanConjecture.lean。
改动：去掉 `answer(sorry) ↔`、`@[category …]` 等属性与 `sorry`，theorem 的参数改写成 `∀`，
只登记命题本身，写成 `def`。
-/
module

public import Mathlib.Algebra.BigOperators.Group.Finset.Defs
public import Mathlib.Algebra.Group.Defs
public import Mathlib.Analysis.Analytic.Basic
public import Mathlib.Analysis.CStarAlgebra.Classes
public import Mathlib.Analysis.Calculus.IteratedDeriv.Defs
public import Mathlib.Analysis.Complex.Basic
public import Mathlib.Analysis.Complex.Norm
public import Mathlib.Analysis.Normed.Field.Basic
public import Mathlib.Analysis.Normed.Group.Defs
public import Mathlib.Analysis.Normed.Ring.Basic
public import Mathlib.Data.Complex.Basic
public import Mathlib.Data.ENat.Basic
public import Mathlib.Data.ENat.Defs
public import Mathlib.Data.Nat.Basic
public import Mathlib.Data.Nat.Cast.Defs
public import Mathlib.Data.Nat.Factorial.Basic
public import Mathlib.Data.Real.Basic
public import Mathlib.Data.Set.Card
public import Mathlib.Data.Set.Defs
public import Mathlib.Order.Interval.Finset.Defs
public import Mathlib.Order.Interval.Finset.Nat
public import Mathlib.Topology.MetricSpace.Pseudo.Defs

@[expose] public section

namespace Registry.GoodmanConjectureOnCoefficientsOfPValentFunctions

namespace S20261014_43_aux

open Complex Set

structure IsPValent (f : ℂ → ℂ) (p : ℕ) : Prop where
  one_le_p   : 1 ≤ p
  analyticOn : AnalyticOn ℂ f (Metric.ball 0 1)
  /-- Every value $w$ is attained at most $p$ times on the disk. -/
  atMost     : ∀ w : ℂ, {z ∈ Metric.ball 0 1 | f z = w}.encard ≤ p
  /-- Some value $w$ is attained exactly $p$ times on the disk. -/
  exactly    : ∃ w : ℂ, {z ∈ Metric.ball 0 1 | f z = w}.encard = p

noncomputable def coeff (f : ℂ → ℂ) (n : ℕ) : ℂ := iteratedDeriv n f 0 / n.factorial

structure IsNormalized (f : ℂ → ℂ) : Prop where
  map_zero   : f 0 = 0

noncomputable def goodmanBound (f : ℂ → ℂ) (p n : ℕ) : ℝ :=
  ∑ k ∈ Finset.Icc 1 p,
    (2 * k * (n + p).factorial : ℝ) /
      ((p - k).factorial * (p + k).factorial * (n - p - 1).factorial * ((n : ℝ) ^ 2 - k ^ 2)) *
      ‖coeff f k‖

end S20261014_43_aux

open S20261014_43_aux in
/-- 表述 #20261014-43。

**Goodman's conjecture.** For every $p$-valent normalised function $f$ on the unit disk and every
$n > p$, the $n$-th coefficient is bounded by the Goodman bound:
$$|b_n| \le \sum_{k=1}^{p} \frac{2k (n+p)!}{(p-k)!\,(p+k)!\,(n-p-1)!\,(n^2-k^2)} |b_k|.$$ -/
def S20261014_43 : Prop :=
  ∀ (f : ℂ → ℂ) (p n : ℕ) (hf : IsPValent f p)
      (hf' : IsNormalized f) (hn : p < n), ‖coeff f n‖ ≤ goodmanBound f p n

end Registry.GoodmanConjectureOnCoefficientsOfPValentFunctions

end
