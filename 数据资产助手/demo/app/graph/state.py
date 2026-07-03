from __future__ import annotations

from typing import Any

from pydantic import BaseModel, Field

from app.core.response import Card, NeedConfirm, UserContext


class GraphState(BaseModel):
    thread_id: str
    task_id: str
    question: str
    user_context: UserContext
    intent: str = "UNKNOWN"
    status: str = "running"
    slots: dict[str, Any] = Field(default_factory=dict)
    selected_asset: dict[str, Any] = Field(default_factory=dict)
    user_preferences: dict[str, Any] = Field(default_factory=dict)
    evidence: dict[str, Any] = Field(default_factory=dict)
    draft: dict[str, Any] = Field(default_factory=dict)
    cards: list[Card] = Field(default_factory=list)
    need_confirm: NeedConfirm = Field(default_factory=NeedConfirm)
    answer: str = ""
    next_actions: list[str] = Field(default_factory=list)

