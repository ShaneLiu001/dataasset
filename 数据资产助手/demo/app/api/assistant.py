from __future__ import annotations

from fastapi import APIRouter, HTTPException

from app.core.response import AssistantResponse, ChatRequest, ConfirmRequest, MetadataPrefillStartRequest
from app.core.store import store
from app.graph.builder import demo_graph

router = APIRouter(prefix="/assistant", tags=["assistant"])


@router.post("/chat", response_model=AssistantResponse)
def chat(request: ChatRequest) -> AssistantResponse:
    return demo_graph.run_chat(request)


@router.post("/confirm", response_model=AssistantResponse)
def confirm(request: ConfirmRequest) -> AssistantResponse:
    return demo_graph.run_confirm(request)


@router.post("/metadata-prefill/start", response_model=AssistantResponse)
def start_metadata_prefill(request: MetadataPrefillStartRequest) -> AssistantResponse:
    return demo_graph.start_metadata_prefill(request)


@router.get("/metadata-prefill/tasks/{task_id}")
def get_metadata_prefill_task(task_id: str) -> dict:
    state = store.get_task(task_id)
    if not state:
        raise HTTPException(status_code=404, detail="task not found")
    prefill = state.get("slots", {}).get("metadata_prefill")
    if not prefill:
        raise HTTPException(status_code=404, detail="metadata prefill not found")
    return prefill


@router.get("/metadata-prefill/tasks/{task_id}/evidence/{field_name}")
def get_metadata_prefill_evidence(task_id: str, field_name: str) -> dict:
    state = store.get_task(task_id)
    if not state:
        raise HTTPException(status_code=404, detail="task not found")
    prefill = state.get("slots", {}).get("metadata_prefill", {})
    for item in prefill.get("fields", []):
        if item.get("field_name") == field_name:
            return {
                "task_id": task_id,
                "field_name": field_name,
                "confidence": item.get("confidence"),
                "evidence": item.get("evidence", []),
                "risk_tips": item.get("risk_tips", []),
            }
    raise HTTPException(status_code=404, detail="field evidence not found")


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
