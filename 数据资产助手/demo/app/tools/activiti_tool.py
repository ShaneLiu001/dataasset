from __future__ import annotations

from datetime import datetime


def submit_activiti_process(task_id: str, payload: dict) -> dict:
    return {
        "process_instance_id": f"ACT_{datetime.now().strftime('%Y%m%d%H%M%S')}",
        "task_id": task_id,
        "status": "submitted",
        "process_name": "单表元数据治理流程",
        "payload_summary": {
            "asset_id": payload.get("asset_id"),
            "space_id": payload.get("space_id"),
            "project_id": payload.get("project_id"),
        },
    }

