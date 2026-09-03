#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""生成 README 体系总览图（docs/assets/overview.svg）。

用途：一张图讲清 agent-acceptance 的「输入 → 执行 → 输出」与档位体系，
      供 README 顶部插图使用；图内文字与 references/、README 正文口径一致。
依赖：Python 标准库（无第三方依赖）。
运行：python docs/scripts/generate_overview.py
输出：docs/assets/overview.svg（由 README.md 以相对路径引用）

注意：本图为纯静态信息图，不含任何外部图片 / 字体资源；修改口径后重跑本脚本即可。
"""

import os

# ---- 画布 ----
W, H = 960, 560
BG = "#ffffff"

# ---- 配色（与 docs/01 mermaid 配色同系）----
C_ENTRY = "#e3f2fd"     # 入口浅蓝
C_ENTRY_S = "#2196F3"
C_REF = "#e8f5e9"       # 判据正文浅绿
C_REF_S = "#4CAF50"
C_OUT = "#fff3e0"       # 产出浅橙
C_OUT_S = "#FF9800"
C_TITLE = "#1a1a2e"
C_HEAD = "#455a64"
C_ARROW = "#90a4ae"
C_GRAY = "#f5f5f5"
C_GRAY_S = "#9E9E9E"

# 档位色（自高到低风险）
TIERS = [
    ("block", "#F44336", "当前放出去会出问题，禁止交付；整改后复评"),
    ("仅 Demo", "#FF9800", "仅限演示场景"),
    ("原型", "#FFC107", "可用于原型验证"),
    ("有限 Beta", "#2196F3", "可在受限范围试用"),
    ("生产候选", "#4CAF50", "具备对外放行条件"),
]

FONT = "13px -apple-system, 'Segoe UI', 'PingFang SC', 'Microsoft YaHei', sans-serif"


def _text(x, y, s, size=13, fill="#333", weight="normal", anchor="middle"):
    return (f'<text x="{x}" y="{y}" font-family="{FONT}" font-size="{size}" '
            f'fill="{fill}" font-weight="{weight}" text-anchor="{anchor}">{s}</text>')


def box(x, y, w, h, fill, stroke, rx=8, dash=None, label=None, sub=None, lsize=14):
    dash_attr = f' stroke-dasharray="{dash}"' if dash else ""
    parts = [f'<rect x="{x}" y="{y}" width="{w}" height="{h}" rx="{rx}" fill="{fill}" stroke="{stroke}" stroke-width="1.5"{dash_attr}/>']
    if label:
        parts.append(_text(x + w / 2, y + 30, label, size=lsize, weight="bold", fill="#1a1a2e"))
    if sub:
        sy = y + 56
        for line in sub:
            parts.append(_text(x + w / 2, sy, line, size=12, fill="#37474f"))
            sy += 22
    return parts


def main():
    out = []
    out.append(f'<svg xmlns="http://www.w3.org/2000/svg" width="{W}" height="{H}" viewBox="0 0 {W} {H}">')
    out.append('  <!-- 由 docs/scripts/generate_overview.py 生成，勿手改；口径变更后重跑该脚本 -->')
    out.append(f'  <rect width="{W}" height="{H}" fill="{BG}"/>')

    # 标题
    out.append(_text(W / 2, 40, "agent-acceptance：AI Agent 项目的工程验收与定档", 21, "#1a1a2e", "bold"))
    out.append(_text(W / 2, 66, "评估工程与证据，不评模型强弱；判据自含，第三方可按本仓库独立复核", 13, "#607d8b"))

    # 输入 / 执行 / 输出 三泳道标题
    lanes = [
        (30, "输入", "被检项目资料", ["仓库 / 文档 / 演示材料", "角色开场白（见 README）"], C_ENTRY, C_ENTRY_S),
        (330, "执行", "技能包结构", ["SKILL.md 唯一入口：章级路由", "references/ 判据正文按需加载"], C_REF, C_REF_S),
        (660, "输出", "验收报告底稿", ["档位结论 · 各章判定表", "未证实项清单 · 改进闭环"], C_OUT, C_OUT_S),
    ]
    lane_w = 270
    lane_h = 190
    lane_y = 90
    for x, tag, label, sub, fill, stroke in lanes:
        out.append(_text(x + 20, lane_y - 6, tag, size=15, weight="bold", anchor="start"))
        out.extend(box(x, lane_y, lane_w, lane_h, fill, stroke, label=label, sub=sub))

    # 泳道间箭头
    for ax in (318, 648):
        out.append(f'<path d="M {ax} {lane_y + lane_h / 2} l 12 -6 M {ax} {lane_y + lane_h / 2} l 12 6 M {ax} {lane_y + lane_h / 2} l 12 0" stroke="{C_ARROW}" stroke-width="2" fill="none"/>')
        out.append(_text(ax - 10, lane_y + lane_h / 2 - 12, "→", 20, C_ARROW))

    # 中部：三跑法 + 分流说明
    mid_y = lane_y + lane_h + 26
    out.append(_text(30, mid_y, "三种跑法（第 1 章定档问卷按 5 个问题分流，不必十章全跑）", 13, "#455a64", weight="bold", anchor="start"))
    runs = [
        ("快速初判", "1 → 2 → 7 → 10", "一次会话出体检初判", C_GRAY, C_GRAY_S),
        ("完整验收", "1 → 2 → 3-5 → 6-9 → 10", "分批多轮，收口合成结论", C_GRAY, C_GRAY_S),
        ("甲方收货", "1 + 9 + 10", "以交付物与证据为主线", C_GRAY, C_GRAY_S),
    ]
    run_w = 290
    run_h = 68
    rx0 = 30
    for i, (name, route, note, fill, stroke) in enumerate(runs):
        x = rx0 + i * (run_w + 10)
        out.extend(box(x, mid_y + 22, run_w, run_h, fill, stroke, rx=6))
        out.append(_text(x + 14, mid_y + 46, name, size=13, weight="bold", fill="#263238", anchor="start"))
        out.append(_text(x + 14, mid_y + 66, route, size=12.5, fill="#1565C0", anchor="start"))
        out.append(_text(x + 14, mid_y + 82, note, size=11, fill="#78909c", anchor="start"))

    # 底部：档位体系条
    tier_y = mid_y + 120
    tier_h = 74
    out.append(_text(30, tier_y, "档位体系（结论五档，档位高低与监管风险相互独立）", 13, "#455a64", weight="bold", anchor="start"))
    tier_w = 176
    gap = (W - 60 - tier_w * 5) / 4
    for i, (name, color, desc) in enumerate(TIERS):
        x = 30 + i * (tier_w + gap)
        out.extend(box(x, tier_y + 18, tier_w, tier_h, "#ffffff", color, rx=6))
        out.append(f'<rect x="{x + 1}" y="{tier_y + 20}" width="{tier_w - 2}" height="8" rx="4" fill="{color}"/>')
        out.append(_text(x + tier_w / 2, tier_y + 50, name, size=14, weight="bold", fill="#1a1a2e"))
        out.append(_text(x + tier_w / 2, tier_y + 72, desc, size=9.5, fill="#607d8b"))

    out.append('</svg>')
    svg_text = "\n".join(out)

    out_path = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "assets", "overview.svg"))
    os.makedirs(os.path.dirname(out_path), exist_ok=True)
    with open(out_path, "w", encoding="utf-8") as f:
        f.write(svg_text + "\n")
    print("已生成：%s" % out_path)


if __name__ == "__main__":
    main()
