/-
Formalia · 条目 #20261014-89
猜想：Integer values of $\tan(\arctan 1 + \arctan 2 + \cdots + \arctan n)$
内容许可：Apache-2.0（与原作相同）
原作版权：Copyright 2025 The Formal Conjectures Authors，Apache License 2.0

改编自 google-deepmind/formal-conjectures 仓库的 FormalConjectures/Arxiv/2607.05739/TanArctanSum.lean。
改动：去掉 `answer(sorry) ↔`、`@[category …]` 等属性与 `sorry`，theorem 的参数改写成 `∀`，
只登记命题本身，写成 `def`。
-/
module

public import Mathlib.Data.Finset.Defs
public import Mathlib.Algebra.BigOperators.Group.Finset.Defs
public import Mathlib.Data.Nat.Basic
public import Mathlib.NumberTheory.Zsqrtd.Basic
public import Mathlib.NumberTheory.Zsqrtd.GaussianInt
public import Mathlib.Order.Interval.Finset.Defs
public import Mathlib.Order.Interval.Finset.Nat

@[expose] public section

namespace Registry.IntegerValuesOfTanArctan1Arctan2CdotsArctanN

namespace S20261014_89_aux

open Finset

def gaussProd (n : ℕ) : GaussianInt := ∏ k ∈ Finset.Icc 1 n, (⟨1, (k : ℤ)⟩ : GaussianInt)

def A (n : ℕ) : ℤ := (gaussProd n).re

def B (n : ℕ) : ℤ := (gaussProd n).im

def IsIntegerValue (n : ℕ) : Prop := A n ∣ B n

instance (n : ℕ) : Decidable (IsIntegerValue n) := by unfold IsIntegerValue; infer_instance

end S20261014_89_aux

open S20261014_89_aux in
/-- 表述 #20261014-89。

**Conjecture (Amdeberhan-Medina-Moll, 2008).** For every integer $n \geq 5$, the value
$$x_n = \tan(\arctan 1 + \arctan 2 + \cdots + \arctan n)$$
is not an integer. -/
def S20261014_89 : Prop :=
  ∀ n : ℕ, 5 ≤ n → ¬ IsIntegerValue n

end Registry.IntegerValuesOfTanArctan1Arctan2CdotsArctanN

end
