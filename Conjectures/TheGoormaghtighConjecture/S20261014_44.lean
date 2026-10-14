/-
Formalia · 条目 #20261014-44
猜想：The Goormaghtigh conjecture
内容许可：Apache-2.0（与原作相同）
原作版权：Copyright 2025 The Formal Conjectures Authors，Apache License 2.0

改编自 google-deepmind/formal-conjectures 仓库的 FormalConjectures/Wikipedia/Goormaghtigh.lean。
改动：去掉 `answer(sorry) ↔`、`@[category …]` 等属性与 `sorry`，theorem 的参数改写成 `∀`，
只登记命题本身，写成 `def`。
-/
module

public import Mathlib.Algebra.BigOperators.Group.Finset.Defs
public import Mathlib.Algebra.Group.Defs
public import Mathlib.Algebra.Group.Nat.Defs
public import Mathlib.Data.Finset.Range

@[expose] public section

namespace Registry.TheGoormaghtighConjecture

namespace S20261014_44_aux

def repunit (base digits : ℕ) : ℕ :=
  ∑ i ∈ Finset.range digits, base ^ i

def IsGoormaghtighNumber (N : ℕ) : Prop :=
  ∃ base₁ base₂ digits₁ digits₂ : ℕ,
    2 ≤ base₁ ∧ 2 ≤ base₂ ∧ base₁ ≠ base₂ ∧
      3 ≤ digits₁ ∧ 3 ≤ digits₂ ∧
        repunit base₁ digits₁ = N ∧ repunit base₂ digits₂ = N

end S20261014_44_aux

open S20261014_44_aux in
/-- 表述 #20261014-44。

The only Goormaghtigh numbers are $31$ and $8191$. -/
def S20261014_44 : Prop :=
  ∀ (N : ℕ) (hN : IsGoormaghtighNumber N), N = 31 ∨ N = 8191

end Registry.TheGoormaghtighConjecture

end
