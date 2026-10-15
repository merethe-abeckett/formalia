/-
Formalia · 条目 #20261014-73
猜想：Selfridge's conjectures
内容许可：Apache-2.0（与原作相同）
原作版权：Copyright 2025 The Formal Conjectures Authors，Apache License 2.0

改编自 google-deepmind/formal-conjectures 仓库的 FormalConjectures/Wikipedia/Selfridge.lean。
改动：去掉 `answer(sorry) ↔`、`@[category …]` 等属性与 `sorry`，theorem 的参数改写成 `∀`，
只登记命题本身，写成 `def`。
-/
module

public import Mathlib.Algebra.Group.Defs
public import Mathlib.Algebra.Group.Nat.Defs
public import Mathlib.Algebra.Ring.Nat
public import Mathlib.Algebra.Ring.Parity
public import Mathlib.Data.Nat.Fib.Basic
public import Mathlib.Data.Nat.ModEq
public import Mathlib.Data.Nat.Prime.Defs

@[expose] public section

namespace Registry.SelfridgeConjectures

namespace S20261014_73_aux

structure IsSelfridge (p : ℕ) where
  is_odd : Odd p
  mod_5 : p ≡ 2 [MOD 5] ∨ p ≡ 3 [MOD 5]
  pow_2 : 2^(p-1) ≡ 1 [MOD p]
  fib : (p+1).fib ≡ 0 [MOD p]

end S20261014_73_aux

open S20261014_73_aux in
/-- 表述 #20261014-73。

**PSW conjecture** (Selfridge's test)
Let $p$ be an odd number, with $p \equiv \pm 2 \pmod{5}$, $2^{p-1} \equiv 1 \pmod{p}$
and $F_{p+1} \equiv 0 \pmod{p}$, then $p$ is a prime number. -/
def S20261014_73 : Prop :=
  ∀ (p : ℕ) (hp : IsSelfridge p), p.Prime

end Registry.SelfridgeConjectures

end
