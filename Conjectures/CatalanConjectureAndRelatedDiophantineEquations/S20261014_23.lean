/-
Formalia · 条目 #20261014-23
猜想：Catalan's conjecture and related Diophantine equations
内容许可：Apache-2.0（与原作相同）
原作版权：Copyright 2025 The Formal Conjectures Authors，Apache License 2.0

改编自 google-deepmind/formal-conjectures 仓库的 FormalConjectures/Wikipedia/Catalan.lean。
改动：去掉 `answer(sorry) ↔`、`@[category …]` 等属性与 `sorry`，theorem 的参数改写成 `∀`，
只登记命题本身，写成 `def`。
-/
module

public import Mathlib.Algebra.Group.Defs
public import Mathlib.Algebra.Group.Nat.Defs
public import Mathlib.Data.Finite.Defs
public import Mathlib.Data.Set.Defs

@[expose] public section

namespace Registry.CatalanConjectureAndRelatedDiophantineEquations

/-- 表述 #20261014-23。

For positive integers a, b, and c, there are only finitely many positive solutions (x, y, m, n) to the
equation $ax^n - by^m = c$ where $(m, n) \neq (2, 2)$ and $x, y > 1$. -/
def S20261014_23 : Prop :=
  ∀ (a b c : ℕ) (ha : 0 < a) (hb : 0 < b) (hc : 0 < c), { (x, y, m, n) : (ℕ × ℕ × ℕ × ℕ) |
        1 < x ∧ 1 < y ∧ 1 < m ∧ 1 < n ∧ (m, n) ≠ (2, 2) ∧
        a * x^n - b * y^m = c }.Finite

end Registry.CatalanConjectureAndRelatedDiophantineEquations

end
