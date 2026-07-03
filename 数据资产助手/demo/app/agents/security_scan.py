from __future__ import annotations

from app.tools.registry import ToolRegistry


def collect_security_scan(asset_id: str, tools: ToolRegistry) -> dict:
    return tools.call("scan_security_level_tool", asset_id=asset_id)

