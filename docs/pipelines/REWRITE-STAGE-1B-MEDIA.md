---
title: 'REWRITE-STAGE-1B-MEDIA'
description: 'REWRITE v9 stage contract — Step 1.9 全段：深度媒體掃描協議 / 圖片授權矩陣 / transcript / persona 讀者缺口稽核'
type: 'pipeline-sub-canonical'
status: 'canonical'
current_version: 'v9.1'
last_updated: 2026-07-25
last_session: '2026-07-25-外送專法（v7.8 spine 第三型「多觀點立場議題探討矛盾型」——哲宇 directive，以外送專法 dogfood 校準）'
parent_canonical: 'REWRITE-PIPELINE.md'
upstream_canonical:
  - '../semiont/MANIFESTO.md'
  - '../editorial/EDITORIAL.md'
---

# Stage 1 contract — 取材 B（媒體素材＋persona 讀者缺口，Step 1.9）

> **本檔是 REWRITE-PIPELINE v9.0 的 stage contract**：一個執行者（主 session、sub-agent、
> 或任何 context 有限的 model）只讀本檔＋本檔 INPUTS 宣告的檔案，就能執行本 stage。
> 派發路由與全 pipeline spine 在 [REWRITE-PIPELINE.md](REWRITE-PIPELINE.md)（薄索引）。
> 內文自 v8.0 主檔 verbatim 搬移（原行號 RP v8.0 L1124-1355），歷史敘事與教訓保留在文內。

## 執行卡

|                  |                                                                                                                   |
| ---------------- | ----------------------------------------------------------------------------------------------------------------- |
| **職責**         | 深掃媒體（rendered-DOM＋官方頻道）、建三表授權矩陣、抓 transcript、20 persona 對研究報告補洞                      |
| **執行者**       | 主 session（授權判斷 human）；persona 稽核 4 parallel Sonnet（契約在 [PERSONA-PIPELINE.md](PERSONA-PIPELINE.md)） |
| **INPUTS**       | research report（Stage 1A 產物）；EDITORIAL §媒體編織/§圖片的證據層級                                             |
| **OUTPUTS**      | research 檔 §媒體授權矩陣三表＋§讀者缺口稽核；`public/article-images/{cat}/` 圖檔；`{slug}-transcripts/`          |
| **GATES**        | 深掃協議必跑才可下 no-media 結論（落 §6 negative finding）；增補後重跑 `research-report-health.py`                |
| **context 預算** | 本檔＋research report；persona agent 只吃 PERSONA-PIPELINE 契約                                                   |

## AGENT PROMPT

- persona 讀者缺口稽核：4 Sonnet 契約唯一來源 [PERSONA-PIPELINE.md](PERSONA-PIPELINE.md)（mode=gap-audit）
- 媒體深掃：主 session 自跑（Chrome MCP rendered-DOM；授權判斷永遠 human）；反方視角 agent prompt 在本檔 §Step 1.4.5 做法 A（含防呆三條）

## 交付條件（stage 完成的定義）

- [ ] 深掃協議跑過（no-media 結論必附 §6 negative finding）
- [ ] research 檔末尾媒體授權矩陣三表齊
- [ ] §讀者缺口稽核 落檔（20 persona 分類＋增補）
- [ ] 增補後 `research-report-health.py` 重跑 exit 0

## HANDOFF（stage 完成時）

> stage 若委派 sub-agent，本五步由 orchestrator 於收件驗證後執行（agent 不碰共用看板——2026-07-16 高教 dogfood F6）。

1. OUTPUTS 全數落檔（顯式路徑，不存 scratchpad / tmp——REFLEXES #81）**並隨手 commit（只 stage 本 stage 產物路徑——可觀測性與跨 session 接力的底座，v9.5；勿 `git add -A`）**
2. GATES 逐條跑過，結果如實回報（sub-agent claim 是線索不是 oracle，REFLEXES #31）
3. 更新編輯台：`python3 scripts/core/generate-newsroom-data.py`（看板反映現況）
4. 回報格式：stage id ＋ 產物路徑清單 ＋ gate 結果 ＋ 未解疑慮（有就寫，不粉飾）
5. 下一棒：REWRITE-STAGE-2A-PROJECTION.md

---

### Step 1.9: 媒體素材研究 🎬

> Stage 1 結尾必跑（除非 hub / 短修正）。蒐集媒體素材 + 授權檢查 + manifest 落 research 檔末尾。

#### Step 1.9.0: 深度媒體掃描協議（HARD，v6.8）🔍🎬

> **v6.8 新增（2026-06-07 哲宇 directive「媒體完整度低標提升」）**：媒體完整度是**素材挖掘深度問題，不是素材有無問題**。複雜生活節 worked example——同一個 niche 主題，`curl` / `WebFetch` 抓圖全 404 → 一度 text-only ship；改用 Chrome MCP 驅動瀏覽器讀 rendered DOM 後，9 圖 + 3 官方影片全挖出來。**「找不到媒體」這個結論在跑完本協議之前不成立。**

**強制兩段掃描（出任何「找不到 / 不勉強塞 / text-only」結論之前必跑）**：

1. **Chrome MCP rendered-DOM 圖片掃描** — Medium / FB / 官網 / 機構新聞稿頁是 JS-render，`curl` / `WebFetch` 取不到圖片 CDN URL（miro.medium.com 等被 JS 包住）：
   - `list_connected_browsers` → `select_browser` → `tabs_context_mcp(createIfEmpty)`
   - `navigate` 到來源頁 → `javascript_tool` 跑 scroll-through 觸發 lazy-load + `[...document.querySelectorAll('figure img')].map(i=>({src:i.currentSrc||i.src, cap:figcaption}))` 取 rendered `img.src` + 圖說
   - 下載 hi-res（miro 改 `resize:fit:2000`）→ `sips` 優化 + 清 EXIF → cache `public/article-images/{cat}/` → fair use editorial commentary 標註（per Step 1.9.2 第 8 點）
2. **YouTube 官方頻道影片掃描** — `navigate` 到 `youtube.com/results?search_query={主題／人物／創辦人／機構}` → `javascript_tool` 取 `ytd-video-renderer` 的 videoId + channel → 篩**官方頻道**（藝人／廠牌／節目方／機構／政府單位，如 教育部青年發展署 / TEDxTaipei / 數位時代 / 公視）→ Step 4.3.6 iframe embed

**落檔**：掃描結果（找到的 URL 清單 + negative finding「跑過深掃仍無 X」）寫進 research report §6 媒體 manifest。**跑過深掃後真的無官方媒體 → 才可走 image-only / text-only，並在 §6 明記 negative finding**（不是省略掃描）。

**為什麼是 HARD**：text-only / media-poor ship 過去多半不是「真沒素材」，是深掃沒做（curl 失敗就放棄）。把深掃變必經 = 把媒體完整度的低標從「有沒有順手的 CC 圖」提到「有沒有挖到該有的素材」。儀器化在 `image-health`（length-scaled hard，見 §Hard Gate Inventory）+ `media-richness`（≥1 官方影片 WARN for People/Music/Nature）+ `paragraph-rhythm`（density floor 0.8）三個 plugin；但工具只擋「數量不足」，**深掃這個動作本身是 SOP HARD 步驟**。

#### Step 1.9.1: inline 外連 manifest（YouTube／影像／音檔）

**觸發條件**：任何題材敘事中提到**有公開影像／音檔／影片**的具體作品：

- 音樂人：歌名 → 官方 MV／lyric video／official audio
- 電影 / 紀錄片：片名 → 官方預告／導演頻道／串流官方頁
- 電視劇 / 綜藝：節目名 → 官方頻道／公視+／Netflix 官方
- YouTube 創作者 / Podcaster：節目名 → 官方頻道
- 演唱會 / 表演 / 舞作：場次名 → 主辦官方／售票頁／aftermovie
- 音樂節：節目名 → 官方 lineup
- 新聞事件：被引用的關鍵公開影片 → 官方 YouTube

**URL 優先序**：(1) 官方頻道（藝人／廠牌／節目方／導演）(2) 國際串流官方（Spotify / Apple Music / KKBOX）(3) 主辦／策展單位官方頁。**不接受**搜尋結果頁、UGC 翻唱、二手轉貼。

**密度建議**：每篇 3-8 inline 外連最合理。少於 3 → 讀者沒得點；多於 10 → 視覺擁擠。

**位置建議**：作品名在文章中**第一次出現**時加 link；同一作品再次出現不重複加。

**跟 footnote 的分工**：inline 外連走「邊讀邊聽／邊讀邊看」的閱讀體驗；footnote 走「來源驗證 + 補充資料」。同一首歌的官方 MV 可以同時放 footnote（給研究者）+ 文中第一次提及加 inline link（給讀者）。

**跟 Step 4.3.6 iframe embed 的分工**（2026-05-17 新增）：Music / People 條目可以**升級** inline link 到 iframe embed，提高閱讀的多重感受。判準：3-5 首代表作 → iframe（直接內嵌、視覺呼吸），其餘提及作品 → inline link。同篇可並存。詳見 [Step 4.3.6 影片 iframe 嵌入](REWRITE-STAGE-4-FORMAT.md#step-437-影片-iframe-嵌入music--people--nature-條目升級)。

**強制動作**：研究 agent 額外蒐集「文章預期會提到的所有公開作品」的官方連結，列入研究筆記獨立一節 §inline 外連 manifest。找不到官方版本 → 標 `[no official URL found]`，**Stage 2 寫作時不附 link 也不掰連結**。

#### Step 1.9.2: 圖片素材（hero + inline 圖）+ 授權矩陣

**🥇 選圖第一問：證據層級（2026-06-04 設研院 session 新增）** — 在挑授權之前先挑「這張圖讓讀者看到主角嗎」。Tier A 主體成果圖（改造後成果／作品本身／當事人在做那件事）> Tier B 脈絡圖 > Tier C generic 填位圖。**機構／設計／產品／作品／工程／事件題材，Tier A 成果圖優先；Tier A 找不到 CC 授權就走下方來源優先序第 8 點 fair use editorial commentary，不要退用 generic CC 填位圖**（授權便利不凌駕證據強度）。caption 一旦得寫「示意／非當事／非改造後」= Tier C 警訊，回頭找 Tier A。完整證據層級表 + source 技巧 canonical 在 [EDITORIAL §媒體編織 §圖片的證據層級](../editorial/EDITORIAL.md)。

**圖片用途分類**：

| 用途              | 位置                               | 數量           | 範例                                   |
| ----------------- | ---------------------------------- | -------------- | -------------------------------------- |
| **hero**          | frontmatter `image:`               | 1              | 林琪兒 EMU 1692×1691                   |
| **inline 圖**     | 文中 markdown `![]()`              | 1-2            | 林琪兒 Expedition 42 + Crew-4 training |
| **OG / 社群分享** | derived from hero（`/og-images/`） | auto           | dashboard 自動生成，不手動處理         |
| **spore poster**  | derived（`/spore-images/`）        | auto on demand | `make-spore.sh` 自動產，不手動處理     |

**理想數量 — length-scaled 媒體 band**（2026-06-04 哲宇 directive 升級，原 2026-05-09「2-3 張圖」是短文 baseline）：

媒體總量隨字數縮放，目標 **圖+影片+視覺模組 ≈ 1 媒體 / 500–800 字**（含 hero 與 tw-\* 模組），落在 **1.2–2.0 / 1k CJK** 健康帶（2026-07-12 哲宇 directive「提升上限，1.5x-2x 都是健康，新基準範圍 1.2~2」第三波上修，原 0.7–1.2）；**長文（≥ 7000 字）朝 圖+影片 ≥ 8**。短文 hero only（1 張）。舊富媒體範本（設研院 0.91 / 黃魚鴞 0.82 / 天下 0.92）在新基準下屬偏少，帶內範本：陳建年 1.48。**圖、影片、tw-\* 視覺模組都算媒體**——image-rich 或 video-rich 或 viz-rich 或 mixed 都可達標。儀器：`paragraph-rhythm` 密度 band（floor 1.2 / ceiling 2.0 / hard 2.5+median<55）+ `media-richness` count target（長文朝 ≥8）。完整 baseline 表見 [EDITORIAL §媒體編織](../editorial/EDITORIAL.md#媒體編織圖片與影片穿插的敘事流2026-05-17-新增)。

- **2 張**：適用於人物文 / 短深度文（hero + 1 scene-mid 視覺呼吸）
- **3 張**：適用於 ≥ 3000 字深度文 / 多時序敘事（hero + 2 scene-mid）
- **0 張**：適用於 Hub 頁（`_*.md`） / 純架構性條目
- **> 3 張**：例外場景才用（如展演紀錄需多角度），避免敘事被視覺打斷

**來源優先序**（2026-05-09 fair use scope 升級後）：

1. **官方機構釋出 PD**（NASA / 政府開放資料 / NMTH）— 完全免授權追問，cache 即可
2. **Wikimedia Commons CC0 / PD** — cache 即可
3. **Wikimedia Commons CC BY / CC BY-SA** — 必須在文末「## 圖片來源」標 author + license + link
4. **Flickr CC BY / CC BY-SA** — 同上
5. **企業 / 機構官網釋出圖**（official press kit / news release / about page）— 標 ©機構 + 用途。**對企業文 / 機構文這層通常是首選**
6. **出版社 / 媒體授權圖**（哲宇 / Taiwan.md 取得明確授權）— 文末標 © 來源 + 授權範圍
7. **自拍 / 自製插畫** — 標 © Taiwan.md / contributor name
8. **Fair use editorial commentary**（2026-05-09 啟動）— 對「在世藝術家作品紀錄圖」「企業產品圖」「電影海報」「專輯封面」「個展裝置照」走 fair use editorial commentary scope，**不需 CC license**，標來源 + 單位 + 用途即可
9. **歷史史料圖無 PD 替代**（如 1947 二二八紀錄照）— 同 fair use editorial scope，但要更謹慎查證歷史出處

**Fair use 法理依據**：17 U.S.C. § 107 + 著作權法 § 65 fair use 四要素：(a) 非商業教育性質 (b) 已發表作品 (c) 引用比例小 (d) 對市場無實質替代效果。

**Fair use 用法守則**：(i) 一定要 cache 本地不熱連結 (ii) 文末 §圖片來源 完整 attribution (iii) 標明「Fair use editorial commentary on [target]'s work」license type。

**絕對禁止**：

- 熱連結（hot-link）任何外站圖（Wikimedia / Flickr / 媒體網站）→ **永遠 cache 本地**
- 未授權的攝影師圖（Google 圖片找到的）
- AI 生成圖片（暫時禁用，紀實 portrait 永遠禁用）
- GIF / HEIC / BMP / TIFF（須先轉 JPG 才入庫）

**🔧 影像後處理 SSOT — `image-ingest.mjs`**（2026-06-13 儀器化，REFLEXES #15 + #30）：下載 / magic-byte 格式驗 / EXIF 清除 / 縮放上限 / **WebP 轉檔** / size budget 壓縮 / 命名規範 / aspect 護欄 / attribution stub 一條龍，取代手跑 curl + sips。sharp-based（Astro 已帶，cross-platform）。

```bash
# ingest 一張（下載→驗→清 EXIF→縮放→轉 WebP→壓到 budget→命名→cache→印 md/§圖片來源/授權矩陣 row）
node scripts/tools/image-ingest.mjs ingest --src <URL|path> --cat <Category> \
  --name <subject>-<topic>-<year> --role hero|inline [--format webp|jpg|png] \
  --alt "具體 alt" --credit "..." --license "..." --source-url "https://commons.wikimedia.org/wiki/File:..."

# check 檢驗 gate（格式白名單 / aspect / size budget / EXIF 殘留）— pre-commit / CI 可掛
node scripts/tools/image-ingest.mjs check public/article-images/{cat}/<name>.webp --role hero

# audit 全站體檢（格式分佈 / 超標 / EXIF 洩漏 / WebP 遷移面）
node scripts/tools/image-ingest.mjs audit [--cat <Category>]
```

**授權仍是 human 判斷，tool 不查授權**：研究階段（Step 1.9）WebFetch File 頁逐字引用 license + 落 §媒體授權矩陣；REFLEXES #31 主 session 重驗每張 license（agent / manifest 的 license claim 是線索不是事實），確認後才把 `--credit/--license/--source-url` 交 tool 入庫。tool 只負責「驗證過的圖 → 乾淨入庫」。

**格式規範**：

```
✅ JPG (.jpg) — 預設：人像 / 風景 / 紀實照。sRGB / quality 80-90 / 無 EXIF GPS
                hero < 600KB / inline < 400KB
✅ PNG (.png) — 插圖 / 圖表 / 透明背景 logo / 螢幕截圖。8-bit RGBA / < 800KB
✅ WEBP (.webp) — **2026-06-13 起新媒體預設**（`image-ingest --format webp` source-level 轉檔；Astro passthrough 直送，瀏覽器全支援。既有 jpg/png 待全站遷移 roadmap）
✅ SVG (.svg) — vector logo / 簡單插圖。< 50KB / 無外部 reference / 文字 outline
❌ GIF / HEIC / BMP / TIFF — 禁用
```

**命名 convention**：`public/article-images/{category-lower-kebab}/{subject-slug}-{topic}-{year}.{ext}`

範例：

```
public/article-images/people/lindgren-emu-2014.webp
public/article-images/people/lindgren-crew4-training.webp
public/article-images/history/twenty-eight-incident-monument-2025.jpg
```

規則：全 lowercase / kebab-case / 必含 subject-slug + topic + year / ext 副檔名

**Aspect ratio 護欄**（避免 Astro 16:9 框切到頭，林琪兒 ι session 教訓）：

| 圖種                | 推薦比例                           | 推薦尺寸             | 理由                            |
| ------------------- | ---------------------------------- | -------------------- | ------------------------------- |
| hero（frontmatter） | **16:9 或更寬** landscape          | 1600×900 / 2000×1200 | Astro 16:9 框直接 fit           |
| inline 圖           | 可 portrait 但 ≤ 4:3 高比          | 1200×900 / 1500×1000 | markdown `![]()` 框較寬鬆       |
| 1:1 方形            | 接近方形 1:1 ± 10%                 | 1600×1600            | hero 也接受（如 EMU 1692×1691） |
| **絕對禁止 hero**   | 9:16 portrait（高 > 寬 1.5x 以上） | —                    | Astro 一定切到頭                |

強制檢查：`image-ingest ingest` 入庫時自動報 aspect（亦可 `image-ingest check <file> --role hero` 或舊 `check-aspect.sh` 單跑）。Hero aspect 必過 0.9 ≤ ratio ≤ 2.0；inline 必過 0.75 ≤ ratio ≤ 2.5。不過 → **換圖**（不要強塞，tool 不自動裁切，裁切是編輯判斷）。

#### Step 1.9.3: transcript 素材

| 來源類型                            | 處理方式                                                                                                                         |
| ----------------------------------- | -------------------------------------------------------------------------------------------------------------------------------- |
| 公視／TaiwanPlus／官方 YouTube 訪談 | `yt-transcript.py fetch`（抓字幕 + 清逐字稿一條龍）→ 落 `reports/research/YYYY-MM/{slug}-transcripts/` → footnote 引 YouTube URL |
| Podcast 官方頁                      | footnote 引 podcast URL；若有 transcript 公開 → cache transcript                                                                 |
| 自製訪談錄音                        | 不公開原始錄音；只引 verbatim 段落，footnote 註明「Taiwan.md 自訪談 YYYY-MM-DD」                                                 |

**工具（2026-06-27 儀器化，REFLEXES #15 + §造橋）— `scripts/tools/yt-transcript.py`**：給 YouTube URL → yt-dlp 抓字幕 → 清成**連續逐字稿 + 每 ~60s 一個 `[MM:SS]` 錨點**（腳註可精確標時間，如「塞掐 E350 @ 12:34」）→ `.vtt`（raw 永留證據鏈）+ `.txt`（可讀版）落 `reports/research/YYYY-MM/{slug}-transcripts/`。取代手跑 yt-dlp + 臨時清時間戳/dedup。

```bash
# 一支或多支訪談抓進文章研究資料夾（預設 zh-TW,en；--month 預設今月）
python3 scripts/tools/yt-transcript.py fetch <URL> [<URL> ...] --slug {article-slug}
# 已手抓好的 vtt 單清
python3 scripts/tools/yt-transcript.py clean path/to/file.vtt -o out.txt
```

> ⚠️ **auto-caption 專名誤植鐵律**：自動字幕對人名／論文／機構／數字常誤植（紀懷新 case：季懷新→紀懷新、Danny→Denny Zhou、Information Forging→Foraging、Daniel Cunningham→Kahneman）。**逐字稿是線索不是定本，引用前每個專名對權威源校正**，別逐字照抄（[MANIFESTO §10 幻覺鐵律](../semiont/MANIFESTO.md) + [§挖引語紅線](../editorial/EDITORIAL.md#挖引語制度)）。底層仍是 yt-dlp（`brew install yt-dlp`）。

#### Step 1.9.4: 媒體授權矩陣三表（research 檔強制）

每篇 depth article 的 research 檔末尾 append：

```markdown
## 媒體授權矩陣

### inline 外連（YouTube／影像／音檔）

| 作品      | 第一次提及位置                              | URL                                         | 來源頻道          | 授權             |
| --------- | ------------------------------------------- | ------------------------------------------- | ----------------- | ---------------- |
| 〈Cazzo〉 | L346「2019 年 6 月 28 日，她以『?te』之名」 | https://www.youtube.com/watch?v=CM-6FJlYHI4 | 華風數位 official | YouTube standard |

### 圖片素材

| 媒體檔                | 用途 | 來源 URL                                                                    | 授權                 | 攝影者/作者        | 拍攝日期   | NASA Image ID / Commons File             | 本地 cache 路徑                               | alt text                                  |
| --------------------- | ---- | --------------------------------------------------------------------------- | -------------------- | ------------------ | ---------- | ---------------------------------------- | --------------------------------------------- | ----------------------------------------- |
| lindgren-emu-2014.jpg | hero | https://commons.wikimedia.org/wiki/File:Kjell_Lindgren_in_EMU_(cropped).jpg | Public domain (NASA) | NASA/Bill Stafford | 2014-08-27 | File:Kjell*Lindgren_in_EMU*(cropped).jpg | /article-images/people/lindgren-emu-2014.webp | 林琪兒 2014 年穿艙外活動服（EMU）官方人像 |

### 引用 transcript

| Transcript     | 來源                   | URL                                         | 落檔路徑                                                      |
| -------------- | ---------------------- | ------------------------------------------- | ------------------------------------------------------------- |
| 公視訪談 zh-TW | 公視新聞網 official YT | https://www.youtube.com/watch?v=f9DQuQ8EwVE | reports/research/2026-04/林琪兒-transcripts/transcript-zh.txt |
```

#### Step 1.9.7: persona 讀者缺口稽核 + 增補（v7.7 新增，persona 從 Stage 0 搬來）🫂

> **v7.7（2026-07-06 施振榮）**：persona 20 路讀者切入點從 Stage 0（[原 0.6.1-bis](REWRITE-STAGE-0-VIEWPOINT.md#step-061-bis-persona-已移到研究後v77--見-step-197)）搬到這裡——研究報告 SSOT 組完之後、Stage 2 寫作之前。角色從「發散定調」改成「**讀者缺口稽核 + 增補**」。設計：[reports/design-立體群像...](../../reports/design-立體群像-default-persona-reposition-2026-07-06.md)。

**觸發**：所有 depth article（Micro / heal / 純翻譯不跑）。前提：Step 1.7 研究報告 §6 fact-pack 已組好、Step 0 立體觀點已成形。

**呼叫**（完整 contract + 20 archetypes + 4-agent 平行見 [PERSONA-PIPELINE](PERSONA-PIPELINE.md)）：

```
call PERSONA-PIPELINE:
  subject_brief: 題目 brief + 研究報告 §6 fact-pack + §觀點成型（給 persona 讀，不是冷 brief）
  mode: gap-audit          # v7.7 新 mode：對已成形的立體畫像補洞，不是冷發散定調
  profile_set: default 20
```

**每個 persona 問的**（跟舊 research-diverge 的差別）：不是冷讀者的第一反應，是「**看完這份研究後，我這種讀者還想知道什麼？哪個我在意的面向沒被 cover？**」。20 顆讀者腦袋在一張已成形的立體畫像上找洞。

**輸出處理（三分類 + 一個閥門）**：

1. 🆕 **真缺口** → 起 targeted 增補搜尋（補這個 facet 的事實/場景/引語），把 finding 加進 report §3/§6。**增補後 report 變了，Step 1.9.5 收尾前重跑 [research-report-health gate](REWRITE-STAGE-1A-RESEARCH.md#step-17-研究報告--ssot對標研究所論文標準-)。**
2. ✅ **已 cover** → 記錄不重複。
3. ⛔ **超 scope** → 落 `rationale.whats_excluded`。
4. 🔴 **反向閥門（立體 ≠ 迴避的自我糾正）**：如果 persona（尤其 D 軸挑硬傷/反方）揪出「這篇立體群像其實洗掉了一個真該被尖銳處理的公共爭議」→ 回 [Step 0.1.5](REWRITE-STAGE-0-VIEWPOINT.md#step-015-spine-類型判定v77-重構--立體群像是預設畫布) 重判，**三個合法目的地**（v7.8 從兩個擴為三個）：(i) 把那個爭議升成一個 substantial facet；(ii) **改判第三型「多觀點立場議題探討矛盾型」**——若該題是進行中的公共議題且多方都有正當立場，這通常是正解；(iii)（罕見）解鎖單軸矛盾驅動主脊。**這條讓立體 default 不變擋箭牌。**
   ⚠️ **為什麼要明列第三個目的地**（2026-07-25 外送專法）：該篇三軸反向閥門都命中，但 Step 0.1.5 的兜底是「拿不準 → 立體群像」，**偵測成功卻沒有轉成重判**，最後是觀察者一句話補上那個目的地。偵測機制有了、目的地沒寫，等於沒接上。

**為什麼放這裡而不是 Stage 0**：冷讀者天生問尖銳問題，放搜尋之前 → 尖角變研究方向 → 脊椎被推向矛盾驅動（施振榮 v1 教訓）。放研究後，同一句尖問變「要不要補一個 facet」而非「整篇該不該講這個」——從定調變補洞，且剛好接住 persona 誕生的 use case（《看不見的國家》ship 後哲宇追問三題＝完成度缺口，正該 ship 前被稽核接住）。

**Cost guard**：4 Sonnet agent 短輸出（reuse-from-report 優先）；下游 caller（SPORE hook-select）reuse 同一份 persona pool，見 [PERSONA-PIPELINE §4-5](PERSONA-PIPELINE.md)。

**落檔**：research report §讀者缺口稽核（20 persona × 分類 + 增補了什麼 + 反向閥門判斷）。

#### Step 1.9.5: Stage 1 收尾 checklist

Stage 1 結束時 deliverable：

- [x] 核心矛盾欄位必填（Step 1.4）— 填不出來 → 不進 Stage 2
- [x] depth-article 研究報告必存（Step 1.7）— `reports/research/YYYY-MM/{slug}.md` 不存在 → 不進 Stage 2
- [x] 媒體授權矩陣三表 append 完成（inline 外連 / 圖片 / transcript）
- [x] 圖片已 cache 在 `public/article-images/{category}/`
- [x] Aspect ratio 護欄通過（hero 0.9-2.0 / inline 0.75-2.5）
- [x] Transcript 已 cache 在 `reports/research/YYYY-MM/{slug}-transcripts/`
- [x] 私有 SSOT 整合過 Step 1.6 觀察者拍板（如有觸發）
- [x] Frontmatter audit 完成（`[STUB-TITLE]` / `[NO-MEDIA]` 標籤）— EVOLVE 才必跑

**沒過 = 不進 Stage 2。**

---
