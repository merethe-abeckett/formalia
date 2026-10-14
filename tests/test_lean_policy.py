# Lean 规范的对抗测试：python3 tests/test_lean_policy.py
import sys; from pathlib import Path; sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "scripts"))
from lean_policy import check_fragment as cf, check_imports, check_statement_file
ok_props = [
 "∀ n : ℕ, 2 < n → Even n → ∃ p q : ℕ, Nat.Prime p ∧ Nat.Prime q ∧ n = p + q",
 "∀ x : ℝ, 0 < x → Real.log x < x  -- 注释里写 #eval 和 end 没关系",
 "/- 块注释 /- 嵌套 -/ 里写 IO 也没关系 -/ True",
 "Set.Infinite {p : ℕ | Nat.Prime p ∧ Nat.Prime (p + 2)}",
 "∀ f : ℕ → ℕ, (fun x => f x) = f",
]
bad_props = {
 "#eval IO.println 1": "#",
 "True\ndef evil : Nat := 1": "def",
 "True\n#eval (IO.Process.run {cmd := \"sh\"})": "#",
 "True\nrun_cmd Lean.logInfo m!\"x\"": "run_cmd",
 "True\nelab \"x\" : term => pure default": "elab",
 "(by native_decide : 1 + 1 = 2) = (by native_decide : 1 + 1 = 2)": "native_decide",
 "True\nend Registry.Goldbach\nend\n#exit": "end",
 "True ∧ sorry": "sorry",
 "True -/ #eval 1": "#",
 "/- unterminated True": "闭合",
 "True\n@[init] def x : IO Unit := pure ()": "@[",
 "True\nmacro \"m\" : term => `(1)": "macro",
 "True\nset_option maxHeartbeats 0": "set_option",
 "True\nattribute [instance] foo": "attribute",
 "(decide (config := {native := true}) : True)": "native",
 "True\nimport Lean": "import",
 "True\nopen Lean in run_cmd pure ()": "open",
 "True\ntheorem t : False := by simp": "theorem",
 "": "空",
}
fails = 0
for p in ok_props:
    e = cf(p, "proposition")
    if e: fails += 1; print("FALSE REJECT", repr(p), e)
for p, needle in bad_props.items():
    e = cf(p, "proposition")
    if not e or not any(needle in x for x in e): fails += 1; print("MISSED", repr(p), e)
ok_helpers = ["/-- 孪生素数对 -/\ndef IsTwin (p : ℕ) : Prop := Nat.Prime p ∧ Nat.Prime (p + 2)",
              "abbrev MyNat := ℕ\nstructure Pt where\n  x : ℕ\n  y : ℕ"]
bad_helpers = {"def x : Nat := 1\n#eval x": "#", "unsafe def x : Nat := 1": "unsafe",
               "def x : IO Unit := pure ()": "IO", "namespace Foo\nend Foo": "namespace",
               "partial def f (n : Nat) : Nat := f n": "partial", "axiom a : False": "axiom",
               "def s := \"x\"": "双引号", "instance : Inhabited Nat := ⟨Lean.Name.anonymous.hash.toNat⟩": "Lean"}
for p in ok_helpers:
    e = cf(p, "helpers")
    if e: fails += 1; print("FALSE REJECT helper", repr(p), e)
for p, needle in bad_helpers.items():
    e = cf(p, "helpers")
    if not e or not any(needle in x for x in e): fails += 1; print("MISSED helper", repr(p), e)
assert not check_imports(["Mathlib.Data.Nat.Prime.Defs", "Batteries.Data.List.Basic"])
for bad in ["Lean", "Lean.Elab", "Mathlib", "Mathlib.Tactic; #eval 1", "FormalConjectures.Util", "Mathlib.X\n#eval"]:
    if not check_imports([bad]): fails += 1; print("MISSED import", bad)
# 完整文件：篡改结构
good = open(Path(__file__).resolve().parent.parent / "Conjectures/Goldbach/S20261014_01.lean", encoding="utf-8").read()
assert not check_statement_file(good)
tampered = [good.replace("namespace Registry.Goldbach", "namespace Registry.Goldbach\n#eval 1"),
            good.replace("public import Mathlib.Algebra.Group.Even", "public import Lean"),
            good.replace("end Registry.Goldbach", "theorem x : True := trivial\nend Registry.Goldbach"),
            good + "\n#eval 1\n",
            good.replace("@[expose] public section", "@[expose] public section\nset_option x 1")]
for t in tampered:
    if not check_statement_file(t): fails += 1; print("MISSED tampered file")
print("policy tests:", "PASS" if not fails else f"{fails} FAIL")
sys.exit(1 if fails else 0)
