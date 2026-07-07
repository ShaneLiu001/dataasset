from __future__ import annotations

from typing import Any, Literal

from pydantic import BaseModel, Field


class UserContext(BaseModel):
    user_id: str = "mock_user"
    user_name: str = "Mock User"
    org_id: str = "data_center"
    role_codes: list[str] = Field(default_factory=list)
    trace_id: str = "trace-demo"
    access_token: str | None = None


class ChatRequest(BaseModel):
    session_id: str
    thread_id: str
    question: str
    user_context: UserContext = Field(default_factory=UserContext)


class ConfirmRequest(BaseModel):
    thread_id: str
    task_id: str
    confirm_id: str
    confirmed: bool
    payload: dict[str, Any] = Field(default_factory=dict)


class MetadataPrefillStartRequest(BaseModel):
    thread_id: str
    asset_id: str = "asset_001"
    table_name: str = "dwd_customer_income_df"
    user_context: UserContext = Field(default_factory=UserContext)


class Action(BaseModel):
    code: str
    label: str
    payload: dict[str, Any] = Field(default_factory=dict)


class Card(BaseModel):
    type: str
    title: str
    data: dict[str, Any] = Field(default_factory=dict)
    actions: list[Action] = Field(default_factory=list)


class NeedConfirm(BaseModel):
    required: bool = False
    confirm_id: str | None = None
    type: str | None = None
    payload: dict[str, Any] = Field(default_factory=dict)


class ToolCallAudit(BaseModel):
    tool_name: str
    success: bool
    input_summary: dict[str, Any] = Field(default_factory=dict)
    output_summary: dict[str, Any] = Field(default_factory=dict)
    error_code: str | None = None
    duration_ms: int = 0


class AssistantResponse(BaseModel):
    task_id: str
    thread_id: str
    intent: str
    status: Literal["running", "waiting_confirm", "completed", "failed"]
    answer: str
    cards: list[Card] = Field(default_factory=list)
    need_confirm: NeedConfirm = Field(default_factory=NeedConfirm)
    next_actions: list[str] = Field(default_factory=list)
    tool_calls: list[ToolCallAudit] = Field(default_factory=list)
    trace_id: str


class ErrorResponse(BaseModel):
    error_code: str
    error_message: str
    trace_id: str | None = None
