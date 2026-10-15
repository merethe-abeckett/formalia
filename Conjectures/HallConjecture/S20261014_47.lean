/-
Formalia · 条目 #20261014-47
猜想：Hall's conjecture
内容许可：Apache-2.0（与原作相同）
原作版权：Copyright 2025 The Formal Conjectures Authors，Apache License 2.0

改编自 google-deepmind/formal-conjectures 仓库的 FormalConjectures/Wikipedia/Hall.lean。
改动：去掉 `answer(sorry) ↔`、`@[category …]` 等属性与 `sorry`，theorem 的参数改写成 `∀`，
只登记命题本身，写成 `def`。
-/
module

public import Mathlib.Algebra.Group.Defs
public import Mathlib.Algebra.Group.Int.Defs
public import Mathlib.Algebra.Order.Group.Unbundled.Abs
public import Mathlib.Analysis.SpecialFunctions.Pow.Real
public import Mathlib.Data.Nat.Cast.Defs
public import Mathlib.Data.Real.Basic
public import Mathlib.Order.Lattice

@[expose] public section

namespace Registry.HallConjecture

namespace S20261014_47_aux

open Real

def HallIneq (C : ℝ) (e : ℝ) : Prop :=
  ∀ x y : ℤ, y ^ 2 ≠ x ^ 3 → |y ^ 2 - x ^ 3| > C * (|x| : ℝ) ^ e

def HallConjectureExp (e : ℝ) : Prop := ∃ C : ℝ, C > 0 ∧ HallIneq C e

end S20261014_47_aux

open S20261014_47_aux in
/-- 表述 #20261014-47。

Original Hall's conjecture with exponent $1/2$. -/
def S20261014_47 : Prop :=
  HallConjectureExp 2⁻¹

end Registry.HallConjecture

end
