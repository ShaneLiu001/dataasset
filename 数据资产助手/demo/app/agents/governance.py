from __future__ import annotations

from app.core.response import Action, Card


def build_governance_draft(asset: dict, standards: list[dict], lineage: dict, security: dict, context: dict) -> dict:
    standards_by_field = {item["field"]: item for item in standards}
    return {
        "asset_id": asset["asset_id"],
        "table_name": asset["table_name"],
        "table_cn_name": asset.get("table_cn_name") or "客户收入日汇总表",
        "table_comment": lineage.get("comment_suggestion") or asset.get("description"),
        "space_id": context.get("space_id"),
        "project_id": context.get("project_id"),
        "dev_account": context.get("dev_account"),
        "security_level": security.get("security_level"),
        "field_suggestions": [
            {
                "field": field["name"],
                "current_cn_name": field.get("cn_name", ""),
                "suggested_cn_name": standards_by_field.get(field["name"], {}).get("standard_name", field.get("cn_name", "")),
                "suggested_comment": standards_by_field.get(field["name"], {}).get("rule", field.get("comment", "")),
            }
            for field in asset.get("fields", [])
        ],
        "evidence": {
            "standards": standards,
            "lineage": lineage,
            "security_scan": security,
        },
    }


def build_governance_card(draft: dict) -> Card:
    return Card(
        type="metadata_governance_draft",
        title="元数据治理草案",
        data=draft,
        actions=[
            Action(code="submit_activiti", label="提交 Activiti 流程", payload={"asset_id": draft["asset_id"]}),
            Action(code="edit_draft", label="调整草案", payload={"asset_id": draft["asset_id"]}),
        ],
    )

