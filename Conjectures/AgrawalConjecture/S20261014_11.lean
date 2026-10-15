/-
Formalia · 条目 #20261014-11
猜想：Agrawal's conjecture
内容许可：Apache-2.0（与原作相同）
原作版权：Copyright 2025 The Formal Conjectures Authors，Apache License 2.0

改编自 google-deepmind/formal-conjectures 仓库的 FormalConjectures/Wikipedia/Agrawal.lean。
改动：去掉 `answer(sorry) ↔`、`@[category …]` 等属性与 `sorry`，theorem 的参数改写成 `∀`，
只登记命题本身，写成 `def`。
-/
module

public import Mathlib.Algebra.Group.Defs
public import Mathlib.Algebra.GroupWithZero.Defs
public import Mathlib.Algebra.Polynomial.Basic
public import Mathlib.Algebra.Quotient
public import Mathlib.Algebra.Ring.Defs
public import Mathlib.Algebra.Ring.Hom.Defs
public import Mathlib.Data.FunLike.Basic
public import Mathlib.Data.Int.Cast.Defs
public import Mathlib.Data.Nat.Cast.Defs
public import Mathlib.Data.Nat.Prime.Defs
public import Mathlib.Data.Set.Defs
public import Mathlib.Data.ZMod.Defs
public import Mathlib.RingTheory.Ideal.Defs
public import Mathlib.RingTheory.Ideal.Quotient.Defs
public import Mathlib.RingTheory.Ideal.Span

@[expose] public section

namespace Registry.AgrawalConjecture

namespace S20261014_11_aux

open Polynomial

end S20261014_11_aux

open S20261014_11_aux in
/-- 表述 #20261014-11。

**Agrawal's Primality Conjecture.**

Does the congruence $(X-1)^n \equiv X^n - 1 \pmod{n, X^r-1}$ imply
$n$ is prime (with a specific exception for $n^2 \equiv 1 \pmod{r}$)?

While the "if" direction is a known theorem, the "only if" direction
remains a conjecture. -/
def S20261014_11 : Prop :=
  ∀ (n r : ℕ), n > 1 → r > 0 → n.gcd r = 1 →
        let R := Polynomial (ZMod n)
        let X : R := Polynomial.X
        let I : Ideal R := Ideal.span ({X^r - 1} : Set R)
        Ideal.Quotient.mk I ((X - 1)^n) = Ideal.Quotient.mk I (X^n - 1) →
        (n.Prime ∨ (n^2 : ZMod r) = 1)

end Registry.AgrawalConjecture

end
