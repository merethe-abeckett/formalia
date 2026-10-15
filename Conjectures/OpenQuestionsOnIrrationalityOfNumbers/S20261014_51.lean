/-
Formalia · 条目 #20261014-51
猜想：Open questions on irrationality of numbers
内容许可：Apache-2.0（与原作相同）
原作版权：Copyright 2025 The Formal Conjectures Authors，Apache License 2.0

改编自 google-deepmind/formal-conjectures 仓库的 FormalConjectures/Wikipedia/Irrational.lean。
改动：去掉 `answer(sorry) ↔`、`@[category …]` 等属性与 `sorry`，theorem 的参数改写成 `∀`，
只登记命题本身，写成 `def`。
-/
module

public import Mathlib.Analysis.SpecialFunctions.Pow.Real
public import Mathlib.Analysis.SpecialFunctions.Trigonometric.Basic
public import Mathlib.Data.Real.Basic
public import Mathlib.NumberTheory.Real.Irrational

@[expose] public section

namespace Registry.OpenQuestionsOnIrrationalityOfNumbers

namespace S20261014_51_aux

open Real

def statement : Prop :=
  Irrational (π ^ π)

end S20261014_51_aux

open S20261014_51_aux in
/-- 表述 #20261014-51。

Is $\pi ^ \pi$ irrational? -/
def S20261014_51 : Prop :=
  statement

end Registry.OpenQuestionsOnIrrationalityOfNumbers

end
