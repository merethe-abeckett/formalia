/-
Formalia · 条目 #20261014-41
猜想：Firoozbakht's conjecture
内容许可：Apache-2.0（与原作相同）
原作版权：Copyright 2025 The Formal Conjectures Authors，Apache License 2.0

改编自 google-deepmind/formal-conjectures 仓库的 FormalConjectures/Wikipedia/Firoozbakht.lean。
改动：去掉 `answer(sorry) ↔`、`@[category …]` 等属性与 `sorry`，theorem 的参数改写成 `∀`，
只登记命题本身，写成 `def`。
-/
module

public import Mathlib.Algebra.Group.Defs
public import Mathlib.Algebra.GroupWithZero.Nat
public import Mathlib.Algebra.Prime.Defs
public import Mathlib.Analysis.SpecialFunctions.Pow.Real
public import Mathlib.Data.Nat.Nth
public import Mathlib.Data.Real.Basic

@[expose] public section

namespace Registry.FiroozbakhtConjecture

namespace S20261014_41_aux

open Real

noncomputable def firoozbakhtSeq (n : ℕ) : ℝ :=
  (n.nth Prime)^(1/(n + 1) : ℝ)

end S20261014_41_aux

open S20261014_41_aux in
/-- 表述 #20261014-41。

**Firoozbakht's conjecture**
The inequality $\sqrt[n+1]{p_{n+1}} < \sqrt[n]{p_n}$ holds for all prime numbers $p_n$. -/
def S20261014_41 : Prop :=
  ∀ (n : ℕ), firoozbakhtSeq (n+1) < firoozbakhtSeq n

end Registry.FiroozbakhtConjecture

end
