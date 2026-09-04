# -*- coding: utf-8 -*-
"""docs/scripts/generate_badges.py 与 generate_overview.py 单元测试。

覆盖：
- badges()：从 skill.json 和 references 读取数据
- est_w()：文本宽度估算
- badge_svg()：生成单个徽章 SVG
- _text() / _card()：概览图基础构件
- main()：端到端生成到目标文件
- 双端同步输出一致性
"""

import sys
import json
from pathlib import Path

import pytest

DOCS_SCRIPTS = Path(__file__).resolve().parent.parent / "docs" / "scripts"
sys.path.insert(0, str(DOCS_SCRIPTS))
import generate_badges  # noqa: E402
import generate_overview  # noqa: E402


# ---------------------------------------------------------------------------
# generate_badges.py
# ---------------------------------------------------------------------------


class TestBadgesData:
    """badges()：从源数据读取徽章数据。"""

    def test_returns_five_badges(self, repo_root):
        items = generate_badges.badges()
        assert len(items) == 5

    def test_contains_required_labels(self, repo_root):
        labels = {b[0] for b in generate_badges.badges()}
        assert labels == {"version", "license", "references", "updated", "spec"}

    def test_version_matches_skill_json(self, repo_root):
        meta = json.loads((repo_root / "skill.json").read_text(encoding="utf-8"))
        version_badge = next(b for b in generate_badges.badges() if b[0] == "version")
        assert version_badge[1] == meta["version"]

    def test_references_count_matches_files(self, repo_root):
        actual = len(list((repo_root / "references").glob("*.md")))
        ref_badge = next(b for b in generate_badges.badges() if b[0] == "references")
        assert ref_badge[1] == str(actual)


class TestEstW:
    """est_w()：文本宽度估算。"""

    def test_empty_string(self):
        assert generate_badges.est_w("") == 2  # 末尾 +2 留白

    def test_longer_text_wider(self):
        assert generate_badges.est_w("hello") < generate_badges.est_w("helloworld")

    def test_narrow_chars(self):
        # 窄字符 i, l 应当比同等长度的普通字符占用更少宽度
        narrow = generate_badges.est_w("ilil")
        wide = generate_badges.est_w("mwmw")
        assert narrow < wide


class TestBadgeSvg:
    """badge_svg()：单个徽章 SVG 生成。"""

    def test_returns_parts_and_width(self):
        parts, w = generate_badges.badge_svg("version", "1.0.0", "#0369a1", 0)
        assert isinstance(parts, list)
        assert isinstance(w, float)
        assert w > 0

    def test_contains_label_and_value(self):
        parts, _ = generate_badges.badge_svg("version", "1.0.0", "#0369a1", 0)
        text = "\n".join(parts)
        assert "version" in text
        assert "1.0.0" in text
        assert "#0369a1" in text

    def test_x_offset(self):
        _, w0 = generate_badges.badge_svg("a", "1", "#000", 0)
        parts1, w1 = generate_badges.badge_svg("a", "1", "#000", 100)
        # x=100 时，矩形 x 属性应为 100
        assert 'x="100.0"' in parts1[1]  # rect 元素


class TestGenerateBadgesMain:
    """generate_badges.main()：端到端生成到目标文件。"""

    def test_writes_two_files(self, tmp_path, monkeypatch):
        monkeypatch.setattr(generate_badges, "ROOT", tmp_path)
        # 创建 skill.json 和 references
        (tmp_path / "skill.json").write_text(
            json.dumps({"version": "9.9.9", "updated": "2026-12-31"}),
            encoding="utf-8",
        )
        (tmp_path / "references").mkdir()
        (tmp_path / "references" / "00-全局地图.md").write_text("占位", encoding="utf-8")

        generate_badges.main()

        badge_docs = tmp_path / "docs" / "assets" / "badges.svg"
        badge_ov = tmp_path / "project_overview" / "assets" / "badges.svg"
        assert badge_docs.exists()
        assert badge_ov.exists()

    def test_both_outputs_identical(self, tmp_path, monkeypatch):
        monkeypatch.setattr(generate_badges, "ROOT", tmp_path)
        (tmp_path / "skill.json").write_text(
            json.dumps({"version": "9.9.9", "updated": "2026-12-31"}),
            encoding="utf-8",
        )
        (tmp_path / "references").mkdir()
        (tmp_path / "references" / "00-全局地图.md").write_text("占位", encoding="utf-8")

        generate_badges.main()

        badge_docs = tmp_path / "docs" / "assets" / "badges.svg"
        badge_ov = tmp_path / "project_overview" / "assets" / "badges.svg"
        assert badge_docs.read_bytes() == badge_ov.read_bytes()

    def test_contains_expected_values(self, tmp_path, monkeypatch):
        monkeypatch.setattr(generate_badges, "ROOT", tmp_path)
        (tmp_path / "skill.json").write_text(
            json.dumps({"version": "9.9.9", "updated": "2026-12-31"}),
            encoding="utf-8",
        )
        (tmp_path / "references").mkdir()
        (tmp_path / "references" / "00-全局地图.md").write_text("占位", encoding="utf-8")

        generate_badges.main()

        content = (tmp_path / "docs" / "assets" / "badges.svg").read_text(encoding="utf-8")
        assert "9.9.9" in content
        assert "2026-12-31" in content
        assert "MIT" in content
        assert '1</text>' in content  # references 数量 = 1


# ---------------------------------------------------------------------------
# generate_overview.py
# ---------------------------------------------------------------------------


class TestOverviewText:
    """_text()：SVG text 元素生成。"""

    def test_basic(self):
        svg = generate_overview._text(10, 20, "hello", size=12)
        assert 'x="10"' in svg
        assert 'y="20"' in svg
        assert 'font-size="12"' in svg
        assert ">hello<" in svg

    def test_mono_class(self):
        svg = generate_overview._text(0, 0, "test", mono=True)
        assert "ui-monospace" in svg

    def test_escapes_xml(self):
        svg = generate_overview._text(0, 0, "a & b < c")
        assert "&amp;" in svg
        assert "&lt;" in svg


class TestOverviewCard:
    """_card()：SVG 卡片生成。"""

    def test_has_rect(self):
        parts = generate_overview._card(10, 20, 100, 50)
        text = "\n".join(parts)
        assert "<rect" in text
        assert 'x="10"' in text

    def test_accent_adds_bar(self):
        parts = generate_overview._card(10, 20, 100, 50, accent="#ff0000")
        text = "\n".join(parts)
        assert "#ff0000" in text


class TestOverviewMain:
    """generate_overview.main()：端到端生成到目标文件。"""

    def test_writes_two_files(self, tmp_path, monkeypatch):
        monkeypatch.setattr(generate_overview, "ROOT", tmp_path)
        generate_overview.main()
        ov_docs = tmp_path / "docs" / "assets" / "overview.svg"
        ov_po = tmp_path / "project_overview" / "assets" / "overview.svg"
        assert ov_docs.exists()
        assert ov_po.exists()

    def test_both_outputs_identical(self, tmp_path, monkeypatch):
        monkeypatch.setattr(generate_overview, "ROOT", tmp_path)
        generate_overview.main()
        ov_docs = tmp_path / "docs" / "assets" / "overview.svg"
        ov_po = tmp_path / "project_overview" / "assets" / "overview.svg"
        assert ov_docs.read_bytes() == ov_po.read_bytes()

    def test_contains_brand_text(self, tmp_path, monkeypatch):
        monkeypatch.setattr(generate_overview, "ROOT", tmp_path)
        generate_overview.main()
        content = (tmp_path / "docs" / "assets" / "overview.svg").read_text(encoding="utf-8")
        assert "agent-acceptance" in content
        assert 'xmlns="http://www.w3.org/2000/svg"' in content
