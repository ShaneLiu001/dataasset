# 数小智整体 Agent 结构图

## 1. 定位说明

数小智是数据中台统一智能助手，承担主 Agent 职责。它不直接承载所有专业能力，而是负责理解用户诉求、识别业务域、选择对应专家助手、汇总结果并统一返回。

数据资产助手是数小智下的一个子 Agent / 专家助手，和离线开发助手、离线同步助手、运维监控助手、统一门户助手、实时同步助手、报表开发助手属于平级专业能力模块。

## 2. 整体结构图

```mermaid
flowchart TB
  User[用户] --> Portal[数据中台统一入口<br/>门户 / 工作台 / 对话框]
  Portal --> Gateway[数据中台 Gateway<br/>认证 / 鉴权 / 审计 / 上下文透传]
  Gateway --> Xiaozhi[数小智主 Agent<br/>意图识别 / 任务路由 / 多专家协同 / 结果汇总]

  Xiaozhi --> Context[统一上下文中心<br/>用户 / 组织 / 角色 / 会话 / traceId]
  Xiaozhi --> Memory[会话与任务状态<br/>thread_id / task_id / state_json]
  Xiaozhi --> Obs[公司可观测平台<br/>OpenTelemetry + Langfuse]

  Xiaozhi --> AssetAgent[数据资产助手<br/>资产搜索 / 元数据治理 / 血缘 / 稽核 / 标准]
  Xiaozhi --> OfflineDevAgent[离线开发助手<br/>作业开发 / SQL 生成 / 调度配置 / 代码解释]
  Xiaozhi --> OfflineSyncAgent[离线同步助手<br/>数据同步任务 / 源端目标端配置 / 同步诊断]
  Xiaozhi --> OpsAgent[运维监控助手<br/>任务告警 / 失败诊断 / 资源分析 / SLA]
  Xiaozhi --> PortalAgent[统一门户助手<br/>菜单导航 / 权限申请 / 使用指引 / 入口推荐]
  Xiaozhi --> RealtimeSyncAgent[实时同步助手<br/>实时链路 / Topic / 延迟诊断 / 异常处理]
  Xiaozhi --> ReportAgent[报表开发助手<br/>指标取数 / 报表口径 / 图表配置 / 发布检查]

  AssetAgent --> AssetPlatform[数据资产管理平台<br/>Gateway / 元数据接口 / 数据地图 ES / 血缘 / 稽核]
  OfflineDevAgent --> OfflineDev[离线开发平台<br/>开发 IDE / 调度 / 任务 / SQL 引擎]
  OfflineSyncAgent --> OfflineSync[离线同步平台<br/>采集任务 / 数据源 / 同步链路]
  OpsAgent --> Ops[运维监控平台<br/>告警 / 日志 / 指标 / 调度运行态]
  PortalAgent --> UnifiedPortal[统一门户平台<br/>菜单 / 权限 / 待办 / 通知]
  RealtimeSyncAgent --> RealtimeSync[实时同步平台<br/>Flink / Kafka / 实时任务]
  ReportAgent --> BI[报表开发平台<br/>数据集 / 指标 / 看板 / 发布]
```

## 3. 分层视图

```mermaid
flowchart TB
  subgraph L1[用户入口层]
    U1[数据中台门户]
    U2[工作台助手入口]
    U3[各模块侧边栏助手]
  end

  subgraph L2[统一接入层]
    GW[数据中台 Gateway]
    Auth[认证鉴权]
    Audit[审计日志]
    Ctx[用户 / 组织 / 角色上下文]
  end

  subgraph L3[主 Agent 层]
    Main[数小智主 Agent]
    Router[意图识别与专家路由]
    Planner[跨模块任务规划]
    Aggregator[结果汇总与解释]
  end

  subgraph L4[专家 Agent 层]
    A1[数据资产助手]
    A2[离线开发助手]
    A3[离线同步助手]
    A4[运维监控助手]
    A5[统一门户助手]
    A6[实时同步助手]
    A7[报表开发助手]
  end

  subgraph L5[平台能力层]
    P1[数据资产管理平台]
    P2[离线开发平台]
    P3[离线同步平台]
    P4[运维监控平台]
    P5[统一门户平台]
    P6[实时同步平台]
    P7[报表开发平台]
  end

  subgraph L6[公共能力层]
    Model[企业大模型服务]
    Tool[工具网关 / Tool Registry]
    State[任务状态中心]
    Obs[OpenTelemetry + Langfuse]
    Knowledge[知识库 / 规则库 / Prompt 版本]
  end

  L1 --> L2
  L2 --> L3
  L3 --> L4
  L4 --> L5
  L3 --> L6
  L4 --> L6
```

## 4. 数小智与数据资产助手的关系

```mermaid
sequenceDiagram
  participant U as 用户
  participant X as 数小智主 Agent
  participant A as 数据资产助手
  participant G as 数据资产管理 Gateway
  participant ES as 数据地图 ES
  participant M as 元数据管理平台接口
  participant O as 公司可观测平台

  U->>X: 客户收入用哪张表？顺便看下下游报表影响
  X->>O: 记录用户输入、会话、traceId
  X->>X: 识别为数据资产域任务
  X->>A: 路由到数据资产助手，传递用户上下文
  A->>G: 调用数据资产管理平台能力
  G->>ES: 搜索客户收入相关资产
  ES-->>G: 返回候选表、字段、主题域
  G->>M: 查询候选资产详情和血缘摘要
  M-->>G: 返回字段、指标、负责人、下游报表
  G-->>A: 返回结构化资产证据
  A-->>X: 返回推荐资产、依据、风险提示
  X->>O: 记录专家调用、工具调用和输出
  X-->>U: 汇总回答并展示结果卡片
```

## 5. 主 Agent 职责

数小智主 Agent 负责平台级编排：

1. 识别用户问题属于哪个业务域。
2. 将任务路由到对应专家助手。
3. 对跨模块任务进行拆解和多专家协同。
4. 统一管理会话、任务状态、上下文和 traceId。
5. 对多个专家的结果进行汇总、去重、解释和下一步建议生成。
6. 对写操作、跨模块影响操作、批量操作执行统一确认策略。

## 6. 数据资产助手职责

数据资产助手只负责数据资产管理领域内的专业任务：

1. 数据资产搜索、查表、查字段、查指标。
2. 元数据详情查询、字段解释、指标口径解释。
3. 数据地图搜索，基于 Elasticsearch 加速资产检索。
4. 血缘分析、下游影响分析。
5. 数据标准匹配、元数据补全、治理建议生成。
6. 数据稽核规则草案生成和确认后创建。
7. 通过数据资产管理 Gateway 和平台接口访问底层能力。

## 7. 跨专家协同示例

```text
用户：帮我找客户收入相关表，用它开发一张月度收入报表，并配置每日稽核。

数小智主 Agent 拆解：
1. 数据资产助手：查找客户收入权威表、字段、指标口径、血缘影响。
2. 报表开发助手：根据推荐资产生成报表数据集和图表配置建议。
3. 离线开发助手：必要时生成加工 SQL 或调度任务。
4. 数据稽核助手能力由数据资产助手承接：生成收入金额非空、波动、及时性规则草案。
5. 数小智汇总：返回报表开发建议、数据来源依据、稽核草案和待确认动作。
```

## 8. 设计原则

1. 数小智是主 Agent，负责统一入口、统一路由、统一上下文和结果汇总。
2. 数据资产助手是数小智下的数据资产领域子 Agent，不直接替代数小智。
3. 各专家助手平级，分别绑定对应数据中台模块能力。
4. 专家助手通过各自模块 Gateway / 平台接口访问业务系统。
5. 公共能力包括企业大模型、工具网关、状态中心、OpenTelemetry、Langfuse、Prompt 管理和知识库。
6. 跨模块任务由数小智拆解，专家助手只处理自己领域内的专业任务。
7. 写操作必须经过用户确认，并由对应业务平台完成审计和权限校验。

