/-
Formalia · 条目 #20261014-03
猜想：考拉兹猜想
内容许可：Apache-2.0
经网站提交：merethe-abeckett(经 Claude 代提交)

本文件只登记一条形式化表述，不对它是否等价于原猜想作任何判断。
-/
module

public import Mathlib.Algebra.Group.Nat.Even
public import Mathlib.Order.Iterate

@[expose] public section

namespace Registry.CollatzConjecture

/-- 表述 #20261014-03。

对每个正整数 n,存在 m 使得对 n 迭代 m 次 Collatz 映射后得到 1。映射内联写出:偶数取 n / 2,奇数取 3 * n + 1。 -/
def S20261014_03 : Prop :=
  ∀ n : ℕ, 0 < n → ∃ m : ℕ, (fun k : ℕ => if Even k then k / 2 else 3 * k + 1)^[m] n = 1

end Registry.CollatzConjecture

end
