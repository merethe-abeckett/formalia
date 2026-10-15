/-
Formalia · 条目 #20261014-84
猜想：Conway's subprime Fibonacci sequences
内容许可：Apache-2.0（与原作相同）
原作版权：Copyright 2025 The Formal Conjectures Authors，Apache License 2.0

改编自 google-deepmind/formal-conjectures 仓库的 FormalConjectures/Arxiv/1207.5099/SubprimeFibonacci.lean。
改动：去掉 `answer(sorry) ↔`、`@[category …]` 等属性与 `sorry`，theorem 的参数改写成 `∀`，
只登记命题本身，写成 `def`。
-/
module

public import Mathlib.Data.Nat.Prime.Defs
public import Mathlib.Dynamics.PeriodicPts.Defs
public import Mathlib.Logic.Function.Iterate

@[expose] public section

namespace Registry.ConwaySubprimeFibonacciSequences

namespace S20261014_84_aux

def subprimePart (n : ℕ) : ℕ :=
  if n < 2 then n else if n.Prime then n else n / n.minFac

def step (state : ℕ × ℕ) : ℕ × ℕ :=
  (state.2, subprimePart (state.1 + state.2))

def EventuallyPeriodic (initial : ℕ × ℕ) : Prop :=
  ∃ preperiod period : ℕ, 0 < period ∧
    Function.IsPeriodicPt step period ((step^[preperiod]) initial)

end S20261014_84_aux

open S20261014_84_aux in
/-- 表述 #20261014-84。

Every subprime Fibonacci sequence starting from two positive integers eventually enters a cycle.
This is the "no infinite chains" conjecture recorded in [A214897](https://oeis.org/A214897),
associated with [Guy–Khovanova–Salazar](https://arxiv.org/abs/1207.5099). -/
def S20261014_84 : Prop :=
  ∀ (x y : ℕ) (hx : 0 < x) (hy : 0 < y), EventuallyPeriodic (x, y)

end Registry.ConwaySubprimeFibonacciSequences

end
