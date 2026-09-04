# -*- coding: utf-8 -*-
"""scripts/verify.py 单元测试。

覆盖：
- 字符白名单/黑名单 (is_allowed_char, check_banned_chars)
- frontmatter 解析 (parse_frontmatter, extract_metadata)
- 标题编号/导航编号提取 (heading_numbers, toc_numbers_in)
- 主题词归一化 (strip_topic, line_of)
- 判点引用守卫 (check_ref_ids, collect_checkpoint_ids)
- 地图小节双向对齐 (check_map_section)
- 执行硬协议锚定 (check_hard_protocol)
- check_project_overview 全套检查
"""

import json
import sys
from pathlib import Path

import pytest

# 引入被测模块（scripts/ 已通过 conftest.py 加入 sys.path）
sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "scripts"))
import verify  # noqa: E402


# ---------------------------------------------------------------------------
# 纯函数测试：不依赖全局 ROOT
# ---------------------------------------------------------------------------


class TestIsAllowedChar:
    """is_allowed_char：字符白名单判断。"""

    def test_cjk_han(self):
        assert verify.is_allowed_char("中") is True
        assert verify.is_allowed_char("文") is True

    def test_allowed_punct(self):
        for ch in "、。，：；‘’“”！？《》":
            assert verify.is_allowed_char(ch) is True, f"U+{ord(ch):04X} 应被允许"

    def test_allowed_symbols(self):
        assert verify.is_allowed_char("±") is True
        assert verify.is_allowed_char("≤") is True
        assert verify.is_allowed_char("≥") is True

    def test_ascii_alnum(self):
        # ASCII 英文数字不在白名单函数判定范围内；仅 CJK + 允许标点 + 允许符号 返回 True
        assert verify.is_allowed_char("a") is False
        assert verify.is_allowed_char("0") is False

    def test_banned_non_ascii(self):
        # 不在白名单内的非 ASCII 字符应返回 False
        assert verify.is_allowed_char("→") is False
        assert verify.is_allowed_char("★") is False


class TestParseFrontmatter:
    """parse_frontmatter：从文本中提取 YAML frontmatter 顶层键。"""

    def test_valid_frontmatter(self):
        text = (
            "---\n"
            "name: agent-acceptance\n"
            "description: A test skill\n"
            "metadata:\n"
            "  version: 1.0.0\n"
            "---\n"
            "# Title\n"
        )
        fm = verify.parse_frontmatter(text)
        assert fm is not None
        assert fm["name"] == "agent-acceptance"
        assert fm["description"] == "A test skill"

    def test_no_frontmatter(self):
        verify.parse_frontmatter("# Just a title\n\nbody") is None

    def test_quoted_value_unwrapped(self):
        text = '---\nname: "my-skill"\n---\n'
        fm = verify.parse_frontmatter(text)
        assert fm["name"] == "my-skill"


class TestExtractMetadata:
    """extract_metadata：从 frontmatter metadata: 子块提取键。"""

    def test_happy_path(self):
        text = (
            "---\n"
            "name: x\n"
            "metadata:\n"
            "  version: 2.0.0\n"
            "  author: alice\n"
            "  updated: 2026-01-01\n"
            "---\n"
        )
        m = verify.extract_metadata(text)
        assert m == {"version": "2.0.0", "author": "alice", "updated": "2026-01-01"}

    def test_no_metadata_block(self):
        assert verify.extract_metadata("---\nname: x\n---\n") == {}


class TestHeadingNumbers:
    """heading_numbers：提取 ## N.M 级小节编号。"""

    def test_basic(self):
        text = "## 1.1 简介\n\n## 1.2 细节\n\n## 10.1 大型章节\n"
        assert verify.heading_numbers(text) == {"1.1", "1.2", "10.1"}

    def test_ignores_non_section_headings(self):
        text = "# 一级标题\n\n## 2.1 正文\n\n### 2.1.1 更小\n"
        assert verify.heading_numbers(text) == {"2.1"}


class TestTocNumbersIn:
    """toc_numbers_in：从「正文小节导航」引用块提取编号。"""

    def test_happy_path(self):
        text = (
            "前缀\n"
            "> 正文小节导航\n"
            "> - 1.1 简介\n"
            "> - 1.2 细节\n"
            "后续\n"
        )
        assert verify.toc_numbers_in(text) == {"1.1", "1.2"}

    def test_no_toc(self):
        assert verify.toc_numbers_in("随便什么正文") is None


class TestStripTopic:
    """strip_topic：标题主题词归一化。"""

    def test_strips_number_prefix(self):
        assert verify.strip_topic("3. 考卷与评测集") == "考卷与评测集"

    def test_strips_chinese_paren(self):
        assert verify.strip_topic("范围（定义）") == "范围"

    def test_strips_english_paren(self):
        assert verify.strip_topic("Scope (definition)") == "Scope"

    def test_no_change(self):
        assert verify.strip_topic("纯净主题") == "纯净主题"


class TestLineOf:
    """line_of：pos 所在行号。"""

    def test_first_line(self):
        assert verify.line_of("abc", 0) == 1
        assert verify.line_of("abc", 2) == 1

    def test_later_line(self):
        assert verify.line_of("ab\ncd\nef", 3) == 2
        assert verify.line_of("ab\ncd\nef", 6) == 3


# ---------------------------------------------------------------------------
# 依赖全局 results / 文件系统的测试
# ---------------------------------------------------------------------------


class TestCheckBannedChars:
    """check_banned_chars：黑名单字符扫描。"""

    def test_clean_text_no_fail(self, tmp_path):
        verify.results.clear()
        p = tmp_path / "clean.md"
        p.write_text("这是正文，含有允许的标点：、。，。\n", encoding="utf-8")
        verify.check_banned_chars(p, p.read_text(encoding="utf-8"))
        assert not any(s == "FAIL" for s, _ in verify.results)

    def test_banned_char_triggers_fail(self, tmp_path):
        verify.results.clear()
        p = tmp_path / "bad.md"
        p.write_text("含有 ★ 非法符号\n", encoding="utf-8")
        verify.check_banned_chars(p, p.read_text(encoding="utf-8"))
        assert any("黑名单字符" in msg and "FAIL" == sev for sev, msg in verify.results)


class TestCheckWikilink:
    """check_wikilink：Obsidian [[ ]] 扫描。"""

    def test_no_wikilink(self, tmp_path):
        verify.results.clear()
        p = tmp_path / "ok.md"
        p.write_text("这是普通正文，没有维基链接。\n", encoding="utf-8")
        verify.check_wikilink(p, p.read_text(encoding="utf-8"))
        assert not verify.results

    def test_wikilink_detected(self, tmp_path):
        verify.results.clear()
        p = tmp_path / "bad.md"
        p.write_text("参见 [[某文件]] 了解更多\n", encoding="utf-8")
        verify.check_wikilink(p, p.read_text(encoding="utf-8"))
        assert any("wikilink" in msg for _, msg in verify.results)


class TestCheckLinks:
    """check_links：相对链接目标存在性 + 白名单范围。"""

    def test_valid_relative_link(self, tmp_path):
        verify.results.clear()
        (tmp_target := tmp_path / "target.md").write_text("目标", encoding="utf-8")
        p = tmp_path / "src.md"
        p.write_text("跳转到](./target.md)\n", encoding="utf-8")
        verify.check_links(p, p.read_text(encoding="utf-8"))
        assert not any(sev == "FAIL" for sev, _ in verify.results)

    def test_broken_link_fails(self, tmp_path):
        verify.results.clear()
        p = tmp_path / "src.md"
        # 使用合法的 Markdown 链接格式 [text](target)，但目标不存在
        p.write_text("[跳转到](./不存在.md)\n", encoding="utf-8")
        verify.check_links(p, p.read_text(encoding="utf-8"))
        fails = [msg for sev, msg in verify.results if sev == "FAIL"]
        assert any("链接目标不存在" in msg for msg in fails), f"应报断链 FAIL，实际结果: {fails}"


class TestCheckHardProtocol:
    """check_hard_protocol：SKILL.md 中执行硬协议锚定。"""

    def test_all_anchors_present(self):
        verify.results.clear()
        text = "\n".join(phrase for phrase, _ in verify.HARD_PROTOCOL_ANCHORS) + "\n"
        verify.check_hard_protocol(text)
        assert not verify.results

    def test_missing_anchor_fails(self):
        verify.results.clear()
        # 只保留前面一半锚点，后面缺失
        partial = "\n".join(phrase for phrase, _ in verify.HARD_PROTOCOL_ANCHORS[:3])
        verify.check_hard_protocol(partial)
        assert any("执行硬协议锚定缺失" in msg and sev == "FAIL" for sev, msg in verify.results)


class TestCollectCheckpointIds:
    """collect_checkpoint_ids：跨章判点全集收集。"""

    def test_collects_ids(self, tmp_path, monkeypatch):
        ref_dir = tmp_path / "references"
        ref_dir.mkdir()
        (ref_dir / "00-全局地图.md").write_text("# 地图\n", encoding="utf-8")
        (ref_dir / "01-章.md").write_text("| 1.1.1 | 判点 |\n| 1.1.2 | 判点 |\n", encoding="utf-8")
        (ref_dir / "02-章.md").write_text("| 2.3.4 | 判点 |\n", encoding="utf-8")
        monkeypatch.setattr(verify, "REF_DIR", ref_dir)
        ids = verify.collect_checkpoint_ids()
        assert ids == {"1.1.1", "1.1.2", "2.3.4"}

    def test_excludes_00_map(self, tmp_path, monkeypatch):
        ref_dir = tmp_path / "references"
        ref_dir.mkdir()
        (ref_dir / "00-全局地图.md").write_text("| 99.99.99 | 伪判点 |\n", encoding="utf-8")
        monkeypatch.setattr(verify, "REF_DIR", ref_dir)
        assert verify.collect_checkpoint_ids() == set()


class TestCheckRefIds:
    """check_ref_ids：判点引用守卫。"""

    def test_valid_reference(self, tmp_path):
        verify.results.clear()
        p = tmp_path / "ref.md"
        p.write_text("参见 1.1.1 的描述\n", encoding="utf-8")
        verify.check_ref_ids(p, p.read_text(encoding="utf-8"), {"1.1.1", "1.1.2"})
        assert not verify.results

    def test_orphan_reference_fails(self, tmp_path):
        verify.results.clear()
        p = tmp_path / "ref.md"
        p.write_text("参见 9.9.9 的描述\n", encoding="utf-8")
        verify.check_ref_ids(p, p.read_text(encoding="utf-8"), {"1.1.1"})
        assert any("判点号 9.9.9" in msg and sev == "FAIL" for sev, msg in verify.results)


class TestCheckMapSection:
    """check_map_section：地图 ↔ 正文小节双向对齐。"""

    def test_aligned(self, tmp_path):
        verify.results.clear()
        (ref_dir := tmp_path / "references").mkdir()
        chapter = ref_dir / "01-章.md"
        chapter.write_text("# 1 章\n\n## 1.1 简介\n", encoding="utf-8")
        # 地图小节必须用 ## N.M 格式（与正文小节同级）
        map_text = "## 1. 章\n\n## 1.1 简介\n"
        verify.check_map_section(chapter, chapter.read_text(encoding="utf-8"), map_text)
        assert not verify.results

    def test_body_has_extra_fails(self, tmp_path):
        verify.results.clear()
        (ref_dir := tmp_path / "references").mkdir()
        chapter = ref_dir / "01-章.md"
        chapter.write_text("# 1 章\n\n## 1.1 简介\n\n## 1.2 漏网\n", encoding="utf-8")
        map_text = "## 1. 章\n- 1.1 简介\n"
        verify.check_map_section(chapter, chapter.read_text(encoding="utf-8"), map_text)
        assert any("未出现在 00-全局地图" in msg for _, msg in verify.results)


class TestCheckProjectOverview:
    """check_project_overview：展示页同步检查。"""

    def test_missing_overview_file_fails(self, tmp_path, monkeypatch, sample_metadata):
        verify.results.clear()
        monkeypatch.setattr(verify, "OVERVIEW_DIR", tmp_path / "project_overview")
        monkeypatch.setattr(verify, "OVERVIEW_HTML", tmp_path / "project_overview" / "index.html")
        monkeypatch.setattr(verify, "OVERVIEW_SCRIPT", tmp_path / "project_overview" / "script.js")
        monkeypatch.setattr(verify, "OVERVIEW_CHARTS", tmp_path / "project_overview" / "charts.js")
        monkeypatch.setattr(verify, "OVERVIEW_STYLE", tmp_path / "project_overview" / "style.css")
        verify.check_project_overview(sample_metadata, {"1.1.1"})
        assert any("缺失展示文件" in msg and sev == "FAIL" for sev, msg in verify.results)

    def test_all_synced_passes(self, tmp_path, monkeypatch, sample_metadata):
        verify.results.clear()
        ov_dir = tmp_path / "project_overview"
        ov_dir.mkdir()
        # 1 章 2 个判点，其余 0
        charts = "var data = [2, 0, 0, 0, 0, 0, 0, 0, 0, 0];"
        # script.js 中章节判点数必须与 charts 一致
        script = (
            "var chapters = [\n"
            "  { no: '01', pts: 2 },\n"
            "  { no: '02', pts: 0 },\n"
            "  { no: '03', pts: 0 },\n"
            "  { no: '04', pts: 0 },\n"
            "  { no: '05', pts: 0 },\n"
            "  { no: '06', pts: 0 },\n"
            "  { no: '07', pts: 0 },\n"
            "  { no: '08', pts: 0 },\n"
            "  { no: '09', pts: 0 },\n"
            "  { no: '10', pts: 0 },\n"
            "];\n"
            "setAttribute('role', 'tablist')\n"
            "addEventListener('keydown'\n"
        )
        style = "@media (prefers-reduced-motion: reduce) { }"
        html = (
            f"v{sample_metadata['version']} {sample_metadata['updated']}"
            'data-count="2" data-count="2" 2 个判点'
            '<script src="https://cdn.jsdelivr.net/npm/chart.js@4.4.1/dist/chart.umd.min.js"'
            ' integrity="sha384-abc" crossorigin="anonymous"></script>'
        )
        (ov_dir / "index.html").write_text(html, encoding="utf-8")
        (ov_dir / "script.js").write_text(script, encoding="utf-8")
        (ov_dir / "charts.js").write_text(charts, encoding="utf-8")
        (ov_dir / "style.css").write_text(style, encoding="utf-8")

        docs_assets = tmp_path / "docs" / "assets"
        docs_assets.mkdir(parents=True)
        # badges.svg 必须包含 version / updated / 文件数
        badge_content = (
            f">1.0.0</text>"
            f">2026-09-04</text>"
            f">12</text>"
        )
        for name in ("badges.svg", "overview.svg"):
            (ov_dir / "assets").mkdir(exist_ok=True)
            if name == "badges.svg":
                (docs_assets / name).write_text(badge_content, encoding="utf-8")
                (ov_dir / "assets" / name).write_text(badge_content, encoding="utf-8")
            else:
                (docs_assets / name).write_text("content", encoding="utf-8")
                (ov_dir / "assets" / name).write_text("content", encoding="utf-8")

        monkeypatch.setattr(verify, "OVERVIEW_DIR", ov_dir)
        monkeypatch.setattr(verify, "OVERVIEW_HTML", ov_dir / "index.html")
        monkeypatch.setattr(verify, "OVERVIEW_SCRIPT", ov_dir / "script.js")
        monkeypatch.setattr(verify, "OVERVIEW_CHARTS", ov_dir / "charts.js")
        monkeypatch.setattr(verify, "OVERVIEW_STYLE", ov_dir / "style.css")
        monkeypatch.setattr(verify, "ROOT", tmp_path)

        verify.check_project_overview(sample_metadata, {"1.1.1", "1.1.2"})
        fails = [msg for sev, msg in verify.results if sev == "FAIL"]
        assert fails == [], f"不应有 FAIL，但看到: {fails}"


# ---------------------------------------------------------------------------
# 集成测试：跑一次完整的主流程
# ---------------------------------------------------------------------------


class TestMainIntegration:
    """跑 verify.main() 集成测试，断言退出码与摘要。"""

    def test_main_on_real_repo(self, monkeypatch, capsys):
        """对真实仓库跑 verify.main()，应当无 FAIL。"""
        monkeypatch.setattr(sys, "argv", ["verify.py"])
        with pytest.raises(SystemExit) as exc:
            verify.main()
        # 真实仓库应当通过（exit 0）；Windows 上 capsys 可能因编码截断输出，
        # 这里只断言退出码——FAIL 详情由 verify.py 自身输出。
        assert exc.value.code == 0, "verify.py 不应 FAIL，请直接运行 python scripts/verify.py 查看详情"
