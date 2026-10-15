/-
Formalia · 条目 #20261014-69
猜想：Decimal Repunit Primes
内容许可：Apache-2.0（与原作相同）
原作版权：Copyright 2025 The Formal Conjectures Authors，Apache License 2.0

改编自 google-deepmind/formal-conjectures 仓库的 FormalConjectures/Wikipedia/RepunitPrime.lean。
改动：去掉 `answer(sorry) ↔`、`@[category …]` 等属性与 `sorry`，theorem 的参数改写成 `∀`，
只登记命题本身，写成 `def`。
-/
module

public import Mathlib.Algebra.BigOperators.Group.Finset.Defs
public import Mathlib.Algebra.Group.Defs
public import Mathlib.Algebra.Group.Nat.Defs
public import Mathlib.Data.Finite.Defs
public import Mathlib.Data.Finset.Range
public import Mathlib.Data.Nat.Prime.Defs
public import Mathlib.Data.Set.Defs

@[expose] public section

namespace Registry.DecimalRepunitPrimes

namespace S20261014_69_aux

def repunit10 (n : ℕ) : ℕ :=
  ∑ i ∈ Finset.range n, 10 ^ i

end S20261014_69_aux

open S20261014_69_aux in
/-- 表述 #20261014-69。

[Wikipedia's repunit article](https://en.wikipedia.org/wiki/Repunit#Decimal_repunit_primes)
states: "It has been conjectured that there are infinitely many repunit primes." -/
def S20261014_69 : Prop :=
  {n : ℕ | (repunit10 n).Prime}.Infinite

end Registry.DecimalRepunitPrimes

end
