// formalia 网页编辑表单。无需 GitHub 账号。提交给 /api/submit（Cloudflare Worker）。
// 代码许可：Apache-2.0。
(function () {
  "use strict";
  const $ = (s, r = document) => r.querySelector(s);
  const el = (tag, attrs = {}, ...kids) => {
    const e = document.createElement(tag);
    for (const [k, v] of Object.entries(attrs)) {
      if (k === "class") e.className = v; else if (k === "text") e.textContent = v;
      else if (v !== undefined && v !== null && v !== false) e.setAttribute(k, v === true ? "" : v);
    }
    for (const k of kids) e.append(k);
    return e;
  };
  const params = new URLSearchParams(location.search);
  const type = params.get("type") || "";
  const target = params.get("target") || "";
  const root = $("#edit-root");
  const TITLES = { claim: "声明证明或证否了一条表述", meta: "编辑表述信息", conjecture: "编辑猜想信息", statement: "新增一条表述", essay: target ? "修改解读" : "写一篇解读" };
  const sha256 = async (s) => [...new Uint8Array(await crypto.subtle.digest("SHA-256", new TextEncoder().encode(s.trim())))].map(b => b.toString(16).padStart(2, "0")).join("");
  const splitAbout = (s) => s.split(/[\s,，、;；]+/).map(x => x.trim().replace(/^#/, "")).filter(Boolean);

  function field(label, input, hint) {
    return el("label", { class: "f" }, el("span", { class: "fl", text: label }), input, hint ? el("span", { class: "fh", text: hint }) : "");
  }
  const text = (name, value = "", attrs = {}) => el("input", { name, value, type: "text", ...attrs });
  const area = (name, value = "", rows = 4, attrs = {}) => { const t = el("textarea", { name, rows, ...attrs }); t.value = value; return t; };
  const linesToLinks = (s) => s.split("\n").map(l => l.trim()).filter(Boolean).map(l => {
    const i = l.lastIndexOf("|"); return i < 0 ? { label: "", url: l } : { label: l.slice(0, i).trim(), url: l.slice(i + 1).trim() };
  });
  const linksToLines = (ls) => (ls || []).map(l => (l.label && l.label !== l.url ? `${l.label} | ${l.url}` : l.url)).join("\n");

  function fail(msg) { root.replaceChildren(el("p", { class: "note bad", text: msg })); }

  async function main() {
    if (!TITLES[type]) return fail("链接不完整：缺少编辑类型。请从表述页或猜想页上的按钮进入。");
    let data, cfg;
    try {
      [data, cfg] = await Promise.all([fetch("../data.json", { cache: "no-store" }).then(r => r.json()),
                                       fetch("/api/config").then(r => r.ok ? r.json() : {})]);
    } catch (e) { return fail("无法加载页面数据，请检查网络后刷新。"); }
    document.title = TITLES[type] + " · Formalia";
    $("#edit-title").textContent = TITLES[type];

    const form = el("form", { class: "edit", novalidate: true });
    const base = {}; let collect;

    if (type === "claim" || type === "meta") {
      const st = data.statements[target];
      if (!st) return fail(`找不到表述 #${target}。`);
      form.append(el("p", {}, "对象：", el("a", { href: `../${st.conjecture}/${target}/index.html`, text: `#${target}` }), `（${st.conjecture_name}）`));
      if (type === "claim") {
        const today = new Date().toISOString().slice(0, 10);
        const dir = el("select", { name: "direction" },
          el("option", { value: "prove", text: "证明：这条表述成立" }),
          el("option", { value: "disprove", text: "证否：这条表述不成立（证明它的否命题）", selected: params.get("dir") === "disprove" }));
        const how = el("select", { name: "how" }, el("option", { value: "github", text: "GitHub 仓库的固定提交（多文件项目）" }),
          el("option", { value: "pasted", text: "直接粘贴（单个文件）" }));
        const gh = el("fieldset", {}, el("legend", { text: "GitHub 仓库" }),
          field("仓库 *", text("repo", "", { maxlength: 300, placeholder: "https://github.com/用户名/仓库名" })),
          field("提交号 *", text("commit", "", { maxlength: 40, pattern: "[0-9a-f]{40}", spellcheck: "false", class: "mono" }), "完整的 40 位 commit，不能是分支名。登记的是这个固定版本，验证通过后登记库会存一份副本。"),
          field("证明所在模块 *", text("module", "", { maxlength: 200, placeholder: "MyProof.Main", spellcheck: "false" }),
            "定理所在文件的模块名。只会拉取顶层名对应的 MyProof.lean 和 MyProof/ 目录下的 .lean 文件，不用你的 lakefile。"));
        const proofArea = area("proof", "", 14, { maxlength: 40000, spellcheck: "false", class: "mono" });
        const tryOut = el("span", { class: "fh" });
        const tryBtn = el("button", { type: "button", class: "btn", text: "在 Lean 4 Web 中试编译 ↗" });
        const ps = el("fieldset", {}, el("legend", { text: "粘贴证明" }),
          field("证明代码 *", proofArea, "整个 .lean 文件，最多 4 万字符。"),
          el("div", { class: "actions" }, tryBtn), tryOut);
        const want = el("code"), note = el("p", { class: "note" });
        const sync = () => {
          const neg = dir.value === "disprove" ? "¬ " : "";
          want.textContent = neg + st.declaration;
          proofArea.placeholder = `import ${st.module}\n\ntheorem Proof.${neg ? "no" : "ok"} : ${neg}${st.declaration} := by\n  sorry`;
          gh.hidden = how.value !== "github"; ps.hidden = how.value !== "pasted";
        };
        note.append("提交后会自动编译检查：用 Lean 4.29.0 和 Mathlib v4.29.0 编译，定理的类型必须正好是 ", want,
          "，没有 sorry，只用标准公理，并经 Lean 内核重放。不通过就不登记。证明里用 ", el("code", { text: `import ${st.module}` }),
          " 导入这条表述。可以用 native_decide：登记库会让内核把那一步重新算一遍，通过后在页面上标出感叹号。");
        dir.addEventListener("change", sync); how.addEventListener("change", sync);
        // 提交前先在浏览器里试编译：把表述的代码贴在前面，换成 import Mathlib。Lean 4 Web 用的是最新版 Mathlib，结果只作参考。
        tryBtn.addEventListener("click", async () => {
          tryOut.textContent = "";
          let lean;
          try { lean = (await fetch(`../ask/${target}.json`).then(r => r.json())).lean; } catch { tryOut.textContent = "没能加载这条表述的代码。"; return; }
          const stmt = lean.replace(/^module[ \t]*\n/m, "").replace(/^public import [^\n]*\n/gm, "").replace("@[expose] public section\n", "")
            .trimEnd().replace(/\nend[ \t]*$/, "").replace(/\/-[\s\S]*?-\/\s*/, "").trim();
          const proof = proofArea.value.replace(/^\s*(public\s+)?import\s+[^\n]*\n?/gm, "").trim();
          if (!proof) { tryOut.textContent = "先在上面粘贴证明代码。"; return; }
          const code = `import Mathlib\n\n${stmt}\n\n${proof}\n`;
          window.open("https://live.lean-lang.org/#code=" + encodeURIComponent(code), "_blank", "noopener");
          tryOut.textContent = "已在新标签页打开。Lean 4 Web 用的是最新版 Mathlib，和登记库钉死的 v4.29.0 可能不同：那边通过不代表这边一定通过，以提交后的正式验证为准。";
        });
        form.append(note,
          field("方向 *", dir, "证否就是证明这条表述的否命题。两者都登记在同一个表述页上。"),
          field("声称方 *", text("claimant", "", { required: true, maxlength: 120, placeholder: "人名、机构名或模型名" }),
            "页面上会标为“自称”，登记库不核实身份。以机构或模型的名义声称时，请在下面附上公告链接。"),
          field("声称日期 *", text("date", today, { required: true, pattern: "\\d{4}-\\d{2}-\\d{2}" }), "格式 YYYY-MM-DD。这是你自己填的日期，只作参考；谁先谁后以登记库收到的时间为准。"),
          field("证明从哪里来", how), gh, ps,
          field("定理名 *", text("theorem", "", { required: true, maxlength: 200, placeholder: "MyProof.goldbach", spellcheck: "false" }), "完整的定理名。"),
          field("公告链接", text("url", "", { maxlength: 500, placeholder: "https://" }), "论文、博客或新闻稿。以机构或模型名义声称时请务必填写。"),
          field("备注", area("note", "", 3, { maxlength: 2000 }), "只写事实。"));
        sync();
        collect = (f) => {
          const d = { direction: f.direction.value, claimant: f.claimant.value, date: f.date.value, theorem: f.theorem.value.trim(), url: f.url.value.trim(), note: f.note.value };
          if (f.how.value === "pasted") d.proof = f.proof.value;
          else Object.assign(d, { repo: f.repo.value.trim(), commit: f.commit.value.trim().toLowerCase(), module: f.module.value.trim() });
          return { data: d };
        };
      } else {
        const cur = { source_note: st.source_note, source_url: st.source_url, restatement: st.restatement, external_links: st.external_links };
        form.append(
          field("来源链接", text("source_url", cur.source_url, { maxlength: 500 })),
          field("来源备注", area("source_note", cur.source_note, 3, { maxlength: 2000 })),
          field("非正式复述", area("restatement", cur.restatement, 5, { maxlength: 4000 }), "你对 Lean 代码的自然语言解读。页面上会标注为撰写者个人解读。"),
          field("外部链接", area("external_links", linksToLines(cur.external_links), 4), "每行一条，格式：名称 | 链接。只放链接，不加评价。"),
          el("p", { class: "fh", text: "Lean 代码本身不能编辑：编号永远指向同一段代码。要改代码，请新增一条表述。" }));
        collect = (f) => {
          const now = { source_url: f.source_url.value.trim(), source_note: f.source_note.value.trim(),
                        restatement: f.restatement.value.trim(), external_links: linesToLinks(f.external_links.value) };
          const d = {};
          for (const k of Object.keys(now)) if (JSON.stringify(now[k] || null) !== JSON.stringify(cur[k] || null)) { d[k] = now[k]; base[k] = cur[k]; }
          return { data: d };
        };
      }
    } else if (type === "conjecture") {
      const c = data.conjectures[target];
      if (!c) return fail(`找不到猜想 ${target}。`);
      const cur = { name_zh: c.name_zh, informal: c.informal, references: c.references };
      form.append(el("p", {}, "对象：", el("a", { href: `../${target}/index.html`, text: c.name_zh || c.name })),
        field("中文名", text("name_zh", cur.name_zh, { maxlength: 120 })),
        field("自然语言表述 *", area("informal", cur.informal, 4, { maxlength: 4000 })),
        field("参考资料", area("references", linksToLines(cur.references), 4), "每行一条，格式：名称 | 链接。"));
      collect = (f) => {
        const now = { name_zh: f.name_zh.value.trim(), informal: f.informal.value.trim(), references: linesToLinks(f.references.value) };
        const d = {};
        for (const k of Object.keys(now)) if (JSON.stringify(now[k] || null) !== JSON.stringify(cur[k] || null)) { d[k] = now[k]; base[k] = cur[k]; }
        return { data: d };
      };
    } else if (type === "essay") {
      const e = target ? (data.essays || {})[target] : null;
      if (target && !e) return fail(`找不到解读 ${target}。`);
      const cur = e ? { title: e.title, about: e.about, body: e.body } : { title: "", about: splitAbout(params.get("about") || ""), body: "" };
      if (e) form.append(el("p", {}, "对象：", el("a", { href: `../essays/${target}/index.html`, text: `《${e.title}》` })));
      const lic = el("select", { name: "license" },
        el("option", { value: "CC-BY-4.0", text: "CC-BY-4.0 知识共享 署名（默认）" }),
        el("option", { value: "CC-BY-SA-4.0", text: "CC-BY-SA-4.0 署名-相同方式共享" }),
        el("option", { value: "CC0-1.0", text: "CC0-1.0 公有领域" }));
      form.append(
        field("标题 *", text("title", cur.title, { required: true, maxlength: 120 })),
        field("相关条目 *", text("about", cur.about.join(" "), { required: true, maxlength: 400, placeholder: "例如 20261014-01 goldbach" }),
          "这篇解读讨论的表述编号或猜想标识，空格分开，最多 10 个。"),
        field("正文 *", area("body", cur.body, 18, { required: true, maxlength: 20000 }),
          "支持简单格式：## 小标题、- 列表、**粗体**、`代码`、``` 代码块 ```、[文字](https://链接)。不支持 $公式$，公式请写成代码。"),
        e ? "" : field("许可", lic, "解读发表后，任何人都可以修改它，修改按同一许可发布。"));
      collect = async (f) => {
        const now = { title: f.title.value.trim(), about: splitAbout(f.about.value), body: f.body.value.trim() };
        if (!e) return { data: { ...now, license: f.license.value } };
        const d = {};
        if (now.title !== cur.title) { d.title = now.title; base.title = cur.title; }
        if (JSON.stringify(now.about) !== JSON.stringify(cur.about)) { d.about = now.about; base.about = cur.about; }
        if (now.body !== cur.body.trim()) { d.body = now.body; base.body_sha256 = await sha256(cur.body); }
        return { data: d };
      };
    } else {
      const pre = params.get("conjecture") || "";
      const sel = el("select", { name: "conjecture" }, el("option", { value: "", text: "＋ 登记一个新猜想" }),
        ...Object.entries(data.conjectures).map(([slug, c]) => el("option", { value: slug, selected: slug === pre, text: c.name_zh ? `${c.name_zh}（${c.name}）` : c.name })));
      const nc = el("fieldset", { class: "nc" }, el("legend", { text: "新猜想" }),
        field("英文名 *", text("nc_name", "", { maxlength: 120, placeholder: "例如 Twin prime conjecture" }), "用来生成目录名，必须以字母开头。"),
        field("中文名", text("nc_name_zh", "", { maxlength: 120 })),
        field("自然语言表述 *", area("nc_informal", "", 3, { maxlength: 4000 })));
      const toggle = () => { nc.hidden = !!sel.value; };
      sel.addEventListener("change", toggle);
      const lic = el("select", { name: "license" },
        el("option", { value: "CC-BY-4.0", text: "CC-BY-4.0 知识共享 署名（默认）" }),
        el("option", { value: "CC-BY-SA-4.0", text: "CC-BY-SA-4.0 署名-相同方式共享" }),
        el("option", { value: "CC0-1.0", text: "CC0-1.0 公有领域" }),
        el("option", { value: "Apache-2.0", text: "Apache-2.0" }),
        el("option", { value: "MIT", text: "MIT" }));
      const kind = el("select", { name: "kind" }, el("option", { value: "original", text: "原创" }), el("option", { value: "adapted", text: "改编" }), el("option", { value: "verbatim", text: "照录" }));
      form.append(field("所属猜想", sel), nc,
        field("import *", area("imports", "Mathlib.Data.Nat.Prime.Defs", 3, { spellcheck: "false", class: "mono" }), "每行一个 Mathlib 或 Batteries 模块名。"),
        field("辅助定义", area("helpers", "", 5, { spellcheck: "false", class: "mono" }), "可选。只能写 def、abbrev、structure、theorem 等普通声明，会放进独立的命名空间。"),
        field("命题 *", area("proposition", "", 6, { spellcheck: "false", class: "mono", placeholder: "∀ n : ℕ, 2 < n → Even n → ∃ p q : ℕ, Nat.Prime p ∧ Nat.Prime q ∧ n = p + q" }),
          "只写 := 后面的命题本身。系统会生成 def S<编号> : Prop := …。不允许 #eval、属性、元编程、sorry、native_decide、字符串。"),
        field("说明", area("doc", "", 2, { maxlength: 2000 }), "可选，会写进文档字符串。"),
        field("来源类型", kind), field("来源链接", text("source_url", "", { maxlength: 500 }), "改编或照录时必填。"),
        field("来源备注", area("source_note", "", 2, { maxlength: 2000 })),
        field("许可", lic, "你自己写的表述可以任选。改编或照录别人的作品，必须选与原作相同或兼容的许可，并在来源备注里写明原作版权。"),
        field("非正式复述", area("restatement", "", 3, { maxlength: 4000 })));
      toggle();
      collect = (f) => {
        const d = { imports: f.imports.value.split("\n").map(s => s.trim()).filter(Boolean), helpers: f.helpers.value,
          proposition: f.proposition.value, doc: f.doc.value, restatement: f.restatement.value,
          source: { kind: f.kind.value, url: f.source_url.value.trim(), note: f.source_note.value }, license: f.license.value };
        if (f.conjecture.value) d.conjecture = f.conjecture.value;
        else d.new_conjecture = { name: f.nc_name.value, name_zh: f.nc_name_zh.value, informal: f.nc_informal.value };
        return { data: d };
      };
    }

    // 人机验证是可选的：只有配置了 Turnstile 才显示
    const ts = cfg.sitekey ? el("div", { class: "cf-turnstile", "data-sitekey": cfg.sitekey, "data-language": "zh-cn" }) : el("span");
    const btn = el("button", { type: "submit", text: "提交" });
    const out = el("p", { class: "note", hidden: true, role: "status" });
    form.append(
      field("编辑摘要", text("summary", "", { maxlength: 200, placeholder: "一句话说明改了什么" })),
      field("署名", text("name", "", { maxlength: 40, placeholder: "可不填" }), "不填就显示为“匿名者 xxxxxxxx”。"),
      el("p", { class: "fh" }, (type === "statement" ? "提交即表示同意按你选择的许可发布这条表述。" : type === "essay" && !target ? "提交即表示同意按你选择的许可发布这篇解读。" : "提交即表示同意按该条目的许可发布你的修改。") + "系统会记录你的 IP 地址以防滥用，只有维护者可见，90 天后删除；公开显示的只是由 IP 派生的匿名编号。",
         el("a", { href: "../about/privacy.html", text: "隐私与编辑规则" })),
      ts, btn, out);
    root.replaceChildren(form);
    if (!cfg.edit) { out.hidden = false; out.textContent = "编辑服务暂未开通。"; btn.disabled = true; }
    else if (cfg.sitekey) { const s = el("script", { src: "https://challenges.cloudflare.com/turnstile/v0/api.js", async: true, defer: true }); document.head.append(s); }

    form.addEventListener("submit", async (ev) => {
      ev.preventDefault();
      out.hidden = false; out.className = "note";
      const f = form.elements;
      for (const i of form.querySelectorAll("[required]")) if (!i.value.trim()) { out.textContent = "请填写所有带 * 的项目。"; i.focus(); return; }
      const { data: d } = await collect(f);
      if ((type === "meta" || type === "conjecture" || (type === "essay" && target)) && !Object.keys(d).length) { out.textContent = "你还没有修改任何内容。"; return; }
      const token = (f["cf-turnstile-response"] || {}).value || "";
      if (cfg.sitekey && !token) { out.textContent = "请先完成人机验证。"; return; }
      btn.disabled = true; out.textContent = "正在提交……";
      try {
        const r = await fetch("/api/submit", { method: "POST", headers: { "Content-Type": "application/json" },
          body: JSON.stringify({ type, target: type === "statement" ? "" : target, data: d, base, summary: f.summary.value, name: f.name.value, turnstile: token }) });
        const j = await r.json().catch(() => ({}));
        if (!r.ok || !j.ok) throw new Error(j.error || `提交失败（${r.status}）`);
        location.href = `status.html?issue=${j.issue}`;
      } catch (e) {
        out.className = "note bad"; out.textContent = e.message; btn.disabled = false;
        if (window.turnstile) window.turnstile.reset();
      }
    });
  }

  async function status() {
    const issue = parseInt(params.get("issue") || "", 10);
    const box = $("#status-root");
    if (!(issue > 0)) { box.textContent = "缺少编辑编号。"; return; }
    const STATES = { pending: "正在检查……新增表述需要编译 Lean，大约要几分钟。本页会自动刷新。", applied: "已写入。网站几分钟后更新。", rejected: "没有通过检查，未写入。" };
    for (let i = 0; i < 120; i++) {
      let j;
      try { j = await fetch(`/api/status?issue=${issue}`, { cache: "no-store" }).then(r => r.json()); } catch { j = { ok: false }; }
      box.replaceChildren();
      if (!j.ok) { box.append(el("p", { class: "note bad", text: j.error || "暂时查不到状态，稍后自动重试。" })); }
      else {
        box.append(el("p", {}, el("strong", { text: `编辑 #${issue}：` }), el("span", { class: j.state === "applied" ? "ok" : j.state === "rejected" ? "bad" : "warn", text: STATES[j.state] })));
        if (j.message) box.append(el("pre", { class: "msg", text: j.message }));
        box.append(el("p", { class: "fh" }, "完整记录：", el("a", { href: j.issue_url, text: "GitHub 议题" }), "（在中国大陆可能打不开，本页内容相同）"));
        if (j.state !== "pending") return;
      }
      await new Promise(r => setTimeout(r, 10000));
    }
  }

  if ($("#status-root")) status(); else main();
})();
