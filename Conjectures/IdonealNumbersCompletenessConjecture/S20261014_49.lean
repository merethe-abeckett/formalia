/-
Formalia · 条目 #20261014-49
猜想：Idoneal numbers completeness conjecture
内容许可：Apache-2.0（与原作相同）
原作版权：Copyright 2025 The Formal Conjectures Authors，Apache License 2.0

改编自 google-deepmind/formal-conjectures 仓库的 FormalConjectures/Wikipedia/IdonealCompleteness.lean。
改动：去掉 `answer(sorry) ↔`、`@[category …]` 等属性与 `sorry`，theorem 的参数改写成 `∀`，
只登记命题本身，写成 `def`。
-/
module

public import Mathlib.Data.Finset.Defs
public import Mathlib.Data.Finset.Insert
public import Mathlib.Data.SetLike.Basic

@[expose] public section

namespace Registry.IdonealNumbersCompletenessConjecture

namespace S20261014_49_aux

def IsIdoneal (n : ℕ) : Prop :=
  0 < n ∧
    ¬ ∃ a b c : ℕ,
      0 < a ∧ a < b ∧ b < c ∧ n = a * b + b * c + a * c

def knownIdonealNumbers : Finset ℕ :=
  {1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 12, 13, 15, 16, 18, 21, 22, 24, 25, 28,
   30, 33, 37, 40, 42, 45, 48, 57, 58, 60, 70, 72, 78, 85, 88, 93, 102, 105,
   112, 120, 130, 133, 165, 168, 177, 190, 210, 232, 240, 253, 273, 280, 312,
   330, 345, 357, 385, 408, 462, 520, 760, 840, 1320, 1365, 1848}

end S20261014_49_aux

open S20261014_49_aux in
/-- 表述 #20261014-49。

Idoneal numbers completeness conjecture. -/
def S20261014_49 : Prop :=
  ∀ n : ℕ, IsIdoneal n → n ∈ knownIdonealNumbers

end Registry.IdonealNumbersCompletenessConjecture

end
