from __future__ import annotations

from app.core.response import Action, Card


def build_governance_draft(
    asset: dict,
    standards: list[dict],
    lineage: dict,
    security: dict,
    context: dict,
    prefill: dict | None = None,
) -> dict:
    standards_by_field = {item["field"]: item for item in standards}
    prefill_by_field = {item["field_name"]: item for item in (prefill or {}).get("fields", [])}
    return {
        "asset_id": asset["asset_id"],
        "table_name": asset["table_name"],
        "table_cn_name": (prefill or {}).get("asset", {}).get("suggested_chinese_name")
        or asset.get("table_cn_name")
        or "客户收入日汇总表",
        "table_comment": (prefill or {}).get("asset", {}).get("suggested_comment")
        or lineage.get("comment_suggestion")
        or asset.get("description"),
        "space_id": context.get("space_id"),
        "project_id": context.get("project_id"),
        "dev_account": context.get("dev_account"),
        "security_level": security.get("security_level"),
        "prefill_summary": (prefill or {}).get("summary", {}),
        "field_suggestions": [
            {
                "field": field["name"],
                "current_cn_name": field.get("cn_name", ""),
                "suggested_cn_name": prefill_by_field.get(field["name"], {}).get(
                    "final_cn_name",
                    prefill_by_field.get(field["name"], {}).get(
                        "suggested_cn_name",
                        standards_by_field.get(field["name"], {}).get("standard_name", field.get("cn_name", "")),
                    ),
                ),
                "suggested_comment": prefill_by_field.get(field["name"], {}).get(
                    "final_comment",
                    prefill_by_field.get(field["name"], {}).get(
                        "suggested_comment",
                        standards_by_field.get(field["name"], {}).get("rule", field.get("comment", "")),
                    ),
                ),
                "security_level": prefill_by_field.get(field["name"], {}).get("final_security_level")
                or prefill_by_field.get(field["name"], {}).get("recommended_security_level"),
                "confidence": prefill_by_field.get(field["name"], {}).get("confidence"),
            }
            for field in asset.get("fields", [])
        ],
        "evidence": {
            "standards": standards,
            "lineage": lineage,
            "security_scan": security,
            "metadata_prefill": prefill or {},
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


def build_metadata_prefill_card(prefill: dict) -> Card:
    return Card(
        type="metadata_prefill_review",
        title="元数据治理 Agent · 智能元数据补全",
        data=prefill,
        actions=[
            Action(code="confirm_metadata_prefill", label="确认补全结果并生成治理草案"),
            Action(code="edit_metadata_prefill", label="调整候选值"),
        ],
    )
