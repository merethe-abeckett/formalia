#!/usr/bin/env python3
"""Patrol: model-assisted review of registered statements for Lean-level problems.

Scope is deliberately narrow. The patrol looks ONLY for problems in the Lean
code itself (ill-formed statement, trivially true/false, hidden axiom or sorry,
wrong declaration shape, broken under the pinned Mathlib). Whether a statement
is equivalent to the informal conjecture is OUT of scope and is never asked.

Two independent models review every statement. The combination rule, as decided
for the registry:
  * both flag a problem AND CI evidence exists (checker report not ok)  -> "deletion proposal" issue, public notice period starts
  * both flag a problem, no CI evidence                                 -> "patrol finding" issue, for the maintainer to look at
  * exactly one flags                                                   -> "patrol disagreement" issue, maintainer decides
  * neither flags                                                       -> nothing
Issues are deduplicated by a marker line, so a re-run never opens a second
issue for the same statement while the first is open.

Providers are configured by environment variables and use only the standard
library (no SDKs):
  QWEN_API_KEY, QWEN_BASE_URL (default DashScope OpenAI-compatible, intl), QWEN_MODEL (default qwen-plus)
  GEMINI_API_KEY, GEMINI_MODEL (default gemini-2.5-flash)
  GITHUB_TOKEN, GITHUB_REPOSITORY  (for opening issues; omitted => dry run)
Run with --dry-run to print verdicts without touching GitHub, and with
--fake to use a built-in stub provider for testing the plumbing.

Code licence: Apache-2.0.
"""
import argparse, json, os, sys, urllib.request, urllib.error, time
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
CONJ = ROOT / "Conjectures"
CHECK = ROOT / "build" / "check"
NOTICE_DAYS = 14

PROMPT = """You are reviewing ONE Lean 4 file from a registry of formal statements of
mathematical conjectures. The registry is a neutral catalogue: it lists formal
statements and does NOT judge whether they are equivalent to the informal
conjecture. You must not judge that either.

Your only job: report problems in the Lean code itself. Examples of in-scope problems:
- the statement is not a single `def <Name> : Prop := ...` as required;
- the proposition is trivially true or trivially false (vacuous hypotheses, `True`, a contradiction in the hypotheses, quantifying over an empty type);
- it uses `sorry`, declares an `axiom`/`opaque`/`constant`, or uses `native_decide`;
- it relies on a custom definition that contradicts or silently diverges from its name/docstring;
- it would not typecheck, or references a non-existent constant, under the pinned Mathlib.
OUT of scope (do not report): whether the formalisation matches the informal conjecture, choice of one Mathlib definition over another, style.

Pinned toolchain: {toolchain}
Checker report (facts produced by CI): {report}

File {path}:
```lean
{code}
```

Answer with ONLY a JSON object, no prose around it:
{{"problem": true|false, "category": "<short label or empty>", "reason": "<one or two sentences, empty if no problem>"}}
"""

def http_json(url, payload, headers, timeout=120):
    data = json.dumps(payload).encode()
    req = urllib.request.Request(url, data=data, headers={"Content-Type": "application/json", **headers})
    with urllib.request.urlopen(req, timeout=timeout) as r:
        return json.loads(r.read().decode())

def ask_qwen(prompt):
    key = os.environ["QWEN_API_KEY"]
    base = os.environ.get("QWEN_BASE_URL", "https://dashscope-intl.aliyuncs.com/compatible-mode/v1")
    model = os.environ.get("QWEN_MODEL", "qwen-plus")
    out = http_json(f"{base}/chat/completions",
        {"model": model, "messages": [{"role": "user", "content": prompt}], "temperature": 0},
        {"Authorization": f"Bearer {key}"})
    return out["choices"][0]["message"]["content"]

def ask_gemini(prompt):
    key = os.environ["GEMINI_API_KEY"]
    model = os.environ.get("GEMINI_MODEL", "gemini-2.5-flash")
    url = f"https://generativelanguage.googleapis.com/v1beta/models/{model}:generateContent"
    out = http_json(url,
        {"contents": [{"parts": [{"text": prompt}]}], "generationConfig": {"temperature": 0, "responseMimeType": "application/json"}},
        {"x-goog-api-key": key})
    return out["candidates"][0]["content"]["parts"][0]["text"]

def ask_fake(prompt):
    # Stub for testing the plumbing: flags anything containing `True ∧` or `sorry`.
    flag = ("sorry" in prompt.split("```lean",1)[1]) or ("True ∧" in prompt)
    return json.dumps({"problem": flag, "category": "stub" if flag else "", "reason": "stub provider" if flag else ""})

def parse_verdict(text):
    text = text.strip()
    if text.startswith("```"):
        text = text.strip("`")
        if text.startswith("json"): text = text[4:]
    try:
        obj = json.loads(text)
        return {"problem": bool(obj.get("problem")), "category": str(obj.get("category", "")), "reason": str(obj.get("reason", "")), "raw": None}
    except Exception:
        return {"problem": False, "category": "unparseable", "reason": "", "raw": text[:500]}

def entries():
    tc = (ROOT / "lean-toolchain").read_text().strip()
    for cdir in sorted(p for p in CONJ.iterdir() if p.is_dir()):
        for mj in sorted(cdir.glob("S*.json")):
            meta = json.loads(mj.read_text(encoding="utf-8"))
            lean = mj.with_suffix(".lean")
            rep_path = CHECK / (meta["module"] + ".json")
            rep = json.loads(rep_path.read_text()) if rep_path.exists() else None
            decl = None
            if rep:
                decl = next((d for d in rep["declarations"] if d["name"] == meta["declaration"]), None)
            yield {"meta": meta, "path": str(lean.relative_to(ROOT)), "code": lean.read_text(encoding="utf-8"),
                   "report": decl, "toolchain": tc, "ci_ok": bool(decl and decl.get("ok") and decl.get("is_prop"))}

# ---------- GitHub issues ----------
def gh(method, path, payload=None):
    tok = os.environ["GITHUB_TOKEN"]; repo = os.environ["GITHUB_REPOSITORY"]
    url = f"https://api.github.com/repos/{repo}{path}"
    data = json.dumps(payload).encode() if payload is not None else None
    req = urllib.request.Request(url, data=data, method=method, headers={
        "Authorization": f"Bearer {tok}", "Accept": "application/vnd.github+json", "Content-Type": "application/json"})
    with urllib.request.urlopen(req, timeout=60) as r:
        return json.loads(r.read().decode() or "null")

def open_issue_once(marker, title, body, labels):
    existing = gh("GET", "/issues?state=open&per_page=100&labels=" + ",".join(labels))
    for it in existing:
        if marker in (it.get("body") or ""):
            return it["html_url"], False
    it = gh("POST", "/issues", {"title": title, "body": body, "labels": labels})
    return it["html_url"], True

def issue_text(kind, e, verdicts):
    sid = e["meta"]["id"]; conj = e["meta"]["conjecture"]
    marker = f"<!-- patrol:{kind}:{sid} -->"
    lines = [marker, f"Statement `#{sid}` ({conj}), file `{e['path']}`.", ""]
    if kind == "deletion-proposal":
        lines += [f"**Deletion proposal.** Both patrol models flag a Lean-level problem and the CI checker report is not clean. "
                  f"Public notice period: {NOTICE_DAYS} days from the opening of this issue. If the problem stands, the entry is **archived** (moved to `Archive/`, id kept, never reused), not deleted.", ""]
    elif kind == "patrol-finding":
        lines += ["**Patrol finding.** Both patrol models flag a Lean-level problem, but CI reports the entry as clean. Maintainer to verify. No notice period starts until CI evidence exists.", ""]
    else:
        lines += ["**Patrol disagreement.** Exactly one patrol model flags a problem. The maintainer decides whether to proceed.", ""]
    lines += ["Scope reminder: equivalence to the informal conjecture is out of scope for the patrol and for this issue.", "", "| model | problem | category | reason |", "|---|---|---|---|"]
    for name, v in verdicts.items():
        lines.append(f"| {name} | {'yes' if v['problem'] else 'no'} | {v['category']} | {v['reason'].replace('|','/')} |")
    rep = e["report"]
    lines += ["", "CI checker report: " + ("not available" if rep is None else f"ok={rep['ok']}, is_prop={rep['is_prop']}, axioms={rep['axioms']}, sorry={rep['uses_sorry']}, native_decide={rep['uses_native_decide']}, non_standard={rep['non_standard_axioms']}")]
    return marker, lines

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--dry-run", action="store_true", help="print verdicts, do not open issues")
    ap.add_argument("--fake", action="store_true", help="use the stub provider instead of real models")
    ap.add_argument("--only", help="only this statement id")
    args = ap.parse_args()

    if args.fake:
        providers = {"fake-A": ask_fake, "fake-B": ask_fake}
    else:
        providers = {}
        if os.environ.get("QWEN_API_KEY"): providers["qwen"] = ask_qwen
        if os.environ.get("GEMINI_API_KEY"): providers["gemini"] = ask_gemini
        if len(providers) < 2:
            print("patrol needs two providers (QWEN_API_KEY and GEMINI_API_KEY); got", list(providers), file=sys.stderr)
            return 2
    can_post = not args.dry_run and os.environ.get("GITHUB_TOKEN") and os.environ.get("GITHUB_REPOSITORY")

    summary = []
    for e in entries():
        if args.only and e["meta"]["id"] != args.only: continue
        prompt = PROMPT.format(toolchain=e["toolchain"], report=json.dumps(e["report"]), path=e["path"], code=e["code"])
        verdicts = {}
        for name, fn in providers.items():
            try:
                verdicts[name] = parse_verdict(fn(prompt))
            except (urllib.error.URLError, KeyError, json.JSONDecodeError) as ex:
                verdicts[name] = {"problem": False, "category": "error", "reason": f"provider error: {ex}", "raw": None}
            time.sleep(0.5)
        flags = [v["problem"] for v in verdicts.values()]
        if all(flags):
            kind = "deletion-proposal" if not e["ci_ok"] else "patrol-finding"
        elif any(flags):
            kind = "patrol-disagreement"
        else:
            kind = None
        sid = e["meta"]["id"]
        summary.append((sid, kind, verdicts))
        print(f"#{sid}: {kind or 'clean'}  " + "  ".join(f"{n}={'FLAG' if v['problem'] else 'ok'}" for n, v in verdicts.items()))
        if kind and can_post:
            marker, lines = issue_text(kind, e, verdicts)
            url, created = open_issue_once(marker, f"[{kind}] statement #{sid}", "\n".join(lines), [kind])
            print("   ", "opened" if created else "already open", url)
        elif kind:
            marker, lines = issue_text(kind, e, verdicts)
            print("    (dry run) would open issue:\n    " + "\n    ".join(lines[:6]))
    return 0

if __name__ == "__main__":
    sys.exit(main())
