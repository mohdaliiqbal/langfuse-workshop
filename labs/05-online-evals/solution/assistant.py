"""
Lab 5 Solution: assistant.py
Returns (response, trace_id, observation_id) so web.py can attach scores to the specific observation.
"""

import os
import uuid
from langfuse.openai import OpenAI
from langfuse import observe, get_client, propagate_attributes
from app.knowledge_base import retrieve, format_context

client = OpenAI()


def get_system_prompt():
    langfuse = get_client()
    return langfuse.get_prompt("datastream-system-prompt", label="production")


@observe()
def retrieve_context(question: str) -> str:
    docs = retrieve(question)
    return format_context(docs)


@observe()
def call_llm(messages: list[dict], prompt=None) -> str:
    response = client.chat.completions.create(
        model=os.getenv("APP_MODEL", "gpt-4o-mini"),
        messages=messages,
        temperature=0.3,
        langfuse_prompt=prompt,  # links this generation to the prompt version
    )
    return response.choices[0].message.content


@observe(name="support-question")
def answer(
    question: str,
    history: list[dict] | None = None,
    session_id: str | None = None,
    user_id: str | None = None,
) -> tuple[str, str | None, str | None]:
    langfuse = get_client()

    with propagate_attributes(
        trace_name="support-question",
        session_id=session_id or str(uuid.uuid4()),
        user_id=user_id,
        tags=["workshop"],
        metadata={"app_version": "1.0.0"},
    ):
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

        response = call_llm(messages, prompt=prompt_obj)
        trace_id = langfuse.get_current_trace_id()
        observation_id = langfuse.get_current_observation_id()

    return response, trace_id, observation_id
