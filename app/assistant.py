"""
Core assistant logic - no Langfuse instrumentation yet.
Users will add observability in the labs.
"""

import os
from openai import OpenAI
from app.knowledge_base import retrieve, format_context

client = OpenAI()

SYSTEM_PROMPT = """You are a helpful customer support assistant for DataStream, a real-time data pipeline platform.

Your role is to help users with questions about DataStream's features, pricing, troubleshooting, and best practices.

Guidelines:
- Be concise and direct. Answer the question asked.
- Use the provided documentation context when available.
- If the answer is not in the context, say so honestly rather than guessing.
- For technical issues, provide actionable steps.
- Maintain a friendly, professional tone.
"""


def answer(question: str, history: list[dict] | None = None) -> str:
    """
    Answer a user question using retrieved context and conversation history.

    Args:
        question: The user's question
        history: List of previous messages in the format [{"role": ..., "content": ...}]

    Returns:
        The assistant's response
    """
    # Retrieve relevant docs
    docs = retrieve(question)
    context = format_context(docs)

    # Build message list
    messages = [{"role": "system", "content": SYSTEM_PROMPT}]

    if history:
        messages.extend(history)

    messages.append({
        "role": "user",
        "content": f"Documentation context:\n{context}\n\nQuestion: {question}"
    })

    # Call the LLM
    response = client.chat.completions.create(
        model=os.getenv("APP_MODEL", "gpt-4o-mini"),
        messages=messages,
        temperature=0.3,
    )

    return response.choices[0].message.content
