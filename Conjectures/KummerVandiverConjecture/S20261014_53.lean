/-
Formalia · 条目 #20261014-53
猜想：Kummer–Vandiver conjecture
内容许可：Apache-2.0（与原作相同）
原作版权：Copyright 2025 The Formal Conjectures Authors，Apache License 2.0

改编自 google-deepmind/formal-conjectures 仓库的 FormalConjectures/Wikipedia/KummerVandiver.lean。
改动：去掉 `answer(sorry) ↔`、`@[category …]` 等属性与 `sorry`，theorem 的参数改写成 `∀`，
只登记命题本身，写成 `def`。
-/
module

public import Mathlib.Algebra.Field.Defs
public import Mathlib.Algebra.Field.Rat
public import Mathlib.Algebra.Field.Subfield.Defs
public import Mathlib.Data.PNat.Notation
public import Mathlib.Data.PNat.Prime
public import Mathlib.Data.SetLike.Basic
public import Mathlib.NumberTheory.Cyclotomic.Basic
public import Mathlib.NumberTheory.NumberField.ClassNumber
public import Mathlib.NumberTheory.NumberField.InfinitePlace.TotallyRealComplex

@[expose] public section

namespace Registry.KummerVandiverConjecture

namespace S20261014_53_aux

open NumberField CyclotomicField IsCyclotomicExtension

def statement : Prop :=
  ∀ (p : ℕ+) (hp : p.Prime), ¬ ↑p ∣ (classNumber (maximalRealSubfield (CyclotomicField p ℚ)))

end S20261014_53_aux

open S20261014_53_aux in
/-- 表述 #20261014-53。

Kummer–Vandiver conjecture states that for every prime $p$, the class number of the maximal
real subfield of $\mathbb{Q}(\zeta_p)$ is not divisible by $p$.
- -/
def S20261014_53 : Prop :=
  statement

end Registry.KummerVandiverConjecture

end
