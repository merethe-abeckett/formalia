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
CHECK = ROOT / "build" / "check"
OUT = ROOT / "_site"

def _inline(t):
    """行内：先转义，再处理粗体、代码、链接、$公式$（只去掉美元符号，按代码显示）。"""
    t = esc(t)
    t = re.sub(r"`([^`]+)`", r"<code>\1</code>", t)
    t = re.sub(r"\$([^$\n]+)\$", r"<code>\1</code>", t)
    t = re.sub(r"\*\*(.+?)\*\*", r"<strong>\1</strong>", t)
    def link(m):
        label, url = m.group(1), m.group(2)
        if not re.match(r"^(https?://|[a-zA-Z0-9_./#-]+$)", url) or url.lower().startswith("javascript"):
            return label
        return f'<a href="{url}">{label}</a>'
    return re.sub(r"\[([^\]]+)\]\(([^)\s]+)\)", link, t)

def md_to_html(md):
    """够用的 Markdown：标题、段落、无序/有序列表、引用、粗体、代码、链接。"""
    out, mode = [], None          # mode: None | "ul" | "ol" | "quote"
    def close():
        nonlocal mode
        if mode: out.append({"ul": "</ul>", "ol": "</ol>", "quote": "</blockquote>"}[mode]); mode = None
    for raw in md.splitlines():
        line = raw.strip()
        if line.startswith("<!--"): continue
        if not line: close(); continue
        h = re.match(r"^(#{2,4})\s+(.*)$", line)
        if h:
            close(); n = len(h.group(1)); out.append(f"<h{n}>{_inline(h.group(2))}</h{n}>"); continue
        if line.startswith(("- ", "* ")):
            if mode != "ul": close(); out.append("<ul>"); mode = "ul"
            out.append(f"<li>{_inline(line[2:])}</li>"); continue
        o = re.match(r"^\d+\.\s+(.*)$", line)
        if o:
            if mode != "ol": close(); out.append("<ol>"); mode = "ol"
            out.append(f"<li>{_inline(o.group(1))}</li>"); continue
        if line.startswith(">"):
            if mode != "quote": close(); out.append("<blockquote>"); mode = "quote"
            out.append(f"<p>{_inline(line.lstrip('>').strip())}</p>"); continue
        close(); out.append(f"<p>{_inline(line)}</p>")
    close()
    return "\n".join(out)

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
:root{--bg:#fbfaf7;--fg:#1d1d1b;--muted:#6b6b66;--line:#e4e2dc;--box:#f3f1ec;--card:#fff;--link:#1f5f8b;--accent:#1f5f8b;
--ok:#1a7f37;--bad:#b42318;--warn:#9a6700;--sans:system-ui,-apple-system,"PingFang SC","Noto Sans SC","Microsoft YaHei",sans-serif;
--serif:"Noto Serif SC","Source Han Serif SC","Songti SC",SimSun,Georgia,serif;--mono:ui-monospace,"JetBrains Mono",Menlo,Consolas,monospace}
@media(prefers-color-scheme:dark){:root{--bg:#151514;--fg:#e8e6e1;--muted:#9c9a94;--line:#2e2d2a;--box:#1d1c1a;--card:#1b1a18;--link:#8cc3ea;--accent:#8cc3ea;--ok:#4cc26a;--bad:#ff7b6b;--warn:#e3b341}}
*{box-sizing:border-box}html{-webkit-text-size-adjust:100%}
body{margin:0;background:var(--bg);color:var(--fg);font:16px/1.75 var(--serif)}
a{color:var(--link);text-underline-offset:2px}
.top{border-bottom:1px solid var(--line);font-family:var(--sans);font-size:14px}
.top .in{max-width:980px;margin:0 auto;padding:12px 16px;display:flex;align-items:center;gap:20px;flex-wrap:wrap}
.top .brand{font-weight:700;font-size:17px;letter-spacing:.02em;color:var(--fg);text-decoration:none}
.top nav{display:flex;gap:16px;flex-wrap:wrap;margin-left:auto}.top nav a{color:var(--muted);text-decoration:none}.top nav a:hover{color:var(--fg)}
.crumbs{max-width:980px;margin:0 auto;padding:10px 16px 0;font-family:var(--sans);font-size:13px;color:var(--muted)}
.crumbs a{color:var(--muted)}
main{max-width:980px;margin:0 auto;padding:8px 16px 16px}
h1{font-weight:600;font-size:1.9em;line-height:1.3;margin:18px 0 10px}
h2{font-weight:600;font-size:1.2em;border-bottom:1px solid var(--line);padding-bottom:4px;margin-top:34px}
h3{font-weight:600;font-size:1.05em;margin-top:22px}
table{border-collapse:collapse;width:100%;font-family:var(--sans);font-size:14px;background:var(--card)}
td,th{border:1px solid var(--line);padding:7px 10px;text-align:left;vertical-align:top}
th{background:var(--box);font-weight:600;width:200px}
pre{background:var(--box);border:1px solid var(--line);border-radius:6px;padding:12px 14px;overflow:auto;font-size:13.5px;line-height:1.5}
code{font-family:var(--mono);font-size:.92em}
blockquote{margin:16px 0;padding:4px 18px;border-left:3px solid var(--line);color:var(--fg);background:var(--box);border-radius:0 6px 6px 0}
.ok{color:var(--ok);font-weight:600}.bad{color:var(--bad);font-weight:600}.warn{color:var(--warn);font-weight:600}
.note{background:var(--box);border-left:3px solid var(--line);padding:8px 12px;font-family:var(--sans);font-size:14px;color:var(--muted);border-radius:0 6px 6px 0}
.muted{color:var(--muted)}
footer{max-width:980px;margin:48px auto 0;padding:18px 16px 28px;border-top:1px solid var(--line);font-family:var(--sans);font-size:12.5px;color:var(--muted);line-height:1.7}
.btn{display:inline-block;padding:7px 14px;border:1px solid var(--line);border-radius:7px;background:var(--card);color:var(--fg);text-decoration:none;font-family:var(--sans);font-size:14px}
.btn:hover{border-color:var(--muted)}.btn.primary{background:var(--accent);border-color:var(--accent);color:#fff}
@media(prefers-color-scheme:dark){.btn.primary{color:#0d1b26}}
ul.plain{list-style:none;padding:0}ul.plain li{padding:5px 0;border-bottom:1px dotted var(--line)}
.actions{display:flex;flex-wrap:wrap;gap:8px;margin:14px 0}
/* 首页 */
.hero{padding:44px 0 18px}.hero h1{font-size:2.6em;margin:0;letter-spacing:.01em;font-family:var(--sans);font-weight:700}
.hero .sub{font-size:1.2em;margin:6px 0 14px;color:var(--fg)}.hero p{max-width:640px;color:var(--muted);font-family:var(--sans);font-size:15px;margin:0 0 6px}
.steps{display:grid;grid-template-columns:repeat(3,1fr);gap:14px;margin:26px 0 8px}
.step{background:var(--card);border:1px solid var(--line);border-radius:10px;padding:14px 16px;font-family:var(--sans);font-size:14px}
.step b{display:block;font-size:15px;margin-bottom:4px}.step .k{font-family:var(--mono);color:var(--accent);font-size:12.5px}
.step p{margin:4px 0 0;color:var(--muted);line-height:1.6}
.stats{display:flex;gap:28px;flex-wrap:wrap;font-family:var(--sans);font-size:13px;color:var(--muted);margin:18px 0 0}
.stats b{display:block;font-size:22px;color:var(--fg);font-weight:600}
.cards{list-style:none;padding:0;margin:10px 0;display:grid;grid-template-columns:repeat(auto-fill,minmax(260px,1fr));gap:12px}
.cards a{display:block;height:100%;background:var(--card);border:1px solid var(--line);border-radius:10px;padding:12px 14px;text-decoration:none;color:var(--fg);font-family:var(--sans)}
.cards a:hover{border-color:var(--muted)}.cards .t{font-weight:600}.cards .e{font-size:13px;color:var(--muted)}
.cards .n{font-size:12.5px;color:var(--muted);margin-top:6px}
/* 表单 */
form.edit{font-family:var(--sans);font-size:15px;max-width:760px}
form.edit .f{display:block;margin:14px 0}form.edit .fl{display:block;font-weight:600;margin-bottom:4px}
form.edit .fh{display:block;color:var(--muted);font-size:13px;margin-top:3px}
form.edit input[type=text],form.edit textarea,form.edit select{width:100%;padding:7px 9px;border:1px solid var(--line);border-radius:6px;background:var(--card);color:var(--fg);font:inherit}
form.edit textarea.mono{font-family:var(--mono);font-size:14px}
form.edit fieldset{border:1px solid var(--line);border-radius:6px;padding:4px 12px}
form.edit button,.ask button{padding:8px 22px;border:0;border-radius:6px;background:var(--accent);color:#fff;font:inherit;cursor:pointer;margin-top:12px}
form.edit button:disabled,.ask button:disabled{opacity:.5;cursor:default}
pre.msg{white-space:pre-wrap}
.cf-turnstile{margin-top:12px}
/* 首页引文 */
figure.quote{margin:22px 0 4px;max-width:760px}figure.quote blockquote{margin:0;font-size:15.5px;line-height:1.85}
figure.quote figcaption{font-family:var(--sans);font-size:12.5px;color:var(--muted);margin:6px 0 0 21px}
/* 搜索 */
.search{display:flex;gap:8px;margin:16px 0 4px;max-width:640px}
.search input{flex:1;padding:10px 14px;border:1px solid var(--line);border-radius:8px;background:var(--card);color:var(--fg);font:16px var(--sans)}
.search input:focus{outline:2px solid var(--accent);outline-offset:-1px}
.search button{padding:0 18px;border:0;border-radius:8px;background:var(--accent);color:#fff;font:15px var(--sans);cursor:pointer}
#search-info{font-family:var(--sans);font-size:13px;color:var(--muted);margin:6px 0 10px}
#results{list-style:none;padding:0;margin:0;font-family:var(--sans)}
#results li{border-bottom:1px solid var(--line)}#results a{display:block;padding:10px 4px;text-decoration:none;color:var(--fg)}
#results a:hover{background:var(--box)}#results .t{font-weight:600}#results .e{color:var(--muted);font-size:14px}
#results .tag{display:inline-block;font-size:11.5px;border:1px solid var(--line);border-radius:4px;padding:0 5px;margin-right:8px;color:var(--muted);vertical-align:1px}
#results .snip{font-size:13.5px;color:var(--muted);margin-top:3px;line-height:1.6}
mark{background:#fde68a;color:inherit;border-radius:2px;padding:0 1px}
@media(prefers-color-scheme:dark){mark{background:#6b5310}}
/* 灌水区 */
.chat{font-family:var(--mono);font-size:14px;border:1px solid var(--line);border-radius:10px;background:var(--card);display:flex;flex-direction:column;height:min(70vh,640px)}
.chat .bar{display:flex;justify-content:space-between;padding:6px 12px;border-bottom:1px solid var(--line);color:var(--muted);font-size:12.5px;font-family:var(--sans)}
#chat-log{flex:1;overflow-y:auto;padding:8px 12px;line-height:1.55;word-break:break-word;--nick-l:38%}
@media(prefers-color-scheme:dark){#chat-log{--nick-l:68%}}
#chat-log .ts{color:var(--muted)}#chat-log .lt,#chat-log .star{color:var(--muted)}#chat-log .nick{font-weight:600}
#chat-log .sys{color:var(--muted)}#chat-log .err{color:var(--bad)}#chat-log .mine{background:var(--box)}
#chat-log .adm{font:inherit;font-size:11px;border:1px solid var(--line);background:none;color:var(--muted);border-radius:4px;padding:0 4px;margin-left:4px;cursor:pointer}
#chat-form{display:flex;border-top:1px solid var(--line)}
#chat-input{flex:1;border:0;padding:10px 12px;background:transparent;color:var(--fg);font:inherit;outline:none}
#chat-form button{border:0;background:var(--accent);color:#fff;padding:0 18px;font-family:var(--sans);cursor:pointer;border-radius:0 0 10px 0}
/* 交互式导读 */
.ask{font-family:var(--sans);font-size:15px;border:1px solid var(--line);border-radius:10px;padding:12px 14px;background:var(--card);margin-top:14px}
.ask .log{display:flex;flex-direction:column;gap:10px;margin-bottom:8px}
.ask .q{align-self:flex-end;background:var(--box);border-radius:10px;padding:6px 10px;max-width:85%;white-space:pre-wrap}
.ask .a{white-space:pre-wrap;line-height:1.7}.ask .a code{background:var(--box);padding:0 3px;border-radius:3px}
.ask textarea{width:100%;padding:7px 9px;border:1px solid var(--line);border-radius:6px;background:var(--bg);color:var(--fg);font:inherit;resize:vertical}
.ask .row{display:flex;gap:10px;align-items:center;flex-wrap:wrap}.ask .row button{margin-top:6px}
@media(max-width:700px){.steps{grid-template-columns:1fr}.hero h1{font-size:2.1em}}
@media(max-width:600px){th{width:auto}td,th{display:block;width:100%}tr{display:block;border-bottom:1px solid var(--line)}}
"""

SITE_NAME = "Formalia"
REPO_URL = "https://github.com/merethe-abeckett/formalia"
CONTACT = "merethe.abeckett@outlook.com"

def page(title, crumbs, body, depth, home=False):
    rel = "../" * depth
    crumb_html = "" if home else ('<div class="crumbs"><a href="' + rel + 'index.html">首页</a> › ' + " › ".join(
        f'<a href="{esc(h)}">{esc(t)}</a>' if h else esc(t) for t, h in crumbs) + "</div>")
    full = SITE_NAME if home else f"{title} · {SITE_NAME}"
    return f"""<!doctype html><html lang="zh-CN"><head><meta charset="utf-8">
<meta name="viewport" content="width=device-width,initial-scale=1"><title>{esc(full)}</title>
<meta name="description" content="Formalia：数学猜想的 Lean 4 表述目录。只列出，不判断。">
<link rel="stylesheet" href="{rel}style.css"></head><body>
<header class="top"><div class="in"><a class="brand" href="{rel}index.html">{SITE_NAME}</a>
<nav><a href="{rel}search/index.html">搜索</a><a href="{rel}index.html#conjectures">猜想</a><a href="{rel}about/guide.html">使用说明</a><a href="{rel}about/index.html">关于</a><a href="{rel}edit/index.html?type=statement">登记表述</a><a href="{rel}chat/index.html">灌水区</a></nav></div></header>
{crumb_html}<main>{body}</main>
<footer>Formalia 只列出形式化表述及其事实，不判断某条表述是否等价于原猜想。<br>
代码 Apache-2.0 · 条目内容按各自声明的许可，默认 CC-BY-4.0 · <a href="{rel}about/privacy.html">隐私与编辑规则</a> ·
<a href="{REPO_URL}">GitHub 仓库 merethe-abeckett/formalia</a> · 联系 <a href="mailto:{CONTACT}">{CONTACT}</a> · 构建于 {esc(datetime.date.today().isoformat())}，提交 <code>{esc(git('rev-parse','--short','HEAD') or '?')}</code></footer>
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

def live_url(src, decl):
    """在 Lean 4 Web（live.lean-lang.org）中打开：换成 import Mathlib，去掉模块系统的包装，末尾打印公理。"""
    from urllib.parse import quote
    code = re.sub(r"(?m)^module[ \t]*\n", "", src)
    code = re.sub(r"(?m)^public import [^\n]*\n", "", code)
    code = code.replace("@[expose] public section\n", "")
    code = re.sub(r"\nend[ \t]*\n*$", "\n", code.rstrip() + "\n")
    code = "import Mathlib\n\n" + code.strip() + f"\n\n#print axioms {decl}\n"
    return "https://live.lean-lang.org/#code=" + quote(code, safe="")

def verify_html(meta, tc):
    commit = git("rev-parse", "HEAD") or "main"
    mod = meta["module"]
    return (f'<pre><code>git clone https://github.com/merethe-abeckett/formalia\ncd formalia\ngit checkout {esc(commit[:12])}\n'
            f'lake exe cache get\nlake build {esc(mod)}\nlake exe check report.json {esc(mod)}\nleanchecker {esc(mod)}</code></pre>'
            f'<p class="muted" style="font-family:var(--sans);font-size:13px">需要先<a href="https://lean-lang.org/install/">安装 Lean</a>（elan）。'
            f'工具链 <code>{esc(tc)}</code> 会按仓库里的 <code>lean-toolchain</code> 自动下载。第一次下载 Mathlib 缓存约 5 GB。</p>')

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

    body = f"<h1>表述 #{esc(sid)} <span class=\"muted\" style=\"font-weight:400\">· {esc(cname)}</span></h1>"
    if meta.get("archived"):
        a = meta["archived"]
        body += f'<p class="note"><span class="bad">已于 {esc(a.get("at",""))} 归档。</span>{esc(a.get("reason",""))} 讨论：<a href="{esc(a.get("issue",""))}">{esc(a.get("issue",""))}</a>。仅供查阅，不再编译和检查。</p>'
    if not meta.get("archived"):
        body += (f'<div class="actions"><a class="btn" href="{edit_link("../../", type="meta", target=sid)}">编辑本条信息</a>'
                 f'<a class="btn" href="{edit_link("../../", type="claim", target=sid)}">＋ 声明证明了这条表述</a>'
                 f'<a class="btn" href="{edit_link("../../", type="statement", conjecture=conj["slug"])}">＋ 为该猜想新增一条表述</a></div>')
    body += table
    body += "<h2>Lean 代码</h2><pre><code>" + esc(lean_src) + "</code></pre>"
    body += (f'<div class="actions"><a class="btn" href="{esc(live_url(lean_src, meta["declaration"]))}" target="_blank" rel="noopener">在 Lean 4 Web 中试编译 ↗</a></div>'
             '<p class="note">在浏览器里直接编译这段代码，不用安装任何东西。Lean 4 Web 使用最新版 Mathlib，和本站钉死的版本可能不同：'
             '那边报错不一定说明代码有问题，权威结果以下面的检查器报告为准。</p>')

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
    if not meta.get("archived"):
        body += "<h2>自己验证</h2><p>不想相信本站的检查结果？在自己电脑上用同样的版本重跑一遍：</p>" + verify_html(meta, tc)
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
    n_stmt = sum(n for _, n in conjs)
    n_claim = sum(len(read_json(mj).get("claimed_proofs") or []) for c, _ in conjs for mj in (CONJ / c["_dir"]).glob("S*.json"))
    mathlib = next((r for n, r, _ in deps if n == "mathlib"), "?")
    body = f'''<section class="hero"><h1>Formalia</h1>
<p class="sub">数学猜想的 Lean 表述目录</p>
<p>当有人说“AI 证明了某个猜想”，真正被证明的是一段 Lean 代码。这段代码写得是否忠实于原猜想，机器回答不了。
Formalia 把每一种写法固定下来，给它一个永久编号，再记录谁声称证明了哪个编号。只列出，不判断。</p>
<form class="search" action="search/index.html" method="get" role="search"><input name="q" placeholder="搜索猜想、表述、编号，例如“素数”" aria-label="搜索"><button>搜索</button></form>
<div class="actions"><a class="btn primary" href="#conjectures">浏览猜想</a><a class="btn" href="about/guide.html">使用说明</a>
<a class="btn" href="{edit_link("", type="statement")}">＋ 登记一条表述</a></div></section>
{author_quote()}
<div class="steps">
<div class="step"><span class="k">猜想</span><b>自然语言的命题</b><p>例如哥德巴赫猜想。每个猜想一个页面，列出它的各种 Lean 写法。</p></div>
<div class="step"><span class="k">#20261014-01</span><b>表述</b><p>一段 Lean 代码，一个永久编号。编号指向的代码永远不变。</p></div>
<div class="step"><span class="k">声称的证明</span><b>谁证明了哪个编号</b><p>只记录声明和链接，不托管证明，也不认证。</p></div>
</div>
<div class="stats"><div><b>{len(conjs)}</b>个猜想</div><div><b>{n_stmt}</b>条表述</div><div><b>{n_claim}</b>条证明声明</div>
<div><b>{"全部通过" if check_ok else "见各条目"}</b>自动检查</div><div><b style="font-size:15px;line-height:2"><code>{esc(tc.split(":")[-1])}</code> · Mathlib <code>{esc(mathlib)}</code></b>工具链</div></div>
<h2 id="conjectures">猜想</h2><ul class="cards">'''
    for c, n in conjs:
        body += (f'<li><a href="{esc(c["slug"])}/index.html"><div class="t">{esc(c.get("name_zh") or c["name"])}</div>'
                 + (f'<div class="e">{esc(c["name"])}</div>' if c.get("name_zh") else "")
                 + f'<div class="n">{n} 条表述</div></a></li>')
    body += "</ul>"
    body += ('<p class="note">谁都可以编辑，不需要注册。机器检查通过就直接写入，每次编辑都有记录、可以回退。'
             '表述是否等价于原猜想不在检查范围内，留给数学家讨论。<a href="about/guide.html">怎么用？</a></p>')
    return page(SITE_NAME, [], body, 0, home=True)

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
        "<h1>隐私与编辑规则</h1>" + md_to_html((SITE_SRC / "privacy.md").read_text(encoding="utf-8")), 1), encoding="utf-8")
    (OUT / "about" / "guide.html").write_text(page("使用说明", [("使用说明", None)],
        "<h1>使用说明</h1>" + md_to_html((SITE_SRC / "guide.md").read_text(encoding="utf-8")), 1), encoding="utf-8")
    about = (SITE_SRC / "about.md").read_text(encoding="utf-8").replace("{{PREFACE}}", "## 作者的话\n\n" + readme_preface())
    (OUT / "about" / "index.html").write_text(page("关于", [("关于", None)], "<h1>关于 Formalia</h1>" + md_to_html(about), 1), encoding="utf-8")

def write_search(index_rows):
    """站内搜索：生成 search.json 和搜索页。"""
    docs = []
    for conj, n in index_rows:
        cdir = CONJ / conj["_dir"]
        cname = conj.get("name_zh") or conj["name"]
        refs = " ".join(r.get("label", "") for r in conj.get("references") or [])
        docs.append({"kind": "c", "url": f'{conj["slug"]}/index.html', "title": cname,
                     "sub": conj["name"] if conj.get("name_zh") else "", "text": f'{conj.get("informal","")} {refs}'.strip(), "code": ""})
        for mj in sorted(cdir.glob("S*.json")):
            m = read_json(mj)
            lean = (cdir / (mj.stem + ".lean")).read_text(encoding="utf-8")
            code = re.sub(r"\s+", " ", re.sub(r"--[^\n]*", "", re.sub(r"/-.*?-/", " ", lean, flags=re.S))).strip()
            guide = GUIDES / conj["_dir"] / (mj.stem + ".md")
            gtext = re.sub(r"<!--.*?-->", "", guide.read_text(encoding="utf-8"), flags=re.S) if guide.exists() else ""
            doc = " ".join(x for x in [(m.get("informal_restatement") or {}).get("text"), (m.get("source") or {}).get("note"),
                                       " ".join(c.get("claimant", "") for c in m.get("claimed_proofs") or []),
                                       re.sub(r"[*`#]", "", gtext)] if x)
            docs.append({"kind": "s", "url": f'{conj["slug"]}/{m["id"]}/index.html', "title": f'#{m["id"]}',
                         "sub": cname, "text": re.sub(r"\s+", " ", doc).strip(), "code": f'{m["declaration"]} {code}'})
    (OUT / "search.json").write_text(json.dumps({"docs": docs}, ensure_ascii=False), encoding="utf-8")
    (OUT / "search").mkdir(exist_ok=True)
    (OUT / "search" / "search.js").write_text((SITE_SRC / "search.js").read_text(encoding="utf-8"), encoding="utf-8")
    body = ('<h1>搜索</h1><form class="search" id="search-form" role="search"><input id="q" placeholder="猜想名、关键词、编号，例如“素数”" aria-label="搜索" autocomplete="off">'
            '<button>搜索</button></form><p id="search-info">正在加载……</p><ol id="results"></ol>'
            '<noscript><p class="note bad">搜索需要启用 JavaScript。</p></noscript><script src="search.js" defer></script>')
    (OUT / "search" / "index.html").write_text(page("搜索", [("搜索", None)], body, 1), encoding="utf-8")

def write_chat_page():
    (OUT / "chat").mkdir(exist_ok=True)
    (OUT / "chat" / "chat.js").write_text((SITE_SRC / "chat.js").read_text(encoding="utf-8"), encoding="utf-8")
    body = ('<h1>灌水区</h1><p class="muted" style="font-family:var(--sans);font-size:14px">随便聊。不用注册，不用验证，进来就能说话。'
            '消息保留 7 天；为防刷屏，每两秒最多一条。发言的 IP 只有维护者可见，随消息一起 7 天后删除。'
            '<a href="../about/privacy.html">隐私与编辑规则</a></p>'
            '<div class="chat"><div class="bar"><span>#formalia</span><span id="chat-status">连接中……</span></div>'
            '<div id="chat-log" role="log" aria-live="polite"></div>'
            '<form id="chat-form" autocomplete="off"><input id="chat-input" maxlength="500" placeholder="说点什么，回车发送"><button>发送</button></form></div>'
            '<noscript><p class="note bad">聊天需要启用 JavaScript。</p></noscript><script src="chat.js" defer></script>')
    (OUT / "chat" / "index.html").write_text(page("灌水区", [("灌水区", None)], body, 1), encoding="utf-8")

def author_quote():
    """首页引文：README“阅读前说明”里以“我觉得中国”开头的那一段，标为作者的话。"""
    for line in readme_preface().splitlines():
        t = line.lstrip("> ").strip()
        if t.startswith("我觉得中国"):
            return (f'<figure class="quote"><blockquote><p>{esc(t)}</p></blockquote>'
                    '<figcaption>作者的话 · <a href="about/index.html">全文与本站原则</a></figcaption></figure>')
    return ""

def readme_preface():
    """README 里“阅读前说明”一节，网站与 README 共用一份原文。"""
    text = (ROOT / "README.md").read_text(encoding="utf-8")
    m = re.search(r"^## 阅读前说明[^\n]*\n(.*?)^---", text, re.S | re.M)
    if not m: return ""
    keep = [l for l in m.group(1).splitlines() if not re.search(r"域名|网址", l)]
    return "\n".join(keep).strip()

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
    write_chat_page()
    write_search(index_rows)
    (OUT / ".nojekyll").write_text("")
    print(f"wrote {OUT} ({sum(n for _,n in index_rows)} statements, {len(index_rows)} conjectures)")

if __name__ == "__main__":
    main()
