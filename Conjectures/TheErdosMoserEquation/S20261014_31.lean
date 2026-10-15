/-
Formalia · 条目 #20261014-31
猜想：The Erdős–Moser equation
内容许可：Apache-2.0（与原作相同）
原作版权：Copyright 2025 The Formal Conjectures Authors，Apache License 2.0

改编自 google-deepmind/formal-conjectures 仓库的 FormalConjectures/Wikipedia/ErdosMoser.lean。
改动：去掉 `answer(sorry) ↔`、`@[category …]` 等属性与 `sorry`，theorem 的参数改写成 `∀`，
只登记命题本身，写成 `def`。
-/
module

public import Mathlib.Algebra.BigOperators.Group.Finset.Defs
public import Mathlib.Algebra.Group.Defs
public import Mathlib.Algebra.Group.Nat.Defs
public import Mathlib.Data.Nat.Basic
public import Mathlib.Order.Interval.Finset.Defs
public import Mathlib.Order.Interval.Finset.Nat

@[expose] public section

namespace Registry.TheErdosMoserEquation

namespace S20261014_31_aux

def powerSum (k m : ℕ) : ℕ :=
  ∑ i ∈ Finset.Ico 1 m, i ^ k

end S20261014_31_aux

open S20261014_31_aux in
/-- 表述 #20261014-31。

The only positive solution of $S_k(m)=m^k$ is $(k,m)=(1,3)$. -/
def S20261014_31 : Prop :=
  ∀ k m : ℕ, 0 < k → 0 < m → powerSum k m = m ^ k → k = 1 ∧ m = 3

end Registry.TheErdosMoserEquation

end
