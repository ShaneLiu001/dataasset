import fs from 'node:fs';
import path from 'node:path';
import { fileURLToPath } from 'node:url';

const outputDir = path.dirname(fileURLToPath(import.meta.url));

const style = `<style>
  text { font-family: -apple-system, BlinkMacSystemFont, "PingFang SC", "Microsoft YaHei", sans-serif; fill: #39404a; font-size: 14px; }
  .title { font-size: 18px; font-weight: 600; fill: #252b34; }
  .section { font-size: 16px; font-weight: 600; fill: #252b34; }
  .label { text-anchor: end; dominant-baseline: middle; }
  .value { dominant-baseline: middle; fill: #5b6470; }
  .muted { fill: #9aa3af; }
  .head { font-weight: 600; fill: #303846; dominant-baseline: middle; }
  .cell { fill: #5b6470; dominant-baseline: middle; }
  .blue { fill: #356fca; }
  .amber { fill: #d99525; }
  .green { fill: #2f9b63; }
  .white { fill: #ffffff; }
  .small { font-size: 12px; }
  .tiny { font-size: 11px; }
</style>`;

function tag(x, y, text, color = '#356fca') {
  return `<rect x="${x}" y="${y - 15}" width="102" height="24" rx="3" fill="${color}"/><text x="${x + 51}" y="${y - 2}" text-anchor="middle" dominant-baseline="middle" class="white tiny">${text}</text>`;
}

function input(x, y, width, textValue, stroke = '#d8dde5') {
  return `<rect x="${x}" y="${y - 19}" width="${width}" height="38" fill="#ffffff" stroke="${stroke}"/><text x="${x + 14}" y="${y}" class="value">${textValue}</text>`;
}

function blankPage() {
  return `
    <rect width="1920" height="1080" fill="#f5f7fa"/>
    <rect x="220" y="35" width="1480" height="1010" fill="#ffffff" stroke="#d8dde5"/>
    <text x="255" y="76" class="title">编辑盘点任务</text>
    <text x="1660" y="76" class="title" fill="#8a929d">×</text>
    <line x1="220" y1="100" x2="1700" y2="100" stroke="#e3e7ed"/>

    <rect x="250" y="125" width="1420" height="410" fill="#ffffff" stroke="#e3e7ed"/>
    <text x="280" y="160" class="section">通用属性</text>
    <line x1="250" y1="182" x2="1670" y2="182" stroke="#e3e7ed"/>

    <text x="450" y="220" class="label">数据源 ID：</text><text x="470" y="220" class="value">RTDS_MYSQL_198_48_1</text>
    <text x="1080" y="220" class="label">数据源名称：</text><text x="1100" y="220" class="value">RTDS_MYSQL_198_48_1</text>
    <text x="450" y="264" class="label">schema：</text><text x="470" y="264" class="value">zzh_tidb</text>
    <text x="1080" y="264" class="label">表名：</text><text x="1100" y="264" class="value">tidb02_lv_minus1_xysb</text>
    <text x="450" y="308" class="label"><tspan fill="#ef4f4f">*</tspan> 表中文名：</text>
    ${input(470, 308, 455, '省市基础信息表')}
    <text x="1080" y="308" class="label"><tspan fill="#ef4f4f">*</tspan> 目录挂载：</text>
    ${input(1100, 308, 455, '请选择')}
    <text x="450" y="352" class="label">技术 Owner：</text><text x="470" y="352" class="value">柳鑫015500</text>
    <text x="1080" y="352" class="label"><tspan fill="#ef4f4f">*</tspan> 业务 Owner：</text>
    ${input(1100, 352, 455, '请选择')}
    <text x="450" y="396" class="label">分层标签：</text>
    ${input(470, 396, 455, '请选择分层')}
    <text x="1080" y="396" class="label"><tspan fill="#ef4f4f">*</tspan> 数据主管单位：</text>
    ${input(1100, 396, 455, '请选择')}
    <text x="450" y="456" class="label">备注：</text>
    ${input(470, 456, 1085, '包含省份与城市相关基础字段，用于维护行政区划编码与名称。')}

    <rect x="250" y="555" width="1420" height="390" fill="#ffffff" stroke="#e3e7ed"/>
    <text x="280" y="592" class="section">字段信息</text>
    <text x="1230" y="592" class="value muted small">预填范围包含全部分页字段</text>
    <rect x="1410" y="570" width="220" height="40" rx="4" fill="#eef8f2" stroke="#8bc7a6"/>
    <text x="1520" y="591" text-anchor="middle" dominant-baseline="middle" class="green">✓ 后台智能预填已完成</text>

    <line x1="220" y1="970" x2="1700" y2="970" stroke="#e3e7ed"/>
    <rect x="1490" y="990" width="70" height="36" rx="4" fill="#fff" stroke="#d8dde5"/><text x="1525" y="1009" text-anchor="middle" dominant-baseline="middle">取消</text>
    <rect x="1570" y="990" width="75" height="36" rx="4" fill="#356fca"/><text x="1607" y="1009" text-anchor="middle" dominant-baseline="middle" class="white">确定</text>
  `;
}

function prefillResult() {
  const rows = [
    ['province', 'varchar(100)', '省份', '省级行政区名称，具体取值范围需确认。', '2级', '安全推荐｜中置信', '#356fca', '需确认'],
    ['cityid', 'int(11)', '城市编码', '城市编码标识，建议结合关联表确认。', '2级', '安全推荐｜中置信', '#356fca', '需确认'],
    ['cityname', 'varchar(100)', '城市名称', '城市中文名称，与 cityid 配套使用。', '1级', '安全推荐｜高置信', '#2f9b63', '已预填'],
    ['amt', 'decimal(18,2)', '待人工补充', '待人工补充', '3级', '安全推荐｜需确认', '#d99525', '待补充']
  ];
  const rowMarkup = rows.map((row, index) => {
    const y = 760 + index * 44;
    const [field, type, cn, remark, level, securityText, securityColor, status] = row;
    const cnMarkup = index === 3
      ? `<text x="670" y="${y}" class="amber">证据不足，请人工填写</text>`
      : `<text x="670" y="${y}" class="cell">${cn}</text>${tag(808, y, 'AI生成｜置信度：中')}`;
    return `
      <text x="280" y="${y}" class="cell">${field}</text>
      <text x="405" y="${y}" class="cell">${type}</text>
      ${cnMarkup}
      <text x="930" y="${y}" class="cell">${remark}</text>
      <rect x="1310" y="${y - 17}" width="64" height="32" fill="#ffffff" stroke="#d8dde5"/>
      <text x="1325" y="${y}" class="cell">${level}</text>
      ${tag(1384, y, securityText, securityColor)}
      <text x="1518" y="${y}" class="${status === '已预填' ? 'green' : 'amber'}">${status}</text>
    `;
  }).join('\n');

  return `
    <rect x="270" y="612" width="1380" height="82" fill="#f2f7ff" stroke="#b9d6ff"/>
    <text x="290" y="634" class="blue"><tspan font-weight="600">后台智能预填已完成</tspan><tspan fill="#5b6470">　完成时间：2026-06-22 09:10　表信息 2 项，字段信息 11 项，安全等级 4 项</tspan></text>
    <text x="1210" y="634" class="value">安全等级需确认 2 项　低置信度 2 项　待人工补充 1 项</text>
    <text x="1625" y="634" text-anchor="end" class="blue">只看待处理项</text>
    <text x="290" y="670" class="value small">标识说明：“安全推荐”来自既有安全等级确认接口；中低置信度及 3/4 级安全等级需人工确认。</text>

    <rect x="270" y="714" width="1380" height="220" fill="#ffffff" stroke="#e3e7ed"/>
    <rect x="270" y="714" width="1380" height="44" fill="#fafbfc"/>
    <line x1="395" y1="714" x2="395" y2="934" stroke="#e3e7ed"/>
    <line x1="650" y1="714" x2="650" y2="934" stroke="#e3e7ed"/>
    <line x1="910" y1="714" x2="910" y2="934" stroke="#e3e7ed"/>
    <line x1="1290" y1="714" x2="1290" y2="934" stroke="#e3e7ed"/>
    <line x1="1500" y1="714" x2="1500" y2="934" stroke="#e3e7ed"/>
    <text x="280" y="736" class="head">字段名称</text><text x="405" y="736" class="head">字段类型</text><text x="670" y="736" class="head">字段中文名称</text><text x="930" y="736" class="head">备注</text><text x="1310" y="736" class="head"><tspan fill="#ef4f4f">*</tspan> 安全等级</text><text x="1518" y="736" class="head">状态</text>
    <line x1="270" y1="758" x2="1650" y2="758" stroke="#e3e7ed"/><line x1="270" y1="802" x2="1650" y2="802" stroke="#e3e7ed"/><line x1="270" y1="846" x2="1650" y2="846" stroke="#e3e7ed"/><line x1="270" y1="890" x2="1650" y2="890" stroke="#e3e7ed"/>
    ${rowMarkup}
  `;
}

function pendingOverride() {
  return `
    <rect x="270" y="714" width="1380" height="176" fill="#ffffff" stroke="#e3e7ed"/>
    <rect x="270" y="714" width="1380" height="44" fill="#fafbfc"/>
    <line x1="395" y1="714" x2="395" y2="890" stroke="#e3e7ed"/><line x1="650" y1="714" x2="650" y2="890" stroke="#e3e7ed"/><line x1="910" y1="714" x2="910" y2="890" stroke="#e3e7ed"/><line x1="1290" y1="714" x2="1290" y2="890" stroke="#e3e7ed"/><line x1="1500" y1="714" x2="1500" y2="890" stroke="#e3e7ed"/>
    <text x="280" y="736" class="head">字段名称</text><text x="405" y="736" class="head">字段类型</text><text x="670" y="736" class="head">字段中文名称</text><text x="930" y="736" class="head">备注</text><text x="1310" y="736" class="head"><tspan fill="#ef4f4f">*</tspan> 安全等级</text><text x="1518" y="736" class="head">状态</text>
    <line x1="270" y1="758" x2="1650" y2="758" stroke="#e3e7ed"/><line x1="270" y1="802" x2="1650" y2="802" stroke="#e3e7ed"/><line x1="270" y1="846" x2="1650" y2="846" stroke="#e3e7ed"/>
    <text x="280" y="780" class="cell">province</text><text x="405" y="780" class="cell">varchar(100)</text><text x="670" y="780" class="cell">省份</text>${tag(808, 780, 'AI生成｜置信度：中')}<text x="930" y="780" class="cell">结合样例确认具体范围。</text><rect x="1310" y="763" width="64" height="32" fill="#ffffff" stroke="#d8dde5"/><text x="1325" y="780" class="cell">2级</text>${tag(1384, 780, '安全推荐｜中置信')}<text x="1518" y="780" class="amber">需确认</text>
    <text x="280" y="824" class="cell">cityid</text><text x="405" y="824" class="cell">int(11)</text><text x="670" y="824" class="cell">城市编码</text>${tag(808, 824, 'AI生成｜置信度：中')}<text x="930" y="824" class="cell">确认编码体系及关联表。</text><rect x="1310" y="807" width="64" height="32" fill="#ffffff" stroke="#d8dde5"/><text x="1325" y="824" class="cell">2级</text>${tag(1384, 824, '安全推荐｜中置信')}<text x="1518" y="824" class="amber">需确认</text>
    <text x="280" y="868" class="cell">amt</text><text x="405" y="868" class="cell">decimal(18,2)</text><rect x="670" y="852" width="210" height="32" fill="#fff" stroke="#d99525"/><text x="684" y="868" class="muted small">请输入字段中文名称</text><text x="930" y="868" class="muted">待人工补充</text><rect x="1310" y="851" width="64" height="32" fill="#ffffff" stroke="#d99525"/><text x="1325" y="868" class="cell">3级</text>${tag(1384, 868, '安全推荐｜需确认', '#d99525')}<text x="1518" y="868" class="amber">待补充</text>
    <text x="1625" y="634" text-anchor="end" class="blue">查看全部字段</text>
  `;
}

function evidenceDrawer() {
  return `
    <rect width="1920" height="1080" fill="#202733" opacity="0.16"/>
    <rect x="1430" y="0" width="490" height="1080" fill="#ffffff" stroke="#d8dde5"/>
    <text x="1460" y="58" class="title">安全等级推荐依据</text><text x="1880" y="58" text-anchor="end" class="title">×</text>
    <text x="1460" y="125" class="section">字段</text><text x="1460" y="160" class="value">province</text><line x1="1460" y1="190" x2="1880" y2="190" stroke="#e3e7ed"/>
    <text x="1460" y="235" class="section">推荐结果</text><text x="1460" y="275" class="value">2级</text><text x="1510" y="275" class="amber">中置信度 76%</text><line x1="1460" y1="305" x2="1880" y2="305" stroke="#e3e7ed"/>
    <text x="1460" y="350" class="section">生成依据</text>
    <text x="1460" y="390" class="value">• 已调用现有安全等级确认接口</text>
    <text x="1460" y="430" class="value">• 列名匹配：province 行政区划字段</text>
    <text x="1460" y="470" class="value">• 接口能力来源：正则表达式与列名匹配</text>
    <text x="1460" y="510" class="value">• 3/4 级或中低置信度结果需显式确认</text>
    <line x1="1460" y1="550" x2="1880" y2="550" stroke="#e3e7ed"/>
    <text x="1460" y="595" class="section">人工确认建议</text>
    <text x="1460" y="635" class="value">建议技术 Owner 结合字段真实业务含义确认等级；</text>
    <text x="1460" y="665" class="value">AI 不降低接口强规则命中的等级。</text>
    <rect x="1460" y="720" width="130" height="38" rx="4" fill="#fff" stroke="#d8dde5"/><text x="1525" y="740" text-anchor="middle" class="value">调整安全等级</text>
    <rect x="1605" y="720" width="130" height="38" rx="4" fill="#356fca"/><text x="1670" y="740" text-anchor="middle" class="white">确认该等级</text>
  `;
}

function submitDialog() {
  return `
    <text x="670" y="892" class="cell">交易金额</text><text x="930" y="892" class="cell">交易金额，单位为元。</text><text x="1518" y="892" class="blue">人工补充</text>
    <rect width="1920" height="1080" fill="#202733" opacity="0.18"/>
    <rect x="610" y="330" width="700" height="380" fill="#ffffff" stroke="#d8dde5"/>
    <text x="650" y="378" class="title">确认提交盘点结果</text><line x1="610" y1="405" x2="1310" y2="405" stroke="#e3e7ed"/>
    <text x="650" y="452" class="section">本次确认结果</text>
    <text x="670" y="494" class="value">✓ 后台预填候选 13 项</text>
    <text x="670" y="532" class="value">✓ 已人工核对安全等级 2 项</text>
    <text x="670" y="570" class="value">✓ 已人工补充 1 项</text>
    <rect x="650" y="598" width="620" height="56" fill="#f2f7ff" stroke="#b9d6ff"/>
    <text x="670" y="622" class="blue">提交后将沿用现有流程进入后续审批，</text>
    <text x="670" y="646" class="blue">字段安全等级以用户确认值作为最终提交值。</text>
    <rect x="1080" y="676" width="85" height="38" rx="4" fill="#fff" stroke="#d8dde5"/><text x="1122" y="696" text-anchor="middle" class="value">返回检查</text>
    <rect x="1178" y="676" width="100" height="38" rx="4" fill="#356fca"/><text x="1228" y="696" text-anchor="middle" class="white">确认提交</text>
  `;
}

const steps = [
  {
    file: '01_一键填充入口_安全等级确认_Figma.svg',
    id: 'step-1-security-prefill-result',
    title: '步骤 1：打开工单查看带安全等级的预填结果',
    extra: `<rect x="1660" y="608" width="230" height="92" fill="#eef8f2" stroke="#8bc7a6"/><text x="1775" y="634" text-anchor="middle" class="green">步骤 1：打开工单</text><text x="1775" y="660" text-anchor="middle" class="green small">同步展示字段安全等级推荐</text><text x="1775" y="682" text-anchor="middle" class="green small">用户直接核对确认</text>`
  },
  {
    file: '02_填充配置_安全等级确认_Figma.svg',
    id: 'step-2-security-review-pending',
    title: '步骤 2：核对安全等级需确认项',
    extra: `${pendingOverride()}<rect x="1660" y="718" width="230" height="88" fill="#fff2d9" stroke="#d99525"/><text x="1775" y="746" text-anchor="middle" class="amber">步骤 2：核对待处理项</text><text x="1775" y="772" text-anchor="middle" class="amber small">聚焦安全等级需确认字段</text>`
  },
  {
    file: '03_生成中_安全等级确认_Figma.svg',
    id: 'step-3-security-evidence',
    title: '步骤 3：查看安全等级推荐依据',
    extra: evidenceDrawer()
  },
  {
    file: '04_生成结果与依据_安全等级确认_Figma.svg',
    id: 'step-4-security-confirm-submit',
    title: '步骤 4：确认提交安全等级结果',
    extra: submitDialog()
  }
];

const fullSteps = [];

for (const [index, step] of steps.entries()) {
  const frame = `
    ${blankPage()}
    ${prefillResult()}
    ${step.extra}
  `;
  const output = `<svg xmlns="http://www.w3.org/2000/svg" width="1920" height="1080" viewBox="0 0 1920 1080">
  <title>${step.title}</title>
  <defs>${style}</defs>
  <g id="${step.id}">
${frame}
  </g>
</svg>
`;
  fs.writeFileSync(path.join(outputDir, step.file), output);
  fullSteps.push(`  <g id="${step.id}-full" transform="translate(${index * 1920} 0)">\n${frame}\n  </g>`);
}

const fullOutput = `<svg xmlns="http://www.w3.org/2000/svg" width="7680" height="1080" viewBox="0 0 7680 1080">
  <title>数据资产盘点后台智能预填 - 安全等级确认 Figma 全流程画板</title>
  <defs>${style}</defs>
${fullSteps.join('\n')}
</svg>
`;
fs.writeFileSync(path.join(outputDir, '00_全流程画板_安全等级确认_Figma.svg'), fullOutput);

console.log(`Generated ${steps.length + 1} security Figma SVG files in ${outputDir}`);
