/-
Formalia · 条目 #20261014-68
猜想：Ramanujan τ-function
内容许可：Apache-2.0（与原作相同）
原作版权：Copyright 2025 The Formal Conjectures Authors，Apache License 2.0

改编自 google-deepmind/formal-conjectures 仓库的 FormalConjectures/Wikipedia/RamanujanTau.lean。
改动：去掉 `answer(sorry) ↔`、`@[category …]` 等属性与 `sorry`，theorem 的参数改写成 `∀`，
只登记命题本身，写成 `def`。
-/
module

public import Mathlib.Algebra.Group.Defs
public import Mathlib.Algebra.Group.Int.Defs
public import Mathlib.Algebra.GroupWithZero.Defs
public import Mathlib.Algebra.Module.Defs
public import Mathlib.Algebra.Module.LinearMap.Defs
public import Mathlib.Algebra.Ring.Defs
public import Mathlib.Algebra.Ring.Hom.Defs
public import Mathlib.Algebra.Ring.Int.Defs
public import Mathlib.Data.FunLike.Basic
public import Mathlib.Data.PNat.Notation
public import Mathlib.RingTheory.MvPowerSeries.Basic
public import Mathlib.RingTheory.PowerSeries.Basic
public import Mathlib.RingTheory.PowerSeries.PiTopology
public import Mathlib.Topology.Algebra.InfiniteSum.Defs
public import Mathlib.Topology.Algebra.InfiniteSum.SummationFilter
public import Mathlib.Topology.Order

@[expose] public section

namespace Registry.RamanujanFunction

namespace S20261014_68_aux

open PowerSeries PowerSeries.WithPiTopology

noncomputable def Δ : PowerSeries ℤ := X * ∏' (n : ℕ+), (1 - X ^ (n : ℕ)) ^ 24

noncomputable def τ (n : ℕ) : ℤ := PowerSeries.coeff n Δ

end S20261014_68_aux

open S20261014_68_aux in
/-- 表述 #20261014-68。

Lehmer's conjecture: $\tau(n) \ne 0$ for all $n > 0$. -/
def S20261014_68 : Prop :=
  ∀ n > 0, τ n ≠ 0

end Registry.RamanujanFunction

end
