from __future__ import annotations

from app.tools.data_loader import load_json


def create_datasource_register_task() -> dict:
    task = load_json("datasource_tasks.json")["datasource_demo"]
    return {"status": "submitted", **task}


def create_metadata_collect_task() -> dict:
    task = load_json("datasource_tasks.json")["datasource_demo"]
    return {
        "status": "running",
        "metadata_collect_task_id": task["metadata_collect_task_id"],
        "message": "元数据采集任务已创建。",
    }


def create_security_scan_task() -> dict:
    task = load_json("datasource_tasks.json")["datasource_demo"]
    return {
        "status": "running",
        "security_scan_task_id": task["security_scan_task_id"],
        "security_ticket_id": task["security_ticket_id"],
        "message": "安全扫描任务已创建。",
    }

