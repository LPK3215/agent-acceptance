#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""生成 README 顶部徽章条（docs/assets/badges.svg）。

用途：为 README 提供版本 / 许可证 / 文档计数 / 更新时间等元数据徽章。
依赖：Python 标准库（无第三方依赖），须在仓库根目录的 docs/scripts/ 下运行。
运行：python docs/scripts/generate_badges.py
输出：docs/assets/badges.svg（由 README.md 以相对路径引用）

注意：
- 故意不用 shields.io 外链徽章：verify.py 的 R3 规则会对 http(s) 外链产生 WARN，
  且项目质量声明是「仅余官方一手来源外链提示项」，本地 SVG 徽章零外部依赖。
- 修改徽章数值时，同步更新下方常量来源文件：version / updated 取 skill.json，
  引用计数 = references/*.md 文件数（含 00 全局地图与附录A）。
"""

import os

# ---- 徽章数据（改动时须与来源文件保持一致）----
BADGES = [
    # (label, value, value_color, 来源)
    ("version", "1.0.0", "#1976d2", "skill.json version（与 SKILL.md frontmatter 双写同步）"),
    ("license", "MIT", "#97ca00", "LICENSE"),
    ("references", "12", "#7957d5", "references/*.md：00 全局地图 + 01-10 十章 + 附录A"),
    ("updated", "2026-09-03", "#9e9e9e", "skill.json updated"),
    ("spec", "Agent Skills", "#4caf50", "SKILL.md frontmatter spec（agentskills.io）"),
]

# ---- 徽章几何 ----
FONT = "11px -apple-system, 'Segoe UI', Helvetica, Arial, sans-serif"
HEIGHT = 20
RADIUS = 3
GAP = 6                # 徽章间距
LABEL_PAD = 5          # label 文字左右留白
VALUE_PAD = 6          # value 文字左右留白
LABEL_BG = "#555"
TEXT_FG = "#fff"


def est_w(text):
    """估算文本宽度（ASCII 为主，每字符约 6px）。"""
    return len(text) * 6.0 + 2


def badge_svg(label, value, color, x):
    label_w = est_w(label)
    value_w = est_w(value)
    w = int(label_w + value_w + LABEL_PAD + VALUE_PAD)
    parts = [
        '<g>',
        f'  <rect x="{x:.1f}" y="0" width="{w:.1f}" height="{HEIGHT}" rx="{RADIUS}" fill="{LABEL_BG}"/>',
        f'  <rect x="{x + label_w + LABEL_PAD:.1f}" y="0" width="{value_w + VALUE_PAD:.1f}" height="{HEIGHT}" rx="{RADIUS}" fill="{color}"/>',
        f'  <text x="{x + LABEL_PAD + 2:.1f}" y="13.5" font-family="{FONT}" font-size="11" fill="{TEXT_FG}">{label}</text>',
        f'  <text x="{x + label_w + LABEL_PAD + VALUE_PAD / 2:.1f}" y="13.5" font-family="{FONT}" font-size="11" fill="{TEXT_FG}">{value}</text>',
        '</g>',
    ]
    return parts, w


def main():
    total_w = 0
    body = []
    for label, value, color, _src in BADGES:
        parts, w = badge_svg(label, value, color, total_w)
        body.extend(parts)
        total_w += w + GAP
    total_w -= GAP  # 去掉最末间距

    svg = [
        f'<svg xmlns="http://www.w3.org/2000/svg" width="{total_w:.0f}" height="{HEIGHT}" viewBox="0 0 {total_w:.0f} {HEIGHT}">',
        '<!-- 由 docs/scripts/generate_badges.py 生成，勿手改；改数值后重跑该脚本 -->',
        *body,
        '</svg>',
    ]

    out = os.path.join(os.path.dirname(__file__), "..", "assets", "badges.svg")
    out = os.path.abspath(out)
    os.makedirs(os.path.dirname(out), exist_ok=True)
    with open(out, "w", encoding="utf-8") as f:
        f.write("\n".join(svg) + "\n")
    print("已生成：%s" % out)
    print("徽章数据：%s" % ", ".join("%s=%s" % (b[0], b[1]) for b in BADGES))


if __name__ == "__main__":
    main()
