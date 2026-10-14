/-
Formalia · 条目 #20261014-21
猜想：Büchi's problem
内容许可：Apache-2.0（与原作相同）
原作版权：Copyright 2025 The Formal Conjectures Authors，Apache License 2.0

改编自 google-deepmind/formal-conjectures 仓库的 FormalConjectures/Wikipedia/Buchi.lean。
改动：去掉 `answer(sorry) ↔`、`@[category …]` 等属性与 `sorry`，theorem 的参数改写成 `∀`，
只登记命题本身，写成 `def`。
-/
module

public import Mathlib.Algebra.Group.Defs
public import Mathlib.Algebra.Group.Even
public import Mathlib.Algebra.Group.Int.Defs
public import Mathlib.Data.Finset.Defs
public import Mathlib.Data.Finset.Range
public import Mathlib.Data.SetLike.Basic

@[expose] public section

namespace Registry.BuchiProblem

namespace S20261014_21_aux

def IsBuchi (M : ℕ) : Prop :=
  ∀ x a : ℤ, (∀ n ∈ Finset.range M, IsSquare ((x + (n : ℤ)) ^ 2 + a)) → a = 0

end S20261014_21_aux

open S20261014_21_aux in
/-- 表述 #20261014-21。

**Büchi's problem**
There exists a positive integer $M$ such that, for all integers $x$ and $a$,
if $(x+n)^2 + a$ is a square for $M$ consecutive values of $n$, then $a = 0$. -/
def S20261014_21 : Prop :=
  ∃ M : ℕ, 1 ≤ M ∧ IsBuchi M

end Registry.BuchiProblem

end
