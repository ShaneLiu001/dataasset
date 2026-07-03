from __future__ import annotations

import logging
from time import perf_counter
from typing import Any

from app.core.sanitizer import sanitize
from app.core.response import ToolCallAudit

logger = logging.getLogger("data_asset_assistant_demo")


def log_event(name: str, payload: dict[str, Any]) -> None:
    logger.info("%s %s", name, sanitize(payload))


class ToolTimer:
    def __init__(self, tool_name: str, input_summary: dict[str, Any]) -> None:
        self.tool_name = tool_name
        self.input_summary = input_summary
        self.started = perf_counter()

    def finish(self, output_summary: dict[str, Any], success: bool = True) -> ToolCallAudit:
        duration_ms = int((perf_counter() - self.started) * 1000)
        audit = ToolCallAudit(
            tool_name=self.tool_name,
            success=success,
            input_summary=sanitize(self.input_summary),
            output_summary=sanitize(output_summary),
            duration_ms=duration_ms,
        )
        log_event("tool_call", audit.model_dump())
        return audit

