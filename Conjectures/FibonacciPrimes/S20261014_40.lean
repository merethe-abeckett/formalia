/-
Formalia · 条目 #20261014-40
猜想：Fibonacci Primes
内容许可：Apache-2.0（与原作相同）
原作版权：Copyright 2025 The Formal Conjectures Authors，Apache License 2.0

改编自 google-deepmind/formal-conjectures 仓库的 FormalConjectures/Wikipedia/FibonacciPrimes.lean。
改动：去掉 `answer(sorry) ↔`、`@[category …]` 等属性与 `sorry`，theorem 的参数改写成 `∀`，
只登记命题本身，写成 `def`。
-/
module

public import Mathlib.Data.Finite.Defs
public import Mathlib.Data.Nat.Fib.Basic
public import Mathlib.Data.Nat.Prime.Defs
public import Mathlib.Data.Set.Defs

@[expose] public section

namespace Registry.FibonacciPrimes

/-- 表述 #20261014-40。

There are infinitely many Fibonacci primes, i.e., Fibonacci numbers that are prime
It is also a barrier to defining a benchmark from this paper:
https://arxiv.org/html/2505.13938v1 (see Figure 8). -/
def S20261014_40 : Prop :=
  {n : ℕ | (∃ m : ℕ, m.fib = n) ∧ n.Prime}.Infinite

end Registry.FibonacciPrimes

end
