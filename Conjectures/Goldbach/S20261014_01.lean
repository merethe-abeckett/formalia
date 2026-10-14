/-
Lean Statement Registry — entry #20261014-01
Conjecture: Goldbach's conjecture
Content licence: CC-BY-4.0 (see LICENSE-CONTENT)

This file registers ONE formal statement. It makes no claim about whether the
statement is equivalent to the informal conjecture. That question is left to
mathematicians; the registry only lists.
-/
module

public import Mathlib.Data.Nat.Prime.Defs
public import Mathlib.Algebra.Group.Even

@[expose] public section

namespace Registry.Goldbach

/-- Statement #20261014-01.

Every even natural number greater than 2 is the sum of two primes, where
"prime" is `Nat.Prime` from Mathlib. -/
def S20261014_01 : Prop :=
  ∀ n : ℕ, 2 < n → Even n → ∃ p q : ℕ, Nat.Prime p ∧ Nat.Prime q ∧ n = p + q

end Registry.Goldbach

end
