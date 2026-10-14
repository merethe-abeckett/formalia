/-
Formalia · 条目 #20261014-28
猜想：Dickson's conjecture
内容许可：Apache-2.0（与原作相同）
原作版权：Copyright 2025 The Formal Conjectures Authors，Apache License 2.0

改编自 google-deepmind/formal-conjectures 仓库的 FormalConjectures/Wikipedia/Dickson.lean。
改动：去掉 `answer(sorry) ↔`、`@[category …]` 等属性与 `sorry`，theorem 的参数改写成 `∀`，
只登记命题本身，写成 `def`。
-/
module

public import Mathlib.Algebra.Polynomial.Basic
public import Mathlib.Data.Finite.Defs
public import Mathlib.Data.Nat.Prime.Defs
public import Mathlib.Data.Set.CoeSort
public import Mathlib.Data.Set.Defs

@[expose] public section

namespace Registry.DicksonConjecture

namespace S20261014_28_aux

open Polynomial

end S20261014_28_aux

open S20261014_28_aux in
/-- 表述 #20261014-28。

**The generalized twin-prime conjecture**
For any positive integer $k$ there are infinitely many primes $p$ such that $p + 2k$ is prime. -/
def S20261014_28 : Prop :=
  ∀ (k : ℕ) (hk : 0 < k), Infinite {p : ℕ | p.Prime ∧ (p + 2 * k).Prime}

end Registry.DicksonConjecture

end
