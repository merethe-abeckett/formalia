// 交互式导读：在表述页面上向 Gemini 提问。代码许可：Apache-2.0。
// 浏览器只发送编号和问题；表述代码由 Worker 从本站 /ask/<编号>.json 读取。
(function () {
  const box = document.getElementById("ask");
  if (!box) return;
  const id = box.dataset.id;
  const log = box.querySelector(".log"), input = box.querySelector("textarea"),
        btn = box.querySelector("button"), st = box.querySelector(".st");
  const history = [];   // 最近几轮 {q, a}，让追问有上下文

  const esc = s => s.replace(/[&<>"]/g, c => ({ "&": "&amp;", "<": "&lt;", ">": "&gt;", '"': "&quot;" }[c]));
  // 只渲染 `代码` 和 **加粗**，其余原样显示
  const render = s => esc(s).replace(/`([^`\n]+)`/g, "<code>$1</code>").replace(/\*\*([^*\n]+)\*\*/g, "<b>$1</b>");
  const add = (cls, html) => { const d = document.createElement("div"); d.className = cls; d.innerHTML = html; log.append(d); return d; };

  async function send() {
    const q = input.value.trim();
    if (!q || btn.disabled) return;
    add("q", esc(q));
    input.value = ""; btn.disabled = true; st.textContent = "Gemini 正在回答……";
    try {
      const r = await fetch("/api/ask", { method: "POST", headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ id, question: q, history: history.slice(-3) }) });
      const j = await r.json().catch(() => ({}));
      if (r.ok && j.ok) {
        add("a", render(j.answer));
        history.push({ q, a: j.answer });
        st.textContent = j.model ? `由 ${j.model} 回答` : "";
      } else {
        add("a err", esc(j.error || (r.status === 404 ? "问答功能暂未开通" : `出错了（${r.status}），请稍后再试`)));
        st.textContent = "";
      }
    } catch (e) {
      add("a err", "连不上服务器，请检查网络后再试");
      st.textContent = "";
    }
    btn.disabled = false; input.focus();
  }

  btn.addEventListener("click", send);
  input.addEventListener("keydown", e => {
    if (e.key === "Enter" && !e.shiftKey && !e.isComposing) { e.preventDefault(); send(); }
  });
})();
