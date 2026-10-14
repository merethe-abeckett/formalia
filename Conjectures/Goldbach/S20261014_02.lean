/-
Lean Statement Registry — entry #20261014-02
Conjecture: Goldbach's conjecture
Content licence: CC-BY-4.0 (see LICENSE-CONTENT)

Adapted from google-deepmind/formal-conjectures,
FormalConjectures/Wikipedia/GoldbachConjecture.lean (Apache-2.0), where the
statement appears as the right-hand side of `answer(sorry) ↔ ...`. Only the
proposition is registered here, as a `def`, so the file contains no `sorry`.
-/
module

public import Mathlib.Algebra.Prime.Defs
public import Mathlib.Algebra.Ring.Nat
public import Mathlib.Algebra.Group.Even

@[expose] public section

namespace Registry.Goldbach

/-- Statement #20261014-02.

Same shape as #20261014-01, but "prime" is the general ring-theoretic `Prime`
from Mathlib, specialised to `ℕ`, as written in formal-conjectures. -/
def S20261014_02 : Prop :=
  ∀ n : ℕ, 2 < n → Even n → ∃ p q : ℕ, Prime p ∧ Prime q ∧ n = p + q

end Registry.Goldbach

end
