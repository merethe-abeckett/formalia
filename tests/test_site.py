# 网站显示与网址名的测试：python3 tests/test_site.py
# 1. 名称里的 LaTeX / Markdown 转成普通文字；网址名、目录名的生成
# 2. 在临时副本里完整生成网站：旧网址名的跳转页、首页没有原始 LaTeX、手机端断行规则
# 3. 旧网址名与现用网址名冲突时，元数据校验必须拒绝
import json, re, shutil, subprocess, sys, tempfile
from pathlib import Path
ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / "scripts"))
import mathtext as mt

fails = 0
def check(cond, msg):
    global fails
    if not cond: fails += 1; print("FAIL:", msg)
def eq(got, want, what):
    check(got == want, f"{what}: got {got!r}, want {want!r}")

# ---------- 1. 文字转换 ----------
for src, want in [
    ("Digit $2$ in base $3$ representation of $2^n$", "Digit 2 in base 3 representation of 2ⁿ"),
    ("The $\\frac 1 3$–$\\frac 2 3$ conjecture", "The 1/3–2/3 conjecture"),
    ("Integer values of $\\tan(\\arctan 1 + \\arctan 2 + \\cdots + \\arctan n)$", "Integer values of tan(arctan 1 + arctan 2 + ⋯ + arctan n)"),
    ("primes up to $10^{700}$", "primes up to 10⁷⁰⁰"),
    ("$\\frac{n+1}{2}$", "(n+1)/2"),
    ("$x_{12}$ and $a^{p-1}$", "x₁₂ and aᵖ⁻¹"),
    ("$\\zeta(3) \\ne 0$", "ζ(3) ≠ 0"),
    ("$a^{q}$ and $2^{n+q}$", "a^q and 2^(n+q)"),   # 没有对应上标字符时退回 ^
    ("*abc* conjecture", "abc conjecture"),
    ("**Bold** name", "Bold name"),
    ("2 * 3 * 4", "2 * 3 * 4"),                 # 乘号不是斜体
    ("Goldbach's conjecture", "Goldbach's conjecture"),
    ("", ""),
]:
    eq(mt.plain_text(src), want, f"plain_text({src!r})")
eq(mt.html_text("L. Babai, *On <groups>*, $p^2$"), "L. Babai, <em>On &lt;groups&gt;</em>, p²", "html_text escapes and italicises")

# ---------- 网址名与目录名 ----------
for name, slug, dirname in [
    ("Elliott–Halberstam conjecture", "elliott-halberstam-conjecture", "ElliottHalberstamConjecture"),
    ("The Erdős–Moser equation", "the-erdos-moser-equation", "TheErdosMoserEquation"),
    ("Büchi's problem", "buchi-problem", "BuchiProblem"),
    ("Agrawal's conjecture", "agrawal-conjecture", "AgrawalConjecture"),
    ("The $\\frac 1 3$–$\\frac 2 3$ conjecture", "the-1-3-2-3-conjecture", "The1323Conjecture"),
    ("Digit $2$ in base $3$ representation of $2^n$", "digit-2-in-base-3-representation-of-2n", "Digit2InBase3RepresentationOf2n"),
]:
    eq(mt.slugify(name), slug, f"slugify({name!r})")
    eq(mt.dir_name(name), dirname, f"dir_name({name!r})")
long = "An Arithmetic Sum Associated with the Classical Theta Function and Some Further Words"
s = mt.slugify(long)
check(len(s) <= 80 and not s.endswith("-") and s.split("-")[-1] in long.lower().split(), f"slug cut at a word boundary: {s!r}")
dn = mt.dir_name(long)
check(len(dn) <= 60 and any(dn.endswith(w[:1].upper() + w[1:]) for w in long.split()), f"dir name cut at a word boundary: {dn!r}")

# 网页登记新建猜想用的就是这两个函数
import apply_edit
eq(apply_edit.dir_name_from("Kummer–Vandiver conjecture"), ("KummerVandiverConjecture", "kummer-vandiver-conjecture"), "apply_edit.dir_name_from")
try:
    apply_edit.dir_name_from("$1/3$ conjecture"); check(False, "name starting with a digit must be rejected")
except apply_edit.EditError: pass
for reserved in ("Search", "About"):
    try:
        apply_edit.apply_statement({"data": {"new_conjecture": {"name": reserved, "informal": "x"}, "imports": ["Mathlib.Logic.Basic"], "prop": "True"}}, "t", "2026-10-16T00:00:00Z")
        check(False, f"new conjecture named {reserved!r} must be rejected (reserved slug)")
    except apply_edit.EditError as e:
        check("保留" in str(e), f"reserved slug {reserved!r} rejected for the right reason: {e}")

# ---------- 2. 完整生成网站 ----------
def copy_repo(dst):
    ignore = shutil.ignore_patterns(".git", "_site", ".lake", "build", "__pycache__", "node_modules")
    shutil.copytree(ROOT, dst, ignore=ignore)

with tempfile.TemporaryDirectory() as t:
    r = Path(t) / "repo"; copy_repo(r)
    out = subprocess.run([sys.executable, str(r / "scripts" / "build_site.py")], capture_output=True, text=True)
    check(out.returncode == 0, f"build_site failed: {out.stderr[-500:]}")
    site = r / "_site"
    conjs = [json.loads(p.read_text(encoding="utf-8")) for p in (r / "Conjectures").glob("*/conjecture.json")]
    renamed = [c for c in conjs if c.get("former_slugs")]
    check(renamed, "expected at least one conjecture with former_slugs")
    for c in renamed:
        ids = [json.loads(p.read_text(encoding="utf-8"))["id"] for p in (r / "Conjectures").glob(f"*/S*.json")
               if json.loads(p.read_text(encoding="utf-8"))["conjecture"] == c["slug"]]
        for old in c["former_slugs"]:
            page = site / old / "index.html"
            check(page.exists() and f'../{c["slug"]}/index.html' in page.read_text(encoding="utf-8"), f"redirect {old} -> {c['slug']}")
            for sid in ids:
                sp = site / old / sid / "index.html"
                check(sp.exists() and f'../../{c["slug"]}/{sid}/index.html' in sp.read_text(encoding="utf-8"), f"redirect {old}/{sid}")
        check((site / c["slug"] / "index.html").exists(), f"new page {c['slug']} exists")
    index = (site / "index.html").read_text(encoding="utf-8")
    check(not re.search(r"\$[^$<]{1,80}\$", index), "index.html shows raw $…$")
    check(">abc conjecture<" in index, "markdown *abc* stripped on the index cards")
    data = json.loads((site / "data.json").read_text(encoding="utf-8"))
    raw = next(c for c in conjs if "$" in json.dumps(c.get("references") or [], ensure_ascii=False))
    eq(data["conjectures"][raw["slug"]]["references"], raw["references"], "edit form keeps raw references for conflict checks")
    css = (site / "style.css").read_text(encoding="utf-8")
    check("overflow-wrap:anywhere" in css, "phone CSS lets long strings wrap")

    # ---------- 3. 旧网址名冲突 ----------
    a, b = sorted((r / "Conjectures").glob("*/conjecture.json"))[:2]
    ca, cb = json.loads(a.read_text(encoding="utf-8")), json.loads(b.read_text(encoding="utf-8"))
    ca["former_slugs"] = ca.get("former_slugs", []) + [cb["slug"]]
    a.write_text(json.dumps(ca, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    out = subprocess.run([sys.executable, str(r / "scripts" / "validate_meta.py")], capture_output=True, text=True)
    check(out.returncode != 0 and "已被" in out.stdout, f"former slug colliding with a live slug must fail: {out.stdout[-300:]}")
    ca["former_slugs"] = ["Bad Slug"]
    a.write_text(json.dumps(ca, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    out = subprocess.run([sys.executable, str(r / "scripts" / "validate_meta.py")], capture_output=True, text=True)
    check(out.returncode != 0 and "网址名只能用" in out.stdout, "malformed former slug must fail")
    ca["former_slugs"] = ["search"]
    a.write_text(json.dumps(ca, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    out = subprocess.run([sys.executable, str(r / "scripts" / "validate_meta.py")], capture_output=True, text=True)
    check(out.returncode != 0 and "保留" in out.stdout, "reserved former slug must fail")

print("site tests:", "PASS" if not fails else f"{fails} FAIL")
sys.exit(1 if fails else 0)
