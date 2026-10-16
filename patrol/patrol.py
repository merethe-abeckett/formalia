#!/usr/bin/env python3
"""Patrol: model-assisted review of registered statements for Lean-level problems.

Scope is deliberately narrow. The patrol looks ONLY for problems in the Lean
code itself (ill-formed statement, trivially true/false, hidden axiom or sorry,
wrong declaration shape, broken under the pinned Mathlib). Whether a statement
is equivalent to the informal conjecture is OUT of scope and is never asked.

Two independent models review every statement. With only one provider configured
the patrol still runs, but a flag can only open a "patrol finding" for the
maintainer; deletion proposals always need two models. The combination rule:
  * both flag a problem AND CI evidence exists (checker report not ok)  -> "deletion proposal" issue, public notice period starts
  * both flag a problem, checker report clean OR missing                -> "patrol finding" issue, for the maintainer to look at
  * exactly one flags                                                   -> "patrol disagreement" issue, maintainer decides
  * neither flags                                                       -> nothing
A missing checker report is NOT CI evidence: `lake build` stops at the first
broken module, so one bad file leaves every entry without a report.
Issues are deduplicated by a marker line, so a re-run never opens a second
issue for the same statement while the first is open.

Providers are configured by environment variables and use only the standard
library (no SDKs). An empty variable counts as unset, because the workflow
passes `${{ vars.X }}` as "" when the repository variable does not exist:
  QWEN_API_KEY, QWEN_BASE_URL (default DashScope OpenAI-compatible, intl), QWEN_MODEL (default qwen-plus)
  GEMINI_API_KEY, GEMINI_MODEL (default gemini-3.8-flash)
  GITHUB_TOKEN, GITHUB_REPOSITORY  (for opening issues; omitted => dry run)
Run with --dry-run to print verdicts without touching GitHub, and with
--fake to use a built-in stub provider for testing the plumbing.

Code licence: Apache-2.0.
"""
import argparse, json, os, sys, urllib.request, urllib.error, time
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "scripts"))
import llm_gemini

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

Answer with ONLY a JSON object, no prose around it. Write "category" and "reason" in Simplified Chinese:
{{"problem": true|false, "category": "<短标签，无问题则留空>", "reason": "<一两句话，无问题则留空>"}}
"""

def http_json(url, payload, headers, timeout=120):
    data = json.dumps(payload).encode()
    req = urllib.request.Request(url, data=data, headers={"Content-Type": "application/json", **headers})
    with urllib.request.urlopen(req, timeout=timeout) as r:
        return json.loads(r.read().decode())

def env(name, default):
    """环境变量；未设置或为空字符串时用默认值。"""
    return (os.environ.get(name) or "").strip() or default

def ask_qwen(prompt):
    key = os.environ["QWEN_API_KEY"]
    base = env("QWEN_BASE_URL", "https://dashscope-intl.aliyuncs.com/compatible-mode/v1").rstrip("/")
    model = env("QWEN_MODEL", "qwen-plus")
    out = http_json(f"{base}/chat/completions",
        {"model": model, "messages": [{"role": "user", "content": prompt}], "temperature": 0},
        {"Authorization": f"Bearer {key}"})
    return out["choices"][0]["message"]["content"]

def ask_gemini(prompt):
    return llm_gemini.generate(prompt, temperature=0, json_mode=True)

def strip_lean_comments(code):
    """去掉 Lean 的行注释和（可嵌套的）块注释，只留代码。"""
    out, i, depth = [], 0, 0
    while i < len(code):
        two = code[i:i+2]
        if two == "/-": depth += 1; i += 2; continue
        if depth and two == "-/": depth -= 1; i += 2; continue
        if not depth and two == "--":
            j = code.find("\n", i); i = len(code) if j < 0 else j; continue
        if not depth: out.append(code[i])
        i += 1
    return "".join(out)

def ask_fake(prompt):
    # Stub for testing the plumbing: flags code (not comments) containing `True ∧` or `sorry`.
    code = strip_lean_comments(prompt.split("```lean", 1)[1].rsplit("```", 1)[0])
    flag = ("sorry" in code) or ("True ∧" in code)
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
        print(f"[警告] 模型输出不是 JSON: {text[:200]!r}", file=sys.stderr)
        return {"problem": False, "category": "unparseable", "reason": "输出无法解析", "raw": text[:500]}

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
                   "report": decl, "toolchain": tc, "ci": ci_status(rep, decl)}

def ci_status(rep, decl):
    """检查器给出的事实：'ok' 通过，'fail' 未通过，'missing' 没有报告（不算证据）。"""
    if rep is None: return "missing"
    if decl is None: return "fail"     # 模块检查过了，却找不到登记的声明
    return "ok" if decl.get("ok") and decl.get("is_prop") else "fail"

def decide_kind(flags, ci):
    """按 docs/DELETION.md 的规则，由各模型的标记和 CI 事实决定开哪种议题。"""
    if len(flags) == 1:
        return "patrol-finding" if flags[0] else None
    if flags and all(flags):
        return "deletion-proposal" if ci == "fail" else "patrol-finding"
    if any(flags):
        return "patrol-disagreement"
    return None

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
    lines = [marker, f"表述 `#{sid}`（{conj}），文件 `{e['path']}`。", ""]
    if kind == "deletion-proposal":
        lines += [f"**提删公示。** 两个巡查模型都标记了 Lean 层面的问题，且 CI 检查器报告未通过。"
                  f"公示期：自本议题开启起 {NOTICE_DAYS} 天。若问题成立，该条目将被**归档**（移入 `Archive/`，编号保留、永不复用），而不是删除。", ""]
    elif kind == "patrol-finding":
        if len(verdicts) == 1:
            lines += ["**巡查发现（单模型）。** 当前只配置了一个巡查模型，它标记了 Lean 层面的问题。请维护者核实。提删公示需要两个独立模型加 CI 证据。", ""]
        elif e["ci"] == "missing":
            lines += ["**巡查发现。** 两个巡查模型都标记了 Lean 层面的问题，但本次没有该条目的检查器报告，无法确认 CI 是否通过。请维护者核实。没有 CI 证据前不进入公示。", ""]
        else:
            lines += ["**巡查发现。** 两个巡查模型都标记了 Lean 层面的问题，但 CI 报告该条目干净。请维护者核实。没有 CI 证据前不进入公示。", ""]
    else:
        lines += ["**巡查意见不一。** 只有一个巡查模型标记了问题。由维护者裁决是否继续。", ""]
    lines += ["范围提醒：该表述是否等价于原猜想，不在巡查和本议题的范围内。", "", "| 模型 | 有问题 | 类型 | 理由 |", "|---|---|---|---|"]
    for name, v in verdicts.items():
        lines.append(f"| {name} | {'是' if v['problem'] else '否'} | {v['category']} | {v['reason'].replace('|','/')} |")
    rep = e["report"]
    lines += ["", "CI 检查器报告：" + ({"missing": "不可用", "fail": "模块已检查，但报告中没有这条声明"}[e["ci"]] if rep is None else f"ok={rep['ok']}, is_prop={rep['is_prop']}, axioms={rep['axioms']}, sorry={rep['uses_sorry']}, native_decide={rep['uses_native_decide']}, non_standard={rep['non_standard_axioms']}")]
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
        if not providers:
            print("patrol needs at least one provider (QWEN_API_KEY and/or GEMINI_API_KEY)", file=sys.stderr)
            return 2
        if len(providers) == 1:
            print(f"single-provider mode ({list(providers)[0]}): a flag opens a patrol-finding only; "
                  "deletion proposals need two independent models.")
    can_post = not args.dry_run and os.environ.get("GITHUB_TOKEN") and os.environ.get("GITHUB_REPOSITORY")

    summary = []
    had_error = False
    for e in entries():
        if args.only and e["meta"]["id"] != args.only: continue
        prompt = PROMPT.format(toolchain=e["toolchain"], report=json.dumps(e["report"]), path=e["path"], code=e["code"])
        verdicts = {}
        for name, fn in providers.items():
            try:
                verdicts[name] = parse_verdict(fn(prompt))
            except (llm_gemini.GeminiError, urllib.error.URLError, KeyError, json.JSONDecodeError) as ex:
                verdicts[name] = {"problem": False, "category": "error", "reason": f"接口错误: {ex}", "raw": None}
                had_error = True
                print(f"[错误] {name} 审查 #{e['meta']['id']} 失败: {ex}", file=sys.stderr)
            time.sleep(0.5)
        kind = decide_kind([v["problem"] for v in verdicts.values()], e["ci"])
        sid = e["meta"]["id"]
        summary.append((sid, kind, verdicts))
        def tag(v):
            if v["category"] in ("error", "unparseable"): return "ERR"
            return "FLAG" if v["problem"] else "ok"
        print(f"#{sid}: {kind or 'clean'}  " + "  ".join(f"{n}={tag(v)}" for n, v in verdicts.items()))
        if kind and can_post:
            marker, lines = issue_text(kind, e, verdicts)
            url, created = open_issue_once(marker, f"[{kind}] 表述 #{sid}", "\n".join(lines), [kind])
            print("   ", "opened" if created else "already open", url)
        elif kind:
            marker, lines = issue_text(kind, e, verdicts)
            print("    (dry run) would open issue:\n    " + "\n    ".join(lines[:6]))
    if had_error:
        print("巡查未完成：至少一个模型接口出错，上面的“clean”不可信。", file=sys.stderr)
        return 1
    return 0

if __name__ == "__main__":
    sys.exit(main())
