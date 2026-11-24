"""Chat request and response models.

JSON field names stay camelCase so they match the TypeScript workshop API
and the static chat UI.
"""

from __future__ import annotations

from typing import Literal

from pydantic import BaseModel, ConfigDict, Field


class ChatMessage(BaseModel):
    model_config = ConfigDict(populate_by_name=True)

    id: str
    role: Literal["user", "assistant"]
    content: str = Field(min_length=1)
    timestamp: str


class ChatRequest(BaseModel):
    model_config = ConfigDict(populate_by_name=True)

    session_id: str = Field(alias="sessionId", min_length=1)
    user_id: str | None = Field(default=None, alias="userId")
    messages: list[ChatMessage] = Field(min_length=1)


class TraceMeta(BaseModel):
    model_config = ConfigDict(populate_by_name=True)

    context_id: str = Field(alias="contextId")
    context_label: str = Field(alias="contextLabel")
    model: str


class ChatResponse(BaseModel):
    model_config = ConfigDict(populate_by_name=True)

    answer: str
    used_tools: list[str] = Field(alias="usedTools")
    trace_meta: TraceMeta = Field(alias="traceMeta")
