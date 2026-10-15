/-
Formalia · 条目 #20261014-83
猜想：Cunningham chains — Jones's conjecture
内容许可：Apache-2.0（与原作相同）
原作版权：Copyright 2025 The Formal Conjectures Authors，Apache License 2.0

改编自 google-deepmind/formal-conjectures 仓库的 FormalConjectures/Arxiv/1104.1579/CunninghamChain.lean。
改动：去掉 `answer(sorry) ↔`、`@[category …]` 等属性与 `sorry`，theorem 的参数改写成 `∀`，
只登记命题本身，写成 `def`。
-/
module

public import Mathlib.Data.Finite.Defs
public import Mathlib.Data.Nat.Prime.Defs
public import Mathlib.Data.Set.Defs

@[expose] public section

namespace Registry.CunninghamChainsJonesConjecture

namespace S20261014_83_aux

def firstKindTerm (p : ℕ) : ℕ → ℕ
  | 0     => p
  | n + 1 => 2 * firstKindTerm p n + 1

def IsFirstKindChainOfLength (p k : ℕ) : Prop :=
  0 < k ∧ (∀ i < k, (firstKindTerm p i).Prime) ∧ ¬(firstKindTerm p k).Prime

end S20261014_83_aux

open S20261014_83_aux in
/-- 表述 #20261014-83。

Jones's conjecture (first kind): for every positive integer $k$, there are
infinitely many primes $p$ that start a first-kind Cunningham chain of
exactly length $k$. -/
def S20261014_83 : Prop :=
  ∀ (k : ℕ) (hk : 0 < k), Set.Infinite {p : ℕ | IsFirstKindChainOfLength p k}

end Registry.CunninghamChainsJonesConjecture

end
