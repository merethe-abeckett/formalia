/-
Formalia · 条目 #20261014-93
猜想：Erdős Problem 1003
内容许可：Apache-2.0（与原作相同）
原作版权：Copyright 2025 The Formal Conjectures Authors，Apache License 2.0

改编自 google-deepmind/formal-conjectures 仓库的 FormalConjectures/ErdosProblems/1003.lean。
改动：去掉 `answer(sorry) ↔`、`@[category …]` 等属性与 `sorry`，theorem 的参数改写成 `∀`，
只登记命题本身，写成 `def`。
-/
module

public import Mathlib.Order.Filter.Defs
public import Mathlib.Data.Finite.Defs
public import Mathlib.Data.Nat.Totient
public import Mathlib.Data.Set.Defs

@[expose] public section

namespace Registry.ErdosProblem1003

namespace S20261014_93_aux

open scoped Nat

open Filter

def statement : Prop :=
  Set.Infinite {n | φ n = φ (n + 1)}

end S20261014_93_aux

open S20261014_93_aux in
/-- 表述 #20261014-93。

Are there infinitely many solutions to $\phi(n) = \phi(n+1)$, where $\phi$ is the Euler totient
function? -/
def S20261014_93 : Prop :=
  statement

end Registry.ErdosProblem1003

end
