/-
Formalia · 条目 #20261014-30
猜想：Emirps
内容许可：Apache-2.0（与原作相同）
原作版权：Copyright 2025 The Formal Conjectures Authors，Apache License 2.0

改编自 google-deepmind/formal-conjectures 仓库的 FormalConjectures/Wikipedia/Emirp.lean。
改动：去掉 `answer(sorry) ↔`、`@[category …]` 等属性与 `sorry`，theorem 的参数改写成 `∀`，
只登记命题本身，写成 `def`。
-/
module

public import Mathlib.Algebra.Ring.Nat
public import Mathlib.Data.Finite.Defs
public import Mathlib.Data.Nat.Digits.Defs
public import Mathlib.Data.Nat.Prime.Defs
public import Mathlib.Data.Set.Defs

@[expose] public section

namespace Registry.Emirps

namespace S20261014_30_aux

def reverse10 (n : ℕ) : ℕ :=
  Nat.ofDigits 10 (Nat.digits 10 n).reverse

def IsEmirp (p : ℕ) : Prop :=
  p.Prime ∧ (reverse10 p).Prime ∧ reverse10 p ≠ p

end S20261014_30_aux

open S20261014_30_aux in
/-- 表述 #20261014-30。

[Wikipedia's article on emirps](https://en.wikipedia.org/wiki/Emirp) states: "It is not known
whether there are infinitely many emirps." -/
def S20261014_30 : Prop :=
  {p : ℕ | IsEmirp p}.Infinite

end Registry.Emirps

end
