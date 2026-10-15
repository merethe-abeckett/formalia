/-
Formalia · 条目 #20261014-81
猜想：The $\frac 1 3$–$\frac 2 3$ conjecture
内容许可：Apache-2.0（与原作相同）
原作版权：Copyright 2025 The Formal Conjectures Authors，Apache License 2.0

改编自 google-deepmind/formal-conjectures 仓库的 FormalConjectures/Wikipedia/conjecture_1_3_to_2_3.lean。
改动：去掉 `answer(sorry) ↔`、`@[category …]` 等属性与 `sorry`，theorem 的参数改写成 `∀`，
只登记命题本身，写成 `def`。
-/
module

public import Mathlib.Algebra.Order.Ring.Unbundled.Rat
public import Mathlib.Data.Finite.Defs
public import Mathlib.Data.FunLike.Basic
public import Mathlib.Data.Nat.Basic
public import Mathlib.Data.Set.Card
public import Mathlib.Data.Set.Defs
public import Mathlib.Data.Set.Operations
public import Mathlib.Order.Defs.PartialOrder
public import Mathlib.Order.Hom.Basic
public import Mathlib.Order.Interval.Set.Defs
public import Mathlib.SetTheory.Cardinal.Finite

@[expose] public section

namespace Registry.TheFrac13Frac23Conjecture

/-- 表述 #20261014-81。

Does every finite partially ordered set that is not totally ordered
contain two elements $x$ and $y$ such that the probability that
$x$ appears before $y$ in a random linear extension is between $\frac 1 3$ and $\frac 2 3$?

The set of all total order extensions is represented as order preserving
bijections $P$ of $1, ..., n$. -/
def S20261014_81 : Prop :=
  ∀ (P : Type) [Finite P] [PartialOrder P]
      (not_total : ¬ Std.Total (α := P) (· ≤ ·)) (total_ext : Set <| OrderHom P ℕ)
      (total_ext_def : ∀ σ, σ ∈ total_ext ↔ Set.range σ = Set.Icc 1 (Nat.card P)),
      ∃ x y : P, ({σ ∈ total_ext | σ x < σ y}.ncard / total_ext.ncard : ℚ)
        ∈ Set.Icc (1/3) (2/3)

end Registry.TheFrac13Frac23Conjecture

end
