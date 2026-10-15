/-
Formalia · 条目 #20261014-77
猜想：Open questions on transcendence of numbers
内容许可：Apache-2.0（与原作相同）
原作版权：Copyright 2025 The Formal Conjectures Authors，Apache License 2.0

改编自 google-deepmind/formal-conjectures 仓库的 FormalConjectures/Wikipedia/Transcendental.lean。
改动：去掉 `answer(sorry) ↔`、`@[category …]` 等属性与 `sorry`，theorem 的参数改写成 `∀`，
只登记命题本身，写成 `def`。
-/
module

public import Mathlib.Algebra.Algebra.Rat
public import Mathlib.Algebra.Ring.Rat
public import Mathlib.Analysis.RCLike.Basic
public import Mathlib.Analysis.SpecialFunctions.Log.Basic
public import Mathlib.Data.Nat.Cast.Defs
public import Mathlib.Data.Real.Basic
public import Mathlib.RingTheory.Algebraic.Defs

@[expose] public section

namespace Registry.OpenQuestionsOnTranscendenceOfNumbers

namespace S20261014_77_aux

open Real

end S20261014_77_aux

open S20261014_77_aux in
/-- 表述 #20261014-77。

$\log(\log(2))$ is transcendental. -/
def S20261014_77 : Prop :=
  Transcendental ℚ ((2 : ℝ).log.log)

end Registry.OpenQuestionsOnTranscendenceOfNumbers

end
