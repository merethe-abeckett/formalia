/-
Lean 表述登记库 · 条目 #20261014-01
猜想：哥德巴赫猜想
内容许可：CC-BY-4.0

本文件只登记一条形式化表述。它不对“该表述是否等价于原猜想”作任何判断，
这个问题留给数学家讨论；登记库只负责列出。
-/
module

public import Mathlib.Data.Nat.Prime.Defs
public import Mathlib.Algebra.Group.Even

@[expose] public section

namespace Registry.Goldbach

/-- 表述 #20261014-01。

每个大于 2 的偶自然数都是两个素数之和，其中“素数”取 Mathlib 的 `Nat.Prime`。 -/
def S20261014_01 : Prop :=
  ∀ n : ℕ, 2 < n → Even n → ∃ p q : ℕ, Nat.Prime p ∧ Nat.Prime q ∧ n = p + q

end Registry.Goldbach

end
