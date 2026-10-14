#!/usr/bin/env python3
"""把一条编辑提交（网站表单或 GitHub 表单议题）应用到仓库文件。

这是唯一把不可信输入写进仓库的代码。它只做确定性的文件变换，不执行 Lean；
同一份输入在 check 任务和 commit 任务里各跑一次，结果必须相同。

输入：议题正文从 stdin 读入。
  - 网站提交：正文里有一个 ```json 代码块，紧跟标记 <!-- formalia-edit v1 -->
  - GitHub 声明表单：用 --claim-form --author <login> 解析 claim.yml 表单
输出：--result 指定的 JSON 文件 {ok, message, kind, target, changed, needs_lean, commit_message}
退出码：0 成功，1 提交内容有问题（message 写给提交者看），2 用法错误。

提交格式（v1）：
  {"v":1, "type":"claim"|"meta"|"conjecture"|"statement",
   "editor":{"label":"匿名者 7f3a1c2e","anon":"7f3a1c2e","name":""},
   "summary":"编辑摘要", "target":"20261014-01" 或猜想 slug,
   "data":{...}, "base":{...}}
代码许可：Apache-2.0。
"""
import argparse, datetime, json, re, sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import lean_policy
import licenses

ROOT = Path(__file__).resolve().parent.parent
CONJ = ROOT / "Conjectures"
ARCH = ROOT / "Archive"
MARKER = "<!-- formalia-edit v1 -->"
ID_RE = re.compile(r"^(\d{8})-(\d{2})$")
URL_RE = re.compile(r"^https?://[^\s<>\"'`]+$")
TYPE_ZH = {"claim": "声明证明", "meta": "编辑表述信息", "conjecture": "编辑猜想信息", "statement": "新增表述"}

class EditError(Exception):
    pass

# ---------- 清洗 ----------
def clean(v, maxlen, field, multiline=False, required=False):
    if v is None: v = ""
    if not isinstance(v, str): raise EditError(f"{field} 必须是文本")
    v = v.replace("\r\n", "\n").replace("\r", "\n")
    allowed = "\n\t" if multiline else ""
    v = "".join(c for c in v if c >= " " or c in allowed).strip()
    if len(v) > maxlen: raise EditError(f"{field} 太长（{len(v)} 字，上限 {maxlen}）")
    if required and not v: raise EditError(f"{field} 不能为空")
    return v

def clean_url(v, field, required=False):
    v = clean(v, 500, field, required=required)
    if v and not URL_RE.match(v): raise EditError(f"{field} 必须是 http:// 或 https:// 开头的链接")
    return v

def clean_date(v, field):
    v = clean(v, 10, field, required=True)
    try: d = datetime.date.fromisoformat(v)
    except ValueError: raise EditError(f"{field} 格式应为 YYYY-MM-DD")
    if d > datetime.date.today() + datetime.timedelta(days=1): raise EditError(f"{field} 不能是将来的日期")
    return v

def clean_links(v, field):
    if v is None: return []
    if not isinstance(v, list) or len(v) > 20: raise EditError(f"{field} 最多 20 条")
    out = []
    for i, l in enumerate(v):
        if not isinstance(l, dict): raise EditError(f"{field} 第 {i+1} 条格式不对")
        url = clean_url(l.get("url"), f"{field} 第 {i+1} 条链接", required=True)
        out.append({"label": clean(l.get("label"), 120, f"{field} 第 {i+1} 条名称") or url, "url": url})
    return out

def comment_safe(s):
    """放进 Lean 注释或文档字符串的文本，不能提前结束注释。"""
    return s.replace("-/", "- /").replace("/-", "/ -")

# ---------- 仓库查询 ----------
def find_statement(sid):
    m = ID_RE.match(sid or "")
    if not m: raise EditError(f"表述编号格式不对：{sid!r}，应为 YYYYMMDD-NN")
    hits = list(CONJ.glob(f"*/S{m.group(1)}_{m.group(2)}.json"))
    if not hits:
        if list(ARCH.glob(f"*/S{m.group(1)}_{m.group(2)}.json")):
            raise EditError(f"表述 #{sid} 已归档，不再接受编辑")
        raise EditError(f"找不到表述 #{sid}")
    return hits[0]

def load_conjectures():
    out = {}
    for d in sorted(p for p in CONJ.iterdir() if p.is_dir()):
        cj = d / "conjecture.json"
        if cj.exists(): out[json.loads(cj.read_text(encoding="utf-8"))["slug"]] = d
    return out

def norm(v):
    return v if v not in (None, "", []) else None

def check_base(base, field, current):
    if field not in base: return
    if norm(base[field]) != norm(current):
        raise EditError(f"编辑冲突：“{field}”在你打开页面之后已被别人修改。请刷新页面，在最新内容上重新编辑。")

PENDING = {}   # 路径 -> 内容；全部检查通过后才一次性写盘

def write_json(p, obj):
    PENDING[p] = json.dumps(obj, ensure_ascii=False, indent=2) + "\n"

def write_text(p, text):
    PENDING[p] = text

def flush():
    for p, text in PENDING.items():
        p.parent.mkdir(parents=True, exist_ok=True)
        p.write_text(text, encoding="utf-8")

# ---------- 四种编辑 ----------
def apply_claim(sub, editor):
    p = find_statement(sub.get("target"))
    d = sub.get("data") or {}
    claim = {
        "claimant": clean(d.get("claimant"), 120, "声称方", required=True),
        "date": clean_date(d.get("date"), "声称日期"),
        "url": clean_url(d.get("url"), "证明链接", required=True),
        "note": clean(d.get("note"), 2000, "备注", multiline=True),
        "recorded_by": editor,
    }
    meta = json.loads(p.read_text(encoding="utf-8"))
    claims = meta.setdefault("claimed_proofs", [])
    if any(c.get("url") == claim["url"] for c in claims):
        raise EditError(f"这个证明链接已经登记在 #{meta['id']} 下了")
    if len(claims) >= 200: raise EditError("该表述的声明条数已达上限")
    claims.append(claim)
    write_json(p, meta)
    return meta["id"], [p], False

META_FIELDS = {
    "source_note":    (lambda m: (m.get("source") or {}).get("note")),
    "source_url":     (lambda m: (m.get("source") or {}).get("url")),
    "restatement":    (lambda m: (m.get("informal_restatement") or {}).get("text")),
    "external_links": (lambda m: m.get("external_links") or []),
}

def apply_meta(sub, editor):
    p = find_statement(sub.get("target"))
    meta = json.loads(p.read_text(encoding="utf-8"))
    d, base = sub.get("data") or {}, sub.get("base") or {}
    unknown = set(d) - set(META_FIELDS)
    if unknown: raise EditError("不能编辑这些字段：" + "、".join(sorted(unknown)))
    fields = list(d)
    if not fields: raise EditError("没有可编辑的字段")
    changed = False
    for k in fields:
        check_base(base, k, META_FIELDS[k](meta))
        if k == "source_note":
            v = clean(d[k], 2000, "来源备注", multiline=True)
            if v != ((meta.get("source") or {}).get("note") or ""): meta.setdefault("source", {})["note"] = v; changed = True
        elif k == "source_url":
            v = clean_url(d[k], "来源链接")
            if v != ((meta.get("source") or {}).get("url") or ""): meta.setdefault("source", {})["url"] = v; changed = True
        elif k == "restatement":
            v = clean(d[k], 4000, "非正式复述", multiline=True)
            if v != ((meta.get("informal_restatement") or {}).get("text") or ""):
                meta["informal_restatement"] = {"author": editor, "text": v}; changed = True
        elif k == "external_links":
            v = clean_links(d[k], "外部链接")
            if v != (meta.get("external_links") or []): meta["external_links"] = v; changed = True
    if not changed: raise EditError("提交的内容和现有内容完全相同，没有需要修改的地方")
    write_json(p, meta)
    return meta["id"], [p], False

CONJ_FIELDS = {"name_zh": 120, "informal": 4000, "references": None}

def apply_conjecture(sub, editor):
    conjs = load_conjectures()
    slug = sub.get("target")
    if slug not in conjs: raise EditError(f"找不到猜想 {slug!r}")
    p = conjs[slug] / "conjecture.json"
    conj = json.loads(p.read_text(encoding="utf-8"))
    d, base = sub.get("data") or {}, sub.get("base") or {}
    unknown = set(d) - set(CONJ_FIELDS)
    if unknown: raise EditError("不能编辑这些字段：" + "、".join(sorted(unknown)))
    if not d: raise EditError("没有可编辑的字段")
    changed = False
    for k in d:
        check_base(base, k, conj.get(k))
        if k == "references": v = clean_links(d[k], "参考资料")
        else: v = clean(d[k], CONJ_FIELDS[k], {"name_zh": "中文名", "informal": "自然语言表述"}[k], multiline=(k == "informal"), required=(k == "informal"))
        if v != (conj.get(k) or ([] if k == "references" else "")): conj[k] = v; changed = True
    if not changed: raise EditError("提交的内容和现有内容完全相同，没有需要修改的地方")
    write_json(p, conj)
    return slug, [p], False

def dir_name_from(name):
    words = re.findall(r"[A-Za-z0-9]+", name)
    if not words or not words[0][0].isalpha(): raise EditError("新猜想需要一个以字母开头的英文名称，用来生成目录名")
    return "".join(w[:1].upper() + w[1:] for w in words)[:60], "-".join(w.lower() for w in words)[:60]

def next_id(date):
    nns = [int(m.group(1)) for base in (CONJ, ARCH) if base.exists()
           for f in base.glob(f"*/S{date}_*.*") for m in [re.match(rf"S{date}_(\d\d)\.", f.name)] if m]
    nn = max(nns, default=0) + 1
    if nn > 99: raise EditError("今天登记的表述已达 99 条上限，请明天再试")
    return f"{date}-{nn:02d}"

def apply_statement(sub, editor, created_at):
    d = sub.get("data") or {}
    conjs = load_conjectures()
    changed = []
    if d.get("conjecture"):
        slug = d["conjecture"]
        if slug not in conjs: raise EditError(f"找不到猜想 {slug!r}")
        cdir = conjs[slug]
        conj = json.loads((cdir / "conjecture.json").read_text(encoding="utf-8"))
    else:
        nc = d.get("new_conjecture") or {}
        name = clean(nc.get("name"), 120, "猜想英文名", required=True)
        dirname, slug = dir_name_from(name)
        if slug in conjs or (CONJ / dirname).exists(): raise EditError(f"已有同名猜想（{slug}），请在已有猜想下新增表述")
        conj = {"slug": slug, "name": name,
                "name_zh": clean(nc.get("name_zh"), 120, "猜想中文名"),
                "informal": clean(nc.get("informal"), 4000, "自然语言表述", multiline=True, required=True),
                "references": clean_links(nc.get("references"), "参考资料")}
        cdir = CONJ / dirname
        write_json(cdir / "conjecture.json", conj); changed.append(cdir / "conjecture.json")

    imports = [clean(i, 200, "import") for i in (d.get("imports") or [])]
    imports = [i for i in imports if i]
    if not imports: raise EditError("至少需要一个 import（例如 Mathlib.Data.Nat.Prime.Defs）")
    errs = lean_policy.check_imports(imports)
    helpers = clean(d.get("helpers"), lean_policy.MAX_FRAGMENT, "辅助定义", multiline=True)
    prop = clean(d.get("proposition"), lean_policy.MAX_FRAGMENT, "命题", multiline=True, required=True)
    if helpers: errs += ["辅助定义：" + e for e in lean_policy.check_fragment(helpers, "helpers")]
    errs += ["命题：" + e for e in lean_policy.check_fragment(prop, "proposition")]
    doc = clean(d.get("doc"), 2000, "说明", multiline=True)
    if errs: raise EditError("Lean 代码不符合登记库规范：\n- " + "\n- ".join(errs))

    date = datetime.datetime.fromisoformat(created_at.replace("Z", "+00:00")).astimezone(datetime.timezone.utc).strftime("%Y%m%d")
    sid = next_id(date)
    stem = "S" + sid.replace("-", "_")
    ns = f"Registry.{cdir.name}"
    title = comment_safe(conj.get("name_zh") or conj["name"])
    s = d.get("source") or {}
    kind = s.get("kind") or "original"
    if kind not in ("original", "adapted", "verbatim"): raise EditError("来源类型只能是原创、改编或照录")
    lic = clean(d.get("license"), 40, "许可")
    if not lic:
        if kind != "original": raise EditError("改编或照录的表述必须选择许可，并与原作许可一致或兼容")
        lic = licenses.DEFAULT
    if lic not in licenses.ALLOWED: raise EditError("许可只能是：" + "、".join(licenses.ALLOWED))
    lines = ["/-", f"Formalia · 条目 #{sid}", f"猜想：{title}", f"内容许可：{lic}",
             f"经网站提交：{comment_safe(editor)}", "", "本文件只登记一条形式化表述，不对它是否等价于原猜想作任何判断。", "-/",
             "module", ""] + [f"public import {i}" for i in imports] + ["", "@[expose] public section", "", f"namespace {ns}", ""]
    if helpers:
        lines += [f"namespace {stem}_aux", "", helpers, "", f"end {stem}_aux", "", f"open {stem}_aux in"]
    doc_txt = f"表述 #{sid}。" + (f"\n\n{comment_safe(doc)}" if doc else "")
    lines += [f"/-- {doc_txt} -/", f"def {stem} : Prop :=", "\n".join("  " + l for l in prop.splitlines()),
              "", f"end {ns}", "", "end", ""]
    src = "\n".join(lines)
    ferrs = lean_policy.check_statement_file(src)
    if ferrs: raise EditError("生成的文件没有通过规范检查：\n- " + "\n- ".join(ferrs))
    lean_path = cdir / f"{stem}.lean"
    write_text(lean_path, src)

    meta = {"id": sid, "conjecture": conj["slug"], "module": f"Conjectures.{cdir.name}.{stem}",
            "declaration": f"{ns}.{stem}", "submitted_by": editor,
            "submitted_at": f"{date[:4]}-{date[4:6]}-{date[6:]}", "license": lic,
            "source": {"kind": kind, "url": clean_url(s.get("url"), "来源链接"), "note": clean(s.get("note"), 2000, "来源备注", multiline=True)},
            "informal_restatement": {"author": editor, "text": clean(d.get("restatement"), 4000, "非正式复述", multiline=True)},
            "claimed_proofs": [], "external_links": []}
    if kind != "original" and not meta["source"]["url"]: raise EditError("改编或照录的表述必须填写来源链接")
    write_json(cdir / f"{stem}.json", meta)
    changed += [lean_path, cdir / f"{stem}.json"]
    return sid, changed, True

# ---------- 解析议题 ----------
def parse_web(body):
    i = body.rfind(MARKER)   # 取最后一个标记：标记之前的人类可读部分不能伪造数据
    if i < 0: raise EditError("议题里没有找到编辑数据")
    m = re.search(r"```json\s*\n(.*?)\n```", body[i:], re.S)
    if not m: raise EditError("议题里没有找到编辑数据")
    try: sub = json.loads(m.group(1))
    except json.JSONDecodeError as e: raise EditError(f"编辑数据不是合法 JSON：{e}")
    if not isinstance(sub, dict) or sub.get("v") != 1: raise EditError("不支持的编辑数据版本")
    return sub

def parse_claim_form(body, author):
    f = {}
    for m in re.finditer(r"^### (.+?)\s*\n+(.*?)(?=^### |\Z)", body, re.S | re.M):
        v = m.group(2).strip()
        f[m.group(1).strip()] = "" if v == "_No response_" else v
    return {"v": 1, "type": "claim", "target": f.get("表述编号", "").lstrip("#").strip(),
            "summary": "经 GitHub 表单声明证明",
            "editor": {"label": f"GitHub 用户 {author}", "anon": "", "name": author},
            "data": {"claimant": f.get("声称方"), "date": f.get("声称日期"), "url": f.get("证明链接"),
                     "note": f.get("备注（可选，只写事实）")}}

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--issue", required=True, type=int)
    ap.add_argument("--created-at", required=True)
    ap.add_argument("--result", required=True)
    ap.add_argument("--claim-form", action="store_true")
    ap.add_argument("--author", default="")
    a = ap.parse_args()
    body = sys.stdin.read()
    res = {"ok": False, "message": "", "kind": None, "target": None, "changed": [], "needs_lean": False, "commit_message": ""}
    try:
        sub = parse_claim_form(body, a.author) if a.claim_form else parse_web(body)
        kind = sub.get("type")
        if kind not in TYPE_ZH: raise EditError(f"未知的编辑类型：{kind!r}")
        ed = sub.get("editor") or {}
        editor = clean(ed.get("label"), 80, "编辑者", required=True)
        summary = clean(sub.get("summary"), 200, "编辑摘要") or TYPE_ZH[kind]
        if kind == "claim": target, changed, lean = apply_claim(sub, editor)
        elif kind == "meta": target, changed, lean = apply_meta(sub, editor)
        elif kind == "conjecture": target, changed, lean = apply_conjecture(sub, editor)
        else: target, changed, lean = apply_statement(sub, editor, a.created_at)
        flush()
        label = f"#{target}" if ID_RE.match(target) else target
        res.update(ok=True, kind=kind, target=target, needs_lean=lean,
                   changed=[str(p.relative_to(ROOT)) for p in changed],
                   message=f"{TYPE_ZH[kind]} {label} 已通过格式检查。",
                   commit_message=f"网页编辑：{TYPE_ZH[kind]} {label}：{summary}\n\n编辑者：{editor}\n议题：#{a.issue}\n")
    except EditError as e:
        res["message"] = str(e)
    Path(a.result).write_text(json.dumps(res, ensure_ascii=False, indent=2), encoding="utf-8")
    print(res["message"])
    return 0 if res["ok"] else 1

if __name__ == "__main__":
    sys.exit(main())
