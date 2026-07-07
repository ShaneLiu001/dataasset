from __future__ import annotations

from typing import Any

from app.tools.data_loader import load_json


def generate_metadata_prefill(
    asset: dict[str, Any],
    standards: list[dict[str, Any]],
    security: dict[str, Any],
    lineage: dict[str, Any] | None = None,
) -> dict[str, Any]:
    """Generate reviewable metadata candidates from existing platform context."""
    standards_by_field = {item["field"]: item for item in standards}
    history_by_field = {
        item["field"]: item for item in load_json("metadata_prefill/history_examples.json")["examples"]
    }
    naming_rules = load_json("metadata_prefill/naming_rules.json")["rules"]
    security_rules = {
        item["field"]: item for item in load_json("metadata_prefill/security_rules.json")["rules"]
    }
    sensitive_fields = {item["field"]: item for item in security.get("sensitive_fields", [])}

    fields = []
    summary = {
        "table_items": 2,
        "field_items": 0,
        "security_items": 0,
        "need_confirm": 0,
        "low_confidence": 0,
        "need_supplement": 0,
        "manual_modified": 0,
    }
    for field in asset.get("fields", []):
        candidate = _build_field_candidate(
            field,
            standards_by_field.get(field["name"]),
            history_by_field.get(field["name"]),
            _match_naming_rule(field["name"], naming_rules),
            security_rules.get(field["name"]),
            sensitive_fields.get(field["name"]),
        )
        fields.append(candidate)
        summary["field_items"] += 2
        summary["security_items"] += 1
        if candidate["confidence"] == "low":
            summary["low_confidence"] += 1
        if candidate["review_status"] == "need_supplement":
            summary["need_supplement"] += 1
        if candidate["recommended_security_level"] in {"3", "4"} or candidate["confidence"] in {"medium", "low"}:
            summary["need_confirm"] += 1

    table_candidate = _build_table_candidate(asset, lineage or {})
    return {
        "agent": "metadata_governance_agent",
        "capability": "metadata_prefill",
        "asset": table_candidate,
        "summary": summary,
        "fields": fields,
        "collaboration": [
            {
                "agent": "数据地图 Agent",
                "contribution": "提供表、字段、负责人、已有中文名和备注上下文",
                "tools": ["get_asset_detail_tool"],
            },
            {
                "agent": "数据标准 Agent",
                "contribution": "提供字段标准名称、命名规则和标准映射依据",
                "tools": ["get_data_standard_tool"],
            },
            {
                "agent": "安全扫描 Agent",
                "contribution": "提供敏感字段识别、安全等级推荐和风险说明",
                "tools": ["scan_security_level_tool"],
            },
            {
                "agent": "数据血缘 Agent",
                "contribution": "补充上下游加工和使用场景依据",
                "tools": ["query_upstream_lineage_tool", "get_sql_task_detail_tool"],
            },
        ],
    }


def apply_metadata_prefill_confirmation(prefill: dict[str, Any], edits: dict[str, Any] | None = None) -> dict[str, Any]:
    edits = edits or {}
    field_edits = edits.get("fields", {})
    final_fields = []
    manual_modified = 0
    for item in prefill.get("fields", []):
        edit = field_edits.get(item["field_name"], {})
        final_item = {**item}
        if "final_cn_name" in edit:
            final_item["final_cn_name"] = edit["final_cn_name"]
            final_item["review_status"] = "manual_modified"
            manual_modified += 1
        else:
            final_item["final_cn_name"] = item.get("suggested_cn_name", "")
        if "final_comment" in edit:
            final_item["final_comment"] = edit["final_comment"]
            final_item["review_status"] = "manual_modified"
            manual_modified += 1
        else:
            final_item["final_comment"] = item.get("suggested_comment", "")
        if "final_security_level" in edit:
            final_item["final_security_level"] = edit["final_security_level"]
            final_item["review_status"] = "manual_modified"
            manual_modified += 1
        else:
            final_item["final_security_level"] = item.get("recommended_security_level", "2")
        final_fields.append(final_item)

    summary = {**prefill.get("summary", {})}
    summary["manual_modified"] = manual_modified
    return {**prefill, "summary": summary, "fields": final_fields, "review_status": "confirmed"}


def _build_table_candidate(asset: dict[str, Any], lineage: dict[str, Any]) -> dict[str, Any]:
    table_cn_name = asset.get("table_cn_name") or "客户收入明细表"
    table_comment = (
        asset.get("description")
        or lineage.get("comment_suggestion")
        or "存储客户收入统计明细，用于客户价值分析、经营分析和收入指标加工。"
    )
    return {
        "asset_id": asset["asset_id"],
        "table_name": asset["table_name"],
        "current_cn_name": asset.get("table_cn_name", ""),
        "suggested_chinese_name": table_cn_name,
        "suggested_comment": table_comment,
        "confidence": "medium" if asset.get("description") else "low",
        "evidence": [
            "数据地图 Agent 返回表基础信息和已有描述",
            "数据血缘 Agent 返回下游报表和加工任务上下文",
        ],
        "review_status": "pending",
    }


def _build_field_candidate(
    field: dict[str, Any],
    standard: dict[str, Any] | None,
    history: dict[str, Any] | None,
    naming_rule: dict[str, Any] | None,
    security_rule: dict[str, Any] | None,
    sensitive_field: dict[str, Any] | None,
) -> dict[str, Any]:
    suggested_cn_name = (
        field.get("cn_name")
        or (standard or {}).get("standard_name")
        or (history or {}).get("cn_name")
        or (naming_rule or {}).get("cn_name")
        or ""
    )
    suggested_comment = (
        field.get("comment")
        or (history or {}).get("comment")
        or (standard or {}).get("rule")
        or (naming_rule or {}).get("comment")
        or ""
    )
    confidence = _confidence(field, standard, history, naming_rule, security_rule)
    evidence = []
    if field.get("cn_name") or field.get("comment"):
        evidence.append("数据地图 Agent 返回已有人工维护内容，优先保留。")
    if standard:
        evidence.append(f"数据标准 Agent 命中标准：{standard['standard_name']}。")
    if history:
        evidence.append(f"历史样例命中：{history['source']}。")
    if naming_rule:
        evidence.append(f"字段命名规则命中：{naming_rule['pattern']}。")
    if security_rule:
        evidence.append(f"安全扫描 Agent 建议 {security_rule['recommended_security_level']} 级：{security_rule['reason']}")
    if sensitive_field:
        evidence.append(f"安全扫描识别敏感类型：{sensitive_field['type']}，脱敏策略：{sensitive_field['masking']}。")
    if not evidence:
        evidence.append("缺少标准、历史样例和命名规则依据，建议人工补充。")

    return {
        "field_name": field["name"],
        "field_type": field.get("type", ""),
        "current_cn_name": field.get("cn_name", ""),
        "current_comment": field.get("comment", ""),
        "suggested_cn_name": suggested_cn_name,
        "suggested_comment": suggested_comment,
        "recommended_security_level": (security_rule or {}).get("recommended_security_level", "2"),
        "confidence": confidence,
        "source": "metadata_governance_agent",
        "evidence": evidence,
        "risk_tips": _risk_tips(field["name"], confidence, security_rule),
        "review_status": "need_supplement" if not suggested_cn_name or not suggested_comment else "pending",
    }


def _match_naming_rule(field_name: str, rules: list[dict[str, Any]]) -> dict[str, Any] | None:
    for rule in rules:
        if rule["pattern"] in field_name:
            return rule
    return None


def _confidence(
    field: dict[str, Any],
    standard: dict[str, Any] | None,
    history: dict[str, Any] | None,
    naming_rule: dict[str, Any] | None,
    security_rule: dict[str, Any] | None,
) -> str:
    if field.get("cn_name") and history and standard:
        return "high"
    if standard and history:
        return "high"
    if standard or history or (naming_rule and security_rule):
        return "medium"
    return "low"


def _risk_tips(field_name: str, confidence: str, security_rule: dict[str, Any] | None) -> list[str]:
    tips = []
    if confidence in {"medium", "low"}:
        tips.append("置信度不是高，提交前需要人工重点确认。")
    if security_rule and security_rule.get("recommended_security_level") in {"3", "4"}:
        tips.append("字段安全等级较高，需要显式确认后才能提交。")
    if field_name == "income_amt":
        tips.append("收入金额口径可能存在税前、税后或实收差异，建议确认业务口径。")
    return tips
