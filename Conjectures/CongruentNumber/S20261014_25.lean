/-
Formalia · 条目 #20261014-25
猜想：Congruent Number
内容许可：Apache-2.0（与原作相同）
原作版权：Copyright 2025 The Formal Conjectures Authors，Apache License 2.0

改编自 google-deepmind/formal-conjectures 仓库的 FormalConjectures/Wikipedia/CongruentNumber.lean。
改动：去掉 `answer(sorry) ↔`、`@[category …]` 等属性与 `sorry`，theorem 的参数改写成 `∀`，
只登记命题本身，写成 `def`。
-/
module

public import Mathlib.Algebra.Group.Defs
public import Mathlib.Algebra.Group.Int.Defs
public import Mathlib.Algebra.Group.Nat.Defs
public import Mathlib.Algebra.Ring.Nat
public import Mathlib.Algebra.Ring.Parity
public import Mathlib.Algebra.Squarefree.Basic
public import Mathlib.Data.Rat.Defs
public import Mathlib.Data.Set.Card
public import Mathlib.Data.Set.Defs

@[expose] public section

namespace Registry.CongruentNumber

namespace S20261014_25_aux

def congruentNumber (n : ℕ) : Prop :=
  ∃ (a b c : ℚ), a ^ 2 + b ^ 2 = c ^ 2 ∧ n = (2⁻¹ : ℚ) * a * b

def A (n : ℕ) : Set (ℤ × ℤ × ℤ) := {(x, y, z) | n = 2 * x ^ 2 + y ^ 2 + 32 * z ^ 2}

def B (n : ℕ) : Set (ℤ × ℤ × ℤ) := {(x, y, z) | n = 2 * x ^ 2 + y ^ 2 + 8 * z ^ 2}

end S20261014_25_aux

open S20261014_25_aux in
/-- 表述 #20261014-25。

Tunnell's theorem (sufficient condition assuming BSD) for odd squarefree congruent numbers. -/
def S20261014_25 : Prop :=
  ∀ (n : ℕ) (hsqf : Squarefree n) (hodd : Odd n), 2 * (A n).ncard = (B n).ncard → congruentNumber n

end Registry.CongruentNumber

end
