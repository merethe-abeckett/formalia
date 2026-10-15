/-
Formalia · 条目 #20261014-70
猜想：Particular values of the Riemann zeta function
内容许可：Apache-2.0（与原作相同）
原作版权：Copyright 2025 The Formal Conjectures Authors，Apache License 2.0

改编自 google-deepmind/formal-conjectures 仓库的 FormalConjectures/Wikipedia/RiemannZetaValues.lean。
改动：去掉 `answer(sorry) ↔`、`@[category …]` 等属性与 `sorry`，theorem 的参数改写成 `∀`，
只登记命题本身，写成 `def`。
-/
module

public import Mathlib.Data.Complex.Basic
public import Mathlib.Data.Nat.Cast.Defs
public import Mathlib.Data.Real.Basic
public import Mathlib.NumberTheory.LSeries.RiemannZeta
public import Mathlib.NumberTheory.Real.Irrational

@[expose] public section

namespace Registry.ParticularValuesOfTheRiemannZetaFunction

/-- 表述 #20261014-70。

$\zeta(7)$ is irrational. -/
def S20261014_70 : Prop :=
  ∃ x, Irrational x ∧ riemannZeta 7 = x

end Registry.ParticularValuesOfTheRiemannZetaFunction

end
