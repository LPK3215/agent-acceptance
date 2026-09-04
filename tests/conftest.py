# -*- coding: utf-8 -*-
"""测试共享 fixtures。

提供：
- 仓库根路径导入 helpers
- 临时仓库骨架 fixture（用于需要隔离文件系统的测试）
- 常用样本数据
"""

import sys
import json
import tempfile
import shutil
from pathlib import Path

import pytest

# 让 tests/ 下的模块能 import scripts/ 下的被测脚本
REPO_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(REPO_ROOT))


@pytest.fixture
def repo_root():
    """返回仓库根目录路径。"""
    return REPO_ROOT


@pytest.fixture
def sample_metadata():
    """返回可用的 skill.json 样本元数据。"""
    return {
        "name": "agent-acceptance",
        "displayName": "Agent Acceptance",
        "description": "AI Agent 项目的工程验收与定档标准",
        "version": "1.0.0",
        "author": "LPK3215",
        "updated": "2026-09-04",
        "keywords": ["agent", "acceptance", "review"],
    }


@pytest.fixture
def tmp_repo(tmp_path, sample_metadata):
    """创建一个最小化的临时仓库骨架，返回其根目录 Path。

    结构：
      tmp/
        SKILL.md          （含合法 frontmatter）
        skill.json        （与 frontmatter 一致）
        references/
          00-全局地图.md
          01-范围、形态与档位.md
    """
    skill_md = tmp_path / "SKILL.md"
    skill_md.write_text(
        "---\n"
        "name: agent-acceptance\n"
        "description: AI Agent 项目的工程验收与定档标准\n"
        "metadata:\n"
        f"  version: {sample_metadata['version']}\n"
        f"  author: {sample_metadata['author']}\n"
        f"  updated: {sample_metadata['updated']}\n"
        "---\n"
        "# agent-acceptance\n\n"
        "## 1. 引言\n\n"
        "正文占位。\n",
        encoding="utf-8",
    )

    skill_json = tmp_path / "skill.json"
    skill_json.write_text(json.dumps(sample_metadata, ensure_ascii=False, indent=2), encoding="utf-8")

    ref_dir = tmp_path / "references"
    ref_dir.mkdir()

    (ref_dir / "00-全局地图.md").write_text(
        "# 全局地图\n\n"
        "## 1. 范围、形态与档位\n\n"
        "- 1.1 范围定义\n",
        encoding="utf-8",
    )
    (ref_dir / "01-范围、形态与档位.md").write_text(
        "# 1 范围、形态与档位\n\n"
        "## 1.1 范围定义\n\n"
        "| 1.1.1 | 占位判点 |\n",
        encoding="utf-8",
    )

    return tmp_path
