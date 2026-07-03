from __future__ import annotations

from fastapi import APIRouter, HTTPException

from app.core.response import AssistantResponse, ChatRequest, ConfirmRequest
from app.core.store import store
from app.graph.builder import demo_graph

router = APIRouter(prefix="/assistant", tags=["assistant"])


@router.post("/chat", response_model=AssistantResponse)
def chat(request: ChatRequest) -> AssistantResponse:
    return demo_graph.run_chat(request)


@router.post("/confirm", response_model=AssistantResponse)
def confirm(request: ConfirmRequest) -> AssistantResponse:
    return demo_graph.run_confirm(request)


@router.get("/tasks/{task_id}")
def get_task(task_id: str) -> dict:
    state = store.get_task(task_id)
    if not state:
        raise HTTPException(status_code=404, detail="task not found")
    return state


@router.post("/tasks/{task_id}/refresh", response_model=AssistantResponse)
def refresh_task(task_id: str) -> AssistantResponse:
    response = demo_graph.refresh_task(task_id)
    if not response:
        raise HTTPException(status_code=404, detail="task not found")
    return response
