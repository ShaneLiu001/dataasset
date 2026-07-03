from __future__ import annotations

from app.tools.data_loader import load_json


def scan_security_level(asset_id: str) -> dict:
    return load_json("security_scan.json")["scan_results"].get(
        asset_id,
        {
            "security_level": "L1",
            "sensitive_fields": [],
            "risk_summary": "未识别高风险敏感字段。",
            "ticket_id": None,
        },
    )

