#!/usr/bin/env python3
"""Validate registry metadata: ids, file naming, required fields, and that
each .json points at a declaration that really exists in its .lean file."""
import json, re, sys
from pathlib import Path

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
        if re.search(r"\bsorry\b", code): err(lf, "contains `sorry`")
        if re.search(r"^\s*(axiom|opaque|constant)\b", code, re.M): err(lf, "declares an axiom/opaque/constant")
        for cp in meta.get("claimed_proofs") or []:
            for k in ("claimant", "date", "url"):
                if not cp.get(k): err(mj, f"claimed proof missing {k}")

if errors:
    print("\n".join(errors)); sys.exit(1)
print("metadata ok")
