#!/usr/bin/env python3
"""表述文件的 Lean 代码规范（受限子集）。

登记库接受匿名提交的 Lean 代码。Lean 在编译期可以执行任意代码（#eval、
run_cmd、elab、macro、带 @[init] 的声明等），所以表述文件只允许一个很小的
子集。这是纵深防御的一层；另一层是编译不可信 Lean 的 CI 任务不持有任何密钥、
只有只读权限。

两个入口：
  check_fragment(text, kind)   检查用户提交的片段（kind = "proposition" 或 "helpers"）
  check_statement_file(src)    检查完整的表述文件是否符合生成模板
都返回错误信息列表（中文），空列表表示通过。
代码许可：Apache-2.0。
"""
import re

IMPORT_RE = re.compile(r"^(Mathlib|Batteries)(\.[A-Za-z_][A-Za-z0-9_']*)+$")
MAX_IMPORTS = 40
MAX_FRAGMENT = 20000

# 任何片段里都不允许出现的关键字与名称（按 Lean 标识符边界匹配）
FORBIDDEN_ALWAYS = [
    # 元编程、编译期执行
    "elab", "elab_rules", "macro", "macro_rules", "syntax", "declare_syntax_cat",
    "notation", "infix", "infixl", "infixr", "prefix", "postfix",
    "run_cmd", "run_elab", "run_meta", "run_tac", "by_elab",
    "initialize", "builtin_initialize", "attribute", "set_option",
    # 不可信或绕过内核
    "unsafe", "partial", "opaque", "axiom", "constant", "sorry", "admit",
    "native_decide", "native", "implemented_by", "extern", "export",
    "unsafeCast", "unsafeIO", "unsafeBaseIO", "ofReduceBool", "trustCompiler",
    # 系统接口
    "IO", "System", "Lean", "EIO", "BaseIO", "ST",
    # 结构性命令：会打乱生成的文件结构
    "import", "module", "namespace", "section", "end", "mutual",
    "universe", "variable", "omit", "include",
]
# 命题片段里还不允许出现任何声明命令
FORBIDDEN_IN_PROPOSITION = [
    "def", "theorem", "lemma", "example", "abbrev", "structure", "inductive",
    "class", "instance", "open", "deriving", "where", "private", "protected",
    "noncomputable", "irreducible_def",
]

IDENT_CHAR = "A-Za-z0-9_'!?\\u0370-\\u03FF\\u1F00-\\u1FFF\\u2100-\\u214F\\U0001D49C-\\U0001D59F"

def strip_comments(src):
    """去掉 Lean 注释（块注释可嵌套），文档字符串也一并去掉。字符串字面量不在
    允许范围内（片段里禁止双引号），所以这里不需要处理字符串。"""
    out, i, n, depth = [], 0, len(src), 0
    while i < n:
        if src.startswith("/-", i):
            depth += 1; i += 2; continue
        if depth and src.startswith("-/", i):
            depth -= 1; i += 2
            if depth == 0: out.append(" ")
            continue
        if depth:
            if src[i] == "\n": out.append("\n")
            i += 1; continue
        if src.startswith("--", i):
            j = src.find("\n", i)
            i = n if j < 0 else j
            continue
        out.append(src[i]); i += 1
    return "".join(out), depth

def _word_hits(code, words):
    hits = []
    for w in words:
        if re.search(rf"(?<![{IDENT_CHAR}.]){re.escape(w)}(?![{IDENT_CHAR}])", code):
            hits.append(w)
    return hits

def check_fragment(text, kind):
    errs = []
    if text is None: text = ""
    if len(text) > MAX_FRAGMENT:
        return [f"代码过长（{len(text)} 字符，上限 {MAX_FRAGMENT}）"]
    if "\x00" in text:
        return ["包含非法字符"]
    code, depth = strip_comments(text)
    if depth:
        errs.append("块注释 /- … -/ 没有闭合")
    if '"' in code:
        errs.append("不允许字符串字面量（双引号）")
    if "#" in code:
        errs.append("不允许 # 开头的命令（如 #eval、#check）")
    if re.search(r"@\[", code):
        errs.append("不允许属性标注 @[…]")
    if "$(" in code or "`(" in code:
        errs.append("不允许语法引用")
    bad = _word_hits(code, FORBIDDEN_ALWAYS)
    if kind == "proposition":
        bad += _word_hits(code, FORBIDDEN_IN_PROPOSITION)
        if not code.strip():
            errs.append("命题不能为空")
    if bad:
        errs.append("不允许使用：" + "、".join(f"`{w}`" for w in sorted(set(bad))))
    return errs

def check_imports(imports):
    errs = []
    if len(imports) > MAX_IMPORTS:
        errs.append(f"import 太多（上限 {MAX_IMPORTS}）")
    for imp in imports:
        if not IMPORT_RE.match(imp):
            errs.append(f"import 只能引入 Mathlib 或 Batteries 的模块：`{imp}`")
    return errs

FILE_RE = re.compile(
    r"^\s*module\s*\n"
    r"(?P<imports>(?:[ \t]*public import [^\n]+\n)+)"
    r"\s*@\[expose\] public section\s*\n"
    r"\s*namespace (?P<ns>Registry\.[A-Za-z][A-Za-z0-9_]*)\s*\n"
    r"(?P<body>.*?)\n"
    r"\s*end (?P=ns)\s*\n"
    r"\s*end\s*$", re.S)
BODY_RE = re.compile(
    r"^\s*(?:namespace (?P<aux>S\d{8}_\d{2}_aux)\s*\n(?P<helpers>.*?)\n\s*end (?P=aux)\s*\n)?"
    r"\s*(?:open (?P<open>S\d{8}_\d{2}_aux) in\s*\n)?"
    r"\s*def (?P<name>S\d{8}_\d{2}) : Prop :=\s*\n"
    r"(?P<prop>.*?)\s*$", re.S)

def check_statement_file(src):
    """完整表述文件必须是 scripts/apply_edit.py 生成的那种结构。"""
    code, depth = strip_comments(src)
    if depth: return ["块注释没有闭合"]
    m = FILE_RE.match(code)
    if not m:
        return ["文件结构不符合模板（module / public import … / @[expose] public section / namespace Registry.X / … / end Registry.X / end）"]
    imports = [l.strip()[len("public import "):].strip() for l in m.group("imports").strip().splitlines()]
    errs = check_imports(imports)
    b = BODY_RE.match(m.group("body"))
    if not b:
        return errs + ["正文结构不符合模板：应为（可选的辅助定义命名空间）+ 单个 `def S<编号> : Prop :=`"]
    if b.group("open") and b.group("open") != b.group("aux"):
        errs.append("open 的命名空间必须是本文件的辅助命名空间")
    if b.group("aux") and b.group("aux") != b.group("name") + "_aux":
        errs.append("辅助命名空间必须叫 <编号>_aux")
    if b.group("helpers") is not None:
        errs += ["辅助定义：" + e for e in check_fragment(b.group("helpers"), "helpers")]
    errs += ["命题：" + e for e in check_fragment(b.group("prop"), "proposition")]
    return errs

if __name__ == "__main__":
    import sys
    from pathlib import Path
    bad = 0
    for p in sys.argv[1:]:
        e = check_statement_file(Path(p).read_text(encoding="utf-8"))
        if e: bad += 1; print(p, *e, sep="\n  ")
    sys.exit(1 if bad else 0)
