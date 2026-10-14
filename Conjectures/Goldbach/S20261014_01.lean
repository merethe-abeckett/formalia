/-
Formalia · 条目 #20261014-01
猜想：哥德巴赫猜想
内容许可：Apache-2.0（与原作相同）
原作版权：Copyright 2025 The Formal Conjectures Authors，Apache License 2.0

改编自 google-deepmind/formal-conjectures 仓库的
FormalConjectures/Wikipedia/GoldbachConjecture.lean。改动：把环论的 `Prime`
换成 `Nat.Prime`；原文中该命题出现在 `answer(sorry) ↔ ...` 的右侧，这里只登记
命题本身，写成 `def`，因此文件中不含 sorry。（最初误标为原创，2026-10-14 更正。）
-/
module

public import Mathlib.Data.Nat.Prime.Defs
public import Mathlib.Algebra.Group.Even

@[expose] public section

namespace Registry.Goldbach

/-- 表述 #20261014-01。

每个大于 2 的偶自然数都是两个素数之和，其中“素数”取 Mathlib 的 `Nat.Prime`。 -/
def S20261014_01 : Prop :=
  ∀ n : ℕ, 2 < n → Even n → ∃ p q : ℕ, Nat.Prime p ∧ Nat.Prime q ∧ n = p + q

end Registry.Goldbach

end
