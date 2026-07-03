# 数据资产助手 Demo

这个 Demo 用于验证数据资产助手的最小可行链路：

```text
Gateway Mock -> FastAPI -> LangGraph 风格编排 -> Mock Tool Adapter -> 本地 JSON 数据
```

首版先实现单表元数据治理主链路：

1. 用户输入表名。
2. 查询同名表候选。
3. 用户确认唯一资产和治理上下文。
4. 调用数据标准、血缘、安全扫描等 Mock Tool。
5. 生成治理草案。
6. 用户确认后提交 Mock Activiti 流程。

## 启动

```bash
cd 数据资产助手/demo
python -m venv .venv
source .venv/bin/activate
pip install -e .
uvicorn app.main:app --reload --port 8010
```

## 示例请求

```bash
curl -X POST http://127.0.0.1:8010/assistant/chat \
  -H 'Content-Type: application/json' \
  -d '{
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
  }'
```

继续确认：

```bash
curl -X POST http://127.0.0.1:8010/assistant/confirm \
  -H 'Content-Type: application/json' \
  -d '{
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
  }'
```

## 当前取舍

- 不连接真实 Gateway、ES、Oracle、GoldenDB、Activiti。
- 不保存明文 token、密码、连接串。
- 编排实现采用 LangGraph 风格状态机，保留后续替换为真实 LangGraph `StateGraph` 的边界。

