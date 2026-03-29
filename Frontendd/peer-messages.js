const API =
    typeof window !== "undefined" && typeof window.SKILLSWAP_API_BASE === "string"
        ? window.SKILLSWAP_API_BASE
        : "http://127.0.0.1:8000";
const TOKEN_KEY = "skillswap_token";

let myUserId = null;
let activeThreadId = null;

function authHeaders() {
  const t = localStorage.getItem(TOKEN_KEY);
  return {
    "Content-Type": "application/json",
    Authorization: `Bearer ${t}`,
  };
}

function showError(msg) {
  const el = document.getElementById("peer-error");
  if (!el) return;
  el.textContent = msg;
  el.hidden = !msg;
}

function escHtml(s) {
  const d = document.createElement("div");
  d.textContent = s == null ? "" : String(s);
  return d.innerHTML;
}

async function fetchMe() {
  const res = await fetch(`${API}/users/me`, { headers: authHeaders() });
  if (!res.ok) return null;
  return res.json();
}

function avatarInitials(t) {
  const a = (t.other_first_name || "").trim().charAt(0) || "?";
  const b = (t.other_last_name || "").trim().charAt(0) || "?";
  return escHtml((a + b).toUpperCase());
}

function setChatTitle(t) {
  const title = document.getElementById("chat-title");
  if (!title) return;
  if (!t) {
    title.innerHTML =
      '<span class="peer-chat-title-placeholder">Sélectionnez une conversation</span>';
    return;
  }
  title.innerHTML = "";
  const a = document.createElement("a");
  a.href = "member.html?id=" + encodeURIComponent(t.other_user_id);
  a.className = "peer-chat-title-handle";
  a.textContent = "@" + (t.other_handle || "user");
  title.appendChild(a);
}

function renderThreads(threads) {
  const box = document.getElementById("thread-list");
  if (!box) return;
  box.innerHTML = "";
  threads.forEach((t) => {
    const div = document.createElement("div");
    div.className =
      "peer-thread-item" + (t.id === activeThreadId ? " active" : "");
    div.dataset.id = t.id;
    div.innerHTML = `<div class="peer-thread-row">
      <div class="peer-thread-avatar" aria-hidden="true">${avatarInitials(t)}</div>
      <div class="peer-thread-name">
        <span class="peer-fn">${escHtml(t.other_first_name || "")}</span>
        <span class="peer-ln">${escHtml(t.other_last_name || "")}</span>
      </div>
    </div>`;
    div.addEventListener("click", () => selectThread(t.id));
    box.appendChild(div);
  });
}

async function loadThreads() {
  showError("");
  const res = await fetch(`${API}/peer-messages/threads`, {
    headers: authHeaders(),
  });
  if (!res.ok) {
    showError("Impossible de charger les conversations.");
    return;
  }
  const data = await res.json();
  renderThreads(data);
}

async function selectThread(threadId) {
  activeThreadId = threadId;
  await loadThreads();
  const threads = await (
    await fetch(`${API}/peer-messages/threads`, { headers: authHeaders() })
  ).json();
  const t = threads.find((x) => x.id === threadId);
  setChatTitle(t || null);

  document.getElementById("msg-input").disabled = false;
  document.getElementById("btn-send").disabled = false;

  const res = await fetch(
    `${API}/peer-messages/threads/${threadId}/messages`,
    { headers: authHeaders() }
  );
  const msgs = res.ok ? await res.json() : [];
  const area = document.getElementById("msg-area");
  area.innerHTML = "";
  msgs.forEach((m) => {
    const bubble = document.createElement("div");
    bubble.className =
      "peer-bubble " + (m.sender_id === myUserId ? "me" : "them");
    bubble.textContent = m.content;
    area.appendChild(bubble);
  });
  area.scrollTop = area.scrollHeight;
}

async function sendMessage() {
  const input = document.getElementById("msg-input");
  const text = (input.value || "").trim();
  if (!text || !activeThreadId) return;
  input.value = "";
  const res = await fetch(
    `${API}/peer-messages/threads/${activeThreadId}/messages`,
    {
      method: "POST",
      headers: authHeaders(),
      body: JSON.stringify({ content: text }),
    }
  );
  if (!res.ok) {
    const d = await res.json().catch(() => ({}));
    showError(d.detail || "Envoi impossible.");
    return;
  }
  showError("");
  await selectThread(activeThreadId);
  await loadThreads();
}

const UUID_RE =
  /^[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12}$/i;
const UUID_COMPACT_RE = /^[0-9a-f]{32}$/i;

function normalizeUuidIfCompact(s) {
  if (!UUID_COMPACT_RE.test(s)) return s;
  const h = s.toLowerCase();
  return `${h.slice(0, 8)}-${h.slice(8, 12)}-${h.slice(12, 16)}-${h.slice(16, 20)}-${h.slice(20, 32)}`;
}

/** Accept dashed UUID, 32-char hex, or public handle (e.g. alicemartin_89d7308f). */
async function resolvePeerToUserId(raw) {
  let s = (raw || "").trim().replace(/^@/, "");
  if (!s) return null;
  s = normalizeUuidIfCompact(s);
  if (UUID_RE.test(s)) return s;

  const handle = s.toLowerCase();
  const res = await fetch(`${API}/users/by-handle/${encodeURIComponent(handle)}`, {
    headers: authHeaders(),
  });
  if (!res.ok) return null;
  const u = await res.json();
  return u.id || null;
}

async function startThread(skillIdFromUrl) {
  const peerRaw = document.getElementById("start-peer-id").value.trim();
  if (!peerRaw) {
    showError("Indiquez l’ID ou le pseudo du membre.");
    return;
  }
  const peer = await resolvePeerToUserId(peerRaw);
  if (!peer) {
    showError("Membre introuvable — vérifiez l’ID (avec tirets) ou le pseudo exact du profil.");
    return;
  }
  const body = { other_user_id: peer };
  const sid =
    skillIdFromUrl != null && String(skillIdFromUrl).trim()
      ? String(skillIdFromUrl).trim()
      : "";
  if (sid) body.skill_id = sid;

  const res = await fetch(`${API}/peer-messages/threads`, {
    method: "POST",
    headers: authHeaders(),
    body: JSON.stringify(body),
  });
  const data = await res.json().catch(() => ({}));
  if (!res.ok) {
    showError(
      typeof data.detail === "string"
        ? data.detail
        : "Impossible d’ouvrir la discussion."
    );
    return;
  }
  showError("");
  document.getElementById("start-peer-id").value = "";
  await loadThreads();
  await selectThread(data.id);
}

document.addEventListener("DOMContentLoaded", async () => {
  if (!localStorage.getItem(TOKEN_KEY)) {
    window.location.href = "login.html";
    return;
  }
  const me = await fetchMe();
  if (!me) {
    window.location.href = "login.html";
    return;
  }
  myUserId = me.id;

  const params = new URLSearchParams(window.location.search);
  const peer = params.get("peer");
  const skill = params.get("skill");
  if (peer) {
    document.getElementById("start-peer-id").value = peer;
    await startThread(skill || undefined);
  } else {
    await loadThreads();
  }

  document
    .getElementById("btn-start-chat")
    .addEventListener("click", () => startThread(undefined));
  document.getElementById("btn-send").addEventListener("click", sendMessage);
  document.getElementById("msg-input").addEventListener("keydown", (e) => {
    if (e.key === "Enter") sendMessage();
  });
});
