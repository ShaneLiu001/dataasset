from __future__ import annotations

from collections.abc import Callable
from typing import Any

from app.core.observability import ToolTimer
from app.core.response import ToolCallAudit
from app.tools.activiti_tool import submit_activiti_process
from app.tools.data_map_tool import get_asset_detail, search_data_map
from app.tools.datasource_tool import (
    create_datasource_register_task,
    create_metadata_collect_task,
    create_security_scan_task,
)
from app.tools.lineage_tool import extract_sql_comment, get_sql_task_detail, query_upstream_lineage
from app.tools.memory_tool import get_user_common_context
from app.tools.security_scan_tool import scan_security_level
from app.tools.standard_tool import get_data_standards


TOOLS: dict[str, Callable[..., Any]] = {
    "search_data_map_tool": search_data_map,
    "get_asset_detail_tool": get_asset_detail,
    "get_user_common_context_tool": get_user_common_context,
    "get_data_standard_tool": get_data_standards,
    "query_upstream_lineage_tool": query_upstream_lineage,
    "get_sql_task_detail_tool": get_sql_task_detail,
    "extract_sql_comment_tool": extract_sql_comment,
    "scan_security_level_tool": scan_security_level,
    "submit_activiti_process_tool": submit_activiti_process,
    "create_datasource_register_tool": create_datasource_register_task,
    "create_metadata_collect_task_tool": create_metadata_collect_task,
    "create_security_scan_task_tool": create_security_scan_task,
}


class ToolRegistry:
    def __init__(self) -> None:
        self.audit: list[ToolCallAudit] = []

    def call(self, tool_name: str, **kwargs: Any) -> Any:
        if tool_name not in TOOLS:
            raise KeyError(f"Unknown tool: {tool_name}")
        timer = ToolTimer(tool_name, kwargs)
        result = TOOLS[tool_name](**kwargs)
        output_summary = result if isinstance(result, dict) else {"items": len(result) if isinstance(result, list) else 1}
        self.audit.append(timer.finish(output_summary))
        return result

