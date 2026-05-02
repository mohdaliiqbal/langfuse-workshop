"""
Web entry point for the DataStream Support Assistant.

Run with hot reload (reloads on every Python file change):
    gradio app/web.py

This file works across all labs — as answer() gains new parameters
(session_id, user_id in Lab 3; returns trace_id in Lab 5), it adapts
automatically via inspect so you never need to edit this file.
"""

from dotenv import load_dotenv
load_dotenv()

import inspect
import uuid
import gradio as gr
from app.assistant import answer

session_id = str(uuid.uuid4())
user_id = "workshop-user-1"


def chat(message: str, history: list[dict]) -> str:
    # Detect which kwargs answer() currently accepts and pass only those.
    # This lets web.py work unchanged as assistant.py evolves across labs.
    sig = inspect.signature(answer)
    kwargs: dict = {"question": message, "history": history or None}
    if "session_id" in sig.parameters:
        kwargs["session_id"] = session_id
    if "user_id" in sig.parameters:
        kwargs["user_id"] = user_id

    result = answer(**kwargs)
    # From Lab 5, answer() returns (response, trace_id) — unwrap if needed.
    return result[0] if isinstance(result, tuple) else result


demo = gr.ChatInterface(
    fn=chat,
    title="DataStream Support Assistant",
    description="Ask me anything about DataStream — features, pricing, troubleshooting, and best practices.",
    examples=[
        "What connectors does DataStream support?",
        "How does DataStream handle backpressure?",
        "What are the pricing tiers?",
    ],
)

if __name__ == "__main__":
    demo.launch()
