#!/usr/bin/env python3
"""Validate registry metadata: ids, file naming, required fields, and that
each .json points at a declaration that really exists in its .lean file."""
import json, re, sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parent))
import lean_policy
import licenses

ROOT = Path(__file__).resolve().parent.parent / "Conjectures"
ID_RE = re.compile(r"^(\d{8})-(\d{2})$")
REQUIRED = ["id", "conjecture", "module", "declaration", "submitted_by", "submitted_at", "source"]
errors = []

def err(p, msg): errors.append(f"{p}: {msg}")

for cdir in sorted(p for p in ROOT.iterdir() if p.is_dir()):
    cj = cdir / "conjecture.json"
    if not cj.exists():
        err(cdir, "missing conjecture.json"); continue
    conj = json.loads(cj.read_text(encoding="utf-8"))
    for k in ("slug", "name", "informal"):
        if not conj.get(k): err(cj, f"missing field {k}")
    seen = set()
    for lf in sorted(cdir.glob("S*.lean")):
        mj = lf.with_suffix(".json")
        if not mj.exists():
            err(lf, "missing matching .json"); continue
        meta = json.loads(mj.read_text(encoding="utf-8"))
        for k in REQUIRED:
            if k not in meta: err(mj, f"missing field {k}")
        m = ID_RE.match(meta.get("id", ""))
        if not m: err(mj, f"id must look like YYYYMMDD-NN, got {meta.get('id')!r}")
        else:
            expected = f"S{m.group(1)}_{m.group(2)}"
            if lf.stem != expected: err(lf, f"file should be named {expected}.lean for id {meta['id']}")
        if meta.get("id") in seen: err(mj, "duplicate id"); 
        seen.add(meta.get("id"))
        if meta.get("conjecture") != conj.get("slug"): err(mj, "conjecture does not match conjecture.json slug")
        exp_mod = "Conjectures." + cdir.name + "." + lf.stem
        if meta.get("module") != exp_mod: err(mj, f"module should be {exp_mod}")
        decl = meta.get("declaration", "").split(".")[-1]
        src = lf.read_text(encoding="utf-8")
        # strip block and line comments before scanning for forbidden tokens
        code = re.sub(r"/-.*?-/", "", src, flags=re.S)
        code = re.sub(r"--[^\n]*", "", code)
        if not re.search(rf"^\s*def\s+{re.escape(decl)}\s*:\s*Prop\s*:=", code, re.M):
            err(lf, f"expected `def {decl} : Prop :=`")
        for e in lean_policy.check_statement_file(src): err(lf, "Lean 规范：" + e)
        if re.search(r"\bsorry\b", code): err(lf, "contains `sorry`")
        if re.search(r"^\s*(axiom|opaque|constant)\b", code, re.M): err(lf, "declares an axiom/opaque/constant")
        for cp in meta.get("claimed_proofs") or []:
            for k in ("claimant", "date", "url"):
                if not cp.get(k): err(mj, f"claimed proof missing {k}")
        lic = meta.get("license")
        if lic is not None and lic not in licenses.ALLOWED: err(mj, f"不支持的许可：{lic!r}")
        if (meta.get("source") or {}).get("kind") in ("adapted", "verbatim") and not lic:
            err(mj, "改编或照录的表述必须显式声明 license")
        urls = [(meta.get("source") or {}).get("url")] + [c.get("url") for c in meta.get("claimed_proofs") or []] \
             + [l.get("url") for l in meta.get("external_links") or []]
        for u in urls:
            if u and not re.match(r"^https?://[^\s<>\"'`]+$", u): err(mj, f"非法链接：{u!r}")

# ---------- 解读 ----------
ESSAYS = ROOT.parent / "Essays"
ARCH = ROOT.parent / "Archive"
EID_RE = re.compile(r"^J(\d{8})-(\d{2})$")
slugs = {json.loads((d / "conjecture.json").read_text(encoding="utf-8")).get("slug")
         for d in ROOT.iterdir() if (d / "conjecture.json").exists()}
sids = {json.loads(f.read_text(encoding="utf-8")).get("id") for base in (ROOT, ARCH) if base.exists() for f in base.glob("*/S*.json")}
if ESSAYS.exists():
    for mj in sorted(ESSAYS.glob("*.json")):
        meta = json.loads(mj.read_text(encoding="utf-8"))
        m = EID_RE.match(meta.get("id", ""))
        if not m: err(mj, f"解读编号应为 JYYYYMMDD-NN，实际为 {meta.get('id')!r}"); continue
        if mj.stem != f"J{m.group(1)}_{m.group(2)}": err(mj, f"文件名应为 J{m.group(1)}_{m.group(2)}.json")
        if not mj.with_suffix(".md").exists(): err(mj, "缺少同名 .md 正文")
        for k in ("title", "author", "submitted_at"):
            if not meta.get(k): err(mj, f"缺少字段 {k}")
        about = meta.get("about") or []
        if not about: err(mj, "about 至少要有一个表述编号或猜想")
        for a in about:
            if a not in sids and a not in slugs: err(mj, f"about 里的 {a!r} 不是已有的表述编号或猜想")
        if meta.get("license", licenses.DEFAULT) not in licenses.ALLOWED: err(mj, f"不支持的许可：{meta.get('license')!r}")
    for md in ESSAYS.glob("*.md"):
        if not md.with_suffix(".json").exists() and md.name != "README.md": err(md, "缺少同名 .json")

if errors:
    print("\n".join(errors)); sys.exit(1)
print("metadata ok")
