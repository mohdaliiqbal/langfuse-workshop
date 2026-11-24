const SESSION_STORAGE_KEY = "dad-it-support-session";

const SUGGESTIONS = [
  "How do I turn Bluetooth on?",
  "How do I send a photo on WhatsApp?",
  "Why does my Wi-Fi keep dropping?",
  "How do I free up storage on my phone?",
];

const PHONE = {
  ownerName: "Dad",
  ownerSub: "Signed in · iPhone 15",
  model: "iPhone 15",
  finish: "Black, 128 GB",
  os: "iOS 18.5",
  purchased: "Sep 2023",
};

const GREETING =
  "Hi Dad. I'm here for whatever's bothering your iPhone: Wi-Fi, Bluetooth, photos, messages, maps, you name it.\n\nAsk me **one** thing at a time and I'll walk you through it, step by step.";

function createSessionId() {
  const existing = window.localStorage.getItem(SESSION_STORAGE_KEY);
  if (existing) return existing;
  const next = crypto.randomUUID();
  window.localStorage.setItem(SESSION_STORAGE_KEY, next);
  return next;
}

function createMessage(role, content) {
  return {
    id: crypto.randomUUID(),
    role,
    content,
    timestamp: new Date().toISOString(),
  };
}

function escapeHtml(value) {
  return value
    .replaceAll("&", "&amp;")
    .replaceAll("<", "&lt;")
    .replaceAll(">", "&gt;")
    .replaceAll('"', "&quot;");
}

function renderMarkdown(value) {
  const escaped = escapeHtml(value);
  const withBold = escaped.replace(/\*\*(.+?)\*\*/g, "<strong>$1</strong>");
  return withBold
    .split(/\n{2,}/)
    .map((paragraph) => `<p>${paragraph.replaceAll("\n", "<br />")}</p>`)
    .join("");
}

function mascotSvg(thinking) {
  return `
    <svg class="mascot ${thinking ? "thinking" : ""}" viewBox="0 0 80 92" width="40" height="46" xmlns="http://www.w3.org/2000/svg">
      <line x1="40" y1="22" x2="40" y2="12" stroke="var(--text-primary)" stroke-width="1.6" stroke-linecap="round" />
      <circle class="antenna-tip" cx="40" cy="10" r="3.4" fill="var(--surface-cta-primary)" stroke="var(--text-primary)" stroke-width="1.2" />
      <rect x="11" y="22" width="58" height="46" rx="2" fill="var(--surface-bg)" stroke="var(--text-primary)" stroke-width="1.6" />
      <path class="mascot-bracket" d="M14 28 L14 25 L17 25" />
      <path class="mascot-bracket" d="M66 28 L66 25 L63 25" />
      <path class="mascot-bracket" d="M14 62 L14 65 L17 65" />
      <path class="mascot-bracket" d="M66 62 L66 65 L63 65" />
      <circle class="eye left" cx="29" cy="42" r="3.6" fill="var(--text-primary)" />
      <circle class="eye right" cx="51" cy="42" r="3.6" fill="var(--text-primary)" />
      <path class="mouth" d="M32 55 Q40 60 48 55" stroke="var(--text-primary)" stroke-width="1.6" fill="none" stroke-linecap="round" />
      <rect x="22" y="70" width="36" height="8" rx="1.5" fill="var(--surface-1)" stroke="var(--text-primary)" stroke-width="1.4" />
    </svg>`;
}

function agentAvatar() {
  return `
    <svg viewBox="0 0 24 24" width="14" height="14" fill="none">
      <rect x="5" y="7" width="14" height="11" rx="1" stroke="currentColor" stroke-width="1.4" />
      <line x1="12" y1="4" x2="12" y2="7" stroke="currentColor" stroke-width="1.4" stroke-linecap="round" />
      <circle cx="12" cy="3" r="1" fill="currentColor" />
      <circle cx="9.5" cy="12" r="1.2" fill="currentColor" />
      <circle cx="14.5" cy="12" r="1.2" fill="currentColor" />
    </svg>`;
}

const state = {
  sessionId: "",
  messages: [createMessage("assistant", GREETING)],
  draft: "",
  isSending: false,
  suggestions: SUGGESTIONS,
  model: "gpt-5.5-2026-04-23",
};

function shell() {
  return `
    <div class="app">
      <header class="topbar">
        <img class="wordart" src="/static/assets/langfuse-wordart.svg" alt="Langfuse" />
        <div class="divider"></div>
        <div class="title-row">
          <span class="eyebrow">// support workspace</span>
          <span class="title"><span class="mark">Dad</span> IT Support Agent</span>
        </div>
        <span class="spacer"></span>
        <span class="status"><span class="dot"></span> live · ${escapeHtml(state.model)}</span>
      </header>
      <div class="main">
        <section class="chat">
          <header class="chat-header compact">
            <div class="mascot-wrap">${mascotSvg(state.isSending)}</div>
            <div class="who"><h2>Hi Dad, I'm <span class="mark">Specs</span>.</h2></div>
          </header>
          <div class="chat-stream" id="stream">
            <div class="chat-stream-inner">
              ${state.messages
                .map(
                  (message) => `
                <div class="msg ${message.role === "user" ? "user" : "agent"}">
                  <div class="avatar">${message.role === "user" ? "YOU" : agentAvatar()}</div>
                  <div>
                    <div class="bubble">${
                      message.role === "assistant"
                        ? renderMarkdown(message.content)
                        : `<p>${escapeHtml(message.content)}</p>`
                    }</div>
                    <div class="meta">${message.role === "user" ? "you · just now" : "specs · just now"}</div>
                  </div>
                </div>`
                )
                .join("")}
              ${
                state.isSending
                  ? `<div class="msg agent"><div class="avatar">${agentAvatar()}</div><div><div class="bubble"><div class="typing"><span></span><span></span><span></span></div></div><div class="meta">specs · checking…</div></div></div>`
                  : ""
              }
            </div>
          </div>
          ${
            state.messages.length === 1 && !state.isSending
              ? `<div class="suggestions">${state.suggestions
                  .map(
                    (suggestion) =>
                      `<button class="suggestion" type="button" data-suggestion="${escapeHtml(suggestion)}">${escapeHtml(suggestion)}<span class="arr">↵</span></button>`
                  )
                  .join("")}</div>`
              : ""
          }
          <form class="composer" id="composer">
            <div class="composer-inner">
              <div class="composer-box">
                <textarea id="draft" placeholder="What's going on with your phone?" rows="1">${escapeHtml(state.draft)}</textarea>
                <div class="composer-row">
                  <span class="hint"><kbd>↵</kbd> send · <kbd>⇧</kbd>+<kbd>↵</kbd> newline</span>
                  <span class="spacer"></span>
                  <button class="send-btn" type="submit" ${state.isSending || !state.draft.trim() ? "disabled" : ""}>Send <span class="kbd">↵</span></button>
                </div>
              </div>
            </div>
          </form>
        </section>
        <aside class="side">
          <p class="side-eyebrow">// You</p>
          <div class="lf-corners who-card">
            <div class="row">
              <div class="portrait">D</div>
              <div>
                <h3>${PHONE.ownerName}</h3>
                <div class="who-sub">${PHONE.ownerSub}</div>
              </div>
            </div>
          </div>
          <p class="side-eyebrow">// Your phone</p>
          <div class="lf-corners phone-card">
            <div class="phone-hero">
              <div class="phone-illu"><div class="screen"></div></div>
              <div class="phone-meta">
                <div class="model">${PHONE.model}</div>
                <div class="os">${PHONE.os}</div>
                <div class="age">${PHONE.finish} · bought ${PHONE.purchased}</div>
              </div>
            </div>
          </div>
        </aside>
      </div>
    </div>`;
}

function render() {
  const root = document.getElementById("root");
  const draft = document.getElementById("draft");
  const selectionStart = draft ? draft.selectionStart : null;
  root.innerHTML = shell();
  const stream = document.getElementById("stream");
  if (stream) stream.scrollTop = stream.scrollHeight;
  const nextDraft = document.getElementById("draft");
  if (nextDraft) {
    nextDraft.focus();
    if (selectionStart !== null) nextDraft.setSelectionRange(selectionStart, selectionStart);
    nextDraft.addEventListener("input", () => {
      state.draft = nextDraft.value;
      const button = document.querySelector(".send-btn");
      if (button) button.disabled = state.isSending || !state.draft.trim();
    });
    nextDraft.addEventListener("keydown", (event) => {
      if (event.key === "Enter" && !event.shiftKey) {
        event.preventDefault();
        void send();
      }
    });
  }
  document.getElementById("composer").addEventListener("submit", (event) => {
    event.preventDefault();
    void send();
  });
  document.querySelectorAll("[data-suggestion]").forEach((button) => {
    button.addEventListener("click", () => void send(button.dataset.suggestion));
  });
}

async function send(textOverride) {
  const text = (textOverride ?? state.draft).trim();
  if (!text || !state.sessionId || state.isSending) return;
  const nextMessages = [...state.messages, createMessage("user", text)];
  state.messages = nextMessages;
  state.draft = "";
  state.isSending = true;
  render();
  try {
    const response = await fetch("/api/chat", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ messages: nextMessages, sessionId: state.sessionId }),
    });
    if (!response.ok) {
      const errText = await response.text();
      throw new Error(errText || "Chat request failed.");
    }
    const result = await response.json();
    state.messages = [...state.messages, createMessage("assistant", result.answer)];
  } catch (error) {
    const fallback = error instanceof Error ? error.message : "The chat request failed.";
    state.messages = [
      ...state.messages,
      createMessage("assistant", `I hit a snag while answering that question.\n\n${fallback}`),
    ];
  } finally {
    state.isSending = false;
    render();
  }
}

async function boot() {
  state.sessionId = createSessionId();
  render();
  try {
    const [health, context] = await Promise.all([
      fetch("/api/health").then((response) => (response.ok ? response.json() : null)),
      fetch("/api/support-context").then((response) => (response.ok ? response.json() : null)),
    ]);
    if (health && health.model) state.model = health.model;
    if (context && Array.isArray(context.starterQuestions) && context.starterQuestions.length) {
      state.suggestions = context.starterQuestions;
    }
    render();
  } catch {
    /* The panel falls back to the hardcoded copy. */
  }
}

void boot();
