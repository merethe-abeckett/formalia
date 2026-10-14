/-
Formalia · 条目 #20261014-37
猜想：Feit-Thompson conjecture on primes
内容许可：Apache-2.0（与原作相同）
原作版权：Copyright 2025 The Formal Conjectures Authors，Apache License 2.0

改编自 google-deepmind/formal-conjectures 仓库的 FormalConjectures/Wikipedia/FeitThompsonPrimeConjecture.lean。
改动：去掉 `answer(sorry) ↔`、`@[category …]` 等属性与 `sorry`，theorem 的参数改写成 `∀`，
只登记命题本身，写成 `def`。
-/
module

public import Mathlib.Algebra.Group.Defs
public import Mathlib.Algebra.Group.Nat.Defs
public import Mathlib.Data.Nat.Prime.Defs

@[expose] public section

namespace Registry.FeitThompsonConjectureOnPrimes

/-- 表述 #20261014-37。

There are no distinct primes $p$ and $q$ such that $\frac{q^p - 1}{q - 1}$ divides $\frac{p^q - 1}{p - 1}$ -/
def S20261014_37 : Prop :=
  ∀ (p q : ℕ) (hp : p.Prime) (hq : q.Prime) (h : p < q), ¬ (q ^ p - 1) / (q - 1) ∣ (p ^ q - 1) / (p - 1)

end Registry.FeitThompsonConjectureOnPrimes

end
