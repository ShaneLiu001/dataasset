# 数据准备专家详细技术设计方案

## 1. 文档定位

本文档是在《数据准备专家需求文档》《数据准备专家交互设计说明》《数据准备专家架构设计文档》基础上进一步落地的详细技术设计，目标是明确：

1. 服务拆分与工程结构。
2. 前后端框架与组件版本基线。
3. 大模型、Agent、MCP 工具的实现方式。
4. 状态机、数据表、接口契约和事件协议。
5. 异步流程、补偿机制、权限安全和可观测性。
6. 一期可落地的开发边界和实施计划。

本文档中的版本为建议基线，优先满足“稳定、易运维、企业内可落地”。如果公司已有统一技术栈、脚手架、网关、流程平台 SDK 或中间件版本，应以公司基线为准，并将本文档中的组件映射到公司标准组件。

## 2. 技术选型总览

### 2.1 推荐技术栈

| 层级 | 推荐组件 | 建议版本 | 说明 |
| --- | --- | --- | --- |
| 前端框架 | React | 19.1.x | 智能助手工作台、进度卡片、弹窗容器 |
| 前端构建 | Vite | 7.x | 快速构建和本地开发 |
| 前端语言 | TypeScript | 5.8.x 或 5.9.x | 强类型约束 |
| UI 组件 | Ant Design | 5.26.x | 企业后台表单、弹窗、步骤条、表格 |
| 状态管理 | Zustand | 5.x | 会话态和进度卡片轻量状态 |
| 请求库 | Axios | 1.10.x | REST API 调用 |
| 服务端语言 | Java | 21 LTS | 企业后端主语言 |
| 服务端框架 | Spring Boot | 3.5.x | 主业务服务、编排服务、MCP 网关 |
| 微服务治理 | Spring Cloud | 2025.0.x | 配置、注册、网关、熔断按公司基线接入 |
| ORM | MyBatis-Plus | 3.5.x | 状态表、事件表、审计表 |
| 数据库 | MySQL | 8.0.x 或 8.4 LTS | 任务状态、事件、工具调用日志 |
| 缓存 | Redis | 7.2.x 或 7.4.x | 会话缓存、分布式锁、短期状态 |
| 消息队列 | Kafka | 3.8.x | 事件流、异步状态推进 |
| 定时调度 | XXL-JOB | 2.4.x | 轮询、补偿、超时提醒 |
| 搜索与日志 | Elasticsearch | 8.15.x 或公司统一版本 | 工具调用日志、审计检索 |
| 可观测性 | OpenTelemetry Java Agent | 2.x | Trace、Metric、Log 关联 |
| 指标监控 | Prometheus + Grafana | Prometheus 2.54.x / Grafana 11.x | 服务指标和业务指标 |
| 容器运行 | Kubernetes | 1.30+ | 服务部署、弹性伸缩 |
| 大模型接入 | 本地大模型网关 | 企业内部版本 | 统一封装模型鉴权、限流、审计和协议适配 |
| 模型推理服务 | vLLM 或 SGLang | vLLM 0.10.x / SGLang 0.4.x | 本地部署开源模型，提供类 Chat Completions 协议 |
| 主模型 | DeepSeek V4 Pro | `deepseek-v4-pro` | 复杂编排、工具选择、用户反馈生成 |
| 轻量策略 | DeepSeek V4 Pro 小参数配置 | `deepseek-v4-pro` | 一期不额外引入小模型，通过低 token、低温度、短上下文降低成本 |

### 2.2 一期推荐架构形态

一期建议采用“模块化单体 + 独立前端”的方式落地，避免过早拆分带来联调成本。

```text
data-prepare-web
  智能助手前端、进度卡片、弹窗容器

data-prepare-service
  会话模块
  意图识别模块
  编排状态机模块
  MCP 工具网关模块
  事件监听模块
  调度补偿模块
  权限审计模块
```

如果公司微服务治理成熟，也可以在一期拆为：

```text
data-prepare-conversation-service
data-prepare-orchestrator-service
data-prepare-mcp-gateway-service
data-prepare-event-service
data-prepare-scheduler-service
```

建议一期代码内先按模块边界组织，后续再按流量和团队边界拆服务。

## 3. 工程结构设计

### 3.1 前端工程结构

```text
data-prepare-web/
  src/
    api/
      conversation.ts
      process.ts
      event.ts
    components/
      AssistantShell/
      ProgressCard/
      ProcessTimeline/
      DatasourceRegisterModal/
      SpaceBindingModal/
      ActionBar/
      StatusBadge/
    pages/
      DataPrepareWorkspace.tsx
    stores/
      conversationStore.ts
      processStore.ts
    types/
      process.ts
      event.ts
      conversation.ts
    utils/
      statusMapper.ts
      format.ts
```

核心页面只保留一个工作台：

```text
/data-prepare/expert
```

页面内通过状态驱动展示：

1. 对话消息区。
2. 数据准备进度卡片。
3. 登记页面弹窗。
4. 空间项目绑定弹窗。
5. 安全等级确认入口。
6. 后续操作入口。

### 3.2 后端工程结构

```text
data-prepare-service/
  src/main/java/com/company/dataprepare/
    DataPrepareApplication.java
    conversation/
      ConversationController.java
      ConversationService.java
      IntentClassifier.java
      SlotExtractor.java
      LlmClient.java
    orchestrator/
      OrchestratorController.java
      ProcessOrchestrator.java
      StateMachineEngine.java
      NextActionResolver.java
      ReadyForUseEvaluator.java
    mcp/
      McpToolController.java
      McpToolRegistry.java
      DatasourceRegisterTool.java
      ConnectivityTool.java
      FirewallTool.java
      MetadataTool.java
      SecurityScanTool.java
      SpaceBindingTool.java
    event/
      EventCallbackController.java
      ProcessEventConsumer.java
      EventNormalizer.java
      EventDispatcher.java
    scheduler/
      PollingJob.java
      RetryJob.java
      TimeoutNotifyJob.java
    domain/
      DataPrepareProcess.java
      DataSourceSubTask.java
      ProcessEvent.java
      ToolInvocationLog.java
    repository/
      DataPrepareProcessMapper.java
      DataSourceSubTaskMapper.java
      ProcessEventMapper.java
      ToolInvocationLogMapper.java
    security/
      UserContext.java
      PermissionChecker.java
      SensitiveDataMasker.java
    integration/
      workflow/
      datasource/
      metadata/
      firewall/
      securityscan/
      spacebinding/
    common/
      ApiResult.java
      ErrorCode.java
      IdempotencyKey.java
      TraceContext.java
```

## 4. 大模型与 Agent 设计

### 4.1 模型选择

当前项目不能使用 GPT 或外部闭源大模型，统一采用本地部署的开源 `deepseek-v4-pro`。模型通过企业内部大模型网关接入，网关负责协议适配、鉴权、限流、审计、日志脱敏和推理服务路由。

一期建议只引入一个主模型，避免多模型评测和路由复杂度过高。不同场景通过不同推理参数控制成本、延迟和输出稳定性。

推荐模型路由：

| 场景 | 模型 | temperature | max_tokens | 说明 |
| --- | --- | --- | --- | --- |
| 主对话编排 | `deepseek-v4-pro` | 0.2 | 2048 | 用户多轮对话、复杂状态解释、工具候选生成 |
| 复杂异常诊断 | `deepseek-v4-pro` | 0.1 | 3072 | 多系统失败、状态不一致、补偿建议 |
| 意图识别 | `deepseek-v4-pro` | 0 | 512 | 登记、采集、扫描、绑定、查询进度分类 |
| 槽位提取 | `deepseek-v4-pro` | 0 | 1024 | 数据源类型、环境、是否立即扫描等结构化抽取 |
| 固定模板回复 | 不调用模型 | - | - | 审批等待、任务完成、超时提醒等确定性反馈 |
| 高风险写操作前解释 | `deepseek-v4-pro` | 0.1 | 1024 | 发起防火墙、创建工单、提交绑定流程前生成确认文案 |

### 4.1.1 本地模型部署建议

推荐通过“推理服务 + 模型网关”的方式部署。

```text
data-prepare-service
  |
  v
企业大模型网关
  |  鉴权、限流、审计、协议适配、日志脱敏
  v
deepseek-v4-pro 推理服务
  |  vLLM / SGLang
  v
GPU 节点
```

推理服务建议：

| 项目 | 建议 |
| --- | --- |
| 推理框架 | vLLM 0.10.x 或 SGLang 0.4.x |
| 服务协议 | 类 Chat Completions 协议 |
| 部署方式 | Kubernetes GPU 节点或独立 GPU 服务器 |
| 精度策略 | 优先 BF16；资源紧张时评估量化方案 |
| 上下文长度 | 一期建议限制 16k-32k，超长上下文通过摘要压缩 |
| 并发控制 | 模型网关按用户、应用、租户限流 |
| 日志策略 | 不记录原始敏感字段，落库前脱敏 |

如果公司已有统一模型平台，应优先接入公司模型平台，不在数据准备专家内直接管理 GPU 和模型权重。

### 4.1.2 模型接口契约

数据准备专家后端不直接依赖某个推理框架 SDK，而是统一调用企业大模型网关。网关建议提供类 Chat Completions 的 HTTP 接口，便于未来替换模型或推理框架。

请求示例：

```json
{
  "model": "deepseek-v4-pro",
  "messages": [
    {
      "role": "system",
      "content": "你是数据准备专家..."
    },
    {
      "role": "user",
      "content": "帮我登记一个生产 MySQL 数据源"
    }
  ],
  "temperature": 0.2,
  "max_tokens": 2048,
  "response_format": {
    "type": "json_object"
  }
}
```

响应示例：

```json
{
  "id": "llm_req_xxx",
  "model": "deepseek-v4-pro",
  "content": {
    "intent": "REGISTER_DATASOURCE",
    "slots": {
      "datasourceType": "MySQL",
      "environment": "PRD"
    }
  },
  "usage": {
    "prompt_tokens": 1200,
    "completion_tokens": 300
  }
}
```

如果 `deepseek-v4-pro` 当前推理服务不支持原生工具调用，则一期采用“模型输出结构化 JSON + 编排服务执行工具”的方式。模型只输出候选意图、槽位和建议动作，真正的 MCP 工具调用仍由 `ProcessOrchestrator` 根据状态机和权限校验执行。

### 4.2 模型调用原则

1. 确定性流程不交给模型判断，必须由状态机判断。
2. 模型只负责理解自然语言、补齐上下文、生成用户可读反馈和选择候选工具。
3. 所有工具调用都必须经过编排服务二次校验。
4. 写操作必须满足状态机允许、权限允许、参数完整、幂等键存在。
5. 工具返回不得把密码、密钥等敏感信息传回模型上下文。
6. 对于可枚举状态，优先使用结构化输出，不依赖自由文本解析。

### 4.3 Agent 分层

推荐拆为三个逻辑 Agent，初期可在同一个服务内实现：

| Agent | 职责 | 是否可调用工具 |
| --- | --- | --- |
| Intent Agent | 意图识别、槽位提取 | 否 |
| Orchestrator Agent | 根据状态和用户输入生成下一步建议 | 只读工具为主 |
| Response Agent | 将状态机结果转成用户话术 | 否 |

写操作不直接由 Agent 执行，而由 `ProcessOrchestrator` 根据状态机结果调用 MCP 工具。

### 4.4 Prompt 基线

系统提示词建议分为静态段和动态段，便于缓存。

静态段：

```text
你是数据准备专家，负责帮助用户完成数据源登记、审批跟踪、连通性准备、元数据采集、数据地图更新、安全扫描、安全等级确认和中台空间项目绑定。

你不能绕过现有审批流程，不能直接处理密码或密钥，不能承诺已经完成尚未办结的流程。
你需要优先依据系统状态机输出回答用户，而不是凭空推断。
```

动态段：

```json
{
  "userInput": "帮我登记一个生产 MySQL 数据源，并立即安全扫描",
  "process": {},
  "subTasks": [],
  "availableActions": []
}
```

结构化输出：

```json
{
  "intent": "REGISTER_DATASOURCE",
  "slots": {
    "datasourceType": "MySQL",
    "environmentMode": "SINGLE",
    "environment": "PRD",
    "collectMetadataImmediately": true,
    "securityScanImmediately": true
  },
  "needClarification": false,
  "clarificationQuestion": null
}
```

## 5. 状态机落地设计

### 5.1 主任务状态

```java
public enum ProcessStatus {
    INIT,
    REGISTERING,
    APPROVING,
    CONNECTIVITY_PREPARING,
    METADATA_PREPARING,
    SECURITY_PREPARING,
    SPACE_BINDING,
    READY_FOR_USE,
    WAITING_USER_ACTION,
    WAITING_EXTERNAL_SYSTEM,
    FAILED,
    CANCELLED
}
```

### 5.2 子任务状态

```java
public enum SubTaskStatus {
    INIT,
    PAGE_OPENING,
    FORM_FILLING,
    REGISTER_FLOW_SUBMITTED,
    LEADER_APPROVING,
    REGISTRANT_REVIEWING,
    REGISTER_COMPLETED,
    CONNECTIVITY_CHECKING,
    CONNECTIVITY_FAILED,
    FIREWALL_REQUESTING,
    WAITING_FIREWALL_COMPLETED,
    CONNECTIVITY_READY,
    WAITING_METADATA_COLLECTION,
    METADATA_COLLECTING,
    DATA_MAP_UPDATING,
    DATA_MAP_UPDATED,
    SECURITY_SCANNING,
    WAITING_SECURITY_LEVEL_CONFIRM,
    SECURITY_LEVEL_CONFIRMED,
    WAITING_SPACE_BINDING,
    SPACE_BINDING_SUBMITTED,
    SPACE_BINDING_COMPLETED,
    READY_FOR_USE,
    FAILED,
    CANCELLED
}
```

### 5.3 状态流转规则

| 当前状态 | 触发事件 | 下一状态 | 动作 |
| --- | --- | --- | --- |
| INIT | USER_START_REGISTER | PAGE_OPENING | 唤醒登记页面 |
| FORM_FILLING | REGISTER_FORM_SUBMITTED | REGISTER_FLOW_SUBMITTED | 记录登记流程 ID |
| REGISTER_FLOW_SUBMITTED | LEADER_APPROVAL_STARTED | LEADER_APPROVING | 展示审批人和待办 |
| LEADER_APPROVING | LEADER_APPROVED | REGISTRANT_REVIEWING | 等待登记人复核 |
| REGISTRANT_REVIEWING | REGISTER_COMPLETED | CONNECTIVITY_CHECKING | 自动检测连通性 |
| CONNECTIVITY_CHECKING | CONNECTIVITY_PASSED | CONNECTIVITY_READY | 判断是否采集表结构 |
| CONNECTIVITY_CHECKING | NETWORK_UNREACHABLE | FIREWALL_REQUESTING | 发起防火墙流程 |
| FIREWALL_REQUESTING | FIREWALL_REQUEST_SUBMITTED | WAITING_FIREWALL_COMPLETED | 监听 IT 流程 |
| WAITING_FIREWALL_COMPLETED | FIREWALL_COMPLETED | CONNECTIVITY_CHECKING | 重新检测连通性 |
| CONNECTIVITY_READY | COLLECT_IMMEDIATELY_TRUE | METADATA_COLLECTING | 创建并执行采集任务 |
| CONNECTIVITY_READY | COLLECT_IMMEDIATELY_FALSE | WAITING_METADATA_COLLECTION | 等待用户后续触发 |
| METADATA_COLLECTING | METADATA_COLLECT_COMPLETED | DATA_MAP_UPDATING | 更新数据地图 |
| DATA_MAP_UPDATING | DATA_MAP_UPDATED | SECURITY_SCANNING / WAITING_SPACE_BINDING | 根据是否立即扫描分支 |
| SECURITY_SCANNING | SECURITY_SCAN_COMPLETED | WAITING_SECURITY_LEVEL_CONFIRM | 创建安全等级确认总工单 |
| WAITING_SECURITY_LEVEL_CONFIRM | SECURITY_LEVEL_CONFIRMED | WAITING_SPACE_BINDING | 提示可进入数据脱敏 |
| WAITING_SPACE_BINDING | SPACE_BINDING_SUBMITTED | SPACE_BINDING_SUBMITTED | 监听绑定流程 |
| SPACE_BINDING_SUBMITTED | SPACE_BINDING_COMPLETED | READY_FOR_USE | 重新计算主任务状态 |

## 6. 数据库设计

### 6.1 data_prepare_process

```sql
CREATE TABLE data_prepare_process (
  id BIGINT PRIMARY KEY AUTO_INCREMENT,
  process_id VARCHAR(64) NOT NULL UNIQUE,
  user_id VARCHAR(64) NOT NULL,
  user_name VARCHAR(128) NULL,
  mode VARCHAR(32) NOT NULL COMMENT 'SINGLE, PRD_UAT',
  datasource_type VARCHAR(64) NULL,
  status VARCHAR(64) NOT NULL,
  collect_metadata_immediately TINYINT(1) NOT NULL DEFAULT 1,
  security_scan_immediately TINYINT(1) NOT NULL DEFAULT 0,
  ready_for_use TINYINT(1) NOT NULL DEFAULT 0,
  last_error_code VARCHAR(64) NULL,
  last_error_message VARCHAR(512) NULL,
  created_at DATETIME NOT NULL,
  updated_at DATETIME NOT NULL,
  INDEX idx_user_status (user_id, status),
  INDEX idx_updated_at (updated_at)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;
```

### 6.2 data_source_sub_task

```sql
CREATE TABLE data_source_sub_task (
  id BIGINT PRIMARY KEY AUTO_INCREMENT,
  sub_task_id VARCHAR(64) NOT NULL UNIQUE,
  process_id VARCHAR(64) NOT NULL,
  environment VARCHAR(32) NOT NULL COMMENT 'PRD, UAT',
  datasource_id VARCHAR(128) NULL,
  datasource_name VARCHAR(256) NULL,
  register_flow_id VARCHAR(128) NULL,
  firewall_flow_id VARCHAR(128) NULL,
  metadata_task_id VARCHAR(128) NULL,
  security_scan_task_id VARCHAR(128) NULL,
  security_level_ticket_id VARCHAR(128) NULL,
  space_binding_flow_id VARCHAR(128) NULL,
  status VARCHAR(64) NOT NULL,
  blocker_type VARCHAR(64) NULL,
  blocker_owner VARCHAR(128) NULL,
  next_action VARCHAR(128) NULL,
  retry_count INT NOT NULL DEFAULT 0,
  last_error_code VARCHAR(64) NULL,
  last_error_message VARCHAR(512) NULL,
  created_at DATETIME NOT NULL,
  updated_at DATETIME NOT NULL,
  INDEX idx_process_id (process_id),
  INDEX idx_status (status),
  INDEX idx_register_flow_id (register_flow_id),
  INDEX idx_firewall_flow_id (firewall_flow_id)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;
```

### 6.3 process_event

```sql
CREATE TABLE process_event (
  id BIGINT PRIMARY KEY AUTO_INCREMENT,
  event_id VARCHAR(64) NOT NULL UNIQUE,
  process_id VARCHAR(64) NOT NULL,
  sub_task_id VARCHAR(64) NULL,
  event_type VARCHAR(128) NOT NULL,
  source_system VARCHAR(64) NOT NULL,
  payload JSON NULL,
  occurred_at DATETIME NULL,
  received_at DATETIME NOT NULL,
  handled TINYINT(1) NOT NULL DEFAULT 0,
  handled_at DATETIME NULL,
  INDEX idx_process_event (process_id, event_type),
  INDEX idx_handled (handled, received_at)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;
```

### 6.4 tool_invocation_log

```sql
CREATE TABLE tool_invocation_log (
  id BIGINT PRIMARY KEY AUTO_INCREMENT,
  invocation_id VARCHAR(64) NOT NULL UNIQUE,
  process_id VARCHAR(64) NOT NULL,
  sub_task_id VARCHAR(64) NULL,
  tool_name VARCHAR(128) NOT NULL,
  idempotency_key VARCHAR(256) NOT NULL,
  request_digest VARCHAR(1024) NULL,
  response_code VARCHAR(64) NULL,
  success TINYINT(1) NOT NULL,
  retryable TINYINT(1) NOT NULL DEFAULT 0,
  trace_id VARCHAR(128) NULL,
  duration_ms INT NULL,
  called_at DATETIME NOT NULL,
  INDEX idx_process_tool (process_id, tool_name),
  INDEX idx_idempotency_key (idempotency_key)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;
```

## 7. 后端接口设计

### 7.1 对话接口

```http
POST /api/data-prepare/conversations/message
Content-Type: application/json
```

请求：

```json
{
  "conversationId": "CONV_xxx",
  "processId": "DP_xxx",
  "message": "帮我登记一个生产 MySQL 数据源，并立即安全扫描"
}
```

响应：

```json
{
  "success": true,
  "data": {
    "conversationId": "CONV_xxx",
    "processId": "DP_xxx",
    "assistantMessage": "我会打开数据源登记页面，并预填生产环境和 MySQL 类型。",
    "progressCard": {},
    "actions": [
      {
        "type": "OPEN_DATASOURCE_REGISTER_MODAL",
        "url": "https://xxx/register?sessionId=xxx"
      }
    ]
  }
}
```

### 7.2 查询任务状态

```http
GET /api/data-prepare/processes/{processId}
```

响应：

```json
{
  "processId": "DP_xxx",
  "status": "APPROVING",
  "readyForUse": false,
  "subTasks": [
    {
      "subTaskId": "DST_PRD_xxx",
      "environment": "PRD",
      "datasourceId": "prd_order_db",
      "status": "LEADER_APPROVING",
      "blockerOwner": "张三",
      "nextAction": "WAIT_APPROVAL"
    }
  ]
}
```

### 7.3 页面提交回调

```http
POST /api/data-prepare/callbacks/datasource-register
Content-Type: application/json
```

请求：

```json
{
  "sessionId": "SESSION_xxx",
  "processId": "DP_xxx",
  "environment": "PRD",
  "datasourceId": "prd_order_db",
  "datasourceType": "MySQL",
  "registerFlowId": "PROC_xxx",
  "submittedBy": "u001",
  "submittedAt": "2026-06-17T10:00:00+08:00"
}
```

### 7.4 统一事件回调

```http
POST /api/data-prepare/callbacks/events
Content-Type: application/json
```

请求：

```json
{
  "eventId": "EVT_xxx",
  "eventType": "FIREWALL_REQUEST_COMPLETED",
  "sourceSystem": "IT_RESOURCE_PLATFORM",
  "businessId": "FW_xxx",
  "processId": "DP_xxx",
  "subTaskId": "DST_PRD_xxx",
  "payload": {}
}
```

## 8. MCP 工具落地设计

### 8.1 工具注册格式

每个 MCP 工具需要具备：

1. 工具名称。
2. 工具描述。
3. JSON Schema 入参。
4. JSON Schema 出参。
5. 权限点。
6. 幂等策略。
7. 超时与重试策略。

### 8.2 工具清单

| 工具 | 权限点 | 幂等键 | 超时 | 重试 |
| --- | --- | --- | --- | --- |
| open_datasource_register_page | DATASOURCE_REGISTER_VIEW | processId + environment | 3s | 否 |
| query_datasource_register_flow | DATASOURCE_REGISTER_QUERY | flowId | 5s | 是 |
| check_datasource_connectivity | DATASOURCE_CONNECTIVITY_CHECK | processId + subTaskId + datasourceId | 10s | 是 |
| create_firewall_request | FIREWALL_REQUEST_CREATE | processId + subTaskId | 10s | 是 |
| query_firewall_request | FIREWALL_REQUEST_QUERY | firewallFlowId | 5s | 是 |
| create_metadata_collect_task | METADATA_TASK_CREATE | processId + subTaskId | 10s | 是 |
| run_metadata_collect_task | METADATA_TASK_RUN | metadataTaskId | 10s | 是 |
| query_task_status | METADATA_TASK_QUERY | metadataTaskId | 5s | 是 |
| update_data_map | DATA_MAP_UPDATE | processId + subTaskId | 15s | 是 |
| run_security_scan | SECURITY_SCAN_RUN | processId + subTaskId | 10s | 是 |
| create_security_level_confirm_ticket | SECURITY_LEVEL_TICKET_CREATE | securityScanTaskId | 10s | 是 |
| open_space_project_binding_form | SPACE_BINDING_VIEW | processId + subTaskId | 3s | 否 |
| query_space_project_binding_status | SPACE_BINDING_QUERY | spaceBindingFlowId | 5s | 是 |

### 8.3 工具返回协议

```json
{
  "success": true,
  "code": "OK",
  "message": "success",
  "retryable": false,
  "traceId": "TRACE_xxx",
  "data": {}
}
```

错误码建议：

| 错误码 | 说明 | 是否可重试 |
| --- | --- | --- |
| PARAM_INVALID | 参数错误 | 否 |
| PERMISSION_DENIED | 无权限 | 否 |
| DOWNSTREAM_TIMEOUT | 下游超时 | 是 |
| DOWNSTREAM_UNAVAILABLE | 下游不可用 | 是 |
| FLOW_REJECTED | 流程被驳回 | 否 |
| NETWORK_UNREACHABLE | 网络不可达 | 否，转防火墙流程 |
| DUPLICATE_REQUEST | 重复请求 | 否，返回已有结果 |
| UNKNOWN_ERROR | 未知异常 | 视情况 |

## 9. 异步流程与补偿

### 9.1 Kafka Topic 设计

| Topic | 生产者 | 消费者 | 说明 |
| --- | --- | --- | --- |
| data-prepare-event | 回调服务、调度服务 | 编排服务 | 标准流程事件 |
| data-prepare-tool-result | MCP 网关 | 编排服务 | 异步工具结果 |
| data-prepare-notification | 编排服务 | 通知服务 | 用户提醒 |
| data-prepare-dead-letter | 各消费者 | 运维或补偿任务 | 死信事件 |

### 9.2 轮询任务

| 任务 | 频率 | 范围 |
| --- | --- | --- |
| RegisterFlowPollingJob | 5 分钟 | 审批中、复核中 |
| FirewallPollingJob | 10 分钟 | 等待防火墙办结 |
| MetadataTaskPollingJob | 2 分钟 | 元数据采集中 |
| SecurityScanPollingJob | 5 分钟 | 安全扫描中 |
| SecurityLevelTicketPollingJob | 10 分钟 | 等待安全等级确认 |
| SpaceBindingPollingJob | 5 分钟 | 空间绑定流程中 |

### 9.3 超时提醒

| 场景 | 超时阈值 | 提醒内容 |
| --- | --- | --- |
| 直属领导审批 | 24 小时 | 当前处理人、流程编号、待办入口 |
| 登记人复核 | 24 小时 | 复核入口、下一步说明 |
| 防火墙开通 | 48 小时 | IT 流程编号、当前状态 |
| 安全等级确认 | 24 小时 | 工单编号、确认入口 |
| 空间项目绑定 | 24 小时 | 绑定流程编号、处理入口 |

## 10. 权限与安全设计

### 10.1 权限点

| 权限点 | 说明 |
| --- | --- |
| DATASOURCE_PREPARE_START | 发起数据准备任务 |
| DATASOURCE_REGISTER_VIEW | 打开数据源登记页面 |
| DATASOURCE_REGISTER_QUERY | 查询登记流程 |
| DATASOURCE_CONNECTIVITY_CHECK | 执行连通性检测 |
| FIREWALL_REQUEST_CREATE | 发起防火墙流程 |
| METADATA_TASK_RUN | 执行元数据采集 |
| DATA_MAP_UPDATE | 更新数据地图 |
| SECURITY_SCAN_RUN | 执行安全扫描 |
| SPACE_BINDING_VIEW | 打开空间项目绑定页面 |
| PROCESS_ADMIN_RETRY | 管理员重试失败任务 |

### 10.2 敏感信息处理

1. 数据库密码、Token、密钥不进入模型上下文。
2. 页面提交回调只传 `credentialRef`，不传明文密码。
3. 工具调用日志只保存 `requestDigest`，不保存完整请求。
4. 对话日志需要脱敏 IP、账号、库名等敏感字段，按公司安全规范执行。
5. 写操作必须记录真实用户、代理服务、时间、工具名、下游 traceId。

## 11. 前端交互组件设计

### 11.1 ProgressCard

入参：

```ts
interface ProgressCardProps {
  processId: string;
  status: ProcessStatus;
  readyForUse: boolean;
  subTasks: DataSourceSubTaskView[];
  actions: ProcessAction[];
}
```

展示规则：

1. 单环境展示一条纵向步骤线。
2. PRD/UAT 展示环境维度分组。
3. 阻塞状态高亮当前处理人和处理入口。
4. 自动任务展示任务编号和最近更新时间。
5. 完成态展示后续入口。

### 11.2 DatasourceRegisterModal

职责：

1. iframe 或微前端方式承载现有登记页面。
2. URL 携带 `sessionId`、`processId`、`environment`。
3. 监听页面提交成功、取消、失败事件。
4. 弹窗关闭时不取消后端任务，只更新前端展示。

### 11.3 ActionBar

动作类型：

```ts
type ActionType =
  | 'OPEN_REGISTER_FORM'
  | 'OPEN_APPROVAL_TODO'
  | 'OPEN_FIREWALL_FLOW'
  | 'OPEN_SECURITY_LEVEL_TICKET'
  | 'OPEN_SPACE_BINDING_FORM'
  | 'RETRY_FAILED_STEP'
  | 'OPEN_QUERY_EXPLORE'
  | 'OPEN_OFFLINE_DEV'
  | 'OPEN_DATA_SYNC'
  | 'OPEN_DATA_MASKING';
```

## 12. 部署拓扑

```text
Ingress / API Gateway
  |
  +--> data-prepare-web
  |
  +--> data-prepare-service
          |
          +--> MySQL
          +--> Redis
          +--> Kafka
          +--> XXL-JOB
          +--> 企业大模型网关 / deepseek-v4-pro 推理服务
          +--> 数据源登记系统
          +--> 审批流系统
          +--> IT 资源管理平台
          +--> 元数据采集服务
          +--> 数据地图服务
          +--> 安全扫描服务
          +--> 空间项目绑定服务
```

### 12.1 资源建议

| 服务 | 副本 | CPU | 内存 | 说明 |
| --- | --- | --- | --- | --- |
| data-prepare-web | 2 | 0.5 Core | 512 Mi | 静态资源服务 |
| data-prepare-service | 2-4 | 2 Core | 4 Gi | 编排、工具、事件处理 |
| scheduler worker | 2 | 1 Core | 2 Gi | 可合并在 service 中 |
| llm-gateway | 2 | 2 Core | 4 Gi | 企业大模型网关，负责限流、审计、协议适配 |
| deepseek-v4-pro inference | 按 GPU 资源规划 | 视模型规格而定 | 视模型规格而定 | 建议由统一模型平台承载 |

### 12.2 环境变量

```text
LLM_PROVIDER=LOCAL_DEEPSEEK
LLM_GATEWAY_BASE_URL=http://llm-gateway.internal/v1
LLM_GATEWAY_TOKEN=***
LLM_PRIMARY_MODEL=deepseek-v4-pro
LLM_FAST_MODEL=deepseek-v4-pro
LLM_DEFAULT_TEMPERATURE=0.2
LLM_INTENT_TEMPERATURE=0
DB_URL=jdbc:mysql://...
REDIS_URL=redis://...
KAFKA_BOOTSTRAP_SERVERS=...
DATASOURCE_REGISTER_BASE_URL=...
SPACE_BINDING_BASE_URL=...
```

## 13. 测试方案

### 13.1 单元测试

| 模块 | 测试重点 |
| --- | --- |
| IntentClassifier | 意图识别准确率、未知意图兜底 |
| SlotExtractor | PRD/UAT、立即采集、立即安全扫描抽取 |
| StateMachineEngine | 状态流转合法性 |
| ReadyForUseEvaluator | 完成态判定 |
| McpToolRegistry | 工具权限、幂等、错误码映射 |

### 13.2 集成测试

1. 登记页面提交回调后进入审批跟踪。
2. 审批办结后自动执行连通性检测。
3. 网络不可达后创建防火墙流程。
4. 防火墙办结后重新检测连通性。
5. 元数据采集完成后更新数据地图。
6. 立即安全扫描分支生成安全等级确认总工单。
7. 空间项目绑定完成后进入 `READY_FOR_USE`。
8. PRD/UAT 任一环境失败时主任务不完成。

### 13.3 模型评测

准备 50-100 条真实或模拟用户输入，覆盖：

1. 普通登记。
2. 指定环境和类型。
3. 同时登记 PRD/UAT。
4. 登记后立即采集和安全扫描。
5. 查询进度。
6. 用户表达模糊或信息缺失。
7. 用户要求跳过审批等不允许动作。

评测指标：

| 指标 | 目标 |
| --- | --- |
| 意图识别准确率 | >= 95% |
| 槽位抽取准确率 | >= 95% |
| 不允许动作拒绝率 | 100% |
| 工具调用误触发率 | 0 |
| 用户反馈可理解性 | 人工评审通过 |

## 14. 开发计划

### 14.1 一期里程碑

| 周期 | 交付 |
| --- | --- |
| 第 1 周 | 工程脚手架、数据库表、状态机基础实现 |
| 第 2 周 | 对话接口、意图识别、登记页面唤醒 |
| 第 3 周 | 登记回调、审批状态跟踪、进度卡片 |
| 第 4 周 | 连通性检测、防火墙异步流程 |
| 第 5 周 | 元数据采集、数据地图更新 |
| 第 6 周 | 空间项目绑定、READY_FOR_USE 判定 |
| 第 7 周 | PRD/UAT 双环境、异常补偿、审计日志 |
| 第 8 周 | 联调、压测、模型评测、灰度上线 |

### 14.2 二期增强

1. 安全扫描和安全等级确认总工单完整联动。
2. 用户主动继续采集表结构的恢复流程。
3. 更多数据源类型字段模板。
4. 更细粒度的权限治理和审计报表。
5. 模型评测平台和提示词版本管理。

## 15. 关键落地建议

1. 一期不要把所有流程都做成“模型驱动”，确定性流程必须由状态机驱动。
2. 先打通单环境闭环，再扩展 PRD/UAT 双环境。
3. 页面唤醒协议和回调协议是联调关键，需要尽早和现有页面团队确认。
4. 防火墙、审批、空间绑定都要按异步流程设计，不能依赖同步等待。
5. MCP 工具网关必须从第一天就做幂等、权限和审计，否则后期补会很痛。
6. 模型调用先做路由和评测，不建议所有请求都使用最高规格模型。
7. 对用户可见的“完成”必须严格对应 `READY_FOR_USE` 判定，不能只看登记流程办结。

## 16. 参考资料

1. DeepSeek V4 Pro 模型部署文档：待补充公司内部地址。
2. 企业大模型网关接入规范：待补充公司内部地址。
3. vLLM 部署与推理服务文档：待补充公司内部基线版本。
4. SGLang 部署与推理服务文档：待补充公司内部基线版本。
