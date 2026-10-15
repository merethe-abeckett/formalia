/-
Formalia · 条目 #20261014-87
猜想：Digit $2$ in base $3$ representation of $2^n$
内容许可：Apache-2.0（与原作相同）
原作版权：Copyright 2025 The Formal Conjectures Authors，Apache License 2.0

改编自 google-deepmind/formal-conjectures 仓库的 FormalConjectures/Arxiv/2107.12475/CollatzLike.lean。
改动：去掉 `answer(sorry) ↔`、`@[category …]` 等属性与 `sorry`，theorem 的参数改写成 `∀`，
只登记命题本身，写成 `def`。
-/
module

public import Mathlib.Algebra.Group.Defs
public import Mathlib.Algebra.Group.Nat.Defs
public import Mathlib.Data.Nat.Digits.Defs

@[expose] public section

namespace Registry.Digit2InBase3RepresentationOf2N

/-- 表述 #20261014-87。

For $n > 8$, $2^n$ is not the the sum of distinct powers of $3$. Expressed here in terms of the base $3$ digits of $n$.

This conjecture is equivalent to the halting of a $15$-state $2$-symbol Turing Machine.

TODO(lezeau): Formalize the Turing Machine version of this problem.

Source: *Hardness of Busy Beaver Value BB(15)*: https://link.springer.com/chapter/10.1007/978-3-031-72621-7_9
This is also https://arxiv.org/abs/2107.12475. -/
def S20261014_87 : Prop :=
  ∀ (n : ℕ) (hn : 8 < n), 2 ∈ Nat.digits 3 (2^n)

end Registry.Digit2InBase3RepresentationOf2N

end
