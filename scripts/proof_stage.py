#!/usr/bin/env python3
"""把提交的证明放进编译工作区：Submitted/<顶层名>…，并在 lakefile.toml 里加一个库。

只在没有密钥、只读权限的编译任务里运行。只拷贝 .lean 文件，不用对方的 lakefile，
所以证明只能依赖 Mathlib（钉死版本）和本登记库的表述模块。

用法：proof_stage.py <result.json>   （apply_edit.py 的输出，其中 proof 字段说明证明来源）
代码许可：Apache-2.0。
"""
import json, os, re, shutil, subprocess, sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
DEST = ROOT / "Submitted"
MAX_FILES, MAX_BYTES = 500, 20 * 1024 * 1024
ALLOWED_IMPORT = re.compile(r"^(Mathlib|Batteries|Aesop|Qq|Plausible|ProofWidgets|LeanSearchClient|ImportGraph|Lean|Std|Init)(\.|$)")
IMPORT_LINE = re.compile(r"^\s*(?:public\s+)?(?:meta\s+)?import\s+(?:all\s+)?([A-Za-z_][A-Za-z0-9_'.«»]*)", re.M)

def die(msg):
    print(msg, file=sys.stderr)
    Path("proof-out").mkdir(exist_ok=True)
    Path("proof-out/stage_error.txt").write_text(msg, encoding="utf-8")
    sys.exit(1)

def header(text):
    """只看文件开头的导入部分（去掉注释）。"""
    text = re.sub(r"/-.*?-/", "", text, flags=re.S)
    text = re.sub(r"--[^\n]*", "", text)
    return text

def main():
    spec = json.loads(Path(sys.argv[1]).read_text(encoding="utf-8"))["proof"]
    root, module = spec["root"], spec["module"]
    if DEST.exists(): shutil.rmtree(DEST)
    DEST.mkdir()
    if spec["kind"] == "pasted":
        (DEST / "Proof.lean").write_text(spec["text"] + "\n", encoding="utf-8")
    else:
        src = Path("/tmp/proof-src")
        if src.exists(): shutil.rmtree(src)
        env = {**os.environ, "GIT_TERMINAL_PROMPT": "0", "GIT_LFS_SKIP_SMUDGE": "1"}
        try:
            subprocess.run(["git", "init", "-q", str(src)], check=True, env=env)
            subprocess.run(["git", "-C", str(src), "fetch", "-q", "--depth", "1", spec["repo"], spec["commit"]],
                           check=True, env=env, timeout=600)
            subprocess.run(["git", "-C", str(src), "-c", "core.symlinks=false", "checkout", "-q", "FETCH_HEAD"],
                           check=True, env=env, timeout=600)
        except subprocess.SubprocessError:
            die(f"拉取 {spec['repo']} 的提交 {spec['commit']} 失败。请确认仓库是公开的、提交号正确。")
        files = []
        if (src / f"{root}.lean").is_file(): files.append(Path(f"{root}.lean"))
        if (src / root).is_dir():
            files += [p.relative_to(src) for p in (src / root).rglob("*.lean")]
        if not files: die(f"仓库里没有找到 {root}.lean 或 {root}/ 目录。")
        if len(files) > MAX_FILES: die(f"文件太多（{len(files)} 个，上限 {MAX_FILES}）。")
        total = 0
        for rel in files:
            p = src / rel
            if p.is_symlink() or not p.resolve().is_relative_to(src.resolve()): die(f"不接受符号链接：{rel}")
            total += p.stat().st_size
            if total > MAX_BYTES: die("证明文件总大小超过 20 MB。")
            (DEST / rel).parent.mkdir(parents=True, exist_ok=True)
            shutil.copyfile(p, DEST / rel)
    target = DEST / (module.replace(".", "/") + ".lean")
    if not target.is_file(): die(f"找不到模块 {module} 对应的文件 {module.replace('.', '/')}.lean。")
    stmt_mod = spec["statement_module"]
    bad = []
    for f in sorted(DEST.rglob("*.lean")):
        for imp in IMPORT_LINE.findall(header(f.read_text(encoding="utf-8", errors="replace"))):
            imp = imp.replace("«", "").replace("»", "")
            if ALLOWED_IMPORT.match(imp) or imp == root or imp.startswith(root + "."): continue
            if imp.startswith("Conjectures.") and re.fullmatch(r"Conjectures\.[A-Za-z0-9_]+\.S\d{8}_\d{2}", imp): continue
            bad.append(f"{f.relative_to(DEST)}：import {imp}")
    if bad:
        die("证明只能导入 Mathlib（及其依赖）、本登记库的表述模块（Conjectures.<猜想>.S<编号>）和自己的文件。不允许的导入：\n- " + "\n- ".join(bad))
    with open(ROOT / "lakefile.toml", "a", encoding="utf-8") as f:
        f.write(f'\n[[lean_lib]]\nname = "{root}"\nsrcDir = "Submitted"\nroots = ["{module}"]\n')
    print(f"staged {spec['kind']} proof: module {module}, theorem {spec['theorem']}, statement {spec['statement']} ({stmt_mod})")

if __name__ == "__main__":
    main()
