"""
Lab 1 Solution: Basic Tracing
Drop-in replacement for app/assistant.py
"""

import os
from openai import OpenAI
from langfuse import observe, get_client
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


@observe()  # Creates a child span for retrieval
def retrieve_context(question: str) -> str:
    docs = retrieve(question)
    return format_context(docs)


@observe(as_type="generation")  # Marks this as an LLM generation
def call_llm(messages: list[dict]) -> str:
    response = client.chat.completions.create(
        model=os.getenv("APP_MODEL", "gpt-4o-mini"),
        messages=messages,
        temperature=0.3,
    )
    return response.choices[0].message.content


@observe()  # Root trace for the full answer pipeline
def answer(question: str, history: list[dict] | None = None) -> str:
    # Retrieval - creates a nested span automatically
    context = retrieve_context(question)

    # Build messages
    messages = [{"role": "system", "content": SYSTEM_PROMPT}]
    if history:
        messages.extend(history)
    messages.append({
        "role": "user",
        "content": f"Documentation context:\n{context}\n\nQuestion: {question}"
    })

    # LLM call - creates a nested generation automatically
    return call_llm(messages)
