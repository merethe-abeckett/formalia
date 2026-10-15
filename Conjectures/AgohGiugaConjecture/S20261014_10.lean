/-
Formalia · 条目 #20261014-10
猜想：Agoh-Giuga conjecture
内容许可：Apache-2.0（与原作相同）
原作版权：Copyright 2025 The Formal Conjectures Authors，Apache License 2.0

改编自 google-deepmind/formal-conjectures 仓库的 FormalConjectures/Wikipedia/AgohGiuga.lean。
改动：去掉 `answer(sorry) ↔`、`@[category …]` 等属性与 `sorry`，theorem 的参数改写成 `∀`，
只登记命题本身，写成 `def`。
-/
module

public import Mathlib.Algebra.Group.Defs
public import Mathlib.Algebra.Group.Int.Defs
public import Mathlib.Data.Nat.Prime.Defs
public import Mathlib.NumberTheory.Bernoulli

@[expose] public section

namespace Registry.AgohGiugaConjecture

namespace S20261014_10_aux

open scoped Nat
/-

The **Agoh-Giuga Conjecture**.

References:
* Wikipedia: https://en.wikipedia.org/wiki/Agoh-Giuga_conjecture
* Wikipedia: https://en.wikipedia.org/wiki/Giuga_number
* G. Giuga, _Su una presumibile proprieta caratteristica dei numeri primi_
* E. Bedocchi, _Note on a conjecture about prime numbers_
* D. Borwein, J. M. Borwein, P. B. Borwein, and R. Girgensohn, _Giuga’s conjecture on primality_
* V. Tipu, _A Note on Giuga’s Conjecture_

-/

def AgohGiugaCongr : Prop :=
  ∀ p ≥ 2, p.Prime ↔ ∃ (k : ℤ),
  let B := bernoulli' (p - 1)
  p * B.num + B.den = k * p^2

end S20261014_10_aux

open S20261014_10_aux in
/-- 表述 #20261014-10。

The **Agoh-Giuga Conjecture**, Agoh's formulation -/
def S20261014_10 : Prop :=
  AgohGiugaCongr

end Registry.AgohGiugaConjecture

end
