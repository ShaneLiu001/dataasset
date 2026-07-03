from __future__ import annotations

import re


def classify_intent(question: str) -> str:
    if "治理" in question or "补充中文名" in question or "补齐备注" in question:
        return "GOVERN_METADATA"
    if "数据源" in question and ("登记" in question or "接入" in question or "新增" in question):
        return "REGISTER_DATASOURCE"
    if "血缘" in question or "上游" in question or "加工任务" in question:
        return "QUERY_LINEAGE"
    if "哪张表" in question or "用哪张表" in question or "查表" in question:
        return "FIND_ASSET"
    return "UNKNOWN"


def extract_table_name(question: str) -> str:
    match = re.search(r"([a-zA-Z][a-zA-Z0-9_]*\.[a-zA-Z0-9_]+|[a-zA-Z][a-zA-Z0-9_]{2,})", question)
    if match:
        value = match.group(1)
        return value.split(".")[-1]
    return "dwd_customer_income_df"
