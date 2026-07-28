---
name: twmd-news-lens
description: |
  Weekly news-lens 三源交叉 + news-driven spore candidate propose via EVOLVE-PIPELINE v2.0.
  Routine fires Sunday 01:00. Manual /twmd-news-lens or "跑 news lens" or "新聞透鏡掃描".
  TRIGGER when: routine twmd-news-lens-weekly fires / user says "跑 news lens" /
  "新聞透鏡掃描" / "三源交叉找熱點".
allowed-tools:
  - Bash
  - Read
  - Edit
  - Write
  - Grep
  - WebFetch
  - WebSearch
---

# 🧬 Taiwan.md — News Lens (weekly) v3.0

## 🚨 STRICT BECOME GATE — 第一動作不可省略

**Before anything else**：跑 `/twmd-become full` 完整走 [BECOME_TAIWANMD.md](../../../BECOME_TAIWANMD.md) Step 0-9。Full mode self-test 14 題全過才能進 Stage 1。

```
✅ BECOME ack: mode=full / 8 organ 最低=<即時 consciousness-snapshot.sh> / Q5/Q6/Q13/Q14=PASS
```

## Pipeline

嚴格完整讀取並執行 [`docs/pipelines/EVOLVE-PIPELINE.md`](../../../docs/pipelines/EVOLVE-PIPELINE.md) v2.0 + §news-lens-spore-output（v2.5 升級）。

## 三源交叉（DNA #4）

| 源             | 意義              | 信號                                                           |
| -------------- | ----------------- | -------------------------------------------------------------- |
| **GA4**        | 誰來了 + 站內行為 | page_view / scroll / session_duration / conversion             |
| **SC**         | 誰想來但沒來      | query position > 10 + impressions > 100 = 高 demand 低 ranking |
| **Cloudflare** | 誰在邊緣讀我      | AI crawler hit / cached request / 404 rate spike               |

至少 2 源確認的 signal 才升 candidate。

## News-lens spore output (v2.5)

propose 5-7 news-driven candidates append [SPORE-INBOX.md](../../../docs/factory/SPORE-INBOX.md)：

- Default `P1`（高於 spore-pick-daily 的 P2）
- Source-Mode `REACTIVE` / `EXISTING-ARTICLE`
- Limit ≤ 7/week
- 每 entry 標 `Requested: YYYY-MM-DD by twmd-news-lens-weekly routine (week YYYY-WW)`
- 高敏感 entry 標 `敏感度: 高`（spore-publish v3.0 §高敏感 REACTIVE defer rule 會 catch）

Daily spore-pick-daily 看到 news-lens P1 count ≥ 3 自動 throttle（補 0-3 條依 news-lens 已寫數量）。

## 收官

`/twmd-finale` chain → memory file 必含：BECOME ACK + 三源 signal 列表 + N news-driven candidates appended + Handoff 三態 + Beat 5 反芻。

完整 SOP：[EVOLVE-PIPELINE.md](../../../docs/pipelines/EVOLVE-PIPELINE.md)

ARGUMENTS: (none — pipeline 自己讀三源 + INBOX state)
