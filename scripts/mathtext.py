#!/usr/bin/env python3
"""猜想名称里的 LaTeX 和 Markdown：转成普通文字（网站显示用），或转成网址名（slug）。

名称来自 formal-conjectures 等上游，常带 `$2^n$`、`$\\frac 1 3$`、`*abc*` 这类标记。
网站不加载公式渲染库，标题、搜索、浏览器标签页里也放不了 HTML，所以统一转成
Unicode 文字：`$2^n$` → `2ⁿ`，`$\\frac 1 3$` → `1/3`，`*abc*` → `abc`。
只用于显示；仓库里的原文不改。代码许可：Apache-2.0。
"""
import re, unicodedata

SYMBOLS = {
    "cdots": "⋯", "ldots": "…", "dots": "…", "le": "≤", "leq": "≤", "ge": "≥", "geq": "≥",
    "ne": "≠", "neq": "≠", "times": "×", "cdot": "·", "pm": "±", "infty": "∞", "to": "→",
    "in": "∈", "mid": "∣", "equiv": "≡", "approx": "≈", "sim": "∼",
    "alpha": "α", "beta": "β", "gamma": "γ", "delta": "δ", "epsilon": "ε", "varepsilon": "ε",
    "zeta": "ζ", "eta": "η", "theta": "θ", "lambda": "λ", "mu": "μ", "pi": "π", "rho": "ρ",
    "sigma": "σ", "tau": "τ", "phi": "φ", "varphi": "φ", "chi": "χ", "psi": "ψ", "omega": "ω",
    "Gamma": "Γ", "Delta": "Δ", "Theta": "Θ", "Lambda": "Λ", "Pi": "Π", "Sigma": "Σ", "Phi": "Φ", "Omega": "Ω",
    "mathbb": "", "mathrm": "", "mathcal": "", "operatorname": "", "text": "", "left": "", "right": "",
    ",": " ", ";": " ", "!": "", "quad": " ", "qquad": " ",
}
SUP = dict(zip("0123456789+-=()abcdeiklmnoprstx", "⁰¹²³⁴⁵⁶⁷⁸⁹⁺⁻⁼⁽⁾ᵃᵇᶜᵈᵉⁱᵏˡᵐⁿᵒᵖʳˢᵗˣ"))
SUB = dict(zip("0123456789+-=()aeiknmx", "₀₁₂₃₄₅₆₇₈₉₊₋₌₍₎ₐₑᵢₖₙₘₓ"))

def _group(s, i):
    """从 s[i] 读一个 TeX 参数：{…} 或单个字符，返回 (内容, 下一个位置)。"""
    while i < len(s) and s[i] == " ": i += 1
    if i >= len(s): return "", i
    if s[i] == "{":
        depth, j = 1, i + 1
        while j < len(s) and depth:
            depth += {"{": 1, "}": -1}.get(s[j], 0); j += 1
        return s[i+1:j-1], j
    if s[i] == "\\":
        m = re.match(r"\\[A-Za-z]+", s[i:])
        if m: return m.group(0), i + len(m.group(0))
    return s[i], i + 1

def _script(body, table, mark):
    body = _math(body)
    return "".join(table[c] for c in body) if body and all(c in table for c in body) else f"{mark}({body})" if len(body) > 1 else mark + body

def _math(s):
    out, i = [], 0
    while i < len(s):
        c = s[i]
        if c == "\\":
            m = re.match(r"\\([A-Za-z]+|.)", s[i:])
            name = m.group(1); i += len(m.group(0))
            if name in ("frac", "tfrac", "dfrac"):
                a, i = _group(s, i); b, i = _group(s, i)
                a, b = _math(a), _math(b)
                wrap = lambda x: x if re.fullmatch(r"[\w.]+", x) else f"({x})"
                out.append(f"{wrap(a)}/{wrap(b)}")
            elif name in ("sqrt",):
                a, i = _group(s, i); out.append(f"√{_math(a)}" if len(_math(a)) == 1 else f"√({_math(a)})")
            elif name in SYMBOLS: out.append(SYMBOLS[name])
            else: out.append(name)          # \tan、\log、\gcd 之类直接去掉反斜杠
        elif c in "^_":
            body, i = _group(s, i + 1)
            out.append(_script(body, SUP if c == "^" else SUB, c))
        elif c in "{}": i += 1
        else: out.append(c); i += 1
    return "".join(out)

def plain_text(s):
    """名称、参考资料标签 → 适合显示的普通文字。"""
    if not s: return s or ""
    s = re.sub(r"\$\$?(.+?)\$\$?", lambda m: _math(m.group(1)), s)
    s = re.sub(r"\*\*(.+?)\*\*", r"\1", s)
    s = re.sub(r"(?<![\w*])\*(?!\s)([^*]+?)(?<!\s)\*(?![\w*])", r"\1", s)
    s = re.sub(r"(?<![\w_])_(?!\s)([^_]+?)(?<!\s)_(?![\w_])", r"\1", s)
    return re.sub(r"[ \t]{2,}", " ", s).strip()

def ascii_words(s):
    """名称 → ASCII 单词列表：去掉标记，去掉英文所有格，重音字母转成不带重音的字母。"""
    s = plain_text(s)
    s = re.sub(r"['’]s\b", "", s)
    s = re.sub(r"[^\w]+", " ", s)   # 先把连接号、斜杠等标点换成空格，否则 Elliott–Halberstam 会粘成一个词
    s = unicodedata.normalize("NFKD", s).encode("ascii", "ignore").decode()
    return re.findall(r"[A-Za-z0-9]+", s)

# 网站顶层已有的目录和文件；猜想的网址名（现用或旧的）不能和它们重名，否则会覆盖这些页面
RESERVED_SLUGS = {"about", "ask", "chat", "edit", "essays", "proofs", "search", "api", "cdn-cgi", "index"}

def slugify(name, limit=80):
    """名称 → 网址名：小写、连字符分隔，超长时在单词边界截断。"""
    out = ""
    for w in ascii_words(name):
        nxt = (out + "-" + w.lower()) if out else w.lower()
        if len(nxt) > limit: break
        out = nxt
    return out or "-".join(w.lower() for w in ascii_words(name))[:limit]

def dir_name(name, limit=60):
    """名称 → 目录名（Lean 模块名的一段）：每个单词首字母大写，超长时在单词边界截断。"""
    out = ""
    for w in ascii_words(name):
        nxt = out + w[:1].upper() + w[1:]
        if len(nxt) > limit: break
        out = nxt
    return out

def html_text(s):
    """参考资料标签之类 → HTML：数学转成文字，*书名* 转成斜体，其余转义。"""
    import html
    s = re.sub(r"\$\$?(.+?)\$\$?", lambda m: _math(m.group(1)), s or "")
    s = html.escape(re.sub(r"\s+", " ", s).strip(), quote=True)
    s = re.sub(r"\*\*(.+?)\*\*", r"<strong>\1</strong>", s)
    return re.sub(r"(?<![\w*])\*(?!\s)([^*]+?)(?<!\s)\*(?![\w*])", r"<em>\1</em>", s)
