"""
Lab 3 Solution: Prompt Management
Drop-in replacement for app/assistant.py
"""

import os
import uuid
from openai import OpenAI
from langfuse import observe, get_client, propagate_attributes
from app.knowledge_base import retrieve, format_context

client = OpenAI()


def get_system_prompt():
    """Fetch the system prompt from Langfuse prompt management."""
    langfuse = get_client()
    prompt = langfuse.get_prompt("datastream-system-prompt", label="production")
    return prompt


@observe()
def retrieve_context(question: str) -> str:
    docs = retrieve(question)
    return format_context(docs)


@observe(as_type="generation")
def call_llm(messages: list[dict], prompt=None) -> str:
    langfuse = get_client()

    response = client.chat.completions.create(
        model=os.getenv("APP_MODEL", "gpt-4o-mini"),
        messages=messages,
        temperature=0.3,
    )

    langfuse.update_current_observation(
        model=response.model,
        prompt=prompt,  # Links this generation to the prompt version in Langfuse
        usage_details={
            "input": response.usage.prompt_tokens,
            "output": response.usage.completion_tokens,
            "total": response.usage.total_tokens,
        }
    )

    return response.choices[0].message.content


@observe()
def answer(
    question: str,
    history: list[dict] | None = None,
    session_id: str | None = None,
    user_id: str | None = None,
) -> str:
    with propagate_attributes(
        trace_name="support-question",
        session_id=session_id or str(uuid.uuid4()),
        user_id=user_id,
        tags=["workshop", "lab-3"],
        metadata={"app_version": "1.0.0"},
    ):
        # Fetch prompt from Langfuse (cached after first call)
        prompt_obj = get_system_prompt()
        system_prompt = prompt_obj.compile(product_name="DataStream")

        context = retrieve_context(question)

        messages = [{"role": "system", "content": system_prompt}]
        if history:
            messages.extend(history)
        messages.append({
            "role": "user",
            "content": f"Documentation context:\n{context}\n\nQuestion: {question}"
        })

        # Pass prompt_obj so the generation is linked to this prompt version
        return call_llm(messages, prompt=prompt_obj)
