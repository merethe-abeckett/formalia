/-
Formalia · 条目 #20261014-36
猜想：Factorial primes
内容许可：Apache-2.0（与原作相同）
原作版权：Copyright 2025 The Formal Conjectures Authors，Apache License 2.0

改编自 google-deepmind/formal-conjectures 仓库的 FormalConjectures/Wikipedia/FactorialPrime.lean。
改动：去掉 `answer(sorry) ↔`、`@[category …]` 等属性与 `sorry`，theorem 的参数改写成 `∀`，
只登记命题本身，写成 `def`。
-/
module

public import Mathlib.Data.Finite.Defs
public import Mathlib.Data.Nat.Factorial.Basic
public import Mathlib.Data.Nat.Prime.Defs
public import Mathlib.Data.Set.Defs

@[expose] public section

namespace Registry.FactorialPrimes

namespace S20261014_36_aux

def IsFactorialPrime (p : ℕ) : Prop :=
  p.Prime ∧ ∃ n : ℕ, p = n.factorial + 1 ∨ n.factorial = p + 1

end S20261014_36_aux

open S20261014_36_aux in
/-- 表述 #20261014-36。

There are infinitely many factorial primes. -/
def S20261014_36 : Prop :=
  Set.Infinite {p : ℕ | IsFactorialPrime p}

end Registry.FactorialPrimes

end
