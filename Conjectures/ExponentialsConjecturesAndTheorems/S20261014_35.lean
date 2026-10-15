/-
Formalia · 条目 #20261014-35
猜想：Exponentials conjectures and theorems
内容许可：Apache-2.0（与原作相同）
原作版权：Copyright 2025 The Formal Conjectures Authors，Apache License 2.0

改编自 google-deepmind/formal-conjectures 仓库的 FormalConjectures/Wikipedia/Exponentials.lean。
改动：去掉 `answer(sorry) ↔`、`@[category …]` 等属性与 `sorry`，theorem 的参数改写成 `∀`，
只登记命题本身，写成 `def`。
-/
module

public import Mathlib.Data.Complex.Basic
public import Mathlib.Algebra.Algebra.Rat
public import Mathlib.Algebra.Ring.Rat
public import Mathlib.Analysis.RCLike.Basic
public import Mathlib.Analysis.SpecialFunctions.Pow.Real
public import Mathlib.Data.Nat.Cast.Defs
public import Mathlib.Data.Real.Basic
public import Mathlib.NumberTheory.Real.Irrational
public import Mathlib.RingTheory.Algebraic.Defs

@[expose] public section

namespace Registry.ExponentialsConjecturesAndTheorems

namespace S20261014_35_aux

open Complex

end S20261014_35_aux

open S20261014_35_aux in
/-- 表述 #20261014-35。

The four exponential conjecture would imply that for any irrational number $t$,
at least one of the numbers $2^t$ and $3^t$ is transcendental. -/
def S20261014_35 : Prop :=
  ∀ (t : ℝ) (h : Irrational t), Transcendental ℚ (2 ^ t : ℝ) ∨ Transcendental ℚ (3 ^ t : ℝ)

end Registry.ExponentialsConjecturesAndTheorems

end
