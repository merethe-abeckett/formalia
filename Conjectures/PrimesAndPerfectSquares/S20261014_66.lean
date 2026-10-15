/-
Formalia · 条目 #20261014-66
猜想：Primes and perfect squares
内容许可：Apache-2.0（与原作相同）
原作版权：Copyright 2025 The Formal Conjectures Authors，Apache License 2.0

改编自 google-deepmind/formal-conjectures 仓库的 FormalConjectures/Wikipedia/PrimesAndPerfectSquares.lean。
改动：去掉 `answer(sorry) ↔`、`@[category …]` 等属性与 `sorry`，theorem 的参数改写成 `∀`，
只登记命题本身，写成 `def`。
-/
module

public import Mathlib.Algebra.Group.Defs
public import Mathlib.Algebra.Group.Nat.Defs
public import Mathlib.Algebra.GroupWithZero.Nat
public import Mathlib.Algebra.Prime.Defs
public import Mathlib.Data.Finite.Defs
public import Mathlib.Data.Set.Defs

@[expose] public section

namespace Registry.PrimesAndPerfectSquares

/-- 表述 #20261014-66。

Are there infinitely many primes $p$ such that $p - 1$ is a perfect square? In other words: Are there infinitely many primes of the form $n^2 + 1$? -/
def S20261014_66 : Prop :=
  {n : ℕ | Prime (n^2 + 1)}.Infinite

end Registry.PrimesAndPerfectSquares

end
