from app.core.response import ChatRequest, ConfirmRequest, MetadataPrefillStartRequest, UserContext
from app.graph.builder import demo_graph


def test_governance_flow_reaches_activiti_submission() -> None:
    user_context = UserContext(
        user_id="zhangsan",
        user_name="张三",
        org_id="data_center",
        role_codes=["data_steward"],
        trace_id="trace-test-001",
        access_token="mock-token",
    )
    chat = demo_graph.run_chat(
        ChatRequest(
            session_id="S_10001",
            thread_id="T_10001",
            question="帮我治理 dwd_customer_income_df 这张表",
            user_context=user_context,
        )
    )

    assert chat.intent == "GOVERN_METADATA"
    assert chat.status == "waiting_confirm"
    assert chat.need_confirm.type == "confirm_asset"
    assert chat.cards[0].type == "asset_candidates"

    prefill = demo_graph.run_confirm(
        ConfirmRequest(
            thread_id=chat.thread_id,
            task_id=chat.task_id,
            confirm_id=chat.need_confirm.confirm_id or "",
            confirmed=True,
            payload={
                "asset_id": "asset_001",
                "space_id": "space_finance",
                "project_id": "project_dwd",
                "dev_account": "dev_zhangsan",
            },
        )
    )

    assert prefill.status == "waiting_confirm"
    assert prefill.need_confirm.type == "confirm_metadata_prefill"
    assert prefill.cards[0].type == "metadata_prefill_review"
    assert prefill.cards[0].data["agent"] == "metadata_governance_agent"
    assert prefill.cards[0].data["capability"] == "metadata_prefill"
    assert prefill.cards[0].data["summary"]["need_confirm"] >= 1
    assert any(item["field_name"] == "income_amt" for item in prefill.cards[0].data["fields"])

    draft = demo_graph.run_confirm(
        ConfirmRequest(
            thread_id=prefill.thread_id,
            task_id=prefill.task_id,
            confirm_id=prefill.need_confirm.confirm_id or "",
            confirmed=True,
            payload={
                "edits": {
                    "fields": {
                        "income_amt": {
                            "final_cn_name": "客户统计收入金额",
                            "final_comment": "客户在统计周期内产生的收入金额，口径按经营分析收入统计规则确认。",
                            "final_security_level": "3",
                        }
                    }
                }
            },
        )
    )

    assert draft.status == "waiting_confirm"
    assert draft.need_confirm.type == "submit_activiti"
    assert draft.cards[0].type == "metadata_governance_draft"
    assert draft.cards[0].data["security_level"] == "L2"
    income = next(item for item in draft.cards[0].data["field_suggestions"] if item["field"] == "income_amt")
    assert income["suggested_cn_name"] == "客户统计收入金额"
    assert income["security_level"] == "3"

    submitted = demo_graph.run_confirm(
        ConfirmRequest(
            thread_id=draft.thread_id,
            task_id=draft.task_id,
            confirm_id=draft.need_confirm.confirm_id or "",
            confirmed=True,
            payload={"asset_id": "asset_001"},
        )
    )

    assert submitted.status == "completed"
    assert submitted.cards[0].type == "process_status"
    assert submitted.cards[0].data["process_instance_id"].startswith("ACT_")


def test_metadata_prefill_capability_can_start_directly() -> None:
    response = demo_graph.start_metadata_prefill(
        MetadataPrefillStartRequest(
            thread_id="T_META_PREFILL_TEST",
            asset_id="asset_001",
            table_name="dwd_customer_income_df",
            user_context=UserContext(user_id="zhangsan", user_name="张三"),
        )
    )

    assert response.status == "waiting_confirm"
    assert response.need_confirm.type == "confirm_metadata_prefill"
    assert response.cards[0].type == "metadata_prefill_review"
    fields = response.cards[0].data["fields"]
    mobile = next(item for item in fields if item["field_name"] == "mobile_no")
    assert mobile["recommended_security_level"] == "3"
    assert "安全扫描 Agent" in "\n".join(mobile["evidence"])
