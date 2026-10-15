/-
Formalia · 条目 #20261014-33
猜想：Open questions regarding the existence of Euler bricks
内容许可：Apache-2.0（与原作相同）
原作版权：Copyright 2025 The Formal Conjectures Authors，Apache License 2.0

改编自 google-deepmind/formal-conjectures 仓库的 FormalConjectures/Wikipedia/EulerBrick.lean。
改动：去掉 `answer(sorry) ↔`、`@[category …]` 等属性与 `sorry`，theorem 的参数改写成 `∀`，
只登记命题本身，写成 `def`。
-/
module

public import Mathlib.Algebra.Group.Defs
public import Mathlib.Algebra.Group.Even
public import Mathlib.Data.PNat.Basic
public import Mathlib.Data.PNat.Notation

@[expose] public section

namespace Registry.OpenQuestionsRegardingTheExistenceOfEulerBricks

namespace S20261014_33_aux

def IsEulerBrick (a b c : ℕ+) : Prop :=
  IsSquare (a^2 + b^2) ∧ IsSquare (a^2 + c^2) ∧ IsSquare (b^2 + c^2)

def IsPerfectCuboid (a b c : ℕ+) : Prop :=
  IsEulerBrick a b c ∧ IsSquare (a^2 + b^2 + c^2)

end S20261014_33_aux

open S20261014_33_aux in
/-- 表述 #20261014-33。

Is there a perfect Euler brick? -/
def S20261014_33 : Prop :=
  ∃ a b c : ℕ+, IsPerfectCuboid a b c

end Registry.OpenQuestionsRegardingTheExistenceOfEulerBricks

end
