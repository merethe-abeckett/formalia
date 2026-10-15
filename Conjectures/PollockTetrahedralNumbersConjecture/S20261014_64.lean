/-
Formalia · 条目 #20261014-64
猜想：Pollock's (tetrahedral numbers) conjecture
内容许可：Apache-2.0（与原作相同）
原作版权：Copyright 2025 The Formal Conjectures Authors，Apache License 2.0

改编自 google-deepmind/formal-conjectures 仓库的 FormalConjectures/Wikipedia/PollocksConjecture.lean。
改动：去掉 `answer(sorry) ↔`、`@[category …]` 等属性与 `sorry`，theorem 的参数改写成 `∀`，
只登记命题本身，写成 `def`。
-/
module

public import Mathlib.Algebra.BigOperators.Group.Finset.Defs
public import Mathlib.Algebra.Group.Nat.Defs
public import Mathlib.Data.Fintype.Basic
public import Mathlib.Data.Fintype.Defs

@[expose] public section

namespace Registry.PollockTetrahedralNumbersConjecture

namespace S20261014_64_aux

open scoped BigOperators

/-  ## Definitions -/

def tetrahedral (n : ℕ) : ℕ :=
  n * (n + 1) * (n + 2) / 6

/-  ## Auxiliary definition -/

end S20261014_64_aux

open S20261014_64_aux in
/-- 表述 #20261014-64。

Pollock's (tetrahedral numbers) conjecture:
every integer is the sum of at most $5$ tetrahedral numbers. -/
def S20261014_64 : Prop :=
  ∀ (N : ℕ), ∃ f : Fin 5 → ℕ, N = ∑ i, tetrahedral (f i)

end Registry.PollockTetrahedralNumbersConjecture

end
