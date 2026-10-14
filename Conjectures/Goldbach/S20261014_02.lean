/-
Lean 表述登记库 · 条目 #20261014-02
猜想：哥德巴赫猜想
内容许可：Apache-2.0（与原作相同）
原作版权：Copyright 2025 The Formal Conjectures Authors，Apache License 2.0

改编自 google-deepmind/formal-conjectures 仓库的
FormalConjectures/Wikipedia/GoldbachConjecture.lean。改动：原文中该命题
出现在 `answer(sorry) ↔ ...` 的右侧；这里只登记命题本身，写成 `def`，因此文件中
不含 sorry。
-/
module

public import Mathlib.Algebra.Prime.Defs
public import Mathlib.Algebra.Ring.Nat
public import Mathlib.Algebra.Group.Even

@[expose] public section

namespace Registry.Goldbach

/-- 表述 #20261014-02。

形状与 #20261014-01 相同，但“素数”取 Mathlib 中一般环论意义上的 `Prime`，
在 `ℕ` 上特化，与 formal-conjectures 的写法一致。 -/
def S20261014_02 : Prop :=
  ∀ n : ℕ, 2 < n → Even n → ∃ p q : ℕ, Prime p ∧ Prime q ∧ n = p + q

end Registry.Goldbach

end
