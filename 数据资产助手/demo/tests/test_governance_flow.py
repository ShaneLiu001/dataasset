from app.core.response import ChatRequest, ConfirmRequest, UserContext
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

    draft = demo_graph.run_confirm(
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

    assert draft.status == "waiting_confirm"
    assert draft.need_confirm.type == "submit_activiti"
    assert draft.cards[0].type == "metadata_governance_draft"
    assert draft.cards[0].data["security_level"] == "L2"

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

