from app.core.response import ChatRequest, ConfirmRequest, UserContext
from app.graph.builder import demo_graph


def _request(question: str) -> ChatRequest:
    return ChatRequest(
        session_id="S_10002",
        thread_id="T_10002",
        question=question,
        user_context=UserContext(user_id="zhangsan", trace_id="trace-test-002"),
    )


def test_find_asset_flow() -> None:
    response = demo_graph.run_chat(_request("客户收入用哪张表？"))
    assert response.intent == "FIND_ASSET"
    assert response.status == "completed"
    assert response.cards[0].type == "asset_recommendation"


def test_lineage_flow() -> None:
    response = demo_graph.run_chat(_request("dwd_customer_income_df 的上游来源和加工任务说明是什么？"))
    assert response.intent == "QUERY_LINEAGE"
    assert response.status == "completed"
    assert response.cards[0].type == "lineage_summary"


def test_datasource_flow() -> None:
    response = demo_graph.run_chat(_request("帮我登记一个生产 MySQL 数据源，同时采集元数据并做安全扫描"))
    assert response.intent == "REGISTER_DATASOURCE"
    assert response.status == "waiting_confirm"
    assert response.need_confirm.type == "submit_datasource_register"
    assert response.cards[0].type == "datasource_register_form"

    submitted = demo_graph.run_confirm(
        ConfirmRequest(
            thread_id=response.thread_id,
            task_id=response.task_id,
            confirm_id=response.need_confirm.confirm_id or "",
            confirmed=True,
            payload={
                "datasource_name": "crm_prod_mysql",
                "datasource_type": "MySQL",
                "env": "PRD",
                "host": "10.12.8.21",
                "port": "3306",
                "owner": "zhangsan",
                "collect_metadata": True,
                "run_security_scan": True,
                "sync_data_map": True,
            },
        )
    )

    assert submitted.intent == "REGISTER_DATASOURCE"
    assert submitted.status == "running"
    assert submitted.cards[0].type == "datasource_status"
    assert submitted.cards[0].data["stage"] == "approval_pending"

    collecting = demo_graph.refresh_task(submitted.task_id)
    assert collecting is not None
    assert collecting.status == "running"
    assert collecting.cards[0].data["stage"] == "metadata_collecting"

    collected = demo_graph.refresh_task(submitted.task_id)
    assert collected is not None
    assert collected.status == "waiting_confirm"
    assert collected.need_confirm.type == "start_security_scan"
    assert collected.cards[0].data["stage"] == "metadata_collected"

    scanning = demo_graph.run_confirm(
        ConfirmRequest(
            thread_id=collected.thread_id,
            task_id=collected.task_id,
            confirm_id=collected.need_confirm.confirm_id or "",
            confirmed=True,
            payload={"run_security_scan": True},
        )
    )
    assert scanning.status == "running"
    assert scanning.cards[0].data["stage"] == "security_scanning"

    scanned = demo_graph.refresh_task(submitted.task_id)
    assert scanned is not None
    assert scanned.status == "waiting_confirm"
    assert scanned.need_confirm.type == "create_security_ticket"
    assert scanned.cards[0].data["stage"] == "security_scanned"

    ticket = demo_graph.run_confirm(
        ConfirmRequest(
            thread_id=scanned.thread_id,
            task_id=scanned.task_id,
            confirm_id=scanned.need_confirm.confirm_id or "",
            confirmed=True,
            payload={"create_ticket": True},
        )
    )
    assert ticket.status == "running"
    assert ticket.cards[0].data["stage"] == "security_ticket_pending"

    ready = demo_graph.refresh_task(submitted.task_id)
    assert ready is not None
    assert ready.status == "completed"
    assert ready.cards[0].data["stage"] == "data_ready"
