/-
Formalia · 条目 #20261014-06
猜想：安德里卡猜想
内容许可：Apache-2.0（与原作相同）
原作版权：Copyright 2025 The Formal Conjectures Authors，Apache License 2.0

改编自 google-deepmind/formal-conjectures 仓库的
FormalConjectures/Wikipedia/Andrica.lean。改动：去掉 `answer(sorry) ↔`、
`@[category …]` 等属性与 `sorry`，只登记命题本身，写成 `def`。
-/
module

public import Mathlib.Data.Nat.Nth
public import Mathlib.Data.Nat.Prime.Defs
public import Mathlib.Analysis.SpecialFunctions.Sqrt

@[expose] public section

namespace Registry.Andrica

/-- 表述 #20261014-06。

`Nat.nth Nat.Prime n` 是按 0 起算的第 `n` 个素数。命题：对所有 `n`，`√(p(n+1)) - √(p n) < 1`（在 `ℝ` 中）。 -/
def S20261014_06 : Prop :=
  ∀ n : ℕ, Real.sqrt ((Nat.nth Nat.Prime (n + 1) : ℕ) : ℝ) - Real.sqrt ((Nat.nth Nat.Prime n : ℕ) : ℝ) < 1

end Registry.Andrica

end
