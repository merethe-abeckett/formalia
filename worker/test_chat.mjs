// 灌水区（ChatRoom Durable Object）测试。需要先在 worker/ 目录用 wrangler 本地运行：
//   npx wrangler dev --local --port 8799 （wrangler.toml 里 ANON_SECRET、CHAT_ADMIN_TOKEN=admin-token-0123456789 设为测试值）
// 然后：node worker/test_chat.mjs
import assert from "node:assert/strict";
const URL_ = "ws://127.0.0.1:8799/api/chat";
const O = "https://formalnaturalist.co.nz";
const sleep = (ms) => new Promise(r => setTimeout(r, ms));
function client(ip, origin = O) {
  return new Promise((resolve, reject) => {
    const ws = new WebSocket(URL_, { headers: { Origin: origin, "CF-Connecting-IP": ip } });
    const c = { ws, msgs: [], closed: null };
    ws.onmessage = (e) => c.msgs.push(JSON.parse(e.data));
    ws.onclose = (e) => { c.closed = e.code; };
    ws.onerror = (e) => reject(new Error("ws error"));
    ws.onopen = () => resolve(c);
    c.send = (o) => ws.send(JSON.stringify(o));
    c.last = (t) => [...c.msgs].reverse().find(m => m.t === t);
  });
}
let n = 0; const ok = (s) => { n++; console.log("  ✓", s); };

const a = await client("198.51.100.1"); await sleep(300);
const hello = a.msgs.find(m => m.t === "hello"); assert.ok(hello && /^[0-9a-f]{8}$/.test(hello.anon)); ok(`hello, anon=${hello.anon}, history=${hello.history.length}`);
const b = await client("198.51.100.2"); await sleep(300);
assert.notEqual(b.msgs.find(m => m.t === "hello").anon, hello.anon, "different IPs → different anon ids"); ok("different IP → different anon id");
a.send({ t: "nick", nick: "小王<script>@" }); await sleep(200); assert.match(a.last("sys").text, /小王script/); ok("nick sanitised");
a.send({ t: "msg", text: "大家好\n第二行 <b>hi</b>" }); await sleep(300);
const got = b.last("msg"); assert.equal(got.text, "大家好 第二行 <b>hi</b>"); assert.equal(got.nick, "小王script"); assert.ok(!("ip" in got)); ok("broadcast to other client, newlines collapsed, no IP in payload");
a.send({ t: "msg", text: "太快" }); await sleep(200); assert.match(a.last("err").text, /太快/); ok("2-second gap enforced");
await sleep(2100); a.send({ t: "msg", text: "/me 挥手" }); await sleep(300); assert.equal(b.last("msg").me, true); assert.equal(b.last("msg").text, "挥手"); ok("/me action");
await sleep(2100); a.send({ t: "msg", text: "/unknown" }); await sleep(200); assert.match(a.last("sys").text, /可用命令/); ok("unknown command not broadcast");
await sleep(2100); a.send({ t: "msg", text: "x".repeat(900) }); await sleep(300); assert.equal(b.last("msg").text.length, 500); ok("500-char cap");
// 新连接收到历史
const c = await client("198.51.100.3"); await sleep(300);
assert.ok(c.msgs.find(m => m.t === "hello").history.length >= 3); ok("history delivered to new client");
// 非管理员不能删
const target = b.last("msg").id;
b.send({ t: "del", id: target }); await sleep(200); assert.ok(!c.msgs.some(m => m.t === "del")); ok("non-admin delete ignored");
// 管理员：错口令 / 对口令 / 删除 / 封禁
c.send({ t: "auth", token: "wrong" }); await sleep(200); assert.match(c.last("sys").text, /不对/);
c.send({ t: "auth", token: "admin-token-0123456789" }); await sleep(200); assert.equal(c.last("sys").admin, true); ok("admin auth");
c.send({ t: "del", id: target }); await sleep(300); assert.deepEqual(b.last("del").ids, [target]); ok("admin delete broadcast");
await sleep(2100); a.send({ t: "msg", text: "又一条" }); await sleep(300);
c.send({ t: "ban", id: c.last("msg").id }); await sleep(500);
assert.match(c.last("sys").text, /已封禁/); await sleep(300); assert.equal(a.closed, 4003); ok("ban closes the author's socket");
let refused = false; try { const z = await client("198.51.100.1"); await sleep(300); refused = z.closed !== null || !z.msgs.length; } catch { refused = true; }
assert.ok(refused, "banned IP cannot reconnect"); ok("banned IP refused on reconnect");
// 连接数上限：同一 IP 最多 3 个
const same = []; let fails = 0;
for (let i = 0; i < 4; i++) { try { same.push(await client("198.51.100.9")); } catch { fails++; } }
await sleep(300); assert.equal(fails, 1); ok("max 3 connections per anon id");
// 外站来源
let bad = false; try { await client("198.51.100.10", "https://evil.example"); } catch { bad = true; } assert.ok(bad); ok("foreign origin refused");
console.log(`chat tests: ${n} passed`); process.exit(0);
