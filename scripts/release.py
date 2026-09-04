#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""agent-acceptance 一键发布工具（作者 / 维护者专用）。

参考 CodeBuddy 官方 skill-creator 的发布范式（quick_validate + package_skill），
但按本仓库 docs/00 写作规范做差异化：
  - 校验复用 scripts/verify.py（比官方 quick_validate 更严：黑名单字符 / wikilink / 链接白名单 / ToC / 元数据三方一致）；
  - 打包单元 = SKILL.md + skill.json + references/（docs/ scripts/ .codebuddy 等维护物不进发布物）；
  - zip 顶层带技能目录名（agent-acceptance/），解压即得一个可直接加载的技能目录；
  - 提供 install：一键装到本机 CodeBuddy 用户技能目录（~/.codebuddy/skills/<name>/）；
    若同名目录已存在，先保留带时间戳的备份，再切换至新目录。

用法（任意目录执行均可，脚本按自身路径定位仓库根）：
  python scripts/release.py check      一键检验（等价 python scripts/verify.py）
  python scripts/release.py package    校验通过后打 zip 到 dist/agent-acceptance-<version>.zip
  python scripts/release.py install    校验通过后装到本机 ~/.codebuddy/skills/agent-acceptance/
  python scripts/release.py all        按序执行 check -> package -> install（缺省子命令）
  python scripts/release.py package --dest 其它输出目录
  python scripts/release.py install --dest 其它技能目录（覆盖默认本机路径）

退出码：0 = 成功；1 = 校验失败或发布过程出错；2 = 用法错误。
"""

import argparse
from datetime import datetime
import json
import shutil
import subprocess
import sys
import zipfile
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
SKILL_NAME = ROOT.name                       # agent-acceptance（zip 顶层目录名 = 技能目录名）
VERIFY = ROOT / "scripts" / "verify.py"
SKILL_JSON = ROOT / "skill.json"
DEFAULT_DIST = ROOT / "dist"
DEFAULT_INSTALL = Path.home() / ".codebuddy" / "skills" / SKILL_NAME

# 发布物清单（与 docs/00 打包边界一致：SKILL.md + skill.json + references/）
RELEASE_FILES = ("SKILL.md", "skill.json")
RELEASE_DIRS = ("references",)


def banner(text):
    print("=" * 64)
    print(text)
    print("=" * 64)


_verified = False


def run_verify():
    """先过一遍 scripts/verify.py；FAIL 非零即中止发布。同进程内只跑一次（缓存结果）。"""
    global _verified
    if _verified:
        return True
    banner("第 1 步 / 校验（scripts/verify.py）")
    proc = subprocess.run([sys.executable, str(VERIFY)], cwd=str(ROOT))
    if proc.returncode != 0:
        print("\n[FAIL] 校验未通过，请先修复 FAIL 项再发布。")
        return False
    _verified = True
    print("[OK] 校验通过，机械项放行。")
    return True


def version():
    return json.loads(SKILL_JSON.read_text(encoding="utf-8"))["version"]


def release_items():
    """返回发布物绝对路径列表：顶层文件 + references/ 下全部文件。"""
    items = [ROOT / f for f in RELEASE_FILES]
    for d in RELEASE_DIRS:
        items.extend(sorted((ROOT / d).glob("*")))
    return [p for p in items if p.is_file()]


def cmd_package(dest):
    if not run_verify():
        return 1
    banner("第 2 步 / 打包 zip")
    out_dir = Path(dest).resolve() if dest else DEFAULT_DIST
    out_dir.mkdir(parents=True, exist_ok=True)
    zip_path = out_dir / f"{SKILL_NAME}-{version()}.zip"
    try:
        with zipfile.ZipFile(zip_path, "w", zipfile.ZIP_DEFLATED) as zf:
            for p in release_items():
                arc = f"{SKILL_NAME}/{p.relative_to(ROOT).as_posix()}"
                zf.write(p, arc)
                print("  + %s" % arc)
    except OSError as e:
        print("[FAIL] 写 zip 失败：%s" % e)
        return 1
    print("\n[OK] 发布包已生成：%s" % zip_path)
    print("     解压后得到 %s/ 目录，即为可加载的技能目录（本仓库已提供一键安装：`python scripts/release.py install`）。" % SKILL_NAME)
    return 0


def cmd_install(dest):
    if not run_verify():
        return 1
    banner("第 2 步 / 安装到本机 CodeBuddy 用户技能目录")
    target = Path(dest).resolve() if dest else DEFAULT_INSTALL
    if target == target.parent or not target.name:
        print("[FAIL] install 目标必须是一个具体技能目录，不能是文件系统根目录。")
        return 1
    target.parent.mkdir(parents=True, exist_ok=True)
    staging = target.parent / (".%s.staging" % target.name)
    if staging.exists():
        print("[FAIL] 临时安装目录已存在，请先人工检查后再重试：%s" % staging)
        return 1

    backup = None
    try:
        staging.mkdir()
        for p in release_items():
            rel = staging / p.relative_to(ROOT)
            rel.parent.mkdir(parents=True, exist_ok=True)
            shutil.copy2(p, rel)
        if target.exists():
            stamp = datetime.now().strftime("%Y%m%d-%H%M%S")
            backup = target.parent / (".%s.backup-%s" % (target.name, stamp))
            target.rename(backup)
            print("  [备份] %s" % backup)
        staging.rename(target)
    except OSError as e:
        if staging.exists():
            shutil.rmtree(staging)
        if backup is not None and backup.exists() and not target.exists():
            backup.rename(target)
        print("[FAIL] 安装失败，已尝试恢复原目录：%s" % e)
        return 1

    for p in release_items():
        print("  + %s" % (target / p.relative_to(ROOT)).relative_to(target.parent).as_posix())
    print("\n[OK] 已安装：%s" % target)
    if backup is not None:
        print("     原安装内容已保留为：%s" % backup)
    print("     重启 CodeBuddy（或重载技能索引）后，即可用名称触发本技能。")
    return 0


def main():
    parser = argparse.ArgumentParser(description="agent-acceptance 一键发布工具")
    parser.add_argument("cmd", nargs="?", default="all", choices=["check", "package", "install", "all"],
                        help="子命令：check/package/install/all（默认 all）")
    parser.add_argument("--dest", default=None, help="package 的输出目录或 install 的目标技能目录")
    args = parser.parse_args()

    if args.cmd == "check":
        return 0 if run_verify() else 1
    if args.cmd == "package":
        return cmd_package(args.dest)
    if args.cmd == "install":
        return cmd_install(args.dest)
    # all：check -> package -> install
    if not run_verify():
        return 1
    if cmd_package(args.dest) != 0:
        return 1
    return cmd_install(args.dest)


if __name__ == "__main__":
    sys.exit(main())
