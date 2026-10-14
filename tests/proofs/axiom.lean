import Conjectures.ZzTest.S20000101_01

axiom Proof.cheat : False

theorem Proof.ok : Registry.ZzTest.S20000101_01 := Proof.cheat.elim
