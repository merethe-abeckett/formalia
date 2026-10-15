/-
Formalia · 条目 #20261014-75
猜想：(m,k)-perfect numbers
内容许可：Apache-2.0（与原作相同）
原作版权：Copyright 2025 The Formal Conjectures Authors，Apache License 2.0

改编自 google-deepmind/formal-conjectures 仓库的 FormalConjectures/Wikipedia/Superperfectnumbers.lean。
改动：去掉 `answer(sorry) ↔`、`@[category …]` 等属性与 `sorry`，theorem 的参数改写成 `∀`，
只登记命题本身，写成 `def`。
-/
module

public import Mathlib.Algebra.GroupWithZero.Defs
public import Mathlib.Algebra.GroupWithZero.Nat
public import Mathlib.Data.FunLike.Basic
public import Mathlib.Logic.Function.Iterate
public import Mathlib.NumberTheory.ArithmeticFunction.Defs
public import Mathlib.NumberTheory.ArithmeticFunction.Misc

@[expose] public section

namespace Registry.MKPerfectNumbers

namespace S20261014_75_aux

open ArithmeticFunction.sigma

def PerfectFor (n m k : ℕ) : Prop := 0 < n ∧ Nat.iterate (fun x => σ 1 x) m n = k * n

end S20261014_75_aux

open S20261014_75_aux in
/-- 表述 #20261014-75。

There does not exist a $(2,5)$-perfect number -/
def S20261014_75 : Prop :=
  ¬ ∃ n, PerfectFor n 2 5

end Registry.MKPerfectNumbers

end
