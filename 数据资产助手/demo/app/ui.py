INDEX_HTML = """
<!doctype html>
<html lang="zh-CN">
  <head>
    <meta charset="utf-8" />
    <meta name="viewport" content="width=device-width, initial-scale=1" />
    <title>数据资产助手 Demo</title>
    <style>
      :root {
        --bg: #f4f7fb;
        --panel: #ffffff;
        --line: #d8dee8;
        --text: #1f2937;
        --muted: #667085;
        --blue: #2563eb;
        --blue-weak: #eef5ff;
        --green: #16803c;
        --green-weak: #eefaf2;
        --amber: #b7791f;
        --amber-weak: #fff7e6;
        --red: #c2410c;
        --red-weak: #fff0ea;
      }

      * { box-sizing: border-box; }
      body {
        margin: 0;
        min-height: 100vh;
        background: var(--bg);
        color: var(--text);
        font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", "PingFang SC", "Microsoft YaHei", sans-serif;
        font-size: 14px;
      }

      button, input, select { font: inherit; }
      button { cursor: pointer; }

      .topbar {
        height: 58px;
        display: flex;
        justify-content: space-between;
        align-items: center;
        padding: 0 20px;
        border-bottom: 1px solid var(--line);
        background: #fff;
      }

      .brand { display: flex; align-items: center; gap: 12px; }
      .logo {
        width: 34px;
        height: 34px;
        display: grid;
        place-items: center;
        border-radius: 8px;
        color: #fff;
        background: #1d4ed8;
        font-weight: 800;
      }
      .brand h1 { margin: 0; font-size: 18px; }
      .brand p { margin: 2px 0 0; color: var(--muted); font-size: 12px; }

      .toplinks { display: flex; gap: 10px; align-items: center; }
      .toplinks a {
        color: #2563eb;
        text-decoration: none;
        font-weight: 700;
        font-size: 13px;
      }

      .layout {
        min-height: calc(100vh - 58px);
        display: grid;
        grid-template-columns: minmax(640px, 1fr) 340px;
        gap: 14px;
        padding: 14px;
      }

      .panel {
        min-width: 0;
        background: var(--panel);
        border: 1px solid var(--line);
        border-radius: 8px;
      }

      .title { font-weight: 800; font-size: 13px; color: #344054; margin-bottom: 10px; }
      .quick-list {
        margin-top: 10px;
        display: flex;
        gap: 8px;
        flex-wrap: wrap;
      }
      .quick-btn {
        min-height: 30px;
        border-radius: 999px;
        border: 1px solid #bfdbfe;
        background: var(--blue-weak);
        color: #1d4ed8;
        padding: 0 11px;
        font-weight: 700;
        font-size: 12px;
      }

      .chat-panel {
        display: grid;
        grid-template-rows: auto 1fr auto;
        min-height: calc(100vh - 86px);
        overflow: hidden;
      }
      .chat-head {
        padding: 14px 16px;
        border-bottom: 1px solid var(--line);
        display: grid;
        grid-template-columns: 1fr auto;
        gap: 10px 12px;
        align-items: start;
      }
      .chat-head h2 { margin: 0; font-size: 16px; }
      .chat-head p { margin: 3px 0 0; color: var(--muted); font-size: 12px; }
      .chat {
        padding: 16px;
        overflow: auto;
        display: flex;
        flex-direction: column;
        gap: 12px;
      }
      .msg { display: flex; gap: 10px; align-items: flex-start; max-width: 920px; }
      .msg.user { align-self: flex-end; flex-direction: row-reverse; }
      .avatar {
        width: 30px;
        height: 30px;
        border-radius: 50%;
        display: grid;
        place-items: center;
        flex: 0 0 auto;
        color: #fff;
        background: var(--green);
        font-size: 12px;
        font-weight: 800;
      }
      .avatar.user { background: #1d4ed8; }
      .bubble {
        padding: 10px 12px;
        border: 1px solid var(--line);
        border-radius: 8px;
        background: #fff;
        line-height: 1.65;
      }
      .msg.user .bubble { color: #fff; background: #1d4ed8; border-color: #1d4ed8; }

      .composer {
        padding: 12px;
        border-top: 1px solid var(--line);
        display: grid;
        grid-template-columns: 1fr auto;
        gap: 10px;
        background: #fff;
      }
      .composer input {
        height: 38px;
        border-radius: 7px;
        border: 1px solid var(--line);
        padding: 0 12px;
        min-width: 0;
      }

      .btn {
        min-height: 32px;
        border-radius: 7px;
        border: 1px solid var(--line);
        background: #fff;
        color: #344054;
        padding: 0 12px;
        font-weight: 700;
      }
      .btn.primary { color: #fff; background: var(--blue); border-color: var(--blue); }
      .btn.primary:hover { background: #1d4ed8; border-color: #1d4ed8; }

      .cards { display: grid; gap: 10px; margin-top: 8px; }
      .card {
        border: 1px solid var(--line);
        border-radius: 8px;
        overflow: hidden;
        background: #fff;
      }
      .card-head {
        padding: 10px 12px;
        background: #f9fafb;
        border-bottom: 1px solid var(--line);
        display: flex;
        justify-content: space-between;
        gap: 8px;
        align-items: center;
      }
      .card-body { padding: 12px; }
      .table {
        width: 100%;
        border-collapse: collapse;
        font-size: 12px;
      }
      .table th, .table td {
        border-bottom: 1px solid #edf0f5;
        padding: 8px;
        text-align: left;
        vertical-align: top;
      }
      .table th { color: var(--muted); font-weight: 700; background: #fbfcfe; }

      .badge {
        display: inline-flex;
        align-items: center;
        min-height: 23px;
        padding: 0 8px;
        border-radius: 999px;
        font-size: 12px;
        border: 1px solid var(--line);
        background: #f9fafb;
        color: #475467;
        white-space: nowrap;
      }
      .badge.blue { color: #1d4ed8; background: var(--blue-weak); border-color: #bfdbfe; }
      .badge.green { color: #137333; background: var(--green-weak); border-color: #b7e4c7; }
      .badge.amber { color: #915f00; background: var(--amber-weak); border-color: #f5d28a; }

      .right-section { padding: 14px; border-bottom: 1px solid var(--line); }
      .right-section:last-child { border-bottom: 0; }
      .kv { display: grid; grid-template-columns: 86px 1fr; gap: 8px; font-size: 12px; }
      .kv div:nth-child(odd) { color: var(--muted); }
      .steps { display: grid; gap: 10px; margin-top: 10px; }
      .step { display: grid; grid-template-columns: 22px 1fr; gap: 8px; align-items: start; }
      .dot {
        width: 20px;
        height: 20px;
        border-radius: 50%;
        display: grid;
        place-items: center;
        font-size: 11px;
        border: 1px solid var(--line);
        background: #fff;
        color: var(--muted);
      }
      .step.done .dot { color: #fff; background: var(--green); border-color: var(--green); }
      .step.active .dot { color: #fff; background: var(--blue); border-color: var(--blue); }
      .step strong { display: block; font-size: 12px; margin-bottom: 2px; }
      .step span { color: var(--muted); font-size: 12px; line-height: 1.4; }

      .tool-list { display: grid; gap: 8px; font-size: 12px; }
      .tool-item { padding: 8px; border: 1px solid #edf0f5; border-radius: 7px; background: #fbfcfe; }
      .tool-item strong { display: block; margin-bottom: 3px; color: #344054; }
      .empty { color: var(--muted); font-size: 12px; }

      .modal {
        position: fixed;
        inset: 0;
        display: none;
        place-items: center;
        padding: 22px;
        background: rgba(15, 23, 42, 0.36);
        z-index: 20;
      }
      .modal.open { display: grid; }
      .modal-panel {
        width: min(780px, 100%);
        max-height: 90vh;
        overflow: auto;
        background: #fff;
        border: 1px solid var(--line);
        border-radius: 8px;
      }
      .form-grid {
        display: grid;
        grid-template-columns: repeat(3, minmax(0, 1fr));
        gap: 10px;
      }
      label {
        display: grid;
        gap: 5px;
        color: #344054;
        font-size: 12px;
        font-weight: 700;
      }
      label input, label select {
        height: 34px;
        border: 1px solid var(--line);
        border-radius: 6px;
        padding: 0 9px;
        color: var(--text);
        font-weight: 400;
      }
      .option-line {
        display: flex;
        align-items: center;
        gap: 8px;
        min-height: 34px;
        padding: 0 10px;
        border: 1px solid var(--line);
        border-radius: 6px;
        background: #f9fafb;
        color: #344054;
        font-size: 12px;
        font-weight: 700;
      }
      .option-line input {
        width: 15px;
        height: 15px;
        margin: 0;
        accent-color: var(--blue);
      }
      .modal-actions {
        margin-top: 14px;
        display: flex;
        justify-content: flex-end;
        gap: 8px;
      }
    </style>
  </head>
  <body>
    <header class="topbar">
      <div class="brand">
        <div class="logo">智</div>
        <div>
          <h1>数小智 · 数据资产助手 Demo</h1>
          <p>FastAPI + LangGraph 风格编排 + Mock Tool Adapter</p>
        </div>
      </div>
      <div class="toplinks">
        <a href="/docs" target="_blank">接口文档</a>
        <a href="/health" target="_blank">健康检查</a>
      </div>
    </header>

    <main class="layout">
      <section class="panel chat-panel">
        <div class="chat-head">
          <div>
            <h2>数据资产助手</h2>
            <p>输入你的数据资产问题，我会自动路由到数据源、数据地图、血缘或治理 Agent。</p>
            <div class="quick-list" id="quickQuestions"></div>
          </div>
          <button class="btn" id="resetBtn">重置对话</button>
        </div>
        <div class="chat" id="chat"></div>
        <div class="composer">
          <input id="questionInput" />
          <button class="btn primary" id="sendBtn">发送</button>
        </div>
      </section>

      <aside class="panel">
        <div class="right-section">
          <div class="title">当前任务</div>
          <div class="kv" id="taskKv"></div>
        </div>
        <div class="right-section">
          <div class="title">链路步骤</div>
          <div class="steps" id="steps"></div>
        </div>
        <div class="right-section">
          <div class="title">Tool 调用</div>
          <div class="tool-list" id="toolList"></div>
        </div>
      </aside>
    </main>

    <div class="modal" id="datasourceModal">
      <div class="modal-panel">
        <div class="card-head">
          <strong>请确认数据源登记信息</strong>
          <button class="btn" id="closeDatasourceModal">关闭</button>
        </div>
        <div class="card-body">
          <div class="form-grid">
            <label>数据源名称<input id="dsName" /></label>
            <label>数据库类型<select id="dsType"><option>MySQL</option><option>Oracle</option><option>GoldenDB</option></select></label>
            <label>环境<select id="dsEnv"><option>PRD</option><option>UAT</option><option>DEV</option></select></label>
            <label>Host<input id="dsHost" /></label>
            <label>端口<input id="dsPort" /></label>
            <label>负责人<input id="dsOwner" /></label>
            <div class="option-line"><input id="dsCollect" type="checkbox" />立即采集元数据</div>
            <div class="option-line"><input id="dsScan" type="checkbox" />采集完成后安全扫描</div>
            <div class="option-line"><input id="dsSync" type="checkbox" />同步 ES 数据地图</div>
          </div>
          <div class="modal-actions">
            <button class="btn" id="mockConnBtn">连通性检测</button>
            <button class="btn primary" id="submitDatasourceBtn">确认提交登记流程</button>
          </div>
        </div>
      </div>
    </div>

    <div class="modal" id="decisionModal">
      <div class="modal-panel">
        <div class="card-head">
          <strong id="decisionTitle">确认下一步</strong>
          <button class="btn" id="closeDecisionModal">关闭</button>
        </div>
        <div class="card-body">
          <p id="decisionText" style="margin:0;color:#344054;line-height:1.7;"></p>
          <div class="modal-actions">
            <button class="btn" id="decisionNoBtn">暂不处理</button>
            <button class="btn primary" id="decisionYesBtn">是，立即执行</button>
          </div>
        </div>
      </div>
    </div>

    <script>
      const commonQuestions = [
        "如何登记数据源？",
        "帮我登记一个生产 MySQL 数据源，同时采集元数据并做安全扫描",
        "帮我治理 dwd_customer_income_df 这张表",
        "帮我治理 dwd_customer_income_df 这张表，并补全缺失的中文名和备注",
        "客户收入用哪张表？",
        "dwd_customer_income_df 的上游来源和加工任务说明是什么？"
      ];

      let latestResponse = null;
      let datasourceFormPayload = null;
      let decisionPayload = null;
      const sessionId = "S_WEB_DEMO";
      const threadId = "T_WEB_DEMO";
      const userContext = {
        user_id: "zhangsan",
        user_name: "张三",
        org_id: "data_center",
        role_codes: ["data_steward"],
        trace_id: "trace-web-demo",
        access_token: "mock-token"
      };

      const chat = document.getElementById("chat");
      const questionInput = document.getElementById("questionInput");

      function init() {
        renderQuickQuestions();
        resetConversation();
        document.getElementById("sendBtn").addEventListener("click", sendQuestion);
        document.getElementById("resetBtn").addEventListener("click", resetConversation);
        document.getElementById("closeDatasourceModal").addEventListener("click", closeDatasourceModal);
        document.getElementById("mockConnBtn").addEventListener("click", () => addMessage("assistant", "连通性检测通过，当前为 Mock 检测结果。"));
        document.getElementById("submitDatasourceBtn").addEventListener("click", submitDatasourceForm);
        document.getElementById("closeDecisionModal").addEventListener("click", closeDecisionModal);
        document.getElementById("decisionNoBtn").addEventListener("click", closeDecisionModal);
        document.getElementById("decisionYesBtn").addEventListener("click", submitDecision);
        document.getElementById("datasourceModal").addEventListener("click", event => {
          if (event.target.id === "datasourceModal") closeDatasourceModal();
        });
        document.getElementById("decisionModal").addEventListener("click", event => {
          if (event.target.id === "decisionModal") closeDecisionModal();
        });
        questionInput.addEventListener("keydown", event => {
          if (event.key === "Enter") sendQuestion();
        });
      }

      function renderQuickQuestions() {
        const list = document.getElementById("quickQuestions");
        list.innerHTML = "";
        commonQuestions.forEach(question => {
          const btn = document.createElement("button");
          btn.className = "quick-btn";
          btn.textContent = question;
          btn.addEventListener("click", () => {
            questionInput.value = question;
            sendQuestion();
          });
          list.appendChild(btn);
        });
      }

      function resetConversation() {
        latestResponse = null;
        questionInput.value = "如何登记数据源？";
        chat.innerHTML = "";
        addMessage("assistant", "你好，我是数据资产助手。你可以直接问我如何登记数据源、治理某张表、查找推荐表或查看血缘。");
        renderSteps([
          ["active", "等待问题", "输入自然语言问题"],
          ["", "意图识别", "自动路由到对应 Agent"],
          ["", "执行链路", "调用 Mock Tool 并展示结果"]
        ]);
        renderTask(null);
        renderTools([]);
      }

      function addMessage(role, html) {
        const row = document.createElement("div");
        row.className = "msg " + role;
        row.innerHTML = `<div class="avatar ${role === "user" ? "user" : ""}">${role === "user" ? "我" : "AI"}</div><div class="bubble">${html}</div>`;
        chat.appendChild(row);
        chat.scrollTop = chat.scrollHeight;
      }

      async function sendQuestion() {
        const question = questionInput.value.trim();
        if (!question) return;
        addMessage("user", escapeHtml(question));
        setBusy(true);
        try {
          const response = await postJson("/assistant/chat", {
            session_id: sessionId,
            thread_id: threadId,
            question,
            user_context: userContext
          });
          handleResponse(response);
        } catch (error) {
          addMessage("assistant", `<span style="color:#c2410c;">请求失败：${escapeHtml(error.message)}</span>`);
        } finally {
          setBusy(false);
        }
      }

      async function refreshTask() {
        if (!latestResponse || !latestResponse.task_id) return;
        setBusy(true);
        try {
          const response = await postJson(`/assistant/tasks/${latestResponse.task_id}/refresh`, {});
          handleResponse(response);
        } catch (error) {
          addMessage("assistant", `<span style="color:#c2410c;">刷新失败：${escapeHtml(error.message)}</span>`);
        } finally {
          setBusy(false);
        }
      }

      async function confirmAction(actionPayload = {}) {
        if (!latestResponse || !latestResponse.need_confirm || !latestResponse.need_confirm.required) return;
        setBusy(true);
        try {
          const response = await postJson("/assistant/confirm", {
            thread_id: latestResponse.thread_id,
            task_id: latestResponse.task_id,
            confirm_id: latestResponse.need_confirm.confirm_id,
            confirmed: true,
            payload: actionPayload
          });
          handleResponse(response);
        } catch (error) {
          addMessage("assistant", `<span style="color:#c2410c;">确认失败：${escapeHtml(error.message)}</span>`);
        } finally {
          setBusy(false);
        }
      }

      async function postJson(url, payload) {
        const res = await fetch(url, {
          method: "POST",
          headers: {"Content-Type": "application/json"},
          body: JSON.stringify(payload)
        });
        if (!res.ok) throw new Error(await res.text());
        return res.json();
      }

      function handleResponse(response) {
        latestResponse = response;
        addMessage("assistant", escapeHtml(response.answer));
        const datasourceFormCard = (response.cards || []).find(card => card.type === "datasource_register_form");
        const visibleCards = (response.cards || []).filter(card => card.type !== "datasource_register_form");
        if (visibleCards.length) {
          const wrap = document.createElement("div");
          wrap.className = "cards";
          visibleCards.forEach(card => wrap.appendChild(renderCard(card, response)));
          const row = document.createElement("div");
          row.className = "msg";
          row.innerHTML = `<div class="avatar">AI</div>`;
          const bubble = document.createElement("div");
          bubble.className = "bubble";
          bubble.appendChild(wrap);
          row.appendChild(bubble);
          chat.appendChild(row);
          chat.scrollTop = chat.scrollHeight;
        }
        renderTask(response);
        renderTools(response.tool_calls || []);
        renderStepsByResponse(response);
        if (datasourceFormCard) {
          addMessage("assistant", "已弹出数据源登记确认窗口，请在弹窗中补充信息并确认提交。");
          openDatasourceModal(datasourceFormCard.data.form);
        }
        if (response.need_confirm.type === "start_security_scan") {
          openDecisionModal("是否立即进行安全扫描？", "元数据采集已完成。是否立即调用安全扫描 Agent，对该数据源采集到的元数据执行安全扫描？", {run_security_scan: true});
        }
        if (response.need_confirm.type === "create_security_ticket") {
          openDecisionModal("是否生成安全等级确认工单？", "安全扫描已完成。是否立即发起元数据及安全等级确认工单？", {create_ticket: true});
        }
      }

      function renderCard(card, response) {
        const el = document.createElement("div");
        el.className = "card";
        el.innerHTML = `<div class="card-head"><strong>${escapeHtml(card.title)}</strong><span class="badge blue">${escapeHtml(card.type)}</span></div><div class="card-body"></div>`;
        const body = el.querySelector(".card-body");
        if (card.type === "asset_candidates") renderAssetCandidates(body, card);
        else if (card.type === "metadata_prefill_review") renderMetadataPrefill(body, card);
        else if (card.type === "metadata_governance_draft") renderGovernanceDraft(body, card);
        else if (card.type === "process_status") renderProcessStatus(body, card);
        else if (card.type === "datasource_status") renderDatasourceStatus(body, card);
        else if (card.type === "datasource_prepare_task") renderDatasourceStatus(body, card);
        else if (card.type === "lineage_summary") renderJsonCard(body, card.data);
        else if (card.type === "asset_recommendation") renderAssetRecommendation(body, card);
        else renderJsonCard(body, card.data);
        return el;
      }

      function renderAssetCandidates(body, card) {
        const rows = card.data.candidates.map(candidate => `
          <tr>
            <td>${escapeHtml(candidate.table_name)}</td>
            <td>${escapeHtml(candidate.datasource_id)}</td>
            <td>${escapeHtml(candidate.schema)}</td>
            <td>${candidate.certified ? '<span class="badge green">认证</span>' : '<span class="badge">普通</span>'}</td>
            <td><button class="btn primary" data-asset="${escapeHtml(candidate.asset_id)}">选择</button></td>
          </tr>
        `).join("");
        body.innerHTML = `<table class="table"><thead><tr><th>表名</th><th>数据源 ID</th><th>Schema</th><th>状态</th><th></th></tr></thead><tbody>${rows}</tbody></table>`;
        body.querySelectorAll("button[data-asset]").forEach(btn => {
          btn.addEventListener("click", () => confirmAction({
            asset_id: btn.dataset.asset,
            space_id: "space_finance",
            project_id: "project_dwd",
            dev_account: "dev_zhangsan"
          }));
        });
      }

      function renderGovernanceDraft(body, card) {
        const data = card.data;
        const fieldRows = data.field_suggestions.map(item => `
          <tr>
            <td>${escapeHtml(item.field)}</td>
            <td>${escapeHtml(item.suggested_cn_name || "")}</td>
            <td>${escapeHtml(item.suggested_comment || "")}</td>
            <td>${item.security_level ? `<span class="badge amber">${escapeHtml(item.security_level)}级</span>` : ""}</td>
            <td>${item.confidence ? confidenceBadge(item.confidence) : ""}</td>
          </tr>
        `).join("");
        body.innerHTML = `
          <div class="kv">
            <div>表名</div><div>${escapeHtml(data.table_name)}</div>
            <div>中文名</div><div>${escapeHtml(data.table_cn_name)}</div>
            <div>安全等级</div><div><span class="badge amber">${escapeHtml(data.security_level)}</span></div>
            <div>空间/项目</div><div>${escapeHtml(data.space_id)} / ${escapeHtml(data.project_id)}</div>
            <div>人工修改</div><div>${escapeHtml((data.prefill_summary || {}).manual_modified || 0)} 项</div>
          </div>
          <table class="table" style="margin-top:10px;"><thead><tr><th>字段</th><th>建议中文名</th><th>建议备注</th><th>安全等级</th><th>置信度</th></tr></thead><tbody>${fieldRows}</tbody></table>
          <div style="margin-top:10px;"><button class="btn primary" id="submitActivitiBtn">提交 Mock Activiti</button></div>
        `;
        body.querySelector("#submitActivitiBtn").addEventListener("click", () => confirmAction({asset_id: data.asset_id}));
      }

      function renderMetadataPrefill(body, card) {
        const data = card.data;
        const summary = data.summary || {};
        const asset = data.asset || {};
        const collaboration = (data.collaboration || []).map(item => `
          <tr>
            <td>${escapeHtml(item.agent)}</td>
            <td>${escapeHtml(item.contribution)}</td>
            <td>${escapeHtml((item.tools || []).join(", "))}</td>
          </tr>
        `).join("");
        const fieldRows = (data.fields || []).map(item => `
          <tr>
            <td><strong>${escapeHtml(item.field_name)}</strong><br><span class="empty">${escapeHtml(item.field_type)}</span></td>
            <td>${escapeHtml(item.suggested_cn_name || "")}</td>
            <td>${escapeHtml(item.suggested_comment || "")}</td>
            <td><span class="badge amber">${escapeHtml(item.recommended_security_level)}级</span></td>
            <td>${confidenceBadge(item.confidence)}</td>
            <td>
              <details>
                <summary>查看依据</summary>
                <ul style="margin:6px 0 0 16px;padding:0;">${(item.evidence || []).map(e => `<li>${escapeHtml(e)}</li>`).join("")}</ul>
                ${(item.risk_tips || []).length ? `<div style="margin-top:6px;color:#915f00;">${item.risk_tips.map(escapeHtml).join("<br>")}</div>` : ""}
              </details>
            </td>
          </tr>
        `).join("");
        body.innerHTML = `
          <div class="kv">
            <div>承载 Agent</div><div>元数据治理 Agent</div>
            <div>能力</div><div>智能元数据补全</div>
            <div>表名</div><div>${escapeHtml(asset.table_name)}</div>
            <div>表中文名</div><div>${escapeHtml(asset.suggested_chinese_name)}</div>
            <div>表备注</div><div>${escapeHtml(asset.suggested_comment)}</div>
          </div>
          <div style="margin-top:10px;display:flex;gap:8px;flex-wrap:wrap;">
            <span class="badge blue">字段信息 ${escapeHtml(summary.field_items || 0)} 项</span>
            <span class="badge amber">需确认 ${escapeHtml(summary.need_confirm || 0)} 项</span>
            <span class="badge amber">低置信度 ${escapeHtml(summary.low_confidence || 0)} 项</span>
            <span class="badge">待补充 ${escapeHtml(summary.need_supplement || 0)} 项</span>
          </div>
          <table class="table" style="margin-top:10px;"><thead><tr><th>协作 Agent</th><th>贡献</th><th>Tool</th></tr></thead><tbody>${collaboration}</tbody></table>
          <table class="table" style="margin-top:10px;"><thead><tr><th>字段</th><th>候选中文名</th><th>候选备注</th><th>安全等级</th><th>置信度</th><th>依据</th></tr></thead><tbody>${fieldRows}</tbody></table>
          <div style="margin-top:10px;display:flex;gap:8px;justify-content:flex-end;">
            <button class="btn" id="mockEditPrefillBtn">模拟修改 income_amt 口径</button>
            <button class="btn primary" id="confirmPrefillBtn">确认补全结果并生成治理草案</button>
          </div>
        `;
        body.querySelector("#confirmPrefillBtn").addEventListener("click", () => confirmAction({}));
        body.querySelector("#mockEditPrefillBtn").addEventListener("click", () => confirmAction({
          edits: {
            fields: {
              income_amt: {
                final_cn_name: "客户统计收入金额",
                final_comment: "客户在统计周期内产生的收入金额，口径按经营分析收入统计规则确认。",
                final_security_level: "3"
              }
            }
          }
        }));
      }

      function confidenceBadge(confidence) {
        const label = confidence === "high" ? "高" : confidence === "medium" ? "中" : "低";
        const klass = confidence === "high" ? "green" : confidence === "medium" ? "amber" : "";
        return `<span class="badge ${klass}">置信度：${label}</span>`;
      }

      function renderProcessStatus(body, card) {
        const data = card.data;
        body.innerHTML = `
          <div class="kv">
            <div>流程实例</div><div>${escapeHtml(data.process_instance_id)}</div>
            <div>流程名称</div><div>${escapeHtml(data.process_name)}</div>
            <div>状态</div><div><span class="badge green">${escapeHtml(data.status)}</span></div>
          </div>
        `;
      }

      function renderDatasourceTask(body, card) {
        const data = card.data;
        const rows = data.steps.map(step => `<tr><td>${escapeHtml(step.name)}</td><td>${escapeHtml(step.status)}</td></tr>`).join("");
        body.innerHTML = `
          <div class="kv">
            <div>数据源</div><div>${escapeHtml(data.submitted_form.datasource_name || data.register.datasource_name)}</div>
            <div>类型/环境</div><div>${escapeHtml(data.submitted_form.datasource_type || data.register.datasource_type)} / ${escapeHtml(data.submitted_form.env || data.register.env)}</div>
            <div>登记流程</div><div>${escapeHtml(data.register.register_process_id)}</div>
            <div>采集任务</div><div>${escapeHtml(data.metadata_collect.metadata_collect_task_id)}</div>
            <div>扫描任务</div><div>${escapeHtml(data.security_scan.security_scan_task_id)}</div>
          </div>
          <table class="table" style="margin-top:10px;"><thead><tr><th>步骤</th><th>状态</th></tr></thead><tbody>${rows}</tbody></table>
        `;
      }

      function renderDatasourceStatus(body, card) {
        const data = card.data;
        const datasource = data.datasource || data.submitted_form || data.register || {};
        const rows = (data.steps || []).map(step => `<tr><td>${escapeHtml(step.name)}</td><td>${escapeHtml(step.status)}</td></tr>`).join("");
        const ids = [
          data.register_process_id ? ["登记流程", data.register_process_id] : null,
          data.metadata_collect_task_id ? ["采集任务", data.metadata_collect_task_id] : null,
          data.security_scan_task_id ? ["扫描任务", data.security_scan_task_id] : null,
          data.security_ticket_id ? ["确认工单", data.security_ticket_id] : null,
          data.security_level ? ["安全等级", data.security_level] : null
        ].filter(Boolean);
        body.innerHTML = `
          <div class="kv">
            <div>数据源</div><div>${escapeHtml(datasource.datasource_name || "crm_prod_mysql")}</div>
            <div>类型/环境</div><div>${escapeHtml(datasource.datasource_type || "MySQL")} / ${escapeHtml(datasource.env || "PRD")}</div>
            ${ids.map(([key, value]) => `<div>${escapeHtml(key)}</div><div>${escapeHtml(value)}</div>`).join("")}
          </div>
          <table class="table" style="margin-top:10px;"><thead><tr><th>步骤</th><th>状态</th></tr></thead><tbody>${rows}</tbody></table>
          ${latestResponse && latestResponse.next_actions.includes("refresh_datasource_status") ? '<div style="margin-top:10px;"><button class="btn primary" id="refreshDsBtn">刷新状态</button></div>' : ""}
        `;
        const refreshBtn = body.querySelector("#refreshDsBtn");
        if (refreshBtn) refreshBtn.addEventListener("click", refreshTask);
      }

      function openDatasourceModal(form) {
        datasourceFormPayload = {...form};
        document.getElementById("dsName").value = form.datasource_name || "";
        document.getElementById("dsType").value = form.datasource_type || "MySQL";
        document.getElementById("dsEnv").value = form.env || "PRD";
        document.getElementById("dsHost").value = form.host || "";
        document.getElementById("dsPort").value = form.port || "";
        document.getElementById("dsOwner").value = form.owner || "";
        document.getElementById("dsCollect").checked = Boolean(form.collect_metadata);
        document.getElementById("dsScan").checked = Boolean(form.run_security_scan);
        document.getElementById("dsSync").checked = Boolean(form.sync_data_map);
        document.getElementById("datasourceModal").classList.add("open");
      }

      function closeDatasourceModal() {
        document.getElementById("datasourceModal").classList.remove("open");
      }

      function submitDatasourceForm() {
        const payload = {
          ...(datasourceFormPayload || {}),
          datasource_name: document.getElementById("dsName").value.trim(),
          datasource_type: document.getElementById("dsType").value,
          env: document.getElementById("dsEnv").value,
          host: document.getElementById("dsHost").value.trim(),
          port: document.getElementById("dsPort").value.trim(),
          owner: document.getElementById("dsOwner").value.trim(),
          collect_metadata: document.getElementById("dsCollect").checked,
          run_security_scan: document.getElementById("dsScan").checked,
          sync_data_map: document.getElementById("dsSync").checked
        };
        closeDatasourceModal();
        addMessage("user", `确认提交数据源登记：${escapeHtml(payload.datasource_name)}，${escapeHtml(payload.datasource_type)} / ${escapeHtml(payload.env)}`);
        confirmAction(payload);
      }

      function openDecisionModal(title, text, payload) {
        decisionPayload = payload;
        document.getElementById("decisionTitle").textContent = title;
        document.getElementById("decisionText").textContent = text;
        document.getElementById("decisionModal").classList.add("open");
      }

      function closeDecisionModal() {
        document.getElementById("decisionModal").classList.remove("open");
      }

      function submitDecision() {
        const payload = decisionPayload || {};
        closeDecisionModal();
        addMessage("user", "是，立即执行。");
        confirmAction(payload);
      }

      function renderAssetRecommendation(body, card) {
        const asset = card.data.asset;
        body.innerHTML = `
          <div class="kv">
            <div>推荐表</div><div>${escapeHtml(asset.table_name)}</div>
            <div>中文名</div><div>${escapeHtml(asset.table_cn_name)}</div>
            <div>数据源</div><div>${escapeHtml(asset.datasource_id)} / ${escapeHtml(asset.schema)}</div>
          </div>
          <ul>${card.data.reason.map(item => `<li>${escapeHtml(item)}</li>`).join("")}</ul>
        `;
      }

      function renderJsonCard(body, data) {
        body.innerHTML = `<pre style="white-space:pre-wrap;margin:0;font-size:12px;">${escapeHtml(JSON.stringify(data, null, 2))}</pre>`;
      }

      function renderTask(response) {
        const el = document.getElementById("taskKv");
        if (!response) {
          el.innerHTML = `<div>状态</div><div>未开始</div><div>trace</div><div>${escapeHtml(userContext.trace_id)}</div>`;
          return;
        }
        el.innerHTML = `
          <div>task_id</div><div>${escapeHtml(response.task_id)}</div>
          <div>intent</div><div>${escapeHtml(response.intent)}</div>
          <div>状态</div><div>${escapeHtml(response.status)}</div>
          <div>确认</div><div>${response.need_confirm.required ? escapeHtml(response.need_confirm.type) : "无"}</div>
        `;
      }

      function renderTools(tools) {
        const list = document.getElementById("toolList");
        if (!tools.length) {
          list.innerHTML = `<div class="empty">暂无 Tool 调用</div>`;
          return;
        }
        list.innerHTML = "";
        tools.forEach(tool => {
          const item = document.createElement("div");
          item.className = "tool-item";
          item.innerHTML = `<strong>${escapeHtml(tool.tool_name)}</strong><span>${tool.success ? "成功" : "失败"} · ${tool.duration_ms} ms</span>`;
          list.appendChild(item);
        });
      }

      function renderSteps(steps) {
        const el = document.getElementById("steps");
        el.innerHTML = "";
        steps.forEach(([state, title, desc], index) => {
          const row = document.createElement("div");
          row.className = "step " + state;
          row.innerHTML = `<div class="dot">${state === "done" ? "✓" : index + 1}</div><div><strong>${escapeHtml(title)}</strong><span>${escapeHtml(desc)}</span></div>`;
          el.appendChild(row);
        });
      }

      function renderStepsByResponse(response) {
        if (response.intent === "GOVERN_METADATA") {
          if (response.need_confirm.type === "confirm_asset") renderSteps([
            ["done", "表名识别", "已抽取 dwd_customer_income_df"],
            ["active", "候选表确认", "等待选择唯一表"],
            ["", "智能补全", "待协同专业 Agent"],
            ["", "治理草案", "待生成"],
            ["", "提交流程", "待确认"]
          ]);
          else if (response.need_confirm.type === "confirm_metadata_prefill") renderSteps([
            ["done", "表名识别", "已抽取 dwd_customer_income_df"],
            ["done", "候选表确认", "已选择资产"],
            ["active", "智能补全", "等待确认候选值"],
            ["", "治理草案", "待生成"],
            ["", "提交流程", "待提交"]
          ]);
          else if (response.need_confirm.type === "submit_activiti") renderSteps([
            ["done", "表名识别", "已抽取 dwd_customer_income_df"],
            ["done", "候选表确认", "已选择资产"],
            ["done", "智能补全", "已确认候选值"],
            ["active", "治理草案", "等待提交确认"],
            ["", "提交流程", "待提交"]
          ]);
          else renderSteps([
            ["done", "表名识别", "已抽取 dwd_customer_income_df"],
            ["done", "候选表确认", "已选择资产"],
            ["done", "智能补全", "已确认"],
            ["done", "治理草案", "已生成"],
            ["done", "提交流程", "已提交 Mock Activiti"]
          ]);
        } else if (response.intent === "REGISTER_DATASOURCE") {
          if (response.need_confirm.type === "submit_datasource_register") renderSteps([
            ["done", "登记诉求", "已识别"],
            ["active", "填写表单", "等待用户补充并二次确认"],
            ["", "登记流程", "待提交 Mock 流程"],
            ["", "元数据采集", "待登记办结"],
            ["", "安全扫描", "待采集完成"],
            ["", "数据准备完成", "待完成"]
          ]);
          else if (response.need_confirm.type === "start_security_scan") renderSteps([
            ["done", "登记诉求", "已识别"],
            ["done", "填写表单", "已确认提交"],
            ["done", "登记流程", "已审批通过"],
            ["done", "元数据采集", "已完成"],
            ["active", "安全扫描", "等待用户确认是否立即扫描"],
            ["", "数据准备完成", "待完成"]
          ]);
          else if (response.need_confirm.type === "create_security_ticket") renderSteps([
            ["done", "登记诉求", "已识别"],
            ["done", "填写表单", "已确认提交"],
            ["done", "登记流程", "已审批通过"],
            ["done", "元数据采集", "已完成"],
            ["done", "安全扫描", "已完成"],
            ["active", "安全等级确认", "等待用户确认生成工单"],
            ["", "数据准备完成", "待完成"]
          ]);
          else renderSteps([
            ["done", "登记诉求", "已识别"],
            ["done", "填写表单", "已二次确认"],
            ["done", "登记流程", "状态已更新"],
            [response.status === "completed" ? "done" : "active", "后续处理", response.answer],
          ]);
        } else if (response.intent === "QUERY_LINEAGE") {
          renderSteps([
            ["done", "对象定位", "已定位资产"],
            ["done", "血缘查询", "已返回上游和任务"],
            ["done", "SQL 注释识别", "已生成备注建议"]
          ]);
        } else if (response.intent === "FIND_ASSET") {
          renderSteps([
            ["done", "问题识别", "已识别查表诉求"],
            ["done", "数据地图搜索", "已返回推荐资产"],
            ["done", "推荐解释", "已生成理由"]
          ]);
        }
      }

      function setBusy(busy) {
        document.getElementById("sendBtn").disabled = busy;
        questionInput.disabled = busy;
      }

      function escapeHtml(value) {
        return String(value ?? "").replace(/[&<>"']/g, ch => ({
          "&": "&amp;",
          "<": "&lt;",
          ">": "&gt;",
          '"': "&quot;",
          "'": "&#039;"
        }[ch]));
      }

      init();
    </script>
  </body>
</html>
"""
