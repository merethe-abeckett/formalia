/-
Formalia · 条目 #20261014-34
猜想：Euler's sum of powers conjecture
内容许可：Apache-2.0（与原作相同）
原作版权：Copyright 2025 The Formal Conjectures Authors，Apache License 2.0

改编自 google-deepmind/formal-conjectures 仓库的 FormalConjectures/Wikipedia/EulerSumOfPowers.lean。
改动：去掉 `answer(sorry) ↔`、`@[category …]` 等属性与 `sorry`，theorem 的参数改写成 `∀`，
只登记命题本身，写成 `def`。
-/
module

public import Mathlib.Algebra.BigOperators.Group.Finset.Defs
public import Mathlib.Algebra.Group.Defs
public import Mathlib.Algebra.Group.Nat.Defs
public import Mathlib.Data.Fintype.Basic
public import Mathlib.Data.Fintype.Defs

@[expose] public section

namespace Registry.EulerSumOfPowersConjecture

/-- 表述 #20261014-34。

Euler's sum of powers conjecture states that for integers $n > 1$ and $k > 1$,
if the sum of $n$ positive integers each raised to the $k$-th power equals another integer
raised to the $k$-th power, then $n ≥ k$.

The conjecture is known to be false for $k = 4$ and $k = 5$,
but remains open for $k ≥ 6$. -/
def S20261014_34 : Prop :=
  ∀ (n k b : ℕ) (hn : 1 < n) (hk : 5 < k) (a : Fin n → ℕ)
      (ha : ∀ i, a i > 0) (hsum : ∑ i, (a i) ^ k = b ^ k), k ≤ n

end Registry.EulerSumOfPowersConjecture

end
