/-
Formalia · 条目 #20261014-76
猜想：Taxicab numbers
内容许可：Apache-2.0（与原作相同）
原作版权：Copyright 2025 The Formal Conjectures Authors，Apache License 2.0

改编自 google-deepmind/formal-conjectures 仓库的 FormalConjectures/Wikipedia/Taxicab.lean。
改动：去掉 `answer(sorry) ↔`、`@[category …]` 等属性与 `sorry`，theorem 的参数改写成 `∀`，
只登记命题本身，写成 `def`。
-/
module

public import Mathlib.Algebra.BigOperators.Group.Multiset.Defs
public import Mathlib.Algebra.Group.Defs
public import Mathlib.Algebra.Group.Nat.Defs
public import Mathlib.Data.Finset.Card
public import Mathlib.Data.Finset.Defs
public import Mathlib.Data.Multiset.Defs
public import Mathlib.Data.Multiset.MapFold
public import Mathlib.Data.Set.Defs
public import Mathlib.Data.SetLike.Basic
public import Mathlib.Order.Bounds.Defs

@[expose] public section

namespace Registry.TaxicabNumbers

namespace S20261014_76_aux

def IsTaxicabFor' (k m n x : ℕ) : Prop :=
  ∃ S : Finset (Multiset ℕ), n ≤ S.card ∧
    ∀ L ∈ S, Multiset.card L = m ∧ 0 ∉ L ∧ (L.map (· ^ k)).sum = x

def IsTaxicabFor (k m n : ℕ) (x : ℕ) : Prop :=
  IsLeast { x : ℕ | IsTaxicabFor' k m n x } x

end S20261014_76_aux

open S20261014_76_aux in
/-- 表述 #20261014-76。

Taxicab number for $k=5$, $m=2$, and $n=2$ is not known.
Whether such a number exists is also not known. -/
def S20261014_76 : Prop :=
  ∃ x : ℕ, IsTaxicabFor 5 2 2 x

end Registry.TaxicabNumbers

end
