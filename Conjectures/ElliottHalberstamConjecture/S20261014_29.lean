/-
Formalia · 条目 #20261014-29
猜想：Elliott–Halberstam conjecture
内容许可：Apache-2.0（与原作相同）
原作版权：Copyright 2025 The Formal Conjectures Authors，Apache License 2.0

改编自 google-deepmind/formal-conjectures 仓库的 FormalConjectures/Wikipedia/ElliottHalberstamConjecture.lean。
改动：去掉 `answer(sorry) ↔`、`@[category …]` 等属性与 `sorry`，theorem 的参数改写成 `∀`，
只登记命题本身，写成 `def`。
-/
module

public import Mathlib.Algebra.BigOperators.Group.Finset.Defs
public import Mathlib.Algebra.Group.Defs
public import Mathlib.Algebra.Group.Units.Defs
public import Mathlib.Algebra.GroupWithZero.Defs
public import Mathlib.Algebra.Order.Floor.Defs
public import Mathlib.Algebra.Order.Group.Unbundled.Abs
public import Mathlib.Algebra.Ring.Defs
public import Mathlib.Analysis.SpecialFunctions.Log.Basic
public import Mathlib.Analysis.SpecialFunctions.Pow.Real
public import Mathlib.Data.Finset.Card
public import Mathlib.Data.Finset.Filter
public import Mathlib.Data.Finset.Range
public import Mathlib.Data.Int.Cast.Defs
public import Mathlib.Data.Nat.Basic
public import Mathlib.Data.Nat.Cast.Defs
public import Mathlib.Data.Nat.Prime.Defs
public import Mathlib.Data.Nat.Totient
public import Mathlib.Data.Real.Archimedean
public import Mathlib.Data.Real.Basic
public import Mathlib.Data.ZMod.Defs
public import Mathlib.NumberTheory.PrimeCounting
public import Mathlib.Order.Interval.Finset.Defs
public import Mathlib.Order.Interval.Finset.Nat
public import Mathlib.Order.SetNotation

@[expose] public section

namespace Registry.ElliottHalberstamConjecture

namespace S20261014_29_aux

def primesInAPCount (x q : ℕ) (a : ZMod q) : ℕ :=
  ((Finset.range (x + 1)).filter fun p : ℕ => p.Prime ∧ (p : ZMod q) = a).card

noncomputable def E (x q : ℕ) : ℝ :=
  ⨆ a : (ZMod q)ˣ, |(primesInAPCount x q a : ℝ) - (x.primeCounting : ℝ) / (q.totient : ℝ)|

end S20261014_29_aux

open S20261014_29_aux in
/-- 表述 #20261014-29。

The Elliott–Halberstam conjecture: for every $\theta < 1$ and $A > 0$ there exists a
constant $C > 0$ such that
$$\sum_{1 \le q \le x^{\theta}} E(x; q) \le \frac{C x}{\log^A x}$$
for all $x > 2$. -/
def S20261014_29 : Prop :=
  ∀ (θ : ℝ) (hθ : θ < 1) (A : ℝ) (hA : 0 < A), ∃ C > (0 : ℝ), ∀ x : ℕ, 2 < x →
        ∑ q ∈ Finset.Icc 1 ⌊(x : ℝ) ^ θ⌋₊, E x q ≤ C * x / Real.log x ^ A

end Registry.ElliottHalberstamConjecture

end
