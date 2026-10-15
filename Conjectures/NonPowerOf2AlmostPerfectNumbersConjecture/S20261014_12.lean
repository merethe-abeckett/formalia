/-
Formalia · 条目 #20261014-12
猜想：Non-Power-of-2 Almost Perfect Numbers Conjecture
内容许可：Apache-2.0（与原作相同）
原作版权：Copyright 2025 The Formal Conjectures Authors，Apache License 2.0

改编自 google-deepmind/formal-conjectures 仓库的 FormalConjectures/Wikipedia/AlmostPerfectNumbers.lean。
改动：去掉 `answer(sorry) ↔`、`@[category …]` 等属性与 `sorry`，theorem 的参数改写成 `∀`，
只登记命题本身，写成 `def`。
-/
module

public import Mathlib.Algebra.Group.Defs
public import Mathlib.Algebra.Group.Nat.Defs
public import Mathlib.Algebra.GroupWithZero.Defs
public import Mathlib.Algebra.GroupWithZero.Nat
public import Mathlib.Data.FunLike.Basic
public import Mathlib.NumberTheory.ArithmeticFunction.Defs
public import Mathlib.NumberTheory.ArithmeticFunction.Misc

@[expose] public section

namespace Registry.NonPowerOf2AlmostPerfectNumbersConjecture

namespace S20261014_12_aux

open Nat

open scoped ArithmeticFunction.sigma

def AlmostPerfect (n : ℕ) : Prop :=
  1 + σ 1 n = 2 * n

end S20261014_12_aux

open S20261014_12_aux in
/-- 表述 #20261014-12。

**Non-Power-of-2 Almost Perfect Numbers Conjecture.**
Does there exist an almost perfect number that is not a power of 2? -/
def S20261014_12 : Prop :=
  ∃ n : ℕ, AlmostPerfect n ∧ ¬ ∃ k : ℕ, n = 2^k

end Registry.NonPowerOf2AlmostPerfectNumbersConjecture

end
