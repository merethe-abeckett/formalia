/-
Formalia · 条目 #20261014-09
猜想：*abc* conjecture
内容许可：Apache-2.0（与原作相同）
原作版权：Copyright 2025 The Formal Conjectures Authors，Apache License 2.0

改编自 google-deepmind/formal-conjectures 仓库的 FormalConjectures/Wikipedia/ABC.lean。
改动：去掉 `answer(sorry) ↔`、`@[category …]` 等属性与 `sorry`，theorem 的参数改写成 `∀`，
只登记命题本身，写成 `def`。
-/
module

public import Mathlib.Algebra.BigOperators.Group.Finset.Defs
public import Mathlib.Algebra.Group.Nat.Defs
public import Mathlib.Analysis.SpecialFunctions.Pow.Real
public import Mathlib.Data.Finite.Defs
public import Mathlib.Data.Nat.PrimeFin
public import Mathlib.Data.Real.Basic
public import Mathlib.Data.Set.Defs
public import Mathlib.Logic.Pairwise

@[expose] public section

namespace Registry.AbcConjecture

namespace S20261014_09_aux

def radical (n : ℕ) : ℕ := n.primeFactors.prod id

end S20261014_09_aux

open S20261014_09_aux in
/-- 表述 #20261014-09。

For every positive real number `ε`, there exist only finitely many triples `(a, b, c)` of coprime positive integers, with `a + b = c`, such that `c > rad(abc)^(1+ε)` -/
def S20261014_09 : Prop :=
  ∀ (ε : ℝ) (hε : 0 < ε), {(a, b, c) : ℕ × ℕ × ℕ | 0 < a ∧ 0 < b ∧ 0 < c ∧ ({a, b, c} : Set ℕ).Pairwise Nat.Coprime ∧
      a + b = c ∧ (radical <| a * b * c : ℝ)^(1 + ε) < c}.Finite

end Registry.AbcConjecture

end
