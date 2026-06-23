import fs from 'node:fs';
import path from 'node:path';
import { fileURLToPath } from 'node:url';

const directory = path.dirname(fileURLToPath(import.meta.url));
const drawioPath = path.join(directory, '数据资产盘点一键智能填充原型.drawio');
let xml = fs.readFileSync(drawioPath, 'utf8');

function escapeXml(value) {
  return value
    .replaceAll('&', '&amp;')
    .replaceAll('<', '&lt;')
    .replaceAll('>', '&gt;')
    .replaceAll('"', '&quot;');
}

function setCellValue(id, value) {
  const pattern = new RegExp(`(<mxCell id="${id}" value=")[^"]*(")`);
  if (!pattern.test(xml)) throw new Error(`mxCell not found: ${id}`);
  xml = xml.replace(pattern, `$1${escapeXml(value)}$2`);
}

function setCellStyle(id, style) {
  const pattern = new RegExp(`(<mxCell id="${id}"[^>]* style=")[^"]*(")`);
  if (!pattern.test(xml)) throw new Error(`mxCell style not found: ${id}`);
  xml = xml.replace(pattern, `$1${style}$2`);
}

const commonTable = `<b>通用属性</b><br><table style="width:100%;border-collapse:collapse;margin-top:18px;">
<tr><td style="width:140px;text-align:right;padding:9px;">数据源 ID：</td><td style="width:360px;padding:9px;">RTDS_MYSQL_198_48_1</td><td style="width:140px;text-align:right;padding:9px;">数据源名称：</td><td style="padding:9px;">RTDS_MYSQL_198_48_1</td></tr>
<tr><td style="text-align:right;padding:9px;">schema：</td><td style="padding:9px;">zzh_tidb</td><td style="text-align:right;padding:9px;">表名：</td><td style="padding:9px;">tidb02_lv_minus1_xysb</td></tr>
<tr><td style="text-align:right;padding:9px;">表中文名：</td><td style="padding:9px;">省市基础信息表　<font color="#356FCA">AI生成｜置信度：中</font></td><td style="text-align:right;padding:9px;">目录挂载：</td><td style="padding:9px;">[ 请选择 ]</td></tr>
<tr><td style="text-align:right;padding:9px;">技术 Owner：</td><td style="padding:9px;">柳鑫015500</td><td style="text-align:right;padding:9px;">业务 Owner：</td><td style="padding:9px;">[ 请选择 ]</td></tr>
<tr><td style="text-align:right;padding:9px;">备注：</td><td colspan="3" style="padding:9px;">包含省份与城市相关基础字段，用于维护行政区划编码与名称。</td></tr>
</table>`;

const resultTable = `<table style="width:100%;border-collapse:collapse;text-align:left;">
<tr style="background:#FAFBFC;font-weight:bold;"><td style="width:18%;padding:12px;">字段名称</td><td style="width:16%;padding:12px;">字段类型</td><td style="width:27%;padding:12px;">字段中文名称</td><td style="width:29%;padding:12px;">备注</td><td style="width:10%;padding:12px;">状态</td></tr>
<tr><td style="padding:12px;">province</td><td style="padding:12px;">varchar(100)</td><td style="padding:12px;">省份　<font color="#356FCA">AI生成｜置信度：中</font></td><td style="padding:12px;">省级行政区名称，需结合样例确认。</td><td style="padding:12px;color:#D99525;">需确认</td></tr>
<tr><td style="padding:12px;">cityid</td><td style="padding:12px;">int(11)</td><td style="padding:12px;">城市编码　<font color="#356FCA">AI生成｜置信度：中</font></td><td style="padding:12px;">城市编码标识，需确认编码体系。</td><td style="padding:12px;color:#D99525;">需确认</td></tr>
<tr><td style="padding:12px;">cityname</td><td style="padding:12px;">varchar(100)</td><td style="padding:12px;">城市名称　<font color="#2F9B63">AI生成｜置信度：高</font></td><td style="padding:12px;">城市中文名称，与 cityid 配套使用。</td><td style="padding:12px;color:#2F9B63;">已预填</td></tr>
<tr><td style="padding:12px;">amt</td><td style="padding:12px;">decimal(18,2)</td><td style="padding:12px;color:#D99525;">证据不足，请人工填写</td><td style="padding:12px;">待人工补充</td><td style="padding:12px;color:#D99525;">待补充</td></tr>
</table>`;

const finalTable = resultTable
  .replaceAll('需确认</td>', '已确认</td>')
  .replace('<td style="padding:12px;color:#D99525;">证据不足，请人工填写</td><td style="padding:12px;">待人工补充</td><td style="padding:12px;color:#D99525;">待补充</td>', '<td style="padding:12px;">交易金额　<font color="#356FCA">人工补充</font></td><td style="padding:12px;">交易金额，单位为元。</td><td style="padding:12px;color:#356FCA;">已补充</td>');

xml = xml
  .replace('name="01_一键填充入口"', 'name="01_打开工单查看预填结果"')
  .replace('name="02_填充配置"', 'name="02_核对待处理项"')
  .replace('name="03_生成中"', 'name="03_查看生成依据"')
  .replace('name="04_生成结果与依据"', 'name="04_确认提交"');

setCellValue('notice', '● 后台已完成智能预填，请技术 Owner 核对候选内容并提交。');
setCellValue('source', commonTable);
setCellValue('scope', '预填范围包含全部分页字段');
setCellValue('smartBtn', '✓ 后台智能预填已完成　09:10');
setCellValue('fieldHead', resultTable);
setCellValue('annotation', '步骤 1：打开工单即展示后台候选结果，无需点击生成');

setCellValue('configTitle', '步骤 2：核对待处理项');
setCellValue('commonGhost', commonTable);
setCellValue('fillLabel', '后台预填结果已载入，系统默认定位中低置信度和待人工补充字段。');
setCellValue('checks', '待处理范围　☑ 中置信度 2 项　☑ 待人工补充 1 项');
setCellValue('modeLabel', '人工处理要求');
setCellValue('mode1', '① 结合样例值确认 province 的具体业务范围');
setCellValue('mode2', '② 结合关联表确认 cityid 的编码体系');
setCellValue('mode3', '③ 补充 amt 的字段中文名称与备注');
setCellValue('cancel2', '查看全部字段');
setCellValue('start2', '完成核对');
setCellValue('note2', '只展示需要人工处理的内容<br>高置信度字段仍可查看');

setCellValue('disabledBtn3', '✓ 后台智能预填已完成');
setCellValue('common3', commonTable);
setCellValue('progressText3', '步骤 3：点击完整置信度标签查看生成依据并确认或修改');
setCellValue('progressPct3', '');
setCellStyle('track3', 'rounded=0;fillColor=#FFFFFF;strokeColor=#FFFFFF;');
setCellStyle('bar3', 'rounded=0;fillColor=#FFFFFF;strokeColor=#FFFFFF;');
setCellValue('fieldHead3', resultTable);
setCellValue('note3', '候选值由后台生成<br>人工修改后不再被覆盖');

setCellValue('refill4', '✓ 后台智能预填已完成');
setCellValue('common4', commonTable);
setCellValue('summary4', '<b><font color="#2367C6">准备提交</font></b>　后台候选 9 项　已核对中置信度 2 项　已人工补充 1 项');
setCellValue('head4', finalTable);
setCellValue('drawerTitle4', '确认提交盘点结果　　　　　　　　　　　　　　　×');
setCellValue('drawerContent4', '<b>本次确认结果</b><br><br>✓ 后台预填候选 9 项<br><br>✓ 已人工核对中置信度 2 项<br><br>✓ 已人工补充 1 项<br><br><hr><br>提交后将沿用现有流程进入后续审批，不直接发布正式元数据。<br><br><b><font color="#356FCA">[ 返回检查 ]　[ 确认提交 ]</font></b>');
setCellValue('note4', '步骤 4：用户只确认最终结果<br>后台候选不会直接发布');

if (!xml.includes('id="drawer3"')) {
  const diagramStart = xml.indexOf('<diagram id="progress-page"');
  const rootEnd = xml.indexOf('</root>', diagramStart);
  if (diagramStart < 0 || rootEnd < 0) throw new Error('progress-page root not found');
  const drawerCells = `
        <mxCell id="drawerShade3" value="" style="rounded=0;fillColor=#202733;opacity=16;strokeColor=none;" vertex="1" parent="1"><mxGeometry width="1920" height="1080" as="geometry"/></mxCell>
        <mxCell id="drawer3" value="" style="rounded=0;fillColor=#FFFFFF;strokeColor=#D8DDE5;shadow=1;" vertex="1" parent="1"><mxGeometry x="1430" width="490" height="1080" as="geometry"/></mxCell>
        <mxCell id="drawerTitle3" value="AI 生成依据　　　　　　　　　　　　　　　　　×" style="text;html=1;strokeColor=none;fillColor=none;align=left;fontSize=18;fontStyle=1;" vertex="1" parent="1"><mxGeometry x="1460" y="35" width="420" height="40" as="geometry"/></mxCell>
        <mxCell id="drawerContent3" value="&lt;b&gt;字段&lt;/b&gt;&lt;br&gt;&lt;br&gt;cityid&lt;br&gt;&lt;br&gt;&lt;hr&gt;&lt;br&gt;&lt;b&gt;推荐结果&lt;/b&gt;&lt;br&gt;&lt;br&gt;城市编码　&lt;font color=&quot;#D99525&quot;&gt;中置信度 76%&lt;/font&gt;&lt;br&gt;&lt;br&gt;&lt;hr&gt;&lt;br&gt;&lt;b&gt;生成依据&lt;/b&gt;&lt;br&gt;&lt;br&gt;• 字段名可拆分为 city + id&lt;br&gt;&lt;br&gt;• 字段类型为整数，符合编码类字段特征&lt;br&gt;&lt;br&gt;• 同表存在 cityname，可形成编码与名称组合&lt;br&gt;&lt;br&gt;&lt;hr&gt;&lt;br&gt;&lt;b&gt;人工确认建议&lt;/b&gt;&lt;br&gt;&lt;br&gt;建议结合样例值或关联表确认编码体系。&lt;br&gt;&lt;br&gt;&lt;font color=&quot;#356FCA&quot;&gt;[ 修改候选值 ]　[ 确认该字段 ]&lt;/font&gt;" style="text;html=1;strokeColor=none;fillColor=none;align=left;verticalAlign=top;fontSize=14;fontColor=#626C79;spacing=8;" vertex="1" parent="1"><mxGeometry x="1460" y="100" width="420" height="820" as="geometry"/></mxCell>
`;
  xml = `${xml.slice(0, rootEnd)}${drawerCells}${xml.slice(rootEnd)}`;
}

fs.writeFileSync(drawioPath, xml);
console.log(`Updated ${drawioPath}`);
