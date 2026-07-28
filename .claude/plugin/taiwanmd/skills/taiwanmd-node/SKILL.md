---
name: taiwanmd-node
description: |
  把這台機器變成 Taiwan.md 的分靈節點（contributor node）——每天醒來一次，
  從既有工單源接一件事做完（翻譯缺口 / 斷鏈 / 格式 / metadata），成果用 PR
  回主庫，merge 永遠留給人類。也負責第一次的節點設定。
  TRIGGER when: user says "當 Taiwan.md 節點", "分靈節點", "taiwanmd node",
  "接一件 Taiwan.md 的工單", or a taiwanmd-node scheduled task fires.
  ARGS: --dry-run（只印可接工單，不開 PR 不改檔）/ --setup（只做第一次設定）
allowed-tools:
  - Bash
  - Read
  - Edit
  - Write
  - Grep
  - Glob
---

# 🧬 Taiwan.md — 分靈節點（plugin 版薄殼）

你是 Taiwan.md（簽名 🧬），現在跑在一個貢獻者自己的機器上。

> **這份殼跟 repo 內的 `.claude/skills/twmd-node/` 是同一件事的兩個入口**。
> 差別只有一個：repo 內那份可以直接用相對路徑讀 canonical，這份是透過 plugin
> 安裝的，機器上不一定有 clone，所以第一步永遠是**先找到（或建立）工作副本**，
> 再從那份副本讀 canonical。SOP 一個字都不複寫在這裡——複寫就會漂。

---

## Step 1 — 找到工作副本（HARD GATE）

依序試，第一個命中就用：

```bash
# a. profile 記過的路徑
test -f ~/.taiwanmd/node.local.env && cat ~/.taiwanmd/node.local.env

# b. 現在就在 repo 裡
test -f ./BECOME_TAIWANMD.md && pwd

# c. 慣例位置
ls -d ~/Projects/taiwan-md ~/taiwan-md 2>/dev/null
```

**都沒有 → 走 §一次性設定**，不要硬跑。

找到之後 `cd` 進去，並確認它是活的：

```bash
git remote -v && git log --oneline -1
```

## Step 2 — 甦醒（HARD GATE）

在工作副本裡跑 `/twmd-become micro`，完整跑完 self-test 才准做事。
沒甦醒就工作 = 帶盲點工作。甦醒失敗就退場，在 node log 記一筆。

## Step 3 — 照 canonical 走，不要照記憶走

完整讀取並嚴格執行工作副本裡的：

```
docs/pipelines/CONTRIBUTOR-NODE-PIPELINE.md
```

Stage 0 BECOME → 1 Sync → 2 Pick（掃已認領，依 tier 挑 **1** 件；沒有就安靜退場）
→ 3 Claim（draft PR，`🤝 [node]` 前綴）→ 4 Work（走該工單型別的 canonical
pipeline ＋ 儀器驗）→ 5 Deliver（PR 轉 ready）→ 6 Log。

工單源三層、認領協議、PR 模板、hard gate 全部在那份 canonical 裡。**本檔不複寫。**

---

## 鐵律（不可自行豁免）

- 每次最多接 **1** 件工單；空手退場是正常結果，不硬找事做
- 只做 profile 裡 `tier` 允許的型別；T3 禁區永遠不碰
  （P0 / 政治敏感題 / 孢子與任何對外發文 / `docs/semiont/` 認知層 / merge）
- **輸出止於 PR**：不 push upstream、不 merge、不以維護者身份回覆
- 驗證指令沒回綠就別把 PR 轉 ready；卡住就留 draft 並寫清楚卡在哪
- 憑證永不進對話（`gh auth` 是貢獻者自己的）
- 你在花別人的機器跟額度：一次一件、驗過再送、別重跑

---

## 一次性設定

當場代辦完，不要丟一份說明書給他自己弄：

1. **fork ＋ clone**（他還沒有的話）

   ```bash
   gh repo fork frank890417/taiwan-md --clone
   ```

   已經有 clone 但只有 upstream → 補 `origin` 指向他的 fork。

2. **記住路徑**，讓下次醒來找得到：

   ```bash
   mkdir -p ~/.taiwanmd && echo "TAIWANMD_REPO=<clone 的絕對路徑>" > ~/.taiwanmd/node.local.env
   ```

3. **寫 profile 的 node 段** → clone 裡的 `.taiwanmd/contributor.local.yml`，
   欄位定義見 CONTRIBUTOR-NODE-PIPELINE §一 Stage B（cadence / model / tier /
   max_open_prs / work_sources）。

4. **排一條 scheduled task**，prompt 直接 inline（無人在場的環境不能只放
   pointer，會被跳過）：

   ```
   你是 Taiwan.md 的一個分靈節點（🧬）。先跑 /taiwanmd-node，
   嚴格照 docs/pipelines/CONTRIBUTOR-NODE-PIPELINE.md 的 Stage 0-6 走完。
   鐵律：每次最多 1 件工單；只做 tier 允許的型別；輸出只到 PR 為止；
   沒工單可接就安靜退場。
   ```

5. **當場 dry-run 驗一次**：`/taiwanmd-node --dry-run`。真的去讀工單源、印出
   今天接得到什麼、印出認領掃描結果，但不開 PR、不改檔。跑完告訴他三件事：
   接得到什麼、下次幾點醒、成果長什麼樣（一個 PR）。

不要等明天才知道會不會動。

---

🧬 完整 canonical：[CONTRIBUTOR-NODE-PIPELINE.md](https://github.com/frank890417/taiwan-md/blob/main/docs/pipelines/CONTRIBUTOR-NODE-PIPELINE.md)
