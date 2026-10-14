/-
Formalia · 条目 #20261014-57
猜想：Lychrel numbers in base 10
内容许可：Apache-2.0（与原作相同）
原作版权：Copyright 2025 The Formal Conjectures Authors，Apache License 2.0

改编自 google-deepmind/formal-conjectures 仓库的 FormalConjectures/Wikipedia/LychrelNumbers.lean。
改动：去掉 `answer(sorry) ↔`、`@[category …]` 等属性与 `sorry`，theorem 的参数改写成 `∀`，
只登记命题本身，写成 `def`。
-/
module

public import Mathlib.Algebra.Ring.Nat
public import Mathlib.Data.Nat.Digits.Defs
public import Mathlib.Logic.Function.Iterate

@[expose] public section

namespace Registry.LychrelNumbersInBase10

namespace S20261014_57_aux

abbrev base : ℕ := 10

def rev10 (n : ℕ) : ℕ :=
  Nat.ofDigits base (Nat.digits base n).reverse

def IsPalindrome10 (n : ℕ) : Prop :=
  rev10 n = n

def lychrelStep (n : ℕ) : ℕ :=
  n + rev10 n

def IsLychrel10 (n : ℕ) : Prop :=
  ∀ k : ℕ, ¬ IsPalindrome10 (lychrelStep^[k] n)

end S20261014_57_aux

open S20261014_57_aux in
/-- 表述 #20261014-57。

**Lychrel conjecture (base 10):** conjecturally, there are no Lychrel numbers in base 10.

Equivalently, every positive integer eventually becomes a palindrome under the Lychrel iteration. -/
def S20261014_57 : Prop :=
  ∀ n : ℕ, 0 < n → ¬ IsLychrel10 n

end Registry.LychrelNumbersInBase10

end
