# 数据资产 Agent 助手实现思路

## 1. 建设定位

数据资产 Agent 助手不是单一的问答机器人，而是面向数据资产管理平台的一层智能编排入口。它通过自然语言承接用户诉求，再调用查表、血缘、数据源登记、数据稽核、元数据治理等平台能力，把原来分散在多个模块里的操作串成可跟踪、可审计、可恢复的任务。

可以延续前期“数据准备专家”的建设逻辑：

```text
自然语言入口
  -> 意图识别与槽位抽取
  -> 编排服务创建任务
  -> 调用平台工具 / 唤醒现有页面
  -> 监听异步事件
  -> 展示进度卡片与结果解释
```

但数据资产 Agent 助手需要进一步升级为：

```text
自然语言入口
  -> 主 Agent 判断任务类型和上下文
  -> 调用领域子 Agent
  -> 子 Agent 调用 MCP 工具、语义检索、图谱血缘、规则引擎
  -> 主 Agent 汇总证据、生成解释和下一步动作
  -> 状态中心持续跟踪任务
```

核心目标是让用户用一句话完成以下工作：

1. 查表、查字段、查指标、查口径。
2. 查询表级、字段级、任务级、报表级血缘。
3. 登记数据源，并跟踪审批、连通性、元数据采集、地图更新。
4. 配置数据稽核规则，生成规则建议，跟踪稽核运行结果。
5. 发起元数据治理任务，包括补全、纠错、发布、下线、冲突识别。
6. 跨模块组合处理，例如“帮我找客户收入相关表，确认血缘后配置一条每日稽核规则”。

## 2. 总体架构

推荐采用“主 Agent + 子 Agent + 工具网关 + 状态中心 + 事件调度”的架构。

```text
用户入口层
  - 数据资产助手对话框
  - 进度卡片
  - 结果卡片
  - 现有页面弹窗 / 侧边栏唤醒

智能编排层
  - 主 Agent / Router Agent
  - 会话服务
  - 任务编排服务
  - 计划生成器
  - 结果解释器

领域子 Agent 层
  - 查表问数 Agent
  - 血缘分析 Agent
  - 数据源登记 Agent
  - 数据稽核 Agent
  - 元数据治理 Agent
  - 权限与风险校验 Agent

工具与知识层
  - MCP 工具网关
  - 元数据搜索服务
  - 本体语义服务
  - 血缘图谱服务
  - 质量规则服务
  - 数据源管理服务
  - 工单 / 审批 / 任务调度接口

状态与审计层
  - 会话状态
  - Agent 任务状态
  - 子任务状态
  - 工具调用日志
  - 事件回调日志
  - 用户确认记录
```

### 2.1 主 Agent 职责

主 Agent 不直接承载所有专业能力，而是负责“判断、拆解、调度、汇总”。

职责包括：

1. 识别用户意图：查表、查血缘、登记数据源、配置稽核、元数据治理、组合任务。
2. 抽取关键槽位：系统、数据源、库、表、字段、指标、主题域、环境、频率、规则类型等。
3. 判断是否需要澄清：缺少必要参数时，不盲目调用写操作。
4. 生成执行计划：把复杂诉求拆成多个子任务。
5. 选择子 Agent：把专业任务交给对应领域 Agent。
6. 汇总证据：合并元数据、本体、血缘、质量、权限结果。
7. 控制风险：写操作、发布操作、批量操作必须经过用户确认。
8. 输出用户可理解的解释和下一步建议。

### 2.2 子 Agent 职责

子 Agent 是领域能力单元，每个子 Agent 只负责一类高内聚任务。

| 子 Agent | 主要职责 | 典型问题 |
| --- | --- | --- |
| 查表问数 Agent | 找表、找字段、找指标、解释口径、生成样例 SQL | “客户收入用哪张表？” |
| 血缘分析 Agent | 查询上下游、解释加工链路、影响分析、血缘摘要 | “这个字段下游影响哪些报表？” |
| 数据源登记 Agent | 复用数据准备专家逻辑，登记数据源、跟踪审批和采集 | “帮我登记一个生产 Oracle 数据源” |
| 数据稽核 Agent | 推荐稽核规则、配置规则、运行检查、解释异常 | “给这张表配置每日空值率稽核” |
| 元数据治理 Agent | 补全中文名、备注、主题域、负责人、标准映射、发起审核 | “把这批字段备注补齐并提交审核” |
| 权限与风险 Agent | 判断访问权限、敏感等级、写操作风险、合规提醒 | “我能不能查看这个表的样例数据？” |

子 Agent 对外暴露标准接口：

```json
{
  "agent": "LINEAGE_AGENT",
  "taskId": "AT_20260701_0001",
  "input": {},
  "output": {
    "answer": "",
    "evidence": [],
    "actions": [],
    "confidence": 0.92
  },
  "needUserConfirm": false
}
```

## 3. 核心能力设计

### 3.1 自然语言查表

处理链路：

```text
用户问题
  -> 主 Agent 识别为 FIND_DATA_ASSET
  -> 查表问数 Agent 抽取业务概念
  -> 本体语义服务映射实体 / 属性 / 指标
  -> 元数据搜索服务混合召回表、字段、指标
  -> 血缘分析 Agent 补充权威来源和上下游证据
  -> 权限与风险 Agent 判断可访问性
  -> 主 Agent 返回推荐表、字段、口径、关联方式和样例 SQL
```

检索策略建议采用三路召回：

1. 关键词检索：表名、字段名、系统名、编码精确匹配。
2. 向量检索：中文描述、业务口径、历史问法、备注语义匹配。
3. 图检索：本体实体关系、Join 路径、指标来源、血缘上下游扩展。

排序权重建议：

```text
综合得分 =
  语义相关性 * 0.30
  + 权威认证程度 * 0.25
  + 使用热度 * 0.15
  + 血缘可信度 * 0.15
  + 元数据完整度 * 0.10
  + 当前用户权限匹配 * 0.05
```

输出不只给“搜索结果”，而应给“推荐理由”：

```text
建议优先使用 dwd_customer_income_df。

原因：
1. 命中本体概念：客户 Customer、收入 Revenue。
2. 该表是客户收入分析主题下的认证宽表。
3. 收入字段 income_amt 来源于合同收入指标口径。
4. 下游已有 12 张报表引用，近 30 天查询 86 次。
5. 当前用户具备表访问权限，但手机号字段需要脱敏查看。
```

### 3.2 血缘查询

血缘查询要支持三种粒度：

1. 表级血缘：表的上游来源、下游消费、任务链路。
2. 字段级血缘：字段来源字段、加工表达式、派生逻辑。
3. 业务血缘：指标、报表、数据服务、业务对象之间的影响关系。

处理链路：

```text
用户问题
  -> 主 Agent 识别为 QUERY_LINEAGE
  -> 血缘分析 Agent 标准化对象
  -> 调用血缘图谱工具
  -> 按方向、深度、对象类型过滤
  -> 调用元数据服务补充中文名、负责人、热度、安全等级
  -> 生成血缘摘要、影响清单和风险提示
```

典型工具：

| 工具 | 说明 |
| --- | --- |
| search_asset | 先把自然语言对象定位成具体表、字段、指标 |
| query_table_lineage | 查询表级上下游 |
| query_column_lineage | 查询字段级上下游 |
| query_metric_lineage | 查询指标来源和消费 |
| explain_lineage_path | 解释两点之间的血缘路径 |
| analyze_change_impact | 分析改表、改字段、下线资产的影响 |

血缘结果要避免只展示图，建议返回“摘要 + 图 + 影响列表”：

```text
ods.crm_customer 是 dwd.customer_profile_df 的直接上游。
字段 cust_id 在下游 8 张表中继续作为客户主键使用，其中 3 张表被报表引用。
如果修改 cust_id 类型，将影响客户画像、客户收入分析和重点客户名单三个主题。
```

### 3.3 数据源登记

数据源登记 Agent 可以最大化复用前期数据准备专家：

```text
自然语言
  -> 识别数据源类型、环境、是否 PRD/UAT、是否立即采集、是否安全扫描
  -> 创建 DataAssetAgentTask
  -> 创建 DataSourceRegisterSubTask
  -> 唤醒现有数据源登记页面
  -> 跟踪审批流
  -> 检测连通性
  -> 必要时发起防火墙流程
  -> 执行元数据采集
  -> 更新数据地图 / ES / Redis / 元数据接口
  -> 进入可用状态
```

与数据准备专家相比，需要补充两个点：

1. 登记完成后自动沉淀资产上下文，包括主题域、负责人、系统、数据分层、元数据完整度。
2. 可以继续联动元数据治理和稽核配置，例如提示“是否为该数据源生成基础稽核规则”。

写操作必须受控：

1. 自动预填可以直接做。
2. 创建登记流程、创建防火墙流程、发起采集、发起扫描前需要明确用户意图。
3. 发布、下线、批量修改元数据前必须二次确认。

### 3.4 数据稽核配置

数据稽核 Agent 的核心不是让用户记住规则配置页面，而是把自然语言转换为可审核的规则草案。

处理链路：

```text
用户诉求
  -> 定位表 / 字段 / 指标
  -> 读取字段类型、分区、历史分布、空值率、唯一性、码值、标准
  -> 推荐稽核模板
  -> 生成规则草案
  -> 用户确认
  -> 调用稽核配置工具创建规则
  -> 创建调度和告警
  -> 返回规则 ID 和运行计划
```

支持的规则类型：

| 类型 | 示例 |
| --- | --- |
| 完整性 | 主键不能为空、关键字段空值率小于 1% |
| 唯一性 | customer_id 每日分区内唯一 |
| 及时性 | 每日 8 点前完成更新 |
| 波动性 | 收入金额较 7 日均值波动不超过 30% |
| 码值合法性 | status 必须属于有效码值集 |
| 参照完整性 | 事实表 customer_id 必须能关联客户主表 |
| 指标一致性 | 明细汇总金额与指标平台结果一致 |

生成规则草案示例：

```json
{
  "ruleName": "客户收入表主键唯一性稽核",
  "asset": "dwd_customer_income_df",
  "ruleType": "UNIQUE",
  "columns": ["customer_id", "biz_date"],
  "schedule": "0 8 * * *",
  "threshold": {
    "maxDuplicateCount": 0
  },
  "alertLevel": "P2"
}
```

### 3.5 元数据治理

元数据治理 Agent 要覆盖“发现问题、生成建议、人工确认、发布回写、持续学习”的闭环。

典型场景：

1. 字段中文名、业务含义、备注自动补全。
2. 表归属主题域、业务实体、本体属性映射。
3. 负责人、使用说明、数据分层、生命周期补齐。
4. 口径冲突识别。
5. 废弃资产、低价值资产、重复资产识别。
6. 安全等级、权限标签、脱敏建议联动。

处理链路：

```text
用户选择治理对象
  -> 元数据治理 Agent 采集上下文
  -> 调用本体语义服务、标准服务、血缘服务、质量服务
  -> 生成候选元数据
  -> 输出置信度和证据
  -> 用户审核修改
  -> 调用审核发布接口
  -> 回写样例库、本体映射和治理记录
```

治理建议必须带证据：

```json
{
  "field": "cust_id",
  "suggestedChineseName": "客户编码",
  "suggestedMeaning": "客户在主数据系统中的唯一标识。",
  "confidence": 0.96,
  "evidence": [
    "命中本体属性 Customer.customer_id",
    "上游字段 mdm_customer.customer_id 已审核为客户编码",
    "字段在 18 条血缘路径中作为客户主键使用"
  ],
  "risk": "无明显冲突"
}
```

## 4. AI 编排机制

### 4.1 意图分类

建议先定义稳定意图枚举，不让大模型自由发挥。

| 意图 | 说明 |
| --- | --- |
| FIND_ASSET | 查表、查字段、查指标 |
| QUERY_LINEAGE | 查询血缘、影响分析 |
| REGISTER_DATASOURCE | 登记数据源 |
| CONFIG_QUALITY_RULE | 配置稽核规则 |
| GOVERN_METADATA | 元数据补全、纠错、发布 |
| QUERY_TASK_PROGRESS | 查询任务进度 |
| COMPOSITE_TASK | 跨模块组合任务 |
| SMALL_TALK_OR_HELP | 帮助说明或闲聊 |

意图识别输出：

```json
{
  "intent": "COMPOSITE_TASK",
  "confidence": 0.91,
  "slots": {
    "businessConcepts": ["客户", "收入"],
    "actions": ["find_asset", "query_lineage", "config_quality_rule"],
    "schedule": "daily",
    "qualityGoal": "amount_not_null"
  },
  "needClarification": false
}
```

### 4.2 计划生成

复杂任务先生成计划，再逐步执行。

示例：

用户输入：

```text
帮我找客户收入相关的权威表，看看来源是否可靠，然后配置每日金额非空稽核。
```

主 Agent 生成计划：

```json
{
  "plan": [
    {
      "step": 1,
      "agent": "SEARCH_AGENT",
      "action": "find_authoritative_asset",
      "status": "PENDING"
    },
    {
      "step": 2,
      "agent": "LINEAGE_AGENT",
      "action": "analyze_source_reliability",
      "status": "PENDING"
    },
    {
      "step": 3,
      "agent": "QUALITY_AGENT",
      "action": "draft_quality_rule",
      "status": "PENDING"
    },
    {
      "step": 4,
      "agent": "MAIN_AGENT",
      "action": "ask_user_confirm_before_create_rule",
      "status": "PENDING"
    }
  ]
}
```

### 4.3 主子 Agent 调用方式

主 Agent 调子 Agent 时，不建议只传自然语言，应该传结构化任务上下文。

```json
{
  "parentTaskId": "DAA_20260701_0001",
  "subTaskId": "DAA_SUB_0001",
  "userId": "u001",
  "intent": "QUERY_LINEAGE",
  "target": {
    "type": "table",
    "name": "dwd_customer_income_df"
  },
  "constraints": {
    "direction": "upstream",
    "depth": 3,
    "includeColumnLineage": true
  },
  "context": {
    "conversationSummary": "",
    "selectedAssets": [],
    "permissionScope": []
  }
}
```

子 Agent 返回时必须结构化：

```json
{
  "subTaskId": "DAA_SUB_0001",
  "status": "SUCCEEDED",
  "summary": "该表上游来自合同、客户主数据和财务确认收入三类来源。",
  "evidence": [
    {
      "type": "lineage_path",
      "source": "lineage_service",
      "content": "ods_contract -> dwd_contract -> dwd_customer_income_df"
    }
  ],
  "artifacts": {
    "lineageGraphId": "LG_001"
  },
  "recommendedActions": [
    {
      "action": "CONFIG_QUALITY_RULE",
      "reason": "收入金额字段为关键指标字段，建议配置非空和波动稽核"
    }
  ],
  "confidence": 0.9
}
```

### 4.4 执行控制

需要把操作分为三类：

| 类型 | 示例 | 控制方式 |
| --- | --- | --- |
| 只读查询 | 查表、查血缘、查进度 | 可直接执行 |
| 可恢复写操作 | 创建草稿、生成规则草案、发起采集任务 | 明确意图后执行，记录幂等键 |
| 高风险写操作 | 发布元数据、下线资产、批量改规则、删除配置 | 必须二次确认，展示影响范围 |

所有工具调用都要有：

1. 用户身份。
2. 业务权限校验。
3. 幂等键。
4. traceId。
5. 输入输出脱敏日志。
6. 标准错误码。
7. 可重试标记。

## 5. MCP 工具体系

工具网关负责把现有系统能力包装成 Agent 可调用的稳定工具。

### 5.1 元数据与查表工具

| 工具 | 说明 |
| --- | --- |
| search_metadata | 按关键词、语义、过滤条件搜索表字段指标 |
| get_table_detail | 获取表详情、字段、分区、负责人、热度 |
| get_column_detail | 获取字段详情、类型、备注、安全等级 |
| search_metric | 搜索指标和口径 |
| generate_sample_sql | 根据表、字段、指标和 Join 路径生成样例 SQL |

### 5.2 血缘工具

| 工具 | 说明 |
| --- | --- |
| query_table_lineage | 查询表级血缘 |
| query_column_lineage | 查询字段级血缘 |
| query_report_lineage | 查询报表引用链路 |
| analyze_impact | 分析变更影响 |
| explain_lineage_path | 解释血缘路径 |

### 5.3 数据源工具

可复用数据准备专家工具：

| 工具 | 说明 |
| --- | --- |
| open_datasource_register_page | 唤醒数据源登记页面 |
| query_datasource_register_flow | 查询登记审批状态 |
| check_datasource_connectivity | 检测连通性 |
| create_firewall_request | 发起防火墙开通 |
| create_metadata_collect_task | 创建元数据采集任务 |
| run_metadata_collect_task | 执行元数据采集 |
| update_data_map | 更新数据地图 |

### 5.4 稽核工具

| 工具 | 说明 |
| --- | --- |
| recommend_quality_rules | 根据资产上下文推荐稽核规则 |
| create_quality_rule_draft | 创建稽核规则草稿 |
| publish_quality_rule | 发布稽核规则 |
| run_quality_check | 立即执行稽核 |
| query_quality_result | 查询稽核结果 |

### 5.5 治理工具

| 工具 | 说明 |
| --- | --- |
| autocomplete_metadata | 生成元数据补全建议 |
| detect_metadata_issue | 识别缺失、冲突、重复、过期元数据 |
| create_governance_task | 创建治理任务 |
| submit_metadata_review | 提交元数据审核 |
| publish_metadata_change | 发布元数据变更 |

## 6. 状态模型

建议将所有 Agent 任务统一成一张主任务表和一张子任务表。

### 6.1 主任务

| 字段 | 说明 |
| --- | --- |
| taskId | 数据资产 Agent 任务 ID |
| userId | 发起人 |
| originalText | 用户原始输入 |
| intent | 主意图 |
| status | RUNNING / WAITING_USER / SUCCEEDED / FAILED / CANCELLED |
| currentStep | 当前步骤 |
| summary | 当前摘要 |
| createdAt | 创建时间 |
| updatedAt | 更新时间 |

### 6.2 子任务

| 字段 | 说明 |
| --- | --- |
| subTaskId | 子任务 ID |
| taskId | 主任务 ID |
| agentType | 子 Agent 类型 |
| actionType | 动作类型 |
| status | 子任务状态 |
| inputRef | 输入上下文引用 |
| outputRef | 输出结果引用 |
| externalBizId | 外部流程、工单、任务 ID |
| traceId | 工具调用链路 ID |

### 6.3 事件

统一事件格式：

```json
{
  "eventId": "EVT_001",
  "taskId": "DAA_20260701_0001",
  "subTaskId": "SUB_001",
  "eventType": "QUALITY_RULE_CREATED",
  "sourceSystem": "quality-platform",
  "occurredAt": "2026-07-01T10:00:00+08:00",
  "payload": {}
}
```

## 7. 前端交互

前端可以沿用数据准备专家的“对话 + 卡片 + 弹窗承载现有页面”模式，但结果卡片要按资产场景扩展。

建议组件：

1. 对话输入区：承接自然语言。
2. 任务进度卡片：展示多步骤执行状态。
3. 资产推荐卡片：展示推荐表、字段、指标、可信原因。
4. 血缘摘要卡片：展示上下游摘要、影响对象、图谱入口。
5. 稽核规则草案卡片：展示规则类型、阈值、调度、告警级别，并提供确认创建。
6. 元数据治理建议卡片：展示候选值、置信度、证据、审核入口。
7. 风险确认弹窗：发布、下线、批量修改前展示影响范围。

交互原则：

1. 查询类结果直接返回。
2. 写操作先生成草案，再让用户确认。
3. 长流程进入进度卡片，用户关闭页面后可恢复。
4. 现有复杂表单不重做，优先弹窗或侧边栏承载。
5. 每个 AI 建议都要能看到依据。

## 8. 分阶段落地路线

### 一期：统一入口和只读查询

目标是先把“查表、查血缘、查指标、查进度”做顺。

交付：

1. 数据资产助手入口。
2. 主 Agent 意图识别和会话服务。
3. 查表问数 Agent。
4. 血缘分析 Agent。
5. 元数据搜索、血缘查询、指标查询 MCP 工具。
6. 资产推荐卡片和血缘摘要卡片。

一期尽量不做高风险写操作，重点建立用户信任。

### 二期：复用数据准备专家，接入数据源登记

目标是把前期数据准备专家能力迁入数据资产 Agent 助手。

交付：

1. 数据源登记 Agent。
2. 数据源登记、审批、连通性、防火墙、采集、地图更新工具。
3. Agent 任务状态中心。
4. 异步事件监听和补偿。
5. 数据源准备进度卡片。

### 三期：稽核配置和元数据治理

目标是从“问”升级到“办”。

交付：

1. 数据稽核 Agent。
2. 元数据治理 Agent。
3. 稽核规则推荐和草稿创建。
4. 元数据补全、审核、发布流程。
5. 用户确认和审计机制。

### 四期：复合任务和主动治理

目标是支持跨模块自动编排。

交付：

1. 复杂计划生成。
2. 主子 Agent 协同。
3. 资产健康评分。
4. 主动发现治理问题。
5. 低价值资产、重复资产、口径冲突治理建议。

## 9. 关键设计原则

1. 主 Agent 做编排，子 Agent 做专业判断，工具做确定性执行。
2. 只读查询可以自动执行，写操作必须有确认边界。
3. AI 输出必须结构化，不能只返回自然语言。
4. 所有建议必须带证据、置信度和来源。
5. 不重复建设已有平台能力，通过 MCP 工具网关接入。
6. 状态中心是长流程、异步回调、进度恢复和审计追踪的核心。
7. 本体语义层是查表、查指标、血缘解释和元数据治理的共同底座。
8. 第一阶段先把高频只读场景做准，再逐步开放自动办理能力。

