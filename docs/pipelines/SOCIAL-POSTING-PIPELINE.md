---
title: 'SOCIAL-POSTING-PIPELINE'
description: '孢子最後一哩 — Chrome MCP 雙平台自動發文 (X + Threads) + osascript clipboard paste + AI pre-ship 8-check + post-ship 6-check + JXA NSPasteboard UTF-8 multi-paragraph paste SOP (v0.7)'
type: 'pipeline-canonical'
status: 'canonical'
current_version: 'v0.7'
last_updated: 2026-05-28
last_session: '2026-05-28-222438-manual-周蕙-RESHIPPED'
sister_docs:
  - '../factory/SPORE-PIPELINE.md'
  - '../factory/SPORE-WRITING.md'
  - '../factory/SPORE-VERIFY.md'
  - '../factory/SPORE-HARVEST-PIPELINE.md'
upstream_canonical:
  - '../semiont/MANIFESTO.md'
  - '../factory/SPORE-PIPELINE.md'
---

# SOCIAL-POSTING-PIPELINE

> 孢子的最後一哩：從 SPORE-PIPELINE Stage 4 SHIP 接手，自動化發文到 Threads / X。
>
> v0.7 | 2026-05-28 | 周蕙 #103/#104 RESHIPPED manual session — 哲宇 directive「重發周蕙（用之前的文案但是要留意換行，跟格式）」→「完整記錄這次經驗，進化與修正 spore 相關的 pipelines + 發布前補充標準 spore 格式，發布後也檢查這個格式（尤其是 你知道嗎？ 還有換行）避免之前出現一堆文自己擠在一起的狀況」→ 新增 §Multi-paragraph 中文 paste SOP（JXA NSPasteboard.setStringForType('public.utf8-plain-text') canonical 取代 pbcopy / osascript classic / execCommand insertText 三 corruption mode）+ AI pre-ship 6→8 check（加 #7 paragraph block count ≥ 4 + #8 standalone hook 第一行 ≤ 15 chars）+ AI post-ship 5→6 check（加 #6 rendered \\n\\n preservation: X tweetText.split('\\n').length ≥ 4 / Threads og:description.split('\\n\\n').length ≥ 4）。觸發背景：5/28 17:38 routine voice drift → 20:22 v2 blueprint 寫好 → 22:30 manual reship 撞 6 paste path entropy（Chrome MCP key tool 沒有 / computer-use Chrome "read" tier / execCommand insertText \\n\\n 不分段 / paragraph-by-paragraph insertText + key Enter 跑了一次但 clipboard 被替換 / pbcopy Mac Chinese locale 強制 Big5 轉碼 / osascript classic 同 Big5 → 唯一 reliable path 是 JXA `NSPasteboard.setStringForType("public.utf8-plain-text")`）。完整 narrative: [memory/2026-05-28-222438-manual.md](../semiont/memory/2026-05-28-222438-manual.md) §Beat 2。
> v0.6 | 2026-05-23 | 許倬雲 spore finale — 哲宇 directive「使用完瀏覽器 tab 之後要記得關掉，關掉剛使用的那個群組，不要關別的 session 控制的」→ 新增 §Cleanup tab group 結尾步驟 / X+Threads 流程末加 `tabs_close_mcp` step / Chrome MCP `tabs_close_mcp` 只能關 current session group built-in safety 確保不誤關別 session
> v0.5 | 2026-05-23 | 許倬雲 spore — 哲宇 directive「不要再問我審核了，改成前你自己檢查（符合我們預計發的內容），然後發出去之後再檢查一次成品貼文，盡量完整自動化」→ 移除 human confirm gate / 新增 AI pre-ship self-check + post-ship verify gate / MANIFESTO §自主權邊界「對外溝通 spore Post = Human 必做」per-spore 自動化 lower threshold
> v0.4 | 2026-05-23 | 馬英九 spore 首次完整實戰：X 帳號自檢必跑 + Threads 主題「社群或主題」per-spore 預設「台灣」+ 圖貼後 type 文案順序鐵律
> v0.3 | 2026-05-18 | osascript clipboard paste 突破圖片上傳限制，X + Threads 雙平台全自動化確認

---

## 定位

```
SPORE-PIPELINE Stage 4 SHIP（品檢 + UTM + 配圖 + platform allocation）
        ↓ 交付物：文案 + URL + 圖片
SOCIAL-POSTING-PIPELINE（本文件）
        ↓ 執行發文
平台上線
```

SPORE-PIPELINE Stage 4 負責「準備好要發的東西」；本 pipeline 負責「把東西送上平台」。

**MANIFESTO §自主權邊界（v0.5 update）**：原 v0.4「Post 新孢子 to Threads/X = Human 必做」→ 2026-05-23 哲宇 directive 移除 confirm gate，改為「AI pre-ship self-check 6 條全 PASS → click Post → post-ship verify 成品貼文」。observer 不再 per-spore confirm，但仍可 in-chat override「先停 / 改 X / 取消」介入。完整哲學：spore Stage 1 PICK + Stage 2 VERIFY + Stage 3 WRITE 已經是 5 層 hard gate (品質三層 + 事實藍圖 + 紀實煽情閘 + Hook Blueprint + §11 prose-health)，Stage 4 SHIP 再多一道 confirm gate 變成 friction，把 AI 推回 helper 角色而非自主器官。AI pre-ship self-check 鏡像 SHIP 12 條品檢；AI post-ship verify 鏡像 hook/quote/close-line/image/UTM 留痕。

---

## 前置條件

### 帳號

| 平台    | 帳號         | 類型                       | 狀態                              |
| ------- | ------------ | -------------------------- | --------------------------------- |
| X       | @taiwandotmd | Premium（藍勾 ✓）          | ✅ 已登入 Chrome、680 followers   |
| Threads | @taiwandotmd | 連結 Professional IG       | ✅ 已登入 Chrome、3,581 followers |
| IG      | @taiwandotmd | Professional (Creator/Biz) | ✅ 已登入 Chrome、220 followers   |

### Chrome MCP 必要條件

- Claude in Chrome 擴充功能已安裝且連線
- X：browser 已登入 @taiwandotmd ✅
- Threads：browser 已登入 @taiwandotmd ✅（需先在 IG 登入 taiwandotmd 帳號，Threads 會跟隨 IG session）

### API 必要條件（未來穩定自動化）

- X：Developer Portal 帳號 + App + OAuth 2.0 credentials
- Threads：Meta Developer App + App Review 通過

---

## 方法一：Chrome MCP 瀏覽器自動化

### X 發文流程 ✅ 已測試確認可行（含圖片）

```
步驟（v0.5 許倬雲 spore 自動化升級）：
1. osascript 把方形配圖寫進 macOS 剪貼簿
2. navigate → x.com/home
2.5 ⚠️ HARD GATE: screenshot 確認左下角 account = @taiwandotmd
    （Chrome 預設 active account 可能是 @cheyuwu345 個人帳號）
    若 wrong account → left_click 左下角 ... 按鈕 → dropdown 選 @taiwandotmd → 確認綠勾移動
3. left_click compose 區域（"What's happening?"）
4. key cmd+v → 圖片從剪貼簿貼入 compose（自動附加）
4.5 ⚠️ 圖貼入後 compose textbox 可能 lose focus → 再 left_click compose textbox 一次確保 focus
5. type 孢子文案（含 inline UTM URL for X）
6. **AI pre-ship self-check 6 條 PASS**（見下方 §AI pre-ship self-check）→ left_click Post button（不再 ask 觀察者）
7. 等待「Your post was sent」toast
8. navigate → x.com/taiwandotmd → JS query `a[href*="/taiwandotmd/status/"]` 拿最新 post URL
9. **AI post-ship verify 成品貼文**（見下方 §AI post-ship verify）— navigate post URL + JS read text/image/link
10. **Cleanup tab group**（v0.6）— 完成 verify 後 `tabs_close_mcp` 關本 session 用的 tab；group 內最後一個 tab 關掉後 Chrome 自動移除 group（不要 close 別的 session 的 tab，built-in safety: Chrome MCP `tabs_close_mcp` 只能關 current session's group）
```

**⚠️ 2026-05-23 馬英九 spore 實戰 callout（v0.4 新增）**：

預設 X 登入帳號**可能不是** @taiwandotmd。馬英九 spore 首次自動化實戰發現 Chrome 預設 active account 是哲宇個人 @cheyuwu345，需 manual 切換。Pipeline 之前沒檢查 active account 假設 already at @taiwandotmd 是 silent failure 風險（發到錯誤帳號）。

**新 Hard Gate**：navigate x.com 後第一個動作必須 screenshot 確認左下角帳號 = @taiwandotmd。不是 → click account chooser 切換。

**實測結果（2026-05-18）**：

| 測試項目                 | 結果                                                              |
| ------------------------ | ----------------------------------------------------------------- |
| Compose → type → Post    | ✅ 正常，Post 按鈕自動啟用                                        |
| 中文文案輸入             | ✅ 正常，含 emoji、URL 都沒問題                                   |
| Post button 定位         | ✅ `find("Post button")` 或 `read_page(filter: "interactive")`    |
| 圖片上傳 file_upload     | ❌ Chrome MCP `file_upload` 被拒（file input opacity:0, width:0） |
| **圖片 clipboard paste** | **✅ osascript 寫入剪貼簿 + Cmd+V 貼入成功**                      |
| 字數限制                 | ✅ **不是問題**——帳號有 Premium（藍勾），上限 25,000 字元         |
| 字數計數器               | ✅ 200 中文字 + URL 仍有 51 字元餘額                              |

**字數結論**：taiwandotmd 有 X Premium，孢子 150-300 中文字 + URL 完全不會超限。免費帳號上限 280 字元（中文每字算 2），帶 URL 最多約 123 中文字。

**Post URL 結構**：`https://x.com/taiwandotmd/status/{status_id}`

### Threads 發文流程 ✅ 已測試確認可行（含圖片）

**重大發現**：Threads compose 支援**串文模式**——在同一個 compose modal 裡可以寫主貼 + self-reply，一次「發佈」送出。不需要先發主貼再回去 reply。

```
步驟（v0.5 許倬雲 spore 自動化升級）：
1. osascript 把方形配圖寫進 macOS 剪貼簿
2. navigate → threads.net
3. left_click 頂部「有什麼新鮮事？」compose 區域（不是左側「新串文」）
4. 開啟 compose modal → 確認頂部 label「taiwandotmd」（帳號自動跟 IG session）
4.5 ⚠️ 主題設定：scroll modal up → left_click「社群或主題」label → dropdown 選/輸入「台灣」(per-spore 預設 — Taiwan.md 孢子主題都是台灣)
5. left_click 第一則輸入框
6. key cmd+v → 圖片從剪貼簿貼入（自動附加）
6.5 ⚠️ 圖貼入後 textbox 可能 lose focus → 再 left_click 文字框一次確保 focus
7. type 孢子主貼文案（不含連結）
8. scroll modal down → left_click「新增到串文」label → 出現第二則輸入框 (2/2)
9. type self-reply 連結文案（「完整故事 👉 {UTM URL}」）
10. **AI pre-ship self-check 6 條 PASS**（見下方 §AI pre-ship self-check）→ JS click「發佈」button (`document.querySelectorAll('div[role="dialog"] button').find(b => b.textContent.trim() === '發佈').click()`)
11. 「發佈中......」toast 顯示 → wait 4-5s → 兩則同時發出
12. navigate → threads.com/@taiwandotmd → JS query `a[href*="/@taiwandotmd/post/"]` 拿最新 non-pinned post URL（pinned 通常 ID `DWQVn6BkciM` 排除）
13. **AI post-ship verify 成品貼文**（見下方 §AI post-ship verify）— navigate post URL + JS read text/link
14. **Cleanup tab group**（v0.6）— 同上 X step 10（雙平台順序 ship 完最後一個動作；若 Threads + X 用同 tab group 可在 X step 10 一次 close）
```

**⚠️ 2026-05-23 馬英九 spore 實戰 callout（v0.4 新增）**：

(1) **主題「社群或主題」設定** — 之前 pipeline 完全沒提這步。馬英九 spore 哲宇 explicit callout「社群或主題要放台灣」。Threads 主題影響演算法推送，per-spore 必須設定。Default 「台灣」for Taiwan.md spores。

(2) **圖貼後再 click textbox** — Cmd+V 貼圖後 textbox 會 lose focus，type 文字會落空。必須再 click textbox 一次。X + Threads 雙平台都有這個問題。

(3) **新貼文 scroll past 釘選貼文** — Threads profile 頁面把已釘選貼文放最上面，新發貼文在下面。scroll 過去找最新非釘選 post。

**實測結果（2026-05-18）**：

| 測試項目                 | 結果                                                            |
| ------------------------ | --------------------------------------------------------------- |
| Compose modal 開啟       | ✅ 左側「新串文」按鈕                                           |
| 文案輸入                 | ✅ 中文正常，Threads 自動識別 URL 為連結                        |
| 串文模式（主貼+reply）   | ✅ 「新增到串文」按鈕新增第二則，顯示 1/2、2/2                  |
| URL 預覽卡               | ✅ self-reply 的 URL 自動展開 OG 預覽（taiwan.md OG tags 正確） |
| 貼文選項                 | ✅ 「誰可以回覆和引用」：所有人/粉絲/追蹤者                     |
| 草稿功能                 | ✅ 取消時可選「儲存為草稿」/「不儲存」                          |
| 圖片上傳 file_upload     | ❌ Chrome MCP `file_upload` 被拒（Meta CSP 安全策略）           |
| **圖片 clipboard paste** | **✅ osascript 寫入剪貼簿 + Cmd+V 貼入成功**                    |
| 字數限制                 | ✅ 500 chars/post，孢子 150-300 字安全                          |

**Post URL 結構**：`https://www.threads.com/@taiwandotmd/post/{post_code}`

**Threads compose 元素定位**（自動化用）：

- 主貼文字框：`textbox` placeholder「有什麼新鮮事？」
- 第二則文字框：`textbox` placeholder「傳達更多想法......」
- 圖片上傳（第一則）：`find("附加影音內容")` → ref 附近的 `input[type="file"]`
- 圖片上傳（第二則）：第二個 `input[type="file"]`
- 發佈按鈕：compose modal 右下角
- 新增到串文：compose 區域底部

### Multi-paragraph 中文 paste SOP（v0.7 — JXA NSPasteboard canonical）

> ⚠️ **2026-05-28 哲宇 directive 觸發 canonical 化**：「避免之前出現一堆文自己擠在一起的狀況」+「重發周蕙... 要留意換行，跟格式」→ multi-paragraph 中文 spore 的 paste path 必須走 JXA NSPasteboard，**不准走 pbcopy / osascript classic / execCommand insertText**。

#### 為什麼 pbcopy 不能用（Mac Chinese locale）

Mac 系統 region = Taiwan 時，`pbcopy` 跟 `pbpaste` 用系統預設文字編碼（Big5）而非 UTF-8：

```bash
# ❌ 失敗模式（UTF-8 file → pbcopy → clipboard 變 Big5 garbage）
cat /tmp/spore-text-utf8.txt | pbcopy
pbpaste | xxd | head -2
# 顯示 a741 aabe ... (Big5)，不是預期的 e4bd a0 ... (UTF-8 「你」)
# Cmd+V 貼到 Chrome → 中文字壞 / 0 bytes / mojibake

# 即使強制 LANG 也沒用（pbcopy 用 Cocoa NSStringEncoding 不看 env）
LANG=en_US.UTF-8 LC_ALL=en_US.UTF-8 pbcopy < /tmp/spore-text-utf8.txt  # 仍 Big5
```

#### 為什麼 osascript classic 不能用

```bash
# ❌ AppleScript runtime 把 NSString 轉系統預設編碼（Big5）寫 clipboard
osascript -e 'set the clipboard to (read POSIX file "/tmp/spore.txt" as «class utf8»)'
# 讀檔 as utf8 OK 但 set clipboard 經 AppleScript runtime → Big5 corruption
```

#### 為什麼 execCommand insertText 不能用

```javascript
// ❌ X / Threads 用 ProseMirror contenteditable，insertText 路徑跟 paste handler 不同
const tb = document.querySelector('[data-testid="tweetTextarea_0"]');
tb.focus();
document.execCommand('insertText', false, 'para1\n\npara2\n\npara3');
// ProseMirror 把 \n\n 當 literal 字元 collapse 成單塊 prose
// + URL auto-link 重複觸發（觀察到 6× URL duplication）
// + 失去 paragraph block 結構
```

#### ✅ JXA NSPasteboard UTF-8 — canonical SOP

唯一 reliable path：用 JavaScript for Automation (JXA) 直接呼叫 `NSPasteboard.setStringForType('public.utf8-plain-text')`，繞過 AppleScript runtime + pbcopy 編碼層：

```bash
# 1. 把 spore 文案寫到 temp file（heredoc / Write tool）
cat > /tmp/spore-text.txt <<'TEXT'
你知道嗎？🎤

{故事段落 1}

{故事段落 2}

{故事段落 3}

{故事段落 4}

{故事段落 5}

完整故事 👉 https://taiwan.md/.../?utm_source=x&utm_medium=spore&utm_campaign=s{N}
TEXT

# 2. JXA NSPasteboard write UTF-8（取代 pbcopy）
osascript -l JavaScript <<'JXAEND'
ObjC.import('Foundation');
ObjC.import('AppKit');
var nsstr = $.NSString.stringWithContentsOfFileEncodingError(
  '/tmp/spore-text.txt',
  $.NSUTF8StringEncoding,
  null
);
var pb = $.NSPasteboard.generalPasteboard;
pb.clearContents;
pb.setStringForType(nsstr, 'public.utf8-plain-text');
"ok"
JXAEND

# 3. Chrome MCP click textbox + Cmd+V — X/Threads paste handler 正確分段
```

**為什麼 JXA work**：

- `NSPasteboard.setStringForType(nsstr, 'public.utf8-plain-text')` 直接把 NSString 寫入 pasteboard 的 UTF-8 plain-text type，**不經 AppleScript runtime 編碼轉換**
- Chrome 讀 NSPasteboard 拿到 UTF-8 bytes（不走 pbpaste 路徑）
- X / Threads paste handler 收到 UTF-8 text with `\n\n` → 正確 split 成 ProseMirror 段落 block + visual blank line spacing

**驗證**：用 `pbpaste | wc -m` 不準（pbpaste 也走 Big5 re-encode）。真正 verify 是 Cmd+V 進 X/Threads compose 看顯示效果。

**Image clipboard 兼容**：osascript PNGf class（圖片 clipboard）跟 JXA `public.utf8-plain-text` 互斥 — 一次只能存一種 type。SOP：圖片 paste 完後再 JXA write text + Cmd+V text。

```bash
# Image first
osascript -e 'set the clipboard to (read (POSIX file "/path/to/image.png") as «class PNGf»)'
# Chrome MCP click textbox + Cmd+V → image attached

# Then text (overwrite clipboard)
osascript -l JavaScript -e '... NSPasteboard.setStringForType ...'
# Chrome MCP click textbox + Cmd+V → text inserted with proper paragraph breaks
```

#### Clipboard cross-chat-input state warning（v0.7）

⚠️ 哲宇可能在 mid-session paste 範例文 / 別的內容到 Telegram / chat-input，**取代 AI 寫到 clipboard 的內容**。下次 Cmd+V 不會貼到原本的圖片 / 文字。

**SOP**：每次 Cmd+V 前**立即重新寫 clipboard**（PNG via osascript / text via JXA），不要 assume clipboard state 跨 turn 穩定。

---

### AI pre-ship self-check（v0.7 — 8 checks，加 format gates）

Click Post / 發佈 **前**，AI 必須在 chat 對 observer 公開 8 條 check item 結果（全 PASS 才 click）。任一 FAIL → stop + report observer，不 click。

| #   | Check                          | 怎麼驗                                                                                                         | Pass 條件                                                                                                           |
| --- | ------------------------------ | -------------------------------------------------------------------------------------------------------------- | ------------------------------------------------------------------------------------------------------------------- |
| 1   | **Prose 跟 blueprint 對齊**    | read_page 或 JS query compose textbox textContent，跟 blueprint v 對比                                         | 字元級對齊（emoji / 全形標點 / 引語 verbatim 都對）                                                                 |
| 2   | **Inline UTM URL 末段**        | JS query compose textbox 含 `utm_source=` + `utm_medium=spore` + `utm_campaign=s{N}` 三段                      | 三段缺一不可 / 平台對應 (threads/x) 對                                                                              |
| 3   | **Image attached**             | JS query `[data-testid="attachments"] img` 或 `[data-testid="tweetPhoto"]` 或 Threads compose 內 image preview | imageCount ≥ 1 + blob URL exists                                                                                    |
| 4   | **帳號正確**                   | screenshot 確認左下角 / modal 頂部 label                                                                       | X = @taiwandotmd（非 @cheyuwu345）/ Threads = taiwandotmd                                                           |
| 5   | **Post / 發佈 button enabled** | JS query button element state                                                                                  | aria-disabled=false / 按鈕視覺非灰色                                                                                |
| 6   | **字數安全**                   | JS query textContent.length                                                                                    | X Premium ≤ 25,000 chars / Threads ≤ 500 chars                                                                      |
| 7   | **段落 block count（v0.7）**   | JS query compose textbox `<div>` / `<p>` block count（ProseMirror block 結構）                                 | **≥ 4 paragraph blocks**（hook + 3 story 最低；4-7 sweet spot per SPORE-WRITING §標準孢子格式）— 防 collapsed state |
| 8   | **Standalone hook（v0.7）**    | JS query compose textbox `firstElementChild.textContent` length                                                | **第一段 ≤ 15 chars**（你知道嗎？{emoji} 獨立短行）— 防 inline hook drift                                           |

**v0.7 新增 check 7 + 8 觸發背景**：5/28 22:30 周蕙 RESHIPPED 第一次嘗試 execCommand insertText 把 \\n\\n collapse 成單塊 prose + URL 6× duplication，哲宇 callout「文字亂七八糟，麥克風表情符號後面也沒斷行」。Check 7 量化「all collapsed」failure mode（單塊 prose = block_count 1 = 直接 abort 重試）。Check 8 enforce 標準格式 hook 獨立第一行（[SPORE-WRITING.md §標準孢子格式](../factory/SPORE-WRITING.md) canonical）。

**Check 7 JS verify 範例**：

```javascript
// X ProseMirror
(() => {
  const tb = document.querySelector('[data-testid="tweetTextarea_0"]');
  if (!tb) return { ok: false };
  // X ProseMirror uses <div> blocks; count direct children with text
  const blocks = Array.from(tb.querySelectorAll(':scope > div')).filter(
    (d) => d.textContent.trim().length > 0,
  );
  return { block_count: blocks.length, pass: blocks.length >= 4 };
})();

// Threads compose textbox
(() => {
  const tb = document.querySelector('[contenteditable="true"][role="textbox"]');
  if (!tb) return { ok: false };
  // Threads uses <p> tags
  const blocks = Array.from(tb.querySelectorAll('p')).filter(
    (p) => p.textContent.trim().length > 0,
  );
  return { block_count: blocks.length, pass: blocks.length >= 4 };
})();
```

**Check 8 JS verify 範例**：

```javascript
(() => {
  const tb = document.querySelector(
    '[data-testid="tweetTextarea_0"], [contenteditable="true"][role="textbox"]',
  );
  if (!tb) return { ok: false };
  const firstBlock = tb.firstElementChild;
  const firstText = firstBlock?.textContent.trim() || '';
  return {
    first_len: firstText.length,
    first_preview: firstText,
    pass:
      firstText.length <= 15 &&
      /^(你知道嗎|欸|身為|想像|當你|『)/.test(firstText),
  };
})();
```

**Fail handling**：

- Check 7 fail（block_count < 4）→ collapsed state，**不 click Post**。Discard compose draft → 重新 JXA NSPasteboard write + Cmd+V。
- Check 8 fail（first_len > 15 or no hook prefix）→ hook inline drift。Discard 或修補 blueprint 後重 paste。

**v0.5 → v0.7 操作不變**：報告 8 條 check 結果給 observer（chat 顯示 ✅ 表 + 短描述），完成立即 click Post／發佈，不等 observer 回覆。如果 observer 想介入可以 in-chat「先停 / 改 X / 取消」，但 default 是不問。

**為什麼 8 條夠**：SPORE-PIPELINE Stage 1-3 已 5 層 hard gate（品質三層 / 事實藍圖 / 紀實煽情閘 / Hook Blueprint / §11 prose-health + spore-writing plugin Rule #14 v2 + v3 #14.A #14.B），但 plugin 跑在 **blueprint file**，不跑在 **compose textbox**。Check 7 + 8 是 **物理 render 層**最後驗 paragraph block 結構保留 + hook standalone 狀態 — 補 SPORE-PIPELINE Stage 3 plugin 無法覆蓋的 paste/render 邊界。

### AI post-ship verify（v0.5 — 取代 human review）

Click Post / 發佈 **後**，AI 必須 navigate 到剛發佈的 post URL + JS read 成品內容，跟 blueprint 對比，全 PASS 才結束 SHIP stage。任一 FAIL → 立即 report observer（不沉默 silent ship）。

**Step 1: 取得 post URL**

```javascript
// X
Array.from(document.querySelectorAll('a[href*="/taiwandotmd/status/"]'))
  .map((a) => a.href)
  .filter((v, i, arr) => arr.indexOf(v) === i)[0]; // 第一個 = 最新

// Threads（排除 pinned post）
Array.from(document.querySelectorAll('a[href*="/@taiwandotmd/post/"]'))
  .map((a) => a.href)
  .filter((h) => !h.includes('DWQVn6BkciM') && !h.includes('/media'))[0]; // 排除 pinned + media variant
```

**Step 2: navigate 到 post URL + JS read 5 條 verify**

```javascript
// X 範例
(() => {
  const article = document.querySelector('article[data-testid="tweet"]');
  if (!article) return 'tweet not loaded';
  const text =
    article.querySelector('[data-testid="tweetText"]')?.textContent || '';
  const imgs = article.querySelectorAll('[data-testid="tweetPhoto"] img');
  const links = Array.from(article.querySelectorAll('a[href]')).map(
    (a) => a.href,
  );
  return {
    textLen: text.length,
    textHasHook: text.includes('{blueprint hook 開場 key phrase}'),
    textHasQuote: text.includes('{blueprint verbatim quote}'),
    textHasCloseLine: text.includes('{blueprint 結尾 icon}'),
    imageCount: imgs.length,
    hasShortener: links.some((l) => l.includes('t.co')), // X 把 taiwan.md UTM 包成 t.co
  };
})();
```

**Step 3: 6 條 PASS 條件（v0.7 加 #6 paragraph break preservation）**

| #   | Check                               | Pass 條件                                                                                                                                                                                                                                    |
| --- | ----------------------------------- | -------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| 1   | **textHasHook**                     | blueprint 開場 hook key phrase 在成品 prose 內 ✅                                                                                                                                                                                            |
| 2   | **textHasQuote**                    | blueprint 核心 verbatim 引語在成品 prose 內 ✅                                                                                                                                                                                               |
| 3   | **textHasCloseLine**                | blueprint 結尾 icon / phrase 在成品 prose 內 ✅                                                                                                                                                                                              |
| 4   | **imageCount ≥ 1**                  | post 有 attached image ✅                                                                                                                                                                                                                    |
| 5   | **UTM URL 留痕**                    | X = t.co shortener wraps original UTM ✅ / Threads = l.threads.com wrapper 含 UTM redirect / 或直接 taiwan.md href 包含 utm_campaign=s{N}                                                                                                    |
| 6   | **段落 break preservation（v0.7）** | **X**: tweet `[data-testid="tweetText"]` textContent split('\\n').length ≥ 4 ✅<br>**Threads**: og:description (meta tag) split('\\n\\n').length ≥ 4 ✅ — 防「all collapsed」failure mode rendered output（pre-ship 7 漏掉的 backup verify） |

**v0.7 新增 check 6 觸發背景**：5/28 周蕙 RESHIPPED 撞 X compose execCommand insertText \\n\\n collapse bug，pre-ship check 7 + 8 是 compose 層 verify，但 X 有時 paste 進 compose 看起來分段，發出後 rendered 卻 collapse（cache layer / template re-render 路徑差異）。Check 6 是最後一道安全網 — 看 production rendered output 是否真的保留段落結構。

**Check 6 JS verify 範例**：

```javascript
// X 成品
(() => {
  const article = document.querySelector('article[data-testid="tweet"]');
  const text =
    article?.querySelector('[data-testid="tweetText"]')?.textContent || '';
  const lineBreaks = text.split('\n').length;
  return {
    text_preview: text.slice(0, 100),
    line_break_count: lineBreaks,
    pass: lineBreaks >= 4, // hook + 3 story minimum
  };
})();

// Threads 成品（用 og:description meta tag，比 visible DOM 可靠）
(() => {
  const og =
    document.querySelector('meta[property="og:description"]')?.content || '';
  const paragraphs = og.split('\n\n').filter((p) => p.trim());
  return {
    og_preview: og.slice(0, 100),
    paragraph_count: paragraphs.length,
    pass: paragraphs.length >= 4,
  };
})();
```

**Check 6 fail handling**：rendered post 已上線但段落 collapsed → **不能修改貼文內容**（X 雖有 1 hr edit window 但內容修改會留 edit history；Threads 不能編輯）→ 報告 observer，由觀察者決定 delete + reship / accept-as-is。**Pre-ship check 7 是上游 gate，check 6 是下游 backup**；理想狀況 check 7 PASS → check 6 自動 PASS。Check 6 FAIL + check 7 PASS = 平台 paste→render path 有 caching layer drift，記 LESSONS-INBOX 升 routine instrumentation。

**v0.5 注意事項**：

- X / Threads 都會把 outbound URL 包 wrapper（X = t.co / Threads = l.threads.com），JS 直接讀 href 可能拿不到 UTM 完整 string。Verify 邏輯應 fallback 到「outbound link exists + wrapper redirect target 應該指向 taiwan.md UTM」(可選 follow redirect verify)
- 成品 post page title (HTML `<title>`) 通常含完整 prose snippet，可作為 textHasHook/Quote/CloseLine 的 fallback verify 路徑
- 任一 FAIL → 立即 report observer，附 post URL + fail item，由 observer 決定 delete / edit / retract / acceptable
- 全 PASS → ✅ 報告 observer SHIP 完成 + 雙平台 URL，進 Stage 5 HARVEST

**v0.5 鐵律**：post-ship verify 是 silent ship 防護網。沒 verify = 等於 fire-and-forget，孢子發出後出問題（content drift / image not attached / wrong account silently shipped）會晚發現。本 verify 5 條讓 SHIP stage 真正 closed-loop。

### Cleanup tab group（v0.6 — 結尾步驟）

Post-ship verify 完成後**必 close** 本 session 用的 tab group。長期累積 idle tab 會佔 browser memory + 視覺干擾哲宇。

**操作**：

```javascript
// 1. 確認當前 group 內 tabs
mcp__Claude_in_Chrome__tabs_context_mcp();
// 回 { availableTabs: [{tabId, title, url}], tabGroupId }

// 2. 關 group 內所有 tabs（通常 spore SHIP 只有 1 tab）
for (tab of availableTabs) {
  mcp__Claude_in_Chrome__tabs_close_mcp({ tabId: tab.tabId });
}
// group 內最後一 tab 關掉後 Chrome 自動移除 group
```

**Built-in safety**：Chrome MCP `tabs_close_mcp` 只能關 **current session's group** 的 tab（per tool doc「Only tabs in this session's group are closable」）。所以「不要關別的 session 控制的」這個 invariant 由工具層 enforce — 即使 tabId 寫錯也不會誤關別的 session 的 tab，會回 tool error。

**例外情境**（不關）：

- 觀察者 in-chat directive「先留著」/「下次 session 還要看」→ skip cleanup
- Multi-step task 中段需要切回 browser 的場景（rare for spore SHIP，但 maintainer PR triage 可能）→ skip cleanup
- 觀察者 chat 訊息表示要繼續用 browser → skip cleanup

**鐵律觸發背景**（v0.6，2026-05-23 哲宇 directive）：「使用完瀏覽器 tab 之後要記得關掉，關掉剛使用的那個群組（不要關別的 session 控制的）」。Spore SHIP 完成 + verify 完 = session 對 browser 的需求結束，主動 cleanup 是 hygiene 不是 optional。

### 圖片上傳：osascript clipboard paste ✅ 已解決

Chrome MCP 的 `file_upload` 無法操作兩個平台的隱藏 file input（CSP 安全限制），但 **clipboard paste 路線完全繞過這個限制**。

| 平台    | file_upload（file input） | clipboard paste（osascript + Cmd+V） |
| ------- | ------------------------- | ------------------------------------ |
| X       | ❌ "Not allowed"          | ✅ 圖片正確貼入 compose              |
| Threads | ❌ "Not allowed"          | ✅ 圖片正確貼入 compose              |

**原理**：`file_upload` 走 file input element 觸發（被平台 CSP 擋），clipboard paste 走瀏覽器 paste event handler（平台接受）。兩條路徑在安全模型裡是不同的。

**osascript 指令**（把 PNG 圖片資料寫入 macOS 剪貼簿）：

```bash
osascript -e 'set the clipboard to (read (POSIX file "/absolute/path/to/image.png") as «class PNGf»)'
```

**注意事項**：

- 路徑必須是絕對路徑
- `«class PNGf»` 把檔案內容當作 PNG 圖片資料放入剪貼簿（而非檔案參考）
- Finder Cmd+C 複製的是檔案參考（file reference），不是圖片 data——瀏覽器收到檔案參考會貼成螢幕截圖或不被接受
- osascript 方式在 Bash tool 裡直接執行，不需要開 Finder
- 此方法僅適用於 macOS（osascript 是 AppleScript）

---

## 方法二：API 自動化

### X API（twitter-api-v2）

**費用**：Pay-per-use

- 文字 tweet：$0.015/則
- 含 URL tweet：$0.20/則
- Media upload：v1.1 chunked（OAuth 1.0a，免費但需 elevated access）

**設定步驟**：

1. developer.x.com → 註冊 developer account
2. 建立 Project + App
3. 設定 OAuth 2.0 (PKCE) — User Authentication Settings
4. 記下 Client ID + Client Secret
5. 設定 callback URL（可用 `http://localhost:3000/callback`）

**Node.js 範例**：

```javascript
import { TwitterApi } from 'twitter-api-v2';

const client = new TwitterApi({
  appKey: process.env.X_API_KEY,
  appSecret: process.env.X_API_SECRET,
  accessToken: process.env.X_ACCESS_TOKEN,
  accessSecret: process.env.X_ACCESS_SECRET,
});

// 發文
const { data } = await client.v2.tweet('孢子文案 + URL');
console.log(`Posted: https://x.com/taiwandotmd/status/${data.id}`);

// 帶圖發文
const mediaId = await client.v1.uploadMedia('./spore-image.png');
await client.v2.tweet({ text: '孢子文案', media: { media_ids: [mediaId] } });
```

**Python 範例（tweepy）**：

```python
import tweepy

client = tweepy.Client(
    consumer_key=os.environ['X_API_KEY'],
    consumer_secret=os.environ['X_API_SECRET'],
    access_token=os.environ['X_ACCESS_TOKEN'],
    access_token_secret=os.environ['X_ACCESS_SECRET'],
)

response = client.create_tweet(text="孢子文案 + URL")
print(f"Posted: https://x.com/taiwandotmd/status/{response.data['id']}")
```

### Threads API（graph.threads.net）

**前置**：

- taiwandotmd IG 必須是 Professional 帳號（已確認是）
- 需建立 Meta Developer App
- 需通過 App Review（`threads_basic`, `threads_content_publish` permissions）
- Dev mode 可先測自己帳號（不需 Review）

**設定步驟**：

1. developers.facebook.com → 建立 App（Business type）
2. Add Product → Threads API
3. Generate User Token（需 IG 帳號授權）
4. Dev mode 下可直接測試 publish

**兩步驟 container 模型**：

```bash
# Step 1: 建立 container
curl -X POST "https://graph.threads.net/v1.0/me/threads" \
  -d "media_type=TEXT" \
  -d "text=孢子主貼文案" \
  -d "access_token=$THREADS_TOKEN"
# → { "id": "container_id" }

# Step 2: 發佈
curl -X POST "https://graph.threads.net/v1.0/me/threads_publish" \
  -d "creation_id=container_id" \
  -d "access_token=$THREADS_TOKEN"
# → { "id": "post_id" }

# Step 3: Self-reply（reply_to_id = 剛發的 post_id）
curl -X POST "https://graph.threads.net/v1.0/me/threads" \
  -d "media_type=TEXT" \
  -d "text=完整故事 👉 URL" \
  -d "reply_to_id=post_id" \
  -d "access_token=$THREADS_TOKEN"
# → container for reply

curl -X POST "https://graph.threads.net/v1.0/me/threads_publish" \
  -d "creation_id=reply_container_id" \
  -d "access_token=$THREADS_TOKEN"
```

**帶圖**：

```bash
curl -X POST "https://graph.threads.net/v1.0/me/threads" \
  -d "media_type=IMAGE" \
  -d "image_url=https://taiwan.md/spore-images/xxx.png" \
  -d "text=孢子文案" \
  -d "access_token=$THREADS_TOKEN"
```

注意：`image_url` 必須是公開可訪問的 URL（不能是 local file）。taiwan.md 的 spore-images 部署後即是公開 URL。

**限制**：

- 250 posts / 24hr
- 500 chars / post
- 圖片需公開 URL
- Rate limit: 250 API calls / user / hour

---

## 整合流程（Chrome MCP 版）

完整的從孢子到發文的 end-to-end 流程：

```
1. SPORE-PIPELINE Stage 4 SHIP 交付：
   - 文案（中文 150-300 字）
   - Threads UTM URL: taiwan.md/.../?utm_source=threads&utm_medium=spore&utm_campaign=s{N}
   - X UTM URL: taiwan.md/.../?utm_source=x&utm_medium=spore&utm_campaign=s{N+1}
   - 配圖（landscape 1600×900 / square 1080×1080）

2. Platform allocation 已決定（per SPORE-PIPELINE §Platform allocation）

3. 觀察者確認文案 + 平台選擇

4. 執行發文（Chrome MCP）：

   a. 圖片準備（共用）：
      - osascript 把 square 配圖寫入剪貼簿
        `osascript -e 'set the clipboard to (read (POSIX file "{abs_path}") as «class PNGf»)'`

   b. IF X：
      - navigate → x.com/home
      - left_click compose 區域
      - key cmd+v → 圖片從剪貼簿貼入
      - type 文案 + inline UTM URL
      - ⚠️ 觀察者確認 → left_click Post
      - navigate → @taiwandotmd profile → 點最新 post → 擷取 URL

   c. IF Threads：
      - navigate → threads.net
      - 點「新串文」→ compose modal
      - left_click 第一則輸入框
      - key cmd+v → 圖片從剪貼簿貼入
      - type 主貼文案（第一則，不含連結）
      - 點「新增到串文」→ 第二則輸入框
      - type self-reply「完整故事 👉 {Threads UTM URL}」
      - ⚠️ 觀察者確認 → 點「發佈」（兩則同時送出）
      - navigate → @taiwandotmd profile → 點最新 post → 擷取 URL

5. 後處理：
   - 記錄到 SPORE-LOG.md（URL 乾淨化：剝掉 query string）
   - 寫回源文章 frontmatter sporeLinks
   - git commit
```

---

## 方法選擇建議

| 需求               | 推薦方法                    | 原因                             |
| ------------------ | --------------------------- | -------------------------------- |
| 立即可用、不需設定 | Chrome MCP + osascript 貼圖 | 零設定，今天就能用，含圖片全自動 |
| 帶圖自動化         | Chrome MCP + osascript 貼圖 | ✅ 已解決——不需要 API            |
| 全自動（無人值守） | API + cron                  | Chrome MCP 需要瀏覽器開啟        |
| 最低成本           | Chrome MCP + osascript      | API 路線 X 每則 $0.015-0.20      |
| Threads self-reply | Chrome MCP 串文模式         | 一次送出主貼 + self-reply        |

**目前推薦**：Chrome MCP + osascript clipboard paste。文字 + 圖片 + URL 全自動，觀察者只需確認後按發佈。零成本、零設定、今天就能用。

---

## 開發優先級

| 優先 | 項目                                   | 前置         | 預估                  |
| ---- | -------------------------------------- | ------------ | --------------------- |
| P0   | ~~重設 taiwandotmd IG 密碼~~           | ~~email~~    | ✅ 已解決             |
| P1   | Chrome MCP 文字發文（雙平台）          | 無（已就緒） | ✅ 已測試             |
| P1   | Chrome MCP 圖片上傳（osascript paste） | 無           | ✅ 已測試（雙平台）   |
| P2   | 第一次實戰走完整流程（下一篇 spore）   | 無           | 下次 /twmd-spore      |
| P3   | X Developer Account 申請（backup）     | 無           | 審核 1-3 天           |
| P3   | Meta Developer App 建立（backup）      | IG 登入      | 設定 1hr + 審核 7-14d |
| P4   | API 自動化 script（X + Threads）       | P3 完成      | 4hr                   |

---

## 安全與治理

- **AI pre-ship self-check + post-ship verify gate (v0.5)**：取代 v0.4 「觀察者 confirm gate」。每次發文前 AI 公開 6 條 check 結果 + 全 PASS 立即 click Post（不等 observer 回覆）；發後 navigate post URL JS read 5 條 verify（hook/quote/close-line/image/UTM 留痕）全 PASS 才結束 SHIP stage。Observer 仍可 in-chat「先停 / 改 X / 取消」介入。對應 MANIFESTO §自主權邊界 spore Post per-spore 自動化 lower threshold（2026-05-23 哲宇 directive）
- **Cleanup tab group (v0.6)**：post-ship verify 完成後必 `tabs_close_mcp` 關本 session 的 tab group（per §Cleanup tab group section）。Built-in safety: tool 只能關 current session's group，不會誤關別 session — 即使 tabId 寫錯也由工具層 enforce
- **不存 credentials 在 repo**：API keys 放 `.env`（gitignored）或系統 keychain
- **Rate limit 遵守**：X 50/day、Threads 250/day，script 內建 counter
- **Dry-run mode**：所有自動化 script 預設 `--dry-run`，加 `--publish` 才真的發
- **回滾**：Threads/X 都支援刪除貼文，但觸及已發生無法收回
- **Threads IG 連動**：登入 IG 帳號 = 自動切換 Threads 帳號，注意不要混用 cheyuwu345 / taiwandotmd

---

## 附錄：平台比較

| 維度                 | X                              | Threads                         |
| -------------------- | ------------------------------ | ------------------------------- |
| **帳號**             | @taiwandotmd（Premium ✓）      | @taiwandotmd（Professional IG） |
| **字數**             | 25,000（Premium）/ 280（免費） | 500 chars                       |
| **孢子適合度**       | ✅ 150-300 字 + URL 沒問題     | ✅ 150-300 字 + URL 沒問題      |
| **Self-reply**       | 不需要（單則含 URL）           | 串文模式（1/2 主貼 + 2/2 URL）  |
| **Compose 方式**     | Home feed 頂部 inline          | Modal popup                     |
| **URL 預覽**         | 自動展開 OG card               | 自動展開 OG card                |
| **圖片 file_upload** | ❌ 被拒（hidden input）        | ❌ 被拒（hidden input）         |
| **圖片 clipboard**   | ✅ osascript + Cmd+V           | ✅ osascript + Cmd+V            |
| **API 費用**         | $0.015-0.20/post               | 免費                            |
| **API 認證**         | OAuth 2.0 PKCE                 | OAuth 2.0 via Instagram         |
| **API 圖片**         | Local file upload（v1.1）      | 公開 URL only                   |
| **Rate limit**       | 50 posts / 24hr                | 250 posts / 24hr                |
| **Post URL**         | x.com/.../status/{id}          | threads.com/...post/{code}      |

---

_v0.6 | 2026-05-23 | 許倬雲 spore finale — 哲宇 directive「使用完瀏覽器 tab 之後要記得關掉，關掉剛使用的那個群組（不要關別的 session 控制的）」→ 新增 §Cleanup tab group 結尾步驟（X step 10 / Threads step 14）+ 安全與治理 補 cleanup gate；built-in safety: Chrome MCP `tabs_close_mcp` 只能關 current session's group enforce 不誤關別 session_
_v0.5 | 2026-05-23 | 許倬雲 spore 首例完整自動化實戰 — 哲宇 directive「不要再問我審核了，改成前你自己檢查（符合我們預計發的內容），然後發出去之後再檢查一次成品貼文，盡量完整自動化」→ §AI pre-ship self-check 6 條 + §AI post-ship verify 5 條取代 human confirm gate / 對應 MANIFESTO §自主權邊界 spore Post per-spore 自動化 lower threshold / SPORE-PIPELINE Stage 4 SHIP §發佈 step 3-4 同步更新（移除「在聊天中呈現給觀察者必須確認 OK」+「觀察者確認 OK 後」改為 AI self-check + click + verify）_
_v0.4 | 2026-05-23 | 馬英九 spore 首次完整實戰：X 帳號自檢必跑 + Threads 主題「社群或主題」per-spore 預設「台灣」+ 圖貼後 type 文案順序鐵律_
_v0.3 | 2026-05-18 | osascript clipboard paste 突破圖片上傳：X ✅ / Threads ✅ 雙平台全自動化（文字+圖片+URL），觀察者只需確認_
_v0.2 | 2026-05-18 | Chrome MCP 雙平台完整實測：X compose ✅ / Threads compose+串文 ✅ / 圖片上傳雙平台 ❌ / X Premium 字數不受限 / Threads 串文一次送出 self-reply_
_v0.1 | 2026-05-17 | 初版：Chrome MCP X 流程實測 + Threads 架構文件 + API 規格整理_
