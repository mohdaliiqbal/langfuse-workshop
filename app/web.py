"""
Web entry point for the DataStream Support Assistant.

Run with hot reload (reloads on every Python file change):
    uv run gradio app/web.py

The 👍/👎 buttons on assistant messages are dormant until Lab 4 — once
answer() returns a trace_id they start recording user-feedback scores in
Langfuse automatically, with no changes needed to this file.
"""

import sys
import os
# Ensure repo root is on sys.path so `from app.assistant import answer` resolves
# correctly when Gradio runs this file (Gradio adds app/ to sys.path, not the root)
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from dotenv import load_dotenv
load_dotenv()

import inspect
import uuid
import gradio as gr


def _call_answer(message: str, history: list, session_id: str) -> tuple[str, str | None, str | None]:
    # Imported here (not at module level) so gradio hot reload picks up changes to assistant.py
    from app.assistant import answer
    sig = inspect.signature(answer)
    kwargs: dict = {"question": message, "history": history or None}
    if "session_id" in sig.parameters:
        kwargs["session_id"] = session_id
    if "user_id" in sig.parameters:
        kwargs["user_id"] = "workshop-user-1"
    result = answer(**kwargs)
    if isinstance(result, tuple):
        trace_id = result[1] if len(result) > 1 else None
        observation_id = result[2] if len(result) > 2 else None
        return result[0], trace_id, observation_id
    return result, None, None


def _submit(message: str, history: list, state: dict):
    if state is None:
        state = _init_state()
    try:
        response, trace_id, observation_id = _call_answer(message, history, state["session_id"])
    except Exception as e:
        # Show the real error in the chat so attendees don't have to hunt the terminal
        import traceback
        traceback.print_exc()
        error_msg = f"**Error**: {e}\n\nCheck the terminal for the full traceback."
        history = history + [
            {"role": "user", "content": message},
            {"role": "assistant", "content": error_msg},
        ]
        return "", history, state
    history = history + [
        {"role": "user", "content": message},
        {"role": "assistant", "content": response},
    ]
    # Store trace_id and observation_id per turn so .like() can look them up by message index
    trace_ids = state["trace_ids"] + [trace_id]
    observation_ids = state.get("observation_ids", []) + [observation_id]
    return "", history, {**state, "trace_ids": trace_ids, "observation_ids": observation_ids}


def _handle_like(data: gr.LikeData, state: dict) -> None:
    trace_ids = state.get("trace_ids", [])
    observation_ids = state.get("observation_ids", [])
    # data.index is the position in history; assistant messages are at every other slot
    idx = data.index if isinstance(data.index, int) else data.index[0]
    turn = idx // 2
    trace_id = trace_ids[turn] if turn < len(trace_ids) else None
    if not trace_id:
        return  # answer() doesn't return trace_id yet (Labs 0–3) — no-op
    observation_id = observation_ids[turn] if turn < len(observation_ids) else None
    from langfuse import get_client
    get_client().create_score(
        trace_id=trace_id,
        observation_id=observation_id,  # pins the score to the specific observation, not just the trace
        name="user-feedback",
        value=1 if data.liked else 0,
        data_type="BOOLEAN",
        comment="User thumbs up/down from web UI",
    )


def _init_state():
    # Called once per browser session via demo.load() — gives each tab its own session_id
    return {"session_id": uuid.uuid4().hex, "trace_ids": [], "observation_ids": []}


# Langfuse brand: yellow #FCFF74 on near-black, Inter typeface.
# Mirrors langfuse.com / clickhouse.design without claiming to be production-official.
LANGFUSE_YELLOW = "#FCFF74"
LANGFUSE_INK = "#0B0E13"

langfuse_theme = gr.themes.Soft(
    primary_hue=gr.themes.Color(
        c50="#FFFEE0", c100="#FFFDB3", c200="#FEFB85", c300="#FEF858",
        c400="#FDF52B", c500=LANGFUSE_YELLOW, c600="#CAD400", c700="#979F00",
        c800="#646B00", c900="#323600", c950="#1A1C00",
    ),
    neutral_hue="slate",
    font=[gr.themes.GoogleFont("Inter"), "ui-sans-serif", "system-ui", "sans-serif"],
    font_mono=[gr.themes.GoogleFont("JetBrains Mono"), "ui-monospace", "monospace"],
).set(
    # Light surfaces
    body_background_fill="#FAFAFA",
    body_text_color=LANGFUSE_INK,
    body_text_color_subdued="#6B7280",
    background_fill_primary="#FFFFFF",
    background_fill_secondary="#F3F4F6",
    block_background_fill="#FFFFFF",
    block_border_color="#E5E7EB",
    border_color_primary="#E5E7EB",
    input_background_fill="#FFFFFF",
    # Primary action: dark pill with yellow text (Langfuse style)
    button_primary_background_fill=LANGFUSE_INK,
    button_primary_background_fill_hover="#1F242D",
    button_primary_text_color=LANGFUSE_YELLOW,
    button_primary_border_color=LANGFUSE_INK,
    block_radius="*radius_lg",
    block_border_width="1px",
    # Mirror the same palette for dark-mode users so we never flip surfaces.
    # Langfuse marketing is a light brand — keep the workshop on-brand.
    body_background_fill_dark="#FAFAFA",
    body_text_color_dark=LANGFUSE_INK,
    body_text_color_subdued_dark="#6B7280",
    background_fill_primary_dark="#FFFFFF",
    background_fill_secondary_dark="#F3F4F6",
    block_background_fill_dark="#FFFFFF",
    block_border_color_dark="#E5E7EB",
    border_color_primary_dark="#E5E7EB",
    input_background_fill_dark="#FFFFFF",
    button_primary_background_fill_dark=LANGFUSE_INK,
    button_primary_background_fill_hover_dark="#1F242D",
    button_primary_text_color_dark=LANGFUSE_YELLOW,
    button_primary_border_color_dark=LANGFUSE_INK,
)

CUSTOM_CSS = """
/* Force on-brand light surface regardless of OS dark-mode preference. */
.gradio-container, .gradio-container.dark, .dark .gradio-container {
    background: #FAFAFA !important;
    color: #0B0E13 !important;
    color-scheme: light !important;
}
.dark { color-scheme: light !important; }
.gradio-container { max-width: 920px !important; margin: 0 auto !important; }

/* Hide Gradio's default footer — we ship our own branded one. */
footer, .gradio-container > footer, .built-with, .show-api { display: none !important; }

/* Hide Gradio's per-message action buttons we don't want.
   Keep copy + like/dislike; drop delete, share, retry, edit, and any select-all toggles. */
.gradio-container button[aria-label*="Delete" i],
.gradio-container button[aria-label*="Remove" i],
.gradio-container button[aria-label*="Share" i],
.gradio-container button[aria-label*="Retry" i],
.gradio-container button[aria-label*="Regenerate" i],
.gradio-container button[aria-label*="Edit" i],
.gradio-container button[title*="Delete" i],
.gradio-container button[title*="Share" i],
.gradio-container button[title*="Retry" i] { display: none !important; }
/* Gradio sometimes renders a select-all checkbox above the chat — hide it. */
.gradio-container .message-buttons-row input[type="checkbox"],
.gradio-container .chatbot input[type="checkbox"] { display: none !important; }

/* The per-message copy button ships with a near-invisible light-grey icon.
   Force a readable ink tone on the SVG and a clear hover state. */
.gradio-container button[aria-label*="Copy" i],
.gradio-container button[title*="Copy" i] {
    color: #374151 !important;
    opacity: 1 !important;
}
.gradio-container button[aria-label*="Copy" i] svg,
.gradio-container button[title*="Copy" i] svg {
    color: #374151 !important;
    stroke: #374151 !important;
    fill: none !important;
    opacity: 1 !important;
}
.gradio-container button[aria-label*="Copy" i]:hover,
.gradio-container button[title*="Copy" i]:hover {
    background: #FCFF74 !important;
    border-radius: 6px !important;
}
.gradio-container button[aria-label*="Copy" i]:hover svg,
.gradio-container button[title*="Copy" i]:hover svg {
    color: #0B0E13 !important;
    stroke: #0B0E13 !important;
}

/* Chat bubbles — on-brand colors with strong text contrast.
   Selectors are broad on purpose to cover Gradio bubble-layout class variants. */
/* Row wrappers stay transparent so only the inner .message renders as the bubble. */
.gradio-container .message-row,
.gradio-container .message-row.user,
.gradio-container .message-row.bot,
.gradio-container .user-row,
.gradio-container .bot-row,
.gradio-container [data-testid="user"],
.gradio-container [data-testid="bot"] {
    background: transparent !important;
    background-color: transparent !important;
    border: none !important;
    box-shadow: none !important;
}

.gradio-container .message-row.user .message,
.gradio-container .message-row[data-role="user"] .message,
.gradio-container .user-row .message,
.gradio-container .message.user {
    background: #FCFF74 !important;
    color: #0B0E13 !important;
    border: 1px solid #FEF458 !important;
}
.gradio-container .message-row.user .message *,
.gradio-container .message-row[data-role="user"] .message *,
.gradio-container .user-row .message *,
.gradio-container .message.user * {
    color: #0B0E13 !important;
}
.gradio-container .message-row.bot .message,
.gradio-container .message-row[data-role="assistant"] .message,
.gradio-container .bot-row .message,
.gradio-container .message.bot {
    background: #FFFFFF !important;
    color: #0B0E13 !important;
    border: 1px solid #E5E7EB !important;
}
.lf-examples-label {
    font-size: 11px; font-weight: 600; letter-spacing: 0.10em;
    color: #6B7280; text-transform: uppercase;
    margin: 10px 4px 6px 4px;
}
.lf-examples-row { gap: 8px !important; flex-wrap: wrap; }
.lf-example-btn,
.lf-example-btn button,
button.lf-example-btn {
    background: #FFFFFF !important;
    color: #0B0E13 !important;
    border: 1.5px solid #0B0E13 !important;
    font-size: 13px !important;
    padding: 7px 14px !important;
    border-radius: 999px !important;
    font-weight: 600 !important;
    box-shadow: 0 1px 0 rgba(11,14,19,0.04) !important;
    transition: background 0.12s ease, transform 0.06s ease !important;
}
.lf-example-btn:hover,
.lf-example-btn button:hover,
button.lf-example-btn:hover {
    background: #FCFF74 !important;
    border-color: #0B0E13 !important;
    transform: translateY(-1px);
}

.gradio-container .message-row.bot .message *,
.gradio-container .message-row[data-role="assistant"] .message *,
.gradio-container .bot-row .message *,
.gradio-container .message.bot * {
    color: #0B0E13 !important;
}

/* Flatten the nested panel Gradio renders inside each chat bubble.
   DOM is: .bot.message  (the bubble we style)
             └─ .message.panel-full-width  (Gradio's own panel — has its own border/bg)
                  └─ [data-testid="bot"]
                       └─ .message-content
   We keep the outer bubble styling and make every wrapper inside transparent. */
.gradio-container .bot.message .message,
.gradio-container .user.message .message,
.gradio-container .message .panel-full-width,
.gradio-container .panel-full-width,
.gradio-container .message [data-testid="bot"],
.gradio-container .message [data-testid="user"],
.gradio-container .message .message-content,
.gradio-container .message .md,
.gradio-container .message .prose {
    background: transparent !important;
    background-color: transparent !important;
    border: 0 !important;
    border-width: 0 !important;
    box-shadow: none !important;
}

/* Also strip borders from generic content tags inside a bubble (paragraphs, lists, etc). */
.gradio-container .message :where(p, span, ul, ol, li, h1, h2, h3, h4, h5, h6) {
    background: transparent !important;
    border: none !important;
    box-shadow: none !important;
}
/* Same nuke applied from the message-row level, in case the inner panel is a sibling of .message rather than a child. */
.gradio-container .message-row :where(.message-content, .message-body, .bubble-content, .chat-bubble-inner, .markdown-body) {
    background: transparent !important;
    background-color: transparent !important;
    border: none !important;
    box-shadow: none !important;
}

.lf-header {
    display: flex; align-items: center; gap: 14px;
    padding: 22px 4px 18px 4px;
    border-bottom: 1px solid #E5E7EB;
    margin-bottom: 18px;
}
.lf-logo {
    background: #0B0E13; color: #FCFF74;
    font-weight: 700; font-size: 16px;
    padding: 8px 14px; border-radius: 10px;
    letter-spacing: -0.02em; white-space: nowrap;
    font-family: Inter, ui-sans-serif, system-ui, sans-serif;
}
.lf-logo .lf-by { color: #FAFAFA; font-weight: 500; opacity: 0.75; }
.lf-title-block { display: flex; flex-direction: column; line-height: 1.2; }
.lf-eyebrow {
    font-size: 11px; font-weight: 600; letter-spacing: 0.12em;
    color: #6B7280; text-transform: uppercase;
}
.lf-title {
    font-size: 22px; font-weight: 700; color: #0B0E13;
    letter-spacing: -0.02em; margin-top: 2px;
}
.lf-tagline {
    font-size: 14px; color: #4B5563; margin: 0 4px 14px 4px;
}
.lf-tagline .lf-pill {
    display: inline-block; background: #FCFF74; color: #0B0E13;
    padding: 2px 8px; border-radius: 999px; font-size: 11px;
    font-weight: 600; margin-right: 6px; letter-spacing: 0.02em;
}
.lf-footer {
    font-size: 12px; color: #9CA3AF; text-align: center;
    padding: 18px 0 6px 0; border-top: 1px solid #E5E7EB; margin-top: 22px;
}
.lf-footer a { color: #0B0E13; text-decoration: none; border-bottom: 1px solid #FCFF74; }
"""

HEADER_HTML = """
<div class="lf-header">
  <div class="lf-logo">Langfuse <span class="lf-by">by ClickHouse</span></div>
  <div class="lf-title-block">
    <span class="lf-eyebrow">Workshop</span>
    <span class="lf-title">DataStream Support Assistant</span>
  </div>
</div>
<div class="lf-tagline">
  <span class="lf-pill">Demo</span>
  Ask about DataStream features, pricing, troubleshooting, and best practices — every turn is traced in Langfuse.
</div>
"""

FOOTER_HTML = """
<div class="lf-footer">
  Built for the <a href="https://langfuse.com" target="_blank" rel="noreferrer">Langfuse</a> workshop ·
  the open-source LLM engineering platform, now part of ClickHouse.
</div>
"""

EXAMPLE_QUESTIONS = [
    "How is DataStream priced?",
    "Which databases does DataStream connect to?",
    "My pipeline is lagging — where do I start debugging?",
    "What's the recommended way to handle schema changes?",
]

# Detect whether the current lab has wired feedback (answer() returns a trace_id).
# Labs 0–3: `def answer(...) -> str` → no feedback buttons (they'd be dormant).
# Lab 4+:   answer() returns a tuple including trace_id → enable 👍/👎.
# Inspect via AST so we don't execute assistant.py (which imports OpenAI at module load).
def _feedback_enabled() -> bool:
    import ast
    try:
        path = os.path.join(os.path.dirname(__file__), "assistant.py")
        with open(path) as f:
            tree = ast.parse(f.read())
        for node in ast.walk(tree):
            if isinstance(node, ast.FunctionDef) and node.name == "answer":
                ret = node.returns
                if ret is None:
                    return False
                if isinstance(ret, ast.Name) and ret.id == "str":
                    return False
                # Anything else (Tuple, subscript, etc.) implies a richer return → enable
                return True
    except Exception:
        pass
    return False

FEEDBACK_ENABLED = _feedback_enabled()

with gr.Blocks(title="Langfuse by ClickHouse — DataStream Support", theme=langfuse_theme, css=CUSTOM_CSS) as demo:
    state = gr.State(None)

    gr.HTML(HEADER_HTML)

    chatbot = gr.Chatbot(
        height=520,
        layout="bubble",
        show_label=False,
        avatar_images=(None, "https://langfuse.com/icon.svg"),
        buttons=["copy"],   # drops share + copy_all; keep only copy
        editable=None,      # no edit / no delete
        feedback_options=("Like", "Dislike") if FEEDBACK_ENABLED else None,
    )
    msg = gr.Textbox(
        placeholder="Ask about DataStream…",
        show_label=False,
        submit_btn=True,
        autofocus=True,
    )
    gr.HTML('<div class="lf-examples-label">Try one of these</div>')
    with gr.Row(elem_classes="lf-examples-row"):
        for _q in EXAMPLE_QUESTIONS:
            _btn = gr.Button(_q, size="sm", variant="secondary", elem_classes="lf-example-btn")
            _btn.click(lambda q=_q: q, outputs=msg)

    gr.HTML(FOOTER_HTML)

    demo.load(_init_state, outputs=[state])
    msg.submit(_submit, inputs=[msg, chatbot, state], outputs=[msg, chatbot, state])
    if FEEDBACK_ENABLED:
        chatbot.like(_handle_like, inputs=[state], outputs=[])


if __name__ == "__main__":
    demo.launch(theme=langfuse_theme, css=CUSTOM_CSS)
