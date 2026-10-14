/-
Formalia · 条目 #20261014-45
猜想：Graceful Tree Conjecture (Ringel–Kotzig conjecture)
内容许可：Apache-2.0（与原作相同）
原作版权：Copyright 2025 The Formal Conjectures Authors，Apache License 2.0

改编自 google-deepmind/formal-conjectures 仓库的 FormalConjectures/Wikipedia/GracefulLabeling.lean。
改动：去掉 `answer(sorry) ↔`、`@[category …]` 等属性与 `sorry`，theorem 的参数改写成 `∀`，
只登记命题本身，写成 `def`。
-/
module

public import Mathlib.Combinatorics.SimpleGraph.Acyclic
public import Mathlib.Combinatorics.SimpleGraph.Basic
public import Mathlib.Combinatorics.SimpleGraph.Finite
public import Mathlib.Data.Finset.Card
public import Mathlib.Data.Finset.Defs
public import Mathlib.Data.Finset.Image
public import Mathlib.Data.Finset.Sym
public import Mathlib.Data.Fintype.Defs
public import Mathlib.Data.FunLike.Basic
public import Mathlib.Data.FunLike.Equiv
public import Mathlib.Data.Nat.Basic
public import Mathlib.Data.Sym.Sym2
public import Mathlib.Logic.Equiv.Defs
public import Mathlib.Order.Interval.Finset.Defs
public import Mathlib.Order.Interval.Finset.Nat

@[expose] public section

namespace Registry.GracefulTreeConjectureRingelKotzigConjecture

namespace S20261014_45_aux

open SimpleGraph

end S20261014_45_aux

open S20261014_45_aux in
/-- 表述 #20261014-45。

Every tree admits a graceful labeling.

A graceful labeling of a tree $T$ with $m$ edges is an injective map $f : V \to \{0, \dots, m\}$
such that the multiset of absolute differences $|f(u) - f(v)|$ over edges $\{u,v\}$ of $T$
equals $\{1, \dots, m\}$. -/
def S20261014_45 : Prop :=
  ∀ {V : Type*} [Fintype V] [DecidableEq V]
      (T : SimpleGraph V) [DecidableRel T.Adj] (hT : T.IsTree), let m := T.edgeFinset.card
      ∃ f : V → ℕ,
        Function.Injective f ∧
        (∀ v, f v ≤ m) ∧
        T.edgeFinset.image (fun e =>
          e.lift ⟨fun u v => Int.natAbs ((f u : ℤ) - (f v : ℤ)),
                  fun u v => by
                    show ((f u : ℤ) - f v).natAbs = ((f v : ℤ) - f u).natAbs
                    rw [← Int.natAbs_neg, neg_sub]⟩) = Finset.Icc 1 m

end Registry.GracefulTreeConjectureRingelKotzigConjecture

end
