/-
Formalia · 条目 #20261014-67
猜想：Quasiperfect Numbers
内容许可：Apache-2.0（与原作相同）
原作版权：Copyright 2025 The Formal Conjectures Authors，Apache License 2.0

改编自 google-deepmind/formal-conjectures 仓库的 FormalConjectures/Wikipedia/QuasiperfectNumbers.lean。
改动：去掉 `answer(sorry) ↔`、`@[category …]` 等属性与 `sorry`，theorem 的参数改写成 `∀`，
只登记命题本身，写成 `def`。
-/
module

public import Mathlib.Algebra.GroupWithZero.Defs
public import Mathlib.Algebra.GroupWithZero.Nat
public import Mathlib.Data.FunLike.Basic
public import Mathlib.NumberTheory.ArithmeticFunction.Defs
public import Mathlib.NumberTheory.ArithmeticFunction.Misc

@[expose] public section

namespace Registry.QuasiperfectNumbers

namespace S20261014_67_aux

open Nat

open scoped ArithmeticFunction.sigma

def Quasiperfect (n : ℕ) : Prop :=
  σ 1 n = 2 * n + 1

end S20261014_67_aux

open S20261014_67_aux in
/-- 表述 #20261014-67。

**Quasiperfect Numbers Conjecture.**
Do quasiperfect numbers exist? -/
def S20261014_67 : Prop :=
  ∃ n, Quasiperfect n

end Registry.QuasiperfectNumbers

end
