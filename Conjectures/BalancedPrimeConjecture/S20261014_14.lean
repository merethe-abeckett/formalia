/-
Formalia · 条目 #20261014-14
猜想：Balanced prime conjecture
内容许可：Apache-2.0（与原作相同）
原作版权：Copyright 2025 The Formal Conjectures Authors，Apache License 2.0

改编自 google-deepmind/formal-conjectures 仓库的 FormalConjectures/Wikipedia/BalancedPrimes.lean。
改动：去掉 `answer(sorry) ↔`、`@[category …]` 等属性与 `sorry`，theorem 的参数改写成 `∀`，
只登记命题本身，写成 `def`。
-/
module

public import Mathlib.Algebra.GroupWithZero.Nat
public import Mathlib.Algebra.Prime.Defs
public import Mathlib.Data.Finite.Defs
public import Mathlib.Data.Nat.Nth
public import Mathlib.Data.Set.Defs

@[expose] public section

namespace Registry.BalancedPrimeConjecture

/-- 表述 #20261014-14。

Let $p_k$ be the $k$-th prime number.
Are there infinitely many $n$ such that $(p_n + p_{n+2}) / 2$ is prime? -/
def S20261014_14 : Prop :=
  {n : ℕ | Prime ((Nat.nth Prime n + Nat.nth Prime (n + 2)) / 2)}.Infinite

end Registry.BalancedPrimeConjecture

end
