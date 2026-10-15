/-
Formalia · 条目 #20261014-71
猜想：Rudin's conjecture on squares in arithmetic progressions
内容许可：Apache-2.0（与原作相同）
原作版权：Copyright 2025 The Formal Conjectures Authors，Apache License 2.0

改编自 google-deepmind/formal-conjectures 仓库的 FormalConjectures/Wikipedia/RudinsConjecture.lean。
改动：去掉 `answer(sorry) ↔`、`@[category …]` 等属性与 `sorry`，theorem 的参数改写成 `∀`，
只登记命题本身，写成 `def`。
-/
module

public import Mathlib.Analysis.Asymptotics.Defs
public import Mathlib.Data.Real.Basic
public import Mathlib.Order.Filter.Defs
public import Mathlib.Algebra.Group.Even
public import Mathlib.Data.Nat.Lattice
public import Mathlib.Data.Set.Card
public import Mathlib.Data.Set.Defs
public import Mathlib.Order.SetNotation

@[expose] public section

namespace Registry.RudinConjectureOnSquaresInArithmeticProgressions

namespace S20261014_71_aux

open Filter Asymptotics Real

noncomputable abbrev Q (N q a : ℕ) : ℕ := {n : ℕ | n < N ∧ IsSquare (q * n + a)}.ncard

def IsNontrivial (q a : ℕ) : Prop :=
  1 ≤ q ∧ 1 ≤ a ∧ Nat.Coprime q a ∧ (q, a) ≠ (1, 1)

noncomputable def Qmax (N : ℕ) : ℕ :=
  sSup {m : ℕ | ∃ q a : ℕ, IsNontrivial q a ∧ Q N q a = m}

end S20261014_71_aux

open S20261014_71_aux in
/-- 表述 #20261014-71。

A stronger form of Rudin's conjecture: for every $N \ge 6$, the arithmetic progression
$24 n + 1$ attains the maximum $Q(N)$. -/
def S20261014_71 : Prop :=
  ∀ (N : ℕ) (hN : 6 ≤ N), Q N 24 1 = Qmax N

end Registry.RudinConjectureOnSquaresInArithmeticProgressions

end
