/-
Formalia · 条目 #20261014-17
猜想：Betrothed numbers
内容许可：Apache-2.0（与原作相同）
原作版权：Copyright 2025 The Formal Conjectures Authors，Apache License 2.0

改编自 google-deepmind/formal-conjectures 仓库的 FormalConjectures/Wikipedia/BetrothedNumbers.lean。
改动：去掉 `answer(sorry) ↔`、`@[category …]` 等属性与 `sorry`，theorem 的参数改写成 `∀`，
只登记命题本身，写成 `def`。
-/
module

public import Mathlib.Algebra.Group.Even
public import Mathlib.Algebra.GroupWithZero.Defs
public import Mathlib.Algebra.GroupWithZero.Nat
public import Mathlib.Data.FunLike.Basic
public import Mathlib.NumberTheory.ArithmeticFunction.Defs
public import Mathlib.NumberTheory.ArithmeticFunction.Misc

@[expose] public section

namespace Registry.BetrothedNumbers

namespace S20261014_17_aux

open scoped ArithmeticFunction.sigma

structure IsBetrothed (m n : ℕ) : Prop where
  left : σ 1 m = m + n + 1
  right : σ 1 n = m + n + 1

end S20261014_17_aux

open S20261014_17_aux in
/-- 表述 #20261014-17。

**Same parity betrothed numbers conjecture.**
Do there exist betrothed numbers $(m, n)$ where both have the same parity
(both even or both odd)?

All known betrothed pairs consist of one even and one odd number.

The requirement $m \neq n$ is part of the question: $\mathrm{IsBetrothed}\ n\ n$ says
$\sigma(n) = 2n + 1$, i.e. that $n$ is quasiperfect, which is the separate open problem
`QuasiperfectNumbers.exists_quasiperfect`. -/
def S20261014_17 : Prop :=
  ∃ m n : ℕ, m ≠ n ∧ IsBetrothed m n ∧ (Even m ↔ Even n)

end Registry.BetrothedNumbers

end
