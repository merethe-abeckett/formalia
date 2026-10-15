/-
Formalia · 条目 #20261014-60
猜想：Mean value problem
内容许可：Apache-2.0（与原作相同）
原作版权：Copyright 2025 The Formal Conjectures Authors，Apache License 2.0

改编自 google-deepmind/formal-conjectures 仓库的 FormalConjectures/Wikipedia/MeanValueProblem.lean。
改动：去掉 `answer(sorry) ↔`、`@[category …]` 等属性与 `sorry`，theorem 的参数改写成 `∀`，
只登记命题本身，写成 `def`。
-/
module

public import Mathlib.Algebra.Group.Defs
public import Mathlib.Algebra.Module.Defs
public import Mathlib.Algebra.Module.LinearMap.Defs
public import Mathlib.Algebra.Order.Monoid.Unbundled.WithTop
public import Mathlib.Algebra.Polynomial.Basic
public import Mathlib.Algebra.Polynomial.Degree.Defs
public import Mathlib.Algebra.Polynomial.Derivative
public import Mathlib.Algebra.Polynomial.Eval.Defs
public import Mathlib.Algebra.Ring.Defs
public import Mathlib.Algebra.Ring.Hom.Defs
public import Mathlib.Analysis.Complex.Norm
public import Mathlib.Analysis.Normed.Group.Defs
public import Mathlib.Data.Complex.Basic
public import Mathlib.Data.FunLike.Basic
public import Mathlib.Data.Nat.Basic
public import Mathlib.Data.Nat.Cast.Defs
public import Mathlib.Data.Real.Basic
public import Mathlib.Order.Defs.PartialOrder
public import Mathlib.Order.TypeTags
public import Mathlib.Order.WithBot

@[expose] public section

namespace Registry.MeanValueProblem

/-- 表述 #20261014-60。

Given a complex polynomial $p$ of degree $d ≥ 2$ and a complex number $z$
there is a critical point $c$ of $p$, such that $|p(z)-p(c)|/|z-c| ≤ |p'(z)|$. -/
def S20261014_60 : Prop :=
  ∀ (p : Polynomial ℂ) (hp : 2 ≤ p.degree) (z : ℂ) (K : ℝ), ∃ c : ℂ, p.derivative.eval c = 0 ∧
        ‖p.eval z - p.eval c‖ / ‖z - c‖ ≤ ‖p.derivative.eval z‖

end Registry.MeanValueProblem

end
