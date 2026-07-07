# 09 智能元数据补全 Demo 实施路线

## 1. 背景与修正口径

数据资产助手已经明确实施路线，并将“智能元数据补全”作为首要建设能力。

这里需要区分“入口场景”和“能力层”：

```text
单表元数据治理：用户从数据资产助手发起元数据治理，是业务入口之一。
资产盘点工单：用户从资产盘点流程进入元数据维护，是业务入口之一。
智能元数据补全：为上述入口提供候选生成、依据解释、置信度和人工确认支撑的能力层。
```

也就是说，智能元数据补全不是孤立的新业务入口，而是元数据治理、资产盘点等场景背后复用的一套能力。

需要特别修正一点：本体论只是前期讨论元数据语义补全时使用过的概念背景，本次 Demo 不建设本体平台，不接入本体模型，也不做本体实体 / 属性匹配。

本次 Demo 的建设口径是：

```text
基于现有元数据上下文、字段命名规则、历史样例、安全等级规则和 Mock AI 生成能力，
完成表中文名、表备注、字段中文名、字段备注、字段安全等级的候选生成，
并通过单表元数据治理入口或资产盘点入口发起调用，
最终形成可审计、可回写、可演示的人工确认闭环。
```

本次 Demo 重点验证的是“智能元数据补全能力如何被不同入口复用”，而不是本体论能力。

## 2. Demo 目标

### 2.1 业务目标

1. 降低技术 Owner 手工维护表中文名、字段中文名和备注的成本。
2. 提高单表元数据治理和资产盘点工单中的元数据完整度。
3. 让 AI 生成内容具备候选值、置信度、依据和人工确认闭环。
4. 证明数据资产助手可以沉淀可复用能力层，而不是只做单次问答。

### 2.2 技术目标

1. 验证 `Gateway Mock -> FastAPI -> 编排节点 -> Mock Tool -> 本地 JSON` 的最小链路。
2. 验证智能预填能力可以被不同业务入口调用。
3. 验证候选值、置信度、依据、人工修改和最终提交值的结构化表达。
4. 为后续接入真实元数据 API、安全等级确认接口、GoldenDB、Activiti 预留边界。

## 3. 本次 Demo 不做什么

为了控制范围，首版 Demo 明确不做以下内容：

| 不做内容 | 原因 |
| --- | --- |
| 不建设本体平台 | 本体论只是前期概念背景，首版不作为实现依赖 |
| 不做本体实体 / 属性匹配 | 避免把 Demo 做成语义平台建设项目 |
| 不接真实生产元数据 | 先用 Mock 数据证明链路和交互 |
| 不接真实大模型 | 先用规则和样例生成稳定演示结果 |
| 不直接回写正式元数据 | AI 只生成候选值，最终以人工确认值为准 |
| 不做批量任务 | 首版聚焦单表工单，避免调度和大规模状态管理干扰 |
| 不新增独立审批流程 | 复用单表元数据治理或资产盘点工单流程口径 |

## 4. 能力层定位

智能元数据补全在数据资产助手中应定位为公共能力层。

```text
入口层：数据资产助手对话入口 / 元数据治理入口 / 资产盘点工单入口
编排层：识别发起来源、资产对象、补全范围、确认方式
能力层：智能元数据补全能力
执行层：元数据上下文查询、规则命中、历史样例匹配、安全等级推荐、候选生成
确认层：人工确认、人工修改、提交、审计留痕
```

推荐调用关系：

```text
单表元数据治理
  -> 调用智能元数据补全能力
  -> 生成治理草案中的表字段候选值
  -> 用户确认后提交治理流程

资产盘点工单
  -> 调用智能元数据补全能力
  -> 写入盘点任务候选区
  -> 技术 Owner 确认后进入盘点提交

后续批量补全任务
  -> 调用智能元数据补全能力
  -> 生成批量候选结果
  -> 按规则进入抽样审核或强审核
```

## 5. 元数据治理 Agent 与智能元数据补全的关系

元数据治理 Agent 是面向元数据治理全流程的领域 Agent，智能元数据补全是它的一期核心能力之一。

推荐分层：

```text
元数据治理 Agent：领域负责人 / 编排者
智能元数据补全能力：一期重点建设能力
数据地图 Agent：提供资产、表、字段、负责人、已有备注等上下文
数据标准 Agent：提供标准术语、字段标准、命名规范和标准映射依据
安全扫描 Agent：提供敏感字段识别、安全等级推荐和定级依据
数据血缘 Agent：提供上下游使用场景、加工任务和影响范围
Tool Adapter：真正调用现有 Java API、ES、安全扫描接口、标准接口等平台能力
```

元数据治理 Agent 不只包含智能元数据补全，还可以逐步扩展以下能力：

```text
元数据缺失诊断
智能元数据补全
数据标准匹配
安全等级推荐与确认
字段备注质量检查
元数据治理草案生成
元数据治理流程提交
治理任务状态跟踪
治理质量复盘
```

本次 Demo 不要求一次性实现完整元数据治理 Agent，而是先落地其中最容易形成业务价值和演示闭环的能力：

```text
元数据治理 Agent 首期能力：智能元数据补全
```

在单表元数据治理入口下，推荐编排链路为：

```text
用户发起单表元数据治理
  -> 元数据治理 Agent 接管
  -> 调用数据地图 Agent 获取表字段上下文
  -> 调用数据标准 Agent 获取标准映射和命名依据
  -> 调用安全扫描 Agent 获取字段安全等级推荐
  -> 可选调用数据血缘 Agent 补充上下游使用依据
  -> 调用智能元数据补全能力生成候选值、置信度和依据
  -> 用户确认或修改
  -> 生成治理草案
  -> 提交治理流程或 Mock 治理任务
```

因此，对外汇报时可以使用如下口径：

```text
本次 Demo 是“元数据治理 Agent 首期能力：智能元数据补全”。
元数据治理 Agent 负责组织数据地图、数据标准、安全扫描等专业 Agent 协同工作。
智能元数据补全负责把多方上下文转化为可审核的中文名、备注、安全等级候选值和生成依据。
```

## 6. Demo 主线场景

建议首版演示一个“单表元数据治理入口调用智能元数据补全能力”的链路，同时在文档和页面上说明该能力也可被资产盘点入口复用。

示例资产：

```text
表名：dwd_customer_income_df
主题：客户收入明细
问题：表中文名、表备注、部分字段中文名、字段备注和安全等级不完整
```

用户故事：

```text
作为数据资产技术 Owner，
我在数据资产助手中发起单表元数据治理，
系统自动调用智能元数据补全能力生成候选值，
我可以查看 AI 候选值、置信度和生成依据，
对不准确内容进行修改，
最后确认并提交元数据治理流程。
```

资产盘点入口复用口径：

```text
同一套智能元数据补全能力也可以在资产盘点工单创建或资产分派后自动触发，
将候选值写入盘点任务候选区，
由技术 Owner 打开工单后确认、修改并提交。
```

## 7. 推荐演示流程

### 7.1 发起单表元数据治理

用户在数据资产助手中输入：

```text
帮我治理 dwd_customer_income_df 这张表，并补全缺失的中文名和备注。
```

助手识别为：

```text
入口场景：单表元数据治理
需要能力：智能元数据补全
补全范围：表中文名、表备注、字段中文名、字段备注、字段安全等级
```

### 7.2 展示智能补全结果

页面或对话卡片显示：

```text
任务编号：META_PREFILL_10001
发起入口：单表元数据治理
资产名称：dwd_customer_income_df
当前状态：待确认
智能补全完成时间：2026-07-07 10:30:00
```

摘要区展示：

```text
后台预填完成：表信息 2 项，字段信息 36 项，安全等级 36 项
需重点确认：8 项
低置信度：6 项
待人工补充：4 项
```

### 7.3 查看候选值

表级信息展示：

| 字段 | 原值 | AI 候选值 | 置信度 | 状态 |
| --- | --- | --- | --- | --- |
| 表中文名 | 空 | 客户收入明细表 | 高 | 待确认 |
| 表备注 | 空 | 存储客户收入统计明细，用于客户价值分析、经营分析和收入指标加工。 | 中 | 待确认 |

字段级信息展示：

| 字段名 | 类型 | 字段中文名候选 | 字段备注候选 | 安全等级推荐 | 置信度 |
| --- | --- | --- | --- | --- | --- |
| customer_id | varchar | 客户编号 | 用于标识客户在主数据系统中的唯一编码。 | 2级 | 高 |
| mobile_no | varchar | 手机号 | 客户联系手机号，属于个人敏感信息。 | 3级 | 高 |
| income_amt | decimal | 收入金额 | 客户在统计周期内产生的收入金额。 | 3级 | 中 |
| stat_dt | date | 统计日期 | 该条收入明细对应的统计日期。 | 2级 | 高 |

### 7.4 查看生成依据

用户点击置信度标签后，展示依据抽屉：

```text
字段：income_amt
候选中文名：收入金额
候选备注：客户在统计周期内产生的收入金额。
置信度：中

生成依据：
1. 字段名包含 income，命中收入相关命名规则。
2. 字段类型为 decimal，符合金额类字段特征。
3. 同表存在 customer_id、stat_dt，推断该字段与客户统计周期有关。
4. 安全等级规则建议金额类字段为 3 级。

风险提示：
缺少明确业务口径，建议人工确认是否为税前收入、税后收入或实收收入。
```

### 7.5 人工修改

用户可以修改候选值。

修改后字段状态变为：

```text
人工修改
```

后台重新生成或刷新任务时，不允许覆盖人工修改内容。

### 7.6 确认提交

提交时校验：

1. 表中文名不能为空。
2. 字段中文名不能为空。
3. 3级 / 4级安全等级必须确认。
4. 低置信度项需要提示用户重点检查。
5. 待人工补充项未完成时阻止提交或提示定位。

提交后展示：

```text
智能元数据补全已确认提交
已确认表信息：2 项
已确认字段信息：36 项
人工修改：5 项
安全等级确认：36 项
Mock 治理任务编号：GOV_META_202607070001
```

## 8. 后端接口设计

首版可以保留现有 `/assistant/chat`，同时新增专用接口，便于前端页面直接调用。

### 8.1 发起预填任务

```http
POST /assistant/metadata-prefill/start
```

请求示例：

```json
{
  "thread_id": "T_META_PREFILL_10001",
  "asset_id": "asset_001",
  "table_name": "dwd_customer_income_df",
  "user_context": {
    "user_id": "zhangsan",
    "user_name": "张三",
    "role_codes": ["data_steward"],
    "trace_id": "trace-meta-prefill-001"
  }
}
```

响应示例：

```json
{
  "task_id": "META_PREFILL_10001",
  "status": "PREFILLING",
  "message": "智能元数据补全任务已创建，正在后台生成候选值。"
}
```

### 8.2 查询预填结果

```http
GET /assistant/metadata-prefill/tasks/{task_id}
```

响应核心结构：

```json
{
  "task_id": "META_PREFILL_10001",
  "status": "WAITING_CONFIRM",
  "asset": {
    "asset_id": "asset_001",
    "table_name": "dwd_customer_income_df",
    "suggested_chinese_name": "客户收入明细表",
    "suggested_comment": "存储客户收入统计明细，用于客户价值分析、经营分析和收入指标加工。",
    "confidence": "medium"
  },
  "summary": {
    "table_items": 2,
    "field_items": 36,
    "security_items": 36,
    "need_confirm": 8,
    "low_confidence": 6,
    "need_supplement": 4
  },
  "fields": []
}
```

### 8.3 查看生成依据

```http
GET /assistant/metadata-prefill/tasks/{task_id}/evidence/{field_name}
```

### 8.4 提交确认结果

```http
POST /assistant/metadata-prefill/tasks/{task_id}/confirm
```

提交时保存：

```text
AI 原始候选值
人工最终值
人工修改标记
置信度
生成依据
安全等级推荐结果
确认人
确认时间
trace_id
```

### 8.5 重新生成

```http
POST /assistant/metadata-prefill/tasks/{task_id}/regenerate
```

规则：

```text
只重新生成未确认、未人工修改、仍为空或失败的项。
不得覆盖人工修改内容。
```

## 9. 编排流程设计

首版采用 LangGraph 风格状态机即可，后续再替换为真实 LangGraph `StateGraph`。

### 9.1 主流程

```text
receive_request
  -> load_asset_context
  -> load_history_examples
  -> apply_naming_rules
  -> recommend_security_level
  -> generate_metadata_candidates
  -> score_confidence
  -> build_review_payload
  -> wait_human_confirm
  -> submit_mock_governance
  -> final_answer
```

### 9.2 状态流转

```text
CREATED
  -> PREFILLING
  -> WAITING_CONFIRM
  -> SUBMITTED
  -> COMPLETED
```

异常状态：

```text
PARTIAL_NEED_SUPPLEMENT
PREFILL_FAILED
CONFIRM_REJECTED
```

### 9.3 State 字段

```json
{
  "task_id": "META_PREFILL_10001",
  "thread_id": "T_META_PREFILL_10001",
  "asset_id": "asset_001",
  "table_name": "dwd_customer_income_df",
  "status": "WAITING_CONFIRM",
  "asset_context": {},
  "history_examples": [],
  "naming_rule_hits": [],
  "security_recommendations": [],
  "prefill_candidates": [],
  "confidence_summary": {},
  "human_edits": [],
  "final_values": [],
  "audit_events": []
}
```

## 10. Mock 数据设计

建议新增目录：

```text
数据资产助手/demo/app/mock_data/metadata_prefill/
```

文件规划：

| 文件 | 用途 |
| --- | --- |
| `asset_context.json` | 表和字段原始技术元数据 |
| `history_examples.json` | 历史已审核元数据样例 |
| `naming_rules.json` | 字段命名规则和缩写词典 |
| `security_rules.json` | 安全等级规则命中结果 |
| `prefill_result.json` | 预期生成候选结果 |
| `task_status.json` | 预填任务状态样例 |

字段候选结果结构：

```json
{
  "field_name": "mobile_no",
  "field_type": "varchar",
  "original_comment": "",
  "suggested_chinese_name": "手机号",
  "suggested_comment": "客户联系手机号，属于个人敏感信息。",
  "recommended_security_level": "3",
  "confidence": "high",
  "source": "rule_mock",
  "evidence": [
    "字段名 mobile_no 命中手机号命名规则",
    "字段类型为 varchar",
    "安全等级规则建议手机号为 3 级"
  ],
  "risk_tips": [
    "手机号属于个人敏感信息，提交前需要人工确认安全等级"
  ],
  "review_status": "pending"
}
```

## 11. 页面设计建议

Demo 前端可以直接做一个轻量 HTML 页面，不需要先改造真实平台页面。

页面包含四个区：

1. 工单摘要区。
2. 表级预填区。
3. 字段明细表格区。
4. 依据抽屉 / 确认提交区。

重点交互：

```text
只看待处理项
查看生成依据
编辑候选值
标记已确认
提交确认结果
重新生成失败项
```

页面文案必须强调：

```text
AI 只生成候选值，不直接发布正式元数据。
最终以人工确认后的内容为准。
```

## 12. 与现有数据资产助手 Demo 的关系

现有 Demo 已经实现单表元数据治理主链路：

```text
找表 -> 确认资产 -> 查询标准 / 血缘 / 安全 -> 生成治理草案 -> 提交 Mock Activiti
```

需要修正为：单表元数据治理不是和智能元数据补全并列的另一条孤立链路，二者是“入口场景”和“能力实现”的关系。

```text
入口场景：单表元数据治理
实现能力：智能元数据补全
后续入口：资产盘点工单 / 批量补全任务 / 元数据质量整改任务
```

推荐改造后的单表元数据治理链路：

```text
找表
  -> 确认资产
  -> 调用智能元数据补全能力
  -> 展示表字段候选值、置信度和依据
  -> 用户修改和确认
  -> 生成治理草案
  -> 提交 Mock Activiti 或 Mock 治理任务
```

资产盘点复用链路：

```text
资产盘点工单创建 / 资产分派
  -> 后台调用智能元数据补全能力
  -> 候选值写入盘点任务候选区
  -> 技术 Owner 打开工单确认
  -> 提交盘点结果
```

因此，Demo 建议沉淀一套公共能力模块：

```text
metadata_prefill_tool
metadata_prefill_state
metadata_prefill_api
metadata_prefill_ui
metadata_prefill_mock_data
```

再由不同入口调用：

```text
governance_entry -> metadata_prefill_capability
inventory_entry -> metadata_prefill_capability
batch_task_entry -> metadata_prefill_capability
```

## 13. 开发拆解

### 第 1 步：补 Mock 数据

交付物：

```text
asset_context.json
history_examples.json
naming_rules.json
security_rules.json
prefill_result.json
```

验收标准：

```text
至少包含 1 张表、10 个字段、3 种置信度、2 个安全等级重点确认项、1 个待人工补充项。
```

### 第 2 步：实现预填 Tool

交付物：

```text
app/tools/metadata_prefill_tool.py
```

核心函数：

```text
load_asset_context
load_history_examples
apply_naming_rules
recommend_security_level
generate_prefill_candidates
score_confidence
```

### 第 3 步：实现状态编排

交付物：

```text
app/agents/metadata_prefill.py
app/graph/metadata_prefill_nodes.py
```

首版可以用普通 Python 函数模拟节点流转。

### 第 4 步：实现 API

交付物：

```text
POST /assistant/metadata-prefill/start
GET  /assistant/metadata-prefill/tasks/{task_id}
GET  /assistant/metadata-prefill/tasks/{task_id}/evidence/{field_name}
POST /assistant/metadata-prefill/tasks/{task_id}/confirm
POST /assistant/metadata-prefill/tasks/{task_id}/regenerate
```

### 第 5 步：实现页面

交付物：

```text
智能元数据补全 Demo 页面
```

页面必须展示：

```text
预填状态
候选值
置信度
生成依据
安全等级推荐
人工修改
确认提交
```

### 第 6 步：补测试

测试重点：

```text
预填任务能创建
预填结果能查询
高 / 中 / 低置信度能正确汇总
安全等级 3/4 级能进入重点确认
人工修改不会被重新生成覆盖
确认提交后有最终结果和审计摘要
```

## 14. 演示脚本

### 14.1 开场

```text
这次 Demo 演示元数据治理 Agent 的首期能力：智能元数据补全。
它不是一个孤立入口，而是支撑单表元数据治理、资产盘点等入口的公共能力。
元数据治理 Agent 会协同数据地图、数据标准、安全扫描等专业 Agent，为补全生成提供上下文和依据。
它不建设本体平台，也不直接修改正式元数据。
它的目标是把现有技术元数据自动生成可审核的中文名、备注和安全等级候选，帮助技术 Owner 更快完成元数据治理或资产盘点确认。
```

### 14.2 演示过程

```text
第一步，从数据资产助手发起单表元数据治理。
第二步，元数据治理 Agent 接管并调用智能元数据补全能力。
第三步，系统协同数据地图、数据标准、安全扫描等专业 Agent 获取上下文。
第四步，查看表中文名、表备注和字段候选值。
第五步，点击置信度查看生成依据。
第六步，修改一个中置信度候选。
第七步，确认 3 级安全等级。
第八步，提交确认结果并生成治理草案或治理任务。
```

### 14.3 收尾

```text
这个 Demo 证明了数据资产助手不仅能回答问题，还能通过元数据治理 Agent 沉淀可被多个入口复用的元数据补全能力。
AI 负责生成候选和依据，人负责最终确认，平台负责状态、审计和后续流程。
后续只需要把 Mock Tool 替换为真实元数据接口、安全等级确认接口和治理流程接口，就可以进入试点。
```

## 15. 一期后续演进

Demo 跑通后再做以下增强：

1. 接入真实元数据详情接口。
2. 接入真实安全等级确认接口。
3. 接入 GoldenDB 保存任务状态、候选值、最终值和审计摘要。
4. 接入 Activiti 或现有盘点工单提交接口。
5. 接入真实 LLM 生成表备注和字段备注。
6. 增加批量预填任务。
7. 引入 LangGraph `StateGraph` 和 checkpoint。
8. 增加 OpenTelemetry / Langfuse 观测链路。

## 16. 关键结论

本次智能元数据补全 Demo 的成功标准不是“是否完整实现本体论”，而是：

```text
能不能把一个待补全元数据工单，
从候选生成、依据解释、人工确认、最终提交、审计留痕，
完整跑成一个可演示、可复用、可继续接真实接口的闭环。
```
