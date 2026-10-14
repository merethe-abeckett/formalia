/-
Formalia · 条目 #20261014-58
猜想：Magic Squares
内容许可：Apache-2.0（与原作相同）
原作版权：Copyright 2025 The Formal Conjectures Authors，Apache License 2.0

改编自 google-deepmind/formal-conjectures 仓库的 FormalConjectures/Wikipedia/MagicSquares.lean。
改动：去掉 `answer(sorry) ↔`、`@[category …]` 等属性与 `sorry`，theorem 的参数改写成 `∀`，
只登记命题本身，写成 `def`。
-/
module

public import Mathlib.Algebra.BigOperators.Group.Finset.Defs
public import Mathlib.Algebra.Group.Even
public import Mathlib.Algebra.Group.Nat.Defs
public import Mathlib.Data.Fintype.Basic
public import Mathlib.Data.Fintype.Defs
public import Mathlib.Logic.Function.Basic

@[expose] public section

namespace Registry.MagicSquares

/-- 表述 #20261014-58。

Does there exist a $3 \times 3$ matrix such that every entry is a distinct square,
and all rows, columns, and diagonals add up to the same value?

0 is excluded, as a Magic Square of Squares with 0 and 8 distinct squares is know is knownn.
See [Magic Square of Squares](https://static.nsta.org/pdfs/QuantumV6N3.pdf) -/
def S20261014_58 : Prop :=
  ∃ m : Fin 3 → Fin 3 → ℕ, ∃ t : ℕ,
         m.Injective2 ∧
         (∀ i j, 0 < (m i j) ∧ IsSquare (m i j)) ∧
         (∀ i, ∑ j, m i j = t) ∧
         (∀ j, ∑ i, m i j = t) ∧
         m 0 0 + m 1 1 + m 2 2 = t ∧
         m 0 2 + m 1 1 + m 2 0 = t

end Registry.MagicSquares

end
