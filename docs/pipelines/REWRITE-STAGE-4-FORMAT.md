---
title: 'REWRITE-STAGE-4-FORMAT'
description: 'REWRITE v9 stage contract — Stage 4：article-health 7 維度 / 多語 visual smoke / 媒體插入 6 子步（v9.0 修 4.3.6 撞號 → 4.3.7）'
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

# Stage 4 contract — 形（format＋媒體插入）

> **本檔是 REWRITE-PIPELINE v9.0 的 stage contract**：一個執行者（主 session、sub-agent、
> 或任何 context 有限的 model）只讀本檔＋本檔 INPUTS 宣告的檔案，就能執行本 stage。
> 派發路由與全 pipeline spine 在 [REWRITE-PIPELINE.md](REWRITE-PIPELINE.md)（薄索引）。
> 內文自 v8.0 主檔 verbatim 搬移（原行號 RP v8.0 L1902-2253（v9.0 更正：原第二個 Step 4.3.6「影片 iframe 嵌入」重編號為 4.3.7）），歷史敘事與教訓保留在文內。

## 執行卡

|                  |                                                                                                                                                    |
| ---------------- | -------------------------------------------------------------------------------------------------------------------------------------------------- |
| **職責**         | 格式 7 維度、多語 smoke（i18n 改動時）、媒體插入（節奏判斷/fetch/aspect/插入/授權同步/健檢/iframe）                                                |
| **執行者**       | 主 session                                                                                                                                         |
| **INPUTS**       | canonical 正文；research 檔媒體授權矩陣（Stage 1B 產物）；EDITORIAL §媒體編織                                                                      |
| **OUTPUTS**      | 文內媒體＋`## 圖片來源` 段；`public/article-images/{cat}/`                                                                                         |
| **GATES**        | `python3 scripts/tools/article-health.py knowledge/{Cat}/{slug}.md --profile=rewrite-stage-4`（hard=0）＋`--check=image-health`；`check-aspect.sh` |
| **context 預算** | 本檔＋成品＋授權矩陣                                                                                                                               |

## AGENT PROMPT

**不派 agent**——格式與媒體插入主 session 自跑（授權同步與 aspect 判斷需 human 眼）。

## 交付條件（stage 完成的定義）

- [ ] `article-health.py knowledge/{Cat}/{slug}.md --profile=rewrite-stage-4` hard=0
- [ ] `--check=image-health` pass（depth：媒體 ≥ max(3, round(prose-CJK/1200))）
- [ ] 文末 `## 圖片來源` 段與授權矩陣一致；`check-aspect.sh` 過
- [ ] （i18n 改動時）多語 visual smoke 6 步過

## HANDOFF（stage 完成時）

> stage 若委派 sub-agent，本五步由 orchestrator 於收件驗證後執行（agent 不碰共用看板——2026-07-16 高教 dogfood F6）。

1. OUTPUTS 全數落檔（顯式路徑，不存 scratchpad / tmp——REFLEXES #81）**並隨手 commit（只 stage 本 stage 產物路徑——可觀測性與跨 session 接力的底座，v9.5；勿 `git add -A`）**
2. GATES 逐條跑過，結果如實回報（sub-agent claim 是線索不是 oracle，REFLEXES #31）
3. 更新編輯台：`python3 scripts/core/generate-newsroom-data.py`（看板反映現況）
4. 回報格式：stage id ＋ 產物路徑清單 ＋ gate 結果 ＋ 未解疑慮（有就寫，不粉飾）
5. 下一棒：REWRITE-STAGE-5-CROSSLINK.md

---

## Stage 4: 形（Format + Media，預算 5-10%）

**Stage 3 commit 前最後關。**

這一步跟 Stage 3 不同——Stage 3 檢查「寫得好不好 + 事實對不對」，Stage 4 檢查「結構對不對 + 媒體插得對不對」。

### Step 4.1: article-health.py --profile=rewrite-stage-4

#### 強制執行（不是建議，是反射）

```bash
python3 scripts/tools/article-health.py knowledge/{Category}/{文章}.md --profile=rewrite-stage-4
```

`rewrite-stage-4` profile plugin（HARD all；清單與數量以 `article-health.py --list-checks` 為準）：

| Plugin               | 檢查內容                                                                                                                                                                                                                                                                                                                                                                                              |
| -------------------- | ----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| `frontmatter-format` | 必要欄位 + 順序                                                                                                                                                                                                                                                                                                                                                                                       |
| `format-structure`   | 30 秒概覽 / 延伸閱讀 / 參考資料 section 存在                                                                                                                                                                                                                                                                                                                                                          |
| `wikilink-target`    | wikilink 對應檔案存在                                                                                                                                                                                                                                                                                                                                                                                 |
| `link-target`        | markdown link path casing + existence                                                                                                                                                                                                                                                                                                                                                                 |
| `cjk-punct`          | 中文 prose 全形標點                                                                                                                                                                                                                                                                                                                                                                                   |
| `chronicle-lead`     | H2 不是 `## YYYY 年 X 月` 編年體                                                                                                                                                                                                                                                                                                                                                                      |
| `word-count`         | depth article ≥ 4500 CJK chars（v3.1 sad-shockley 新增，HARD via severity_override）                                                                                                                                                                                                                                                                                                                  |
| `image-health`       | depth ≥ 3 張（hero + 2 scene-mid）— v3.2 kind-mirzakhani 新增（HARD）                                                                                                                                                                                                                                                                                                                                 |
| `paragraph-rhythm`   | **段落 median ≥ 55 CJK + H2 prose 段落 ≤ 8 + 媒體密度 band 1.2–2.0/1k CJK**（2026-07-12 哲宇 directive「提升上限，新基準範圍 1.2~2」第三波上修 0.7→0.8→1.2–2.0；floor 1.2 media-poor / ceiling 2.0 / hard 2.5+median<55；舊範本 設研院 0.91/黃魚鴞 0.82 在新基準屬偏少，帶內範本 陳建年 1.48。WARN-only soft launch） + `media-richness` length-scaled count（長文朝 圖+影片 ≥8 INFO + 多模態 nudge） |

> ⚠️ **profile 邊界鐵律**（v6.1，2026-05-17 admiring-montalcini）：`rewrite-stage-4` profile **不含** `footnote-format` / `footnote-density`（那兩個在 `rewrite-stage-3-5` profile，Stage 3.3 跑）。Stage 4 跑全綠**不代表 CI 會過** — CI full sweep 跑全 全量 plugin（以 `--list-checks` 為準），包含 stage-3-5 的 footnote 系列。如果跳過 Stage 3.3 的 `rewrite-stage-3-5` plugin gate，本機 Stage 4 顯示綠燈但 CI 會 hard-fail。誕生事件：2026-05-17 臺灣前途決議文 ship 後 CI footnote-format hard=23（commit `b39ea5529` 補修 29 條 footnote）。對策：**Stage 3.3 必跑 `--profile=rewrite-stage-3-5`**（已寫進本檔 Step 3.3 + 頂部 Hard Gate Inventory）。

**Pre-commit hook 已自動執行**這幾項檢查（SSOT pre-commit profile 自 2026-05-04 Phase 10 接管）。如果被擋：按提示修正，**不要用 `--no-verify` 繞過**。

> **為什麼要強制？** 2026-04-04 我在台灣國樂的延伸閱讀寫了 7 個 `[[wikilink]]`，忘記 Astro 不渲染。規則在本文件 v2.10 已經寫過、工具 wikilink validation 存在——然後還是寫錯了。教訓：**擁有工具 ≠ 使用工具**。所以現在寫進 pre-commit 強制執行。

#### 格式範本檢查清單（手動 audit）

```
□ Frontmatter 完整（title/description/date/category/tags/subcategory/author/featured/lastVerified/lastHumanReview）
□ 30 秒概覽存在（blockquote 格式，開頭 > **30 秒概覽：**）
□ 正文小標題不是問句（除非問句本身是核心矛盾）
□ 延伸閱讀區塊存在且格式正確：
    - 標題是 **延伸閱讀**：
    - 每條用標準 Markdown 連結（不是 [[wikilink]]）
    - 每條有一兩句話描述
    - 3-5 條
□ ## 參考資料 標題存在，且在腳註定義之前
□ 腳註格式正確：[^n]: [來源名稱](URL) — 完整描述文字
□ 沒有殘留的舊格式（## 參考資料 下面不該有 bullet list 式的來源）
□ word-count ≥ 4500 CJK chars（v4 新 hard gate）
```

**⚠️ 格式不合格 = 修正後重新檢查。不進 Step 4.3。**

### Step 4.2: 多語 visual smoke test（i18n 改動時）

> **觸發條件**：commit 涉及任何 i18n 系統 / 多語系路由 / homepage components / `src/pages/{lang}/` / `src/i18n/`、或加新語言、或大型 sed 批次替換。
> 對應 [REFLEXES #19 大型 refactor 後 visual smoke test](../semiont/REFLEXES.md#四工程衛生)。

**強制 SOP**（6 步）：

```bash
# 1. Build verify
npm run build  # 必須 ✅ all categories healthy

# 2. Cascade prevention test（驗 Phase 1 fix 仍 work）
F="dist/fr/people/index.html"
grep -oE '"/[a-z][a-z-]*/people"' "$F" | sort -u
# 預期：/en/people、/ja/people、/ko/people、/fr/people（+ /es/people if dropdown 完整）
# 不應出現：/ja/fr/people、/ko/fr/people 等 cascade URL

# 3. 5 langs 結構對齊檢查
for L in '' en ja ko fr es; do
  if [ -z "$L" ]; then f="dist/index.html"; lang="zh-TW"; else f="dist/$L/index.html"; lang="$L"; fi
  echo "$lang: halls=$(grep -c 'exhibition-hall' $f) RD=$(grep -c 'Random' $f)"
done
# 預期：5 langs 都有 exhibition halls + RandomDiscovery

# 4. Wrong-language prose 檢查（fr/es 不該含日文/中文 hardcoded）
for L in fr es; do
  hits=$(grep -c -P "[\x{3040}-\x{309F}\x{30A0}-\x{30FF}]" "dist/$L/index.html")
  echo "$L: $hits 平假名/片假名 occurrences"
done
# 預期：0 / 0

# 5. LANGUAGES_REGISTRY SSOT 對齊
bash scripts/tools/check-hardcoded-langs.sh

# 6. i18n coverage audit
bash scripts/tools/i18n-coverage-audit.sh
```

**任何一項失敗 = revert 該 commit，不 ship**。歷史教訓：Tailwind Phase 6 反向 sed 讓 ja/ko 壞 2 天 / fr 上線 cp + sed 漏抓日文 prose 持續 1 天 / fr/es 路由疊加 cascade 4 天才被發現——三次都因為缺這層 smoke test。

### Step 4.3: 媒體插入

**觸發時機**：Step 4.1 format-check 通過後、Stage 5 cross-link 之前。

**為什麼這時插入**：寫完 prose 才知道「實際敘事節奏在哪、哪段需要 visual 呼吸」。寫之前布陣會綁死寫作節奏；寫完一次插入更自然。

**依賴**：Stage 1 Step 1.9 必須完成（媒體授權矩陣三表 append research 檔 + 圖片已 cache）。沒做 → 退回 Stage 1 Step 1.9。

#### Step 4.3.1: 三段敘事節奏判斷（圖 + 影片 整合）

媒體插入位置影響敘事節奏，不是隨便塞。三段標準（圖跟影片穿插，per EDITORIAL §媒體編織）：

| 位置          | 用途                       | 圖型                  | 圖數 | 影片可放？                   | 範例                            |
| ------------- | -------------------------- | --------------------- | ---- | ---------------------------- | ------------------------------- |
| **hero**      | 30 秒概覽前，建立視覺認知  | 16:9 landscape 或 1:1 | 1    | ❌（影片在 hero 太重）       | 林琪兒 EMU 2014                 |
| **scene-mid** | 中段重要轉折前 / 後        | landscape 為主        | 0-2  | ✅（代表作 / 直播 / 演講）   | Expedition 42 / 〈海洋〉MV      |
| **closure**   | 結尾段視覺收尾（首尾呼應） | landscape             | 0-1  | 0-1（最後代表作 / 紀念影像） | 訪台首日場景照 / 〈美麗心蘭嶼〉 |

**整體類型 × 媒體比重 baseline**（canonical 在 [EDITORIAL §媒體編織](../editorial/EDITORIAL.md#媒體編織圖片與影片穿插的敘事流2026-05-17-新增)）：

- 音樂人：2-3 圖 + **2-3+** 影片（代表作 MV / 早期 / 最新三層時間軸）
- 運動員 / 演員 / YouTuber：2-3 圖 + 1-3 影片
- 樂團 / 音樂類型史：2-3 圖 + **3-5** 影片
- 政治人物 / 學者：2-3 圖 + 0-2 影片
- Nature / 生態：2-3 圖 + 1-2 影片
- Food / Culture / Tech：2-3 圖 + 0-1 影片
- Hub 頁：0 圖 0 影片

**通用判準**：

- depth-article（≥ 3000 字）：2-3 圖 + 依類型 1-5 影片
- 短文：hero only（1 張），不放影片
- 翻譯文：跟原文同步媒體（不另增 / 不另減）
- 找不到官方影片 → 不勉強塞，多放 1 張圖補位

**圖跟影片穿插原則**：兩者交錯出現，不疊放在同一段。圖跟影片之間至少隔 2-3 段 prose。沿 narrative arc 放，不是按重要性堆在開頭。

**Scene-mid 位置規則**：圖放在「該段 narrative 開始前」而不是「該段中間」：

```markdown
## 紅色 LED 下的第一口萵苣 ← 小標題

[圖：Expedition 42 三人合影] ← 圖放這裡
_caption_

prose 開始... ← 文字接續
```

**呼吸原則**（呼應 EDITORIAL §密度平衡）：連續 3 段以上密集事實段（≥ 200 字 / 段）→ 中間插入一張 scene 圖作為視覺呼吸。

#### Step 4.3.2: 圖檔 fetch + cache + naming

依 Stage 1 Step 1.9.2 的 manifest 已 cache 完成。Step 4.3.2 僅做最後 verify：

```bash
# 確認所有 manifest 列出的圖檔都存在於 public/article-images/
ls public/article-images/{category}/

# 必要時補抓（若 Stage 1 未完成全部圖）
mkdir -p public/article-images/{category}/
curl -sL -A "Mozilla/5.0 Taiwan.md/1.0" "{hi-res-url}" \
  -o public/article-images/{category}/{slug}-{topic}-{year}.{ext}

# 確認 file format + 大小 + EXIF GPS 已清
file public/article-images/{category}/{filename}
sips -g pixelWidth -g pixelHeight public/article-images/{category}/{filename} | tail -3

# 必要時 resize / re-encode（hero < 600KB / inline < 400KB）
sips -Z 2000 --setProperty formatOptions 85 public/article-images/{category}/{filename}

# 清 EXIF GPS / 個人資訊（保留 description / copyright）
exiftool -gps:all= -location:all= -DeviceMfgr= -DeviceModel= public/article-images/{category}/{filename}
```

#### Step 4.3.3: Aspect ratio 護欄

```bash
bash scripts/tools/check-aspect.sh public/article-images/{category}/{filename}
```

| 圖種          | 必過範圍            | 歷史教訓                                                             |
| ------------- | ------------------- | -------------------------------------------------------------------- |
| **hero**      | 0.9 ≤ aspect ≤ 2.0  | lindgren-crew4-portrait.jpg 1041×1561 (0.67) 切到頭 → 換 1041×694 ✅ |
| **inline 圖** | 0.75 ≤ aspect ≤ 2.5 | Expedition 42 4896×3264 (1.5) ✅ / EMU 1692×1691 (1.0) ✅            |

不過 → **換圖**（不要強塞）。

#### Step 4.3.4: Markdown 插入 + caption + alt text

**標準格式**：

```markdown
![alt text 描述](/article-images/{category}/{filename}.jpg)
_caption 說明文字。Photo: {credit}. [License via {source}]({source-url})._
```

**Alt text 規則**（accessibility 必需）：

- 描述「畫面內容」不是「圖名」
- 涵蓋：誰 + 在哪 + 做什麼 + 拍攝氛圍
- 30-80 字
- 不重複 caption 文字

**範例對比**：

```markdown
❌ 壞 alt text（只有圖名）：
![林琪兒 2014](/article-images/people/lindgren-emu-2014.webp)

✅ 好 alt text（描述畫面）：
![林琪兒 2014 年穿艙外活動服（EMU）官方人像，全套白色 NASA 太空服，仰角拍攝顯示頭盔反光](/article-images/people/lindgren-emu-2014.webp)
```

**Caption 規則**：

- 用 markdown italic `_..._`（不用 HTML `<figcaption>`）
- 結構：`{時間 + 地點 + 事件}。Photo: {攝影者 / 機構}. [License via {source}]({URL})。`
- 中文 prose 風格，跟 article 一致
- 關鍵 metadata（NASA Image ID / Commons file name）放括號註

#### Step 4.3.5: 授權清單同步

每張 inline 圖插入後，**強制同步**：

**1. frontmatter**（hero only）：

```yaml
image: '/article-images/{category}/{filename}.jpg'
imageCredit: '攝影者 / 機構'
imageLicense: 'Public domain (NASA)' / 'CC BY-SA 4.0' / etc
imageSource: '{source-URL}'
```

**2. 文末「## 圖片來源」section**（所有圖）：

```markdown
## 圖片來源

本文使用 N 張公有領域 / CC 授權圖片，全部 cache 於 `public/article-images/{category}/` 避免熱連結來源伺服器：

- [圖檔 1 標題](source-URL) — Photo: 攝影者, YYYY-MM-DD, License, NASA Image ID 或 Commons file
- [圖檔 2 標題](source-URL) — ...
```

#### Step 4.3.6: 圖片健康檢查（plugin gate）

```bash
python3 scripts/tools/article-health.py knowledge/{Category}/{slug}.md --check=image-health
```

預期檢查：

- ✅ 文中所有 `![]()` 連結對應檔案存在
- ✅ Frontmatter `image:` 存在 + credit + license + source
- ✅ 文中無外部熱連結（http/https URL 不在 `/article-images/`）
- ✅ `## 圖片來源` section 存在
- ✅ 所有圖全部有完整 metadata（攝影者 / license / source URL）

**不通過 → 不進 Stage 5。**

#### Step 4.3.7: 影片 iframe 嵌入（Music / People / Nature 條目升級）

**觸發時機**：題材含**公開影像作品**且 inline link 不足以承載敘事張力時 — Music 條目（代表作 MV）、Nature 條目（生態直播 / 影像紀錄）、Documentary 條目（紀錄片預告）、Performance 條目（演出片段）。

**為什麼從 inline link 升 iframe**（哲宇 2026-05-17 directive）：「提高閱讀的多重感受」。Inline link 是「邊讀邊聽」option，iframe 是「閱讀流裡內建多媒體感官層」default。Music 條目尤其受惠 — 文字描述歌曲 vs 直接聽到歌曲是完全不同的閱讀體驗。

**URL 來源優先序**（同 Step 1.9.1）：

1. 官方頻道（藝人 / 廠牌 / 節目方 / 導演）— 角頭音樂 / 公視 / 滾石等 official YT
2. 國際串流官方（YouTube Music / Vevo official artist channel）
3. 主辦 / 策展單位官方頁

**不接受**：UGC 翻唱、二手轉貼、搜尋結果頁、Topic auto-generated channel（YouTube 自動生成的 "Provided to YouTube by..." 假頻道）。

**密度建議**（per [EDITORIAL §媒體編織 類型 × 媒體比重 baseline](../editorial/EDITORIAL.md#媒體編織圖片與影片穿插的敘事流2026-05-17-新增)）：

| 條目類型                  | 影片 iframe 最低 | 上限 | 備註                                             |
| ------------------------- | ---------------- | ---- | ------------------------------------------------ |
| **音樂人**                | **2-3**          | 5    | 代表作 / 早期 / 最新三層；找不到 official → 補圖 |
| **樂團 / 音樂類型史**     | 3                | 5    | 各時期代表作 anchored 到時間軸                   |
| **運動員 / 演員**         | 1                | 3    | 表演 / 訪談 / 比賽關鍵時刻                       |
| **YouTuber / Podcaster**  | 2                | 4    | 代表節目 / 訪談 (官方頻道)                       |
| **政治人物 / 學者**       | 0                | 2    | 演講 / 重要場合影像（如有）                      |
| **電影 / 紀錄片**         | 1                | 2    | 預告 / 關鍵片段（注意版權）                      |
| **歷史事件**              | 0                | 2    | 紀錄片 / 倖存者口述（如有官方版本）              |
| **Nature / 生態**         | 1                | 2    | 直播 / 紀錄片 / 觀察影像                         |
| **Food / Culture / Tech** | 0                | 1    | 大多靠圖即可                                     |
| **Hub 頁**                | 0                | 0    | 不放 iframe                                      |

Hub 頁 / 短文 / 純架構性條目不放 iframe。多於上限 → 視覺擁擠打斷敘事，重新分散。

> ⚠️ **媒體密度 band（floor + ceiling）**（2026-07-12 哲宇 directive「提升上限，1.5x-2x 都是健康，新基準範圍 1.2~2」第三波上修；lineage：v6.4 單一上限 0.8 → v6.6 band 0.7–1.2 → v6.8 floor 0.8 → **1.2–2.0**）：總體 (圖+影片+hero+tw-\* 模組) density 落在 **1.2–2.0 / 1k CJK** 健康帶。**下限 1.2**：低於 = 媒體偏少（舊健康範本 設研院 0.91 / 天下 0.92 / 黃魚鴞 0.82 在新基準下屬偏少——方向 = 富媒體 default 再拉升）→ 補圖、官方影片或 tw-\* 視覺模組。**上限 2.0**：高於 = visual 密度偏高。**> 2.5 且段落 median < 55 = HARD atomization**（雙信號結構不變；帶內範本 陳建年 1.48 / 周蕙 1.76——周蕙當年是 density+median 雙信號才 HARD）。`paragraph-rhythm` plugin 自動 catch 全 band。歷史 narrative：[reports/spore-voice-drift-fix-2026-05-28.md §第 7 種 pattern](../../reports/spore-voice-drift-fix-2026-05-28.md)。

**位置原則**（呼應 Step 4.3.1 三段敘事節奏）：

- iframe 放在「該段 prose 結尾」，不是段首 — 讓讀者先讀完文字段，再有 option 聽 / 看
- 沿文章時間軸 / narrative arc 放，不是按重要性堆在開頭
- 每個 iframe 配 italic caption 標明 (1) 官方來源頻道 (2) 跟文章 narrative 的呼應

**標準格式**（黃魚鴞 / 陳建年 pattern）：

```html
<div
  class="video-embed"
  style="position:relative;padding-bottom:56.25%;height:0;overflow:hidden;margin:1.5rem 0;border-radius:8px;"
>
  <iframe
    src="https://www.youtube.com/embed/{VIDEO_ID}"
    title="{原始繁中標題}"
    style="position:absolute;top:0;left:0;width:100%;height:100%;border:0;"
    loading="lazy"
    allow="accelerometer; autoplay; clipboard-write; encrypted-media; gyroscope; picture-in-picture; web-share"
    allowfullscreen
  ></iframe>
</div>

_{source channel} 官方 MV：{跟文章 narrative 呼應的一句話描述}。_
```

> ⚠️ **`</div>` 跟 `_caption_` 之間必須有空行**（2026-06-07 哲宇 live review callout）：markdown / remark 對 HTML block（`</div>`／`</iframe>`）後**緊接**的 `_..._` 不會 render italic，底線會變成字面字元顯示。working pattern（陳建年）是 `</div>` ↵↵ `_caption_`。spawn writer agent 寫 iframe 時最常漏這個空行（複雜生活節 3 支全漏）。`image-health` plugin 已儀器化 catch（caption 缺空行 WARN，2026-06-07）。

**Verify 步驟**（強制）：

1. 每個 video ID 走 WebFetch 確認「Official Music Video」或「官方完整版 MV」標記（不憑 search title 推斷）
2. preview_eval 跑 `document.querySelectorAll('iframe[src*="youtube.com/embed"]').length` 確認 N 個 iframe render
3. preview_eval 列 `[...iframes].map(f => f.src.split('/embed/')[1])` 比對 video ID 跟原稿一致

**跟 Step 1.9.1 inline 外連的分工**：

- Step 1.9.1 inline link：3-8 個，作品名第一次出現處 hyperlink，預設都加（成本低）
- Step 4.3.6 iframe embed：3-5 個，沿 narrative arc 放代表作（高 value、高呈現成本）
- 同篇條目可以**並存** — inline link 給「邊讀邊聽 option」，iframe 給「代表作必看」

**範例參考**：

- Music 條目：[knowledge/People/陳建年.md](../../knowledge/People/陳建年.md) — 4 iframe 沿 1999 → 2000 → 2025 時間軸
- Nature 條目：[knowledge/Nature/黃魚鴞.md](../../knowledge/Nature/黃魚鴞.md) — 2 iframe (公視報導 + 雪霸育雛直播)，敘事密度型

### Stage 4 Step 4.3 邊界與例外

- **Hub 頁**（`_*.md`）：不放圖，跳過 Step 4.3
- **短修正 / heal commit**：不重新走 pipeline，圖用既有的不動
- **翻譯文**：跟原文圖同步（cache 共用），caption 翻譯成對應語言
- **沒有合適媒體素材**：明確標 `no-media` 進 research 檔，跳過 Step 4.3
- **觀察者直接丟連結**（如林琪兒 ι session）：走 Step 4.3.2-4.3.6 補圖 SOP，不走 Stage 1 Step 1.9
- **Article ship 後才發現缺圖**：spawn `heal:` commit + 走 Step 4.3

### 跟 spore 配圖區分

| 圖種                  | 路徑                           | 用途                    | 生成方式                                 |
| --------------------- | ------------------------------ | ----------------------- | ---------------------------------------- |
| article hero / inline | `public/article-images/{cat}/` | 文章內容                | Stage 1 Step 1.9 + Stage 4 Step 4.3 手動 |
| OG 社群分享           | `public/og-images/{cat}/`      | facebook / twitter card | dashboard 自動 derive                    |
| spore poster          | `public/spore-images/`         | Threads / X 配圖        | `make-spore.sh` 自動                     |

不要嘗試共用 — spore 是 social 媒介，需要不同 aspect 跟 brand overlay。article 圖 cache 完整／spore 圖 ephemeral，分開管理。

---
