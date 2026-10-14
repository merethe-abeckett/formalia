/-
Formalia — 证明验证器
代码许可：Apache-2.0

用法：lake exe verify <out.json> <证明模块> <定理名> <表述常量> <表述模块>

检查一份提交的证明是否真的证明了登记库里的某条表述：
  * 同时导入证明模块和登记库自己编译的表述模块。证明里如果自己定义了一个同名的
    “表述”，导入会因为重复声明而失败。
  * 定理必须是 theorem，类型必须**正好**是表述常量本身（不能是改弱、改写的版本）。
  * 表述常量必须来自登记库的表述模块。
  * 定理只能依赖三个标准公理（propext、Classical.choice、Quot.sound）；
    不能有 sorry、native_decide 或自定义公理。
结果写进 out.json；全部通过时退出码为 0。
-/
import Lean

open Lean Meta

namespace FormaliaVerify

def standardAxioms : List Name := [``propext, ``Classical.choice, ``Quot.sound]

def moduleOf (env : Environment) (n : Name) : Option Name :=
  env.getModuleIdxFor? n |>.map fun i => env.header.moduleNames[i.toNat]!

def main (args : List String) : IO UInt32 := do
  match args with
  | [out, proofMod, thm, stmt, stmtMod] =>
    let proofMod := proofMod.toName; let thm := thm.toName
    let stmt := stmt.toName; let stmtMod := stmtMod.toName
    let mut reasons : Array String := #[]
    let mut axs : Array Name := #[]
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
        if ci.type != Expr.const stmt [] then
          reasons := reasons.push s!"{thm} 的类型不是 {stmt} 本身。请把定理写成 `theorem {thm} : {stmt} := …`"
        if moduleOf env thm == some stmtMod then
          reasons := reasons.push s!"{thm} 不在证明模块里"
        let r ← ((collectAxioms thm : CoreM (Array Name)).toIO
          { fileName := "<verify>", fileMap := default } { env }).toBaseIO
        match r with
        | .error e => reasons := reasons.push s!"统计公理失败：{e}"
        | .ok (a, _) =>
          axs := a
          for x in a do
            if !standardAxioms.contains x then
              reasons := reasons.push (if x == ``sorryAx then "证明里有 sorry"
                else s!"用了非标准公理 {x}")
    let ok := reasons.isEmpty
    let json := Json.mkObj [
      ("ok", Json.bool ok), ("lean_version", Json.str Lean.versionString),
      ("theorem", Json.str (toString thm)), ("statement", Json.str (toString stmt)),
      ("axioms", Json.arr (axs.map fun a => Json.str (toString a))),
      ("reasons", Json.arr (reasons.map Json.str))]
    IO.FS.writeFile out (json.pretty ++ "\n")
    IO.println (if ok then s!"[ok] {thm} : {stmt}，公理 = {axs}" else s!"[FAIL] {reasons}")
    return if ok then 0 else 1
  | _ =>
    IO.eprintln "usage: lake exe verify <out.json> <ProofModule> <theorem> <Statement> <StatementModule>"
    return 2

end FormaliaVerify

def main := FormaliaVerify.main
