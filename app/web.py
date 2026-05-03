"""
Web entry point for the DataStream Support Assistant.

Run with hot reload (reloads on every Python file change):
    uv run gradio app/web.py

The 👍/👎 buttons on assistant messages are dormant until Lab 5 — once
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


def _call_answer(message: str, history: list, session_id: str) -> tuple[str, str | None]:
    # Imported here (not at module level) so gradio hot reload picks up changes to assistant.py
    from app.assistant import answer
    sig = inspect.signature(answer)
    kwargs: dict = {"question": message, "history": history or None}
    if "session_id" in sig.parameters:
        kwargs["session_id"] = session_id
    if "user_id" in sig.parameters:
        kwargs["user_id"] = "workshop-user-1"
    result = answer(**kwargs)
    return (result[0], result[1]) if isinstance(result, tuple) else (result, None)


def _submit(message: str, history: list, state: dict):
    try:
        response, trace_id = _call_answer(message, history, state["session_id"])
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
    # Store trace_id per turn so .like() can look it up by message index
    trace_ids = state["trace_ids"] + [trace_id]
    return "", history, {**state, "trace_ids": trace_ids}


def _handle_like(data: gr.LikeData, state: dict) -> None:
    trace_ids = state.get("trace_ids", [])
    # data.index is the position in history; assistant messages are at every other slot
    idx = data.index if isinstance(data.index, int) else data.index[0]
    turn = idx // 2
    trace_id = trace_ids[turn] if turn < len(trace_ids) else None
    if not trace_id:
        return  # answer() doesn't return trace_id yet (Labs 0–4) — no-op
    from langfuse import get_client
    get_client().create_score(
        trace_id=trace_id,
        name="user-feedback",
        value=1 if data.liked else 0,
        data_type="BOOLEAN",
        comment="User thumbs up/down from web UI",
    )


with gr.Blocks(title="DataStream Support") as demo:
    # gr.State with a factory function creates a fresh state per browser session,
    # so each tab (and each hot reload) gets its own session_id
    state = gr.State(lambda: {"session_id": uuid.uuid4().hex, "trace_ids": []})

    gr.Markdown("## DataStream Support Assistant")
    gr.Markdown("Ask me anything about DataStream — features, pricing, troubleshooting, and best practices.")

    chatbot = gr.Chatbot(height=500, layout="bubble")
    msg = gr.Textbox(placeholder="Type your question...", show_label=False, submit_btn=True)

    msg.submit(_submit, inputs=[msg, chatbot, state], outputs=[msg, chatbot, state])
    chatbot.like(_handle_like, inputs=[state], outputs=[])


if __name__ == "__main__":
    demo.launch()
