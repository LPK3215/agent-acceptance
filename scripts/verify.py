# -*- coding: utf-8 -*-
#!/usr/bin/env python3
"""agent-acceptance 打包前自查脚本（作者 / 维护者专用）。

把 docs/00-写作与引用规范.md 第四节「打包前自查清单」中机器可判定的项目
固化为可重复运行的检查，输出 PASS / WARN / FAIL，FAIL 非零退出。

适用范围（与规范一致）：
  - 运行时正文 = SKILL.md + README.md + references/*.md；
  - docs/ 为作者维护区：自身含规则反例示范，不参与字符 / 链接 / wikilink 扫描；
  - project_overview/ 为仓库展示页：只检查与技能正文同步的元数据、判点统计、
    生成资产和基础安全 / 无障碍钩子，不把它混入发布包正文规则；
  - 00-全局地图.md 为全貌导航文件，豁免「正文小节导航」要求。

用法（在仓库根目录执行，零第三方依赖，仅 Python 3 标准库）：
  python scripts/verify.py          # 全量自查
  python scripts/verify.py --quiet  # 只输出问题与摘要
退出码：0 = 可打包；1 = 存在 FAIL。
"""

import json
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
SKILL = ROOT / "SKILL.md"
README = ROOT / "README.md"
REF_DIR = ROOT / "references"
SKILL_JSON = ROOT / "skill.json"
OVERVIEW_DIR = ROOT / "project_overview"
OVERVIEW_HTML = OVERVIEW_DIR / "index.html"
OVERVIEW_SCRIPT = OVERVIEW_DIR / "script.js"
OVERVIEW_CHARTS = OVERVIEW_DIR / "charts.js"
OVERVIEW_STYLE = OVERVIEW_DIR / "style.css"

# references/ 已知文件登记（打包单元 = SKILL.md + skill.json + references/，不允许多出不缺漏）
KNOWN_REF_FILES = {
    "00-全局地图.md",
    "01-范围、形态与档位.md",
    "02-系统组成与真实接线.md",
    "03-考卷与评测集.md",
    "04-判分规则.md",
    "05-指标与目标值.md",
    "06-运行可观测.md",
    "07-安全与权限底线.md",
    "08-生产就绪与上线.md",
    "09-交付物与证据链.md",
    "10-验收结论与档位.md",
    "附录A-元规则.md",
    "附录B-脚手架型通用接入模板.md",
}
SKILL_MAX_LINES = 500   # 规范：SKILL.md 正文保持 500 行内
TOC_MIN_LINES = 100     # 规范：超 100 行章正文需「正文小节导航」

# SKILL.md 执行硬协议锚定（防维护期删弱/挪走）。硬协议是运行期"触发即必达"的
# 最硬保证，正文一旦被删或降级成 references 按需层，打包校验即 FAIL——
# 避免收口/落盘约束悄然丢失。短语按 SKILL.md 正文现文登记，改正文需同步本表。
HARD_PROTOCOL_ANCHORS = (
    ("执行硬协议（必执行、不可跳过", "执行硬协议标题"),
    ("入口必经", "入口必经约束"),
    ("收口必经", "收口必经约束"),
    ("产出必落盘", "产出必落盘约束"),
    ("分批跑接续", "分批跑接续约束"),
    ("输出目录声明", "输出目录声明（与 01 定档记录第 8 项联动）"),
    ("acceptance/<被检对象名>/<YYYY-MM-DD>/", "默认落盘目录路径"),
    ("开跑先复述", "开跑复述钩子（第 0 步自证已读）"),
    ("references/01-范围、形态与档位.md", "入口必经章链接"),
    ("references/10-验收结论与档位.md", "收口必经章链接"),
    ("快速出口（建议性", "1.1 快速出口建议性口径"),
    ("可选出口", "脚手架型/SDK wrapper 快速出口可选"),
    ("脚手架补件必指向附录 B", "脚手架改进必须回链附录 B 模板"),
    ("附录 B **在包内**", "附录 B 包内状态（防再写成包外）"),
    ("被检根目录", "被检对象是用户指定项目根，不是技能仓库根"),
    ("验收快照", "定档须声明工作区或指定 commit，防默认同 HEAD"),
)

# R4 符号纪律：允许的中文标点 / 符号（码点白名单）；其余非 ASCII 一律报 FAIL
ALLOW_PUNCT = {
    0x3001,   # 、
    0x3002,   # 。
    0xFF0C,   # ，
    0xFF1A,   # ：
    0xFF1B,   # ；
    0x2018,   # ‘
    0x2019,   # ’
    0x201C,   # “
    0x201D,   # ”
    0xFF01,   # ！
    0xFF1F,   # ？
    0xFF08,   # （
    0xFF09,   # ）
    0x300A,   # 《
    0x300B,   # 》
}
ALLOW_SYMBOLS = {0x00B1, 0x2264, 0x2265}   # ± ≤ ≥（规范允许列表）
EM_DASH = 0x2014                          # —— 中文破折号，仅成对（另做扫描）

results = []  # (severity, message)


def note(severity, msg):
    results.append((severity, msg))


# ---------- 小工具 ----------

def runtime_targets():
    """运行时正文文件：SKILL.md + README.md + references/*.md（按名排序）。"""
    files = [SKILL, README]
    files += sorted(REF_DIR.glob("*.md"))
    return files


def is_allowed_char(ch):
    o = ord(ch)
    if 0x4E00 <= o <= 0x9FFF or 0x3400 <= o <= 0x4DBF:   # CJK 汉字
        return True
    return o in ALLOW_PUNCT or o in ALLOW_SYMBOLS


def line_of(text, pos):
    return text.count("\n", 0, pos) + 1


def check_wikilink(path, text):
    """自查清单：技能包内全文搜不到 [[（Obsidian wikilink 一律清零）。"""
    for n, line in enumerate(text.splitlines(), 1):
        if "[[" in line or "]]" in line:
            note("FAIL", "发现 Obsidian wikilink [[ ]]，禁止：%s:%d" % (path.name, n))


def check_banned_chars(path, text):
    """R4 符号纪律：非 ASCII 白名单之外字符扫描为零；破折号必须成对。"""
    for n, line in enumerate(text.splitlines(), 1):
        bad = [ch for ch in line if ord(ch) > 127 and not is_allowed_char(ch) and ord(ch) != EM_DASH]
        if bad:
            note("FAIL", "黑名单字符 U+%04X：%s:%d" % (ord(bad[0]), path.name, n))
    for run in re.finditer("\u2014+", text):
        if len(run.group()) % 2 == 1:
            note("FAIL", "中文破折号未成对（run 长度 %d）：%s:%d"
                 % (len(run.group()), path.name, line_of(text, run.start())))


def check_links(path, text):
    """R1 链接白名单：
    - 相对 markdown 链接目标必须存在；
    - SKILL.md 与 references/* 的相对链接解析后必须落在 references/ 内；
    - README 允许链仓库内任何文件（含 docs/）；
    - http(s) 外链仅 WARN，提示人工按 R3 确认是否为官方一手来源。
    """
    base = path.parent
    pattern = re.compile(r"!?\[[^\]\n]*\]\(\s*([^)\s]+)\s*\)")
    for m in pattern.finditer(text):
        target = m.group(1).strip()
        ln = line_of(text, m.start())
        if target.startswith(("http://", "https://", "mailto:")):
            note("WARN", "外部链接（按 R3 人工确认官方一手来源）：%s (%s:%d)" % (target, path.name, ln))
            continue
        frag = target.split("#", 1)[0].strip()
        if not frag or frag in (".", "./"):
            continue
        abs_target = base / frag
        if not abs_target.exists():
            note("FAIL", "链接目标不存在：%s (%s:%d)" % (frag, path.name, ln))
            continue
        if path == README:      # 仓库首页可指向 docs/ 维护区
            continue
        try:
            rel = abs_target.resolve().relative_to(ROOT.resolve())
        except ValueError:
            note("FAIL", "链接解析出包外：%s (%s:%d)" % (frag, path.name, ln))
            continue
        rel_str = rel.as_posix()
        # R1 白名单：references 内正文可回链入口 SKILL.md；不得链 docs/ 或包外
        if not (rel_str == "SKILL.md"
                or rel_str == "references"
                or rel_str.startswith("references/")):
            note("FAIL", "链接目标越过 references/（仅允许 references/ 内文件或入口 SKILL.md）：%s (%s:%d)" % (frag, path.name, ln))


def parse_frontmatter(text):
    """极简 frontmatter 顶层 key 解析（单行值）。metadata 子块另用 extract_metadata。"""
    m = re.match(r"^---\s*\n(.*?)\n---\s*\n", text, re.S)
    if not m:
        return None
    meta = {}
    for line in m.group(1).splitlines():
        if ":" not in line or line.startswith(" "):
            continue
        k, _, v = line.partition(":")
        v = v.strip()
        if len(v) >= 2 and v[0] == v[-1] and v[0] in "\"'":
            v = v[1:-1]
        meta[k.strip()] = v
    return meta


def extract_metadata(text):
    """提取 frontmatter 中 metadata: 下的子键。"""
    m = re.search(r"^metadata:\s*\n((?:  \S.*\n)+)", text, re.M)
    if not m:
        return {}
    meta = {}
    for line in m.group(1).splitlines():
        k, _, v = line.strip().partition(":")
        v = v.strip()
        if len(v) >= 2 and v[0] == v[-1] and v[0] in "\"'":
            v = v[1:-1]
        meta[k.strip()] = v
    return meta


def toc_numbers_in(text):
    """「正文小节导航」引用块中的编号集合（连续引用行合并提取）。"""
    lines = text.splitlines()
    start = None
    for i, line in enumerate(lines):
        if line.startswith(">") and "正文小节导航" in line:
            start = i
            break
    if start is None:
        return None
    buf = []
    for line in lines[start:]:
        if not line.startswith(">"):
            break
        buf.append(line.lstrip(">").strip())
    return set(re.findall(r"\b\d+(?:\.\d+)+\b", " ".join(buf)))


def heading_numbers(text):
    """正文中所有 `## x.y` 级小节编号。"""
    return set(re.findall(r"^##\s*(\d+(?:\.\d+)+)\b", text, re.M))


def check_toc(path):
    """自查清单：超 100 行正文须有「正文小节导航」且编号覆盖全部 ## 小节。"""
    text = path.read_text(encoding="utf-8")
    n_lines = len(text.splitlines())
    toc = toc_numbers_in(text)
    if n_lines > TOC_MIN_LINES and toc is None:
        note("FAIL", "%s：%d 行超 %d 行阈值，缺「正文小节导航」" % (path.name, n_lines, TOC_MIN_LINES))
        return
    if toc is not None:
        missing = heading_numbers(text) - toc
        for num in sorted(missing, key=lambda s: [int(x) for x in s.split(".")]):
            note("FAIL", "%s：正文小节 %s 未进「正文小节导航」" % (path.name, num))


def check_hard_protocol(skill_text):
    """执行硬协议锚定：SKILL.md 必须长期保有收口/落盘关键约束与必经章链接。

    运行期"是否真被读到"由入口指令强度决定、机器不可判；此处机械锁定
    "约束正文仍在常驻入口层"，防止后续编辑把硬协议删弱或挪出 SKILL.md——
    挪走即降级为 references 按需层，失去"触发即必达"的保证。
    """
    missing = [desc for phrase, desc in HARD_PROTOCOL_ANCHORS
               if phrase not in skill_text]
    if missing:
        note("FAIL", "SKILL.md 执行硬协议锚定缺失（收口/落盘约束被删弱或移出常驻层）：%s"
             % "、".join(missing))


def check_chapter_number(path):
    """文件名前缀（01-10）与该章首行标题编号一致。"""
    m = re.match(r"^(\d{2})-", path.name)
    if not m:
        return
    expected = str(int(m.group(1)))
    first = path.read_text(encoding="utf-8").splitlines()
    for line in first[:3]:
        t = re.match(r"^# (\d+)\b", line)
        if t:
            if t.group(1) != expected:
                note("FAIL", "%s：文件名前缀章号 %s 与首行标题章号 %s 不一致"
                     % (path.name, expected, t.group(1)))
            return


def strip_topic(text):
    """取标题的主题词：去编号，去掉「（…）」括注（功能括注只留在地图小节）。"""
    t = re.split(r"[（(]", text, maxsplit=1)[0].strip()
    t = re.sub(r"^\d+(?:[\.、]\s*|\s+)", "", t)   # 去掉 3. / 3 编号
    return t.strip()


def check_title_topic(path, map_text):
    """主题词三方一致：文件名主题（NN- 之后）== H1 主题 == 地图小节主题。

    命名纪律：文件名 = `NN-主题词`；H1 首行 = `# N 主题词`（不带括注）；
    地图小节 = `## N. 主题词（功能括注）`。三者共享同一主题词，改一处必须同步。
    """
    m = re.match(r"^(\d{2})-(.+)\.md$", path.name)
    if not m:
        return
    chap = str(int(m.group(1)))
    file_topic = m.group(2).strip()
    first = path.read_text(encoding="utf-8").splitlines()
    h1 = next((ln for ln in first[:3] if ln.startswith("# ")), "")
    hm = re.match(r"^#\s+(\d+)\s+(.+)$", h1)
    if not hm or hm.group(1) != chap:
        return    # 章号不一致由 check_chapter_number 报
    h1_topic = strip_topic(hm.group(2))
    if h1_topic != file_topic:
        note("FAIL", "%s：文件名主题词 [%s] 与 H1 主题词 [%s] 不一致（H1 应写 `# %s %s`）"
             % (path.name, file_topic, h1_topic, chap, file_topic))
        return
    for ln in map_text.splitlines():
        mm = re.match(r"^#+\s+%s[\.、]?\s+(.+)$" % re.escape(chap), ln)
        if mm:
            if strip_topic(mm.group(1)) != file_topic:
                note("FAIL", "%s：文件名主题词 [%s] 与地图小节主题词 [%s] 不一致（%s 章）"
                     % (path.name, file_topic, strip_topic(mm.group(1)), chap))
            return
    note("FAIL", "%s：00-全局地图.md 中找不到 `## %s. ...` 对应小节" % (path.name, chap))


def collect_checkpoint_ids():
    """跨章判点全集：全部 references 正文表格首列 `| N.M.K |` 的判点号。

    判点号是稳定主键（docs/00：区内引用写纯文本 x.y.z，不链文件名），正文互引
    与跨章引用必须指向已登记判点，防止判点漂移后引用悬空。
    """
    ids = set()
    for path in sorted(REF_DIR.glob("*.md")):
        if path.name == "00-全局地图.md":
            continue
        text = path.read_text(encoding="utf-8")
        ids |= {m.group(1) for m in re.finditer(r"^\|\s*(\d+\.\d+\.\d+)\s*\|", text, re.M)}
    return ids


def check_ref_ids(path, text, universe):
    """判点引用守卫：正文（非标题行）出现的 x.y.z 判点号必须存在于判点全集。

    排除两类伪判点：表格首列（定义处，本身在全集）、两位数版本/日期（后段不齐）。
    用于防漂移——改判点号时漏改的引用在此报 FAIL。
    """
    for ln, line in enumerate(text.splitlines(), 1):
        if line.startswith("#"):
            continue
        for m in re.finditer(r"(?<![\d.])(\d+)\.(\d+)\.(\d+)(?![\d.])", line):
            a, b, c = map(int, m.groups())
            if not (1 <= a <= 10) or b < 1 or c < 1:
                continue       # 非章号段 / 版本号 / 无意义编号，跳过
            cid = "%d.%d.%d" % (a, b, c)
            if cid not in universe:
                note("FAIL", "%s：引用的判点号 %s 在判点全集中不存在（改判点号后漏同步引用？）:%d"
                     % (path.name, cid, ln))


def check_map_section(path, text, map_text):
    """地图 ↔ 正文小节双向对齐：NN- 章正文的 `## N.M` 小节必须在地图出现且一一对应。

    00-全局地图.md 承诺自己是"章树全貌"；正文新增/删除小节若不同步地图，
    全貌导航会失真——此处对 NN- 编号章做双向差集检查。

    注意：文件名前缀 = 2 位（`01-` / `02-` ... / `10-`），而地图与正文小节 =
    1-2 位自然数字（`## 1.1` / `## 10.1`），需将章号归一为 `int` 后取字串，
    不然 01-09 章的 `startswith` 会全部落空、本检查静默失效。
    """
    m = re.match(r"^(\d{2})-", path.name)
    if not m:
        return
    chap = str(int(m.group(1)))
    body_secs = set(re.findall(r"^##\s*(\d+\.\d+)\b", text, re.M))
    body_secs = {s for s in body_secs if s.startswith(chap + ".")}
    map_secs = set(re.findall(r"^#{2,4}\s*(\d+\.\d+)\b", map_text, re.M))
    map_secs = {s for s in map_secs if s.startswith(chap + ".")}
    for s in sorted(body_secs - map_secs, key=lambda x: [int(v) for v in x.split(".")]):
        note("FAIL", "%s：正文小节 %s 未出现在 00-全局地图.md（地图漏登记）" % (path.name, s))
    for s in sorted(map_secs - body_secs, key=lambda x: [int(v) for v in x.split(".")]):
        note("FAIL", "%s：地图小节 %s 在本章正文中不存在（地图冗余或正文缺节）" % (path.name, s))


def check_project_overview(meta, universe):
    """防展示页与技能正文漂移，不将展示页纳入发布包内容校验。"""
    paths = (OVERVIEW_HTML, OVERVIEW_SCRIPT, OVERVIEW_CHARTS, OVERVIEW_STYLE)
    if any(not path.exists() for path in paths):
        for path in paths:
            if not path.exists():
                note("FAIL", "project_overview/ 缺失展示文件：%s" % path.name)
        return

    html = OVERVIEW_HTML.read_text(encoding="utf-8")
    script = OVERVIEW_SCRIPT.read_text(encoding="utf-8")
    charts = OVERVIEW_CHARTS.read_text(encoding="utf-8")
    style = OVERVIEW_STYLE.read_text(encoding="utf-8")
    counts = [sum(cid.startswith("%d." % chap) for cid in universe) for chap in range(1, 11)]
    total = sum(counts)
    expected_chart = "var data = [%s];" % ", ".join(str(count) for count in counts)

    if expected_chart not in charts:
        note("FAIL", "project_overview/charts.js 判点分布与 references/ 实际判点数不一致（应为 %s）"
             % counts)
    if html.count('data-count="%d"' % total) < 2 or ("%d 个判点" % total) not in html:
        note("FAIL", "project_overview/index.html 的判点总数未同步为 %d" % total)

    chapter_pts = {int(no): int(pts) for no, pts in re.findall(
        r"no:\s*'(\d{2})'.*?pts:\s*(\d+)", script, re.S) if no != "00"}
    expected_pts = {chap: count for chap, count in enumerate(counts, 1)}
    if chapter_pts != expected_pts:
        note("FAIL", "project_overview/script.js 的章节判点数与 references/ 不一致（应为 %s）"
             % expected_pts)

    version = meta.get("version", "")
    updated = meta.get("updated", "")
    if version and ("v%s" % version) not in html:
        note("FAIL", "project_overview/index.html 未同步 skill.json.version=%s" % version)
    if updated and updated not in html:
        note("FAIL", "project_overview/index.html 未同步 skill.json.updated=%s" % updated)

    if "fonts.googleapis.com" in html or "fonts.gstatic.com" in html:
        note("FAIL", "project_overview/index.html 仍依赖远程字体，应使用本机字体栈")
    chart_tag = re.search(r'<script[^>]+src="https://cdn\.jsdelivr\.net/npm/chart\.js@4\.4\.1/dist/chart\.umd\.min\.js"[^>]*>', html)
    if chart_tag is None or "integrity=\"sha384-" not in chart_tag.group(0) or "crossorigin=\"anonymous\"" not in chart_tag.group(0):
        note("FAIL", "project_overview 的 Chart.js CDN 脚本须固定版本并设置 SRI 与 anonymous CORS")
    if "prefers-reduced-motion" not in style:
        note("FAIL", "project_overview/style.css 缺少 prefers-reduced-motion 动效降级")
    if "setAttribute('role', 'tablist')" not in script or "addEventListener('keydown'" not in script:
        note("FAIL", "project_overview/script.js 缺少 Tab 的 ARIA 语义或键盘操作")

    pairs = (
        (ROOT / "docs" / "assets" / "badges.svg", OVERVIEW_DIR / "assets" / "badges.svg"),
        (ROOT / "docs" / "assets" / "overview.svg", OVERVIEW_DIR / "assets" / "overview.svg"),
    )
    for source, mirror in pairs:
        if not source.exists() or not mirror.exists():
            note("FAIL", "生成资产缺失：%s 或 %s" % (source, mirror))
        elif source.read_bytes() != mirror.read_bytes():
            note("FAIL", "生成资产副本不一致：%s 与 %s（请重跑对应 docs/scripts/generate_*.py）"
                 % (source.name, mirror.name))

    badge = ROOT / "docs" / "assets" / "badges.svg"
    if badge.exists():
        for value in (version, updated, str(len(KNOWN_REF_FILES))):
            if value and (">%s</text>" % value) not in badge.read_text(encoding="utf-8"):
                note("FAIL", "docs/assets/badges.svg 未同步源数据 %s（请重跑 generate_badges.py）" % value)

    # 展示页行数 / 文件数漂移检查（防"章节行数"类数字失真）
    ref_lines = {p.name: len(p.read_text(encoding="utf-8").splitlines()) for p in REF_DIR.glob("*.md")}
    ref_total = sum(ref_lines.values())
    if ("references/ %d 篇" % len(ref_lines)) not in html:
        note("FAIL", "project_overview/index.html 的 references/ 篇数未同步为 %d" % len(ref_lines))
    if ("%d 行" % ref_total) not in html:
        note("FAIL", "project_overview/index.html 的 references/ 总行数未同步为 %d" % ref_total)
    file_lines = dict(re.findall(r"file:\s*'([^']+\.md)'.*?lines:\s*(\d+)", script, re.S))
    for name, real in ref_lines.items():
        shown = file_lines.get(name)
        if shown is None:
            note("FAIL", "project_overview/script.js 的 CHAPTERS 缺失文件 %s 的行数登记" % name)
        elif int(shown) != real:
            note("FAIL", "project_overview/script.js 的 %s 行数登记为 %s，与磁盘实际 %d 行不一致"
                 % (name, shown, real))


# ---------- 主流程 ----------

def main():
    results.clear()  # 每次运行独立：避免测试/重复调用时残留历史结果
    quiet = "--quiet" in sys.argv[1:]

    # A. 元数据一致性（frontmatter <-> skill.json <-> 目录名）
    skill_text = SKILL.read_text(encoding="utf-8")
    fm = parse_frontmatter(skill_text)
    if fm is None:
        note("FAIL", "SKILL.md 缺少 YAML frontmatter")
        fm = {}
    fm_meta = extract_metadata(skill_text)

    if not re.fullmatch(r"[a-z0-9-]+", fm.get("name", "")):
        note("FAIL", "frontmatter name 须为小写字母/数字/连字符")
    elif fm.get("name") != ROOT.name:
        note("FAIL", "frontmatter name=%s 与目录名 %s 不一致" % (fm.get("name"), ROOT.name))
    if len(fm.get("description", "")) > 1024:
        note("FAIL", "frontmatter description 超 1024 字符（当前 %d）" % len(fm.get("description", "")))
    if not fm_meta:
        note("FAIL", "frontmatter 缺 metadata 块（author/version/updated）")

    if not SKILL_JSON.exists():
        note("FAIL", "缺少 skill.json（与 frontmatter 双写同步的机器可读元数据）")
        meta = {}
    else:
        meta = json.loads(SKILL_JSON.read_text(encoding="utf-8"))
        for key in ("name", "displayName", "description", "version", "author", "keywords"):
            if key not in meta:
                note("FAIL", "skill.json 缺字段：%s" % key)
        if meta.get("name") != fm.get("name"):
            note("FAIL", "skill.json.name=%s 与 frontmatter name=%s 不一致"
                 % (meta.get("name"), fm.get("name")))
        if meta.get("description") != fm.get("description"):
            note("FAIL", "skill.json.description 与 SKILL.md frontmatter.description 不一致（应同源同文）")
        if meta.get("version") != fm_meta.get("version"):
            note("FAIL", "skill.json.version=%s 与 frontmatter metadata.version=%s 不一致"
                 % (meta.get("version"), fm_meta.get("version")))
        if meta.get("author") != fm_meta.get("author"):
            note("FAIL", "skill.json.author=%s 与 frontmatter metadata.author=%s 不一致"
                 % (meta.get("author"), fm_meta.get("author")))
        if meta.get("updated") and fm_meta.get("updated") and meta.get("updated") != fm_meta.get("updated"):
            note("WARN", "skill.json.updated=%s 与 frontmatter metadata.updated=%s 不一致"
                 % (meta.get("updated"), fm_meta.get("updated")))

    # B. 结构完整性
    if len(skill_text.splitlines()) > SKILL_MAX_LINES:
        note("FAIL", "SKILL.md %d 行，超过 %d 行限制" % (len(skill_text.splitlines()), SKILL_MAX_LINES))
    check_hard_protocol(skill_text)   # 执行硬协议锚定：删弱/移出常驻层即 FAIL
    actual = {p.name for p in REF_DIR.glob("*.md")}
    if actual != KNOWN_REF_FILES:
        for name in sorted(actual - KNOWN_REF_FILES):
            note("FAIL", "references/ 出现未登记文件（须同步登记表与维护文档）：%s" % name)
        for name in sorted(KNOWN_REF_FILES - actual):
            note("FAIL", "references/ 缺登记文件：%s" % name)

    # C. 逐运行时正文文件扫描
    map_text = (REF_DIR / "00-全局地图.md").read_text(encoding="utf-8")
    universe = collect_checkpoint_ids()
    check_project_overview(meta, universe)
    for path in runtime_targets():
        if not path.exists():
            note("FAIL", "缺失文件：%s" % path)
            continue
        text = path.read_text(encoding="utf-8")
        check_wikilink(path, text)
        check_banned_chars(path, text)
        check_links(path, text)
        if path != SKILL and path != README and path.name != "00-全局地图.md":
            check_toc(path)
            check_chapter_number(path)
            check_title_topic(path, map_text)
        if path.name != "00-全局地图.md":
            check_ref_ids(path, text, universe)
            check_map_section(path, text, map_text)

    # 汇总
    fails = [r for r in results if r[0] == "FAIL"]
    warns = [r for r in results if r[0] == "WARN"]
    if not quiet:
        for path in runtime_targets():
            if path.exists():
                print("[info] %-34s %5d lines" % (path.name, len(path.read_text(encoding="utf-8").splitlines())))
        print("-" * 60)
    for sev, msg in results:
        print("[%s] %s" % (sev, msg))
    print("-" * 60)
    print("FAIL %d / WARN %d / exit code %d" % (len(fails), len(warns), 1 if fails else 0))
    sys.exit(1 if fails else 0)


def configure_stdio():
    """Windows 默认 GBK 控制台会把中文文件名打成乱码；尽量切到 UTF-8。"""
    for stream in (sys.stdout, sys.stderr):
        reconf = getattr(stream, "reconfigure", None)
        if not callable(reconf):
            continue
        try:
            reconf(encoding="utf-8", errors="replace")
        except (OSError, ValueError):
            pass


if __name__ == "__main__":
    configure_stdio()
    main()
