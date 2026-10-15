/-
Formalia · 条目 #20261014-90
猜想：Bugeaud Collection of Conjectures and Open Questions: Rapidly Increasing Sequences Dense Modulo One
内容许可：Apache-2.0（与原作相同）
原作版权：Copyright 2025 The Formal Conjectures Authors，Apache License 2.0

改编自 google-deepmind/formal-conjectures 仓库的 FormalConjectures/Books/BugeaudDistributionModuloOne/Problem10_6.lean。
改动：去掉 `answer(sorry) ↔`、`@[category …]` 等属性与 `sorry`，theorem 的参数改写成 `∀`，
只登记命题本身，写成 `def`。
-/
module

public import Mathlib.Topology.Instances.AddCircle.Defs
public import Mathlib.Algebra.Group.Defs
public import Mathlib.Algebra.Group.Subgroup.Defs
public import Mathlib.Algebra.Group.Subgroup.ZPowers.Basic
public import Mathlib.Algebra.Quotient
public import Mathlib.Analysis.SpecialFunctions.Log.Basic
public import Mathlib.Data.Nat.Basic
public import Mathlib.Data.Real.Basic
public import Mathlib.Data.Set.Operations
public import Mathlib.GroupTheory.Coset.Defs
public import Mathlib.NumberTheory.Real.Irrational
public import Mathlib.Order.Filter.AtTopBot.Defs
public import Mathlib.Order.Filter.Defs
public import Mathlib.Order.Monotone.Defs
public import Mathlib.Topology.Algebra.Group.Quotient
public import Mathlib.Topology.Defs.Basic
public import Mathlib.Topology.MetricSpace.Pseudo.Defs
public import Mathlib.Topology.UniformSpace.Defs

@[expose] public section

namespace Registry.BugeaudCollectionOfConjecturesAndOpenQuestionsRapidlyIncreas

namespace S20261014_90_aux

open Filter

/- ## Two theorems from the literature -/

def IsGenuinelySublacunary (m : ℕ → ℕ) : Prop :=
  ∃ c > 0, ∀ᶠ (n : ℕ) in atTop, (1 + c / Real.log n) ≤ (m (n+1) : ℝ) / m n

end S20261014_90_aux

open S20261014_90_aux in
/-- 表述 #20261014-90。

Problem 10.6. Find a very rapidly increasing sequence $(m_n)_{n \ge 1}$ of positive
integers such that $(\{\xi m_n\})_{n \ge 1}$ is dense modulo one for every irrational
number $\xi$. Note: Furstenberg's $2^m3^n$ is sublacunary but requires two parameters.

This is the reading of "very rapidly increasing" as a lower bound on the consecutive ratios,
and it is the one that remains open. It is not answered by runs of consecutive integers, since
inside a run $m_{n+1} - m_n = 1$; and by `not_isLacunary_of_dense` any answer is pinched
between a decaying ratio floor and the failure of lacunarity. [Kat16, Cor. 4.9] gives a
universally densifying sequence of the multiplicative shape $\{2^n 3^e\}$, for which the
ratio condition reduces to a Diophantine statement about the differences of the exponents
$e$ times $\log_2 3$ modulo one. -/
def S20261014_90 : Prop :=
  ∃ m : ℕ → ℕ,
      StrictMono m ∧
      IsGenuinelySublacunary m ∧
      ∀ ξ : ℝ, Irrational ξ →
        Dense (Set.range fun n => (↑(ξ * m n) : AddCircle (1 : ℝ)))

end Registry.BugeaudCollectionOfConjecturesAndOpenQuestionsRapidlyIncreas

end
