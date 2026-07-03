from __future__ import annotations

from app.core.response import Action, Card
from app.tools.registry import ToolRegistry


def build_candidate_card(table_name: str, tools: ToolRegistry) -> Card:
    candidates = tools.call("search_data_map_tool", table_name=table_name)
    return Card(
        type="asset_candidates",
        title="同名表候选确认",
        data={"table_name": table_name, "candidates": candidates},
        actions=[
            Action(
                code="confirm_asset",
                label=f"选择 {candidate['datasource_id']} / {candidate['schema']}",
                payload={"asset_id": candidate["asset_id"]},
            )
            for candidate in candidates
        ],
    )


def build_asset_recommendation(question: str, tools: ToolRegistry) -> Card:
    candidates = tools.call("search_data_map_tool", table_name="dwd_customer_income_df")
    best = candidates[0]
    return Card(
        type="asset_recommendation",
        title="推荐资产",
        data={
            "question": question,
            "asset": best,
            "reason": [
                "命中客户、收入两个业务概念。",
                "该表为认证宽表。",
                "下游 12 张报表引用，近 30 天查询 86 次。",
            ],
        },
    )

