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
sys.path.insert(0, str(Path(__file__).resolve().parent))
import licenses

ROOT = Path(__file__).resolve().parent.parent
CONJ = ROOT / "Conjectures"
ARCH = ROOT / "Archive"
GUIDES = ROOT / "Guides"

def md_to_html(md):
    """极简 Markdown：粗体、要点、段落。导读只用这几样。"""
    out, in_list = [], False
    for line in md.splitlines():
        if line.startswith("<!--"): continue
        t = esc(line.strip())
        t = re.sub(r"\*\*(.+?)\*\*", r"<strong>\1</strong>", t)
        t = re.sub(r"`([^`]+)`", r"<code>\1</code>", t)
        if t.startswith("- ") or t.startswith("* "):
            if not in_list: out.append("<ul>"); in_list = True
            out.append(f"<li>{t[2:]}</li>")
        else:
            if in_list: out.append("</ul>"); in_list = False
            if t: out.append(f"<p>{t}</p>")
    if in_list: out.append("</ul>")
    return "\n".join(out)
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
*{box-sizing:border-box}body{margin:0;background:var(--bg);color:var(--fg);font:16px/1.7 "Noto Serif SC","Source Han Serif SC","Songti SC",SimSun,Georgia,serif}
a{color:var(--link)}header{border-bottom:1px solid var(--line);padding:12px 16px;font-family:system-ui,sans-serif;font-size:14px}
header a{text-decoration:none;color:var(--fg)}header .crumb{color:var(--muted)}
main{max-width:960px;margin:0 auto;padding:16px}h1{font-weight:normal;border-bottom:1px solid var(--line);padding-bottom:6px;margin-top:8px}
h2{font-weight:normal;font-size:1.25em;border-bottom:1px solid var(--line);padding-bottom:3px;margin-top:28px}
table{border-collapse:collapse;width:100%;font-family:system-ui,sans-serif;font-size:14px}td,th{border:1px solid var(--line);padding:6px 8px;text-align:left;vertical-align:top}
th{background:var(--box);font-weight:600;width:200px}pre{background:var(--box);border:1px solid var(--line);padding:12px;overflow:auto;font-size:13.5px;line-height:1.45}
code{font-family:ui-monospace,Menlo,Consolas,monospace;font-size:.93em}.ok{color:var(--ok);font-weight:600}.bad{color:var(--bad);font-weight:600}.warn{color:var(--warn);font-weight:600}
.note{background:var(--box);border-left:3px solid var(--line);padding:8px 12px;font-family:system-ui,sans-serif;font-size:14px;color:var(--muted)}
.muted{color:var(--muted)}footer{max-width:960px;margin:40px auto;padding:16px;border-top:1px solid var(--line);font-family:system-ui,sans-serif;font-size:13px;color:var(--muted)}
.btn{display:inline-block;padding:6px 12px;border:1px solid var(--line);border-radius:6px;background:var(--box);text-decoration:none;font-family:system-ui,sans-serif;font-size:14px}
ul.plain{list-style:none;padding:0}ul.plain li{padding:4px 0;border-bottom:1px dotted var(--line)}
.actions{display:flex;flex-wrap:wrap;gap:8px;margin:12px 0}
form.edit{font-family:system-ui,sans-serif;font-size:15px;max-width:760px}
form.edit .f{display:block;margin:14px 0}form.edit .fl{display:block;font-weight:600;margin-bottom:4px}
form.edit .fh{display:block;color:var(--muted);font-size:13px;margin-top:3px}
form.edit input[type=text],form.edit textarea,form.edit select{width:100%;padding:7px 9px;border:1px solid var(--line);border-radius:6px;background:var(--bg);color:var(--fg);font:inherit}
form.edit textarea.mono{font-family:ui-monospace,Menlo,Consolas,monospace;font-size:14px}
form.edit fieldset{border:1px solid var(--line);border-radius:6px;padding:4px 12px}
form.edit button{padding:8px 22px;border:0;border-radius:6px;background:var(--link);color:#fff;font:inherit;cursor:pointer;margin-top:12px}
form.edit button:disabled{opacity:.5;cursor:default}
pre.msg{white-space:pre-wrap}
.cf-turnstile{margin-top:12px}
@media(max-width:600px){th{width:auto}td,th{display:block;width:100%}tr{display:block;border-bottom:1px solid var(--line)}}
"""

def page(title, crumbs, body, depth):
    rel = "../" * depth
    crumb_html = ' <span class="crumb">›</span> '.join(
        f'<a href="{esc(h)}">{esc(t)}</a>' if h else esc(t) for t, h in crumbs)
    return f"""<!doctype html><html lang="zh-CN"><head><meta charset="utf-8">
<meta name="viewport" content="width=device-width,initial-scale=1"><title>{esc(title)}</title>
<link rel="stylesheet" href="{rel}style.css"></head><body>
<header><a href="{rel}index.html"><strong>Lean 表述登记库</strong></a> <span class="crumb">›</span> {crumb_html}</header>
<main>{body}</main>
<footer>本登记库只列出形式化表述及其事实，不记录任何关于“该表述是否等价于原猜想”的判断。
代码：Apache-2.0 · 条目内容：各条目按其声明的许可，未声明默认 CC-BY-4.0 · 构建于 {esc(datetime.date.today().isoformat())}，提交 <code>{esc(git('rev-parse','--short','HEAD') or '?')}</code>。</footer>
</body></html>"""

def status_cell(rep):
    if rep is None:
        return '<span class="warn">未运行</span>'
    if rep.get("ok"):
        return '<span class="ok">通过</span>'
    return '<span class="bad">未通过</span>'

def find_decl(check, decl):
    if not check: return None
    for d in check.get("declarations", []):
        if d["name"] == decl: return d
    return None

KIND_ZH = {"original": "原创", "adapted": "改编", "verbatim": "照录"}

def history(paths, limit=30):
    """从 git 记录里读出编辑历史：日期、说明、编辑者。"""
    out = git("log", f"-{limit}", "--format=%cs%x1f%s%x1f%b%x1e", "--", *paths)
    rows = []
    for rec in out.split("\x1e"):
        rec = rec.strip()
        if not rec: continue
        date, subj, body = (rec.split("\x1f") + ["", ""])[:3]
        editor = next((l.split("：", 1)[1].strip() for l in body.splitlines() if l.startswith("编辑者：")), "")
        rows.append((date, subj, editor))
    return rows

def history_html(paths):
    rows = history(paths)
    if not rows: return '<p class="muted">暂无记录</p>'
    return ("<table><tr><th>日期</th><th>说明</th><th>编辑者</th></tr>" +
            "".join(f"<tr><td>{esc(d)}</td><td>{esc(sj)}</td><td>{esc(e) or '<span class=muted>维护者</span>'}</td></tr>" for d, sj, e in rows) +
            "</table>")

def license_html(meta):
    lic = licenses.of(meta)
    name, url = licenses.ALLOWED.get(lic, (lic, ""))
    tag = f'<a href="{esc(url)}">{esc(lic)}</a>' if url else esc(lic)
    return f'{tag} <span class="muted">{esc(name)}{"（默认）" if not meta.get("license") else ""}</span>'

def edit_link(rel, **q):
    from urllib.parse import urlencode
    return f"{rel}edit/index.html?{esc(urlencode(q))}"

def kind_zh(k): return KIND_ZH.get(k, k)

def render_statement(conj, meta, lean_src, check, tc, deps):
    sid = meta["id"]; decl = find_decl(check, meta["declaration"])
    cname = conj.get("name_zh") or conj["name"]
    first_commit = git("log", "--diff-filter=A", "--format=%H %cs", "--", f"Conjectures/{conj['_dir']}/{meta['_stem']}.lean")
    src = meta.get("source", {})
    src_html = esc(kind_zh(src.get("kind", "")))
    if src.get("url"): src_html += f' · <a href="{esc(src["url"])}">{esc(src["url"])}</a>'
    if src.get("note"): src_html += f'<br><span class="muted">{esc(src["note"])}</span>'
    rows = [
        ("表述编号", f"#{esc(sid)}"),
        ("所属猜想", f'<a href="../index.html">{esc(cname)}</a>'),
        ("Lean 声明", f"<code>{esc(meta['declaration'])}</code>，位于模块 <code>{esc(meta['module'])}</code>"),
        ("提交者", esc(meta.get("submitted_by",""))),
        ("提交日期", esc(meta.get("submitted_at",""))),
        ("首次提交", f"<code>{esc(first_commit)}</code>" if first_commit else '<span class="muted">尚未提交</span>'),
        ("来源", src_html),
        ("许可", license_html(meta)),
        ("Lean 工具链", f"<code>{esc(tc)}</code>"),
        ("依赖（钉死版本）", "<br>".join(f"<code>{esc(n)}</code> @ <code>{esc(r)}</code>" + (f" ({esc(i)})" if i else "") for n,r,i in deps) or "—"),
        ("CI 检查", status_cell(decl)),
    ]
    table = "<table>" + "".join(f"<tr><th>{k}</th><td>{v}</td></tr>" for k,v in rows) + "</table>"

    body = f"<h1>表述 #{esc(sid)} · {esc(cname)}</h1>"
    if meta.get("archived"):
        a = meta["archived"]
        body += f'<p class="note"><span class="bad">已于 {esc(a.get("at",""))} 归档。</span>{esc(a.get("reason",""))} 讨论：<a href="{esc(a.get("issue",""))}">{esc(a.get("issue",""))}</a>。仅供查阅，不再编译和检查。</p>'
    if not meta.get("archived"):
        body += (f'<div class="actions"><a class="btn" href="{edit_link("../../", type="meta", target=sid)}">编辑本条信息</a>'
                 f'<a class="btn" href="{edit_link("../../", type="claim", target=sid)}">＋ 声明证明了这条表述</a>'
                 f'<a class="btn" href="{edit_link("../../", type="statement", conjecture=conj["slug"])}">＋ 为该猜想新增一条表述</a></div>')
    body += table
    body += "<h2>Lean 代码</h2><pre><code>" + esc(lean_src) + "</code></pre>"

    body += "<h2>检查器报告</h2>"
    if decl is None:
        body += '<p class="note">本次构建未运行检查器，或未找到该声明。</p>'
    else:
        def yn(b, good_when_false=True):
            return ('<span class="ok">否</span>' if good_when_false else '<span class="bad">否</span>') if not b else \
                   ('<span class="bad">是</span>' if good_when_false else '<span class="ok">是</span>')
        crows = [
            ("类型为 Prop", yn(decl["is_prop"], good_when_false=False)),
            ("能否编译", '<span class="ok">是</span>'),
            ("含 sorry", yn(decl["uses_sorry"])),
            ("含 native_decide", yn(decl["uses_native_decide"])),
            ("使用的公理", ", ".join(f"<code>{esc(a)}</code>" for a in decl["axioms"]) or "<span class='muted'>无</span>"),
            ("非标准公理", ", ".join(f"<code>{esc(a)}</code>" for a in decl["non_standard_axioms"]) or '<span class="ok">无</span>'),
            ("自定义定义（在本登记库内定义）", ", ".join(f"<code>{esc(a)}</code>" for a in decl["registry_dependencies"]) or '<span class="muted">无，所有定义均来自 Mathlib 或 Lean 核心</span>'),
        ]
        body += "<table>" + "".join(f"<tr><th>{k}</th><td>{v}</td></tr>" for k,v in crows) + "</table>"
        body += "<h2>定义链（直接依赖）</h2>"
        body += '<p class="note">表述中直接出现的常量，以及定义它们的模块。到钉死版本的 Mathlib 中打开对应模块即可阅读其定义。</p>'
        body += "<table><tr><th>常量</th><th>定义所在模块</th></tr>"
        for d in decl["direct_dependencies"]:
            body += f"<tr><td><code>{esc(d['name'])}</code></td><td><code>{esc(d['module'] or '（核心）')}</code></td></tr>"
        body += "</table>"

    guide = GUIDES / conj["_dir"] / (meta["_stem"] + ".md")
    body += "<h2>AI 导读</h2>"
    if guide.exists():
        gtext = guide.read_text(encoding="utf-8")
        m = re.search(r"<!--\s*(.*?)\s*-->", gtext, re.S)
        body += f'<p class="note">{esc(m.group(1)) if m else "AI 生成"}只解释定义和逐句翻译，不代表登记库判断，不涉及是否等价于原猜想。发现错误请提 PR 修改 <code>{esc(str(guide.relative_to(ROOT)))}</code>。</p>'
        body += md_to_html(gtext)
    else:
        body += '<p class="muted">尚未生成</p>'

    ir = meta.get("informal_restatement") or {}
    body += "<h2>非正式复述</h2>"
    if ir.get("text"):
        body += f'<p class="note">撰写者：{esc(ir.get("author","submitter"))}。这是撰写者对 Lean 代码的个人解读，不代表登记库的判断。</p><p>{esc(ir["text"])}</p>'
    else:
        body += '<p class="muted">未提供</p>'

    body += "<h2>声称的证明</h2>"
    body += '<p class="note">登记库只记录“谁声称证明了这个编号”，不托管证明，也不判断证明是否正确。</p>'
    if not meta.get("archived"):
        body += f'<p><a class="btn" href="{edit_link("../../", type="claim", target=sid)}">＋ 声明证明了这条表述</a></p>'
    cps = meta.get("claimed_proofs") or []
    if cps:
        body += "<table><tr><th>声称方</th><th>日期</th><th>链接</th><th>备注</th><th>登记者</th></tr>"
        for c in cps:
            note = esc(c.get('note',''))
            if c.get('issue'): note += f' <a href="{esc(c["issue"])}">议题</a>'
            body += f"<tr><td>{esc(c.get('claimant',''))}</td><td>{esc(c.get('date',''))}</td><td><a href=\"{esc(c.get('url',''))}\" rel=\"nofollow ugc\">{esc(c.get('url',''))}</a></td><td>{note}</td><td>{esc(c.get('recorded_by',''))}</td></tr>"
        body += "</table>"
    else:
        body += '<p class="muted">暂无记录</p>'

    body += "<h2>外部链接</h2>"
    els = meta.get("external_links") or []
    body += "<ul class='plain'>" + "".join(f'<li><a href="{esc(l["url"])}" rel="nofollow ugc">{esc(l.get("label", l["url"]))}</a></li>' for l in els) + "</ul>" if els else '<p class="muted">暂无记录</p>'
    base = "Archive" if meta.get("archived") else "Conjectures"
    body += "<h2>编辑历史</h2>" + history_html([f"{base}/{conj['_dir']}/{meta['_stem']}.lean", f"{base}/{conj['_dir']}/{meta['_stem']}.json"])
    return page(f"#{sid} · {cname}", [(cname, "../index.html"), (f"#{sid}", None)], body, 2)

def render_conjecture(conj, entries, archived=()):
    body = f"<h1>{esc(conj.get('name_zh') or conj['name'])}</h1>"
    if conj.get("name_zh"): body += f'<p class="muted">{esc(conj["name"])}</p>'
    body += f"<p><em>自然语言表述：</em>{esc(conj.get('informal',''))}</p>"
    body += '<p class="note">这是一个消歧义页，列出登记在该猜想之下的全部形式化表述。登记库不判断其中哪一条（如果有）等价于自然语言表述。</p>'
    body += (f'<div class="actions"><a class="btn" href="{edit_link("../", type="statement", conjecture=conj["slug"])}">＋ 新增一条表述</a>'
             f'<a class="btn" href="{edit_link("../", type="conjecture", target=conj["slug"])}">编辑猜想信息</a></div>')
    body += "<h2>已登记的表述</h2><table><tr><th>编号</th><th>Lean 声明</th><th>提交</th><th>来源</th><th>CI 检查</th><th>声称的证明</th></tr>"
    for meta, decl in entries:
        body += f'<tr><td><a href="{esc(meta["id"])}/index.html">#{esc(meta["id"])}</a></td><td><code>{esc(meta["declaration"])}</code></td><td>{esc(meta.get("submitted_at",""))} · {esc(meta.get("submitted_by",""))}</td><td>{esc(kind_zh(meta.get("source",{}).get("kind","")))}</td><td>{status_cell(decl)}</td><td>{len(meta.get("claimed_proofs") or [])}</td></tr>'
    body += "</table>"
    if archived:
        body += "<h2>已归档的表述</h2><p class='note'>经提删公示后移出现行目录（见 docs/DELETION.md）。编号永不复用，各编号所指的原文保留于此。</p>"
        body += "<table><tr><th>编号</th><th>Lean 声明</th><th>归档日期</th><th>原因</th><th>讨论</th></tr>"
        for meta in archived:
            a = meta.get("archived", {})
            body += f'<tr><td><a href="{esc(meta["id"])}/index.html">#{esc(meta["id"])}</a></td><td><code>{esc(meta["declaration"])}</code></td><td>{esc(a.get("at",""))}</td><td>{esc(a.get("reason",""))}</td><td><a href="{esc(a.get("issue",""))}">议题</a></td></tr>'
        body += "</table>"
    refs = conj.get("references") or []
    if refs:
        body += "<h2>参考资料</h2><ul class='plain'>" + "".join(f'<li><a href="{esc(r["url"])}">{esc(r.get("label", r["url"]))}</a></li>' for r in refs) + "</ul>"
    body += "<h2>编辑历史</h2>" + history_html([f"Conjectures/{conj['_dir']}/conjecture.json"])
    cname = conj.get("name_zh") or conj["name"]
    return page(cname, [(cname, None)], body, 1)

def render_index(conjs, tc, deps, check_ok):
    body = "<h1>Lean 表述登记库</h1>"
    body += "<p>一个中立的目录，收录数学猜想的 Lean 4 形式化表述。每个猜想有一个消歧义页，列出已登记的各条表述；每条表述的页面记录 Lean 代码、钉死版本的定义链、来源、自动检查结果，以及声称证明了它的证明。仅此而已。</p>"
    body += f'<p class="note">工具链 <code>{esc(tc)}</code> · Mathlib <code>{esc(next((r for n,r,_ in deps if n=="mathlib"), "?"))}</code> · 最近一次检查： {"<span class=ok>全部条目通过</span>" if check_ok else "<span class=warn>见各条目</span>"}</p>'
    body += "<h2>猜想列表</h2><table><tr><th>猜想</th><th>已登记表述数</th></tr>"
    for c, n in conjs:
        body += f'<tr><td><a href="{esc(c["slug"])}/index.html">{esc(c.get("name_zh") or c["name"])}</a>' + (f' <span class="muted">{esc(c["name"])}</span>' if c.get("name_zh") else "") + f'</td><td>{n}</td></tr>'
    body += "</table>"
    body += f'<div class="actions"><a class="btn" href="{edit_link("", type="statement")}">＋ 登记一条表述（含新猜想）</a></div>'
    body += ('<h2>谁都可以编辑</h2><p>和维基百科一样，不需要注册，也不需要 GitHub 账号。每个页面上都有编辑按钮。'
             '提交后机器会自动检查：Lean 代码要能编译，不能有 <code>sorry</code>、<code>native_decide</code> 或非标准公理，并经 lean4checker 独立复核。'
             '检查通过就直接写入，网站几分钟后更新；每一次编辑都留有记录，可以回退。'
             '是否等价于原猜想不在检查范围内，留给数学家讨论。</p>'
             '<p><a href="about/privacy.html">隐私与编辑规则</a> · 熟悉 GitHub 的人也可以直接提交 Pull Request，见 README。</p>')
    return page("Lean 表述登记库", [("首页", None)], body, 0)

SITE_SRC = ROOT / "site"

def write_edit_pages(index_rows):
    """编辑表单需要的数据，以及编辑、状态、隐私三个页面。"""
    data = {"statements": {}, "conjectures": {}}
    for conj, _ in index_rows:
        cdir = CONJ / conj["_dir"]
        data["conjectures"][conj["slug"]] = {k: conj.get(k) or ([] if k == "references" else "") for k in ("name", "name_zh", "informal", "references")}
        for mj in sorted(cdir.glob("S*.json")):
            m = read_json(mj)
            data["statements"][m["id"]] = {
                "conjecture": conj["slug"], "conjecture_name": conj.get("name_zh") or conj["name"],
                "source_note": (m.get("source") or {}).get("note") or "", "source_url": (m.get("source") or {}).get("url") or "",
                "restatement": (m.get("informal_restatement") or {}).get("text") or "", "external_links": m.get("external_links") or []}
    (OUT / "data.json").write_text(json.dumps(data, ensure_ascii=False), encoding="utf-8")
    (OUT / "edit").mkdir(exist_ok=True); (OUT / "about").mkdir(exist_ok=True)
    (OUT / "edit" / "edit.js").write_text((SITE_SRC / "edit.js").read_text(encoding="utf-8"), encoding="utf-8")
    js = '<script src="edit.js" defer></script>'
    (OUT / "edit" / "index.html").write_text(page("编辑", [("编辑", None)],
        '<h1 id="edit-title">编辑</h1><div id="edit-root"><p class="muted">正在加载……</p></div><noscript><p class="note bad">编辑需要启用 JavaScript。</p></noscript>' + js, 1), encoding="utf-8")
    (OUT / "edit" / "status.html").write_text(page("编辑状态", [("编辑状态", None)],
        '<h1>编辑状态</h1><div id="status-root"><p class="muted">正在查询……</p></div>' + js, 1), encoding="utf-8")
    (OUT / "about" / "privacy.html").write_text(page("隐私与编辑规则", [("隐私与编辑规则", None)],
        md_to_html((SITE_SRC / "privacy.md").read_text(encoding="utf-8")), 1), encoding="utf-8")

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
    write_edit_pages(index_rows)
    (OUT / ".nojekyll").write_text("")
    print(f"wrote {OUT} ({sum(n for _,n in index_rows)} statements, {len(index_rows)} conjectures)")

if __name__ == "__main__":
    main()
