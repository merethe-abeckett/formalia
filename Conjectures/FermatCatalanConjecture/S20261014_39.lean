/-
Formalia · 条目 #20261014-39
猜想：Fermat-Catalan conjecture
内容许可：Apache-2.0（与原作相同）
原作版权：Copyright 2025 The Formal Conjectures Authors，Apache License 2.0

改编自 google-deepmind/formal-conjectures 仓库的 FormalConjectures/Wikipedia/FermatCatalanConjecture.lean。
改动：去掉 `answer(sorry) ↔`、`@[category …]` 等属性与 `sorry`，theorem 的参数改写成 `∀`，
只登记命题本身，写成 `def`。
-/
module

public import Mathlib.Algebra.BigOperators.Group.Finset.Defs
public import Mathlib.Algebra.Group.Defs
public import Mathlib.Algebra.Group.Nat.Defs
public import Mathlib.Data.Finite.Defs
public import Mathlib.Data.Real.Basic
public import Mathlib.Data.Set.Defs
public import Mathlib.Logic.Function.Defs
public import Mathlib.Logic.Pairwise
public import Mathlib.Order.Defs.PartialOrder
public import Mathlib.Order.Fin.Basic
public import Mathlib.Order.Interval.Finset.Defs
public import Mathlib.Order.Interval.Finset.Fin

@[expose] public section

namespace Registry.FermatCatalanConjecture

namespace S20261014_39_aux

open scoped Function

def FermatCatalanSet' : Set (Fin 6 → ℕ) :=
    { f : Fin 6 → ℕ |
        (∀ i, 0 < f i) ∧
        (({0, 1, 2} : Set <| Fin 6).Pairwise (Nat.Coprime on f)) ∧
        (f 0) ^ (f 3) + (f 1) ^ (f 4) = (f 2) ^ (f 5) ∧
        ∑ i ∈ Finset.Icc 3 5, (1 / f i : ℝ) < 1 }

def FermatCatalanSet : Set (ℕ × ℕ × ℕ) :=
    (fun f => ((f 0) ^ (f 3), (f 1) ^ (f 4), (f 2) ^ (f 5))) '' FermatCatalanSet'

def fermatCatalanConjecture : Prop :=
  FermatCatalanSet.Finite

end S20261014_39_aux

open S20261014_39_aux in
/-- 表述 #20261014-39。

The **Fermat–Catalan conjecture** states that the equation
$a^m + b^n = c^k$ has only finitely many solutions $(a,b,c,m,n,k)$ with distinct triplets of values
$(a^m, b^n, c^k)$ where $a, b, c$ are positive coprime integers and $m, n, k$ are positive integers satisfying
$\frac 1 m + \frac 1 n + \frac 1 k < 1$. -/
def S20261014_39 : Prop :=
  fermatCatalanConjecture

end Registry.FermatCatalanConjecture

end
