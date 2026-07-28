---
title: 'REMOTE-GPU-PIPELINE'
description: 'Taiwan.md babel × GPU 軍團整合 — 硬體層委派給 fleet（muse-bot/fleet），Taiwan.md 只留翻譯邏輯 + 整合性閘門。雲地混合 SOP'
type: 'pipeline-canonical'
status: 'canonical'
current_version: 'v2.0'
last_updated: 2026-06-14
last_session: '2026-06-14-000047-manual'
born_from: '2026-06-13 5090 diary 翻譯 session；v2.0 哲宇 callout「local 硬體要用抽象層」→ 委派 fleet'
sister_docs:
  - 'docs/pipelines/SQUEEZE-MODELS-MAX-PIPELINE.md'
  - 'docs/pipelines/BENCH-PIPELINE.md'
related:
  - '~/Projects/muse-bot/fleet/README.md（GPU 軍團指揮系統 — 硬體抽象層 canonical）'
audience: 'claude-session / maintainer'
---

# REMOTE-GPU-PIPELINE — Taiwan.md babel × GPU 軍團

> **一句話**：batch 翻譯（article babel / diary / 未來 embedding）下放地端 sovereignty-safe GPU——**硬體層是 GPU 軍團（`~/Projects/muse-bot/fleet/`）的事，Taiwan.md 只留翻譯邏輯 + 整合性閘門**。雲端 Claude 是 0→1 的腦，軍團是高頻寬的肌肉（零邊際成本、不出境）。
>
> **v2.0 重構（2026-06-14）**：v1.0 在 Taiwan.md 內自建了一條平行硬體層（SSH tunnel + compute-nodes registry + node selection），跟 fleet 重複。哲宇 callout「local 硬體要用抽象層」→ 退役自建層，委派 fleet。Taiwan.md 端只剩一支 thin adapter（`fleet-endpoint.sh`）+ 翻譯工具 + 整合性閘門。

---

## 分層（誰負責什麼）

| 層                     | 擁有者                                                | 職責                                                                                                                                                                                                                   |
| ---------------------- | ----------------------------------------------------- | ---------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| **硬體 / 軍團層**      | `~/Projects/muse-bot/fleet/`（Muse + Taiwan.md 共用） | node registry（`registry.json` = SSOT，live probe）· commander 路由（`select_machine`：非離隊 → 夠用最小 VRAM → 主權→Gemma4）· Ollama-over-Tailscale 工作通道 · Windows SOP · 一鍵接入。**canonical：fleet/README.md** |
| **Taiwan.md babel 層** | 本 repo                                               | 翻譯邏輯（diary-translate.py 的 diary-specific prompt + 雙語慣例 + 🧬/footer 保留）· **整合性閘門**（截斷/refusal/footer-drop/length）· cascade 編排 · reconcile                                                       |

**鐵律**：Taiwan.md 不碰 node selection / SSH / tunnel / serve 管理 / sovereignty model 路由——那些問 fleet。新增 / 移除機器、修連線、調 VRAM 並行 = `fleetctl` 的事，不在本 repo。

---

## 儀器清單（Taiwan.md 端）

| 儀器                                                | 職責                                                                                                                                                                                                                  |
| --------------------------------------------------- | --------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| `scripts/tools/lang-sync/fleet-endpoint.sh`         | **thin adapter**：問 fleet 要一個 sovereignty-safe Ollama endpoint（呼叫 `fleetlib.select_machine` + readiness guard：model 真的 pulled）→ export `OLLAMA_HOST`/`OLLAMA_MODEL`。無 fleet（fork）→ exit 3，caller skip |
| `diary-translate.py` / `diary-translate-cascade.sh` | diary 翻譯（endpoint env 可覆寫）+ inline 整合性閘門                                                                                                                                                                  |
| `diary-translation-audit.py`                        | **整合性閘門**（截斷/refusal-stub/footer-drop/length/fence/signature）。CRITICAL vs WARNING + JSON                                                                                                                    |
| `backends/ollama.py`                                | article babel 的 Ollama backend（`OLLAMA_HOST`/`OLLAMA_MODEL` env 指向 fleet endpoint）                                                                                                                               |

---

## SOP（3 stage）

### Stage 1 — 問 fleet 要 endpoint

```bash
eval "$(bash scripts/tools/lang-sync/fleet-endpoint.sh --export)" || { echo "no fleet GPU — skip"; exit 0; }
# → export OLLAMA_API_URL / OLLAMA_HOST / OLLAMA_MODEL（fleet 挑好的節點 + 主權安全 model，直連 Tailscale 無 tunnel）
```

fleet 自己決定哪台（4090/3090/...；5090 借機 2026-06-16 歸還，commander 自動避開離隊機）。Taiwan.md 不需要知道是哪台。fleet 全離線 / 無 ready 節點 → adapter exit 3 → **skip 不是 fail，下 cycle 重試**（cloud free tier 對 sovereignty 內容會 refuse/截斷，不當 fallback）。

### Stage 2 — 翻譯（整合性閘門必經路徑）⭐

```bash
bash scripts/tools/lang-sync/diary-translate-cascade.sh --tier ollama --langs en,ja,ko,es,fr
```

**本地 LLM 會靜默截斷**：長日記被 gemma4 early-stop 砍成 2KB，**仍 > 1024 bytes → size 閘門標記「已完成」**。眼測抽樣必漏。所以整合性比對**排進必經路徑、不靠警覺**（flywheel diary：「把比對排進必經路徑而非依賴警覺」）：

- **inline**：`diary-translate.py` 落盤前過 `diary_integrity()`（截斷則升溫重試 ×3，全失敗不落盤留空）；skip-guard 整合性化（既存截斷檔自動重譯）。
- 整合性訊號（CRITICAL）：`truncation`（source 收乾淨但譯文中途斷）/ `footer-dropped`（`_..._` 反芻 metadata 掉光）/ `length-low` / `refusal-stub` / `fence-odd`。**byte-size 一律不算閘門**。

### Stage 3 — 收斂（HARD GATE）+ commit

```bash
python3 scripts/tools/lang-sync/diary-translation-audit.py --langs en,ja,ko,es,fr   # CRITICAL == 0 才算完
# reconcile：critical/missing > 0 → 重跑 cascade（skip-guard 自動補壞的）→ 再 audit
git add docs/semiont/diary/{en,ja,ko,es,fr} && git commit && git push   # main-direct
```

---

## Hard Gate Inventory

| Gate            | 位置                                                                | 規則                                                                              |
| --------------- | ------------------------------------------------------------------- | --------------------------------------------------------------------------------- |
| 主權 model      | fleet `select_machine` `sovereignty_safe` + adapter readiness guard | Taiwan content 只准 Gemma4 家族（fleet 路由保證；adapter 再驗 model 真的 pulled） |
| 整合性 inline   | `diary-translate.py diary_integrity()`                              | 截斷/refusal/footer-drop/length-low → 重試;全失敗不落盤                           |
| 整合性 post-hoc | `diary-translation-audit.py`                                        | CRITICAL > 0 → 不算收斂,回 Stage 3 reconcile                                      |
| byte-size       | ~~size>=1024~~                                                      | **退役為閘門** — 攔不住截斷,只當「有沒有東西」訊號                                |

---

## Routine 整合

`twmd-babel-nightly`（00:30 每天）§Stage D：article babel 後 `fleet-endpoint.sh` 接軍團 → diary cascade → 整合性 audit 收斂 0 critical。新日記不再累積未翻。GPU 全離線 → skip 下 cycle 重試。spec：[ROUTINE.md §TWMD babel](../semiont/ROUTINE.md) + [twmd-babel skill §Stage D](../../.claude/skills/twmd-babel/SKILL.md)。

---

## 跨檔案職責分工

- **本檔**：Taiwan.md babel 怎麼用軍團 + 整合性閘門 + 收斂。
- **`~/Projects/muse-bot/fleet/README.md`**：硬體抽象層 canonical（registry / commander / 接入 / Windows SOP）。**改機器、修連線、調並行去這裡，不在本 repo。**
- [SQUEEZE-MODELS-MAX-PIPELINE.md](./SQUEEZE-MODELS-MAX-PIPELINE.md)：cloud 4-tier cascade（軍團是其 local-LLM tier 的地端化）。
- [BENCH-PIPELINE.md](./BENCH-PIPELINE.md)：Sovereignty-Bench-TW，model 主權分級來源（fleet `sovereignty_safe` 欄的依據）。

---

_v2.0 | 2026-06-14 | 哲宇 callout「local 硬體要用抽象層」→ 退役 Taiwan.md 自建的平行硬體層（remote-ollama.sh + compute-nodes registry），委派 GPU 軍團（muse-bot/fleet）。Taiwan.md 端收斂成 fleet-endpoint.sh thin adapter + 翻譯邏輯 + 整合性閘門。核心教訓：要下放硬體前先問「這個抽象層是不是已經存在」——build-on > build-parallel。_
_v1.0 | 2026-06-13 | 5090 diary session 誕生（自建 SSH tunnel + registry，v2.0 已退役）。_
