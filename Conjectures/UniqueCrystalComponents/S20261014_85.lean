/-
Formalia · 条目 #20261014-85
猜想：Unique Crystal Components
内容许可：Apache-2.0（与原作相同）
原作版权：Copyright 2025 The Formal Conjectures Authors，Apache License 2.0

改编自 google-deepmind/formal-conjectures 仓库的 FormalConjectures/Arxiv/1601.03081/UniqueCrystalComponents.lean。
改动：去掉 `answer(sorry) ↔`、`@[category …]` 等属性与 `sorry`，theorem 的参数改写成 `∀`，
只登记命题本身，写成 `def`。
-/
module

public import Mathlib.Algebra.Group.Defs
public import Mathlib.Algebra.Group.Nat.Defs
public import Mathlib.Algebra.Ring.Nat
public import Mathlib.Algebra.Ring.Parity
public import Mathlib.Data.Finset.Defs
public import Mathlib.Data.Finset.Insert

@[expose] public section

namespace Registry.UniqueCrystalComponents

namespace S20261014_85_aux

def IsCrystalWithComponents (n a b : ℕ) : Prop :=
  Odd n ∧ 1 < a ∧ 1 < b ∧ n = a * b ∧ 2 * (a + 1) * (b + 1) ∣ (a + b)^2 + (a * b + 1)^2

end S20261014_85_aux

open S20261014_85_aux in
/-- 表述 #20261014-85。

If $n = ab$ is a crystal, then there are no other pairs of
positive integers $c, d > 1$, different from the couple $a, b$, such that $n = cd$ and
$B(c, d) ∈ ℕ$, i.e., the components of the crystals are unique. -/
def S20261014_85 : Prop :=
  ∀ (n a b c d : ℕ)
      (hab : IsCrystalWithComponents n a b) (hcd : IsCrystalWithComponents n c d), ({a, b} : Finset ℕ) = {c, d}

end Registry.UniqueCrystalComponents

end
