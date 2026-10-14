/-
Formalia · 条目 #20261014-82
猜想：The Curling Number Conjecture
内容许可：Apache-2.0（与原作相同）
原作版权：Copyright 2025 The Formal Conjectures Authors，Apache License 2.0

改编自 google-deepmind/formal-conjectures 仓库的 FormalConjectures/Arxiv/0912.2382/CurlingNumberConjecture.lean。
改动：去掉 `answer(sorry) ↔`、`@[category …]` 等属性与 `sorry`，theorem 的参数改写成 `∀`，
只登记命题本身，写成 `def`。
-/
module

public import Mathlib.Data.Nat.Lattice
public import Mathlib.Data.Set.Defs
public import Mathlib.Order.SetNotation

@[expose] public section

namespace Registry.TheCurlingNumberConjecture

namespace S20261014_82_aux

noncomputable def k (S : List ℤ) : ℕ :=
  sSup {k : ℕ | ∃ X Y : List ℤ, Y ≠ [] ∧ S = X ++ (List.replicate k Y).flatten}

noncomputable def S (S₀ : List ℤ) (n : ℕ) : List ℤ :=
  match n with
  | 0 => S₀
  | n + 1 => (S S₀ n) ++ [Int.ofNat (k (S S₀ n))]

end S20261014_82_aux

open S20261014_82_aux in
/-- 表述 #20261014-82。

Starting from any nonempty finite integer sequence, repeatedly appending its curling number
eventually gives a sequence with curling number $1$ [Chaffin and Sloane, Conjecture 1]. -/
def S20261014_82 : Prop :=
  ∀ (S₀ : List ℤ) (h : S₀ ≠ []), ∃ m, k (S S₀ m) = 1

end Registry.TheCurlingNumberConjecture

end
