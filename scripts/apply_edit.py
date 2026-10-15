#!/usr/bin/env python3
"""把一条编辑提交（网站表单或 GitHub 表单议题）应用到仓库文件。

这是唯一把不可信输入写进仓库的代码。它只做确定性的文件变换，不执行 Lean；
同一份输入在 check 任务和 commit 任务里各跑一次，结果必须相同。

输入：议题正文从 stdin 读入。
  - 网站提交：正文里有一个 ```json 代码块，紧跟标记 <!-- formalia-edit v1 -->
  - GitHub 声明表单：用 --claim-form --author <login> 解析 claim.yml 表单
输出：--result 指定的 JSON 文件 {ok, message, kind, target, claim_id, changed, needs_lean, commit_message}
声明证明写入时（--verified）可以再给 --archive-src：已拉取的证明仓库目录，把证明文件存档到 Proofs/<声明编号>/。
退出码：0 成功，1 提交内容有问题（message 写给提交者看），2 用法错误。

提交格式（v1）：
  {"v":1, "type":"claim"|"meta"|"conjecture"|"statement"|"essay",
   "editor":{"label":"匿名者 7f3a1c2e","anon":"7f3a1c2e","name":""},
   "summary":"编辑摘要", "target":"20261014-01"、猜想 slug、解读编号 J20261014-01，新增时为空,
   "data":{...}, "base":{...}}
代码许可：Apache-2.0。
"""
import argparse, datetime, hashlib, json, re, sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import lean_policy
import licenses

ROOT = Path(__file__).resolve().parent.parent
CONJ = ROOT / "Conjectures"
ARCH = ROOT / "Archive"
ESSAYS = ROOT / "Essays"
MARKER = "<!-- formalia-edit v1 -->"
ID_RE = re.compile(r"^(\d{8})-(\d{2})$")
ESSAY_ID_RE = re.compile(r"^J(\d{8})-(\d{2})$")
CLAIM_ID_RE = re.compile(r"^P(\d{8})-(\d{2})$")
ESSAY_MAX = 20000   # 议题正文上限 65536 字符，留足余量
URL_RE = re.compile(r"^https?://[^\s<>\"'`]+$")
TYPE_ZH = {"claim": "声明证明或证否", "meta": "编辑表述信息", "conjecture": "编辑猜想信息", "statement": "新增表述", "essay": "解读"}

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
PROOF_SPEC = {}  # 声明证明时：交给验证任务的证明说明
CLAIM_ID = []    # 声明证明时：新声明的编号

def write_json(p, obj):
    PENDING[p] = json.dumps(obj, ensure_ascii=False, indent=2) + "\n"

def write_text(p, text):
    PENDING[p] = text

def flush():
    for p, text in PENDING.items():
        p.parent.mkdir(parents=True, exist_ok=True)
        p.write_text(text, encoding="utf-8")

# ---------- 四种编辑 ----------
REPO_RE = re.compile(r"^https://github\.com/([A-Za-z0-9_.-]{1,100})/([A-Za-z0-9_.-]{1,100}?)(?:\.git)?/?$")
SHA_RE = re.compile(r"^[0-9a-f]{40}$")
LEAN_NAME_RE = re.compile(r"^[A-Za-z_][A-Za-z0-9_']*(\.[A-Za-z_][A-Za-z0-9_']*)*$")
ROOT_RE = re.compile(r"^[A-Z][A-Za-z0-9_]{0,40}$")
RESERVED_ROOTS = {"Conjectures", "RegistryTools", "Mathlib", "Batteries", "Lean", "Std", "Init", "Lake", "Aesop", "Qq",
                  "Plausible", "ProofWidgets", "LeanSearchClient", "ImportGraph", "Cli", "Main", "Submitted", "Archive", "Essays", "Proofs"}
PROOF_MAX = 40000   # 粘贴的证明：议题正文上限 65536 字符，JSON 转义后要放得下

def utc_date(created_at):
    return datetime.datetime.fromisoformat(created_at.replace("Z", "+00:00")).astimezone(datetime.timezone.utc).strftime("%Y%m%d")

def next_claim_id(date):
    """声明编号 PYYYYMMDD-NN：按登记日期（UTC）排，全库统一编号，归档的也算，永不复用。"""
    nns = [int(m.group(2)) for base in (CONJ, ARCH) if base.exists() for f in base.glob("*/S*.json")
           for c in json.loads(f.read_text(encoding="utf-8")).get("claimed_proofs") or []
           for m in [CLAIM_ID_RE.match(c.get("id") or "")] if m and m.group(1) == date]
    nn = max(nns, default=0) + 1
    if nn > 99: raise EditError("今天登记的证明声明已达 99 条上限，请明天再试")
    return f"P{date}-{nn:02d}"

ARCHIVE_MAX_FILES, ARCHIVE_MAX_BYTES = 500, 5 * 1024 * 1024

def archive_files(src, root):
    """从已拉取的证明仓库里挑出要存档的文件：<root>.lean 和 <root>/ 下的 .lean，规则和编译时一样。超出上限返回 None。"""
    src = Path(src).resolve()
    files = ([Path(f"{root}.lean")] if (src / f"{root}.lean").is_file() else []) + \
            ([q.relative_to(src) for q in sorted((src / root).rglob("*.lean"))] if (src / root).is_dir() else [])
    out, total = [], 0
    for rel in files:
        q = src / rel
        if q.is_symlink() or not q.resolve().is_relative_to(src): continue
        total += q.stat().st_size
        if len(out) >= ARCHIVE_MAX_FILES or total > ARCHIVE_MAX_BYTES: return None
        out.append((rel, q.read_text(encoding="utf-8", errors="replace")))
    return out

def clean_proof(d, cid):
    """证明的来源：GitHub 仓库的固定提交，或者直接粘贴的单个文件。返回写进登记的字段和交给验证任务的说明。"""
    theorem = clean(d.get("theorem"), 200, "定理名", required=True)
    if not LEAN_NAME_RE.match(theorem): raise EditError("定理名格式不对，应为 Lean 名字，例如 MyProof.goldbach")
    if d.get("proof"):
        text = clean(d.get("proof"), PROOF_MAX, "证明代码", multiline=True, required=True)
        path = f"Proofs/{cid.replace('-', '_')}.lean"
        return ({"source": "pasted", "file": path, "theorem": theorem},
                {"kind": "pasted", "text": text, "root": "Proof", "module": "Proof", "theorem": theorem, "store": path})
    m = REPO_RE.match(clean(d.get("repo"), 300, "仓库链接", required=True))
    if not m: raise EditError("仓库链接应为 https://github.com/用户名/仓库名")
    commit = clean(d.get("commit"), 40, "提交号", required=True).lower()
    if not SHA_RE.match(commit): raise EditError("提交号必须是完整的 40 位十六进制 commit，不能是分支名")
    module = clean(d.get("module"), 200, "证明所在模块", required=True)
    if not LEAN_NAME_RE.match(module): raise EditError("模块名格式不对，例如 MyProof.Main")
    root = module.split(".")[0]
    if not ROOT_RE.match(root) or root in RESERVED_ROOTS:
        raise EditError(f"模块的顶层名 {root} 不可用：需以大写字母开头，且不能是 " + "、".join(sorted(RESERVED_ROOTS)))
    repo = f"https://github.com/{m.group(1)}/{m.group(2)}"
    return ({"source": "github", "repo": repo, "commit": commit, "module": module, "theorem": theorem},
            {"kind": "github", "repo": repo, "commit": commit, "root": root, "module": module, "theorem": theorem})

DIRECTION_ZH = {"prove": "证明", "disprove": "证否"}

def apply_claim(sub, editor, created_at, verified=None, archive_src=None):
    p = find_statement(sub.get("target"))
    d = sub.get("data") or {}
    meta = json.loads(p.read_text(encoding="utf-8"))
    direction = d.get("direction") or "prove"
    if direction not in DIRECTION_ZH: raise EditError("方向只能是证明（prove）或证否（disprove）")
    cid = next_claim_id(utc_date(created_at))
    proof, spec = clean_proof(d, cid)
    claim = {
        "id": cid,
        "direction": direction,
        "registered_at": datetime.datetime.fromisoformat(created_at.replace("Z", "+00:00")).astimezone(datetime.timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ"),
        "claimant": clean(d.get("claimant"), 120, "声称方", required=True),
        "date": clean_date(d.get("date"), "声称日期"),
        "url": (f"{proof['repo']}/tree/{proof['commit']}" if proof["source"] == "github"
                else f"https://github.com/merethe-abeckett/formalia/blob/main/{proof['file']}"),
        "proof": proof,
        "note": clean(d.get("note"), 2000, "备注", multiline=True),
        "recorded_by": editor,
    }
    if d.get("url"): claim["announcement"] = clean_url(d.get("url"), "公告链接")
    if verified: claim["verification"] = verified
    claims = meta.setdefault("claimed_proofs", [])
    same = lambda c: (c.get("proof") or {}).get("repo") == proof.get("repo") and (c.get("proof") or {}).get("commit") == proof.get("commit") \
        and (c.get("proof") or {}).get("theorem") == proof["theorem"]
    if proof["source"] == "github" and any(same(c) for c in claims):
        raise EditError(f"这个提交里的这个定理已经登记在 #{meta['id']} 下了")
    if proof["source"] == "github" and verified and archive_src:
        files = archive_files(archive_src, spec["root"])
        if files:
            proof["archive"] = f"Proofs/{cid.replace('-', '_')}"
            for rel, text in files:
                write_text(ROOT / proof["archive"] / rel, text)
    if len(claims) >= 200: raise EditError("该表述的声明条数已达上限")
    claims.append(claim)
    write_json(p, meta)
    changed = [p]
    if spec["kind"] == "pasted":
        sp = ROOT / spec["store"]
        write_text(sp, spec["text"] + "\n"); changed.append(sp)
    if proof.get("archive"): changed.append(ROOT / proof["archive"])
    spec.update(statement=meta["declaration"], statement_module=meta["module"], direction=direction)
    PROOF_SPEC.update(spec)
    CLAIM_ID.append(cid)
    return meta["id"], changed, False

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

    date = utc_date(created_at)
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

# ---------- 解读 ----------
def essay_about(v, conjs):
    """解读挂在哪些表述或猜想下面：至少一个，最多 10 个，必须都存在。"""
    if not isinstance(v, list) or not v: raise EditError("请至少填写一个相关的表述编号或猜想")
    if len(v) > 10: raise EditError("相关条目最多 10 个")
    out = []
    for x in v:
        x = clean(x, 80, "相关条目").lstrip("#")
        m = ID_RE.match(x)
        if m:
            if not any(b.exists() and list(b.glob(f"*/S{m.group(1)}_{m.group(2)}.json")) for b in (CONJ, ARCH)):
                raise EditError(f"找不到表述 #{x}")
        elif x not in conjs:
            raise EditError(f"找不到表述或猜想：{x}（表述写编号如 20261014-01，猜想写标识如 goldbach）")
        if x not in out: out.append(x)
    return out

def body_sha(text):
    return hashlib.sha256(text.strip().encode("utf-8")).hexdigest()

def apply_essay(sub, editor, created_at):
    d, base = sub.get("data") or {}, sub.get("base") or {}
    conjs = load_conjectures()
    target = sub.get("target") or ""
    if target:                                     # 修改已有的解读
        m = ESSAY_ID_RE.match(target)
        if not m: raise EditError(f"解读编号格式不对：{target!r}，应为 JYYYYMMDD-NN")
        stem = f"J{m.group(1)}_{m.group(2)}"
        mp, bp = ESSAYS / f"{stem}.json", ESSAYS / f"{stem}.md"
        if not mp.exists(): raise EditError(f"找不到解读 {target}")
        meta, body = json.loads(mp.read_text(encoding="utf-8")), bp.read_text(encoding="utf-8")
        unknown = set(d) - {"title", "about", "body"}
        if unknown: raise EditError("不能编辑这些字段：" + "、".join(sorted(unknown)))
        if not d: raise EditError("没有可编辑的字段")
        changed = False
        if "title" in d:
            check_base(base, "title", meta["title"])
            v = clean(d["title"], 120, "标题", required=True)
            if v != meta["title"]: meta["title"] = v; changed = True
        if "about" in d:
            check_base(base, "about", meta["about"])
            v = essay_about(d["about"], conjs)
            if v != meta["about"]: meta["about"] = v; changed = True
        if "body" in d:
            if "body_sha256" in base and base["body_sha256"] != body_sha(body):
                raise EditError("编辑冲突：正文在你打开页面之后已被别人修改。请刷新页面，在最新内容上重新编辑。")
            v = clean(d["body"], ESSAY_MAX, "正文", multiline=True, required=True)
            if v != body.strip(): body = v + "\n"; changed = True
        if not changed: raise EditError("提交的内容和现有内容完全相同，没有需要修改的地方")
        if editor != meta.get("author") and editor not in meta.setdefault("editors", []): meta["editors"].append(editor)
        write_json(mp, meta); write_text(bp, body)
        return target, [mp, bp], False

    unknown = set(d) - {"title", "about", "body", "license"}
    if unknown: raise EditError("不认识这些字段：" + "、".join(sorted(unknown)))
    title = clean(d.get("title"), 120, "标题", required=True)
    about = essay_about(d.get("about"), conjs)
    body = clean(d.get("body"), ESSAY_MAX, "正文", multiline=True, required=True)
    lic = clean(d.get("license"), 40, "许可") or licenses.DEFAULT
    if lic not in licenses.ALLOWED: raise EditError("许可只能是：" + "、".join(licenses.ALLOWED))
    date = utc_date(created_at)
    nns = [int(m.group(1)) for f in (ESSAYS.glob(f"J{date}_*.json") if ESSAYS.exists() else []) for m in [re.match(rf"J{date}_(\d\d)\.", f.name)] if m]
    nn = max(nns, default=0) + 1
    if nn > 99: raise EditError("今天的解读已达 99 篇上限，请明天再试")
    eid, stem = f"J{date}-{nn:02d}", f"J{date}_{nn:02d}"
    meta = {"id": eid, "title": title, "about": about, "author": editor,
            "submitted_at": f"{date[:4]}-{date[4:6]}-{date[6:]}", "license": lic}
    mp, bp = ESSAYS / f"{stem}.json", ESSAYS / f"{stem}.md"
    write_json(mp, meta); write_text(bp, body + "\n")
    return eid, [mp, bp], False

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
            "summary": "经 GitHub 表单声明" + ("证否" if "证否" in f.get("方向", "") else "证明"),
            "editor": {"label": f"GitHub 用户 {author}", "anon": "", "name": author},
            "data": {"direction": "disprove" if "证否" in f.get("方向", "") else "prove",
                     "claimant": f.get("声称方"), "date": f.get("声称日期"), "repo": f.get("证明仓库"),
                     "commit": f.get("提交号"), "module": f.get("证明所在模块"), "theorem": f.get("定理名"),
                     "url": f.get("公告链接（可选）"), "note": f.get("备注（可选，只写事实）")}}

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--issue", required=True, type=int)
    ap.add_argument("--created-at", required=True)
    ap.add_argument("--result", required=True)
    ap.add_argument("--claim-form", action="store_true")
    ap.add_argument("--author", default="")
    ap.add_argument("--verified", default="", help="证明验证通过后由写入任务传入：验证记录 JSON")
    ap.add_argument("--archive-src", default="", help="写入任务传入：已拉取的证明仓库目录，用来存档 GitHub 来源的证明")
    a = ap.parse_args()
    body = sys.stdin.read()
    res = {"ok": False, "message": "", "kind": None, "target": None, "claim_id": None, "changed": [], "needs_lean": False, "needs_proof": False, "proof": None, "commit_message": ""}
    try:
        sub = parse_claim_form(body, a.author) if a.claim_form else parse_web(body)
        kind = sub.get("type")
        if kind not in TYPE_ZH: raise EditError(f"未知的编辑类型：{kind!r}")
        ed = sub.get("editor") or {}
        editor = clean(ed.get("label"), 80, "编辑者", required=True)
        summary = clean(sub.get("summary"), 200, "编辑摘要") or TYPE_ZH[kind]
        if kind == "claim": target, changed, lean = apply_claim(sub, editor, a.created_at, json.loads(a.verified) if a.verified else None, a.archive_src or None)
        elif kind == "meta": target, changed, lean = apply_meta(sub, editor)
        elif kind == "conjecture": target, changed, lean = apply_conjecture(sub, editor)
        elif kind == "essay": target, changed, lean = apply_essay(sub, editor, a.created_at)
        else: target, changed, lean = apply_statement(sub, editor, a.created_at)
        flush()
        label = f"#{target}" if ID_RE.match(target) else target
        if CLAIM_ID: label = f"{CLAIM_ID[0]}（{DIRECTION_ZH[PROOF_SPEC['direction']]} #{target}）"
        res.update(ok=True, kind=kind, target=target, claim_id=(CLAIM_ID or [None])[0], needs_lean=lean, needs_proof=bool(PROOF_SPEC), proof=PROOF_SPEC or None,
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
