// Formalia 灌水区：IRC 风格的即时聊天。连接 /api/chat（WebSocket）。代码许可：Apache-2.0。
(function () {
  "use strict";
  const $ = (s) => document.querySelector(s);
  const log = $("#chat-log"), input = $("#chat-input"), status = $("#chat-status"), form = $("#chat-form");
  let ws, anon = "", admin = false, retry = 0, ping, everConnected = false;
  const sent = []; let hist = -1;

  // 管理员口令：打开 /chat/#admin=口令 一次即可，存进本机，随即从地址栏抹掉
  try {
    const m = location.hash.match(/admin=([^&]+)/);
    if (m) { localStorage.setItem("formalia-chat-admin", decodeURIComponent(m[1])); history.replaceState(null, "", location.pathname); }
  } catch { }
  const adminToken = (() => { try { return localStorage.getItem("formalia-chat-admin") || ""; } catch { return ""; } })();
  const savedNick = (() => { try { return localStorage.getItem("formalia-chat-nick") || ""; } catch { return ""; } })();

  const hue = (s) => { let h = 0; for (const c of s) h = (h * 31 + c.charCodeAt(0)) % 360; return h; };
  const hhmm = (ts) => { const d = new Date(ts); return String(d.getHours()).padStart(2, "0") + ":" + String(d.getMinutes()).padStart(2, "0"); };
  const atBottom = () => log.scrollHeight - log.scrollTop - log.clientHeight < 40;

  function line(cls, parts, id) {
    const keep = atBottom();
    const div = document.createElement("div");
    div.className = "ln " + cls; if (id) div.dataset.id = id;
    for (const p of parts) div.append(p);
    log.append(div);
    while (log.children.length > 600) log.firstChild.remove();
    if (keep) log.scrollTop = log.scrollHeight;
    return div;
  }
  const span = (cls, text) => { const s = document.createElement("span"); s.className = cls; s.textContent = text; return s; };
  function who(m) {
    const s = span("nick", (m.nick ? m.nick : "匿名") + "·" + m.anon.slice(0, 4));
    s.style.color = `hsl(${hue(m.anon)} 55% var(--nick-l))`; s.title = "匿名编号 " + m.anon; return s;
  }
  function msg(m) {
    const parts = [span("ts", hhmm(m.ts) + " ")];
    if (m.me) parts.push(span("star", "* "), who(m), document.createTextNode(" " + m.text));
    else parts.push(span("lt", "<"), who(m), span("lt", "> "), document.createTextNode(m.text));
    if (admin) {
      const del = document.createElement("button"); del.className = "adm"; del.textContent = "删";
      del.onclick = () => ws.send(JSON.stringify({ t: "del", id: m.id }));
      const ban = document.createElement("button"); ban.className = "adm"; ban.textContent = "封";
      ban.onclick = () => { if (confirm("封禁这位发言者 7 天，并删除他的全部消息？")) ws.send(JSON.stringify({ t: "ban", id: m.id })); };
      parts.push(" ", del, ban);
    }
    line(m.anon === anon ? "mine" : "", parts, m.id);
  }
  const sys = (text, cls = "sys") => line(cls, [span("ts", hhmm(Date.now()) + " "), span("star", "-!- "), document.createTextNode(text)]);

  function connect() {
    status.textContent = "连接中……";
    const proto = location.protocol === "https:" ? "wss:" : "ws:";
    ws = new WebSocket(`${proto}//${location.host}/api/chat`);
    ws.onopen = () => {
      retry = 0; everConnected = true;
      if (savedNick) ws.send(JSON.stringify({ t: "nick", nick: savedNick }));
      if (adminToken) ws.send(JSON.stringify({ t: "auth", token: adminToken }));
      clearInterval(ping); ping = setInterval(() => { try { ws.send('{"t":"ping"}'); } catch { } }, 30000);
    };
    ws.onmessage = (e) => {
      let m; try { m = JSON.parse(e.data); } catch { return; }
      if (m.t === "hello") {
        anon = m.anon; log.replaceChildren();
        sys(`欢迎来到灌水区。你的匿名编号是 ${m.anon}。消息保留 ${m.keep_days} 天。输入 /nick 昵称 改名，/me 动作 表示动作。`);
        for (const h of m.history) msg(h);
        status.textContent = `在线 ${m.online} 人`;
      } else if (m.t === "msg") msg(m);
      else if (m.t === "online") status.textContent = `在线 ${m.n} 人`;
      else if (m.t === "del") for (const id of m.ids) log.querySelector(`[data-id="${id}"]`)?.remove();
      else if (m.t === "sys") { if (m.admin !== undefined) { admin = m.admin; } sys(m.text); }
      else if (m.t === "err") sys(m.text, "err");
    };
    ws.onclose = (e) => {
      clearInterval(ping);
      if (e.code === 4003) { status.textContent = "已被暂停发言"; return; }
      if (!everConnected && retry >= 2) {   // 从没连上过：多半是聊天服务还没部署
        status.textContent = "暂未开通";
        if (!log.querySelector(".sys")) sys("灌水区暂未开通：聊天服务器还没有部署。请稍后再来。");
        return;
      }
      const wait = Math.min(30, 2 ** retry++); status.textContent = `已断开，${wait} 秒后重连`;
      setTimeout(connect, wait * 1000);
    };
  }

  form.addEventListener("submit", (e) => {
    e.preventDefault();
    const text = input.value.trim(); if (!text || !ws || ws.readyState !== 1) return;
    if (text.startsWith("/nick")) {
      const nick = text.slice(5).trim();
      try { localStorage.setItem("formalia-chat-nick", nick); } catch { }
      ws.send(JSON.stringify({ t: "nick", nick }));
    } else ws.send(JSON.stringify({ t: "msg", text }));
    sent.push(text); hist = sent.length; input.value = "";
  });
  input.addEventListener("keydown", (e) => {
    if (e.key === "ArrowUp" && sent.length) { hist = Math.max(0, hist - 1); input.value = sent[hist]; e.preventDefault(); }
    if (e.key === "ArrowDown" && sent.length) { hist = Math.min(sent.length, hist + 1); input.value = sent[hist] || ""; e.preventDefault(); }
  });
  connect();
  input.focus();
})();
