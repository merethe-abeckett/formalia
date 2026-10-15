/-
Formalia · 条目 #20261014-20
猜想：Brocard's Conjecture
内容许可：Apache-2.0（与原作相同）
原作版权：Copyright 2025 The Formal Conjectures Authors，Apache License 2.0

改编自 google-deepmind/formal-conjectures 仓库的 FormalConjectures/Wikipedia/BrocardConjecture.lean。
改动：去掉 `answer(sorry) ↔`、`@[category …]` 等属性与 `sorry`，theorem 的参数改写成 `∀`，
只登记命题本身，写成 `def`。
-/
module

public import Mathlib.Data.Finset.Defs
public import Mathlib.Order.Filter.Defs
public import Mathlib.Algebra.Group.Defs
public import Mathlib.Algebra.Group.Nat.Defs
public import Mathlib.Data.Finset.Card
public import Mathlib.Data.Finset.Filter
public import Mathlib.Data.Nat.Basic
public import Mathlib.Data.Nat.Nth
public import Mathlib.Data.Nat.Prime.Defs
public import Mathlib.Order.Interval.Finset.Defs
public import Mathlib.Order.Interval.Finset.Nat

@[expose] public section

namespace Registry.BrocardConjecture

namespace S20261014_20_aux

open Finset Filter

def statement : Prop :=
  ∀ (n : ℕ) (hn : 1 ≤ n), letI prev := n.nth Nat.Prime;
      letI next := (n+1).nth Nat.Prime;
      4 ≤ ((Ioo (prev^2) (next^2)).filter Nat.Prime).card

end S20261014_20_aux

open S20261014_20_aux in
/-- 表述 #20261014-20。

**Brocard's Conjecture**
For every `n ≥ 2`, between the squares of the `n`-th and `(n+1)`-th primes,
there are at least four prime numbers. -/
def S20261014_20 : Prop :=
  statement

end Registry.BrocardConjecture

end
