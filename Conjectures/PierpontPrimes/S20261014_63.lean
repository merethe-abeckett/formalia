/-
Formalia · 条目 #20261014-63
猜想：Pierpont primes
内容许可：Apache-2.0（与原作相同）
原作版权：Copyright 2025 The Formal Conjectures Authors，Apache License 2.0

改编自 google-deepmind/formal-conjectures 仓库的 FormalConjectures/Wikipedia/PierpontPrime.lean。
改动：去掉 `answer(sorry) ↔`、`@[category …]` 等属性与 `sorry`，theorem 的参数改写成 `∀`，
只登记命题本身，写成 `def`。
-/
module

public import Mathlib.Algebra.Group.Defs
public import Mathlib.Algebra.Group.Nat.Defs
public import Mathlib.Data.Finite.Defs
public import Mathlib.Data.Nat.Prime.Defs
public import Mathlib.Data.Set.Defs

@[expose] public section

namespace Registry.PierpontPrimes

namespace S20261014_63_aux

def IsPierpontPrime (p : ℕ) : Prop :=
  p.Prime ∧ ∃ a b : ℕ, p = 2 ^ a * 3 ^ b + 1

end S20261014_63_aux

open S20261014_63_aux in
/-- 表述 #20261014-63。

There are infinitely many Pierpont primes. -/
def S20261014_63 : Prop :=
  Set.Infinite {p : ℕ | IsPierpontPrime p}

end Registry.PierpontPrimes

end
