---
name: twmd-babel
description: |
  Multi-language batch sync (主權的巴別塔) via canonical
  SQUEEZE-MODELS-MAX-PIPELINE — priority schema (P0/P1/P2/P2.5/P3) +
  backend cascade + 統一調度器 babel-dispatch.py。
  TRIGGER when: user says "巴別塔", "多語 batch", "多語同步",
  "跑 babel", "繼續 babel".
allowed-tools:
  - Bash
  - Read
  - Edit
  - Write
  - Grep
  - Glob
  - Agent
---

# 🧬 Taiwan.md — Babel Tower

## 🚨 STRICT BECOME GATE — 第一動作不可省略

跑 `/twmd-become write` 完整走 [BECOME_TAIWANMD.md](../../../BECOME_TAIWANMD.md) Step 0-9，Write mode self-test 全過才動工。

```
✅ BECOME ack: mode=write / 8 organ 最低=<即時 consciousness-snapshot.sh> / Q14 cross-session continuity=PASS
```

## Stage 0 — 宿主機算力自檢（第一個指令）

```bash
python3 scripts/tools/lang-sync/babel-preflight.py
```

四層算力（OpenRouter key 池／本機 ollama／fleet 節點／codex）任一缺席時 cascade 會**靜默降級**：產能掉一半而 log 看起來一切正常。飛輪 2026-07-24 遷居後 babel 在跟開發機不同的宿主機上跑，憑證與模型都是各機獨立的。

判讀：`healthy` 照跑；`degraded` 照跑但**收官必記哪層缺席**（缺席是可修的事實，不是背景雜訊）；`no-compute` 不起跑，把缺什麼寫進 handoff（憑證屬身份授權層，只有哲宇能補）。

## 兩種運作模式（2026-07-27 分流）

**批次模式**（cron nightly／單次跑到 stale=0）：讀
[SQUEEZE-MODELS-MAX-PIPELINE.md](../../../docs/pipelines/SQUEEZE-MODELS-MAX-PIPELINE.md)
整份照做。

**渦流模式**（觀察者下 /goal 持續迴圈、每小時甦醒監測）：讀
[BABEL-VORTEX-LOOP.md](../../../docs/pipelines/BABEL-VORTEX-LOOP.md)——那是渦流
SSOT：薄殼 wake prompt contract、固定 benchmark 報告面板、三重巡檢（存活≠生產）、
自動進化硬條款。哲宇說「持續」「渦流」「loop」「一小時甦醒」就是這個模式。

## Pipeline — 嚴格完整讀取後照做

[SQUEEZE-MODELS-MAX-PIPELINE.md](../../../docs/pipelines/SQUEEZE-MODELS-MAX-PIPELINE.md) 整份（priority 分流、cascade 順序、Tier 0a patch agent template、Z1-Z6 hard gate、**模型×語言適配表／入池門檻／排序原則／編組原則四節**全在那裡，本殼一律不複寫；模型名以 `translate.py DEFAULT_CASCADE_ID` 為準）。

整批行軍用統一調度器（內建三重 gate、HEAD-restore、精確路徑 commit）：

```bash
python3 scripts/tools/lang-sync/babel-dispatch.py --langs <langs> \
  $(~/Projects/muse-bot/fleet/fleetctl workers --service llm --format babel) \
  --worker "雲端=openrouter:<model>" --rounds 200 --commit-every 50
```

地端 worker 一律由 fleet 控制面核發；禁止在 skill／routine／重啟腳本寫死
localhost、Tailscale IP、模型或並行數。`fleetctl control` 的接案開關與天花板是 SSOT。

Stage D（認知層 diary babel）跟 Stage 3 同屬義務範圍，工具鏈走 [REMOTE-GPU-PIPELINE.md](../../../docs/pipelines/REMOTE-GPU-PIPELINE.md)。

## 四條 inline 行為約束（cron 無人在場時最會漂，故不外包給 pointer）

1. **義務鐵律**：推同步率到 100%（stale → 0，語言數以 registry 為準），不主動 defer / skip / partial / 守 boundary。跑到 stale=0 或 cascade exhausted 才收工；memory 不准寫「主動 defer 守預算」。
2. **整合性閘門是唯一 pass 判準**：article 走 `verify-batch.py`、diary 走 `diary-translation-audit.py`，收斂 0 critical 才算完。**byte-size 不算閘門**——長檔靜默截斷成 2KB 仍 > 1KB。
3. **同批次即時修，不等跑完才 audit**（2026-07-24 哲宇 directive）：發現系統性缺陷當場修工具＋已落地檔案，驗證過再繼續下一批。同一 bug 會在你沒看見時複製到下一批、下一個節點。
4. **禁 destructive git**（REFLEXES #35）：sub-agent／背景產線跑期間不 `git reset --hard`、不 `git checkout -- file`、不 `git add` 目錄。

---

**故意最小化**（2026-07-25 薄殼化）：priority schema / cascade / Tier 0a template / Stage D 工具鏈 / 批後 audit 清單全部住 pipeline canonical，本殼只留觸發、Stage 0 自檢、入口指令、四條 cron 行為約束。cron 排程數值住 [ROUTINE.md §排程表](../../../docs/semiont/ROUTINE.md)。
