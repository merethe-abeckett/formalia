/-
Formalia · 条目 #20261014-08
猜想：Riemann Hypothesis and its generalizations
内容许可：Apache-2.0（与原作相同）
原作版权：Copyright 2025 The Formal Conjectures Authors，Apache License 2.0

改编自 google-deepmind/formal-conjectures 仓库的 FormalConjectures/Millennium/RiemannHypothesis.lean。
改动：去掉 `answer(sorry) ↔`、`@[category …]` 等属性与 `sorry`，theorem 的参数改写成 `∀`，
只登记命题本身，写成 `def`。
-/
module

public import Mathlib.NumberTheory.LSeries.RiemannZeta

@[expose] public section

namespace Registry.RiemannHypothesisAndItsGeneralizations

/-- 表述 #20261014-08。

The **Riemann Hypothesis**: all non-trivial zeros of the Riemann zeta function have real
part $\frac{1}{2}$. That is, if $\zeta(s) = 0$, $s \neq 1$, and $s$ is not a trivial zero
$-2(n+1)$ for some $n \in \mathbb{N}$, then $\operatorname{Re}(s) = \frac{1}{2}$.

This is the official Millennium Prize Problem as posed by the
[Clay Mathematics Institute](https://www.claymath.org/wp-content/uploads/2022/05/riemann.pdf).

This uses the `RiemannHypothesis` type from Mathlib, which is defined as
`∀ (s : ℂ), riemannZeta s = 0 → (¬∃ n : ℕ, s = -2 * (n + 1)) → s ≠ 1 → s.re = 1 / 2`. -/
def S20261014_08 : Prop :=
  RiemannHypothesis

end Registry.RiemannHypothesisAndItsGeneralizations

end
