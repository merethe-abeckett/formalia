/-
Formalia · 条目 #20261014-38
猜想：Open questions about Fermat numbers
内容许可：Apache-2.0（与原作相同）
原作版权：Copyright 2025 The Formal Conjectures Authors，Apache License 2.0

改编自 google-deepmind/formal-conjectures 仓库的 FormalConjectures/Wikipedia/Fermat.lean。
改动：去掉 `answer(sorry) ↔`、`@[category …]` 等属性与 `sorry`，theorem 的参数改写成 `∀`，
只登记命题本身，写成 `def`。
-/
module

public import Mathlib.Algebra.GroupWithZero.Nat
public import Mathlib.Algebra.Prime.Defs
public import Mathlib.NumberTheory.Fermat

@[expose] public section

namespace Registry.OpenQuestionsAboutFermatNumbers

/-- 表述 #20261014-38。

Are Fermat numbers composite for all `n > 4`? -/
def S20261014_38 : Prop :=
  ∀ n > 4, ¬Prime n.fermatNumber

end Registry.OpenQuestionsAboutFermatNumbers

end
