/-
Formalia · 条目 #20261014-91
猜想：Erdős Problem 10
内容许可：Apache-2.0（与原作相同）
原作版权：Copyright 2025 The Formal Conjectures Authors，Apache License 2.0

改编自 google-deepmind/formal-conjectures 仓库的 FormalConjectures/ErdosProblems/10.lean。
改动：去掉 `answer(sorry) ↔`、`@[category …]` 等属性与 `sorry`，theorem 的参数改写成 `∀`，
只登记命题本身，写成 `def`。
-/
module

public import Mathlib.Order.Filter.Defs
public import Mathlib.Algebra.BigOperators.Group.Multiset.Defs
public import Mathlib.Algebra.Group.Defs
public import Mathlib.Algebra.Group.Even
public import Mathlib.Algebra.Group.Nat.Defs
public import Mathlib.Algebra.Ring.Nat
public import Mathlib.Algebra.Ring.Parity
public import Mathlib.Data.Multiset.Defs
public import Mathlib.Data.Multiset.MapFold
public import Mathlib.Data.Nat.Prime.Defs
public import Mathlib.Data.Set.Defs

@[expose] public section

namespace Registry.ErdosProblem10

namespace S20261014_91_aux

open Filter

abbrev sumPrimeAndTwoPows (k : ℕ) : Set ℕ :=
  { p + (pows.map (2 ^ ·)).sum | (p : ℕ) (pows : Multiset ℕ) (_ : p.Prime)
    (_ : pows.card ≤ k)}

end S20261014_91_aux

open S20261014_91_aux in
/-- 表述 #20261014-91。

Granville and Soundararajan [GrSo98] have conjectured that at most $3$
powers of $2$ suffice for all odd integers, and hence at most $4$ powers of $2$
suffice for all even integers.

Ref: Granville, A. and Soundararajan, K., _A Binary Additive Problem of Erdős and the Order of $2$ mod $p^2$_ -/
def S20261014_91 : Prop :=
  {n : ℕ | Odd n ∧ 1 < n} ⊆ sumPrimeAndTwoPows 3 ∧
        {n : ℕ | Even n ∧ n ≠ 0} ⊆ sumPrimeAndTwoPows 4

end Registry.ErdosProblem10

end
