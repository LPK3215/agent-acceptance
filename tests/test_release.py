# -*- coding: utf-8 -*-
"""scripts/release.py 单元测试。

覆盖：
- version()：从 skill.json 读取版本
- release_items()：发布物清单（SKILL.md + skill.json + references/*）
- cmd_package()：打包流程（校验 + zip 生成）
- cmd_install()：安装流程（校验 + 复制 + 备份旧目录）
- 安装失败的回滚行为
"""

import json
import sys
import zipfile
from pathlib import Path

import pytest

sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "scripts"))
import release  # noqa: E402


# ---------------------------------------------------------------------------
# 纯函数测试
# ---------------------------------------------------------------------------


class TestVersion:
    """version()：从 skill.json 读取版本号。"""

    def test_reads_version(self, repo_root):
        # 真实仓库的 skill.json 应当有 version 字段
        v = release.version()
        assert isinstance(v, str)
        assert v.count(".") >= 1  # 至少 x.y 格式


class TestReleaseItems:
    """release_items()：发布物清单。"""

    def test_contains_required_files(self, repo_root):
        items = release.release_items()
        names = {p.name for p in items}
        assert "SKILL.md" in names
        assert "skill.json" in names
        assert "LICENSE" in names

    def test_includes_references(self, repo_root):
        items = release.release_items()
        # 至少包含 00-全局地图.md
        assert any(p.name == "00-全局地图.md" for p in items)

    def test_all_items_exist(self, repo_root):
        # 所有发布物都应当是实际存在的文件
        for p in release.release_items():
            assert p.exists(), f"发布物路径不存在: {p}"
            assert p.is_file(), f"发布物不是文件: {p}"


# ---------------------------------------------------------------------------
# 打包流程测试
# ---------------------------------------------------------------------------


class TestCmdPackage:
    """cmd_package()：校验通过后生成 zip。"""

    def test_package_creates_zip(self, tmp_path, monkeypatch):
        monkeypatch.setattr(release, "_verified", True)  # 跳过校验
        dest = tmp_path / "dist"
        rc = release.cmd_package(str(dest))
        assert rc == 0
        zips = list(dest.glob("*.zip"))
        assert len(zips) == 1, f"应生成 1 个 zip，实际: {zips}"

    def test_package_zip_contents(self, tmp_path, monkeypatch):
        monkeypatch.setattr(release, "_verified", True)
        dest = tmp_path / "dist"
        release.cmd_package(str(dest))
        zip_path = next(dest.glob("*.zip"))
        with zipfile.ZipFile(zip_path) as zf:
            names = zf.namelist()
            # zip 顶层应带技能目录名
            assert any(n.startswith("agent-acceptance/") for n in names)
            # 应含 SKILL.md 与 skill.json
            assert any("SKILL.md" in n for n in names)
            assert any("skill.json" in n for n in names)
            assert any(n.endswith("/LICENSE") or n.endswith("LICENSE") for n in names)

    def test_package_skips_without_verify(self, tmp_path, monkeypatch):
        # 校验未通过时，cmd_package 应中止
        monkeypatch.setattr(release, "_verified", False)
        # monkeypatch run_verify 使其返回 False
        monkeypatch.setattr(release, "run_verify", lambda: False)
        rc = release.cmd_package(str(tmp_path / "dist"))
        assert rc == 1


class TestResolveInstallTargets:
    """resolve_install_targets()：显式 dest 优先；否则探测本机助手目录。"""

    def test_explicit_dest_wins(self, tmp_path):
        dest = tmp_path / "skills" / "agent-acceptance"
        targets = release.resolve_install_targets(str(dest))
        assert targets == [dest.resolve()]

    def test_detects_existing_claude(self, tmp_path, monkeypatch):
        claude_skills = tmp_path / ".claude" / "skills"
        codebuddy_skills = tmp_path / ".codebuddy" / "skills"
        (tmp_path / ".claude").mkdir()
        monkeypatch.setattr(
            release,
            "known_skill_parents",
            lambda: (codebuddy_skills, claude_skills),
        )
        targets = release.resolve_install_targets(None)
        assert targets == [claude_skills / release.SKILL_NAME]

    def test_detects_both_assistants(self, tmp_path, monkeypatch):
        claude_skills = tmp_path / ".claude" / "skills"
        codebuddy_skills = tmp_path / ".codebuddy" / "skills"
        (tmp_path / ".claude").mkdir()
        (tmp_path / ".codebuddy").mkdir()
        monkeypatch.setattr(
            release,
            "known_skill_parents",
            lambda: (codebuddy_skills, claude_skills),
        )
        targets = release.resolve_install_targets(None)
        assert targets == [
            codebuddy_skills / release.SKILL_NAME,
            claude_skills / release.SKILL_NAME,
        ]

    def test_fallback_when_none_exist(self, tmp_path, monkeypatch):
        claude_skills = tmp_path / ".claude" / "skills"
        codebuddy_skills = tmp_path / ".codebuddy" / "skills"
        monkeypatch.setattr(
            release,
            "known_skill_parents",
            lambda: (codebuddy_skills, claude_skills),
        )
        targets = release.resolve_install_targets(None)
        assert targets == [codebuddy_skills / release.SKILL_NAME]


# ---------------------------------------------------------------------------
# 安装流程测试
# ---------------------------------------------------------------------------


class TestCmdInstall:
    """cmd_install()：校验通过后安装到目标目录。"""

    def test_install_copies_files(self, tmp_path, monkeypatch):
        monkeypatch.setattr(release, "_verified", True)
        dest = tmp_path / "skills" / "agent-acceptance"
        rc = release.cmd_install(str(dest))
        assert rc == 0
        assert (dest / "SKILL.md").exists()
        assert (dest / "skill.json").exists()
        assert (dest / "LICENSE").exists()

    def test_install_creates_backup(self, tmp_path, monkeypatch):
        monkeypatch.setattr(release, "_verified", True)
        dest = tmp_path / "skills" / "agent-acceptance"
        # 先创建旧安装
        dest.mkdir(parents=True)
        (dest / "old_file.txt").write_text("旧内容", encoding="utf-8")
        rc = release.cmd_install(str(dest))
        assert rc == 0
        # 应当生成了带时间戳的备份目录
        backups = list(dest.parent.glob(".agent-acceptance.backup-*"))
        assert len(backups) == 1, f"应生成 1 个备份，实际: {backups}"
        assert (backups[0] / "old_file.txt").exists(), "备份应保留旧文件"

    def test_install_skips_without_verify(self, tmp_path, monkeypatch):
        monkeypatch.setattr(release, "_verified", False)
        monkeypatch.setattr(release, "run_verify", lambda: False)
        rc = release.cmd_install(str(tmp_path / "skills" / "x"))
        assert rc == 1

    def test_install_validates_name(self, tmp_path, monkeypatch):
        monkeypatch.setattr(release, "_verified", True)
        # 使用一个有效的目标目录
        dest = tmp_path / "skills" / "my-skill"
        rc = release.cmd_install(str(dest))
        assert rc == 0
        assert (dest / "SKILL.md").exists()


# ---------------------------------------------------------------------------
# 主流程集成测试
# ---------------------------------------------------------------------------


class TestMain:
    """main()：解析参数并分发子命令。"""

    def test_check_command(self, monkeypatch):
        monkeypatch.setattr(release, "run_verify", lambda: True)
        monkeypatch.setattr(sys, "argv", ["release.py", "check"])
        # main() 返回退出码（当 __name__ != "__main__" 时不会 sys.exit）
        result = release.main()
        assert result == 0

    def test_invalid_command(self, monkeypatch):
        monkeypatch.setattr(sys, "argv", ["release.py", "no-such-cmd"])
        with pytest.raises(SystemExit) as exc:
            release.main()
        assert exc.value.code == 2
