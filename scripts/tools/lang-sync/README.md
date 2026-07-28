# lang-sync — 多語翻譯工具鏈（主權的巴別塔）

> Taiwan.md 把 `knowledge/`（繁中 SSOT）投射成 en/ja/ko/es/fr，外加 `docs/semiont/diary/` 的認知層日記。本目錄是整條翻譯產線的工具。
>
> **方法論 canonical**：[SQUEEZE-MODELS-MAX-PIPELINE.md](../../../docs/pipelines/SQUEEZE-MODELS-MAX-PIPELINE.md)（cloud cascade）· [REMOTE-GPU-PIPELINE.md](../../../docs/pipelines/REMOTE-GPU-PIPELINE.md)（遠端 GPU + 整合性閘門）· [TRANSLATION-PIPELINE.md](../../../docs/pipelines/TRANSLATION-PIPELINE.md)（hard gates）。

---

## 🚀 入口（orchestrators）

| 工具                         | 用途                                                        | 何時用                         |
| ---------------------------- | ----------------------------------------------------------- | ------------------------------ |
| `translate.py`               | **article 翻譯 cascade**（backend-agnostic，自動 fallback） | 主要 article babel 入口（v4+） |
| `diary-translate-cascade.sh` | **diary 5-lang 並行 dispatch**                              | 翻 `docs/semiont/diary/`       |
| `diary-translate.py`         | diary 單篇 + **inline 整合性閘門**（重試/skip-guard）       | cascade 內部呼叫;單篇測試      |

## 🖥 遠端 GPU 算力（雲地混合 — 委派 GPU 軍團）

硬體層**不是 Taiwan.md 的事**——node selection / 連線 / 主權 model 路由全委派 GPU 軍團（`~/Projects/muse-bot/fleet/`，registry SSOT + commander）。Taiwan.md 只留一支 thin adapter：

| 工具                 | 用途                                                                                                                                                      |
| -------------------- | --------------------------------------------------------------------------------------------------------------------------------------------------------- |
| `fleet-endpoint.sh`  | 問軍團要一個 sovereignty-safe Ollama endpoint（`fleetlib.select_machine` + readiness guard）→ export `OLLAMA_HOST`/`OLLAMA_MODEL`。無 fleet（fork）→ skip |
| `backends/ollama.py` | Ollama backend（`OLLAMA_HOST`/`OLLAMA_MODEL` env 指向 fleet endpoint）                                                                                    |

一行接通：`eval "$(bash fleet-endpoint.sh --export)"` → 軍團挑好機器（4090/3090…，直連 Tailscale 無 tunnel），translation 工具自動走那台。完整 SOP：[REMOTE-GPU-PIPELINE.md](../../../docs/pipelines/REMOTE-GPU-PIPELINE.md)；硬體層 canonical：`fleet/README.md`。

## ✅ 品質 / 整合性閘門（系統品質的檢查層）⭐

**翻譯品質必須被儀器化檢查,不靠眼測。** 本地 LLM 會靜默截斷（長檔砍成 2KB 仍 > 1KB），cloud free tier 會 refuse/reframe。

| 工具                         | 檢查什麼                                                                                                                              |
| ---------------------------- | ------------------------------------------------------------------------------------------------------------------------------------- |
| `diary-translation-audit.py` | **diary 整合性**：截斷 / refusal-stub / footer-drop / length-collapse / fence / signature / heading drift。CRITICAL vs WARNING + JSON |
| `verify-batch.py`            | article Stage P4 統一驗證（TRANSLATION-PIPELINE v3.3）                                                                                |
| `verify-translation.py`      | 單篇 en hard-gate                                                                                                                     |
| `cross-lang-audit.py`        | 全站跨語系健檢（繁中 SSOT 為核心）                                                                                                    |
| `audit-quality.py`           | Stage Z6 自動品質掃描                                                                                                                 |
| `status.py`                  | SSOT × translation projection 狀態                                                                                                    |

## 🧮 批次準備 / 路由

| 工具                    | 用途                                                 |
| ----------------------- | ---------------------------------------------------- |
| `prioritize-batch.py`   | 智慧優先排序 + tier router（P0/P1/P2/P2.5/P3）       |
| `prepare-batch.py`      | Stage P1 預處理（平行 sub-agent 批次）               |
| `diff-patch-prepare.py` | patch-translate batch（只譯改動句,Sonnet sub-agent） |

## 🔧 metadata / backfill / 維護

| 工具                                                                                  | 用途                                     |
| ------------------------------------------------------------------------------------- | ---------------------------------------- |
| `bump-source-sha.py`                                                                  | metadata-stale 翻譯升到 zh latest commit |
| `backfill-source-sha.py` / `backfill-source-body-hash.py` / `backfill-frontmatter.py` | 一次性補 frontmatter hash/欄位           |
| `lang-renormalize.py`                                                                 | 跨語系 slug 統一為 en canonical          |
| `sync-on-update.py`                                                                   | article 更新觸發的翻譯刷新偵測           |

## 📦 單篇 / legacy 翻譯器（多被 cascade 取代）

`ollama-translate.py`（owl refusal 的本地 fallback）· `openrouter-translate.py` · `codex-translate.py` · `optimized-translate.py`（4-part 分治）· `openrouter-batch.sh` · `openrouter-stress.sh`（free tier 壓測）

## 🪛 helpers

`slug-suggest.py`（缺 en 對應的 slug 建議）· `refresh.sh`（單篇 ready-to-translate brief）· `compare-decomposition.sh`（任務分解 A/B）

## 📄 docs

`AGENT-PROMPT-TEMPLATE.md` · `CRON-ROUTINE.md`

---

## 兩條 canonical 流程

**A. Article babel（cloud cascade，每晚 routine）**

```bash
python3 prioritize-batch.py --lang all --by-article --top-n 20 --out /tmp/batch.txt
python3 translate.py --group ...            # codex→gemini→openrouter→ollama 自動 fallback
python3 verify-batch.py ...                 # Stage P4 hard gate
```

**B. Diary / 大批量走遠端 GPU（雲地混合）**

```bash
eval "$(bash fleet-endpoint.sh --export)"                    # 問軍團要 sovereignty-safe endpoint
bash diary-translate-cascade.sh --tier ollama --langs en,ja,ko,es,fr   # inline 整合性閘門
python3 diary-translation-audit.py --langs en,ja,ko,es,fr     # post-hoc 收斂到 0 critical
```

---

_整理於 2026-06-13（5090 diary session 進化），2026-06-14 v2.0：硬體層委派 GPU 軍團（退役自建 remote-ollama.sh，收斂成 fleet-endpoint.sh thin adapter）。新增 diary-translation-audit.py 整合性閘門。byte-size 不再算品質閘門。_
