/-
Formalia · 条目 #20261014-15
猜想：Beal conjecture
内容许可：Apache-2.0（与原作相同）
原作版权：Copyright 2025 The Formal Conjectures Authors，Apache License 2.0

改编自 google-deepmind/formal-conjectures 仓库的 FormalConjectures/Wikipedia/BealConjecture.lean。
改动：去掉 `answer(sorry) ↔`、`@[category …]` 等属性与 `sorry`，theorem 的参数改写成 `∀`，
只登记命题本身，写成 `def`。
-/
module

public import Mathlib.Algebra.GCDMonoid.Finset
public import Mathlib.Algebra.GCDMonoid.Nat
public import Mathlib.Algebra.Group.Defs
public import Mathlib.Algebra.Group.Nat.Defs
public import Mathlib.Algebra.GroupWithZero.Nat
public import Mathlib.Data.Finset.Defs
public import Mathlib.Data.Finset.Insert

@[expose] public section

namespace Registry.BealConjecture

namespace S20261014_15_aux

def bealConjecture : Prop := ∀ {A B C x y z : ℕ},
    A ≠ 0 → B ≠ 0 → C ≠ 0 → 2 < x → 2 < y → 2 < z →
    A^x + B^y = C^z → 1 < Finset.gcd {A, B, C} id

end S20261014_15_aux

open S20261014_15_aux in
/-- 表述 #20261014-15。

The **Beal Conjecture**: if we are given positive integers $A, B, C, x, y, z$ such that
$x, y, z > 2$ and $A^x + B^y = C^z$ then $A, B, C$ have a common divisor. -/
def S20261014_15 : Prop :=
  bealConjecture

end Registry.BealConjecture

end
