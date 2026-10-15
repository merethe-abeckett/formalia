/-
Formalia · 条目 #20261014-74
猜想：Solitary Numbers
内容许可：Apache-2.0（与原作相同）
原作版权：Copyright 2025 The Formal Conjectures Authors，Apache License 2.0

改编自 google-deepmind/formal-conjectures 仓库的 FormalConjectures/Wikipedia/SolitaryNumber.lean。
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

namespace Registry.SolitaryNumbers

namespace S20261014_74_aux

open ArithmeticFunction.sigma

def Friendly (m n : ℕ) : Prop := 0 < m ∧ 0 < n ∧ σ 1 m * n = σ 1 n * m

def IsSolitary (n : ℕ) : Prop := 0 < n ∧ ∀ m, Friendly m n → m = n

end S20261014_74_aux

open S20261014_74_aux in
/-- 表述 #20261014-74。

**Is 10 a solitary number?**  The smallest positive integer whose solitary status is
currently unresolved is $10$, with abundancy index $\sigma(10) / 10 = 9/5$. -/
def S20261014_74 : Prop :=
  IsSolitary 10

end Registry.SolitaryNumbers

end
