/**
 * formalia 编辑网关（Cloudflare Worker）
 *
 * 让没有 GitHub 账号的人也能编辑登记库。网站表单把编辑提交到这里，
 * Worker 验证人机校验、限流、记录 IP，然后用一个只能开议题的令牌在
 * formalia 仓库开一个议题。仓库里的 Edit 工作流接手：检查、写入、发布。
 *
 * 路由（挂在 formalnaturalist.co.nz/api/*）：
 *   GET  /api/config            站点需要的公开配置（Turnstile site key）
 *   POST /api/submit            提交一条编辑
 *   GET  /api/status?issue=N    查询某条编辑的处理结果（不必打开 GitHub）
 *   GET  /api/chat              灌水区聊天室（WebSocket，由 Durable Object ChatRoom 承载）
 *
 * 绑定（在 Cloudflare 后台配置，见 docs/WEB_EDIT.md）：
 *   KV        FORMALIA_KV        限流计数、封禁名单、私有编辑日志
 *   Secret    GITHUB_TOKEN       细粒度令牌，只授予 formalia 的 Issues 读写
 *   Secret    TURNSTILE_SECRET   Turnstile 密钥
 *   Secret    ANON_SECRET        生成匿名编号用的随机串
 *   Variable  REPO               merethe-abeckett/formalia
 *   Variable  TURNSTILE_SITEKEY  Turnstile 站点密钥（公开）
 *   Variable  ALLOWED_ORIGINS    逗号分隔，如 https://formalnaturalist.co.nz,https://www.formalnaturalist.co.nz
 *   Variable  RATE_LIMIT_PER_HOUR  每个匿名编号每小时可提交次数，默认 6
 *   Durable Object  CHAT         ChatRoom 类（灌水区）
 *   Secret    CHAT_ADMIN_TOKEN   聊天室管理员口令（删消息、封禁）
 *
 * 隐私：完整 IP 只写进 KV 的私有日志（log:<议题号>），保存 90 天后自动删除，
 * 只有仓库维护者能在 Cloudflare 后台看到。公开显示的只有由 IP 派生的匿名编号。
 *
 * 代码许可：Apache-2.0。
 */

const LOG_TTL = 90 * 24 * 3600;
const MAX_BODY = 64 * 1024;
const TYPES = { claim: "声明证明", meta: "编辑表述信息", conjecture: "编辑猜想信息", statement: "新增表述" };
const ID_RE = /^\d{8}-\d{2}$/;
const SLUG_RE = /^[a-z0-9][a-z0-9-]{0,59}$/;
const MARKER = "<!-- formalia-edit v1 -->";
const BOT_MARKER = "<!-- formalia-bot -->";

export default {
  async fetch(request, env, ctx) {
    const url = new URL(request.url);
    const origin = request.headers.get("Origin") || "";
    const allowed = (env.ALLOWED_ORIGINS || "").split(",").map(s => s.trim()).filter(Boolean);
    const cors = allowed.includes(origin)
      ? { "Access-Control-Allow-Origin": origin, "Vary": "Origin", "Access-Control-Allow-Methods": "GET, POST, OPTIONS", "Access-Control-Allow-Headers": "Content-Type" }
      : {};
    const reply = (status, obj, extra = {}) => new Response(JSON.stringify(obj), {
      status, headers: { "Content-Type": "application/json; charset=utf-8", "Cache-Control": "no-store", ...cors, ...extra } });

    try {
      if (request.method === "OPTIONS") return new Response(null, { status: 204, headers: cors });
      if (url.pathname === "/api/config" && request.method === "GET")
        return reply(200, { sitekey: env.TURNSTILE_SITEKEY || "", repo: env.REPO || "" });
      if (url.pathname === "/api/submit" && request.method === "POST") {
        if (allowed.length && !allowed.includes(origin)) return reply(403, { ok: false, error: "来源不被允许" });
        return await submit(request, env, reply);
      }
      if (url.pathname === "/api/status" && request.method === "GET") return await status(url, env, reply);
      if (url.pathname === "/api/chat") return await chat(request, env, reply, allowed, origin);
      return reply(404, { ok: false, error: "没有这个接口" });
    } catch (e) {
      return reply(500, { ok: false, error: "服务器内部错误，请稍后再试" });
    }
  },
};

// ---------- 工具 ----------
export function clientIp(request) {
  return request.headers.get("CF-Connecting-IP") || "0.0.0.0";
}

/** IPv6 取 /64 前缀，避免同一个人换地址就换编号。 */
export function ipKey(ip) {
  if (ip.includes(":")) {
    const parts = expandV6(ip);
    return parts.slice(0, 4).join(":") + "::/64";
  }
  return ip;
}
function expandV6(ip) {
  const [head, tail] = ip.split("::");
  const h = head ? head.split(":") : [];
  const t = tail !== undefined ? (tail ? tail.split(":") : []) : [];
  const fill = tail !== undefined ? Array(8 - h.length - t.length).fill("0") : [];
  return [...h, ...fill, ...t].map(x => x.toLowerCase().padStart(4, "0"));
}
/** 封禁可以写完整 IP、IPv4 /24 或 IPv6 /48。 */
export function banKeys(ip) {
  if (ip.includes(":")) {
    const p = expandV6(ip);
    return [`ban:${ip}`, `ban:${p.slice(0, 4).join(":")}::/64`, `ban:${p.slice(0, 3).join(":")}::/48`];
  }
  const o = ip.split(".");
  return [`ban:${ip}`, `ban:${o.slice(0, 3).join(".")}.0/24`];
}

export async function anonId(secret, ip) {
  const key = await crypto.subtle.importKey("raw", new TextEncoder().encode(secret), { name: "HMAC", hash: "SHA-256" }, false, ["sign"]);
  const sig = new Uint8Array(await crypto.subtle.sign("HMAC", key, new TextEncoder().encode(ipKey(ip))));
  return [...sig.slice(0, 4)].map(b => b.toString(16).padStart(2, "0")).join("");
}

/** 显示在议题正文里的人类可读文本：去掉控制字符，中和 HTML、提及、代码块。 */
export function safeText(s, max) {
  s = String(s ?? "").replace(/[\u0000-\u0008\u000b-\u001f\u007f]/g, "").trim().slice(0, max);
  return s.replace(/[<>`]/g, c => ({ "<": "＜", ">": "＞", "`": "｀" }[c])).replace(/@/g, "@​");
}
/** 放进 ```json 代码块的数据：把可能干扰标记和代码块的字符转义。 */
export function fencedJson(obj) {
  return JSON.stringify(obj, null, 2).replace(/[<>`]/g, c => "\\u" + c.charCodeAt(0).toString(16).padStart(4, "0"));
}

async function gh(env, method, path, body) {
  const r = await fetch(`https://api.github.com${path}`, {
    method,
    headers: { "Authorization": `Bearer ${env.GITHUB_TOKEN}`, "Accept": "application/vnd.github+json",
               "User-Agent": "formalia-edit-gateway", "X-GitHub-Api-Version": "2022-11-28",
               ...(body ? { "Content-Type": "application/json" } : {}) },
    body: body ? JSON.stringify(body) : undefined,
  });
  const text = await r.text();
  let data = null; try { data = JSON.parse(text); } catch { /* ignore */ }
  return { ok: r.ok, status: r.status, data };
}

async function verifyTurnstile(env, token, ip) {
  if (!token) return false;
  const form = new FormData();
  form.append("secret", env.TURNSTILE_SECRET || "");
  form.append("response", token);
  form.append("remoteip", ip);
  const r = await fetch("https://challenges.cloudflare.com/turnstile/v0/siteverify", { method: "POST", body: form });
  const d = await r.json().catch(() => ({}));
  return d.success === true;
}

// ---------- 提交 ----------
async function submit(request, env, reply) {
  const raw = await request.text();
  if (raw.length > MAX_BODY) return reply(413, { ok: false, error: "提交内容太大" });
  let req;
  try { req = JSON.parse(raw); } catch { return reply(400, { ok: false, error: "提交格式不对" }); }
  if (!req || typeof req !== "object") return reply(400, { ok: false, error: "提交格式不对" });

  const type = req.type;
  if (!TYPES[type]) return reply(400, { ok: false, error: "未知的编辑类型" });
  const target = String(req.target ?? "");
  if ((type === "claim" || type === "meta") && !ID_RE.test(target)) return reply(400, { ok: false, error: "表述编号格式不对" });
  if (type === "conjecture" && !SLUG_RE.test(target)) return reply(400, { ok: false, error: "猜想标识格式不对" });
  if (req.data == null || typeof req.data !== "object" || Array.isArray(req.data)) return reply(400, { ok: false, error: "缺少编辑内容" });

  const ip = clientIp(request);
  const kv = env.FORMALIA_KV;
  for (const k of banKeys(ip)) {
    if (await kv.get(k)) return reply(403, { ok: false, error: "该网络地址已被暂停编辑。如有误会请写信说明。" });
  }
  if (!(await verifyTurnstile(env, req.turnstile, ip))) return reply(400, { ok: false, error: "人机验证没有通过，请刷新页面重试" });

  const anon = await anonId(env.ANON_SECRET || "", ip);
  const limit = parseInt(env.RATE_LIMIT_PER_HOUR || "6", 10);
  const rlKey = `rl:${anon}:${Math.floor(Date.now() / 3600000)}`;
  const used = parseInt((await kv.get(rlKey)) || "0", 10);
  if (used >= limit) return reply(429, { ok: false, error: `提交太频繁了，每小时最多 ${limit} 次，请稍后再试` });
  await kv.put(rlKey, String(used + 1), { expirationTtl: 7200 });

  const name = safeText(req.name, 40).replace(/[（）()]/g, "");
  const label = name ? `${name}（匿名者 ${anon}）` : `匿名者 ${anon}`;
  const summary = safeText(req.summary, 200);
  const sub = { v: 1, type, target: target || null, summary, editor: { label, anon, name },
                data: req.data, base: (req.base && typeof req.base === "object") ? req.base : {} };

  const where = type === "statement"
    ? (req.data.conjecture ? `猜想 ${safeText(req.data.conjecture, 60)}` : `新猜想 ${safeText(req.data.new_conjecture?.name, 80)}`)
    : (ID_RE.test(target) ? `#${target}` : target);
  const title = `[网页编辑] ${TYPES[type]} · ${where} · ${label}`.slice(0, 250);
  const body = [
    `**${TYPES[type]}** · ${where}`, "",
    `编辑者：${label}`, `摘要：${summary || "（无）"}`, "",
    "本议题由网站自动创建。机器人会自动检查并处理，结果会回复在下面，处理完自动关闭。", "",
    MARKER, "```json", fencedJson(sub), "```", "",
  ].join("\n");

  const r = await gh(env, "POST", `/repos/${env.REPO}/issues`, { title, body });
  if (!r.ok) return reply(502, { ok: false, error: "暂时无法提交，请稍后再试" });
  const issue = r.data.number;

  await kv.put(`log:${issue}`, JSON.stringify({
    ip, anon, ua: (request.headers.get("User-Agent") || "").slice(0, 300),
    country: request.cf?.country || "", ts: new Date().toISOString(), type, target: target || where,
  }), { expirationTtl: LOG_TTL });

  return reply(200, { ok: true, issue, anon, label, status_url: `/edit/status.html?issue=${issue}` });
}

// ---------- 查询 ----------
async function status(url, env, reply) {
  const issue = parseInt(url.searchParams.get("issue") || "", 10);
  if (!(issue > 0)) return reply(400, { ok: false, error: "缺少议题号" });
  const i = await gh(env, "GET", `/repos/${env.REPO}/issues/${issue}`);
  if (!i.ok) return reply(404, { ok: false, error: "找不到这条编辑" });
  if (!String(i.data.body || "").includes(MARKER)) return reply(404, { ok: false, error: "这不是网页编辑" });
  const c = await gh(env, "GET", `/repos/${env.REPO}/issues/${issue}/comments?per_page=50`);
  const bot = (c.data || []).filter(x => String(x.body || "").includes(BOT_MARKER)).pop();
  const labels = (i.data.labels || []).map(l => (typeof l === "string" ? l : l.name));
  let state = "pending";
  if (labels.includes("edit-applied")) state = "applied";
  else if (labels.includes("edit-rejected")) state = "rejected";
  return reply(200, {
    ok: true, issue, state, title: i.data.title, created_at: i.data.created_at,
    message: bot ? String(bot.body).replace(BOT_MARKER, "").trim() : "",
    issue_url: i.data.html_url,
  }, { "Cache-Control": "public, max-age=15" });
}

// ---------- 灌水区 ----------
const CHAT_KEEP_MS = 7 * 24 * 3600 * 1000;   // 消息（连同发言 IP）保存 7 天
const CHAT_HISTORY = 150;                     // 新连接收到的历史条数
const CHAT_MAX_LEN = 500;
const CHAT_MIN_GAP_MS = 2000;                 // 同一编号两条消息至少间隔 2 秒
const CHAT_PER_MIN = 30;
const CHAT_CONN_PER_ANON = 3;
const CHAT_CONN_TOTAL = 300;

async function chat(request, env, reply, allowed, origin) {
  if (request.headers.get("Upgrade") !== "websocket") return reply(426, { ok: false, error: "需要 WebSocket" });
  if (allowed.length && !allowed.includes(origin)) return reply(403, { ok: false, error: "来源不被允许" });
  const ip = clientIp(request);
  for (const k of banKeys(ip)) if (await env.FORMALIA_KV.get(k)) return reply(403, { ok: false, error: "该网络地址已被暂停发言" });
  const anon = await anonId(env.ANON_SECRET || "", ip);
  const headers = new Headers(request.headers);
  headers.set("X-Formalia-Anon", anon);
  headers.set("X-Formalia-IP", ip);
  const stub = env.CHAT.get(env.CHAT.idFromName("lobby"));
  return stub.fetch(new Request("https://chat/connect", { headers }));
}

export function cleanChatText(s, max) {
  return String(s ?? "").replace(/[\u0000-\u001f\u007f\u2028\u2029]/g, " ").replace(/\s+/g, " ").trim().slice(0, max);
}

export class ChatRoom {
  constructor(ctx, env) {
    this.ctx = ctx; this.env = env;
    ctx.blockConcurrencyWhile(async () => {
      ctx.storage.sql.exec(`CREATE TABLE IF NOT EXISTS msg (
        id INTEGER PRIMARY KEY AUTOINCREMENT, ts INTEGER NOT NULL, anon TEXT NOT NULL,
        nick TEXT NOT NULL, text TEXT NOT NULL, me INTEGER NOT NULL, ip TEXT NOT NULL)`);
    });
  }

  online() { return this.ctx.getWebSockets().length; }
  send(ws, obj) { try { ws.send(JSON.stringify(obj)); } catch { /* 连接已断 */ } }
  broadcast(obj) { const m = JSON.stringify(obj); for (const ws of this.ctx.getWebSockets()) { try { ws.send(m); } catch { } } }
  purge() { this.ctx.storage.sql.exec("DELETE FROM msg WHERE ts < ?", Date.now() - CHAT_KEEP_MS); }
  history() {
    return this.ctx.storage.sql.exec("SELECT id, ts, anon, nick, text, me FROM msg ORDER BY id DESC LIMIT ?", CHAT_HISTORY)
      .toArray().reverse().map(r => ({ id: r.id, ts: r.ts, anon: r.anon, nick: r.nick, text: r.text, me: !!r.me }));
  }

  async fetch(request) {
    const anon = request.headers.get("X-Formalia-Anon") || "";
    const ip = request.headers.get("X-Formalia-IP") || "";
    if (!anon) return new Response("bad", { status: 400 });
    if (this.online() >= CHAT_CONN_TOTAL) return new Response("聊天室人数已满，请稍后再来", { status: 503 });
    if (this.ctx.getWebSockets(anon).length >= CHAT_CONN_PER_ANON) return new Response("同一网络连接数过多", { status: 429 });
    const [client, server] = Object.values(new WebSocketPair());
    this.ctx.acceptWebSocket(server, [anon]);
    server.serializeAttachment({ anon, ip, nick: "", admin: false, times: [] });
    this.purge();
    this.send(server, { t: "hello", anon, online: this.online(), history: this.history(), keep_days: 7 });
    this.broadcast({ t: "online", n: this.online() });
    return new Response(null, { status: 101, webSocket: client });
  }

  async webSocketMessage(ws, raw) {
    let m; try { m = JSON.parse(typeof raw === "string" ? raw : new TextDecoder().decode(raw)); } catch { return; }
    if (!m || typeof m !== "object") return;
    const a = ws.deserializeAttachment() || {};
    if (m.t === "ping") return this.send(ws, { t: "pong" });
    if (m.t === "nick") {
      a.nick = cleanChatText(m.nick, 20).replace(/[<>@#]/g, "");
      ws.serializeAttachment(a);
      return this.send(ws, { t: "sys", text: a.nick ? `昵称已改为 ${a.nick}` : "已清除昵称" });
    }
    if (m.t === "auth") {
      const tok = String(this.env.CHAT_ADMIN_TOKEN || "");
      a.admin = tok.length >= 16 && String(m.token || "") === tok;
      ws.serializeAttachment(a);
      return this.send(ws, { t: "sys", text: a.admin ? "管理员模式已开启" : "口令不对", admin: a.admin });
    }
    if ((m.t === "del" || m.t === "ban") && a.admin) {
      const id = parseInt(m.id, 10);
      const row = this.ctx.storage.sql.exec("SELECT anon, ip FROM msg WHERE id = ?", id).toArray()[0];
      if (!row) return this.send(ws, { t: "sys", text: "找不到这条消息" });
      if (m.t === "del") {
        this.ctx.storage.sql.exec("DELETE FROM msg WHERE id = ?", id);
        return this.broadcast({ t: "del", ids: [id] });
      }
      // 封禁：暂停该 IP 7 天，并删除他最近的全部消息
      await this.env.FORMALIA_KV.put(`ban:${row.ip}`, `chat ${new Date().toISOString()}`, { expirationTtl: 7 * 24 * 3600 });
      const ids = this.ctx.storage.sql.exec("SELECT id FROM msg WHERE anon = ?", row.anon).toArray().map(r => r.id);
      this.ctx.storage.sql.exec("DELETE FROM msg WHERE anon = ?", row.anon);
      this.broadcast({ t: "del", ids });
      for (const s of this.ctx.getWebSockets(row.anon)) { this.send(s, { t: "sys", text: "你已被暂停发言 7 天" }); try { s.close(4003, "banned"); } catch { } }
      return this.send(ws, { t: "sys", text: `已封禁 ${row.anon} 7 天，删除 ${ids.length} 条消息` });
    }
    if (m.t !== "msg") return;
    let text = cleanChatText(m.text, CHAT_MAX_LEN);
    if (!text) return;
    let me = false;   // 先解析命令：不会发出消息的命令不占发言次数
    if (text.startsWith("/me ")) { me = true; text = text.slice(4).trim(); if (!text) return; }
    else if (text.startsWith("/")) return this.send(ws, { t: "sys", text: "可用命令：/nick 昵称、/me 动作" });
    const now = Date.now();
    a.times = (a.times || []).filter(t => now - t < 60000);
    if (a.times.length && now - a.times[a.times.length - 1] < CHAT_MIN_GAP_MS) return this.send(ws, { t: "err", text: "说得太快了，歇两秒" });
    if (a.times.length >= CHAT_PER_MIN) return this.send(ws, { t: "err", text: "一分钟内说太多了，休息一下" });
    a.times.push(now); ws.serializeAttachment(a);
    const cur = this.ctx.storage.sql.exec("INSERT INTO msg (ts, anon, nick, text, me, ip) VALUES (?, ?, ?, ?, ?, ?) RETURNING id",
      now, a.anon, a.nick || "", text, me ? 1 : 0, a.ip || "");
    const id = cur.one().id;
    this.broadcast({ t: "msg", id, ts: now, anon: a.anon, nick: a.nick || "", text, me });
  }

  async webSocketClose(ws) { try { ws.close(); } catch { } this.broadcast({ t: "online", n: Math.max(0, this.online() - 1) }); }
  async webSocketError(ws) { this.broadcast({ t: "online", n: Math.max(0, this.online() - 1) }); }
}
