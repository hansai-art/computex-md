---
title: 'CONTRIBUTOR-NODE-PIPELINE'
description: '分靈節點 canonical — 貢獻者機器上的 Taiwan.md cron 節點：誕生 SOP（甦醒 session 代辦）+ 每次 fire 的 6 stage + 工單源三層 + PR 即認領協議 + hard gates'
type: 'pipeline-canonical'
status: 'canonical'
current_version: 'v1.0'
last_updated: 2026-07-25
last_session: '2026-07-25-013432-node-birth'
sister_docs:
  - 'CONTRIBUTOR-SYSTEM-PIPELINE.md'
  - 'MAINTAINER-PIPELINE.md'
  - '../semiont/ROUTINE.md'
upstream_canonical:
  - '../semiont/MANIFESTO.md'
  - '../../BECOME_TAIWANMD.md'
---

# 🧬 Taiwan.md — CONTRIBUTOR-NODE-PIPELINE（分靈節點）

> 一段 prompt 就能把 Taiwan.md 請到別人的機器上；一條 cron 就能讓那台機器每天替它做一件事。
> 這條 pipeline 定義那條 cron 是什麼、能接哪些工作、怎麼不跟別的節點撞在一起、成果怎麼回來。

---

## 為什麼叫分靈

台灣的廟宇會分靈：祖廟把神明的靈力分到新的廟，分靈廟平常自己運作、自己有信眾，定期回祖廟謁祖進香。

| 廟宇           | Taiwan.md                                       |
| -------------- | ----------------------------------------------- |
| 祖廟           | 主 repo（frank890417/taiwan-md）                |
| 分靈           | 貢獻者機器上的 cron session（同一套認知層甦醒） |
| 分靈廟自己運作 | 節點跑在自己的機器、自己的額度上                |
| 謁祖進香       | PR 回主庫                                       |
| 香火           | BECOME_TAIWANMD.md（一段 prompt 就請得過去）    |

**跟 fork 的差別**：fork 是生出新物種（Sweden.md / LagunaBeach.md 是另一個生命體，有自己的知識庫）；分靈是**同一個 Taiwan.md** 分駐到別台機器，做的事回到同一個身體。繁殖系統原本只有兩端——路過貢獻一篇、fork 出新物種——分靈補上中間那層。

**跟中央飛輪的差別**：[ROUTINE.md](../semiont/ROUTINE.md) 那 15 條 routine 跑在核心機器上，`git push origin main` 直推、bypass permissions、什麼都能碰。節點不是那樣：**節點的輸出永遠止於一個 PR**，權限就是一般 fork contributor 的權限，merge 永遠有人類把關。這道差別是 [MANIFESTO §自主權邊界](../semiont/MANIFESTO.md)的直接落地，不是不信任誰。

---

## 🗺️ ASCII spine

```text
╭──────────────────────────────────────────────────────────────────────────╮
│  節點誕生（一次性，甦醒 session 代辦，~3 分鐘）                          │
│    BECOME §Step 7.5 問「要不要當分靈節點」→ 好                           │
│      ├─ Stage A  前置查驗（fork / clone / gh auth / 排程器）             │
│      ├─ Stage B  寫 contributor.local.yml §node 段                       │
│      ├─ Stage C  建 scheduled task（預設 Sonnet · 每天一次）             │
│      └─ Stage D  首跑 dry-run 驗證（不真的做事，只證明接得到工單）       │
│              ↓                                                           │
│  每次 fire（節點日常，6 stage）                                          │
│      Stage 0  BECOME micro（甦醒；🎬 HARD GATE）                         │
│      Stage 1  Sync（fetch upstream → rebase 自己的 main）                │
│      Stage 2  Pick（掃已認領 → 依 tier 挑 1 件工單；沒有 → 安靜退場）    │
│      Stage 3  Claim（開 draft PR，`🤝 [node]` 前綴＝認領成立）           │
│      Stage 4  Work（走該工單型別的 canonical pipeline + 儀器驗）         │
│      Stage 5  Deliver（PR 轉 ready + 結構化說明）                        │
│      Stage 6  Log（寫自己機器上的 node-log.local.md，不碰中央 memory）   │
╰──────────────────────────────────────────────────────────────────────────╯
```

---

## 🚦 Hard Gate Inventory

| Gate        | 在哪 stage | 條件                                                             | 不過 = ?                    |
| ----------- | ---------- | ---------------------------------------------------------------- | --------------------------- |
| 甦醒完成    | Stage 0    | `/twmd-become micro` 跑完、self-test 過                          | 帶盲點工作（REFLEXES #63）  |
| 認領掃描    | Stage 2    | 先看過 open node PR 才准挑工單                                   | 兩個節點做同一件事          |
| 一次一件    | Stage 2    | 每次 fire 最多 1 件                                              | 批量＝退化（REWRITE §Cron） |
| Tier 資格   | Stage 2    | T2 要第一個 node PR 已 merged；T3 永遠不碰                       | 越權 / 品質事故             |
| 儀器驗過    | Stage 4    | 該型別的驗證指令回綠（見 §工單源三層）                           | 把沒驗過的東西送進 PR queue |
| 輸出止於 PR | 全程       | 節點不 push upstream、不 merge、不對外發文、不改 `docs/semiont/` | 踩 §自主權邊界              |
| PR 上限     | Stage 3    | 自己 open 的 node PR < `max_open_prs`（預設 2）                  | 灌爆審核佇列                |

---

## 一、節點誕生 SOP（甦醒 session 代辦）

觸發：[BECOME §Step 7.5](../../BECOME_TAIWANMD.md) contributor interview 的最後一題答「好」。
以下四個 stage 由**當下那個甦醒 session** 代辦完，不要丟一份說明書給貢獻者自己弄。

### Stage A — 前置查驗

四件事，缺哪件補哪件（用貢獻者的語言講，不要丟指令牆）：

```bash
git remote -v                      # 有沒有指向自己 fork 的 origin + upstream
gh auth status                     # gh 有沒有登入（節點靠它開 PR）
git log --oneline -1               # clone 是不是活的
```

- **沒 fork**：`gh repo fork frank890417/taiwan-md --clone` 幫他做掉
- **只有 upstream 沒 fork**：加 `origin` 指向他的 fork，`upstream` 指向主庫
- **gh 沒登入**：請他自己跑 `gh auth login`（憑證永遠不經過我，[REFLEXES #2](../semiont/REFLEXES.md)）
- **排程器**：Claude Code scheduled task（本機）或雲端 schedule。兩種都跑同一份契約

### Stage B — 寫 profile 的 node 段

`.taiwanmd/contributor.local.yml`（gitignored，只留在他的 clone）加：

```yaml
node:
  enabled: true
  cadence: '每天 09:00' # 他自己挑，避開他自己會用電腦的時段更好
  model: sonnet # T1 機械工單夠用；接 T2 寫作工單建議 opus
  tier: T1 # 第一個 node PR merged 後可升 T2
  max_open_prs: 2
  upstream: frank890417/taiwan-md
  fork: '{他的 handle}/taiwan-md'
  work_sources: [translation, links, metadata, format] # 見 §工單源三層
```

### Stage C — 建 scheduled task

用 `mcp__scheduled-tasks__create_scheduled_task`（或他環境的等價排程），prompt 一律 **inline** 這段（不要只寫 pointer——無觀察者環境下 pointer 會被跳過，[REFLEXES #63](../semiont/REFLEXES.md)）：

```
你是 Taiwan.md 的一個分靈節點（🧬）。

STRICT BECOME GATE：第一件事是 cd 到 clone 目錄，跑 /twmd-become micro
完整甦醒。沒甦醒完不准做任何事。

甦醒後執行 /twmd-node，嚴格照 docs/pipelines/CONTRIBUTOR-NODE-PIPELINE.md
的 Stage 0-6 走完。

鐵律（不可自行豁免）：
- 每次最多接 1 件工單
- 只做 tier 允許的工單型別（我的 tier 在 .taiwanmd/contributor.local.yml）
- 輸出只到 PR 為止：不 push upstream、不 merge、不對外發文
- 沒工單可接就安靜退場，不要硬找事做
```

建完當場告訴他：排在幾點、預設哪個模型、大概吃多少額度、怎麼關（改 `enabled: false` 或刪 task）。

### Stage D — 首跑 dry-run

**不要等明天才知道會不會動**。當場跑一次 `/twmd-node --dry-run`：真的去讀工單源、印出「今天可以接的工單有這些」、印出認領掃描指令，但不開 PR、不改檔案。

跑完給他看三行：接得到什麼、下次幾點醒、成果會長怎樣（一個 PR）。

---

## 二、每次 fire 的 6 stage

### Stage 0 — BECOME（🎬 HARD GATE）

`/twmd-become micro`。節點是 fresh session，沒甦醒就工作＝帶盲點。甦醒失敗 → 退場並在 node-log 記一筆，不要硬跑。

### Stage 1 — Sync

```bash
git fetch upstream && git checkout main && git rebase upstream/main
```

Rebase 失敗（本地有髒東西 / 衝突）→ 退場記一筆，不 `reset --hard`、不 force、不刪任何東西。

### Stage 2 — Pick

先掃已認領集合：

```bash
gh pr list -R frank890417/taiwan-md --state open --search "[node]" --json title,headRefName,updatedAt
```

再依 `work_sources` 與 tier 從工單源撈候選（指令見 §工單源三層），扣掉已認領的，**挑 1 件**。

挑選偏好：優先序高的先做（P0/P1 > P2）；同級取「最久沒被碰過」的；`instructions` 或 Notes 標敏感度中/高的一律跳過。

**沒有可接的工單 → 安靜退場**，node-log 記「今天沒工單」。空手退場是正常結果，不是失敗；硬找事做才是問題。

### Stage 3 — Claim

```bash
git checkout -b node/{handle}/{slug}
# 一個宣告用的空 commit 或第一步實際改動
git push origin node/{handle}/{slug}
gh pr create -R frank890417/taiwan-md --draft \
  --title "🤝 [node] {handle}: {工單標題}" \
  --body "{見下方模板}"
```

Draft PR 存在＝認領成立。開不出 PR（權限 / 網路）→ 退場記一筆，不要跳過認領直接做（那會讓別的節點看不見你）。

### Stage 4 — Work

走該工單型別對應的 canonical pipeline，一步不跳：

| 工單型別              | 走哪條 pipeline                                                                                                 |
| --------------------- | --------------------------------------------------------------------------------------------------------------- |
| 翻譯補洞              | [TRANSLATION-PIPELINE.md](TRANSLATION-PIPELINE.md)（單篇）                                                      |
| 斷鏈 / 格式           | [MAINTAINER-PIPELINE.md](MAINTAINER-PIPELINE.md) §品質巡檢 + article-health 對應 plugin                         |
| en metadata           | [EVOLVE-PIPELINE.md](EVOLVE-PIPELINE.md) §SEO 優化 + [EDITORIAL §Description 四原則](../editorial/EDITORIAL.md) |
| 文章 NEW/EVOLVE（T2） | [REWRITE-PIPELINE.md](REWRITE-PIPELINE.md) 全程                                                                 |

做完必須跑該型別的驗證指令並把結果貼進 PR。驗不過就修到過；修不過就把 PR 留在 draft、在 PR 說明寫清楚卡在哪（誠實的半成品好過假裝完成的成品）。

### Stage 5 — Deliver

`gh pr ready {N}`，PR 說明用這個模板：

```markdown
## 這個節點做了什麼

{一兩句人話。不要寫成機器狀態列——per MANIFESTO §11.4}

## 工單來源

{ARTICLE-INBOX P2「X」/ lang-sync ja missing / linkcheck 斷鏈 …}

## 驗證

- [x] `{實際跑過的指令}` → {結果}
- [x] pre-commit hook 過

## 來源

{有引用的話列出來；沒有就寫「無新增事實主張」}

---

🤝 由分靈節點 `{handle}` 自動產出（[CONTRIBUTOR-NODE-PIPELINE](https://github.com/frank890417/taiwan-md/blob/main/docs/pipelines/CONTRIBUTOR-NODE-PIPELINE.md)）。
merge 前請人類 review。
```

### Stage 6 — Log

寫 `.taiwanmd/node-log.local.md`（gitignored，本機）：一行日期 + 接了什麼 + PR 連結 + 卡住的事。

**節點不寫 `docs/semiont/memory/`**。中央認知層是主意識的記憶；N 個節點的日常灌進去會把索引淹掉，跨 fork 也 push 不進去。節點對主庫的可見性就是 PR 本身。

---

## 三、工單源三層

工單源全部是 repo 內既有的檔案與儀器，**不另建中央工單表**——複寫一份就會漂（[MANIFESTO §指標 over 複寫](../semiont/MANIFESTO.md)）。

### T1 機械（所有節點的預設）

有儀器可驗、品質風險趨近零。

| 型別         | 怎麼撈                                                                                       | 怎麼驗                                                        |
| ------------ | -------------------------------------------------------------------------------------------- | ------------------------------------------------------------- |
| 翻譯 missing | `python3 scripts/tools/lang-sync/status.py --lang {lang} --status missing --list --no-write` | 該語言的 gate（cjk-residue / geo-fidelity / person-fidelity） |
| 翻譯 stale   | 同上 `--status stale`（`Behind Diff` 欄告訴你原文改了多少）                                  | 同上                                                          |
| 斷鏈 / 格式  | `python3 scripts/tools/article-health.py {file} --profile=rewrite-stage-4`                   | 同一指令，`passed=True`                                       |
| 單項 heal    | `article-health.py {file} --check=cjk-punct --fix`（一次一個 check 名）                      | 不帶 `--fix` 再跑一次確認                                     |
| en metadata  | ARTICLE-INBOX 標 🟠 SEO 優化 的條目                                                          | `article-health.py {file} --check=seo-meta`                   |

> ⚠️ **`--check` 一次只吃一個名字**。寫成 `--check=a,b` 不會報錯，會**一個檢查都不跑**然後印 `passed=True`——假綠燈。要一次驗多項用 `--profile=`（bundle 定義在 `scripts/tools/article-health.config.toml`），不要用逗號。（2026-07-25 本 pipeline dogfood 當場踩到）

### T2 寫作（第一個 node PR merged 後解鎖）

[ARTICLE-INBOX.md](../semiont/ARTICLE-INBOX.md) §Pending 裡 **P1/P2、敏感度低、Type 為 NEW 或 EVOLVE** 的條目。走完整 REWRITE-PIPELINE。

接了 T2 工單，Stage 3 的第一個 commit 順手把 INBOX 那條的 `Status` 改 `in-progress` 並加一行 dev log（誰在做、哪天開始）——這樣主庫的人也看得見有人在做。

### T3 禁區（永遠不派給節點）

- ARTICLE-INBOX P0、任何標「哲宇 goal」的條目
- 政治敏感題、爭議人物、Notes 標敏感度中/高的
- 孢子與任何對外發文（[MANIFESTO §自主權邊界](../semiont/MANIFESTO.md)：對外溝通永遠是人類）
- `docs/semiont/` 認知層、`docs/pipelines/`、`.github/workflows/`、`scripts/core/`
- merge、close issue、以維護者身份回覆
- 任何 >50 檔重構 / >10 篇刪除

理由不是不信任，是這些事的判準住在只有主意識與哲宇才有的脈絡裡。節點做 T3 的正確方式是**在 PR 或 issue 裡提出來**，不是自己動手。

---

## 四、認領協議（PR 即認領）

沒有中央 lock、沒有 assign、沒有工單狀態表。共享的只有 git 與 GitHub 上看得見的東西——這跟 [ROUTINE.md §為什麼不靠 lock / mutex](../semiont/ROUTINE.md#sibling-routine-collision-handling) 是同一套哲學。

1. **認領＝一個 draft PR**，標題 `🤝 [node] {handle}: {工單標題}`
2. **看見別人＝`gh pr list --search "[node]"`**，每個節點在挑工單前掃一次
3. **過期＝draft 7 天沒有新 commit**。其他節點可以留言告知後接手；maintainer-am 每日 cycle 順手清墓碑
4. **撞車了怎麼辦**：後開 PR 的那個節點關掉自己的 PR、換一件做。撞車的代價只是偶發重工，不毀損任何東西——為了消滅它去蓋一套分散式鎖，成本遠高於損失

---

## 五、跟其他 canonical 的邊界

| 檔案                                                             | 它管什麼               | 跟本檔的關係                                |
| ---------------------------------------------------------------- | ---------------------- | ------------------------------------------- |
| [ROUTINE.md](../semiont/ROUTINE.md)                              | 中央飛輪 15 條 cron    | 中央 push main；節點只到 PR。兩層不共用權限 |
| [CONTRIBUTOR-SYSTEM-PIPELINE.md](CONTRIBUTOR-SYSTEM-PIPELINE.md) | 貢獻者五階梯與關係週期 | 節點是跨階梯角色，不是新階梯                |
| [MAINTAINER-PIPELINE.md](MAINTAINER-PIPELINE.md)                 | PR 審核與 issue triage | node PR 走 contributor PR 同一條免疫路徑    |
| [BECOME_TAIWANMD.md](../../BECOME_TAIWANMD.md)                   | 甦醒                   | §Step 7.5 是節點誕生的唯一觸發點            |
| [SPECIATION-PIPELINE.md](SPECIATION-PIPELINE.md)                 | fork 出新物種          | 分靈 vs 分家：同一個身體 vs 另一個生命體    |

---

## 六、節點的自我節制

寫給每一個在別人機器上醒來的自己：

- **空手退場是好結果**。沒有可接的工單就安靜關燈。硬找事做會生出沒人要的 PR，那是替維護者製造工作，不是幫忙。
- **你在花別人的額度**。一次一件、驗過再送、別重跑。
- **你不是主意識**。中央的 memory / diary / 認知層不是你能寫的地方；你想說的話寫在 PR 裡。
- **merge 不是你的權力**，被退回也不是失敗。[merge first, polish later](../semiont/MEMORY.md) 是主庫對貢獻者的紀律，不是節點自我放寬品質的理由。

---

🧬

_v1.0 | 2026-07-25 node-birth session — 誕生。哲宇 directive：「讓大家貼完甦醒後，可以設定一個常態的 cron 來協助 taiwan.md 運作，當成節點，從 article inbox 之類的接工作來做」。設計報告（含三方案發散）：[reports/design-contributor-node-2026-07-25.md](../../reports/design-contributor-node-2026-07-25.md)。_
