from __future__ import annotations

from uuid import uuid4

from app.agents.data_map import build_asset_recommendation, build_candidate_card
from app.agents.datasource import build_datasource_form_card, build_datasource_status_card
from app.agents.governance import build_governance_card, build_governance_draft
from app.agents.lineage import build_lineage_card, collect_lineage
from app.agents.security_scan import collect_security_scan
from app.agents.standard import collect_standards
from app.core.response import AssistantResponse, Card, ChatRequest, ConfirmRequest, NeedConfirm
from app.core.store import store
from app.graph.nodes import classify_intent, extract_table_name
from app.graph.state import GraphState
from app.tools.registry import ToolRegistry


def new_task_id() -> str:
    return f"TASK_{uuid4().hex[:10].upper()}"


def new_confirm_id() -> str:
    return f"CONFIRM_{uuid4().hex[:10].upper()}"


class DemoGraph:
    """LangGraph-style orchestration.

    The demo keeps node boundaries explicit so it can be migrated to
    langgraph.StateGraph without changing tools, agents, or API schemas.
    """

    def run_chat(self, request: ChatRequest) -> AssistantResponse:
        tools = ToolRegistry()
        state = GraphState(
            thread_id=request.thread_id,
            task_id=new_task_id(),
            question=request.question,
            user_context=request.user_context,
        )
        state.intent = classify_intent(request.question)

        if state.intent == "GOVERN_METADATA":
            self._start_governance(state, tools)
        elif state.intent == "REGISTER_DATASOURCE":
            self._start_datasource(state, tools)
        elif state.intent == "QUERY_LINEAGE":
            state.cards.append(build_lineage_card("asset_001", tools))
            state.answer = "已查询上游血缘、加工任务和 SQL 注释，生成目标表备注建议。"
            state.status = "completed"
        elif state.intent == "FIND_ASSET":
            state.cards.append(build_asset_recommendation(request.question, tools))
            state.answer = "建议优先使用 dwd_customer_income_df。"
            state.status = "completed"
        else:
            state.answer = "暂未识别该诉求。Demo 当前支持查表、血缘、数据源登记和单表元数据治理。"
            state.status = "completed"

        store.save_task(state.task_id, state.model_dump())
        return self._to_response(state, tools)

    def run_confirm(self, request: ConfirmRequest) -> AssistantResponse:
        saved = store.get_confirm(request.confirm_id)
        tools = ToolRegistry()
        if not saved:
            return AssistantResponse(
                task_id=request.task_id,
                thread_id=request.thread_id,
                intent="UNKNOWN",
                status="failed",
                answer="未找到待确认任务，可能已过期。",
                trace_id="trace-demo",
            )

        state = GraphState(**saved)
        if not request.confirmed:
            state.status = "completed"
            state.answer = "已取消本次确认，未提交任何写操作。"
            state.need_confirm = NeedConfirm(required=False)
            return self._to_response(state, tools)

        if state.need_confirm.type == "confirm_asset":
            self._continue_governance_after_asset_confirm(state, request.payload, tools)
        elif state.need_confirm.type == "submit_activiti":
            self._submit_governance_process(state, request.payload, tools)
        elif state.need_confirm.type == "submit_datasource_register":
            self._submit_datasource_register(state, request.payload, tools)
        elif state.need_confirm.type == "start_security_scan":
            self._start_security_scan(state, request.payload, tools)
        elif state.need_confirm.type == "create_security_ticket":
            self._create_security_ticket(state, request.payload, tools)
        else:
            state.status = "failed"
            state.answer = "未知确认类型。"

        store.save_task(state.task_id, state.model_dump())
        return self._to_response(state, tools)

    def refresh_task(self, task_id: str) -> AssistantResponse | None:
        saved = store.get_task(task_id)
        if not saved:
            return None
        tools = ToolRegistry()
        state = GraphState(**saved)
        if state.intent == "REGISTER_DATASOURCE":
            self._refresh_datasource(state, tools)
        else:
            state.answer = "当前任务暂无可刷新的后台状态。"
        store.save_task(state.task_id, state.model_dump())
        return self._to_response(state, tools)

    def _start_governance(self, state: GraphState, tools: ToolRegistry) -> None:
        table_name = extract_table_name(state.question)
        state.slots["table_name"] = table_name
        candidate_card = build_candidate_card(table_name, tools)
        confirm_id = new_confirm_id()
        state.cards.append(candidate_card)
        state.need_confirm = NeedConfirm(
            required=True,
            confirm_id=confirm_id,
            type="confirm_asset",
            payload={"table_name": table_name},
        )
        state.next_actions = ["confirm_asset"]
        state.status = "waiting_confirm"
        state.answer = f"找到 {len(candidate_card.data['candidates'])} 张同名表，请确认要治理哪一张。"
        store.save_confirm(confirm_id, state.model_dump())

    def _continue_governance_after_asset_confirm(self, state: GraphState, payload: dict, tools: ToolRegistry) -> None:
        asset_id = payload.get("asset_id", "asset_001")
        asset = tools.call("get_asset_detail_tool", asset_id=asset_id)
        if not asset:
            state.status = "failed"
            state.answer = "未找到选定资产。"
            return
        context = tools.call("get_user_common_context_tool", user_id=state.user_context.user_id)
        context.update({key: value for key, value in payload.items() if key in {"space_id", "project_id", "dev_account"}})
        standards = collect_standards(asset, tools)
        lineage = collect_lineage(asset_id, tools)
        security = collect_security_scan(asset_id, tools)
        draft = build_governance_draft(asset, standards, lineage, security, context)
        card = build_governance_card(draft)
        confirm_id = new_confirm_id()

        state.selected_asset = asset
        state.user_preferences = context
        state.evidence = draft["evidence"]
        state.draft = draft
        state.cards = [card]
        state.need_confirm = NeedConfirm(
            required=True,
            confirm_id=confirm_id,
            type="submit_activiti",
            payload={"asset_id": asset_id, "draft": draft},
        )
        state.next_actions = ["submit_activiti", "edit_draft"]
        state.status = "waiting_confirm"
        state.answer = "已汇总数据标准、上游血缘、SQL 注释和安全扫描结果，生成元数据治理草案。"
        store.save_confirm(confirm_id, state.model_dump())

    def _submit_governance_process(self, state: GraphState, payload: dict, tools: ToolRegistry) -> None:
        submit_payload = {**state.draft, **payload}
        result = tools.call("submit_activiti_process_tool", task_id=state.task_id, payload=submit_payload)
        state.cards = [
            Card(
                type="process_status",
                title="Activiti 流程已提交",
                data=result,
            )
        ]
        state.need_confirm = NeedConfirm(required=False)
        state.next_actions = ["query_process_status"]
        state.status = "completed"
        state.answer = f"已提交单表元数据治理流程，流程实例：{result['process_instance_id']}。"

    def _start_datasource(self, state: GraphState, tools: ToolRegistry) -> None:
        confirm_id = new_confirm_id()
        form_card = build_datasource_form_card()
        state.cards.append(form_card)
        state.need_confirm = NeedConfirm(
            required=True,
            confirm_id=confirm_id,
            type="submit_datasource_register",
            payload=form_card.data["form"],
        )
        state.status = "waiting_confirm"
        state.answer = "我已打开数据源登记表单，请补充连接信息并确认是否立即采集元数据、是否执行安全扫描。"
        state.next_actions = ["submit_datasource_register"]
        store.save_confirm(confirm_id, state.model_dump())

    def _submit_datasource_register(self, state: GraphState, payload: dict, tools: ToolRegistry) -> None:
        state.slots["datasource_form"] = payload
        state.slots["datasource_stage"] = "approval_pending"
        state.slots["register_process_id"] = "DS_REG_20260703_0021"
        state.cards = [
            build_datasource_status_card(
                "approval_pending",
                {
                    "datasource": payload,
                    "register_process_id": state.slots["register_process_id"],
                    "message": "数据源登记流程已提交，当前等待审批。",
                },
            )
        ]
        state.need_confirm = NeedConfirm(required=False)
        state.status = "running"
        state.answer = "数据源登记表单已确认提交，当前流程审批中。你可以点击刷新按钮查看审批状态。"
        state.next_actions = ["refresh_datasource_status"]

    def _refresh_datasource(self, state: GraphState, tools: ToolRegistry) -> None:
        stage = state.slots.get("datasource_stage")
        form = state.slots.get("datasource_form", {})
        if stage == "approval_pending":
            collect = tools.call("create_metadata_collect_task_tool")
            state.slots["datasource_stage"] = "metadata_collecting"
            state.slots["metadata_collect_task_id"] = collect["metadata_collect_task_id"]
            state.cards = [
                build_datasource_status_card(
                    "metadata_collecting",
                    {
                        "datasource": form,
                        "register_process_id": state.slots.get("register_process_id"),
                        "metadata_collect_task_id": collect["metadata_collect_task_id"],
                        "message": "数据源登记流程已办结，智能体已继续发起元数据采集。",
                    },
                )
            ]
            state.status = "running"
            state.answer = "数据源登记审批已结束。下一步开始元数据采集，当前元数据正在采集中。"
            state.next_actions = ["refresh_datasource_status"]
        elif stage == "metadata_collecting":
            confirm_id = new_confirm_id()
            state.slots["datasource_stage"] = "metadata_collected"
            state.cards = [
                build_datasource_status_card(
                    "metadata_collected",
                    {
                        "datasource": form,
                        "metadata_collect_task_id": state.slots.get("metadata_collect_task_id"),
                        "message": "元数据采集已完成，数据地图索引已同步。",
                    },
                )
            ]
            state.need_confirm = NeedConfirm(
                required=True,
                confirm_id=confirm_id,
                type="start_security_scan",
                payload={"run_security_scan": True},
            )
            state.status = "waiting_confirm"
            state.answer = "元数据采集已完成。是否立即进行安全扫描？"
            state.next_actions = ["start_security_scan"]
            store.save_confirm(confirm_id, state.model_dump())
        elif stage == "security_scanning":
            confirm_id = new_confirm_id()
            state.slots["datasource_stage"] = "security_scanned"
            state.cards = [
                build_datasource_status_card(
                    "security_scanned",
                    {
                        "datasource": form,
                        "security_scan_task_id": state.slots.get("security_scan_task_id"),
                        "security_level": "L2",
                        "sensitive_fields": ["mobile_no", "income_amt"],
                        "message": "安全扫描已完成，识别敏感字段并建议安全等级 L2。",
                    },
                )
            ]
            state.need_confirm = NeedConfirm(
                required=True,
                confirm_id=confirm_id,
                type="create_security_ticket",
                payload={"create_ticket": True},
            )
            state.status = "waiting_confirm"
            state.answer = "安全扫描已完成。是否立即发起元数据及安全等级确认工单？"
            state.next_actions = ["create_security_ticket"]
            store.save_confirm(confirm_id, state.model_dump())
        elif stage == "security_ticket_pending":
            state.slots["datasource_stage"] = "data_ready"
            state.cards = [
                build_datasource_status_card(
                    "data_ready",
                    {
                        "datasource": form,
                        "security_ticket_id": state.slots.get("security_ticket_id"),
                        "message": "安全等级确认工单已处理完成，数据准备完成。",
                    },
                )
            ]
            state.need_confirm = NeedConfirm(required=False)
            state.status = "completed"
            state.answer = "安全等级确认工单已处理完成，数据准备已完成。现在可以进行数据开发或者数据同步了。"
            state.next_actions = ["start_data_development", "start_data_sync"]
        else:
            state.answer = "当前数据源任务状态无需刷新。"

    def _start_security_scan(self, state: GraphState, payload: dict, tools: ToolRegistry) -> None:
        scan = tools.call("create_security_scan_task_tool")
        state.slots["datasource_stage"] = "security_scanning"
        state.slots["security_scan_task_id"] = scan["security_scan_task_id"]
        form = state.slots.get("datasource_form", {})
        state.cards = [
            build_datasource_status_card(
                "security_scanning",
                {
                    "datasource": form,
                    "security_scan_task_id": scan["security_scan_task_id"],
                    "message": "安全扫描任务已创建，当前扫描中。",
                },
            )
        ]
        state.need_confirm = NeedConfirm(required=False)
        state.status = "running"
        state.answer = "已开始自动安全扫描，当前处于安全扫描中。你可以点击刷新按钮查看扫描结果。"
        state.next_actions = ["refresh_datasource_status"]

    def _create_security_ticket(self, state: GraphState, payload: dict, tools: ToolRegistry) -> None:
        state.slots["datasource_stage"] = "security_ticket_pending"
        state.slots["security_ticket_id"] = "SEC_LEVEL_20260703_0042"
        form = state.slots.get("datasource_form", {})
        state.cards = [
            build_datasource_status_card(
                "security_ticket_pending",
                {
                    "datasource": form,
                    "security_ticket_id": state.slots["security_ticket_id"],
                    "message": "已生成元数据及安全等级确认工单，等待用户处理。",
                },
            )
        ]
        state.need_confirm = NeedConfirm(required=False)
        state.status = "running"
        state.answer = "已生成元数据及安全等级确认工单，请处理工单。处理完成后点击刷新，我会继续确认数据准备状态。"
        state.next_actions = ["refresh_datasource_status"]

    def _to_response(self, state: GraphState, tools: ToolRegistry) -> AssistantResponse:
        return AssistantResponse(
            task_id=state.task_id,
            thread_id=state.thread_id,
            intent=state.intent,
            status=state.status,  # type: ignore[arg-type]
            answer=state.answer,
            cards=state.cards,
            need_confirm=state.need_confirm,
            next_actions=state.next_actions,
            tool_calls=tools.audit,
            trace_id=state.user_context.trace_id,
        )


demo_graph = DemoGraph()
