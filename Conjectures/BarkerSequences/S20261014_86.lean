/-
Formalia · 条目 #20261014-86
猜想：Barker sequences
内容许可：Apache-2.0（与原作相同）
原作版权：Copyright 2025 The Formal Conjectures Authors，Apache License 2.0

改编自 google-deepmind/formal-conjectures 仓库的 FormalConjectures/Arxiv/2104.00502/BarkerSequence.lean。
改动：去掉 `answer(sorry) ↔`、`@[category …]` 等属性与 `sorry`，theorem 的参数改写成 `∀`，
只登记命题本身，写成 `def`。
-/
module

public import Mathlib.Algebra.Group.Int.Defs
public import Mathlib.Algebra.GroupWithZero.Defs
public import Mathlib.Algebra.Order.Group.Unbundled.Abs
public import Mathlib.Algebra.Ring.Defs
public import Mathlib.Analysis.Normed.Ring.Basic
public import Mathlib.Analysis.Normed.Ring.Lemmas
public import Mathlib.Order.Lattice

@[expose] public section

namespace Registry.BarkerSequences

namespace S20261014_86_aux

def aperiodicAutocorrelation (a : List ℤ) (k : ℕ) : ℤ :=
  (List.zipWith (· * ·) a (a.drop k)).sum

def IsBarkerSequence (a : List ℤ) : Prop :=
  (∀ x ∈ a, x = 1 ∨ x = -1) ∧
    ∀ k : ℕ, 0 < k → k < a.length → |aperiodicAutocorrelation a k| ≤ 1

end S20261014_86_aux

open S20261014_86_aux in
/-- 表述 #20261014-86。

Every Barker sequence has length at most $13$. -/
def S20261014_86 : Prop :=
  ∀ (a : List ℤ) (ha : IsBarkerSequence a), a.length ≤ 13

end Registry.BarkerSequences

end
