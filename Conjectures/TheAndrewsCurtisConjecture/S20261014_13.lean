/-
Formalia · 条目 #20261014-13
猜想：The Andrews-Curtis conjecture
内容许可：Apache-2.0（与原作相同）
原作版权：Copyright 2025 The Formal Conjectures Authors，Apache License 2.0

改编自 google-deepmind/formal-conjectures 仓库的 FormalConjectures/Wikipedia/AndrewsCurtis.lean。
改动：去掉 `answer(sorry) ↔`、`@[category …]` 等属性与 `sorry`，theorem 的参数改写成 `∀`，
只登记命题本身，写成 `def`。
-/
module

public import Mathlib.Algebra.Group.Subgroup.Basic
public import Mathlib.Algebra.Group.Subgroup.Defs
public import Mathlib.Algebra.Group.Subgroup.Lattice
public import Mathlib.Data.FunLike.Basic
public import Mathlib.Data.FunLike.Equiv
public import Mathlib.Data.Set.Operations
public import Mathlib.GroupTheory.FreeGroup.Basic
public import Mathlib.Logic.Equiv.Basic
public import Mathlib.Logic.Equiv.Defs
public import Mathlib.Logic.Function.Basic
public import Mathlib.Logic.Relation
public import Mathlib.Order.Notation

@[expose] public section

namespace Registry.TheAndrewsCurtisConjecture

namespace S20261014_13_aux

abbrev RelatorTuple (n : ℕ) := Fin n → FreeGroup (Fin n)

def standardRelators (n : ℕ) : RelatorTuple n :=
  fun i ↦ FreeGroup.of i

inductive Move {n : ℕ} : RelatorTuple n → RelatorTuple n → Prop
  | invert (r : RelatorTuple n) (i : Fin n) :
      Move r (Function.update r i (r i)⁻¹)
  | multiply (r : RelatorTuple n) (i j : Fin n) (hij : i ≠ j) :
      Move r (Function.update r i (r i * r j))
  | swap (r : RelatorTuple n) (i j : Fin n) :
      Move r (fun k ↦ r (Equiv.swap i j k))
  | conjugate (r : RelatorTuple n) (i : Fin n) (w : FreeGroup (Fin n)) :
      Move r (Function.update r i (w * r i * w⁻¹))

def Equivalent {n : ℕ} : RelatorTuple n → RelatorTuple n → Prop :=
  Relation.EqvGen Move

def NormallyGenerates {n : ℕ} (r : RelatorTuple n) : Prop :=
  Subgroup.normalClosure (Set.range r) = ⊤

end S20261014_13_aux

open S20261014_13_aux in
/-- 表述 #20261014-13。

**The Andrews-Curtis conjecture.**

Every normally generating `n`-tuple in the free group of rank `n` is
Andrews-Curtis equivalent to the standard tuple of free generators. -/
def S20261014_13 : Prop :=
  ∀ (n : ℕ) (r : RelatorTuple n)
      (hr : NormallyGenerates r), Equivalent r (standardRelators n)

end Registry.TheAndrewsCurtisConjecture

end
