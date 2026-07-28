# docs/reports/ → 已搬移到 reports/archive/2026-Q1/

> 2026-05-27 [reports-archival-audit](../../reports/reports-archival-audit-2026-05-27.md) Layer 1 cleanup

本 folder 是 **2026-03-31 ~ 2026-04-07 早期遺跡**（誕生期沒分流好的 report 放錯位置）。已全部 `git mv` 到 [`reports/archive/2026-Q1/`](../../reports/archive/2026-Q1/)，git history 完整保留。

未來所有 report 一律寫到 `reports/` 根目錄（per [REWRITE-PIPELINE Step 1.7](../pipelines/REWRITE-STAGE-1A-RESEARCH.md#step-17-研究報告必存-reportsresearchyyyy-mm-)）。

## 舊路徑 → 新路徑 對照表

如果你是從歷史 session memory / diary 連過來的：

| 舊位置                                             | 新位置                                                                                                                             |
| -------------------------------------------------- | ---------------------------------------------------------------------------------------------------------------------------------- |
| `docs/reports/FACT-CHECK-120.md`                   | [`reports/archive/2026-Q1/FACT-CHECK-120.md`](../../reports/archive/2026-Q1/FACT-CHECK-120.md)                                     |
| `docs/reports/GA4-ANALYSIS-2026-04-04.md`          | [`reports/archive/2026-Q1/GA4-ANALYSIS-2026-04-04.md`](../../reports/archive/2026-Q1/GA4-ANALYSIS-2026-04-04.md)                   |
| `docs/reports/HOMEPAGE-HUB-STRATEGY-2026-04-07.md` | [`reports/archive/2026-Q1/HOMEPAGE-HUB-STRATEGY-2026-04-07.md`](../../reports/archive/2026-Q1/HOMEPAGE-HUB-STRATEGY-2026-04-07.md) |
| `docs/reports/REWRITE-QUEUE-GA4.md`                | [`reports/archive/2026-Q1/REWRITE-QUEUE-GA4.md`](../../reports/archive/2026-Q1/REWRITE-QUEUE-GA4.md)                               |
| `docs/reports/SEARCH-CONSOLE-2026-04-04.md`        | [`reports/archive/2026-Q1/SEARCH-CONSOLE-2026-04-04.md`](../../reports/archive/2026-Q1/SEARCH-CONSOLE-2026-04-04.md)               |
| `docs/reports/SEO_OPTIMIZATION_SUMMARY.md`         | [`reports/archive/2026-Q1/SEO_OPTIMIZATION_SUMMARY.md`](../../reports/archive/2026-Q1/SEO_OPTIMIZATION_SUMMARY.md)                 |
| `docs/reports/TEST_REPORT.md`                      | [`reports/archive/2026-Q1/TEST_REPORT.md`](../../reports/archive/2026-Q1/TEST_REPORT.md)                                           |
| `docs/reports/research-e-estonia-analysis.md`      | [`reports/archive/2026-Q1/research-e-estonia-analysis.md`](../../reports/archive/2026-Q1/research-e-estonia-analysis.md)           |
| `docs/reports/resources-expanded.md`               | [`reports/archive/2026-Q1/resources-expanded.md`](../../reports/archive/2026-Q1/resources-expanded.md)                             |
| `docs/reports/ux-audit-2026-03-17.md`              | [`reports/archive/2026-Q1/ux-audit-2026-03-17.md`](../../reports/archive/2026-Q1/ux-audit-2026-03-17.md)                           |
| `docs/reports/research/{slug}-RESEARCH.md` × 8     | [`reports/archive/2026-Q1/research-legacy/{slug}-RESEARCH.md`](../../reports/archive/2026-Q1/research-legacy/)                     |

## 為什麼搬移

- `docs/reports/` 最後 commit 在 2026-04-07，被引用 4 次都是 4 月歷史 session memory/diary（不是 live SOP）。
- `reports/` 根目錄已成為活躍 canonical（239 個 doc 反向引用）。
- 2 個位置造成新人困惑「報告該寫哪裡」。

完整 audit + 三層歸檔策略：[`reports/reports-archival-audit-2026-05-27.md`](../../reports/reports-archival-audit-2026-05-27.md)。
