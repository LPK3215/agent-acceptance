#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""生成 README 体系总览图（docs/assets/overview.svg）。

用途：一张图讲清 agent-acceptance 的「输入 → 执行 → 输出」与档位体系，
      供 README 顶部插图使用；图内文字与 references/、README 正文口径一致。
依赖：Python 标准库（无第三方依赖）。
运行：python docs/scripts/generate_overview.py
输出：docs/assets/overview.svg（由 README.md 以相对路径引用）

注意：本图为纯静态信息图，不含任何外部图片 / 字体资源；修改口径后重跑本脚本即可。

配色纪律（2026-09-04 修订）：
    本图与 project_overview/style.css 共用同一套设计 token ——「深空蓝 + 琥珀金」。
    SVG 无法引用 CSS 变量，故此处以字面量镜像 style.css 中 html[data-theme="light"]
    的主题色。改动任一侧配色时，另一侧须同步，否则两套资产会视觉脱节。
    本图固定为浅底（GitHub 默认浅色模式），故一律取浅色主题那一档色值。
"""

import os

# ---- 画布 ----
W, H = 960, 600

# ---- 字体（注意：font-family 里不得混入 font-size，否则整图字体回退为默认衬线体）----
FONT = ("-apple-system, BlinkMacSystemFont, 'Segoe UI', 'PingFang SC', "
        "'Microsoft YaHei', 'Hiragino Sans GB', sans-serif")
FONT_MONO = "ui-monospace, SFMono-Regular, Menlo, Consolas, monospace"

# ---- 设计 token：镜像 style.css 的 html[data-theme="light"] ----
C_INK = "#0f172a"        # 主文字（--text）
C_BODY = "#475569"       # 正文（--text-mid）
C_DIM = "#64748b"        # 弱化文字（--text-dim）
C_FAINT = "#94a3b8"      # 极弱文字 / 箭头

C_BLUE = "#0369a1"       # --accent-2  深空蓝（输入 / 有限 Beta）
C_AMBER = "#b45309"      # --accent    琥珀金（执行 / 原型 / 品牌条）
C_GREEN = "#047857"      # --accent-3  成功绿（输出 / 生产候选）
C_RED = "#be123c"        # --danger    block
C_ORANGE = "#c2410c"     # --warn      仅 Demo

C_SURFACE = "#ffffff"    # 卡片底
C_PAGE_A = "#fbfcfe"     # 页面渐变起
C_PAGE_B = "#eef3fa"     # 页面渐变止
C_RULE = "#e2e8f0"       # 分隔线

# 三泳道：输入(蓝) → 执行(琥珀·品牌) → 输出(绿)
LANES = [
    ("输入", "被检项目资料", ["仓库 / 文档 / 演示材料", "角色开场白（见 README）"], C_BLUE),
    ("执行", "技能包结构", ["SKILL.md 唯一入口：章级路由", "references/ 判据正文按需加载"], C_AMBER),
    ("输出", "验收报告底稿", ["档位结论 · 各章判定表", "未证实项清单 · 改进闭环"], C_GREEN),
]

# 三种跑法
RUNS = [
    ("快速初判", "1 → 2 → 7 → 10", "一次会话出体检初判"),
    ("完整验收", "1 → 2 → 3-5 → 6-9 → 10", "分批多轮，收口合成结论"),
    ("甲方收货", "1 + 9 + 10", "以交付物与证据为主线"),
]

# 档位体系（自高危到可放行；色彩取主题语义色，形成红→橙→琥珀→蓝→绿的连续谱）
TIERS = [
    ("block", C_RED, ["当前放出去会出问题", "禁止交付；整改后复评"]),
    ("仅 Demo", C_ORANGE, ["仅限演示场景"]),
    ("原型", C_AMBER, ["可用于原型验证"]),
    ("有限 Beta", C_BLUE, ["可在受限范围试用"]),
    ("生产候选", C_GREEN, ["具备对外放行条件"]),
]


def _text(x, y, s, size=12, fill=C_BODY, weight="normal", anchor="start",
          mono=False, spacing=None):
    """统一 text 输出。size 与 font-family 严格分离。"""
    fam = FONT_MONO if mono else FONT
    sp = f' letter-spacing="{spacing}"' if spacing else ""
    esc = (s.replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;"))
    return (f'<text x="{x}" y="{y}" font-family="{fam}" font-size="{size}" '
            f'fill="{fill}" font-weight="{weight}" text-anchor="{anchor}"{sp}>{esc}</text>')


def _card(x, y, w, h, rx=12, accent=None):
    """白底卡片 + 轻投影。accent 给定时额外描一条主题色左边条。"""
    parts = [f'<rect x="{x}" y="{y}" width="{w}" height="{h}" rx="{rx}" '
             f'fill="{C_SURFACE}" stroke="{C_RULE}" stroke-width="1" filter="url(#cardShadow)"/>']
    if accent:
        parts.append(f'<path d="M{x + 1} {y + rx} a{rx - 1} {rx - 1} 0 0 1 {rx - 1} -{rx - 1} '
                     f'h{w - 2 * rx + 2} a{rx - 1} {rx - 1} 0 0 1 {rx - 1} {rx - 1} '
                     f'v{h - 2 * rx + 2} l0 0 h-{w - 2} z" fill="none"/>')
        parts.append(f'<rect x="{x}" y="{y + 10}" width="3" height="{h - 20}" rx="1.5" fill="{accent}"/>')
    return parts


def main():
    out = []
    out.append(f'<svg xmlns="http://www.w3.org/2000/svg" width="{W}" height="{H}" '
               f'viewBox="0 0 {W} {H}" role="img" '
               f'aria-label="agent-acceptance 体系总览：输入、执行、输出三泳道，三种跑法与五档结论">')
    out.append('  <!-- 由 docs/scripts/generate_overview.py 生成，勿手改；口径变更后重跑该脚本 -->')

    # ---- defs：页面渐变、卡片投影、品牌渐变、箭头 marker ----
    out.append('  <defs>')
    out.append(f'    <linearGradient id="pageBg" x1="0" y1="0" x2="0.6" y2="1">'
               f'<stop offset="0%" stop-color="{C_PAGE_A}"/>'
               f'<stop offset="100%" stop-color="{C_PAGE_B}"/></linearGradient>')
    out.append(f'    <linearGradient id="brandBar" x1="0" y1="0" x2="1" y2="0">'
               f'<stop offset="0%" stop-color="{C_AMBER}"/>'
               f'<stop offset="55%" stop-color="#d97706"/>'
               f'<stop offset="100%" stop-color="{C_BLUE}"/></linearGradient>')
    out.append(f'    <linearGradient id="brandMark" x1="0" y1="0" x2="1" y2="1">'
               f'<stop offset="0%" stop-color="{C_BLUE}"/>'
               f'<stop offset="100%" stop-color="#0f172a"/></linearGradient>')
    out.append('    <filter id="cardShadow" x="-10%" y="-10%" width="120%" height="130%">')
    out.append(f'      <feDropShadow dx="0" dy="2" stdDeviation="3.5" '
               f'flood-color="{C_INK}" flood-opacity="0.06"/>')
    out.append('    </filter>')
    out.append('    <marker id="arw" viewBox="0 0 10 10" refX="8.5" refY="5" '
               'markerWidth="6" markerHeight="6" orient="auto-start-reverse">')
    out.append(f'      <path d="M 0 1 L 9 5 L 0 9 z" fill="{C_FAINT}"/>')
    out.append('    </marker>')
    out.append('  </defs>')

    # ---- 底：品牌顶条 + 页面渐变 ----
    out.append(f'  <rect width="{W}" height="{H}" fill="url(#pageBg)"/>')
    out.append(f'  <rect x="0" y="0" width="{W}" height="5" fill="url(#brandBar)"/>')

    # ---- 页眉：品牌标记 + 标题 ----
    out.append('  <g>')
    out.append('    <rect x="30" y="24" width="24" height="24" rx="7" fill="url(#brandMark)"/>')
    out.append('    <path d="M36.6 36.6 l3.1 3.1 5.7-6.2" stroke="#ffffff" stroke-width="2" '
               'fill="none" stroke-linecap="round" stroke-linejoin="round"/>')
    out.append('  </g>')
    out.append(_text(64, 42, "agent-acceptance", 21, C_INK, "bold"))
    out.append(_text(64, 63, "AI Agent 项目的工程验收与定档 · 评估工程与证据，不评模型强弱；"
                             "判据自含，第三方可按本仓库独立复核", 12, C_DIM))

    # ---- 泳道区 ----
    lane_w, lane_h, lane_y = 272, 176, 116
    for i, (tag, label, sub, accent) in enumerate(LANES):
        x = 30 + i * (lane_w + 22)
        out.append(_text(x, lane_y - 12, tag, 11, C_DIM, "bold", mono=True, spacing="0.1em"))
        out.extend(_card(x, lane_y, lane_w, lane_h, rx=13, accent=accent))
        # 泳道内标题
        out.append(_text(x + 22, lane_y + 38, label, 15, C_INK, "bold"))
        # 序号徽标
        out.append(f'<circle cx="{x + lane_w - 26}" cy="{lane_y + 31}" r="12" '
                   f'fill="{accent}" opacity="0.10"/>')
        out.append(_text(x + lane_w - 26, lane_y + 36, str(i + 1), 12, accent, "bold", anchor="middle",
                         mono=True))
        sy = lane_y + 70
        for line in sub:
            out.append(_text(x + 22, sy, line, 11.8, C_BODY))
            sy += 24
        # 泳道间箭头
        if i < len(LANES) - 1:
            ax = x + lane_w + 4
            out.append(f'<path d="M{ax} {lane_y + lane_h / 2} L{x + lane_w + 18} '
                       f'{lane_y + lane_h / 2}" stroke="{C_FAINT}" stroke-width="1.6" '
                       f'fill="none" marker-end="url(#arw)"/>')

    # ---- 跑法区 ----
    run_y = 350
    out.append(_text(30, run_y - 12, "三种跑法", 11, C_DIM, "bold", mono=True, spacing="0.1em"))
    out.append(_text(114, run_y - 12, "第 1 章定档问卷按问题分流，不必十章全跑", 11, C_FAINT))
    run_w, run_h = 292, 78
    for i, (name, route, note) in enumerate(RUNS):
        x = 30 + i * (run_w + 12)
        out.extend(_card(x, run_y, run_w, run_h, rx=11))
        out.append(_text(x + 18, run_y + 28, name, 13.2, C_INK, "bold"))
        out.append(_text(x + 18, run_y + 51, route, 12.4, C_BLUE, mono=True))
        out.append(_text(x + 18, run_y + 68, note, 11, C_FAINT))

    # ---- 档位区 ----
    tier_y = 486
    out.append(_text(30, tier_y - 12, "结论五档", 11, C_DIM, "bold", mono=True, spacing="0.1em"))
    out.append(_text(114, tier_y - 12, "档位高低与监管风险相互独立", 11, C_FAINT))
    tier_w, tier_h = 176, 88
    gap = (W - 60 - tier_w * 5) / 4
    for i, (name, color, desc) in enumerate(TIERS):
        x = 30 + i * (tier_w + gap)
        out.extend(_card(x, tier_y, tier_w, tier_h, rx=11))
        # 顶部色条（贴合卡片圆角）
        out.append(f'<path d="M{x + 1} {tier_y + 11} a10 10 0 0 1 10 -10 '
                   f'h{tier_w - 22} a10 10 0 0 1 10 10 v5 h-{tier_w - 2} z" '
                   f'fill="{color}" opacity="0.9"/>')
        out.append(_text(x + tier_w / 2, tier_y + 46, name, 14, C_INK, "bold", anchor="middle"))
        sy = tier_y + 64
        for line in desc:
            out.append(_text(x + tier_w / 2, sy, line, 9.6, C_DIM, anchor="middle"))
            sy += 13

    out.append('</svg>')

    svg_text = "\n".join(out)
    out_path = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "assets", "overview.svg"))
    os.makedirs(os.path.dirname(out_path), exist_ok=True)
    with open(out_path, "w", encoding="utf-8") as f:
        f.write(svg_text + "\n")
    print("已生成：%s" % out_path)


if __name__ == "__main__":
    main()
