/-
Formalia · 条目 #20261014-78
猜想：Wilson primes
内容许可：Apache-2.0（与原作相同）
原作版权：Copyright 2025 The Formal Conjectures Authors，Apache License 2.0

改编自 google-deepmind/formal-conjectures 仓库的 FormalConjectures/Wikipedia/WilsonPrime.lean。
改动：去掉 `answer(sorry) ↔`、`@[category …]` 等属性与 `sorry`，theorem 的参数改写成 `∀`，
只登记命题本身，写成 `def`。
-/
module

public import Mathlib.Algebra.Group.Defs
public import Mathlib.Algebra.Group.Nat.Defs
public import Mathlib.Data.Finite.Defs
public import Mathlib.Data.Nat.Factorial.Basic
public import Mathlib.Data.Nat.Prime.Defs
public import Mathlib.Data.Set.Defs

@[expose] public section

namespace Registry.WilsonPrimes

namespace S20261014_78_aux

def IsWilsonPrime (p : ℕ) : Prop :=
  p.Prime ∧ p ^ 2 ∣ (p - 1).factorial + 1

end S20261014_78_aux

open S20261014_78_aux in
/-- 表述 #20261014-78。

There are infinitely many Wilson primes. -/
def S20261014_78 : Prop :=
  Set.Infinite {p : ℕ | IsWilsonPrime p}

end Registry.WilsonPrimes

end
