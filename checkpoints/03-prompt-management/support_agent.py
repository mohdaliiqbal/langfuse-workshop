"""Traced Dad IT Support Agent. The system prompt is still the local constant.

Prompt management (chapter 03) replaces the direct SYSTEM_PROMPT use with a
Langfuse fetch plus this constant as the fallback.
"""

from __future__ import annotations

import json
from typing import Any

from langfuse import get_client, observe, propagate_attributes
from langfuse.openai import OpenAI

from app.env import env
from app.models import ChatRequest, ChatResponse, TraceMeta
from app.support_data import get_support_context
from app.tools import TOOL_DEFINITIONS, execute_tool

# checkpoint-sync:begin system-prompt
SYSTEM_PROMPT = """You are Dad IT Support Agent.
You are talking to Dad. He opened this chat himself to get help with his iPhone.

Look up which iPhone and apps he has, and search the help library, so the steps match his phone. Then tell him what to do: what to tap, and what he should see on the screen.

Use plain language. Stay with him until he has something to try.
"""
# checkpoint-sync:end system-prompt


def _read_assistant_text(message: Any) -> str:
    content = getattr(message, "content", None)
    if isinstance(content, str):
        return content.strip()
    return ""


def _parse_tool_arguments(arguments_text: str) -> dict[str, Any] | None:
    try:
        parsed = json.loads(arguments_text)
    except json.JSONDecodeError:
        return None
    if isinstance(parsed, dict):
        return parsed
    return {}


@observe(name="dad-it-support-chat-turn", as_type="agent")
def run_support_conversation(request: ChatRequest) -> ChatResponse:
    # Log the request body (messages, sessionId, userId) as the root input, the
    # same shape the TypeScript app logs. The 4.2 evaluators map Input -> messages.
    get_client().update_current_span(
        input=request.model_dump(mode="json", by_alias=True, exclude_none=True)
    )
    context = get_support_context()
    user_id = request.user_id or f"workshop-{context['id']}"

    with propagate_attributes(
        user_id=user_id,
        session_id=request.session_id,
        trace_name="dad-it-support-chat-turn",
        tags=["langfuse-workshop", "dad-it-support"],
    ):
        client = OpenAI(api_key=env.openai_api_key)
        transcript: list[dict[str, Any]] = [
            {"role": "system", "content": SYSTEM_PROMPT},
            *[{"role": message.role, "content": message.content} for message in request.messages],
        ]
        used_tools: list[str] = []
        final_answer = ""

        for _attempt in range(6):
            response = client.chat.completions.create(
                model=env.openai_model,
                messages=transcript,
                tools=TOOL_DEFINITIONS,
                tool_choice="auto",
            )
            message = response.choices[0].message if response.choices else None
            if message is None:
                raise RuntimeError("OpenAI returned no assistant message.")
            transcript.append(message.model_dump(exclude_none=True))

            tool_calls = message.tool_calls or []
            if not tool_calls:
                final_answer = _read_assistant_text(message)
                break

            for tool_call in tool_calls:
                if getattr(tool_call, "type", None) != "function":
                    continue
                if tool_call.function.name not in used_tools:
                    used_tools.append(tool_call.function.name)
                parsed = _parse_tool_arguments(tool_call.function.arguments)
                if parsed is None:
                    result = {
                        "ok": False,
                        "error": (
                            f"The tool arguments for {tool_call.function.name} were not valid JSON."
                        ),
                    }
                else:
                    result = execute_tool(tool_call.function.name, parsed)
                transcript.append(
                    {
                        "role": "tool",
                        "tool_call_id": tool_call.id,
                        "content": json.dumps(result),
                    }
                )

        if not final_answer:
            final_answer = (
                "I ran out of room before finishing that answer. "
                "Please ask the question once more in a slightly shorter way."
            )

        return ChatResponse(
            answer=final_answer,
            used_tools=used_tools,
            trace_meta=TraceMeta(
                context_id=context["id"],
                context_label=context["label"],
                model=env.openai_model,
            ),
        )
