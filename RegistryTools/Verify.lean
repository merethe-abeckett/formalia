/-
Formalia — 证明验证器
代码许可：Apache-2.0

用法：lake exe verify <out.json> <证明模块> <定理名> <表述常量> <表述模块> [prove|disprove]

检查一份提交的证明是否真的证明（或证否）了登记库里的某条表述：
  * 同时导入证明模块和登记库自己编译的表述模块。证明里如果自己定义了一个同名的
    “表述”，导入会因为重复声明而失败。
  * 定理必须是 theorem。证明时类型必须**正好**是表述常量本身；证否时必须正好是
    `¬ 表述常量`（不能是改弱、改写的版本）。
  * 表述常量必须来自登记库的表述模块。
  * 定理只能依赖三个标准公理（propext、Classical.choice、Quot.sound），不能有 sorry
    或自定义公理。
  * native_decide 允许，但要标出来：它会生成形如 `decide P = true` 的辅助公理。
    这种公理谁都能伪造，所以验证器不信它，而是让 Lean 内核自己把 `decide P`
    算一遍（相当于用 decide 重做）。内核算出 true 才接受；算不出来就拒绝。
结果写进 out.json；全部通过时退出码为 0。
-/
import Lean

open Lean Meta

namespace FormaliaVerify

def standardAxioms : List Name := [``propext, ``Classical.choice, ``Quot.sound]

def moduleOf (env : Environment) (n : Name) : Option Name :=
  env.getModuleIdxFor? n |>.map fun i => env.header.moduleNames[i.toNat]!

/-- native_decide 生成的辅助公理：名字里有 `_native` 和 `native_decide` 两段。 -/
def isNativeDecideAxiom (n : Name) : Bool :=
  n.components.any (· == `_native) && n.components.any (· == `native_decide)

/-- 让内核重新计算 native_decide 的结论：公理的类型必须是 `decide P = true`，
内核要能把左边算成 `true`（等于用 `Eq.refl true` 证明它）。成功返回 none，失败返回原因。 -/
def kernelRecheck (env : Environment) (ax : Name) : IO (Option String) := do
  let some ci := env.find? ax | return some s!"找不到 {ax}"
  match ci.type.eq? with
  | some (ty, _, rhs) =>
    unless ty == mkConst ``Bool && rhs == mkConst ``Bool.true do
      return some s!"{ax} 不是 `… = true` 的形式"
    let decl := Declaration.thmDecl {
      name := `_formalia_native_recheck, levelParams := [], type := ci.type,
      value := mkApp2 (mkConst ``Eq.refl [1]) (mkConst ``Bool) (mkConst ``Bool.true) }
    match env.addDeclCore 0 decl none with
    | .ok _ => return none
    | .error e =>
      return some s!"内核没能把 native_decide 那一步重新算出 true（{ax}）：{← (e.toMessageData {}).toString}"
  | none => return some s!"{ax} 不是 `… = true` 的形式"

def main (args : List String) : IO UInt32 := do
  match args with
  | out :: proofMod :: thm :: stmt :: stmtMod :: rest =>
    let disprove := rest == ["disprove"]
    if !(rest == [] || rest == ["prove"] || disprove) then
      IO.eprintln "最后一个参数只能是 prove 或 disprove"; return 2
    let proofMod := proofMod.toName; let thm := thm.toName
    let stmt := stmt.toName; let stmtMod := stmtMod.toName
    let mut reasons : Array String := #[]
    let mut axs : Array Name := #[]
    let mut natives : Array Name := #[]
    initSearchPath (← findSysroot)
    let imports : Array Import := #[{ module := stmtMod }, { module := proofMod, importAll := true }]
    match ← (importModules imports {} 0).toBaseIO with
    | .error e =>
      reasons := reasons.push s!"导入失败（证明是否重新定义了表述，或缺少文件？）：{e}"
    | .ok env =>
      match env.find? stmt with
      | none => reasons := reasons.push s!"找不到表述常量 {stmt}"
      | some _ =>
        if moduleOf env stmt != some stmtMod then
          reasons := reasons.push s!"表述常量 {stmt} 不是来自登记库的模块 {stmtMod}"
      match env.find? thm with
      | none => reasons := reasons.push s!"找不到定理 {thm}。它需要是公开（public）的声明。"
      | some ci =>
        match ci with
        | .thmInfo _ => pure ()
        | _ => reasons := reasons.push s!"{thm} 不是 theorem"
        let want := if disprove then mkApp (mkConst ``Not) (mkConst stmt) else mkConst stmt
        if ci.type != want then
          reasons := reasons.push (if disprove
            then s!"{thm} 的类型不是 ¬ {stmt}。证否请把定理写成 `theorem {thm} : ¬ {stmt} := …`"
            else s!"{thm} 的类型不是 {stmt} 本身。请把定理写成 `theorem {thm} : {stmt} := …`")
        if moduleOf env thm == some stmtMod then
          reasons := reasons.push s!"{thm} 不在证明模块里"
        let r ← ((collectAxioms thm : CoreM (Array Name)).toIO
          { fileName := "<verify>", fileMap := default } { env }).toBaseIO
        match r with
        | .error e => reasons := reasons.push s!"统计公理失败：{e}"
        | .ok (a, _) =>
          axs := a
          for x in a do
            if standardAxioms.contains x then continue
            if x == ``sorryAx then reasons := reasons.push "证明里有 sorry"
            else if isNativeDecideAxiom x then
              match ← kernelRecheck env x with
              | none => natives := natives.push x
              | some why => reasons := reasons.push why
            else reasons := reasons.push s!"用了非标准公理 {x}"
    let ok := reasons.isEmpty
    let json := Json.mkObj [
      ("ok", Json.bool ok), ("lean_version", Json.str Lean.versionString),
      ("theorem", Json.str (toString thm)), ("statement", Json.str (toString stmt)),
      ("direction", Json.str (if disprove then "disprove" else "prove")),
      ("axioms", Json.arr ((axs.filter (!natives.contains ·)).map fun a => Json.str (toString a))),
      ("native_decide", Json.arr (natives.map fun a => Json.str (toString a))),
      ("reasons", Json.arr (reasons.map Json.str))]
    IO.FS.writeFile out (json.pretty ++ "\n")
    let neg := if disprove then "¬ " else ""
    IO.println (if ok then s!"[ok] {thm} : {neg}{stmt}，公理 = {axs}，native_decide = {natives}" else s!"[FAIL] {reasons}")
    return if ok then 0 else 1
  | _ =>
    IO.eprintln "usage: lake exe verify <out.json> <ProofModule> <theorem> <Statement> <StatementModule> [prove|disprove]"
    return 2

end FormaliaVerify

def main := FormaliaVerify.main
