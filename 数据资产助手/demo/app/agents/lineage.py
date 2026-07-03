from __future__ import annotations

from app.core.response import Card
from app.tools.registry import ToolRegistry


def collect_lineage(asset_id: str, tools: ToolRegistry) -> dict:
    lineage = tools.call("query_upstream_lineage_tool", asset_id=asset_id)
    sql_task = tools.call("get_sql_task_detail_tool", asset_id=asset_id)
    comment = tools.call("extract_sql_comment_tool", sql=sql_task.get("sql", ""))
    return {"lineage": lineage, "sql_task": sql_task, "comment_suggestion": comment}


def build_lineage_card(asset_id: str, tools: ToolRegistry) -> Card:
    data = collect_lineage(asset_id, tools)
    return Card(type="lineage_summary", title="血缘与 SQL 注释识别", data=data)

