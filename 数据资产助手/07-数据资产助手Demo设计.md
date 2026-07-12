# 06 数据资产助手 Demo 设计

## 1. 结论

当前已经可以基于技术选型进入 Demo 设计和开发。

Demo 不建议一开始接生产 Oracle、GoldenDB、Elasticsearch、Activiti 和生产 Agent 网关，而是采用：

```text
HTML 交互原型
  -> Agent 网关 Mock
  -> FastAPI AI 助手服务
  -> LangGraph 编排
  -> Mock Tool Adapter
  -> 本地 JSON Mock 数据
  -> OpenTelemetry / Langfuse 预留埋点
```

首版 Demo 的目标不是覆盖全部数据资产能力，而是证明以下关键点：

1. 自然语言可以被识别为明确业务意图。
2. LangGraph 可以完成多步骤编排、用户确认和状态推进。
3. Tool Adapter 可以统一封装数据地图、血缘、标准、安全扫描、Activiti 等平台能力。
4. 写操作不会直接执行，必须先生成草案并等待用户确认。
5. 后续可以平滑替换 Mock Tool 为真实 Java API、ES、Activiti、Redis、GoldenDB。

## 2. Demo 范围

首版 Demo 建议采用“两条主链路 + 两个支撑查询”。

### 2.1 主链路一：单表元数据治理

用户输入：

```text
帮我治理 dwd_customer_income_df 这张表
```

演示流程：

```text
用户输入表名
  -> 数据准备专家调用元数据查询能力，查询同名表候选
  -> 用户二次确认唯一表
  -> 助手读取用户常用空间、项目、开发账号
  -> 用户确认或修改上下文
  -> 数据治理专家调用数据标准能力获取标准
  -> 数据治理专家调用血缘查询能力获取上游血缘和加工任务
  -> 数据治理专家调用数据安全专家或安全扫描能力获取安全等级
  -> 数据治理专家生成治理草案
  -> 用户确认
  -> Mock Activiti 返回流程实例 ID
```

演示价值：

1. 证明 Agent 编排不是简单问答，而是专家 Agent、多 Tool、多确认节点协同。
2. 证明 LangGraph 适合承接状态流转和人工确认。
3. 证明 Tool Adapter 可以先 Mock，后续替换真实接口。

### 2.2 主链路二：数据源登记后自动采集与安全扫描

用户输入：

```text
帮我登记一个生产 MySQL 数据源，同时采集元数据并做安全扫描
```

演示流程：

```text
用户输入登记诉求
  -> 数据准备专家识别数据源类型、环境、采集策略、安全扫描策略
  -> 打开数据源登记表单 Mock
  -> 用户提交登记
  -> Mock 登记审批办结
  -> 创建元数据采集任务
  -> 采集完成后同步 ES 数据地图
  -> 调用数据安全专家或安全扫描能力
  -> 返回敏感字段、安全等级和风险建议
  -> 生成安全等级确认工单
  -> 提示后续绑定空间项目
```

演示价值：

1. 证明数据准备专家可以作为数据资产助手的典型应用场景。
2. 证明专家 Agent 可以协同，但由编排层控制主流程。
3. 证明“登记、采集、扫描、工单”这类异步流程可以用任务状态持续跟踪。

### 2.3 支撑查询一：数据地图查表

用户输入：

```text
客户收入用哪张表？
```

演示流程：

```text
自然语言问题
  -> 数据地图 Mock Tool 搜索候选资产
  -> 返回表名、中文名、数据源 ID、schema、负责人、热度
  -> 血缘 / 标准 Mock Tool 补充推荐理由
  -> 返回推荐资产卡片
```

### 2.4 支撑查询二：血缘查询与 SQL 注释识别

用户输入：

```text
dwd_customer_income_df 的上游来源和加工任务说明是什么？
```

演示流程：

```text
定位表
  -> 调用血缘 Mock Tool 查询上游表
  -> 调用 SQL 任务 Mock Tool 获取加工任务代码
  -> LLM 识别 SQL 注释
  -> 生成目标表备注建议
```

## 3. 技术栈

| 层次 | 技术 | Demo 用法 |
| --- | --- | --- |
| 前端原型 | HTML / CSS / JavaScript | 已有交互原型，后续可对接 FastAPI |
| API 服务 | Python + FastAPI | 提供 `/assistant/chat`、`/assistant/confirm`、`/assistant/tasks/{task_id}` |
| Agent 编排 | LangGraph | 编排意图识别、路由、专家 Agent、工具调用、用户确认 |
| LLM 适配 | LangChain Core | Prompt、Runnable、Tool Calling、模型调用适配 |
| Tool 层 | Mock Tool Adapter | 模拟 ES、Java API、Activiti、安全扫描、数据标准、血缘 |
| 状态 | 内存 / 本地 JSON | Demo 阶段先不依赖 Redis 和 GoldenDB |
| 可观测 | 日志 + 预留 OTel / Langfuse Hook | 先生成 trace_id 和 tool_call 日志，后续接公司平台 |

## 4. 推荐代码目录

建议在 `数据资产助手/demo/` 下建设 Demo 工程：

```text
数据资产助手/demo/
  README.md
  pyproject.toml
  app/
    main.py
    api/
      assistant.py
    core/
      config.py
      context.py
      response.py
      observability.py
    graph/
      state.py
      builder.py
      nodes.py
    agents/
      data_map.py
      datasource.py
      lineage.py
      governance.py
      standard.py
      security_scan.py
    tools/
      registry.py
      data_map_tool.py
      metadata_tool.py
      standard_tool.py
      lineage_tool.py
      security_scan_tool.py
      datasource_tool.py
      activiti_tool.py
      memory_tool.py
    mock_data/
      assets.json
      lineage.json
      standards.json
      security_scan.json
      datasource_tasks.json
      user_preferences.json
    tests/
      test_governance_flow.py
      test_datasource_flow.py
```

## 5. API 草案

### 5.1 对话接口

```http
POST /assistant/chat
```

请求：

```json
{
  "session_id": "S_10001",
  "thread_id": "T_10001",
  "question": "帮我治理 dwd_customer_income_df 这张表",
  "user_context": {
    "user_id": "zhangsan",
    "user_name": "张三",
    "org_id": "data_center",
    "role_codes": ["data_steward"],
    "trace_id": "trace-demo-001",
    "access_token": "mock-token"
  }
}
```

响应：

```json
{
  "task_id": "TASK_10001",
  "thread_id": "T_10001",
  "intent": "GOVERN_METADATA",
  "answer": "找到 3 张同名表，请确认要治理哪一张。",
  "cards": [],
  "need_confirm": true,
  "confirm_id": "CONFIRM_10001",
  "next_actions": ["confirm_asset"],
  "trace_id": "trace-demo-001"
}
```

### 5.2 用户确认接口

```http
POST /assistant/confirm
```

请求：

```json
{
  "thread_id": "T_10001",
  "task_id": "TASK_10001",
  "confirm_id": "CONFIRM_10001",
  "confirmed": true,
  "payload": {
    "asset_id": "asset_001",
    "space_id": "space_finance",
    "project_id": "project_dwd",
    "dev_account": "dev_zhangsan"
  }
}
```

### 5.3 任务状态接口

```http
GET /assistant/tasks/{task_id}
```

返回任务当前节点、步骤状态、已调用 Tool、待确认事项和模拟流程实例 ID。

## 6. LangGraph 状态设计

Demo 状态建议先采用一个统一 State：

```json
{
  "thread_id": "",
  "task_id": "",
  "user_context": {},
  "question": "",
  "intent": "",
  "slots": {},
  "selected_asset": {},
  "user_preferences": {},
  "evidence": {
    "standards": [],
    "lineage": [],
    "security_scan": []
  },
  "draft": {},
  "confirm": {
    "required": false,
    "confirm_id": "",
    "type": "",
    "payload": {}
  },
  "tool_calls": [],
  "messages": [],
  "status": "running"
}
```

## 7. Tool 清单

| Tool | Demo 作用 | 是否首版必做 |
| --- | --- | --- |
| search_data_map_tool | 查询同名表和候选资产 | 是 |
| get_asset_detail_tool | 获取表字段、负责人、备注 | 是 |
| get_user_common_context_tool | 获取常用空间、项目、开发账号 | 是 |
| save_user_common_context_tool | 保存常用上下文 | 可选 |
| get_data_standard_tool | 返回字段标准和命名建议 | 是 |
| query_upstream_lineage_tool | 返回上游表和加工任务 | 是 |
| get_sql_task_detail_tool | 返回 SQL 加工任务代码和注释 | 是 |
| extract_sql_comment_tool | 从 SQL 注释生成目标表备注 | 是 |
| scan_security_level_tool | 返回安全等级和敏感字段 | 是 |
| draft_metadata_governance_tool | 生成元数据治理草案 | 是 |
| submit_activiti_process_tool | 返回 Mock 流程实例 ID | 是 |
| create_datasource_register_tool | 返回 Mock 数据源登记流程号 | 是 |
| create_metadata_collect_task_tool | 返回 Mock 元数据采集任务号 | 是 |
| create_security_scan_task_tool | 调用安全扫描能力并返回扫描任务号 | 是 |
| query_process_status_tool | 查询 Mock 流程状态 | 可选 |

## 8. Mock 数据缺口

Demo 开发前需要补齐以下 Mock 数据：

| 数据文件 | 需要内容 | 当前建议 |
| --- | --- | --- |
| assets.json | 同名表候选、字段列表、schema、数据源 ID、负责人、中文名、备注 | 至少 3 张同名表 |
| standards.json | 字段标准、中文名建议、码值标准、命名规则 | 覆盖客户、收入、手机号、日期字段 |
| lineage.json | 上游表、加工任务、SQL 片段、下游报表 | 覆盖 `dwd_customer_income_df` |
| security_scan.json | 敏感字段、安全等级、脱敏策略、风险建议 | 覆盖手机号、证件号、收入金额 |
| datasource_tasks.json | 数据源登记、审批、采集、扫描、工单状态 | 覆盖 PRD MySQL 数据源 |
| user_preferences.json | 常用空间、项目、开发账号 | 覆盖 `zhangsan` |

## 9. 目前还缺什么

### 9.1 不影响 Mock Demo 启动，但需要补齐

1. Demo 代码工程尚未创建。
2. Mock 数据 JSON 尚未落文件。
3. 交互原型尚未对接 FastAPI，只是前端静态交互。
4. LangGraph 节点边界还需要落实到代码，包括等待确认、恢复执行、写操作提交。
5. 统一响应结构、卡片结构、错误结构还需要定稿。
6. 日志脱敏规则需要形成代码级清单。

推荐实现方式如下：

| 待办项 | 推荐实现方式 | 首版取舍 |
| --- | --- | --- |
| Demo 代码工程尚未创建 | 在 `数据资产助手/demo/` 下新建独立 Python 工程，使用 FastAPI + LangGraph + 本地 Mock Tool；不要混入现有文档目录逻辑 | 先做可本地启动的最小工程，不接真实 Agent 网关、Redis、GoldenDB |
| Mock 数据 JSON 尚未落文件 | 按业务对象拆分为 `assets.json`、`standards.json`、`lineage.json`、`security_scan.json`、`datasource_tasks.json`、`user_preferences.json` | 数据量少但字段完整，每类保留 2 到 3 条样例，优先覆盖演示链路 |
| 交互原型尚未对接 FastAPI | 保留当前 HTML 原型，新增 `apiClient` 封装，优先对接 `/assistant/chat`、`/assistant/confirm`、`/assistant/tasks/{task_id}` | 不引入 React / Vue，避免 Demo 前端工程化成本过高 |
| LangGraph 节点边界还需要落实到代码 | 按“意图识别 -> 路由 -> 专家 Agent 节点 -> Tool 调用 -> 确认节点 -> 写操作执行 -> 结果生成”拆节点 | 首版可以用规则识别意图，不强依赖真实大模型；保留 LLM 适配接口 |
| 统一响应结构、卡片结构、错误结构还需要定稿 | 定义统一 `AssistantResponse`、`Card`、`Action`、`NeedConfirm`、`ToolCallAudit` 结构，所有节点返回同一格式 | 卡片类型先覆盖候选表、治理草案、流程状态、数据源任务四类 |
| 日志脱敏规则需要形成代码级清单 | 新建 `core/sanitizer.py`，对 token、密码、手机号、身份证号、数据库连接串、连接 Host 等字段做脱敏；日志和 mock Langfuse 输出统一走脱敏函数 | 首版只做规则脱敏和字段名黑名单，不做复杂 DLP 检测 |

建议按以下工程顺序处理：

```text
1. 先创建 demo 工程骨架和启动脚本
2. 再落 Mock 数据和 Tool Registry
3. 然后实现统一响应结构
4. 再实现 LangGraph 单表元数据治理主链路
5. 接着实现 confirm 恢复执行逻辑
6. 最后把 HTML 原型接入 FastAPI
```

首版 Demo 可以先把 Redis、GoldenDB、真实 Agent 网关、真实 Langfuse 都替换成本地内存和日志输出，只要代码里保留替换点即可。

### 9.2 接真实接口前必须确认

1. Agent 网关转发 FastAPI 的 Header / Cookie / Body 规范。
2. token 类型、有效期、刷新机制。
3. 数据地图搜索接口是直接查 ES，还是调用平台 Java 搜索接口。
4. 元数据详情、数据标准、血缘、安全扫描、Activiti 的真实接口地址、入参、出参和负责人。
5. Activiti 是否支持以用户 token 作为流程发起人。
6. 助手库表是否使用独立 GoldenDB schema，以及表名前缀、字段规范。
7. Langfuse 中哪些字段禁止记录明文。

### 9.3 需要先统一的产品口径

1. 首版 Demo 是优先演示“单表元数据治理”，还是优先演示“数据源登记后采集与安全扫描”。
2. 写操作确认卡片需要展示哪些字段才算满足审计要求。
3. 数据源登记表单是弹窗承载、侧边栏承载，还是跳转现有页面。
4. 安全等级确认工单是否属于数据源登记流程的一部分，还是独立安全流程。

## 10. 建议实施顺序

```text
第 1 步：创建 FastAPI Demo 骨架
第 2 步：落 Mock 数据和 Tool Registry
第 3 步：实现单表元数据治理 LangGraph
第 4 步：实现数据源登记、元数据采集、安全扫描状态推进
第 5 步：把 HTML 原型接到 FastAPI
第 6 步：补 trace_id、tool_call 日志和脱敏
第 7 步：整理 README、启动命令和演示脚本
```

建议先实现“单表元数据治理”作为第一条端到端链路，因为它最能体现数据地图、标准、血缘、安全扫描、Activiti 和人工确认的综合编排价值；随后补“数据源登记后采集与安全扫描”，用于展示数据准备专家如何并入数据资产助手。
