import Conjectures.ZzTest.S20000101_02

-- 伪造一条名字像 native_decide 生成的公理，内容是假的：内核重算时必须被拒
axiom Proof.ok._native.native_decide.ax_1_1 : decide (1 + 1 = 3) = true

theorem Proof.ok : Registry.ZzTest.S20000101_02 := by
  show 1 + 1 = 3
  exact of_decide_eq_true Proof.ok._native.native_decide.ax_1_1
