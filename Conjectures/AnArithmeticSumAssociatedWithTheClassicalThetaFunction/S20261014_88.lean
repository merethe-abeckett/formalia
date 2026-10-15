/-
Formalia · 条目 #20261014-88
猜想：An Arithmetic Sum Associated with the Classical Theta Function
内容许可：Apache-2.0（与原作相同）
原作版权：Copyright 2025 The Formal Conjectures Authors，Apache License 2.0

改编自 google-deepmind/formal-conjectures 仓库的 FormalConjectures/Arxiv/2501.03234/ArithmeticSumS.lean。
改动：去掉 `answer(sorry) ↔`、`@[category …]` 等属性与 `sorry`，theorem 的参数改写成 `∀`，
只登记命题本身，写成 `def`。
-/
module

public import Mathlib.Algebra.BigOperators.Group.Finset.Defs
public import Mathlib.Algebra.Group.Defs
public import Mathlib.Algebra.Group.Int.Defs
public import Mathlib.Algebra.Order.Floor.Defs
public import Mathlib.Algebra.Order.Ring.Rat
public import Mathlib.Algebra.Order.Ring.Unbundled.Rat
public import Mathlib.Algebra.Ring.Nat
public import Mathlib.Algebra.Ring.Parity
public import Mathlib.Algebra.Ring.Rat
public import Mathlib.Analysis.Normed.Field.Basic
public import Mathlib.Analysis.Normed.Field.Lemmas
public import Mathlib.Analysis.Normed.Ring.Basic
public import Mathlib.Data.Nat.Basic
public import Mathlib.Data.Nat.Prime.Defs
public import Mathlib.Data.Rat.Floor
public import Mathlib.Order.Interval.Finset.Defs
public import Mathlib.Order.Interval.Finset.Nat

@[expose] public section

namespace Registry.AnArithmeticSumAssociatedWithTheClassicalThetaFunction

namespace S20261014_88_aux

def S' (h k : ℕ) : ℤ := ∑ j ∈ Finset.Ico 1 k, (-1 : ℤ) ^ (j + 1 + ⌊(h * j : ℚ) / k⌋₊)

def S (k : ℕ) : ℤ := ∑ h ∈ Finset.Ico 1 k, S' h k

end S20261014_88_aux

open S20261014_88_aux in
/-- 表述 #20261014-88。

**Conjecture 1.1**: For any odd prime $k$, the sum associated with the classical theta function $θ_3$,
$S(k)$ is positive. -/
def S20261014_88 : Prop :=
  ∀ (k : ℕ) (hprim : k.Prime) (hodd : Odd k), 0 < S k

end Registry.AnArithmeticSumAssociatedWithTheClassicalThetaFunction

end
