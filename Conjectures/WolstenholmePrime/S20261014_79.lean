/-
Formalia · 条目 #20261014-79
猜想：Wolstenholme Prime
内容许可：Apache-2.0（与原作相同）
原作版权：Copyright 2025 The Formal Conjectures Authors，Apache License 2.0

改编自 google-deepmind/formal-conjectures 仓库的 FormalConjectures/Wikipedia/WolstenholmePrime.lean。
改动：去掉 `answer(sorry) ↔`、`@[category …]` 等属性与 `sorry`，theorem 的参数改写成 `∀`，
只登记命题本身，写成 `def`。
-/
module

public import Mathlib.Algebra.Group.Defs
public import Mathlib.Algebra.Group.Nat.Defs
public import Mathlib.Data.Finite.Defs
public import Mathlib.Data.Nat.Choose.Basic
public import Mathlib.Data.Nat.ModEq
public import Mathlib.Data.Nat.Prime.Defs
public import Mathlib.Data.Set.Defs

@[expose] public section

namespace Registry.WolstenholmePrime

namespace S20261014_79_aux

def IsWolstenholmePrime (p : ℕ) : Prop :=
  p > 7 ∧ p.Prime ∧ (2 * p - 1).choose (p - 1) ≡ 1 [MOD p ^ 4]

end S20261014_79_aux

open S20261014_79_aux in
/-- 表述 #20261014-79。

It is conjectured that there are infinitely many Wolstenholme primes.

*Reference:* [Wikipedia](https://en.wikipedia.org/wiki/Wolstenholme_prime#Expected_number_of_Wolstenholme_primes) -/
def S20261014_79 : Prop :=
  {p : ℕ | IsWolstenholmePrime p}.Infinite

end Registry.WolstenholmePrime

end
