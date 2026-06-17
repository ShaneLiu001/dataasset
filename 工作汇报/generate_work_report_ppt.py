import html
import zipfile
from pathlib import Path


OUT = Path("2026年上半年工作汇报_浅色Keynote兼容版.pptx")


NS = {
    "a": "http://schemas.openxmlformats.org/drawingml/2006/main",
    "p": "http://schemas.openxmlformats.org/presentationml/2006/main",
    "r": "http://schemas.openxmlformats.org/officeDocument/2006/relationships",
}


def esc(value):
    return html.escape(str(value), quote=True)


def color(hex_value):
    return hex_value.replace("#", "").upper()


def shape_xml(shape_id, x, y, w, h, fill, line=None, radius=False):
    prst = "roundRect" if radius else "rect"
    ln = '<a:ln><a:noFill/></a:ln>' if line is None else f'<a:ln w="12700"><a:solidFill><a:srgbClr val="{color(line)}"/></a:solidFill></a:ln>'
    return f"""
    <p:sp>
      <p:nvSpPr><p:cNvPr id="{shape_id}" name="Shape {shape_id}"/><p:cNvSpPr/><p:nvPr/></p:nvSpPr>
      <p:spPr>
        <a:xfrm><a:off x="{x}" y="{y}"/><a:ext cx="{w}" cy="{h}"/></a:xfrm>
        <a:prstGeom prst="{prst}"><a:avLst/></a:prstGeom>
        <a:solidFill><a:srgbClr val="{color(fill)}"/></a:solidFill>
        {ln}
      </p:spPr>
      <p:txBody><a:bodyPr/><a:lstStyle/><a:p/></p:txBody>
    </p:sp>"""


def text_box_xml(shape_id, x, y, w, h, lines, font_size=2200, fill=None, font_color="FFFFFF", bold=False, align="l"):
    if isinstance(lines, str):
        lines = [lines]
    fill_xml = '<a:noFill/>' if fill is None else f'<a:solidFill><a:srgbClr val="{color(fill)}"/></a:solidFill>'
    paragraphs = []
    for line in lines:
        line = str(line)
        if not line:
            paragraphs.append("<a:p/>")
            continue
        paragraphs.append(
            f"""<a:p>
              <a:pPr algn="{align}"/>
              <a:r><a:rPr lang="zh-CN" sz="{font_size}" b="{1 if bold else 0}">
                <a:solidFill><a:srgbClr val="{color(font_color)}"/></a:solidFill>
                <a:latin typeface="Microsoft YaHei"/><a:ea typeface="Microsoft YaHei"/>
              </a:rPr><a:t>{esc(line)}</a:t></a:r>
            </a:p>"""
        )
    return f"""
    <p:sp>
      <p:nvSpPr><p:cNvPr id="{shape_id}" name="TextBox {shape_id}"/><p:cNvSpPr txBox="1"/><p:nvPr/></p:nvSpPr>
      <p:spPr>
        <a:xfrm><a:off x="{x}" y="{y}"/><a:ext cx="{w}" cy="{h}"/></a:xfrm>
        <a:prstGeom prst="rect"><a:avLst/></a:prstGeom>
        {fill_xml}
        <a:ln><a:noFill/></a:ln>
      </p:spPr>
      <p:txBody>
        <a:bodyPr wrap="square" lIns="91440" tIns="45720" rIns="91440" bIns="45720"/>
        <a:lstStyle/>
        {''.join(paragraphs)}
      </p:txBody>
    </p:sp>"""


def header(title, page, accent="38BDF8"):
    return (
        shape_xml(10, 0, 0, 12192000, 685800, "FFFFFF")
        + shape_xml(11, 0, 685800, 12192000, 45720, accent)
        + text_box_xml(12, 457200, 137160, 9144000, 365760, title, 1800, font_color="0F172A", bold=True)
        + text_box_xml(13, 10972800, 137160, 762000, 365760, f"{page:02d}", 1600, font_color="64748B", bold=True, align="r")
    )


def badge(shape_id, x, y, text, fill="F59E0B"):
    return shape_xml(shape_id, x, y, 1463040, 320040, fill, radius=True) + text_box_xml(
        shape_id + 1, x, y + 18288, 1463040, 283464, text, 1100, font_color="0F172A", bold=True, align="ctr"
    )


def bullet_card(shape_id, x, y, w, h, title, bullets, accent="38BDF8", important=False):
    xml = shape_xml(shape_id, x, y, w, h, "FFFFFF", line="CBD5E1", radius=True)
    xml += shape_xml(shape_id + 1, x, y, 91440, h, accent)
    xml += text_box_xml(shape_id + 2, x + 182880, y + 137160, w - 365760, 274320, title, 1450, font_color="0F172A", bold=True)
    if important:
        xml += badge(shape_id + 30, x + w - 1645920, y + 118872, "重点工作")
    xml += text_box_xml(
        shape_id + 3,
        x + 228600,
        y + 502920,
        w - 411480,
        h - 594360,
        [f"• {b}" for b in bullets],
        1130,
        font_color="334155",
    )
    return xml


def slide_xml(slide_no, title, body):
    bg = '<p:bg><p:bgPr><a:solidFill><a:srgbClr val="F8FAFC"/></a:solidFill><a:effectLst/></p:bgPr></p:bg>'
    footer = text_box_xml(900, 457200, 6400800, 6096000, 228600, "2026年工作汇报 | DataOps / 信创 / 智能化", 850, font_color="64748B")
    return f"""<?xml version="1.0" encoding="UTF-8" standalone="yes"?>
<p:sld xmlns:a="{NS['a']}" xmlns:r="{NS['r']}" xmlns:p="{NS['p']}">
  <p:cSld>{bg}<p:spTree>
    <p:nvGrpSpPr><p:cNvPr id="1" name=""/><p:cNvGrpSpPr/><p:nvPr/></p:nvGrpSpPr>
    <p:grpSpPr><a:xfrm><a:off x="0" y="0"/><a:ext cx="0" cy="0"/><a:chOff x="0" y="0"/><a:chExt cx="0" cy="0"/></a:xfrm></p:grpSpPr>
    {header(title, slide_no)}
    {body}
    {footer}
  </p:spTree></p:cSld>
  <p:clrMapOvr><a:masterClrMapping/></p:clrMapOvr>
</p:sld>"""


def title_slide():
    body = ""
    body += shape_xml(20, 0, 0, 12192000, 6858000, "F8FAFC")
    body += shape_xml(21, 0, 5577840, 12192000, 1280160, "E0F2FE")
    body += shape_xml(22, 7772400, 685800, 3200400, 5029200, "FFFFFF", line="BAE6FD", radius=True)
    body += shape_xml(32, 685800, 960120, 1005840, 91440, "0284C7")
    body += text_box_xml(23, 685800, 1188720, 6553200, 731520, "2026年上半年工作汇报", 3300, font_color="0F172A", bold=True)
    body += text_box_xml(24, 685800, 2011680, 6553200, 914400, "一站式 DataOps / 信创改造 / 研发交付 / 智能化建设", 1700, font_color="0369A1")
    body += text_box_xml(25, 685800, 3200400, 6172200, 731520, ["20260317 交接后 | 当前 6 个迭代", "浅色技术汇报版"], 1450, font_color="475569")
    body += text_box_xml(26, 8046720, 1188720, 2560320, 640080, "重点提示", 1900, font_color="B45309", bold=True, align="ctr")
    body += text_box_xml(27, 8046720, 2103120, 2560320, 2743200, ["境外中台建设", "大数据引擎升级", "用户信创切换", "智能化能力落地"], 1600, font_color="0F172A", bold=True, align="ctr")
    body += badge(28, 685800, 5029200, "不超过10页")
    body += badge(30, 2324100, 5029200, "浅色技术汇报", "38BDF8")
    return f"""<?xml version="1.0" encoding="UTF-8" standalone="yes"?>
<p:sld xmlns:a="{NS['a']}" xmlns:r="{NS['r']}" xmlns:p="{NS['p']}">
  <p:cSld><p:spTree>
    <p:nvGrpSpPr><p:cNvPr id="1" name=""/><p:cNvGrpSpPr/><p:nvPr/></p:nvGrpSpPr>
    <p:grpSpPr><a:xfrm><a:off x="0" y="0"/><a:ext cx="0" cy="0"/><a:chOff x="0" y="0"/><a:chExt cx="0" cy="0"/></a:xfrm></p:grpSpPr>
    {body}
  </p:spTree></p:cSld><p:clrMapOvr><a:masterClrMapping/></p:clrMapOvr>
</p:sld>"""


slides = [
    title_slide(),
    slide_xml(
        2,
        "工作总览",
        bullet_card(30, 640080, 1005840, 3291840, 4389120, "上半年工作主线", [
            "一站式 DataOps 建设持续扩展",
            "信创改造与云原生切换推进",
            "研发交付管理整合与提效",
            "资产智能化与个人能力建设"
        ], important=True)
        + bullet_card(70, 4389120, 1005840, 3291840, 4389120, "交付规模", [
            "20260317 交接后推进 6 个迭代",
            "统一数据源、元数据、血缘、稽核、安全等多模块协同",
            "24 名开发商 + 9 名自有人员纳入晨会协同"
        ], accent="22C55E")
        + bullet_card(110, 8138160, 1005840, 3291840, 4389120, "管理看板", [
            "晨会看板、集成测试看板",
            "缺陷问题看板、临时上线看板",
            "通过看板提升透明度与节奏控制"
        ], accent="A78BFA")
    ),
    slide_xml(
        3,
        "一站式 DataOps 建设",
        bullet_card(30, 548640, 960120, 5105400, 2194560, "境外中台建设", [
            "统一数据源、元数据采集、数据地图、数据稽核",
            "数据血缘、数据安全、离线开发、离线同步",
            "查询探索、运维监控支持 Redshift 与镜像源"
        ], important=True)
        + bullet_card(70, 6126480, 960120, 5105400, 2194560, "引擎与源能力升级", [
            "支持 StarRocks 内表、mixed_iceberg",
            "支持 OceanBase Oracle 模式",
            "多模块适配统一推进，降低后续接入成本"
        ], accent="22C55E", important=True)
        + bullet_card(110, 548640, 3657600, 5105400, 1828800, "用户信创支持", [
            "数据源支持用户切换类型、切换绑定关系",
            "离线同步支持批量复制、提交、校验、下线、切换"
        ], accent="F59E0B")
        + bullet_card(150, 6126480, 3657600, 5105400, 1828800, "组织架构适配", [
            "多个 owner 转交",
            "权限流程支持 OA 委托",
            "作业流 Owner 转交联动空间绑定优化"
        ], accent="A78BFA")
    ),
    slide_xml(
        4,
        "实时同步与运维能力提升",
        bullet_card(30, 731520, 1097280, 4572000, 3840480, "同步链路扩展", [
            "MySQL / Oracle / GoldenDB -> DM",
            "DM -> Kafka / GoldenDB",
            "覆盖增量同步与全量同步"
        ], important=True)
        + bullet_card(70, 6309360, 1097280, 4572000, 3840480, "运维能力建设", [
            "实时运维能力建设持续推进",
            "围绕同步链路可观测、可定位、可恢复增强",
            "提升生产问题处理效率与系统稳定性"
        ], accent="22C55E")
        + text_box_xml(110, 1097280, 5364480, 10058400, 548640, "提示：实时同步是 DataOps 从“离线建设”走向“生产级数据流转”的关键能力，应作为下半年持续强化方向。", 1300, fill="FEF3C7", font_color="92400E", bold=True)
    ),
    slide_xml(
        5,
        "信创改造建设",
        bullet_card(30, 640080, 1005840, 3383280, 4389120, "生产切换与降本", [
            "完成数据稽核生产切换，满足合规要求",
            "完成云原生容器化改造",
            "旧机器下线，释放成本空间"
        ], accent="F59E0B", important=True)
        + bullet_card(70, 4297680, 1005840, 3383280, 4389120, "安全与解耦", [
            "完成安全扫描",
            "完成地图解耦改造",
            "系统间依赖更松耦合，便于后续演进"
        ], accent="38BDF8")
        + bullet_card(110, 7955280, 1005840, 3383280, 4389120, "Mapper 改造", [
            "统一数据源 mapper 改造",
            "数据血缘 mapper 改造",
            "元数据采集 mapper 改造"
        ], accent="22C55E", important=True)
    ),
    slide_xml(
        6,
        "研发交付管理整合",
        bullet_card(30, 548640, 914400, 5105400, 2377440, "研发管理模式升级", [
            "数据采建和管理晨会整合",
            "20260501 后：24 开发商 + 9 自有人员参与晨会",
            "以晨会、测试、缺陷、上线看板形成闭环"
        ], important=True)
        + bullet_card(70, 6126480, 914400, 5105400, 2377440, "重点专项支撑", [
            "Trinity 迁移与批量能力建设",
            "数据资产信创改造",
            "配合 AI 平台改造"
        ], accent="A78BFA")
        + bullet_card(110, 548640, 3749040, 5105400, 1645920, "开发效率提升", [
            "督促外包使用 AI 技术",
            "提升 UT 编写、mapper 脚本翻译等效率"
        ], accent="22C55E")
        + bullet_card(150, 6126480, 3749040, 5105400, 1645920, "资源池协同", [
            "支撑其他系统",
            "支撑 LLM、网关、大模型应用平台等工作"
        ], accent="F59E0B")
    ),
    slide_xml(
        7,
        "资产智能化与个人能力提升",
        bullet_card(30, 640080, 1005840, 3383280, 4389120, "资产智能化", [
            "标准、码值、元数据 MCP 能力建设",
            "探索数据源登记专家、查表助手等场景",
            "从工具能力走向业务流程嵌入"
        ], accent="38BDF8", important=True)
        + bullet_card(70, 4297680, 1005840, 3383280, 4389120, "能力学习", [
            "opencode、claudecode、codex、workbuddy、QClaw、Zcode",
            "MCP、提示词工程、上下文工程",
            "驾驭工程、循环工程等方法学习"
        ], accent="A78BFA")
        + bullet_card(110, 7955280, 1005840, 3383280, 4389120, "Vibe Coding 实践", [
            "智能记录待办到 Wiki 并录入需求",
            "智能优化 SQL",
            "智能翻译元数据备注"
        ], accent="22C55E")
    ),
    slide_xml(
        8,
        "问题与下半年重点",
        bullet_card(30, 548640, 914400, 5105400, 2194560, "当前问题", [
            "前端人员较多，需求相对较少，人员匹配度需优化",
            "智能化探索需尽快设计用户旅程",
            "智能化方案选型需形成明确判断"
        ], accent="EF4444")
        + bullet_card(70, 6126480, 914400, 5105400, 2194560, "下半年重点", [
            "继续完善境外中台建设",
            "升级各类驱动，支持用户信创切换场景",
            "力争完成数据资产 mapper 改造与性能测试",
            "完成数据源登记专家、查表助手等智能化建设"
        ], accent="F59E0B", important=True)
        + text_box_xml(110, 914400, 3931920, 10363200, 1188720, [
            "提示：下半年建议把重点压到“中台能力收敛 + 信创切换闭环 + 智能化样板落地”三件事上。",
            "衡量方式：交付里程碑、性能测试结果、用户旅程验证、智能助手可用率。"
        ], 1450, fill="FEF3C7", font_color="92400E", bold=True)
    ),
    slide_xml(
        9,
        "2027 展望",
        bullet_card(30, 731520, 1097280, 3291840, 3657600, "趋势判断", [
            "用户需求、技术需求可能逐步减少",
            "外包投入假设变化，需要提前思考交付模式",
            "能力沉淀比单点交付更重要"
        ], accent="38BDF8")
        + bullet_card(70, 4389120, 1097280, 3291840, 3657600, "能力建设方向", [
            "建设领域专家能力",
            "建设可复用 skill 与知识资产",
            "将外包内容转化为流程、工具和规范"
        ], accent="22C55E", important=True)
        + bullet_card(110, 8138160, 1097280, 3291840, 3657600, "团队演进", [
            "教会外包使用大模型",
            "以 AI 工具提升需求分析、开发、测试效率",
            "推动团队从执行型向专家型转变"
        ], accent="A78BFA")
    ),
]


def rels_xml(slide_count):
    rels = [
        '<Relationship Id="rId1" Type="http://schemas.openxmlformats.org/officeDocument/2006/relationships/slideMaster" Target="slideMasters/slideMaster1.xml"/>',
        '<Relationship Id="rId2" Type="http://schemas.openxmlformats.org/officeDocument/2006/relationships/theme" Target="theme/theme1.xml"/>',
    ]
    for i in range(slide_count):
        rels.append(f'<Relationship Id="rId{i+3}" Type="http://schemas.openxmlformats.org/officeDocument/2006/relationships/slide" Target="slides/slide{i+1}.xml"/>')
    return f"""<?xml version="1.0" encoding="UTF-8" standalone="yes"?>
<Relationships xmlns="http://schemas.openxmlformats.org/package/2006/relationships">{''.join(rels)}</Relationships>"""


def presentation_xml(slide_count):
    ids = "\n".join([f'<p:sldId id="{256+i}" r:id="rId{i+3}"/>' for i in range(slide_count)])
    return f"""<?xml version="1.0" encoding="UTF-8" standalone="yes"?>
<p:presentation xmlns:a="{NS['a']}" xmlns:r="{NS['r']}" xmlns:p="{NS['p']}">
  <p:sldMasterIdLst><p:sldMasterId id="2147483648" r:id="rId1"/></p:sldMasterIdLst>
  <p:sldIdLst>{ids}</p:sldIdLst>
  <p:sldSz cx="12192000" cy="6858000" type="screen16x9"/>
  <p:notesSz cx="6858000" cy="9144000"/>
  <p:defaultTextStyle/>
</p:presentation>"""


CONTENT_TYPES = """<?xml version="1.0" encoding="UTF-8" standalone="yes"?>
<Types xmlns="http://schemas.openxmlformats.org/package/2006/content-types">
  <Default Extension="rels" ContentType="application/vnd.openxmlformats-package.relationships+xml"/>
  <Default Extension="xml" ContentType="application/xml"/>
  <Override PartName="/docProps/app.xml" ContentType="application/vnd.openxmlformats-officedocument.extended-properties+xml"/>
  <Override PartName="/docProps/core.xml" ContentType="application/vnd.openxmlformats-package.core-properties+xml"/>
  <Override PartName="/ppt/presentation.xml" ContentType="application/vnd.openxmlformats-officedocument.presentationml.presentation.main+xml"/>
  <Override PartName="/ppt/slideMasters/slideMaster1.xml" ContentType="application/vnd.openxmlformats-officedocument.presentationml.slideMaster+xml"/>
  <Override PartName="/ppt/slideLayouts/slideLayout1.xml" ContentType="application/vnd.openxmlformats-officedocument.presentationml.slideLayout+xml"/>
  <Override PartName="/ppt/theme/theme1.xml" ContentType="application/vnd.openxmlformats-officedocument.theme+xml"/>
""" + "\n".join(
    [f'  <Override PartName="/ppt/slides/slide{i}.xml" ContentType="application/vnd.openxmlformats-officedocument.presentationml.slide+xml"/>' for i in range(1, len(slides) + 1)]
) + "\n</Types>"


ROOT_RELS = """<?xml version="1.0" encoding="UTF-8" standalone="yes"?>
<Relationships xmlns="http://schemas.openxmlformats.org/package/2006/relationships">
  <Relationship Id="rId1" Type="http://schemas.openxmlformats.org/officeDocument/2006/relationships/officeDocument" Target="ppt/presentation.xml"/>
  <Relationship Id="rId2" Type="http://schemas.openxmlformats.org/package/2006/relationships/metadata/core-properties" Target="docProps/core.xml"/>
  <Relationship Id="rId3" Type="http://schemas.openxmlformats.org/officeDocument/2006/relationships/extended-properties" Target="docProps/app.xml"/>
</Relationships>"""


CORE_PROPS = """<?xml version="1.0" encoding="UTF-8" standalone="yes"?>
<cp:coreProperties xmlns:cp="http://schemas.openxmlformats.org/package/2006/metadata/core-properties" xmlns:dc="http://purl.org/dc/elements/1.1/" xmlns:dcterms="http://purl.org/dc/terms/" xmlns:dcmitype="http://purl.org/dc/dcmitype/" xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance">
  <dc:title>2026年上半年工作汇报</dc:title>
  <dc:subject>根据 PPT生成Prompt.md 自动生成</dc:subject>
  <dc:creator>Codex</dc:creator>
  <cp:lastModifiedBy>Codex</cp:lastModifiedBy>
  <dcterms:created xsi:type="dcterms:W3CDTF">2026-06-16T00:00:00Z</dcterms:created>
  <dcterms:modified xsi:type="dcterms:W3CDTF">2026-06-16T00:00:00Z</dcterms:modified>
</cp:coreProperties>"""


APP_PROPS = f"""<?xml version="1.0" encoding="UTF-8" standalone="yes"?>
<Properties xmlns="http://schemas.openxmlformats.org/officeDocument/2006/extended-properties" xmlns:vt="http://schemas.openxmlformats.org/officeDocument/2006/docPropsVTypes">
  <Application>Microsoft PowerPoint</Application>
  <PresentationFormat>On-screen Show (16:9)</PresentationFormat>
  <Slides>{len(slides)}</Slides>
  <Company></Company>
  <AppVersion>16.0000</AppVersion>
</Properties>"""


THEME = """<?xml version="1.0" encoding="UTF-8" standalone="yes"?>
<a:theme xmlns:a="http://schemas.openxmlformats.org/drawingml/2006/main" name="Tech Report">
  <a:themeElements>
    <a:clrScheme name="Tech"><a:dk1><a:srgbClr val="0F172A"/></a:dk1><a:lt1><a:srgbClr val="FFFFFF"/></a:lt1><a:dk2><a:srgbClr val="334155"/></a:dk2><a:lt2><a:srgbClr val="F8FAFC"/></a:lt2><a:accent1><a:srgbClr val="0284C7"/></a:accent1><a:accent2><a:srgbClr val="16A34A"/></a:accent2><a:accent3><a:srgbClr val="F59E0B"/></a:accent3><a:accent4><a:srgbClr val="7C3AED"/></a:accent4><a:accent5><a:srgbClr val="DC2626"/></a:accent5><a:accent6><a:srgbClr val="64748B"/></a:accent6><a:hlink><a:srgbClr val="0284C7"/></a:hlink><a:folHlink><a:srgbClr val="7C3AED"/></a:folHlink></a:clrScheme>
    <a:fontScheme name="YaHei"><a:majorFont><a:latin typeface="Microsoft YaHei"/><a:ea typeface="Microsoft YaHei"/><a:cs typeface="Microsoft YaHei"/></a:majorFont><a:minorFont><a:latin typeface="Microsoft YaHei"/><a:ea typeface="Microsoft YaHei"/><a:cs typeface="Microsoft YaHei"/></a:minorFont></a:fontScheme>
    <a:fmtScheme name="Default"><a:fillStyleLst><a:solidFill><a:schemeClr val="phClr"/></a:solidFill></a:fillStyleLst><a:lnStyleLst><a:ln w="9525"><a:solidFill><a:schemeClr val="phClr"/></a:solidFill></a:ln></a:lnStyleLst><a:effectStyleLst><a:effectStyle><a:effectLst/></a:effectStyle></a:effectStyleLst><a:bgFillStyleLst><a:solidFill><a:schemeClr val="phClr"/></a:solidFill></a:bgFillStyleLst></a:fmtScheme>
  </a:themeElements>
</a:theme>"""


SLIDE_MASTER = f"""<?xml version="1.0" encoding="UTF-8" standalone="yes"?>
<p:sldMaster xmlns:a="{NS['a']}" xmlns:r="{NS['r']}" xmlns:p="{NS['p']}">
  <p:cSld><p:spTree><p:nvGrpSpPr><p:cNvPr id="1" name=""/><p:cNvGrpSpPr/><p:nvPr/></p:nvGrpSpPr><p:grpSpPr><a:xfrm><a:off x="0" y="0"/><a:ext cx="0" cy="0"/><a:chOff x="0" y="0"/><a:chExt cx="0" cy="0"/></a:xfrm></p:grpSpPr></p:spTree></p:cSld>
  <p:clrMap bg1="lt1" tx1="dk1" bg2="lt2" tx2="dk2" accent1="accent1" accent2="accent2" accent3="accent3" accent4="accent4" accent5="accent5" accent6="accent6" hlink="hlink" folHlink="folHlink"/>
  <p:sldLayoutIdLst><p:sldLayoutId id="2147483649" r:id="rId1"/></p:sldLayoutIdLst>
  <p:txStyles><p:titleStyle/><p:bodyStyle/><p:otherStyle/></p:txStyles>
</p:sldMaster>"""


SLIDE_MASTER_RELS = """<?xml version="1.0" encoding="UTF-8" standalone="yes"?>
<Relationships xmlns="http://schemas.openxmlformats.org/package/2006/relationships">
  <Relationship Id="rId1" Type="http://schemas.openxmlformats.org/officeDocument/2006/relationships/slideLayout" Target="../slideLayouts/slideLayout1.xml"/>
  <Relationship Id="rId2" Type="http://schemas.openxmlformats.org/officeDocument/2006/relationships/theme" Target="../theme/theme1.xml"/>
</Relationships>"""


SLIDE_LAYOUT = f"""<?xml version="1.0" encoding="UTF-8" standalone="yes"?>
<p:sldLayout xmlns:a="{NS['a']}" xmlns:r="{NS['r']}" xmlns:p="{NS['p']}" type="blank" preserve="1">
  <p:cSld name="Blank"><p:spTree><p:nvGrpSpPr><p:cNvPr id="1" name=""/><p:cNvGrpSpPr/><p:nvPr/></p:nvGrpSpPr><p:grpSpPr><a:xfrm><a:off x="0" y="0"/><a:ext cx="0" cy="0"/><a:chOff x="0" y="0"/><a:chExt cx="0" cy="0"/></a:xfrm></p:grpSpPr></p:spTree></p:cSld>
  <p:clrMapOvr><a:masterClrMapping/></p:clrMapOvr>
</p:sldLayout>"""


SLIDE_LAYOUT_RELS = """<?xml version="1.0" encoding="UTF-8" standalone="yes"?>
<Relationships xmlns="http://schemas.openxmlformats.org/package/2006/relationships">
  <Relationship Id="rId1" Type="http://schemas.openxmlformats.org/officeDocument/2006/relationships/slideMaster" Target="../slideMasters/slideMaster1.xml"/>
</Relationships>"""


def write_pptx():
    with zipfile.ZipFile(OUT, "w", zipfile.ZIP_DEFLATED) as z:
        z.writestr("[Content_Types].xml", CONTENT_TYPES)
        z.writestr("_rels/.rels", ROOT_RELS)
        z.writestr("docProps/core.xml", CORE_PROPS)
        z.writestr("docProps/app.xml", APP_PROPS)
        z.writestr("ppt/presentation.xml", presentation_xml(len(slides)))
        z.writestr("ppt/_rels/presentation.xml.rels", rels_xml(len(slides)))
        z.writestr("ppt/theme/theme1.xml", THEME)
        z.writestr("ppt/slideMasters/slideMaster1.xml", SLIDE_MASTER)
        z.writestr("ppt/slideMasters/_rels/slideMaster1.xml.rels", SLIDE_MASTER_RELS)
        z.writestr("ppt/slideLayouts/slideLayout1.xml", SLIDE_LAYOUT)
        z.writestr("ppt/slideLayouts/_rels/slideLayout1.xml.rels", SLIDE_LAYOUT_RELS)
        for i, slide in enumerate(slides, 1):
            z.writestr(f"ppt/slides/slide{i}.xml", slide)
    print(OUT)


if __name__ == "__main__":
    write_pptx()
