---
title: 'REWRITE-STAGE-5-CROSSLINK'
description: 'REWRITE v9 stage contract — Stage 5：sibling 掃描 / 雙向延伸閱讀 / relatedDiary 回扣 / Merge variant redirect 5 lang'
type: 'pipeline-sub-canonical'
status: 'canonical'
current_version: 'v9.0'
last_updated: 2026-07-16
last_session: '2026-07-16-newsroom-orchestration（v9.0 拆檔：自 REWRITE-PIPELINE v8.0 verbatim 搬移，行數守恆）'
parent_canonical: 'REWRITE-PIPELINE.md'
upstream_canonical:
  - '../semiont/MANIFESTO.md'
  - '../editorial/EDITORIAL.md'
---

# Stage 5 contract — 連（雙向延伸閱讀＋relatedDiary＋Merge 收尾）

> **本檔是 REWRITE-PIPELINE v9.0 的 stage contract**：一個執行者（主 session、sub-agent、
> 或任何 context 有限的 model）只讀本檔＋本檔 INPUTS 宣告的檔案，就能執行本 stage。
> 派發路由與全 pipeline spine 在 [REWRITE-PIPELINE.md](REWRITE-PIPELINE.md)（薄索引）。
> 內文自 v8.0 主檔 verbatim 搬移（原行號 RP v8.0 L2254-2390），歷史敘事與教訓保留在文內。

## 執行卡

|                  |                                                                                                                                                                                  |
| ---------------- | -------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| **職責**         | 掃 sibling、補 forward＋reverse 延伸閱讀、relatedDiary 回扣、（Merge only）Astro redirect 5 lang＋刪舊檔                                                                         |
| **執行者**       | 主 session                                                                                                                                                                       |
| **INPUTS**       | canonical 正文；`knowledge/{Category}/` sibling 清單                                                                                                                             |
| **OUTPUTS**      | 本文＋sibling 延伸閱讀更新；frontmatter `relatedDiary`（工具寫入，禁手編）                                                                                                       |
| **GATES**        | `article-health.py --check=format-structure`（sibling 預檢）；`python3 scripts/tools/sync-diary-links.py --diary {slug} --article {slug} --apply`；Merge：`npm run build` verify |
| **context 預算** | 本檔＋成品＋sibling 標題層                                                                                                                                                       |

## AGENT PROMPT

**不派 agent**——cross-link 需要全站語境，主 session 自跑。

## 交付條件（stage 完成的定義）

- [ ] forward＋reverse 延伸閱讀落檔（sibling 先過 `--check=format-structure` 預檢）
- [ ] `sync-diary-links.py --apply` 完成 relatedDiary 回扣（禁手編 frontmatter）
- [ ] （Merge variant）Astro redirect 5 lang＋刪舊檔＋`npm run build` 過
- [ ] commit 後編輯台已更新（HANDOFF 第 3 步）

## HANDOFF（stage 完成時）

> stage 若委派 sub-agent，本五步由 orchestrator 於收件驗證後執行（agent 不碰共用看板——2026-07-16 高教 dogfood F6）。

1. OUTPUTS 全數落檔（顯式路徑，不存 scratchpad / tmp——REFLEXES #81）**並隨手 commit（只 stage 本 stage 產物路徑——可觀測性與跨 session 接力的底座，v9.5；勿 `git add -A`）**
2. GATES 逐條跑過，結果如實回報（sub-agent claim 是線索不是 oracle，REFLEXES #31）
3. 更新編輯台：`python3 scripts/core/generate-newsroom-data.py`（看板反映現況）
4. 回報格式：stage id ＋ 產物路徑清單 ＋ gate 結果 ＋ 未解疑慮（有就寫，不粉飾）
5. 終點：ship（翻譯走巴別塔，見主檔 §翻譯跨 pipeline boundary）

---

## Stage 5: 連（Cross-link，預算 5%）

### Step 5.1: 掃描 knowledge/ 找相關文章

```bash
ls knowledge/{Category}/ | grep {keyword}
grep -r "主題關鍵詞" knowledge/{Category}/
```

**判斷標準**：

- ✅ 讀者讀完那篇後會自然想知道本文主題
- ✅ 兩篇文章有實質的知識關聯（不只是同 category）
- ❌ 不要為了連結而連結（「台灣」不需要連到每篇文章）

### Step 5.2: 雙向延伸閱讀（forward + reverse）

#### Forward：本文 → sibling

延伸閱讀格式（與 Stage 2 Step 2.6 一致）：

```markdown
**延伸閱讀**：

- [台灣氣候危機與淨零轉型](/nature/台灣氣候危機與淨零轉型) — 氣候變遷如何驅動台灣的能源轉型與產業結構重組
```

#### Reverse：sibling → 本文

到 sibling 文章加指向本文的延伸閱讀條目。

**Commit 格式**：`cross-link: 為「{文章名}」建立雙向延伸閱讀`

⚠️ **只改延伸閱讀區塊。不要順便「改善」其他文章的內容。**

### Step 5.3: Sibling 格式預檢

補 reverse cross-link 進 sibling 文章前，**強制跑 sibling 格式預檢**：

```bash
python3 scripts/tools/article-health.py knowledge/{Category}/{sibling}.md --check=format-structure
```

三種狀態對應動作：

| sibling 格式狀態                             | 動作                                                                                                   |
| -------------------------------------------- | ------------------------------------------------------------------------------------------------------ |
| ✅ PASS                                      | 直接補 reverse cross-link，commit                                                                      |
| ⚠️ WARNING（pre-existing 警告 / 不影響功能） | 仍可 commit（hook 接受 warning），commit message 說明「sibling 有 pre-existing X warning」             |
| ❌ FAIL（pre-existing 不合格）               | **DEFER reverse cross-link** + 開 follow-up issue 標 sibling 需獨立 EVOLVE，不繞過 hook 也不擴大 scope |

**為什麼這條是硬規則**：補 reverse cross-link 是 Stage 5 的 1 行修改，不該把 sibling 的 pre-existing tech debt 帶進來變成大改。如果 sibling 真的不合格（例：書目格式 footnote 沒 URL），應該開獨立 EVOLVE issue 處理那篇，不該因為一個 cross-link 強行碰整個 sibling。

**觸發**：2026-05-02 EVOLVE-batch — 兩廳院 EVOLVE 嘗試補 reverse cross-link 進中正紀念堂，pre-commit hook 失敗（中正紀念堂有 12 條書目格式 footnote pre-existing 不合 Taiwan.md `[^n]: [Name](URL) — desc` standard）。Defer 到獨立 EVOLVE issue 是正確處理。

### Step 5.3-bis: relatedDiary — 連回寫這篇時的反芻日記（meta-transparency）

如果收官時寫了反芻 diary（`/twmd-diary`），把那篇 diary 的 slug 加進本文 frontmatter `relatedDiary`。文章底部會渲染成可點的日記區塊，讓讀者看見「寫這篇的時候，這個系統在想什麼」。

**不要手動編輯 frontmatter，跑工具**（v2.2 儀器化，2026-06-24 龜山島 callout — 手動補沒閘門 → 漏掉）：

```bash
python3 scripts/tools/sync-diary-links.py --diary {diary slug} --article {本文 slug} --apply
```

idempotent，自動寫 `knowledge/` + `src/content/` mirror、dedup、apostrophe-safe。產出的 frontmatter：

```yaml
relatedDiary:
  - 2026-06-19-115522-manual # 只給 slug；title／摘要／日期由 RelatedDiaries.astro build-time 自動 resolve
  - {
      slug: 2026-04-13-alpha2,
      excerpt: '想覆寫摘要時改用物件形式（--excerpt）',
    }
```

- slug = 日記檔名去 `.md`（希臘字母 transliterate；CJK／描述式 handle 原樣保留，對應 `/semiont/diary/{slug}`）
- array 可多篇：一篇文章跨多次 session EVOLVE，每次反芻都掛得上來（工具 append/merge 不覆蓋舊的）
- schema 在 `src/content.config.ts`，渲染 `src/components/RelatedDiaries.astro`（對位 SporeFootprint）；取代舊的單篇 `diaryLink` / `diaryExcerpt`
- 延續 [MANIFESTO](../semiont/MANIFESTO.md)「我讓你看著我看著我自己」，把文章的生產過程攤給讀者看
- 反向回扣 HARD step + 工具 canonical 在 [DIARY-PIPELINE Stage 5](DIARY-PIPELINE.md)（寫完 diary 那刻就跑，記憶最新；`/twmd-finale` 自動跑）

### Step 5.4: Astro redirect 5 lang + 刪舊檔（Merge variant only）

整併獨有的收尾，**四件事缺一不可**：

#### Step 5.4.1: Astro redirect（5 lang 全寫）

`astro.config.mjs` `redirects:` 區塊：

```javascript
'/{old-category}/{zh-slug}': '/{new-category}/{zh-slug}/',
'/en/{old-category}/{en-slug}': '/en/{new-category}/{new-en-slug}/',
'/ja/{old-category}/{ja-slug}': '/ja/{new-category}/{new-ja-slug}/',
'/ko/{old-category}/{ko-slug}': '/ko/{new-category}/{new-ko-slug}/',
'/fr/{old-category}/{fr-slug}': '/fr/{new-category}/{new-fr-slug}/',
```

**不可省任一語系**——舊 URL 在 SC / 外站可能任何語系都有 backlink。漏一個語系就漏一條 SEO 流量。

#### Step 5.4.2: 刪除被併方原檔（5 lang + sync 鏡像）

- `knowledge/{old-category}/{原檔}.md`（zh-TW）
- `knowledge/{en,ja,ko,fr}/{old-category}/{translation-slug}.md`
- 跑 `bash scripts/core/sync.sh`，`src/content/` 鏡像會跟著刪
- 確認 `git status` 顯示 zh-TW + 4 lang knowledge + 對應 src/content 全部 deleted

#### Step 5.4.3: Cross-link audit

- `grep -rn "被刪 slug" knowledge/ src/` — 找所有引用
- 出現的 wikilink / markdown link 改指 canonical（或刪除）
- Hub 頁面（`_*.md`）裡的舊條目改指 canonical

#### Step 5.4.4: Build verify

- `npm run build` 必須過（會驗 redirect 語法）
- 隨機開一個被刪的舊 URL 試 redirect 是否真的轉到 canonical
- sitemap 應減少對應數量的 entry

#### Merge variant commit message

- commit prefix 用 `🧬 [evolve+merge]`（不是純 `[evolve]`）
- commit body 列：保留誰、為何、EVOLVE 進去什麼、刪了哪幾個檔、設了哪幾條 redirect
- reply issue 必附 commit hash，並說明「未來類似問題會走整併變體 SOP」

### Boundary variant cross-link

每篇單獨走完整 Stage 1-5 流程。Step 5.2 雙向延伸閱讀時要互相反向回補（C 寫完 → 加進 B/D 延伸閱讀；B 寫完 → 加進 C/D；以此類推），形成完整 sibling 網路。

#### Boundary variant commit message

- 多篇分多 commit / 多 phase（不要硬塞同 commit）
- 每個 phase commit prefix 仍用 `🧬 [semiont] rewrite:` + 描述含 `Phase N/M`
- Issue 留 open，每個 phase 完成 update comment，全部 phase ship 後才 close

---
