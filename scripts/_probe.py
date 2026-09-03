# -*- coding: utf-8 -*-
"""二次探测：判点号引用守卫 + 地图-正文小节编号双向一致性。跑完即删。"""
import re, sys
from pathlib import Path

REF = Path(__file__).resolve().parents[1] / "references"
sys.stdout.reconfigure(encoding="utf-8")

def load(name):
    return (REF / name).read_text(encoding="utf-8")

MAP = load("00-global-map.md")
FILES = [
    ("01-项目定档与边界.md","1"),("02-本体构成.md","2"),("03-考卷与评测集.md","3"),
    ("04-判分器.md","4"),("05-指标与目标值.md","5"),("06-运行可观测.md","6"),
    ("07-安全与权限底线.md","7"),("08-生产就绪与上线.md","8"),
    ("09-交付物与证据链.md","9"),("10-验收结论与档位.md","10")]
texts = {n: load(n) for n,_ in FILES}
texts["附录A-元规则.md"] = load("附录A-元规则.md")

# 判点全集 = 表格首列 N.M.K
check_ids = set()
for t in texts.values():
    check_ids |= {m.group(1) for m in re.finditer(r"^\|\s*(\d+\.\d+\.\d+)\s*\|", t, re.M)}
print("判点全集(表格首列):", len(check_ids))

# ---- 探测1：正文引用判点号，不在全集则报；先按章号∈1..10过滤日期/arxiv ----
print("\n--- 探测1：引用到全集外的 N.M.K（章号1-10、三位段）---")
bad = []
for fname, t in texts.items():
    own = {m.group(1) for m in re.finditer(r"^\|\s*(\d+\.\d+\.\d+)\s*\|", t, re.M)}
    for ln_no, ln in enumerate(t.splitlines(), 1):
        if ln.startswith("|") or ln.startswith("#"):
            continue
        for m in re.finditer(r"(?<![\d.])(\d+)\.(\d+)\.(\d+)(?![\d.])", ln):
            a,b,c = map(int, m.groups())
            if not (1 <= a <= 10) or b < 1 or c < 1:
                continue
            cid = m.group(0)
            if cid not in check_ids and cid not in own:
                bad.append((fname[:6], cid, ln_no, ln.strip()[:70]))
for x in bad:
    print(" ", x)
print("命中:", len(bad))

# ---- 探测2：正文小节 ## N.M 是否都出现在地图 (### N.M)；反之亦然 ----
print("\n--- 探测2：小节编号双向一致性 ---")
chap_sec = {}
for fname, t in texts.items():
    m = re.match(r"(\d{2})-(.+)\.md", fname)
    if not m:
        continue
    chap = m.group(1)
    chap_sec[chap] = set(re.findall(r"^##\s*(\d+\.\d+)\b", t, re.M))
map_sec = set(re.findall(r"^#{2,4}\s*(\d+\.\d+)\b", MAP, re.M))
for chap, secs in sorted(chap_sec.items()):
    miss = secs - map_sec
    if miss:
        print(f"  正文{chap}有小节但地图缺: {sorted(miss, key=lambda s:[int(x) for x in s.split('.')])}")
print("地图小节(所有含4级):", len(map_sec))
print("地图小节(仅N.M级去重):", len({s for s in map_sec if len(s.split('.'))==2}))
