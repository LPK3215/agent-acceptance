#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""生成 README 顶部徽章条（docs/assets/badges.svg）。

用途：为 README 提供版本 / 许可证 / 文档计数 / 更新时间等元数据徽章。
依赖：Python 标准库（无第三方依赖），可从任意工作目录运行。
运行：python docs/scripts/generate_badges.py
输出：docs/assets/badges.svg（由 README.md 以相对路径引用），并同步
      project_overview/assets/badges.svg。

注意：
- 故意不用 shields.io 外链徽章：verify.py 的 R3 规则会对 http(s) 外链产生 WARN，
  且项目质量声明是「仅余官方一手来源外链提示项」，本地 SVG 徽章零外部依赖。
- 徽章数值在运行时读取：version / updated 取 skill.json，引用计数取
  references/*.md 文件数（含 00 全局地图与附录A），不得手工维护常量。

配色纪律（2026-09-04 修订）：
    与 docs/scripts/generate_overview.py、project_overview/style.css 共用
    「深空蓝 + 琥珀金」设计 token。SVG 无法引用 CSS 变量，故以字面量镜像
    style.css 浅色主题色值；改动任一侧时另一侧须同步。
"""

import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]


def badges():
    """从发布源读取徽章数据，避免版本、日期与正文数量发生漂移。"""
    meta = json.loads((ROOT / "skill.json").read_text(encoding="utf-8"))
    ref_count = len(list((ROOT / "references").glob("*.md")))
    return [
        # (label, value, value_color, 来源)
        ("version", meta["version"], "#0369a1", "skill.json version（与 SKILL.md frontmatter 双写同步）"),
        ("license", "MIT", "#047857", "LICENSE"),
        ("references", str(ref_count), "#6d28d9", "references/*.md：00 全局地图 + 01-10 十章 + 附录A + 附录B"),
        ("updated", meta["updated"], "#64748b", "skill.json updated"),
        ("spec", "Agent Skills", "#b45309", "SKILL.md frontmatter spec（agentskills.io）"),
    ]

# ---- 设计 token：镜像 style.css 的 html[data-theme="light"] ----
LABEL_BG = "#334155"     # 徽章标签底：深空蓝灰
TEXT_FG = "#ffffff"
STROKE = "rgba(15,23,42,0.08)"

# ---- 字体（font-family 里不得混入 font-size，否则字体回退为默认衬线体）----
FONT = ("-apple-system, BlinkMacSystemFont, 'Segoe UI', 'PingFang SC', "
        "'Microsoft YaHei', Helvetica, Arial, sans-serif")

# ---- 徽章几何 ----
HEIGHT = 22
RADIUS = 4
GAP = 7                  # 徽章间距
LABEL_PAD = 7            # label 文字左右留白
VALUE_PAD = 8            # value 文字左右留白
FONT_SIZE = 11

_NARROW = set("ilItf.,:;'|!j")
_WIDE = set("mwMW@%")


def est_w(text):
    """估算 11px 无衬线字体下的文本宽度。"""
    w = 0.0
    for ch in text:
        if ch in _NARROW:
            w += 3.3
        elif ch in _WIDE:
            w += 8.8
        elif ch.isupper():
            w += 7.1
        else:
            w += 6.15
    return w + 2


def _right_rounded(x0, x1, h, r):
    """只有右侧带圆角的矩形路径（避免徽章中段出现圆角缺口）。"""
    return (f'M{x0:.1f} 0 L{x1 - r:.1f} 0 a{r} {r} 0 0 1 {r} {r} '
            f'L{x1:.1f} {h - r} a{r} {r} 0 0 1 -{r} {r} L{x0:.1f} {h} Z')


def badge_svg(label, value, color, x):
    label_w = est_w(label)
    value_w = est_w(value)
    w = label_w + value_w + LABEL_PAD + VALUE_PAD
    split = x + label_w + LABEL_PAD
    baseline = HEIGHT / 2 + FONT_SIZE * 0.36
    parts = [
        '<g>',
        # 整枚徽章垫底（提供左侧圆角）
        f'  <rect x="{x:.1f}" y="0" width="{w:.1f}" height="{HEIGHT}" rx="{RADIUS}" '
        f'fill="{LABEL_BG}" stroke="{STROKE}" stroke-width="1"/>',
        # value 区盖在右侧，仅右侧圆角
        f'  <path d="{_right_rounded(split, x + w, HEIGHT, RADIUS)}" fill="{color}"/>',
        f'  <text x="{x + LABEL_PAD / 2 + 1:.1f}" y="{baseline:.1f}" font-family="{FONT}" '
        f'font-size="{FONT_SIZE}" fill="{TEXT_FG}" opacity="0.92">{label}</text>',
        f'  <text x="{split + VALUE_PAD / 2:.1f}" y="{baseline:.1f}" font-family="{FONT}" '
        f'font-size="{FONT_SIZE}" font-weight="600" fill="{TEXT_FG}">{value}</text>',
        '</g>',
    ]
    return parts, w


def main():
    total_w = 0.0
    body = []
    source_badges = badges()
    for label, value, color, _src in source_badges:
        parts, w = badge_svg(label, value, color, total_w)
        body.extend(parts)
        total_w += w + GAP
    total_w -= GAP  # 去掉最末间距

    svg = [
        f'<svg xmlns="http://www.w3.org/2000/svg" width="{total_w:.0f}" height="{HEIGHT}" '
        f'viewBox="0 0 {total_w:.0f} {HEIGHT}" role="img" '
        f'aria-label="项目元数据徽章：版本、许可证、引用文档数、更新时间、规范">',
        '<!-- 由 docs/scripts/generate_badges.py 生成，勿手改；改数值后重跑该脚本 -->',
        *body,
        '</svg>',
    ]

    content = "\n".join(svg) + "\n"
    targets = (
        ROOT / "docs" / "assets" / "badges.svg",
        ROOT / "project_overview" / "assets" / "badges.svg",
    )
    for out in targets:
        out.parent.mkdir(parents=True, exist_ok=True)
        out.write_text(content, encoding="utf-8")
        print("已生成：%s" % out)
    print("徽章数据：%s" % ", ".join("%s=%s" % (b[0], b[1]) for b in source_badges))


if __name__ == "__main__":
    main()
