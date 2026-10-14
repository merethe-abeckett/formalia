#!/usr/bin/env python3
"""Render the registry as a static, wiki-style site.

Reads:
  Conjectures/<Name>/conjecture.json        one per conjecture (disambiguation page)
  Conjectures/<Name>/S<id>.json + .lean     one per registered statement
  build/check/<Module>.json                 checker output (optional; "not run" if absent)
Writes:
  _site/index.html, _site/<slug>/index.html, _site/<slug>/<id>/index.html

The site states facts only. It carries no field for "is this equivalent to the
informal conjecture"; that discussion happens offline among mathematicians.
"""
import html, json, os, re, sys, subprocess, datetime
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
CONJ = ROOT / "Conjectures"
ARCH = ROOT / "Archive"
CHECK = ROOT / "build" / "check"
OUT = ROOT / "_site"

def esc(s): return html.escape(str(s), quote=True)

def git(*args):
    try:
        return subprocess.check_output(["git", *args], cwd=ROOT, text=True).strip()
    except Exception:
        return ""

def read_json(p):
    with open(p, encoding="utf-8") as f: return json.load(f)

def pinned_versions():
    tc = (ROOT / "lean-toolchain").read_text().strip()
    deps = []
    mf = ROOT / "lake-manifest.json"
    if mf.exists():
        for p in read_json(mf).get("packages", []):
            deps.append((p.get("name"), p.get("rev", ""), p.get("inputRev", "")))
    return tc, deps

CSS = """
:root{--bg:#fff;--fg:#1b1b1b;--muted:#666;--line:#ddd;--ok:#1a7f37;--bad:#b42318;--warn:#9a6700;--box:#f7f7f5;--link:#0b57d0}
@media(prefers-color-scheme:dark){:root{--bg:#141414;--fg:#e6e6e6;--muted:#9a9a9a;--line:#333;--box:#1e1e1e;--link:#8ab4f8;--ok:#3fb950;--bad:#f85149;--warn:#d29922}}
*{box-sizing:border-box}body{margin:0;background:var(--bg);color:var(--fg);font:16px/1.55 Georgia,"Noto Serif",serif}
a{color:var(--link)}header{border-bottom:1px solid var(--line);padding:12px 16px;font-family:system-ui,sans-serif;font-size:14px}
header a{text-decoration:none;color:var(--fg)}header .crumb{color:var(--muted)}
main{max-width:960px;margin:0 auto;padding:16px}h1{font-weight:normal;border-bottom:1px solid var(--line);padding-bottom:6px;margin-top:8px}
h2{font-weight:normal;font-size:1.25em;border-bottom:1px solid var(--line);padding-bottom:3px;margin-top:28px}
table{border-collapse:collapse;width:100%;font-family:system-ui,sans-serif;font-size:14px}td,th{border:1px solid var(--line);padding:6px 8px;text-align:left;vertical-align:top}
th{background:var(--box);font-weight:600;width:200px}pre{background:var(--box);border:1px solid var(--line);padding:12px;overflow:auto;font-size:13.5px;line-height:1.45}
code{font-family:ui-monospace,Menlo,Consolas,monospace;font-size:.93em}.ok{color:var(--ok);font-weight:600}.bad{color:var(--bad);font-weight:600}.warn{color:var(--warn);font-weight:600}
.note{background:var(--box);border-left:3px solid var(--line);padding:8px 12px;font-family:system-ui,sans-serif;font-size:14px;color:var(--muted)}
.muted{color:var(--muted)}footer{max-width:960px;margin:40px auto;padding:16px;border-top:1px solid var(--line);font-family:system-ui,sans-serif;font-size:13px;color:var(--muted)}
ul.plain{list-style:none;padding:0}ul.plain li{padding:4px 0;border-bottom:1px dotted var(--line)}
"""

def page(title, crumbs, body, depth):
    rel = "../" * depth
    crumb_html = ' <span class="crumb">›</span> '.join(
        f'<a href="{esc(h)}">{esc(t)}</a>' if h else esc(t) for t, h in crumbs)
    return f"""<!doctype html><html lang="en"><head><meta charset="utf-8">
<meta name="viewport" content="width=device-width,initial-scale=1"><title>{esc(title)}</title>
<link rel="stylesheet" href="{rel}style.css"></head><body>
<header><a href="{rel}index.html"><strong>Lean Statement Registry</strong></a> <span class="crumb">›</span> {crumb_html}</header>
<main>{body}</main>
<footer>The registry lists formal statements and the facts about them. It records no judgement on whether a statement is equivalent to the informal conjecture.
Code: Apache-2.0 · Entry content: CC-BY-4.0 · Built {esc(datetime.date.today().isoformat())} from commit <code>{esc(git('rev-parse','--short','HEAD') or '?')}</code>.</footer>
</body></html>"""

def status_cell(rep):
    if rep is None:
        return '<span class="warn">not run</span>'
    if rep.get("ok"):
        return '<span class="ok">passes</span>'
    return '<span class="bad">fails</span>'

def find_decl(check, decl):
    if not check: return None
    for d in check.get("declarations", []):
        if d["name"] == decl: return d
    return None

def render_statement(conj, meta, lean_src, check, tc, deps):
    sid = meta["id"]; decl = find_decl(check, meta["declaration"])
    first_commit = git("log", "--diff-filter=A", "--format=%H %cs", "--", f"Conjectures/{conj['_dir']}/{meta['_stem']}.lean")
    src = meta.get("source", {})
    src_html = esc(src.get("kind", ""))
    if src.get("url"): src_html += f' · <a href="{esc(src["url"])}">{esc(src["url"])}</a>'
    if src.get("note"): src_html += f'<br><span class="muted">{esc(src["note"])}</span>'
    rows = [
        ("Statement id", f"#{esc(sid)}"),
        ("Conjecture", f'<a href="../index.html">{esc(conj["name"])}</a>'),
        ("Lean declaration", f"<code>{esc(meta['declaration'])}</code> in <code>{esc(meta['module'])}</code>"),
        ("Submitted by", esc(meta.get("submitted_by",""))),
        ("Submitted at", esc(meta.get("submitted_at",""))),
        ("First commit", f"<code>{esc(first_commit)}</code>" if first_commit else '<span class="muted">not yet committed</span>'),
        ("Source", src_html),
        ("Lean toolchain", f"<code>{esc(tc)}</code>"),
        ("Dependencies (pinned)", "<br>".join(f"<code>{esc(n)}</code> @ <code>{esc(r)}</code>" + (f" ({esc(i)})" if i else "") for n,r,i in deps) or "—"),
        ("CI check", status_cell(decl)),
    ]
    table = "<table>" + "".join(f"<tr><th>{k}</th><td>{v}</td></tr>" for k,v in rows) + "</table>"

    body = f"<h1>Statement #{esc(sid)} — {esc(conj['name'])}</h1>"
    if meta.get("archived"):
        a = meta["archived"]
        body += f'<p class="note"><span class="bad">Archived {esc(a.get("at",""))}.</span> {esc(a.get("reason",""))} Discussion: <a href="{esc(a.get("issue",""))}">{esc(a.get("issue",""))}</a>. Kept for reference; not built or checked any more.</p>'
    body += table
    body += "<h2>Lean code</h2><pre><code>" + esc(lean_src) + "</code></pre>"

    body += "<h2>Checker report</h2>"
    if decl is None:
        body += '<p class="note">The checker has not been run on this build, or the declaration was not found.</p>'
    else:
        def yn(b, good_when_false=True):
            return ('<span class="ok">no</span>' if good_when_false else '<span class="bad">no</span>') if not b else \
                   ('<span class="bad">yes</span>' if good_when_false else '<span class="ok">yes</span>')
        crows = [
            ("Type is Prop", yn(decl["is_prop"], good_when_false=False)),
            ("Compiles", '<span class="ok">yes</span>'),
            ("Uses sorry", yn(decl["uses_sorry"])),
            ("Uses native_decide", yn(decl["uses_native_decide"])),
            ("Axioms", ", ".join(f"<code>{esc(a)}</code>" for a in decl["axioms"]) or "<span class='muted'>none</span>"),
            ("Non-standard axioms", ", ".join(f"<code>{esc(a)}</code>" for a in decl["non_standard_axioms"]) or '<span class="ok">none</span>'),
            ("Custom definitions (defined in this registry)", ", ".join(f"<code>{esc(a)}</code>" for a in decl["registry_dependencies"]) or '<span class="muted">none — every definition comes from Mathlib / Lean core</span>'),
        ]
        body += "<table>" + "".join(f"<tr><th>{k}</th><td>{v}</td></tr>" for k,v in crows) + "</table>"
        body += "<h2>Definition chain (direct dependencies)</h2>"
        body += '<p class="note">Constants mentioned directly by the statement, with the module that defines each. Follow a module into the pinned Mathlib revision to read its definition.</p>'
        body += "<table><tr><th>Constant</th><th>Defined in module</th></tr>"
        for d in decl["direct_dependencies"]:
            body += f"<tr><td><code>{esc(d['name'])}</code></td><td><code>{esc(d['module'] or '(core)')}</code></td></tr>"
        body += "</table>"

    ir = meta.get("informal_restatement") or {}
    body += "<h2>Informal restatement</h2>"
    if ir.get("text"):
        body += f'<p class="note">Written by: {esc(ir.get("author","submitter"))}. This is the author\'s own reading of the Lean code, not a judgement by the registry.</p><p>{esc(ir["text"])}</p>'
    else:
        body += '<p class="muted">none provided</p>'

    body += "<h2>Claimed proofs</h2>"
    cps = meta.get("claimed_proofs") or []
    if cps:
        body += "<table><tr><th>Claimant</th><th>Date</th><th>Link</th><th>Note</th></tr>"
        for c in cps:
            body += f"<tr><td>{esc(c.get('claimant',''))}</td><td>{esc(c.get('date',''))}</td><td><a href=\"{esc(c.get('url',''))}\">{esc(c.get('url',''))}</a></td><td>{esc(c.get('note',''))}</td></tr>"
        body += "</table>"
    else:
        body += '<p class="muted">none recorded</p>'

    body += "<h2>External links</h2>"
    els = meta.get("external_links") or []
    body += "<ul class='plain'>" + "".join(f'<li><a href="{esc(l["url"])}">{esc(l.get("label", l["url"]))}</a></li>' for l in els) + "</ul>" if els else '<p class="muted">none recorded</p>'
    return page(f"#{sid} — {conj['name']}", [(conj["name"], "../index.html"), (f"#{sid}", None)], body, 2)

def render_conjecture(conj, entries, archived=()):
    body = f"<h1>{esc(conj['name'])}</h1>"
    if conj.get("name_zh"): body += f'<p class="muted">{esc(conj["name_zh"])}</p>'
    body += f"<p><em>Informal statement:</em> {esc(conj.get('informal',''))}</p>"
    body += '<p class="note">This is a disambiguation page. It lists every formal statement registered under this conjecture. The registry does not say which, if any, is equivalent to the informal statement.</p>'
    body += "<h2>Registered statements</h2><table><tr><th>Id</th><th>Declaration</th><th>Submitted</th><th>Source</th><th>CI check</th><th>Claimed proofs</th></tr>"
    for meta, decl in entries:
        body += f'<tr><td><a href="{esc(meta["id"])}/index.html">#{esc(meta["id"])}</a></td><td><code>{esc(meta["declaration"])}</code></td><td>{esc(meta.get("submitted_at",""))} · {esc(meta.get("submitted_by",""))}</td><td>{esc(meta.get("source",{}).get("kind",""))}</td><td>{status_cell(decl)}</td><td>{len(meta.get("claimed_proofs") or [])}</td></tr>'
    body += "</table>"
    if archived:
        body += "<h2>Archived statements</h2><p class='note'>Removed from the live catalogue after a deletion proposal (see docs/DELETION.md). Ids are never reused; the text each id referred to is kept here.</p>"
        body += "<table><tr><th>Id</th><th>Declaration</th><th>Archived</th><th>Reason</th><th>Discussion</th></tr>"
        for meta in archived:
            a = meta.get("archived", {})
            body += f'<tr><td><a href="{esc(meta["id"])}/index.html">#{esc(meta["id"])}</a></td><td><code>{esc(meta["declaration"])}</code></td><td>{esc(a.get("at",""))}</td><td>{esc(a.get("reason",""))}</td><td><a href="{esc(a.get("issue",""))}">issue</a></td></tr>'
        body += "</table>"
    refs = conj.get("references") or []
    if refs:
        body += "<h2>References</h2><ul class='plain'>" + "".join(f'<li><a href="{esc(r["url"])}">{esc(r.get("label", r["url"]))}</a></li>' for r in refs) + "</ul>"
    return page(conj["name"], [(conj["name"], None)], body, 1)

def render_index(conjs, tc, deps, check_ok):
    body = "<h1>Lean Statement Registry</h1>"
    body += "<p>A neutral catalogue of formal (Lean 4) statements of mathematical conjectures. Each conjecture has a disambiguation page listing its registered statements. Each statement page records the Lean code, the pinned definition chain, its provenance, the automated checks, and any claimed proofs. Nothing more.</p>"
    body += f'<p class="note">Toolchain <code>{esc(tc)}</code> · Mathlib <code>{esc(next((r for n,r,_ in deps if n=="mathlib"), "?"))}</code> · Last checker run: {"<span class=ok>all entries pass</span>" if check_ok else "<span class=warn>see entries</span>"}</p>'
    body += "<h2>Conjectures</h2><table><tr><th>Conjecture</th><th>Registered statements</th></tr>"
    for c, n in conjs:
        body += f'<tr><td><a href="{esc(c["slug"])}/index.html">{esc(c["name"])}</a>' + (f' <span class="muted">{esc(c["name_zh"])}</span>' if c.get("name_zh") else "") + f'</td><td>{n}</td></tr>'
    body += "</table>"
    body += '<h2>How to add a statement</h2><p>Open a pull request adding <code>Conjectures/&lt;Name&gt;/S&lt;YYYYMMDD&gt;_&lt;NN&gt;.lean</code> (a <code>def … : Prop</code>) and the matching <code>.json</code>. CI compiles it, rejects <code>sorry</code>, <code>native_decide</code> and non-standard axioms, re-checks with lean4checker, and renders this site. See the README.</p>'
    return page("Lean Statement Registry", [("Index", None)], body, 0)

def main():
    tc, deps = pinned_versions()
    OUT.mkdir(exist_ok=True)
    (OUT / "style.css").write_text(CSS, encoding="utf-8")
    index_rows = []; all_ok = True
    for cdir in sorted(p for p in CONJ.iterdir() if p.is_dir()):
        cj = cdir / "conjecture.json"
        if not cj.exists(): continue
        conj = read_json(cj); conj["_dir"] = cdir.name
        entries = []
        for mj in sorted(cdir.glob("S*.json")):
            meta = read_json(mj); meta["_stem"] = mj.stem
            lean_src = (cdir / (mj.stem + ".lean")).read_text(encoding="utf-8")
            cf = CHECK / (meta["module"] + ".json")
            check = read_json(cf) if cf.exists() else None
            decl = find_decl(check, meta["declaration"])
            if decl is None or not decl.get("ok"): all_ok = False
            d = OUT / conj["slug"] / meta["id"]; d.mkdir(parents=True, exist_ok=True)
            (d / "index.html").write_text(render_statement(conj, meta, lean_src, check, tc, deps), encoding="utf-8")
            entries.append((meta, decl))
        archived = []
        adir = ARCH / cdir.name
        if adir.is_dir():
            for mj in sorted(adir.glob("S*.json")):
                meta = read_json(mj); meta["_stem"] = mj.stem
                lean_src = (adir / (mj.stem + ".lean")).read_text(encoding="utf-8")
                d = OUT / conj["slug"] / meta["id"]; d.mkdir(parents=True, exist_ok=True)
                (d / "index.html").write_text(render_statement(conj, meta, lean_src, None, tc, deps), encoding="utf-8")
                archived.append(meta)
        (OUT / conj["slug"]).mkdir(parents=True, exist_ok=True)
        (OUT / conj["slug"] / "index.html").write_text(render_conjecture(conj, entries, archived), encoding="utf-8")
        index_rows.append((conj, len(entries)))
    (OUT / "index.html").write_text(render_index(index_rows, tc, deps, all_ok), encoding="utf-8")
    (OUT / ".nojekyll").write_text("")
    print(f"wrote {OUT} ({sum(n for _,n in index_rows)} statements, {len(index_rows)} conjectures)")

if __name__ == "__main__":
    main()
