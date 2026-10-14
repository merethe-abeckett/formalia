#!/usr/bin/env python3
"""为每条表述生成 AI 导读（Gemini），写入 Guides/<猜想>/S<编号>.md。

导读只做两件事：逐个解释表述用到的定义，把量词和条件翻译成自然语言。
喂给模型的材料是 Lean 代码、检查器报告中的直接依赖，以及这些依赖在钉死
版本 Mathlib 源码中的定义片段，让模型解释真实定义而不是凭记忆。

用法：
  scripts/gen_guides.py            为没有导读、或 Lean 文件比导读新的条目生成
  scripts/gen_guides.py --force    全部重新生成
  scripts/gen_guides.py --fake     不调用模型，用占位文本测试流程
需要环境变量 GEMINI_API_KEY（可选 GEMINI_MODEL，默认 gemini-3.8-flash）。
代码许可：Apache-2.0。
"""
import argparse, json, os, re, sys, datetime
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parent))
import llm_gemini

ROOT = Path(__file__).resolve().parent.parent
CONJ = ROOT / "Conjectures"
CHECK = ROOT / "build" / "check"
GUIDES = ROOT / "Guides"
MATHLIB = ROOT / ".lake" / "packages" / "mathlib"
SKIP_MODULES = ("Init.", "Lean.", "Std.")   # 核心语法常量不需要解释

PROMPT = """你在为“Lean 表述登记库”撰写一条形式化表述的导读。登记库是中立目录：只列出 Lean 4 形式化表述及其事实，不判断它是否等价于原猜想。你的导读也必须遵守这一点。

你只做两件事：
1. 逐个解释下面列出的每个 Mathlib 定义在这条表述中的含义。以给出的源码片段为准，不要凭记忆。
2. 把表述的量词、前提和结论逐句翻译成自然语言。

禁止：评价表述好坏，比较它与原猜想是否一致，推测作者意图，讨论其他可能的写法。

输出为简体中文 Markdown，不要标题，分成两节，分别以“**定义解释**”和“**逐句翻译**”开头。每个定义一个要点，写清楚它在 Lean 中接受什么参数、返回什么。总长度控制在 400 字以内。

表述文件 {path}：
```lean
{code}
```

直接依赖的定义及其在 Mathlib（{mathlib_rev}）中的源码片段：
{snippets}
"""

def mathlib_rev():
    try:
        for p in json.loads((ROOT / "lake-manifest.json").read_text())["packages"]:
            if p["name"] == "mathlib": return p.get("inputRev") or p["rev"][:12]
    except Exception: pass
    return "?"

def source_snippet(module, const):
    """在钉死版本的 Mathlib 源码中找 const 的定义，返回带文档字符串的片段（约 20 行）。"""
    if not module or module.startswith(SKIP_MODULES) or not module.startswith("Mathlib."):
        return None
    f = MATHLIB / (module.replace(".", "/") + ".lean")
    if not f.exists(): return None
    short = const.split(".")[-1]
    lines = f.read_text(encoding="utf-8", errors="replace").splitlines()
    kw = r"(def|theorem|lemma|structure|class|inductive|abbrev|instance)"
    head = re.compile(rf"^\s*(@\[[^\]]*\]\s*)?((public|protected|private|noncomputable|nonrec)\s+)*{kw}\s+{re.escape(short)}(?![\w.'])")
    any_decl = re.compile(rf"^\s*(@\[[^\]]*\]\s*)?((public|protected|private|noncomputable|nonrec)\s+)*{kw}\s+\S")
    for i, l in enumerate(lines):
        if not head.match(l): continue
        # 向上吸收紧邻的属性行和文档字符串
        j = i
        while j > 0 and lines[j-1].strip().startswith("@["): j -= 1
        if j > 0 and lines[j-1].strip().endswith("-/"):
            k = j - 1
            while k >= 0 and not lines[k].lstrip().startswith("/--"): k -= 1
            if k >= 0 and j - k <= 15: j = k
        end = i + 1
        while end < len(lines) and end - i < 20 and lines[end].strip() != "" and not any_decl.match(lines[end]) and not lines[end].lstrip().startswith("/--"):
            end += 1
        return f"-- {module}\n" + "\n".join(lines[j:end])
    # 回退：由 `to_additive` 从乘法版本自动生成的定义（如 Even 来自 IsSquare）
    for i, l in enumerate(lines):
        if not any_decl.match(l): continue
        j = i
        while j > 0 and lines[j-1].strip() != "" and not any_decl.match(lines[j-1]): j -= 1
        block = "\n".join(lines[j:i])
        if "to_additive" in block and re.search(rf"`{re.escape(short)}\b", block):
            end = i + 1
            while end < len(lines) and end - i < 20 and lines[end].strip() != "" and not any_decl.match(lines[end]):
                end += 1
            return f"-- {module}\n-- 注：`{short}` 由 to_additive 从下面的乘法版本自动生成，把 * 读作 +。\n" + "\n".join(lines[j:end])
    return None

def entries():
    for cdir in sorted(p for p in CONJ.iterdir() if p.is_dir()):
        for mj in sorted(cdir.glob("S*.json")):
            meta = json.loads(mj.read_text(encoding="utf-8"))
            lean = mj.with_suffix(".lean")
            rep_path = CHECK / (meta["module"] + ".json")
            decl = None
            if rep_path.exists():
                rep = json.loads(rep_path.read_text())
                decl = next((d for d in rep["declarations"] if d["name"] == meta["declaration"]), None)
            yield cdir.name, meta, lean, decl

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--force", action="store_true"); ap.add_argument("--fake", action="store_true")
    a = ap.parse_args()
    if not a.fake and not os.environ.get("GEMINI_API_KEY"):
        print("需要 GEMINI_API_KEY", file=sys.stderr); return 2
    rev = mathlib_rev(); n = 0
    for cname, meta, lean, decl in entries():
        out = GUIDES / cname / (lean.stem + ".md")
        if out.exists() and not a.force and out.stat().st_mtime >= lean.stat().st_mtime:
            continue
        snippets = []
        for d in (decl or {}).get("direct_dependencies", []):
            sn = source_snippet(d.get("module"), d["name"])
            if sn: snippets.append(f"```lean\n{sn}\n```")
        prompt = PROMPT.format(path=str(lean.relative_to(ROOT)), code=lean.read_text(encoding="utf-8"),
                               mathlib_rev=rev, snippets="\n".join(snippets) or "（未找到 Mathlib 源码片段）")
        if a.fake:
            text = "**定义解释**\n\n- （占位）\n\n**逐句翻译**\n\n（占位）"
        else:
            text = llm_gemini.generate(prompt, temperature=0.2)
        model = "fake" if a.fake else llm_gemini.resolve_model()
        header = f"<!-- 由 {model} 于 {datetime.date.today().isoformat()} 生成，依据 Mathlib {rev} 的源码片段。可人工修改。 -->\n\n"
        out.parent.mkdir(parents=True, exist_ok=True)
        out.write_text(header + text + "\n", encoding="utf-8")
        print("wrote", out.relative_to(ROOT), f"({len(snippets)} 个源码片段)")
        n += 1
    print(f"{n} 份导读已生成")
    return 0

if __name__ == "__main__":
    sys.exit(main())
