// 本地测试：node worker/test.mjs
// 模拟 KV、Turnstile 和 GitHub API，检查 Worker 的各条路径。
import worker, { anonId, ipKey, banKeys, safeText, fencedJson } from "./src/index.js";
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
let r = await get("/api/config"); assert.equal(r.status, 200); assert.equal((await r.json()).sitekey, "0xSITE");
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
// 查询状态
r = await get("/api/status?issue=41"); j = await r.json();
assert.equal(j.state, "applied"); assert.equal(j.message, "已写入。"); ok("status");
r = await get("/api/status?issue=999"); assert.equal(r.status, 404); ok("status of non-web issue → 404");
assert.equal(safeText("a\u0000b<c>`@x", 99), "ab＜c＞｀@​x");
assert.ok(!fencedJson({ s: "``` <!--" }).match(/[<`]/)); ok("escaping helpers");
console.log(`worker tests: ${n} passed`);
