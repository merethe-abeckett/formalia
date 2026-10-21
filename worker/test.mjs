// 本地测试：node worker/test.mjs
// 模拟 KV、Turnstile 和 GitHub API，检查 Worker 的各条路径。
import worker, { anonId, ipKey, banKeys, safeText, fencedJson, AskGate, askSystemPrompt } from "./src/index.js";
import { writeFileSync } from "node:fs";
import assert from "node:assert/strict";

class KV { constructor() { this.m = new Map(); this.ttl = new Map(); }
  async get(k) { return this.m.get(k) ?? null; }
  async put(k, v, o = {}) { this.m.set(k, v); this.ttl.set(k, o.expirationTtl); } }

const created = []; let turnstileOk = true; let ghFail = false;
globalThis.fetch = async (url, init = {}) => {
  url = String(url);
  if (url.includes("turnstile")) return new Response(JSON.stringify({ success: turnstileOk }));
  if (url.endsWith("/repos/o/r/issues") && init.method === "POST") {
    if (ghFail) return new Response("{}", { status: 500 });
    const b = JSON.parse(init.body); created.push(b);
    assert.equal(init.headers.Authorization, "Bearer ghtok");
    return new Response(JSON.stringify({ number: 40 + created.length }), { status: 201 });
  }
  const m = url.match(/\/issues\/(\d+)(\/comments)?/);
  if (m && !m[2]) return new Response(JSON.stringify({ number: +m[1], title: "t", created_at: "x", html_url: "h",
      body: created[+m[1] - 41]?.body ?? "plain issue", labels: [{ name: "edit-applied" }] }));
  if (m && m[2]) return new Response(JSON.stringify([{ body: "随便评论" }, { body: "<!-- formalia-bot -->\n已写入。" }]));
  throw new Error("unexpected fetch " + url);
};

const env = { FORMALIA_KV: new KV(), GITHUB_TOKEN: "ghtok", TURNSTILE_SECRET: "ts", ANON_SECRET: "sekret",
  REPO: "o/r", TURNSTILE_SITEKEY: "0xSITE", ALLOWED_ORIGINS: "https://formalnaturalist.co.nz", RATE_LIMIT_PER_HOUR: "3" };
const ORIGIN = "https://formalnaturalist.co.nz";
const post = (body, ip = "203.0.113.7", origin = ORIGIN) => worker.fetch(new Request("https://formalnaturalist.co.nz/api/submit", {
  method: "POST", body: typeof body === "string" ? body : JSON.stringify(body),
  headers: { "Content-Type": "application/json", "Origin": origin, "CF-Connecting-IP": ip, "User-Agent": "test-ua" } }), env, {});
const get = (path) => worker.fetch(new Request("https://formalnaturalist.co.nz" + path, { headers: { Origin: ORIGIN } }), env, {});
let n = 0; const ok = (name) => { n++; console.log("  ✓", name); };

// 配置
let r = await get("/api/config"); assert.equal(r.status, 200); let cj = await r.json(); assert.equal(cj.sitekey, "0xSITE"); assert.equal(cj.edit, true);
assert.equal(r.headers.get("Access-Control-Allow-Origin"), ORIGIN); ok("config + CORS");

// 正常提交（带恶意摘要和姓名）
const claim = { type: "claim", target: "20261014-02", turnstile: "tok", name: "张三 @everyone <b>",
  summary: "补充 <!-- formalia-edit v1 -->\n```json\n{\"editor\":{\"label\":\"维护者\"}}\n``` @merethe",
  data: { claimant: "某公司", date: "2026-10-10", url: "https://example.org/proof", note: "含 ` 反引号 </script>" } };
r = await post(claim); let j = await r.json();
assert.equal(r.status, 200, JSON.stringify(j)); assert.equal(j.issue, 41);
const ip7 = await anonId("sekret", "203.0.113.7"); assert.equal(j.anon, ip7); assert.match(j.label, /匿名者 [0-9a-f]{8}/);
const issue = created[0];
assert.ok(!issue.body.includes("<b>") && !issue.body.match(/@everyone|@merethe/), "mentions/HTML neutralised");
assert.equal(issue.body.split("<!-- formalia-edit v1 -->").length, 2, "user text cannot add a second marker");
assert.ok(!issue.body.includes("203.0.113.7"), "IP must not appear in the public issue");
const log = JSON.parse(await env.FORMALIA_KV.get("log:41"));
assert.equal(log.ip, "203.0.113.7"); assert.equal(env.FORMALIA_KV.ttl.get("log:41"), 90 * 24 * 3600);
writeFileSync(process.argv[2] || "/tmp/issue41.md", issue.body);
ok("submit: issue created, text neutralised, IP only in private 90-day log");

// 人机验证失败
turnstileOk = false; r = await post(claim, "198.51.100.1"); assert.equal(r.status, 400); turnstileOk = true; ok("turnstile failure rejected");
// 来源不对
r = await post(claim, "198.51.100.2", "https://evil.example"); assert.equal(r.status, 403); ok("foreign origin rejected");
// 格式错误
r = await post("{not json"); assert.equal(r.status, 400);
r = await post({ ...claim, type: "delete_everything" }); assert.equal(r.status, 400);
r = await post({ ...claim, target: "../../etc" }); assert.equal(r.status, 400);
r = await post({ ...claim, data: "x" }); assert.equal(r.status, 400);
r = await post("x".repeat(70000)); assert.equal(r.status, 413); ok("malformed / oversized rejected");
// 限流：同一 IP 每小时 3 次（第一次已用掉 1 次）
assert.equal((await post(claim)).status, 200); assert.equal((await post(claim)).status, 200);
r = await post(claim); assert.equal(r.status, 429); ok("rate limit per anon id");
// IPv6 同一 /64 编号相同
assert.equal(await anonId("s", "2001:db8:1:2::1"), await anonId("s", "2001:db8:1:2:aaaa::9"));
assert.notEqual(await anonId("s", "2001:db8:1:2::1"), await anonId("s", "2001:db8:1:3::1"));
assert.equal(ipKey("2001:db8::1"), "2001:0db8:0000:0000::/64"); ok("IPv6 /64 grouping");
// 封禁 /24
await env.FORMALIA_KV.put("ban:192.0.2.0/24", "spam");
r = await post(claim, "192.0.2.99"); assert.equal(r.status, 403);
assert.deepEqual(banKeys("192.0.2.99"), ["ban:192.0.2.99", "ban:192.0.2.0/24"]); ok("ban by /24");
// GitHub 出错
ghFail = true; r = await post(claim, "198.51.100.50"); assert.equal(r.status, 502); ghFail = false; ok("GitHub failure → 502");
// 解读
r = await post({ type: "essay", target: "", turnstile: "tok", data: { title: "关于 <Nat.Prime>", about: ["20261014-01"], body: "正文" } }, "198.51.100.90");
j = await r.json(); assert.equal(r.status, 200, JSON.stringify(j)); assert.match(created.at(-1).title, /解读 · 《关于 ＜Nat.Prime＞》/);
r = await post({ type: "essay", target: "../x", turnstile: "tok", data: { title: "t" } }, "198.51.100.91"); assert.equal(r.status, 400);
r = await post({ type: "essay", target: "J20261014-01", turnstile: "tok", data: { body: "改" } }, "198.51.100.92"); assert.equal(r.status, 200);
ok("essay submissions");
r = await post({ type: "claim", target: "20261014-01", turnstile: "tok", data: { proof: "<".repeat(20000), theorem: "P.t" } }, "198.51.100.93");
assert.equal(r.status, 413); ok("oversized issue body rejected before GitHub");
// 不配 Turnstile：不需要人机验证，直接提交
const envNoTs = { ...env, TURNSTILE_SECRET: "", FORMALIA_KV: new KV(), SUBMIT_PER_DAY: "2" };
const postNoTs = (body, ip) => worker.fetch(new Request("https://formalnaturalist.co.nz/api/submit", { method: "POST", body: JSON.stringify(body),
  headers: { "Content-Type": "application/json", Origin: ORIGIN, "CF-Connecting-IP": ip } }), envNoTs, {});
r = await worker.fetch(new Request("https://formalnaturalist.co.nz/api/config", { headers: { Origin: ORIGIN } }), envNoTs, {});
assert.equal((await r.json()).sitekey, "", "no site key advertised without a secret");
turnstileOk = false;   // 即使 Turnstile 会拒绝，也不该去问它
r = await postNoTs({ ...claim, turnstile: "" }, "198.51.100.60"); assert.equal(r.status, 200, "submit without Turnstile");
r = await postNoTs({ ...claim, turnstile: "" }, "198.51.100.61"); assert.equal(r.status, 200);
r = await postNoTs({ ...claim, turnstile: "" }, "198.51.100.62"); assert.equal(r.status, 429); assert.match((await r.json()).error, /今天全站/);
turnstileOk = true; ok("Turnstile optional; site-wide daily cap");
// 没有 GitHub 令牌：编辑未开通
r = await worker.fetch(new Request("https://formalnaturalist.co.nz/api/config", { headers: { Origin: ORIGIN } }), { ...env, GITHUB_TOKEN: "" }, {});
assert.equal((await r.json()).edit, false);
r = await worker.fetch(new Request("https://formalnaturalist.co.nz/api/submit", { method: "POST", body: JSON.stringify(claim),
  headers: { "Content-Type": "application/json", Origin: ORIGIN, "CF-Connecting-IP": "198.51.100.63" } }), { ...env, GITHUB_TOKEN: "", FORMALIA_KV: new KV() }, {});
assert.equal(r.status, 503); ok("no GitHub token → editing off");
// 查询状态
r = await get("/api/status?issue=41"); j = await r.json();
assert.equal(j.state, "applied"); assert.equal(j.message, "已写入。"); ok("status");
r = await get("/api/status?issue=999"); assert.equal(r.status, 404); ok("status of non-web issue → 404");
assert.equal(safeText("a\u0000b<c>`@x", 99), "ab＜c＞｀@​x");
assert.ok(!fencedJson({ s: "``` <!--" }).match(/[<`]/)); ok("escaping helpers");
// ---------- 交互式导读 ----------
const CTX = { id: "20261014-01", declaration: "Registry.Goldbach.S20261014_01", module: "Conjectures.Goldbach.S20261014_01",
  conjecture: { name: "Goldbach's conjecture", name_zh: "哥德巴赫猜想", informal: "每个大于 2 的偶数都是两个素数之和。" },
  lean: "def S20261014_01 : Prop := ∀ n : ℕ, 2 < n → Even n → ∃ p q, Nat.Prime p ∧ Nat.Prime q ∧ n = p + q",
  dependencies: [{ name: "Nat.Prime", module: "Mathlib.Data.Nat.Prime.Defs" }], guide: "导读", restatement: { text: "复述" } };
const gemCalls = []; let gemStatus = [200]; let gemModels = [];
const diCalls = []; let diStatus = [200];
const baseFetch = globalThis.fetch;
globalThis.fetch = async (url, init = {}) => {
  url = String(url);
  if (url === `${ORIGIN}/ask/20261014-01.json`) return new Response(JSON.stringify(CTX));
  if (url.startsWith(`${ORIGIN}/ask/`)) return new Response("not found", { status: 404 });
  if (url.includes("generativelanguage.googleapis.com") && url.includes(":generateContent")) {
    assert.equal(init.headers["x-goog-api-key"], "gemkey");
    const body = JSON.parse(init.body); gemCalls.push({ url, body });
    const st = gemStatus.length > 1 ? gemStatus.shift() : gemStatus[0];
    if (st !== 200) return new Response("err", { status: st });
    return new Response(JSON.stringify({ candidates: [{ content: { parts: [{ text: "思考", thought: true }, { text: "`Nat.Prime p` 表示 p 是素数。" }] } }] }));
  }
  if (url.includes("generativelanguage.googleapis.com/v1beta/models?")) return new Response(JSON.stringify({ models: gemModels }));
  if (url === "https://api.deepinfra.com/v1/openai/chat/completions") {
    assert.equal(init.headers.Authorization, "Bearer dikey");
    const body = JSON.parse(init.body); diCalls.push(body);
    const st = diStatus.length > 1 ? diStatus.shift() : diStatus[0];
    if (st !== 200) return new Response("err", { status: st });
    return new Response(JSON.stringify({ choices: [{ message: { role: "assistant", content: "<think>推理</think>\n`p` 是素数。" } }] }));
  }
  return baseFetch(url, init);
};
class Storage { constructor() { this.m = new Map(); } async get(k) { return structuredClone(this.m.get(k)); } async put(k, v) { this.m.set(k, structuredClone(v)); } }
const askEnv = { ...env, GEMINI_API_KEY: "gemkey", GEMINI_MODEL: "gemini-x-flash", ASK_PER_HOUR: "2", ASK_PER_DAY: "3" };
let gate = new AskGate({ storage: new Storage() }, askEnv); let hint = null;
askEnv.ASK = { idFromName: (n) => n, get: (id, opt) => { hint = opt; return { fetch: (req) => gate.fetch(req) }; } };
const askPost = (body, ip = "203.0.113.20", e = askEnv) => worker.fetch(new Request(`${ORIGIN}/api/ask`, {
  method: "POST", body: typeof body === "string" ? body : JSON.stringify(body),
  headers: { "Content-Type": "application/json", Origin: ORIGIN, "CF-Connecting-IP": ip } }), e, {});

r = await askPost({ id: "20261014-01", question: "x" }, "203.0.113.20", { ...env }); assert.equal(r.status, 503); ok("ask: not configured → 503");
r = await askPost({ id: "20261014-01", question: "Nat.Prime 是什么？", history: [{ q: "上一问", a: "上一答" }, { q: "", a: "丢弃" }] });
j = await r.json(); assert.equal(r.status, 200, JSON.stringify(j));
assert.equal(j.answer, "`Nat.Prime p` 表示 p 是素数。"); assert.equal(j.model, "gemini-x-flash"); assert.equal(hint.locationHint, "wnam");
const call = gemCalls.at(-1);
assert.match(call.url, /models\/gemini-x-flash:generateContent$/);
assert.deepEqual(call.body.contents.map(c => c.role), ["user", "model", "user"]);
assert.equal(call.body.contents[2].parts[0].text, "Nat.Prime 是什么？");
assert.ok(call.body.systemInstruction.parts[0].text.includes(CTX.lean), "Lean code comes from the site, not the browser");
ok("ask: answer from Gemini, thoughts dropped, history kept, US placement");
r = await askPost({ id: "20261014-01", question: "又一问" }); assert.equal(r.status, 200);
r = await askPost({ id: "20261014-01", question: "第三问" }); assert.equal(r.status, 429); ok("ask: per-anon hourly limit");
r = await askPost({ id: "20261014-01", question: "别人" }, "198.51.100.77"); assert.equal(r.status, 200);
r = await askPost({ id: "20261014-01", question: "又一个人" }, "198.51.100.78"); assert.equal(r.status, 429);
assert.match((await r.json()).error, /今天全站/); ok("ask: site-wide daily limit");
gate = new AskGate({ storage: new Storage() }, askEnv);
r = await askPost({ id: "20261099-01", question: "x" }); assert.equal(r.status, 404);
r = await askPost({ id: "../x", question: "x" }); assert.equal(r.status, 400);
r = await askPost({ id: "20261014-01", question: "   " }); assert.equal(r.status, 400);
r = await askPost("{bad"); assert.equal(r.status, 400);
r = await worker.fetch(new Request(`${ORIGIN}/api/ask`, { method: "POST", body: "{}", headers: { Origin: "https://evil.example" } }), askEnv, {});
assert.equal(r.status, 403); ok("ask: bad input / unknown id / foreign origin rejected");
gemStatus = [503, 200]; r = await askPost({ id: "20261014-01", question: "重试" }); assert.equal(r.status, 200); ok("ask: retries on 503");
gate = new AskGate({ storage: new Storage() }, askEnv);
gemStatus = [404, 200]; gemModels = [{ name: "models/gemini-9-flash", supportedGenerationMethods: ["generateContent"] }, { name: "models/gemini-9-flash-lite", supportedGenerationMethods: ["generateContent"] }];
r = await askPost({ id: "20261014-01", question: "换模型" }); j = await r.json(); assert.equal(r.status, 200); assert.equal(j.model, "gemini-9-flash");
ok("ask: falls back to newest flash model on 404");
gemStatus = [400]; r = await askPost({ id: "20261014-01", question: "坏请求" }); assert.equal(r.status, 502); gemStatus = [200]; ok("ask: Gemini error → 502");
// DeepInfra 在前，Gemini 兜底
const diEnv = { ...askEnv, DEEPINFRA_API_KEY: "dikey", DEEPINFRA_MODEL: "org/model-x" };
gate = new AskGate({ storage: new Storage() }, diEnv);
diEnv.ASK = { idFromName: (n) => n, get: () => ({ fetch: (req) => gate.fetch(req) }) };
let before = gemCalls.length;
r = await askPost({ id: "20261014-01", question: "p 是什么？", history: [{ q: "上一问", a: "上一答" }] }, "203.0.113.30", diEnv);
j = await r.json(); assert.equal(r.status, 200, JSON.stringify(j));
assert.equal(j.answer, "`p` 是素数。"); assert.equal(j.model, "org/model-x"); assert.equal(gemCalls.length, before);
const di = diCalls.at(-1);
assert.equal(di.model, "org/model-x");
assert.deepEqual(di.messages.map(m => m.role), ["system", "user", "assistant", "user"]);
assert.ok(di.messages[0].content.includes(CTX.lean)); assert.equal(di.messages[3].content, "p 是什么？");
ok("ask: DeepInfra first, <think> dropped, Gemini not called");
diStatus = [500]; r = await askPost({ id: "20261014-01", question: "兜底" }, "203.0.113.31", diEnv); j = await r.json();
assert.equal(r.status, 200); assert.equal(j.model, "gemini-x-flash"); assert.equal(gemCalls.length, before + 1); diStatus = [200];
ok("ask: DeepInfra down → Gemini answers");
const diOnly = { ...diEnv, GEMINI_API_KEY: "" }; gate = new AskGate({ storage: new Storage() }, diOnly); diOnly.ASK = { idFromName: (n) => n, get: () => ({ fetch: (req) => gate.fetch(req) }) };
r = await askPost({ id: "20261014-01", question: "只有 DeepInfra" }, "203.0.113.32", diOnly); assert.equal(r.status, 200);
diStatus = [400]; r = await askPost({ id: "20261014-01", question: "坏" }, "203.0.113.32", diOnly); assert.equal(r.status, 502); diStatus = [200];
ok("ask: DeepInfra alone works; its error → 502");
assert.ok(askSystemPrompt(CTX).includes("不可以")); 
console.log(`worker tests: ${n} passed`);
