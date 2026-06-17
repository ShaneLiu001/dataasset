# 数据准备专家架构设计文档

## 1. 架构目标

数据准备专家的架构目标是：在不替代现有数据源登记页面、审批流程、IT 资源管理平台、元数据采集、安全扫描和空间项目绑定能力的前提下，新增一层可对话、可编排、可追踪、可审计的数据准备编排能力。

系统需要解决三个核心问题：

1. 用户不知道从哪里开始、下一步做什么。
2. 数据源接入跨多个系统，流程状态分散，缺少统一反馈。
3. 部分步骤是审批流，部分步骤是自动任务，部分步骤是异步外部流程，需要统一编排和恢复。

最终交付状态为 `READY_FOR_USE`，表示数据源已完成登记审批、连通性准备、元数据采集、数据地图更新和中台空间项目绑定，具备进入查询探索、离线开发、数据同步、安全扫描等后续场景的条件。如果用户选择立即安全扫描，则需要同时完成安全扫描和安全等级确认总工单。

## 2. 设计原则

1. 编排优先：数据准备专家负责串联流程，不重复建设已有业务系统。
2. 页面复用：数据源登记和空间项目绑定继续使用现有页面，通过弹窗或新标签页唤醒。
3. 流程不绕过：登记审批、防火墙开通、空间项目绑定、安全等级确认等流程保持原有审批链路。
4. 状态集中：所有子流程状态汇总到统一的数据准备任务中。
5. 工具隔离：智能助手不直接访问业务系统接口，通过 MCP 工具网关调用受控能力。
6. 异步可靠：审批流、IT 资源管理平台、防火墙开通、安全等级确认等长流程采用回调、消息和轮询兜底。
7. 可恢复：任务中断、页面关闭、消息丢失后，可以根据 `processId` 恢复当前状态。
8. 可审计：所有用户操作、工具调用、流程推进和自动任务执行均可追踪。

## 3. 系统边界

### 3.1 新增能力

| 模块 | 说明 |
| --- | --- |
| 智能助手入口 | 承接用户自然语言输入，展示进度卡片和下一步指引 |
| 意图识别与槽位提取 | 识别登记、采集、扫描、绑定、查询进度等意图 |
| 数据准备编排服务 | 维护主流程状态机，决定下一步动作 |
| 状态中心 | 保存数据准备任务、子任务、事件和工具调用记录 |
| MCP 工具网关 | 包装现有接口，向智能助手和编排服务暴露标准工具 |
| 事件监听服务 | 接收审批流、IT 资源管理平台、任务平台的回调或消息 |
| 异步调度与补偿服务 | 处理轮询、超时提醒、失败重试和断点续跑 |

### 3.2 复用能力

| 现有能力 | 复用方式 |
| --- | --- |
| 数据源登记页面 | 弹窗唤醒，携带 `processId/sessionId`，支持预填和提交回调 |
| 数据源登记审批流 | 继续由原流程承载，数据准备专家只跟踪状态 |
| 防火墙开通流程 | 对接 IT 资源管理平台，异步发起并监听办结 |
| 元数据采集接口 | 通过 MCP 工具包装为自动任务 |
| 数据地图更新接口 | 通过 MCP 工具包装，采集完成后自动调用 |
| 安全扫描接口 | 用户选择立即扫描时自动调用 |
| 安全等级确认总工单 | 扫描完成后创建，并跟踪用户确认结果 |
| 中台空间项目绑定页面/流程 | 弹窗或链接唤醒，用户填写表单后跟踪办结状态 |

## 4. 总体架构

```text
用户
  |
  v
智能助手前端
  |  自然语言、进度卡片、弹窗唤醒
  v
意图识别与会话服务
  |  intent / slots / processId
  v
数据准备编排服务
  |  状态机、流程决策、下一步动作
  +----------------------+
  |                      |
  v                      v
状态中心              MCP 工具网关
  |                      |
  |                      +--> 数据源登记页面 / 登记审批流
  |                      +--> 连通性检测接口
  |                      +--> IT 资源管理平台 / 防火墙流程
  |                      +--> 元数据采集服务
  |                      +--> 数据地图 / ES / Redis / 元数据接口
  |                      +--> 安全扫描服务
  |                      +--> 安全等级确认工单
  |                      +--> 中台空间项目绑定流程
  |
  v
事件监听与异步调度服务
  |  回调、消息、轮询、补偿、超时提醒
  v
用户通知 / 进度卡片更新
```

## 5. 核心模块设计

### 5.1 智能助手前端

职责：

1. 接收用户自然语言输入。
2. 展示数据准备进度卡片。
3. 唤醒现有登记页面和绑定页面。
4. 展示审批待办、工单链接、失败原因和后续入口。
5. 支持用户随时查询“当前到哪一步”。

前端不直接执行业务接口调用，只通过后端会话服务和编排服务获取状态与动作。

### 5.2 意图识别与会话服务

职责：

1. 识别用户意图，例如登记数据源、同时登记 PRD/UAT、登记并安全扫描、查询进度。
2. 提取可预填槽位，例如环境、数据源类型、是否立即采集表结构、是否立即安全扫描。
3. 创建或恢复 `processId`。
4. 将用户输入转换为结构化编排请求。

关键输出示例：

```json
{
  "intent": "REGISTER_DATASOURCE",
  "processId": "DP_20260617_0001",
  "mode": "PRD_UAT",
  "slots": {
    "datasourceType": "MySQL",
    "environment": "PRD",
    "collectMetadataImmediately": true,
    "securityScanImmediately": true
  }
}
```

### 5.3 数据准备编排服务

职责：

1. 维护主流程和 PRD/UAT 子任务状态。
2. 决定下一步动作，例如打开登记页面、查询审批状态、发起防火墙流程、执行元数据采集。
3. 调用 MCP 工具网关。
4. 接收事件监听服务推送的状态变更。
5. 生成用户可理解的反馈文案和进度卡片数据。

编排服务是数据准备专家的核心，不保存业务系统明细数据，只保存流程推进所需的引用信息。

### 5.4 MCP 工具网关

职责：

1. 将现有接口包装为稳定工具。
2. 屏蔽不同系统的鉴权、参数和错误码差异。
3. 对工具调用进行权限校验、参数校验、幂等控制和日志记录。
4. 向编排服务返回标准化结果。

工具返回结果应统一包含：

```json
{
  "success": true,
  "code": "OK",
  "message": "submitted",
  "data": {},
  "traceId": "TRACE_xxx",
  "retryable": false
}
```

### 5.5 状态中心

职责：

1. 保存数据准备主任务。
2. 保存 PRD/UAT 子任务。
3. 保存流程事件。
4. 保存工具调用记录。
5. 支持根据 `processId` 恢复任务。

状态中心是进度卡片、异常恢复和审计追踪的统一数据来源。

### 5.6 事件监听与异步调度服务

职责：

1. 接收登记审批流、IT 资源管理平台、防火墙流程、任务平台、工单平台的回调。
2. 对没有回调能力的系统进行定时状态查询。
3. 处理超时提醒、失败重试和补偿执行。
4. 将外部事件转换为标准事件后推送给编排服务。

推荐策略：

1. 回调优先。
2. 流程消息补充。
3. 定时轮询兜底。
4. 人工重试入口保底。

## 6. 数据模型设计

### 6.1 DataPrepareProcess

数据准备主任务。

| 字段 | 说明 |
| --- | --- |
| processId | 数据准备任务 ID |
| userId | 发起用户 |
| status | 主流程状态 |
| mode | 单环境或 PRD/UAT 同时登记 |
| datasourceType | 数据源类型 |
| collectMetadataImmediately | 是否立即采集表结构 |
| securityScanImmediately | 是否立即安全扫描 |
| readyForUse | 是否达到可使用状态 |
| createdAt | 创建时间 |
| updatedAt | 更新时间 |
| lastErrorCode | 最近一次错误码 |
| lastErrorMessage | 最近一次错误描述 |

### 6.2 DataSourceSubTask

环境级子任务。单环境模式下也建议创建一条子任务，便于统一处理。

| 字段 | 说明 |
| --- | --- |
| subTaskId | 子任务 ID |
| processId | 所属主任务 ID |
| environment | PRD、UAT 或其他环境 |
| datasourceId | 数据源 ID |
| registerFlowId | 数据源登记流程 ID |
| firewallFlowId | 防火墙开通流程 ID |
| metadataTaskId | 元数据采集任务 ID |
| securityScanTaskId | 安全扫描任务 ID |
| securityLevelTicketId | 安全等级确认总工单 ID |
| spaceBindingFlowId | 空间项目绑定流程 ID |
| status | 子任务当前状态 |
| blockerType | 阻塞类型 |
| blockerOwner | 当前处理人 |
| nextAction | 下一步动作 |

### 6.3 ProcessEvent

流程事件流水。

| 字段 | 说明 |
| --- | --- |
| eventId | 事件 ID |
| processId | 主任务 ID |
| subTaskId | 子任务 ID，可为空 |
| eventType | 事件类型 |
| sourceSystem | 来源系统 |
| payload | 原始或标准化事件内容 |
| occurredAt | 事件发生时间 |
| receivedAt | 系统接收时间 |

### 6.4 ToolInvocationLog

工具调用审计。

| 字段 | 说明 |
| --- | --- |
| invocationId | 调用 ID |
| processId | 主任务 ID |
| toolName | MCP 工具名称 |
| requestDigest | 请求摘要，不记录敏感明文 |
| responseCode | 返回码 |
| success | 是否成功 |
| traceId | 下游链路追踪 ID |
| calledAt | 调用时间 |
| durationMs | 耗时 |

## 7. 状态机设计

主流程状态用于展示整体进度，子任务状态用于跟踪每个环境的实际推进情况。

### 7.1 子任务状态

```text
INIT
  -> PAGE_OPENING
  -> FORM_FILLING
  -> REGISTER_FLOW_SUBMITTED
  -> LEADER_APPROVING
  -> REGISTRANT_REVIEWING
  -> REGISTER_COMPLETED
  -> CONNECTIVITY_CHECKING
  -> FIREWALL_REQUESTING
  -> WAITING_FIREWALL_COMPLETED
  -> CONNECTIVITY_READY
  -> WAITING_METADATA_COLLECTION
  -> METADATA_COLLECTING
  -> DATA_MAP_UPDATING
  -> SECURITY_SCANNING
  -> WAITING_SECURITY_LEVEL_CONFIRM
  -> SECURITY_LEVEL_CONFIRMED
  -> WAITING_SPACE_BINDING
  -> SPACE_BINDING_SUBMITTED
  -> SPACE_BINDING_COMPLETED
  -> READY_FOR_USE
```

异常状态：

```text
CANCELLED
FAILED
WAITING_USER_ACTION
WAITING_EXTERNAL_SYSTEM
```

### 7.2 READY_FOR_USE 判定

默认判定条件：

1. 数据源登记流程办结。
2. 连通性可用，或防火墙流程办结后连通性检测通过。
3. 元数据采集完成。
4. 数据地图、ES、Redis、元数据对外接口更新完成。
5. 中台空间项目绑定完成。

如果用户选择立即安全扫描，还需要满足：

1. 安全扫描完成。
2. 安全等级确认总工单办结。

如果用户选择同时登记 PRD 和 UAT：

1. PRD 子任务达到 `READY_FOR_USE`。
2. UAT 子任务达到 `READY_FOR_USE`。
3. 主任务才可标记为 `READY_FOR_USE`。

## 8. 核心流程设计

### 8.1 发起数据准备任务

1. 用户输入自然语言。
2. 意图识别服务提取意图和槽位。
3. 编排服务创建 `DataPrepareProcess`。
4. 如果是 PRD/UAT 同时登记，创建两条 `DataSourceSubTask`。
5. 调用 `open_datasource_register_page` 唤醒现有登记页面。
6. 前端展示进度卡片。

### 8.2 登记表单与审批跟踪

1. 用户在现有页面填写并提交表单。
2. 现有页面回传数据源 ID、登记流程 ID、环境等信息。
3. 编排服务更新子任务为 `REGISTER_FLOW_SUBMITTED`。
4. 监听直属领导审批和登记人复核状态。
5. 登记流程办结后，推进到连通性检测。

### 8.3 连通性检测与防火墙开通

1. 调用 `check_datasource_connectivity`。
2. 如果成功，进入元数据准备。
3. 如果网络不可达，调用 `create_firewall_request`。
4. 记录防火墙流程 ID。
5. 子任务进入 `WAITING_FIREWALL_COMPLETED`。
6. 监听 IT 资源管理平台流程办结。
7. 办结后自动重新执行连通性检测。

防火墙流程必须按异步流程处理，不应阻塞用户会话。

### 8.4 元数据采集与数据地图更新

1. 如果用户选择立即采集表结构，调用 `create_metadata_collect_task`。
2. 调用 `run_metadata_collect_task`。
3. 通过回调或 `query_task_status` 获取采集结果。
4. 采集完成后调用 `update_data_map`。
5. 数据地图更新成功后，进入安全扫描或空间项目绑定。

如果用户未选择立即采集表结构，子任务进入 `WAITING_METADATA_COLLECTION`，系统只提示后续入口，不自动触发数据地图更新和安全扫描。

### 8.5 安全扫描与安全等级确认

1. 如果用户选择立即安全扫描，元数据采集完成后调用 `run_security_scan`。
2. 扫描完成后调用 `create_security_level_confirm_ticket`。
3. 子任务进入 `WAITING_SECURITY_LEVEL_CONFIRM`。
4. 用户完成安全等级确认后，系统接收回调或查询确认状态。
5. 确认完成后，提示用户可进入数据脱敏。

安全扫描在本架构中是可选编排分支。未选择立即扫描时，安全扫描作为接入完成后的推荐入口。

### 8.6 中台空间项目绑定

1. 元数据和数据地图准备完成后，检查空间项目绑定状态。
2. 如果未绑定，调用 `open_space_project_binding_form`。
3. 用户填写现有绑定表单并提交。
4. 记录绑定流程 ID。
5. 监听绑定流程办结。
6. 绑定完成后重新计算 `READY_FOR_USE`。

## 9. MCP 工具设计

| 工具名称 | 调用方式 | 说明 |
| --- | --- | --- |
| open_datasource_register_page | 同步 | 唤醒现有数据源登记页面 |
| query_datasource_register_flow | 异步/查询 | 查询登记审批流状态 |
| check_datasource_connectivity | 同步 | 检测数据源连通性 |
| create_firewall_request | 异步 | 发起防火墙开通流程 |
| query_firewall_request | 查询 | 查询防火墙流程状态 |
| create_metadata_collect_task | 同步 | 创建元数据采集任务 |
| run_metadata_collect_task | 异步 | 执行元数据采集 |
| query_task_status | 查询 | 查询采集任务状态 |
| update_data_map | 异步 | 更新数据地图、ES、Redis、元数据接口 |
| run_security_scan | 异步 | 执行安全扫描 |
| query_security_scan_status | 查询 | 查询安全扫描状态 |
| create_security_level_confirm_ticket | 异步 | 创建安全等级确认总工单 |
| query_security_level_confirm_status | 查询 | 查询安全等级确认状态 |
| check_space_project_binding | 同步 | 检查是否已绑定空间项目 |
| open_space_project_binding_form | 同步 | 唤醒空间项目绑定表单 |
| query_space_project_binding_status | 查询 | 查询绑定流程状态 |

工具设计要求：

1. 所有写操作必须支持幂等键，建议使用 `processId + subTaskId + actionType`。
2. 所有工具调用必须记录审计日志。
3. 工具不得返回密码、密钥等敏感明文。
4. 下游异常需要映射为标准错误码。
5. 可重试错误必须标记 `retryable=true`。

## 10. 事件与回调设计

推荐统一事件格式：

```json
{
  "eventId": "EVT_xxx",
  "eventType": "DATASOURCE_REGISTER_APPROVED",
  "processId": "DP_xxx",
  "subTaskId": "DST_xxx",
  "sourceSystem": "workflow",
  "occurredAt": "2026-06-17T10:00:00+08:00",
  "payload": {}
}
```

关键事件类型：

| 事件类型 | 说明 |
| --- | --- |
| DATASOURCE_REGISTER_SUBMITTED | 数据源登记表单提交成功 |
| DATASOURCE_LEADER_APPROVED | 直属领导审批通过 |
| DATASOURCE_REGISTRANT_REVIEWED | 登记人复核完成 |
| DATASOURCE_REGISTER_COMPLETED | 数据源登记流程办结 |
| FIREWALL_REQUEST_COMPLETED | 防火墙开通流程办结 |
| CONNECTIVITY_CHECK_PASSED | 连通性检测通过 |
| METADATA_COLLECT_COMPLETED | 元数据采集完成 |
| DATA_MAP_UPDATED | 数据地图更新完成 |
| SECURITY_SCAN_COMPLETED | 安全扫描完成 |
| SECURITY_LEVEL_CONFIRMED | 安全等级确认完成 |
| SPACE_BINDING_COMPLETED | 空间项目绑定完成 |
| PROCESS_FAILED | 流程失败 |

## 11. 异步与补偿机制

### 11.1 异步处理场景

| 场景 | 处理方式 |
| --- | --- |
| 登记审批 | 回调或审批流查询 |
| 防火墙开通 | IT 资源管理平台回调或轮询 |
| 元数据采集 | 任务状态回调或轮询 |
| 数据地图更新 | 任务状态回调或轮询 |
| 安全扫描 | 扫描状态回调或轮询 |
| 安全等级确认 | 工单回调或轮询 |
| 空间项目绑定 | 流程回调或轮询 |

### 11.2 补偿策略

1. 消息丢失：定时按未完成任务轮询下游状态。
2. 工具调用失败：按错误类型判断是否重试。
3. 重复回调：根据 `eventId` 和业务 ID 去重。
4. 用户关闭页面：任务继续保留，用户再次进入后按 `processId` 恢复。
5. 长时间等待：向用户展示当前处理人、流程编号和待办入口。
6. 下游状态不一致：以业务系统最终状态为准，编排服务修正本地状态。

## 12. 权限与安全设计

1. 用户身份需要透传到现有页面和下游接口。
2. MCP 工具网关需要校验用户是否有发起登记、采集、扫描、绑定的权限。
3. 密码和凭证不进入智能助手上下文，不在日志和事件中明文保存。
4. 推荐使用 `credentialRef` 引用凭证管理系统中的密钥。
5. 页面唤醒链接需要短期有效，避免长期可访问。
6. 审批链接、工单链接只展示给有权限的用户。
7. 所有自动任务需要记录发起人、代理执行人和来源任务。

## 13. 可观测性设计

建议监控以下指标：

| 指标 | 说明 |
| --- | --- |
| 数据准备任务创建数 | 用户使用规模 |
| READY_FOR_USE 完成率 | 整体成功率 |
| 平均准备耗时 | 从发起到完成的平均时间 |
| 审批等待耗时 | 直属领导审批、登记人复核耗时 |
| 防火墙流程耗时 | 网络开通瓶颈 |
| 元数据采集成功率 | 自动任务质量 |
| 数据地图更新成功率 | 资产可见性保障 |
| 安全扫描成功率 | 安全分支质量 |
| 空间项目绑定完成率 | 最终准备完成关键节点 |
| 工具调用失败率 | MCP 网关稳定性 |

## 14. 部署建议

建议按以下服务拆分：

| 服务 | 说明 |
| --- | --- |
| data-prepare-assistant-web | 智能助手前端与进度卡片 |
| data-prepare-conversation-service | 意图识别、会话管理、用户反馈 |
| data-prepare-orchestrator | 流程编排、状态机、下一步决策 |
| data-prepare-mcp-gateway | MCP 工具封装与下游接口适配 |
| data-prepare-event-listener | 回调接收、消息消费、事件标准化 |
| data-prepare-scheduler | 轮询、重试、超时提醒、补偿任务 |

一期也可以合并部署为一个后端服务，但需要在代码模块上保持边界清晰，避免后续拆分困难。

## 15. 风险与待确认

| 风险 | 影响 | 建议 |
| --- | --- | --- |
| 现有页面不支持弹窗承载或预填 | 影响用户体验 | 先支持新标签页降级，逐步改造页面协议 |
| 审批流回调能力不足 | 状态更新不及时 | 建立轮询兜底机制 |
| 防火墙流程耗时不可控 | 用户等待时间长 | 展示流程编号、处理状态和预计下一步 |
| PRD/UAT 其中一个环境失败 | 主任务无法完成 | 子任务独立展示阻塞原因和重试入口 |
| 凭证处理不规范 | 安全风险 | 使用凭证引用，不进助手上下文 |
| 下游接口错误码不统一 | 用户反馈不清晰 | MCP 网关统一错误码和可重试标识 |

## 16. 迭代建议

### 一期

1. 支持自然语言发起数据源登记。
2. 支持唤醒现有登记页面并预填基础字段。
3. 支持登记审批状态跟踪。
4. 支持连通性检测、防火墙流程异步发起和办结监听。
5. 支持元数据采集、数据地图更新。
6. 支持空间项目绑定流程跟踪。
7. 支持 PRD/UAT 同时登记的子任务展示。

### 二期

1. 完善安全扫描和安全等级确认总工单联动。
2. 增强失败恢复、自动重试和人工重试入口。
3. 建设统一事件中心和更完整的可观测指标。
4. 支持更多数据源类型字段差异和校验策略。

### 三期

1. 沉淀为可复用的数据接入 Agent 工作流。
2. 支持与数据血缘、数据质量、权限治理、脱敏策略联动。
3. 支持从数据准备任务直接生成后续开发、同步和治理建议。
