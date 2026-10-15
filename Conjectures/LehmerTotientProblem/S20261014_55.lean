/-
Formalia · 条目 #20261014-55
猜想：Lehmer's totient problem
内容许可：Apache-2.0（与原作相同）
原作版权：Copyright 2025 The Formal Conjectures Authors，Apache License 2.0

改编自 google-deepmind/formal-conjectures 仓库的 FormalConjectures/Wikipedia/LehmerTotient.lean。
改动：去掉 `answer(sorry) ↔`、`@[category …]` 等属性与 `sorry`，theorem 的参数改写成 `∀`，
只登记命题本身，写成 `def`。
-/
module

public import Mathlib.Algebra.GroupWithZero.Nat
public import Mathlib.Algebra.Prime.Defs
public import Mathlib.Data.Nat.Totient

@[expose] public section

namespace Registry.LehmerTotientProblem

/-- 表述 #20261014-55。

Does there exist a composite number $n > 1$ such that Euler’s totient function
$\varphi(n)$ divides $n - 1$? -/
def S20261014_55 : Prop :=
  ∃ n > 1, ¬Prime n ∧ Nat.totient n ∣ n - 1

end Registry.LehmerTotientProblem

end
