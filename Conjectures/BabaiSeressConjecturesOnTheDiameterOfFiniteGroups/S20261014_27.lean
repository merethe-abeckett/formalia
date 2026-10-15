/-
Formalia · 条目 #20261014-27
猜想：Babai–Seress Conjectures on the Diameter of Finite Groups
内容许可：Apache-2.0（与原作相同）
原作版权：Copyright 2025 The Formal Conjectures Authors，Apache License 2.0

改编自 google-deepmind/formal-conjectures 仓库的 FormalConjectures/Wikipedia/DiameterSimpleFiniteGroups.lean。
改动：去掉 `answer(sorry) ↔`、`@[category …]` 等属性与 `sorry`，theorem 的参数改写成 `∀`，
只登记命题本身，写成 `def`。
-/
module

public import Mathlib.Algebra.Group.Basic
public import Mathlib.Algebra.Group.Defs
public import Mathlib.Algebra.Group.End
public import Mathlib.Algebra.Group.Subgroup.Defs
public import Mathlib.Algebra.Group.Subgroup.Lattice
public import Mathlib.Combinatorics.SimpleGraph.Basic
public import Mathlib.Combinatorics.SimpleGraph.Diam
public import Mathlib.Data.Fintype.Basic
public import Mathlib.Data.Fintype.Defs
public import Mathlib.Data.Nat.Lattice
public import Mathlib.Data.Real.Basic
public import Mathlib.Data.Set.Defs
public import Mathlib.Data.SetLike.Basic
public import Mathlib.GroupTheory.SpecificGroups.Alternating
public import Mathlib.Logic.Equiv.Defs
public import Mathlib.Order.Notation
public import Mathlib.Order.SetNotation

@[expose] public section

namespace Registry.BabaiSeressConjecturesOnTheDiameterOfFiniteGroups

namespace S20261014_27_aux

def cayleyGraph {G : Type*} [Group G] (S : Set G) : SimpleGraph G :=
  SimpleGraph.fromRel (fun g h => g⁻¹ * h ∈ S)

noncomputable def groupDiam (G : Type*) [Group G] [Fintype G] : ℕ :=
  sSup { d : ℕ | ∃ S : Set G, Subgroup.closure S = ⊤ ∧ (cayleyGraph S).diam = d }

end S20261014_27_aux

open S20261014_27_aux in
/-- 表述 #20261014-27。

**Babai–Seress Conjecture (Conjecture 1.5)**: There exists an absolute constant $C$ such
that the diameter of the alternating group $A_n$ satisfies
$$\operatorname{diam}(A_n) \leq n^C.$$

*Reference:* [L. Babai and Á. Seress, *On the diameter of permutation groups*,
European Journal of Combinatorics 13 (1992), Conjecture 1.5](https://doi.org/10.1016/S0195-6698(05)80029-0) -/
def S20261014_27 : Prop :=
  ∃ C : ℕ, ∀ n : ℕ,
      (groupDiam (alternatingGroup (Fin n)) : ℝ) ≤ (n : ℝ) ^ C

end Registry.BabaiSeressConjecturesOnTheDiameterOfFiniteGroups

end
