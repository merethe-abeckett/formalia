/-
Formalia · 条目 #20261014-16
猜想：Beck–Fiala theorem and conjecture
内容许可：Apache-2.0（与原作相同）
原作版权：Copyright 2025 The Formal Conjectures Authors，Apache License 2.0

改编自 google-deepmind/formal-conjectures 仓库的 FormalConjectures/Wikipedia/BeckFialaConjecture.lean。
改动：去掉 `answer(sorry) ↔`、`@[category …]` 等属性与 `sorry`，theorem 的参数改写成 `∀`，
只登记命题本身，写成 `def`。
-/
module

public import Mathlib.Algebra.BigOperators.Group.Finset.Defs
public import Mathlib.Algebra.Order.Group.Unbundled.Abs
public import Mathlib.Data.Finset.Card
public import Mathlib.Data.Finset.Defs
public import Mathlib.Data.Finset.Filter
public import Mathlib.Data.Fintype.Basic
public import Mathlib.Data.Fintype.Defs
public import Mathlib.Data.Real.Basic
public import Mathlib.Data.Real.Sqrt
public import Mathlib.Data.SetLike.Basic

@[expose] public section

namespace Registry.BeckFialaTheoremAndConjecture

/-- 表述 #20261014-16。

**The Beck–Fiala conjecture**

There exists a universal constant $C > 0$ such that every set system
$S_1, \dots, S_m \subseteq [n]$ of degree at most $t$ admits a colouring
$\chi \colon [n] \to \{-1, +1\}$ with
$\left|\sum_{j \in S_i} \chi(j)\right| \le C \sqrt{t}$ for every $i$. -/
def S20261014_16 : Prop :=
  ∃ C : ℝ, 0 < C ∧ ∀ (n m t : ℕ) (S : Fin m → Finset (Fin n)),
        (∀ j, (Finset.univ.filter fun i => j ∈ S i).card ≤ t) →
        ∃ χ : Fin n → ℝ, (∀ j, χ j = 1 ∨ χ j = -1) ∧
          ∀ i, |∑ j ∈ S i, χ j| ≤ C * Real.sqrt t

end Registry.BeckFialaTheoremAndConjecture

end
