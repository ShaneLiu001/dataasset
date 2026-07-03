from __future__ import annotations

from app.tools.data_loader import load_json


def query_upstream_lineage(asset_id: str) -> dict:
    return load_json("lineage.json")["lineage"].get(asset_id, {})


def get_sql_task_detail(asset_id: str) -> dict:
    lineage = query_upstream_lineage(asset_id)
    return lineage.get("sql_task", {})


def extract_sql_comment(sql: str) -> str:
    comments = []
    for line in sql.splitlines():
        stripped = line.strip()
        if stripped.startswith("--"):
            comments.append(stripped.lstrip("-").strip())
    if not comments:
        return "未识别到 SQL 注释。"
    return "；".join(comments)

