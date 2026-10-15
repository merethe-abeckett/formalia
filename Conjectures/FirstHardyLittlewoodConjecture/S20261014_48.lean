/-
Formalia · 条目 #20261014-48
猜想：First Hardy–Littlewood conjecture
内容许可：Apache-2.0（与原作相同）
原作版权：Copyright 2025 The Formal Conjectures Authors，Apache License 2.0

改编自 google-deepmind/formal-conjectures 仓库的 FormalConjectures/Wikipedia/HardyLittlewood.lean。
改动：去掉 `answer(sorry) ↔`、`@[category …]` 等属性与 `sorry`，theorem 的参数改写成 `∀`，
只登记命题本身，写成 `def`。
-/
module

public import Mathlib.Analysis.Asymptotics.Defs
public import Mathlib.Order.Filter.Defs
public import Mathlib.NumberTheory.PrimeCounting

@[expose] public section

namespace Registry.FirstHardyLittlewoodConjecture

namespace S20261014_48_aux

open Asymptotics Filter

open scoped Nat.Prime

/-  ## First Hardy-Littlewood Conjecture -/

def SecondHardyLittlewoodConjectureFor (x y : ℕ) : Prop :=
  π (x + y) ≤ π x + π y

end S20261014_48_aux

open S20261014_48_aux in
/-- 表述 #20261014-48。

For integers $x, y \geq 2$,
$$
  \pi(x + y) \leq \pi(x) + \pi(y),
$$
where $\pi(z)$ denotes the prime-counting function, giving the number of primes up to
and including $z$. -/
def S20261014_48 : Prop :=
  ∀ {x y : ℕ} (hx : 2 ≤ x) (hy : 2 ≤ y), SecondHardyLittlewoodConjectureFor x y

end Registry.FirstHardyLittlewoodConjecture

end
