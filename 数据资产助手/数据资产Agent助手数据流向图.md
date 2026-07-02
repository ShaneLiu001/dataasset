# 数据资产 Agent 助手数据流向图

## 1. 总体数据流

```mermaid
flowchart LR
  U[用户] --> FE[数据资产助手前端<br/>对话框 / 进度卡片 / 结果卡片]
  FE --> Gateway[现有数据资产管理 Gateway 服务<br/>认证 / 鉴权 / 审计 / 上下文透传]
  Gateway --> API[FastAPI AI 助手服务<br/>会话接口 / 请求适配 / 流式返回]

  API --> Router[LangGraph 主编排<br/>意图识别 / 槽位抽取 / 计划生成 / 状态流转]
  Router --> State[业务状态中心<br/>任务 / 子任务 / 事件 / 审计]

  Router --> SearchAgent[查表问数 Agent]
  Router --> LineageAgent[血缘分析 Agent]
  Router --> DsAgent[数据源登记 Agent]
  Router --> QualityAgent[数据稽核 Agent]
  Router --> GovernanceAgent[元数据治理 Agent]
  Router --> RiskAgent[权限与风险 Agent]

  SearchAgent --> ToolGateway[MCP 工具网关<br/>鉴权 / 幂等 / 参数校验 / 错误码]
  LineageAgent --> ToolGateway
  DsAgent --> ToolGateway
  QualityAgent --> ToolGateway
  GovernanceAgent --> ToolGateway
  RiskAgent --> ToolGateway

  ToolGateway --> Metadata[元数据管理平台接口<br/>表 / 字段 / 指标 / 负责人]
  ToolGateway --> DataMap[Elasticsearch 数据地图搜索引擎<br/>采集元数据索引 / 资产搜索 / 全文检索]
  ToolGateway --> Ontology[本体语义服务<br/>实体 / 属性 / 指标 / 关系]
  ToolGateway --> Lineage[血缘图谱服务<br/>表级 / 字段级 / 报表级]
  ToolGateway --> Datasource[统一数据源平台<br/>登记 / 连通性 / 采集]
  ToolGateway --> Quality[数据稽核平台<br/>规则 / 调度 / 结果]
  ToolGateway --> Workflow[审批 / 工单 / 任务调度]
  Metadata --> PlatformDB[平台后端数据库<br/>Oracle 存量 / GoldenDB 迁移目标]
  MetadataCollect[元数据采集服务] --> Metadata
  MetadataCollect --> DataMap

  Workflow --> Event[事件监听与异步调度<br/>回调 / 轮询 / 补偿]
  Datasource --> Event
  Quality --> Event
  Metadata --> Event
  Event --> State
  State --> Router

  Router --> Answer[结果解释器<br/>证据 / 置信度 / 下一步动作]
  Answer --> API
  API --> Gateway
  Gateway --> FE

  Router -. trace .-> Obs[公司可观测平台<br/>OpenTelemetry + Langfuse]
  ToolGateway -. trace .-> Obs
  API -. trace .-> Obs
  Gateway -. trace .-> Obs
  SearchAgent -. trace .-> Obs
  LineageAgent -. trace .-> Obs
  DsAgent -. trace .-> Obs
  QualityAgent -. trace .-> Obs
  GovernanceAgent -. trace .-> Obs
```

## 2. 组件分层

```mermaid
flowchart TB
  subgraph L1[用户入口层]
    FE1[对话输入]
    FE2[任务进度卡片]
    FE3[资产推荐卡片]
    FE4[血缘摘要卡片]
    FE5[稽核 / 治理确认卡片]
  end

  subgraph L2[平台接入层]
    Gateway[现有数据资产管理 Gateway 服务]
    Auth[认证鉴权 / 权限上下文]
    Audit[审计日志]
    Api[FastAPI AI 助手服务]
  end

  subgraph L3[AI 编排层]
    Session[会话服务]
    Router[LangGraph 主编排]
    Planner[计划生成器]
    Executor[任务执行器]
    Explainer[结果解释器]
  end

  subgraph L4[领域 Agent 层]
    A1[查表问数 Agent]
    A2[血缘分析 Agent]
    A3[数据源登记 Agent]
    A4[数据稽核 Agent]
    A5[元数据治理 Agent]
    A6[权限与风险 Agent]
  end

  subgraph L5[工具与知识层]
    MCP[MCP 工具网关]
    RAG[混合检索<br/>ES 关键词 / 全文 / 向量可选]
    ES[Elasticsearch 数据地图搜索引擎<br/>采集元数据索引]
    Ontology[本体语义服务]
    Business[业务平台接口<br/>元数据 / 血缘 / 稽核 / 数据源 / 审批]
    DB[Oracle / GoldenDB<br/>数据资产管理平台后端数据库]
    Collect[元数据采集服务<br/>采集后同步到 ES]
  end

  subgraph L6[状态与观测层]
    State[业务状态中心]
    Event[事件监听与补偿]
    Obs[公司可观测平台<br/>OpenTelemetry + Langfuse]
  end

  L1 --> L2
  L2 --> L3
  L3 --> L4
  L4 --> L5
  L5 --> L6
  L6 --> L3
```

## 3. 自然语言查表数据流

适用于“客户收入用哪张表”“帮我找某指标口径”“某字段在哪张表”等只读场景。

```mermaid
sequenceDiagram
  participant U as 用户
  participant FE as 助手前端
  participant GW as 现有数据资产管理 Gateway
  participant API as FastAPI AI 助手服务
  participant R as LangGraph 主编排
  participant S as 查表问数 Agent
  participant O as 本体语义服务
  participant ES as Elasticsearch 数据地图搜索引擎
  participant M as 元数据管理平台接口
  participant L as 血缘图谱服务
  participant P as 权限与风险 Agent
  participant LF as 公司可观测平台

  U->>FE: 客户收入用哪张表？
  FE->>GW: 提交自然语言
  GW->>GW: 登录校验、权限上下文、审计记录
  GW->>API: 转发问题 + userId + role + orgId + traceId
  API->>R: 调用 LangGraph 会话线程
  R->>LF: 记录会话输入和意图识别 Trace
  R->>R: 识别意图 FIND_ASSET，抽取客户/收入
  R->>S: 调用查表问数 Agent
  S->>O: 映射业务概念到本体实体/指标
  O-->>S: Customer / Revenue / 合同收入指标
  S->>ES: 从数据地图搜索引擎检索候选资产
  ES-->>S: 候选表、字段、主题域、标签
  S->>M: 查询候选资产详情
  M-->>S: 字段、指标、负责人、口径、状态
  S->>L: 补充权威来源、上下游和使用情况
  L-->>S: 血缘证据和下游引用
  S->>P: 校验当前用户权限和敏感字段风险
  P-->>S: 可访问范围和风险提示
  S-->>R: 推荐资产 + 证据 + 置信度 + 样例 SQL
  R->>LF: 记录检索、工具调用、输出评分
  R-->>API: 返回资产推荐结果
  API-->>GW: 返回结构化响应
  GW-->>FE: 返回资产推荐卡片
  FE-->>U: 展示推荐表、字段、口径、依据
```

## 4. 血缘查询数据流

适用于“这张表上游是什么”“这个字段影响哪些报表”“下线这张表影响谁”等场景。

```mermaid
sequenceDiagram
  participant U as 用户
  participant FE as 助手前端
  participant GW as 现有数据资产管理 Gateway
  participant API as FastAPI AI 助手服务
  participant R as LangGraph 主编排
  participant A as 血缘分析 Agent
  participant M as 元数据管理平台接口
  participant G as 血缘图谱服务
  participant Risk as 权限与风险 Agent
  participant State as 业务状态中心

  U->>FE: dwd_customer_income_df 下游影响哪些报表？
  FE->>GW: 自然语言查询
  GW->>GW: 认证鉴权、补充用户上下文
  GW->>API: 转发查询 + 权限上下文
  API->>R: 调用 LangGraph
  R->>R: 识别意图 QUERY_LINEAGE
  R->>State: 创建只读查询任务记录
  R->>A: 传入对象、方向、深度、对象类型
  A->>M: 标准化表名并获取资产详情
  M-->>A: 表中文名、负责人、安全等级、热度
  A->>G: 查询下游表、任务、报表、字段链路
  G-->>A: 血缘路径和影响对象
  A->>Risk: 校验结果可见范围
  Risk-->>A: 过滤敏感对象或增加风险提示
  A-->>R: 血缘摘要 + 影响清单 + 图谱 ID
  R->>State: 写入查询结果摘要和 traceId
  R-->>API: 返回血缘摘要和图谱入口
  API-->>GW: 返回结构化响应
  GW-->>FE: 返回血缘摘要卡片和图谱入口
  FE-->>U: 展示血缘摘要、影响报表、负责人
```

## 5. 数据源登记长流程数据流

适用于“帮我登记一个生产 MySQL 数据源，同时采集元数据并安全扫描”等长流程场景。

```mermaid
sequenceDiagram
  participant U as 用户
  participant FE as 助手前端
  participant GWY as 现有数据资产管理 Gateway
  participant API as FastAPI AI 助手服务
  participant R as LangGraph 主编排
  participant D as 数据源登记 Agent
  participant GW as MCP 工具网关
  participant DS as 统一数据源平台
  participant WF as 审批/工单平台
  participant META as 元数据采集服务
  participant EV as 事件监听与补偿
  participant State as 业务状态中心
  participant Obs as 公司可观测平台

  U->>FE: 帮我登记一个生产 MySQL 数据源，并立即采集表结构
  FE->>GWY: 提交自然语言任务
  GWY->>GWY: 认证鉴权、审计、上下文透传
  GWY->>API: 转发任务请求
  API->>R: 调用 LangGraph
  R->>Obs: 记录输入和意图识别
  R->>R: 识别 REGISTER_DATASOURCE，抽取 PRD/MySQL/立即采集
  R->>State: 创建主任务和数据源登记子任务
  R->>D: 调用数据源登记 Agent
  D->>GW: open_datasource_register_page
  GW->>DS: 唤醒现有登记页面并预填低敏字段
  DS-->>FE: 打开登记表单
  U->>DS: 填写连接信息并提交
  DS->>EV: 回调 DATASOURCE_REGISTER_SUBMITTED
  EV->>State: 写入登记流程 ID 和当前状态
  WF->>EV: 回调审批通过 / 复核完成
  EV->>State: 更新审批状态
  EV->>D: 推进下一步
  D->>GW: check_datasource_connectivity
  GW->>DS: 连通性检测
  DS-->>GW: 检测通过
  D->>GW: create_metadata_collect_task
  GW->>META: 创建并运行元数据采集任务
  META->>EV: 回调 METADATA_COLLECT_COMPLETED
  EV->>State: 更新采集完成
  D->>GW: update_data_map
  GW->>META: 更新数据地图、ES、Redis、元数据接口
  META->>EV: 回调 DATA_MAP_UPDATED
  EV->>State: 更新 READY_FOR_USE
  State-->>R: 返回最新任务状态
  R-->>API: 返回进度卡片数据
  API-->>GWY: 返回任务状态
  GWY-->>FE: 返回进度卡片和后续入口
  FE-->>U: 展示数据源已准备完成
```

## 6. 稽核配置数据流

适用于“给这张表配置每日非空稽核”“收入金额波动超过 30% 告警”等场景。

```mermaid
sequenceDiagram
  participant U as 用户
  participant FE as 助手前端
  participant GW as 现有数据资产管理 Gateway
  participant API as FastAPI AI 助手服务
  participant R as LangGraph 主编排
  participant Q as 数据稽核 Agent
  participant M as 元数据管理平台接口
  participant L as 血缘图谱服务
  participant QS as 数据稽核平台
  participant State as 业务状态中心
  participant Obs as 公司可观测平台

  U->>FE: 给客户收入表配置每日金额非空稽核
  FE->>GW: 提交自然语言任务
  GW->>GW: 认证鉴权、审计、上下文透传
  GW->>API: 转发任务请求
  API->>R: 调用 LangGraph
  R->>R: 识别 CONFIG_QUALITY_RULE
  R->>State: 创建稽核配置子任务
  R->>Q: 调用数据稽核 Agent
  Q->>M: 定位客户收入表和金额字段
  M-->>Q: 表字段、分区、字段类型、负责人
  Q->>L: 查询关键字段血缘和下游影响
  L-->>Q: 字段为关键指标字段
  Q->>QS: 查询历史质量分布和可用规则模板
  QS-->>Q: 推荐完整性规则模板
  Q-->>R: 生成稽核规则草案
  R->>Obs: 记录规则草案生成过程
  R-->>API: 返回稽核规则草案
  API-->>GW: 返回结构化响应
  GW-->>FE: 展示规则草案，等待用户确认
  U->>FE: 确认创建
  FE->>GW: 用户确认
  GW->>API: 转发确认请求
  API->>R: 继续 LangGraph 任务
  R->>Q: 执行创建规则
  Q->>QS: create_quality_rule_draft / publish_quality_rule
  QS-->>Q: 返回规则 ID 和调度计划
  Q-->>R: 创建成功
  R->>State: 更新子任务成功和规则 ID
  R-->>API: 返回规则创建结果
  API-->>GW: 返回结构化响应
  GW-->>FE: 返回规则创建结果
```

## 7. 元数据治理数据流

适用于“补齐这批字段备注”“识别重复资产”“把候选元数据提交审核”等场景。

```mermaid
sequenceDiagram
  participant U as 用户
  participant FE as 助手前端
  participant GW as 现有数据资产管理 Gateway
  participant API as FastAPI AI 助手服务
  participant R as LangGraph 主编排
  participant G as 元数据治理 Agent
  participant M as 元数据管理平台接口
  participant O as 本体语义服务
  participant L as 血缘图谱服务
  participant Std as 标准/码值服务
  participant Review as 审核发布服务
  participant State as 业务状态中心

  U->>FE: 帮我补齐这批客户表字段备注
  FE->>GW: 提交自然语言 + 资产范围
  GW->>GW: 认证鉴权、资产权限校验、审计
  GW->>API: 转发任务请求
  API->>R: 调用 LangGraph
  R->>R: 识别 GOVERN_METADATA
  R->>State: 创建元数据治理子任务
  R->>G: 调用元数据治理 Agent
  G->>M: 读取表字段、已有中文名、备注、样例统计
  G->>O: 映射本体实体和属性
  G->>L: 获取上下游字段和加工语境
  G->>Std: 匹配数据标准和码值
  G-->>R: 生成候选中文名、业务含义、备注、证据和置信度
  R-->>API: 返回治理建议
  API-->>GW: 返回结构化响应
  GW-->>FE: 展示治理建议卡片，等待审核
  U->>FE: 修改并确认提交审核
  FE->>GW: 用户确认后的候选值
  GW->>API: 转发确认请求
  API->>R: 继续 LangGraph 任务
  R->>G: 提交治理审核
  G->>Review: submit_metadata_review
  Review-->>G: 返回审核流程 ID
  G-->>R: 治理任务已提交
  R->>State: 更新审核流程 ID 和状态
  R-->>API: 返回审核流程 ID 和状态
  API-->>GW: 返回结构化响应
  GW-->>FE: 展示审核进度入口
```

## 8. 观测与评测数据流

公司可观测平台基于 OpenTelemetry 封装，并采用 Langfuse 做 AI 观测。它不参与业务决策，只负责旁路记录、排障、评测和优化。

```mermaid
flowchart LR
  UserInput[用户输入] --> Trace[Trace Span]
  Gateway[现有 Gateway 鉴权与审计] --> Trace
  FastAPI[FastAPI 请求处理] --> Trace
  Graph[LangGraph 节点执行] --> Trace
  Intent[意图识别结果] --> Trace
  Plan[计划生成结果] --> Trace
  AgentCall[子 Agent 调用] --> Trace
  ToolCall[MCP 工具调用] --> Trace
  ES[Elasticsearch 数据地图搜索] --> Trace
  MetadataApi[元数据管理平台接口调用] --> Trace
  Rag[RAG 检索上下文] --> Trace
  ModelIO[模型输入输出] --> Trace
  Answer[最终回答] --> Trace

  Trace --> Langfuse[Langfuse<br/>Prompt / Trace / Eval / Cost / Feedback]
  Trace --> OTel[OpenTelemetry<br/>指标 / 链路 / 日志 / 告警]

  Langfuse --> Eval[离线评测<br/>意图准确率 / 推荐准确率 / 工具成功率]
  Langfuse --> Prompt[Prompt 版本管理]
  OTel --> Alert[运行告警<br/>错误率 / 延迟 / ES慢查询 / DB慢查询]
```

## 9. 数据流控制原则

1. 查询类链路可以由主 Agent 自动执行，并直接返回结果。
2. 写操作链路先生成草案或计划，再由用户确认后执行。
3. 长流程任务必须进入业务状态中心，不能只依赖大模型上下文。
4. 前端统一调用现有数据资产管理 Gateway 服务，FastAPI AI 助手服务不直接对前端暴露。
5. Gateway 负责认证、鉴权、审计和用户/组织/角色上下文透传。
6. 工具调用统一经过 MCP 工具网关，不能让 Agent 直接访问业务系统。
7. Elasticsearch 是数据地图搜索引擎，元数据采集后同步进入 ES，用于提升资产搜索和全文检索速度。
8. Oracle 是数据资产管理平台当前后端数据库，GoldenDB 是信创迁移目标数据库，Agent 优先通过平台接口访问，不直接绕过平台读写库表。
9. Langfuse 和 OpenTelemetry 只做旁路观测，不保存敏感明文。
10. 血缘、元数据、稽核、数据源登记等平台仍是权威数据源。
11. Agent 输出要结构化保存，便于恢复、审计、评测和二次治理。
