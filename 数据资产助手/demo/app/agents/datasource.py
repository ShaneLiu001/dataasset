from __future__ import annotations

from app.core.response import Action, Card
from app.tools.registry import ToolRegistry


def build_datasource_form_card(defaults: dict | None = None) -> Card:
    defaults = defaults or {}
    form = {
        "datasource_name": defaults.get("datasource_name", "crm_prod_mysql"),
        "datasource_type": defaults.get("datasource_type", "MySQL"),
        "env": defaults.get("env", "PRD"),
        "host": defaults.get("host", "10.12.8.21"),
        "port": defaults.get("port", "3306"),
        "owner": defaults.get("owner", "zhangsan"),
        "collect_metadata": defaults.get("collect_metadata", True),
        "run_security_scan": defaults.get("run_security_scan", True),
        "sync_data_map": defaults.get("sync_data_map", True),
    }
    return Card(
        type="datasource_register_form",
        title="数据源登记表单",
        data={"form": form},
        actions=[
            Action(code="submit_datasource_register", label="提交登记并二次确认", payload=form),
        ],
    )


def build_datasource_task_card(tools: ToolRegistry, form: dict | None = None) -> Card:
    form = form or {}
    register = tools.call("create_datasource_register_tool")
    collect = tools.call("create_metadata_collect_task_tool")
    scan = tools.call("create_security_scan_task_tool")
    return Card(
        type="datasource_prepare_task",
        title="数据源登记、元数据采集与安全扫描",
        data={
            "register": register,
            "metadata_collect": collect,
            "security_scan": scan,
            "submitted_form": form,
            "steps": [
                {"name": "数据源登记", "status": "submitted"},
                {"name": "元数据采集", "status": "running"},
                {"name": "安全扫描", "status": "waiting_metadata"},
            ],
        },
    )


def build_datasource_status_card(stage: str, data: dict) -> Card:
    titles = {
        "approval_pending": "数据源登记审批中",
        "metadata_collecting": "元数据采集中",
        "metadata_collected": "元数据采集完成",
        "security_scanning": "安全扫描中",
        "security_scanned": "安全扫描完成",
        "security_ticket_pending": "安全等级确认工单处理中",
        "data_ready": "数据准备完成",
    }
    step_map = {
        "approval_pending": [
            {"name": "数据源登记", "status": "审批中"},
            {"name": "元数据采集", "status": "待开始"},
            {"name": "安全扫描", "status": "待开始"},
            {"name": "安全等级确认", "status": "待开始"},
            {"name": "数据准备完成", "status": "待开始"},
        ],
        "metadata_collecting": [
            {"name": "数据源登记", "status": "审批通过"},
            {"name": "元数据采集", "status": "采集中"},
            {"name": "安全扫描", "status": "待用户确认"},
            {"name": "安全等级确认", "status": "待开始"},
            {"name": "数据准备完成", "status": "待开始"},
        ],
        "metadata_collected": [
            {"name": "数据源登记", "status": "审批通过"},
            {"name": "元数据采集", "status": "已完成"},
            {"name": "安全扫描", "status": "等待确认是否立即执行"},
            {"name": "安全等级确认", "status": "待开始"},
            {"name": "数据准备完成", "status": "待开始"},
        ],
        "security_scanning": [
            {"name": "数据源登记", "status": "审批通过"},
            {"name": "元数据采集", "status": "已完成"},
            {"name": "安全扫描", "status": "扫描中"},
            {"name": "安全等级确认", "status": "待开始"},
            {"name": "数据准备完成", "status": "待开始"},
        ],
        "security_scanned": [
            {"name": "数据源登记", "status": "审批通过"},
            {"name": "元数据采集", "status": "已完成"},
            {"name": "安全扫描", "status": "已完成"},
            {"name": "安全等级确认", "status": "等待确认是否生成工单"},
            {"name": "数据准备完成", "status": "待开始"},
        ],
        "security_ticket_pending": [
            {"name": "数据源登记", "status": "审批通过"},
            {"name": "元数据采集", "status": "已完成"},
            {"name": "安全扫描", "status": "已完成"},
            {"name": "安全等级确认", "status": "工单处理中"},
            {"name": "数据准备完成", "status": "待开始"},
        ],
        "data_ready": [
            {"name": "数据源登记", "status": "审批通过"},
            {"name": "元数据采集", "status": "已完成"},
            {"name": "安全扫描", "status": "已完成"},
            {"name": "安全等级确认", "status": "已完成"},
            {"name": "数据准备完成", "status": "已完成"},
        ],
    }
    return Card(
        type="datasource_status",
        title=titles.get(stage, "数据源登记状态"),
        data={"stage": stage, "steps": step_map.get(stage, []), **data},
    )
