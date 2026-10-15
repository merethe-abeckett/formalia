/-
Formalia · 条目 #20261014-61
猜想：Oppermann's Conjecture
内容许可：Apache-2.0（与原作相同）
原作版权：Copyright 2025 The Formal Conjectures Authors，Apache License 2.0

改编自 google-deepmind/formal-conjectures 仓库的 FormalConjectures/Wikipedia/Oppermann.lean。
改动：去掉 `answer(sorry) ↔`、`@[category …]` 等属性与 `sorry`，theorem 的参数改写成 `∀`，
只登记命题本身，写成 `def`。
-/
module

public import Mathlib.Order.Filter.Defs
public import Mathlib.Algebra.Group.Defs
public import Mathlib.Algebra.Group.Nat.Defs
public import Mathlib.Data.Finset.Defs
public import Mathlib.Data.Nat.Basic
public import Mathlib.Data.Nat.Prime.Defs
public import Mathlib.Data.SetLike.Basic
public import Mathlib.Order.Interval.Finset.Defs
public import Mathlib.Order.Interval.Finset.Nat

@[expose] public section

namespace Registry.OppermannConjecture

namespace S20261014_61_aux

open Finset Filter

def statement : Prop :=
  ∀ (x : ℕ) (hx : 2 ≤ x), ∃ p ∈ Ioo (x * (x - 1)) (x^2), p.Prime

end S20261014_61_aux

open S20261014_61_aux in
/-- 表述 #20261014-61。

For every integer $x \ge 2$ there exists a prime between $x(x-1)$ and $x^2$. -/
def S20261014_61 : Prop :=
  statement

end Registry.OppermannConjecture

end
