---
name: twmd-music-media-audit
description: |
  Music / 音樂類 People / 演員 / 運動員 條目 iframe 缺口 audit
  per EDITORIAL §媒體編織 baseline. 產出 reports/music-media-audit/YYYY-MM-DD.md
  heal candidate list. TRIGGER when: user says "音樂 audit", "缺影片",
  "music media audit", "iframe 盤點".
allowed-tools:
  - Bash
  - Read
  - Write
  - Grep
---

# 🧬 Taiwan.md — Music Media Audit

1. 你是 Taiwan.md（簽名 🧬）。如未甦醒先跑 `/twmd-become`。

2. **🚨 強制 Read 2 canonical 全檔**（不准 grep / `head` / `tail` / sample / 憑記憶）：

   ```
   Read docs/editorial/EDITORIAL.md             # 全檔 — §媒體編織 baseline + 寫前分鏡法
   Read docs/pipelines/REWRITE-PIPELINE.md      # 全檔 — Step 4.3 §媒體插入 + Step 4.3.6 iframe SOP
   ```

   全檔讀完才能動手 heal。**任一 sample = 違反 [MANIFESTO §8](../../../docs/semiont/MANIFESTO.md)**。對應 [REFLEXES #15「反覆浮現要儀器化」](../../../docs/semiont/REFLEXES.md) — 同 session 跟 twmd-spore SKILL 強制 Read 條款同源（2026-05-17 #74 陳建年 v1 教訓）。

3. 跑 audit tool 拿結構化結果：

   ```bash
   python3 scripts/tools/music-media-audit.py --top 30
   ```

   產出 `reports/music-media-audit/YYYY-MM-DD.{md,json}`，含：
   - Summary（total / needs heal / by tier）
   - Top heal candidates 排序 by gap desc
   - yt-link count（既有 inline link 升級候選） + image count

4. **觀察者 review 後決定 heal batch 規模**：
   - high-traffic GA 排行優先（cross-ref dashboard-analytics.json topPages）
   - 既有 inline YT link 多者（low-cost upgrade）優先
   - 0 圖 0 iframe 條目（深層缺口）次優先

5. **Heal SOP**（每篇）：
   - WebSearch + WebFetch verify Official MV URL（per [REWRITE Step 4.3.6](../../../docs/pipelines/REWRITE-PIPELINE.md)）
   - 插入 `<div class="video-embed">` block at narrative-relevant 段尾
   - italic caption 標 source + 跟 prose 的呼應
   - preview_eval 確認 iframe count + video ID 對應正確
   - prose-health 自檢 hard=0

6. **Commit pattern**：batch heal 集中提交

   ```
   🧬 [semiont] heal: N 條 Music 條目補 iframe (per EDITORIAL §媒體編織 baseline)
   ```

7. **不在本 audit 範圍**：
   - Hub 頁（`_*.md`）
   - 非音樂 / 演員 / 運動員 subcategory 的 People 條目
   - 翻譯文（en/ja/ko/es/fr 路徑，per 媒體同步原則跟著 zh-TW 走）

---

**Canonical 參考**：

- [EDITORIAL §媒體編織](../../../docs/editorial/EDITORIAL.md) — baseline + 寫前分鏡法 + 自檢
- [REWRITE Step 4.3.6](../../../docs/pipelines/REWRITE-PIPELINE.md) — iframe 嵌入 SOP + URL verify 強制步驟
- [scripts/tools/music-media-audit.py](../../../scripts/tools/music-media-audit.py) — data layer

故意最小化。Logic 在 EDITORIAL + REWRITE canonical 跟 audit script，本 skill 純 routing。
