/-
Formalia · 条目 #20261014-52
猜想：Juggler conjecture
内容许可：Apache-2.0（与原作相同）
原作版权：Copyright 2025 The Formal Conjectures Authors，Apache License 2.0

改编自 google-deepmind/formal-conjectures 仓库的 FormalConjectures/Wikipedia/JugglerConjecture.lean。
改动：去掉 `answer(sorry) ↔`、`@[category …]` 等属性与 `sorry`，theorem 的参数改写成 `∀`，
只登记命题本身，写成 `def`。
-/
module

public import Mathlib.Algebra.Group.Defs
public import Mathlib.Algebra.Group.Even
public import Mathlib.Algebra.Group.Nat.Even
public import Mathlib.Algebra.Order.Floor.Defs
public import Mathlib.Analysis.SpecialFunctions.Pow.Real
public import Mathlib.Data.Nat.Cast.Defs
public import Mathlib.Data.Real.Archimedean
public import Mathlib.Data.Real.Basic
public import Mathlib.Logic.Function.Iterate

@[expose] public section

namespace Registry.JugglerConjecture

namespace S20261014_52_aux

noncomputable def jugglerStep (n : ℕ) : ℕ :=
  if Even n then ⌊(n : ℝ) ^ (1/2 : ℝ)⌋₊ else ⌊(n : ℝ) ^ (3/2 : ℝ)⌋₊

end S20261014_52_aux

open S20261014_52_aux in
/-- 表述 #20261014-52。

Now form a sequence beginning with any positive integer, where each subsequent term is obtained
by applying the operation defined above to the previous term.
The **Juggler Conjecture** states that for any positive integer $n$, there exists a natural number
$m$ such that the $m$-th term of the sequence is $1$. -/
def S20261014_52 : Prop :=
  ∀ (n : ℕ) (hn : n > 0), ∃ m, jugglerStep^[m] n = 1

end Registry.JugglerConjecture

end
