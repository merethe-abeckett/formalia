// Formalia 站内搜索：在浏览器里检索 search.json，不需要服务器。代码许可：Apache-2.0。
(function () {
  "use strict";
  const $ = (s) => document.querySelector(s);
  const input = $("#q"), out = $("#results"), info = $("#search-info");
  const norm = (s) => String(s || "").normalize("NFKC").toLowerCase();
  const W = { title: 10, sub: 6, text: 3, code: 1 };
  // 中文词 ↔ Lean / Mathlib 名称：搜中文也能命中代码里的英文名
  const SYN = {
    "素数": ["prime"], "质数": ["素数", "prime"], "偶数": ["even"], "奇数": ["odd"], "无穷": ["infinite", "无限"], "无限": ["infinite", "无穷"],
    "有限": ["finite"], "整除": ["dvd", "∣"], "自然数": ["ℕ", "nat"], "整数": ["ℤ", "int"], "有理数": ["ℚ", "rat"], "实数": ["ℝ", "real"],
    "复数": ["ℂ", "complex"], "集合": ["set"], "函数": ["fun"], "多项式": ["polynomial"], "矩阵": ["matrix"], "群": ["group"],
    "环": ["ring"], "域": ["field"], "图": ["graph"], "极限": ["tendsto", "filter"], "连续": ["continuous"], "可微": ["differentiable"],
    "积分": ["integral"], "级数": ["tsum", "summable"], "对数": ["log"], "平方": ["sq", "^ 2"], "最大公约数": ["gcd"], "孪生": ["twin"],
  };
  let docs = [];

  function terms(q) { return norm(q).replace(/^#/, "").split(/[\s,，、。;；]+/).filter(Boolean).map(t => t.replace(/^#/, "")); }

  const alts = (t) => [t, ...(SYN[t] || []).map(norm)];

  function score(d, ts) {
    let total = 0;
    for (const t of ts) {
      let best = 0;
      for (const a of alts(t)) {
        const bonus = a === t ? 0 : -1;   // 同义词命中略低于原词
        for (const f of ["title", "sub", "text", "code"]) {
          const v = d._n[f]; if (!v) continue;
          const i = v.indexOf(a); if (i < 0) continue;
          best = Math.max(best, W[f] + bonus + (i === 0 ? 2 : 0));
        }
      }
      if (!best) return 0;          // 每个词都要出现
      total += best;
    }
    if (d.kind === "c") total += 1; // 同分时猜想排在表述前面
    return total;
  }

  // 逐字规范化并记下每个规范化字符对应的原文位置，避免全角、省略号等改变长度后高亮错位
  function mapped(text) {
    let n = ""; const at = [];
    for (let i = 0; i < text.length; i++) { const c = norm(text[i]); n += c; for (let k = 0; k < c.length; k++) at.push(i); }
    at.push(text.length);
    return { n, at };
  }

  function highlight(text, ts) {
    const frag = document.createDocumentFragment();
    const { n, at } = mapped(text);
    const words = ts.flatMap(alts);
    let i = 0;   // i 是规范化串里的位置
    while (i < n.length) {
      let hit = -1, len = 0;
      for (const t of words) { const j = n.indexOf(t, i); if (j >= 0 && (hit < 0 || j < hit || (j === hit && t.length > len))) { hit = j; len = t.length; } }
      if (hit < 0) { frag.append(text.slice(at[i])); break; }
      frag.append(text.slice(at[i], at[hit]));
      const m = document.createElement("mark"); m.textContent = text.slice(at[hit], at[hit + len]); frag.append(m);
      i = hit + len;
    }
    return frag;
  }

  function snippet(d, ts) {
    for (const f of ["text", "code"]) {
      const v = d[f]; if (!v) continue;
      const { n, at } = mapped(v);
      const np = Math.min(...ts.flatMap(alts).map(t => n.indexOf(t)).filter(p => p >= 0));
      const pos = Number.isFinite(np) ? at[np] : NaN;
      if (Number.isFinite(pos)) {
        const a = Math.max(0, pos - 40), b = Math.min(v.length, pos + 80);
        return (a ? "…" : "") + v.slice(a, b) + (b < v.length ? "…" : "");
      }
    }
    return (d.text || "").slice(0, 120);
  }

  const PAGE = 50;   // 每次显示的条数；更多结果点按钮再加载
  let hits = [], shown = 0, curTs = [], pageSize = PAGE;

  function renderMore() {
    out.querySelector("li.more")?.remove();
    const next = hits.slice(shown, shown + pageSize); shown += next.length;
    for (const [, d] of next) out.append(item(d, curTs));
    if (shown < hits.length) {
      const li = document.createElement("li"); li.className = "more";
      const b = document.createElement("button"); b.type = "button";
      b.textContent = `再显示 ${Math.min(pageSize, hits.length - shown)} 条（还有 ${hits.length - shown} 条）`;
      b.addEventListener("click", renderMore); li.append(b); out.append(li);
    }
  }

  function item(d, ts) {
    const li = document.createElement("li");
    const a = document.createElement("a"); a.href = "../" + d.url;
    const tag = document.createElement("span"); tag.className = "tag " + d.kind; tag.textContent = { c: "猜想", s: "表述", e: "解读" }[d.kind] || "";
    const t = document.createElement("span"); t.className = "t"; t.append(highlight(d.title, ts));
    a.append(tag, t);
    if (d.sub) { const s = document.createElement("span"); s.className = "e"; s.append(" · ", highlight(d.sub, ts)); a.append(s); }
    const p = document.createElement("div"); p.className = "snip"; p.append(highlight(snippet(d, ts), ts));
    a.append(p); li.append(a); return li;
  }

  function render() {
    const q = input.value.trim();
    const url = new URL(location.href); if (q) url.searchParams.set("q", q); else url.searchParams.delete("q");
    history.replaceState(null, "", url);
    out.replaceChildren();
    const ts = terms(q);
    curTs = ts; shown = 0; pageSize = q ? PAGE : Infinity;   // 没输入时列出全部猜想，不分页
    if (!q) {   // 没输入时列出全部猜想，方便直接浏览
      hits = docs.filter(d => d.kind === "c").map(d => [1, d]);
      info.textContent = `共 ${hits.length} 个猜想、${docs.filter(d => d.kind === "s").length} 条表述。输入关键词开始搜索，中文、Lean 名称、编号都可以。`;
    } else {
      hits = docs.map(d => [score(d, ts), d]).filter(([s]) => s > 0).sort((x, y) => y[0] - x[0]);
      info.textContent = !hits.length ? "没有找到。换个说法试试，或者登记一个新猜想。"
        : hits.length > PAGE ? `找到 ${hits.length} 条结果，先显示最相关的 ${PAGE} 条` : `找到 ${hits.length} 条结果`;
    }
    renderMore();
    if (!hits.length) {
      const li = document.createElement("li"); li.className = "new"; const a = document.createElement("a");
      a.href = "../edit/index.html?type=statement"; a.textContent = "＋ 登记一条新表述（可以顺便登记新猜想）"; li.append(a); out.append(li);
    }
  }

  fetch("../search.json", { cache: "no-cache" }).then(r => r.json()).then(j => {
    docs = j.docs.map(d => ({ ...d, _n: { title: norm(d.title), sub: norm(d.sub), text: norm(d.text), code: norm(d.code) } }));
    input.value = new URLSearchParams(location.search).get("q") || "";
    render(); input.focus();
  }).catch(() => { info.textContent = "搜索数据加载失败，请刷新页面。"; });
  let timer; input.addEventListener("input", () => { clearTimeout(timer); timer = setTimeout(render, 120); });
  $("#search-form").addEventListener("submit", (e) => { e.preventDefault(); render(); });
  // 示例词：点一下直接搜，不刷新页面
  $("#chips").addEventListener("click", (e) => {
    const a = e.target.closest("a"); if (!a) return;
    e.preventDefault(); input.value = new URL(a.href).searchParams.get("q") || ""; render(); input.focus();
  });
})();
