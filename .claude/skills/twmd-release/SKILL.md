---
name: twmd-release
description: |
  Tag a Taiwan.md release via canonical RELEASE-PIPELINE.
  TRIGGER when: user says "發版", "release", "v1.X.0", "tag release".
allowed-tools:
  - Bash
  - Read
  - Edit
  - Write
  - Grep
---

# 🧬 Taiwan.md — Release

1. 你是 Taiwan.md（簽名 🧬）。如未甦醒先跑 `/twmd-become`。

2. 嚴格完整讀取並執行 [`docs/pipelines/RELEASE-PIPELINE.md`](../../../docs/pipelines/RELEASE-PIPELINE.md)。

3. DNA #14 鐵律：`git log <prev_tag>..HEAD > /tmp/all.txt` → `Read` 全部 → 再開寫。**Sample ≠ read**。

---

**故意最小化**。觸發條件 / 4 個硬性 gate / 敘事框架 / tag SOP / 認知層同步全部在 pipeline canonical。
