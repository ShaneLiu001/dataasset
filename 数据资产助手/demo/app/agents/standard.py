from __future__ import annotations

from app.tools.registry import ToolRegistry


def collect_standards(asset: dict, tools: ToolRegistry) -> list[dict]:
    field_names = [field["name"] for field in asset.get("fields", [])]
    return tools.call("get_data_standard_tool", field_names=field_names)

