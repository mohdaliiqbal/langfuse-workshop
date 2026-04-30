"""
The brain of the app. One function — answer() — contains three key pieces of logic:
  - Retrieval (lines 31-32): calls retrieve() and format_context() from the knowledge base to get relevant docs
  - Message assembly (lines 35-43): builds the messages array — system prompt + history + user question with context
  - LLM call (lines 46-50): sends the messages to OpenAI and returns the response

In Lab 2 you'll extract the retrieval and LLM call into their own functions (retrieve_context, call_llm)
so Langfuse can trace each step separately.
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
    # Retrieve relevant docs from the knowledge base
    docs = retrieve(question)
    context = format_context(docs)

    # Build the messages array: system prompt + conversation history + user question with context
    messages = [{"role": "system", "content": SYSTEM_PROMPT}]

    if history:
        messages.extend(history)

    messages.append({
        "role": "user",
        "content": f"Documentation context:\n{context}\n\nQuestion: {question}"
    })

    # Call the LLM and return the response
    response = client.chat.completions.create(
        model=os.getenv("APP_MODEL", "gpt-4o-mini"),
        messages=messages,
        temperature=0.3,
    )

    return response.choices[0].message.content
