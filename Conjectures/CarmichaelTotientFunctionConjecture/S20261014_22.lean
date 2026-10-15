/-
Formalia · 条目 #20261014-22
猜想：Carmichael's totient function conjecture
内容许可：Apache-2.0（与原作相同）
原作版权：Copyright 2025 The Formal Conjectures Authors，Apache License 2.0

改编自 google-deepmind/formal-conjectures 仓库的 FormalConjectures/Wikipedia/CarmichaelTotient.lean。
改动：去掉 `answer(sorry) ↔`、`@[category …]` 等属性与 `sorry`，theorem 的参数改写成 `∀`，
只登记命题本身，写成 `def`。
-/
module

public import Mathlib.Data.Nat.Totient

@[expose] public section

namespace Registry.CarmichaelTotientFunctionConjecture

namespace S20261014_22_aux

open Nat

def CarmichaelTotientFor (n : ℕ) : Prop := ∃ m : ℕ, m ≠ n ∧ φ m = φ n

end S20261014_22_aux

open S20261014_22_aux in
/-- 表述 #20261014-22。

*Carmichael's totient function conjecture*: For every positive natural number $n$,
there exists a natural number $m$ with $m ≠ n$, such that $φ(n) = φ(m)$. -/
def S20261014_22 : Prop :=
  ∀ ⦃n : ℕ⦄, 0 < n → CarmichaelTotientFor n

end Registry.CarmichaelTotientFunctionConjecture

end
