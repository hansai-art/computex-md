#!/usr/bin/env python3
"""pipeline-shell-lint.py — REWRITE v9 薄索引／stage contract 結構尺

防再增厚（reports/newsroom-orchestration-design-2026-07-16.md §四 鐵律 6）：
- 主檔（薄索引）行數 ≤ 550：超線 = 內容又長回主檔（v3.1→v4→v8 增厚循環的復發訊號）
- 每個 REWRITE-STAGE-*.md 必有「執行卡」與「HANDOFF」段：缺 = contract 骨架被拆掉
- stage 檔 frontmatter type 必為 pipeline-sub-canonical + parent_canonical 指回主檔

用法：python3 scripts/tools/pipeline-shell-lint.py   （exit 0 過 / 1 fail）
歸屬：self-evolve weekly 例行掃描候選；手動改 pipeline 後順手跑。
"""
import os
import re
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
PIPE_DIR = os.path.join(ROOT, "docs/pipelines")
MAIN = os.path.join(PIPE_DIR, "REWRITE-PIPELINE.md")
MAIN_LINE_CAP = 550

fails = []

n = sum(1 for _ in open(MAIN, encoding="utf-8"))
if n > MAIN_LINE_CAP:
    fails.append(f"主檔 {n} 行 > {MAIN_LINE_CAP}：內容長回索引了，該搬去 stage contract")

stage_files = sorted(f for f in os.listdir(PIPE_DIR) if f.startswith("REWRITE-STAGE-") and f.endswith(".md"))
if len(stage_files) < 10:
    fails.append(f"stage contract 檔只剩 {len(stage_files)} 個（預期 ≥10）")

for fn in stage_files:
    s = open(os.path.join(PIPE_DIR, fn), encoding="utf-8").read()
    if "## 執行卡" not in s:
        fails.append(f"{fn}: 缺 ## 執行卡")
    if "## HANDOFF" not in s:
        fails.append(f"{fn}: 缺 ## HANDOFF")
    if "## AGENT PROMPT" not in s:
        fails.append(f"{fn}: 缺 ## AGENT PROMPT（該階段派誰、prompt 在哪或為何不派）")
    if "## 交付條件" not in s:
        fails.append(f"{fn}: 缺 ## 交付條件（stage 完成的定義）")
    if "type: 'pipeline-sub-canonical'" not in s:
        fails.append(f"{fn}: frontmatter type 不是 pipeline-sub-canonical")
    if "parent_canonical: 'REWRITE-PIPELINE.md'" not in s:
        fails.append(f"{fn}: 缺 parent_canonical 指回主檔")
    m = re.search(r"\| \*\*INPUTS\*\* \|([^|]*)\|", s)
    if m and "REWRITE-STAGE-" in m.group(1):
        fails.append(f"{fn}: 執行卡 INPUTS 要求讀兄弟 stage 檔（違反 contract 自足鐵律）")

if fails:
    print(f"❌ pipeline-shell-lint：{len(fails)} 項")
    for f in fails:
        print(f"  - {f}")
    sys.exit(1)
print(f"✅ pipeline-shell-lint：主檔 {n} 行 ≤ {MAIN_LINE_CAP}；{len(stage_files)} 個 stage contract 骨架完整")
