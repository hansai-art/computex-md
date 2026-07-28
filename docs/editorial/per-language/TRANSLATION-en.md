---
title: 'TRANSLATION-en'
description: '英文翻譯規範 — 用語對照表 + sovereignty-avoid 詞庫 + register + romanization 規則'
type: 'editorial-canonical'
status: 'canonical'
current_version: 'v2.0'
last_updated: 2026-05-25
last_session: '2026-05-25-w1b5-restart'
prior_sessions:
  - '2026-05-24-twmd-translation-audit'
  - '2026-05-25-w1b5-restart'
sister_docs:
  - 'TRANSLATION-ja.md'
  - 'TRANSLATION-ko.md'
  - 'TRANSLATION-es.md'
  - 'TRANSLATION-fr.md'
upstream_canonical:
  - '../EDITORIAL.md'
  - '../TERMINOLOGY.md'
  - '../../pipelines/TRANSLATION-PIPELINE.md'
  - '../../pipelines/SQUEEZE-MODELS-MAX-PIPELINE.md'
research_evidence: '../../../reports/translation-research/en-2026-05-24.md'
audience: 'translator (human + AI)'
---

# TRANSLATION-en — Taiwan.md 英文翻譯規範

> 完整證據與 source citation 見 [reports/translation-research/en-2026-05-24.md](../../../reports/translation-research/en-2026-05-24.md)。本檔是 canonical actionable guide，每次翻譯前載入。

## TL;DR — 5 條最高優先規則

1. **`Taiwan` is the default name in body prose.** Reserve `Republic of China` / `ROC` for legal-precision contexts (treaties, court decisions, pre-1949 history, formal name disambiguation). Both AP and the Global Taiwan Institute style guide follow this pattern. Never use `Chinese Taipei` outside the specific Olympic / APEC / WHA international-organization contexts where Taiwan was forced into the name.

2. **A banned-phrases lint is the single highest-leverage defense against PRC-coded leak.** Top offenders: `Taiwan, China` / `Taiwan, Province of China` / `China's Taiwan` / `mainland China` (uncontextualized) / `renegade province` / `reunification` / `the island` (when used dismissively). Substitute with `Taiwan`, `the PRC` or `China`, `unification`, and `Taiwan` (repeated rather than `the island`).

3. **Personal names use Wade-Giles-derived ROC-official spelling for politicians and historical figures** (`Lee Teng-hui`, `Tsai Ing-wen`, `Lai Ching-te`, `Chiang Ching-kuo`, `Ma Ying-jeou`). These are the spellings the subjects themselves use and how Reuters / AP / BBC / NYT spell them. Hyphenate two-syllable given names with the second syllable lowercase (`Teng-hui`, never `Tenghui` or `Teng-Hui`). For people with established English names (`Audrey Tang`, `Joseph Wu`, `Hsiao Bi-khim`), use the English form on first reference, optionally with the Chinese form in parentheses.

4. **Place names use legacy Wade-Giles / postal romanization for major settlements** (`Taipei`, `Kaohsiung`, `Hsinchu`, `Taichung`, `Tainan`, `Keelung`, `Kinmen`, `Matsu`). These are the entrenched conventions Taiwan's MOFA-EN, tourism bureau, and international media all use. Hanyu Pinyin is correct for newer district / street level when the local government has adopted it (`Xinyi District` in Taipei; Kaohsiung still uses Tongyong for its districts). Never `Taibei`, `Gaoxiong`, `Xinzhu` — those read as PRC-coded.

5. **For Taiwan-specific cultural terms with no clean English equivalent, use the romanization + gloss pattern.** Format: _lurou fan_ (braised pork rice), _Mazu_ (sea goddess), _Tâi-gí_ (the Taiwanese / Hokkien language). Italicize the romanization on first use, romanization alone after. Prefer Tâi-gí / Taiwanese over Hokkien / Min-nan for the language as spoken in Taiwan — `Min-nan` carries Sinocentric framing many native speakers reject.

## 1. 國名 / 地區指稱（必查）

| zh-TW 源詞              | Recommended English                                                         | When to use                                                                                                                                 | Never use                                               | Notes                                                                                        |
| ----------------------- | --------------------------------------------------------------------------- | ------------------------------------------------------------------------------------------------------------------------------------------- | ------------------------------------------------------- | -------------------------------------------------------------------------------------------- |
| 台灣 / 臺灣             | **Taiwan**                                                                  | Default in all body prose, datelines, polity / people / geography / government references.                                                  | —                                                       | Never wrong as default.                                                                      |
| 中華民國                | **Republic of China (ROC)**                                                 | Legal-precision contexts; pre-1949 history when ROC governed the mainland; when distinguishing ROC state from `Taiwan` as cultural entity.  | As default name in casual prose.                        | Reads stiff / pre-2000s in body prose.                                                       |
| 中華民國 (台灣)         | **Republic of China (Taiwan)**                                              | MOFA-style formal first reference in political / diplomatic articles.                                                                       | Body prose after first mention.                         | —                                                                                            |
| 中華台北                | **Chinese Taipei**                                                          | ONLY Olympic / APEC / WHA / WTO contexts where this name was forced on Taiwan. Add scare quotes or `"the name imposed by..."` on first use. | As a name for Taiwan in any other context.              | Coerced compromise, not a neutral label.                                                     |
| 兩岸 / 海峽兩岸         | **cross-Strait** (modifier) / **Cross-Strait relations** (proper-noun-like) | Diplomatic / political framing of the Taiwan-PRC relationship.                                                                              | `cross-strait` (lowercase s is less sovereignty-aware). | Capital S; per GTI / Taiwan-studies academic preference.                                     |
| 台灣海峽                | **Taiwan Strait**                                                           | The body of water. Capitalize both words.                                                                                                   | `Formosa Strait` (historical only).                     | Per Chicago Manual of Style.                                                                 |
| 國家 / 我國 / 本國      | **Taiwan / the country / the nation**                                       | Translate the deictic into the explicit referent.                                                                                           | Leaving as `our country` reads odd to English readers.  | Taiwan IS a country — use the word without scare quotes.                                     |
| 中國大陸                | **China / the PRC / the People's Republic of China**                        | Modern PRC references.                                                                                                                      | `mainland China` uncontextualized.                      | `Mainland China` tacitly endorses PRC framing that Taiwan is non-mainland part of one China. |
| 大陸 (uncontextualized) | **China / the PRC**                                                         | Modern PRC references.                                                                                                                      | `the mainland`.                                         | Same fix as 中國大陸.                                                                        |
| 福爾摩沙                | **Formosa**                                                                 | Pre-1945 historical / literary contexts; proper nouns (Formosa Plastics).                                                                   | Modern references to country / island.                  | Archaic / colonial in 2026 prose.                                                            |

## 2. 人名 romanization 規則

**Default rule**: Use the romanization the person themselves uses. Check official bio, English-language interviews, or government profile.

**System defaults**:

- **Wade-Giles (ROC-official, simplified, no diacritics)** — politicians, historical figures, anyone whose passport follows this convention.
- **Gwoyeu Romatzyh (GR)** — specific cases like `Tsai Ing-wen` and `Ma Ying-jeou` (their given names are GR, not Wade-Giles). Use the form they use.
- **Hanyu Pinyin** — almost never for Taiwanese personal names. OK for mainland figures (Xi Jinping), or if the Taiwanese person explicitly self-spells in Pinyin.
- **Tâi-lô / POJ** — when the person publicly uses a Tâi-gí name (esp. indigenous-identifying figures, some musicians).

**Name order**:

- Family name first for all Chinese-character names: `Lee Teng-hui`, `Tsai Ing-wen`, `Chen Shui-bian`.
- Western order for people with English names: `Audrey Tang`, `Joseph Wu`, `Stan Shih`.
- Second reference: surname only (`Lee`, `Tsai`, `Lai`). For ambiguity (multiple Lees in the same piece), use full name each time.

**Hyphenation**:

- Two-syllable given names: hyphen + lowercase second syllable. `Lee Teng-hui`, `Tsai Ing-wen`, `Chiang Ching-kuo`, `Lai Ching-te`. NEVER `Lee Tenghui` / `Lee TengHui` / `Lee Teng-Hui` / `Lee Teng Hui`.
- One-syllable given names: no hyphen. `Wang Wei`.

**Canonical roster**:

| Chinese              | English                                     | Notes                                                                    |
| -------------------- | ------------------------------------------- | ------------------------------------------------------------------------ |
| 蔡英文               | Tsai Ing-wen                                | GR for given name                                                        |
| 賴清德               | Lai Ching-te                                | —                                                                        |
| 李登輝               | Lee Teng-hui                                | NOT `Li Denghui`                                                         |
| 馬英九               | Ma Ying-jeou                                | GR for given name                                                        |
| 陳水扁               | Chen Shui-bian                              | —                                                                        |
| 蔣中正 / 蔣介石      | Chiang Kai-shek                             | Wade-Giles + Cantonese hybrid; entrenched                                |
| 蔣經國               | Chiang Ching-kuo                            | —                                                                        |
| 唐鳳                 | Audrey Tang                                 | English name; add `(唐鳳)` first mention if needed                       |
| 吳釗燮               | Joseph Wu                                   | English name; add `(Wu Jaushieh)` if needed                              |
| 蕭美琴               | Hsiao Bi-khim                               | She uses family-name-first form                                          |
| 柯文哲               | Ko Wen-je                                   | —                                                                        |
| 張忠謀               | Morris Chang                                | English name; founder of TSMC                                            |
| 黃仁勳               | Jensen Huang                                | English name; NVIDIA CEO                                                 |
| 李安                 | Ang Lee                                     | Western order; director                                                  |
| 侯孝賢               | Hou Hsiao-hsien                             | —                                                                        |
| 楊德昌               | Edward Yang                                 | English name; director                                                   |
| 林懷民               | Lin Hwai-min                                | Cloud Gate founder                                                       |
| 鄧麗君               | Teresa Teng                                 | English name; singer                                                     |
| 張惠妹               | A-mei (Chang Hui-mei)                       | Stage name primary                                                       |
| 阿信 (五月天)        | Ashin                                       | Stage name; add `(陳信宏 Chen Hsin-hung)` in music-focused first mention |
| 安溥 (formerly 張懸) | Anpu (formerly Deserts Chang / Chang Hsuan) | Use current stage name; note prior name biographically                   |

**Indigenous Taiwanese names**: Use the Latin-script romanization the person uses (e.g., `Kawlo Iyun Pacidal`, `Kolas Yotaka`). The 2024 amendments let indigenous Taiwanese register native names in Latin script — reflect this, don't force a Han name. Avoid `aborigines` / `aboriginal`; use `indigenous Taiwanese` or `Taiwan's Indigenous peoples`.

## 3. 地名 romanization

**Major cities** (Wade-Giles / postal — entrenched, what MOFA / tourism / international media use):

| Chinese | English        | Avoid                                 |
| ------- | -------------- | ------------------------------------- |
| 臺北    | **Taipei**     | Taibei                                |
| 高雄    | **Kaohsiung**  | Gaoxiong                              |
| 臺中    | **Taichung**   | Taizhong                              |
| 臺南    | **Tainan**     | —                                     |
| 新竹    | **Hsinchu**    | Xinzhu                                |
| 基隆    | **Keelung**    | Jilong                                |
| 桃園    | **Taoyuan**    | —                                     |
| 嘉義    | **Chiayi**     | Jiayi                                 |
| 宜蘭    | **Yilan**      | I-lan (current Hanyu Pinyin standard) |
| 花蓮    | **Hualien**    | Hualian                               |
| 臺東    | **Taitung**    | Taidong                               |
| 屏東    | **Pingtung**   | Pingdong                              |
| 苗栗    | **Miaoli**     | —                                     |
| 彰化    | **Changhua**   | Zhanghua                              |
| 雲林    | **Yunlin**     | —                                     |
| 南投    | **Nantou**     | —                                     |
| 新北    | **New Taipei** | Xinbei                                |

**Districts** (mixed — inherit parent city's system):

- **Taipei districts** = Hanyu Pinyin: `Xinyi District` (信義), `Da'an District` (大安), `Zhongshan District`, `Wanhua District`, `Shilin District`, `Songshan District`. Avoid older Wade-Giles `Hsinyi`, `Ta-an`, `Shihlin`, `Sungshan` in current content.
- **Kaohsiung districts** = Tongyong Pinyin: `Sinsing District` (新興), `Cianjhen District` (前鎮). Looks unusual but is the official local-government form.
- **Tainan / Taichung** = mixed; check the city government's current English signage.
- **Rule of thumb**: For Taipei use Hanyu Pinyin. For other cities, defer to most recent official local-government romanization.

**Outlying islands**:

| Chinese | English                                           | Avoid                                 |
| ------- | ------------------------------------------------- | ------------------------------------- |
| 金門    | **Kinmen** (or `Quemoy` pre-1990 historical only) | Jinmen, Chinmen                       |
| 馬祖    | **Matsu** (the islands)                           | `Mazu` is the goddess — don't confuse |
| 澎湖    | **Penghu** (or `Pescadores` historical only)      | —                                     |
| 蘭嶼    | **Orchid Island** or **Lanyu**                    | `Lan Yu` (no space)                   |
| 綠島    | **Green Island** or **Ludao**                     | —                                     |
| 龜山島  | **Guishan Island** or **Turtle Island**           | —                                     |

**Mountains and rivers**:

- 玉山 → **Yushan** (tourism: `Mount Jade`)
- 阿里山 → **Alishan**
- 雪山 → **Xueshan** (tourism: `Snow Mountain`)
- 淡水河 → **Tamsui River** (entrenched in tourism / historical) or `Danshui River` (Hanyu Pinyin)
- 濁水溪 → **Zhuoshui River**
- 高屏溪 → **Gaoping River**
- 日月潭 → **Sun Moon Lake** (translate; do not romanize)

## 4. 文化詞彙（romanize + gloss pattern）

**Pattern**: italicized romanization on first mention + parenthetical English gloss. Romanization alone after.

**Food**:

| Chinese  | First mention                                 | Subsequent       | Notes                                                    |
| -------- | --------------------------------------------- | ---------------- | -------------------------------------------------------- |
| 滷肉飯   | _lurou fan_ (braised pork rice)               | _lurou fan_      | Hanyu Pinyin standard in English food writing            |
| 牛肉麵   | _niurou mian_ (beef noodle soup)              | beef noodle soup | English form usually wins after intro                    |
| 珍珠奶茶 | **bubble tea** (also _boba_ / pearl milk tea) | bubble tea       | `boba` US-regional; `pearl milk tea` Taiwanese self-name |
| 鳳梨酥   | **pineapple cake**                            | pineapple cake   | Can add (_fenglisu_) first mention                       |
| 蚵仔煎   | _ô-á-chian_ (oyster omelet)                   | oyster omelet    | Tâi-gí romanization preferred (NOT _kezi jian_)          |
| 鹹酥雞   | _xian su ji_ (Taiwanese popcorn chicken)      | —                | Both forms common                                        |
| 小籠包   | **xiaolongbao** (soup dumplings)              | xiaolongbao      | Naturalized; no italics after intro                      |
| 滷味     | _lu wei_ (braised snacks)                     | _lu wei_         | —                                                        |
| 臭豆腐   | **stinky tofu** (_chou doufu_)                | stinky tofu      | Fully naturalized                                        |

**Sovereignty-preservation move**: prefer Taiwanese-language (Tâi-gí) romanization when the dish has Tâi-gí roots. Many "Chinese food" dishes are specifically Taiwanese.

**Religion / common spaces**:

| Chinese     | English                             | Notes                                                                    |
| ----------- | ----------------------------------- | ------------------------------------------------------------------------ |
| 媽祖        | **Mazu**                            | Sea goddess; NOT `Matsu` (= the islands)                                 |
| 觀音        | **Guanyin**                         | —                                                                        |
| 土地公      | **Earth God** (_tudi gong_)         | Translate                                                                |
| 城隍        | **City God** (_cheng huang_)        | Translate                                                                |
| 關公 / 關帝 | **Guandi** / **Guan Yu**            | Romanize                                                                 |
| 夜市        | **night market**                    | Translate; _yeshi_ only if emphasizing the term itself                   |
| 廟口        | **temple plaza** / **temple front** | Translate; _Miaokou_ only in proper nouns (Keelung Miaokou Night Market) |

**Festivals**:

| Chinese      | English                                       | Notes                                                        |
| ------------ | --------------------------------------------- | ------------------------------------------------------------ |
| 春節         | **Lunar New Year**                            | NOT `Chinese New Year` as default (sovereignty-aware choice) |
| 元宵節       | **Lantern Festival**                          | —                                                            |
| 端午節       | **Dragon Boat Festival**                      | —                                                            |
| 中秋節       | **Mid-Autumn Festival**                       | Also `Moon Festival`                                         |
| 中元節       | **Zhongyuan Festival** / **Ghost Festival**   | `Hungry Ghost Festival` also common                          |
| 鬼月         | **Ghost Month**                               | The whole seventh lunar month                                |
| 清明節       | **Tomb-Sweeping Day** / **Qingming Festival** | —                                                            |
| 雙十節       | **Double Tenth Day** / **National Day**       | Taiwan's national day, Oct 10                                |
| 大甲媽祖遶境 | **Dajia Mazu Pilgrimage**                     | Standard tourism / academic form                             |

**Language naming**:

- 台語 → **Taiwanese** (most common in English) or **Tâi-gí** (self-name, sovereignty-aware). Acceptable: **Taiwanese Hokkien**. AVOID `Min-nan` / `Minnan` (閩 historically meant "barbarian"; Sinocentric), `Southern Min`, `Fukienese`.
- 客家話 → **Hakka**.
- 國語 → **Mandarin** (in Taiwan). Avoid `Chinese` for the spoken language — ambiguous with PRC framing.
- Indigenous languages → use the language name directly (Atayal, Amis, Bunun, Paiwan, etc.).

## 5. 政治 / 歷史 sensitive terms

| Chinese      | English                                                    | Notes                                                                                                                             |
| ------------ | ---------------------------------------------------------- | --------------------------------------------------------------------------------------------------------------------------------- |
| 二二八事件   | **228 Incident** / **February 28 Incident**                | Subsequent: `228` (no hyphen). `228 Massacre` acceptable when emphasizing scale (~28,000 dead).                                   |
| 228 紀念日   | **228 Peace Memorial Day**                                 | The public holiday                                                                                                                |
| 白色恐怖     | **White Terror**                                           | Capitalized, no quote marks. `White Terror (1947–1992)` or `(1949–1992)`                                                          |
| 戒嚴         | **martial law**                                            | Lowercase general; `the Martial Law era` capitalized for the 1949–1987 period                                                     |
| 解嚴         | **the lifting of martial law (1987)**                      | —                                                                                                                                 |
| 民國 (year)  | **convert to Gregorian** in body (民國 38 → 1949)          | If subject itself: `Year 38 of the Republic (1949)`. NEVER bare `ROC 115`.                                                        |
| 本省人       | **_benshengren_** (italicized + gloss)                     | Gloss: `Taiwanese whose families lived under Japanese rule, pre-1945`. `Native Taiwanese` ambiguous with indigenous.              |
| 外省人       | **_waishengren_** (italicized + gloss)                     | Gloss: `Chinese mainlanders who came to Taiwan with the KMT 1945–1949 and their descendants`. `Mainlander` creates PRC-confusion. |
| 原住民       | **indigenous Taiwanese** / **Taiwan's Indigenous peoples** | Capitalize `Indigenous` per international convention. Avoid `aborigines`.                                                         |
| 新住民       | **new immigrants** / **new residents**                     | Post-1990s, mostly SE Asian                                                                                                       |
| 日治時期     | **Japanese colonial period (1895–1945)**                   | Contemporary academic standard                                                                                                    |
| 日據時期     | **Japanese occupation period**                             | KMT-preferred framing; less used now                                                                                              |
| 皇民化       | **_kōminka_** (italicized) / **Imperialization**           | Late-period assimilation                                                                                                          |
| 一個中國原則 | **the PRC's One China principle**                          | Distinguish from US `One China policy` (different things)                                                                         |
| 九二共識     | **1992 Consensus**                                         | —                                                                                                                                 |
| 統一         | **unification**                                            | NOT `reunification`                                                                                                               |
| 獨立         | **independence** (Taiwan independence)                     | —                                                                                                                                 |
| 現狀         | **the status quo**                                         | —                                                                                                                                 |

**Political parties** (full English first use → abbreviation after):

| Chinese    | English                                | Notes                                                                      |
| ---------- | -------------------------------------- | -------------------------------------------------------------------------- |
| 中國國民黨 | **Kuomintang (KMT)**                   | The party uses `Kuomintang` on its own English materials, NOT `Guomindang` |
| 民主進步黨 | **Democratic Progressive Party (DPP)** | —                                                                          |
| 台灣民眾黨 | **Taiwan People's Party (TPP)**        | Ko Wen-je's party                                                          |
| 時代力量   | **New Power Party (NPP)**              | —                                                                          |
| 親民黨     | **People First Party (PFP)**           | —                                                                          |
| 中國共產黨 | **Chinese Communist Party (CCP)**      | NOT `CPC`                                                                  |
| 泛藍       | **Pan-Blue Coalition**                 | —                                                                          |
| 泛綠       | **Pan-Green Coalition**                | —                                                                          |

**Government bodies**: 總統府 → `Office of the President`; 立法院 → `Legislative Yuan`; 行政院 → `Executive Yuan`.

## 6. Sovereignty-avoid lexicon（PRC-coded → 替代）

| PRC-coded (avoid)                                                 | Taiwan-aligned (use)                                                                           |
| ----------------------------------------------------------------- | ---------------------------------------------------------------------------------------------- |
| `Taiwan, China`                                                   | `Taiwan`                                                                                       |
| `Taiwan, Province of China`                                       | `Taiwan` (only legitimate use: when discussing the labeling controversy itself)                |
| `China's Taiwan` / `Chinese Taiwan`                               | `Taiwan`                                                                                       |
| `renegade province`                                               | omit; if quoting PRC: `which Beijing claims as part of its territory`                          |
| `breakaway province`                                              | (same fix)                                                                                     |
| `reunification`                                                   | `unification` (potential future integration); `annexation` (if discussing PRC coercive intent) |
| `peaceful reunification`                                          | quote PRC verbatim if required; never adopt                                                    |
| `mainland China` (uncontextualized)                               | `China` / `the PRC` / `the People's Republic of China`                                         |
| `the mainland` (uncontextualized)                                 | `China` / `the PRC`                                                                            |
| `the island` (as primary referent for Taiwan-as-nation)           | `Taiwan` / `the country`                                                                       |
| `Taiwan authorities` (uncontextualized)                           | `Taiwan's government` / `the Taiwanese government`                                             |
| `leader of Taiwan`                                                | `President of Taiwan` / `Taiwan's President`                                                   |
| `Chinese Taipei` (outside Olympic/APEC/WHA)                       | `Taiwan`                                                                                       |
| `Chinese New Year`                                                | `Lunar New Year`                                                                               |
| `Min-nan` / `Southern Min` (for language in Taiwan)               | `Taiwanese` / `Tâi-gí`                                                                         |
| `Taiwanese aborigines`                                            | `indigenous Taiwanese` / `Taiwan's Indigenous peoples`                                         |
| `Formosa` (modern context)                                        | `Taiwan`                                                                                       |
| `One China` (ambiguous)                                           | distinguish `the PRC's One China principle` vs `US One China policy`                           |
| Scare quotes around `Taiwan` / `country` / `president` / `nation` | straightforward language; no scare quotes                                                      |

**Boilerplate framing — use with care**: prefer Taiwan-first framing over reflexive PRC-claim foregrounding.

- Avoid: `Taiwan, the self-ruled island that China claims as its own,`
- Use: `Taiwan, a democracy of 23 million,` / `Taiwan, an East Asian island nation,`
- Add `China claims` clause only when cross-Strait dimension is the actual subject.

## 7. Register & 風格規則

- **American English** site-wide. `color` not `colour`, `realize` not `realise`, `defense` not `defence`, `center` not `centre`, `traveled` not `travelled`. Rationale: Taiwan's own English pedagogy + Focus Taiwan / Taipei Times / Taiwan News all use American conventions; largest English-reading audience is North American.
- **Oxford comma**: yes. Standard in Chicago Manual, New Yorker, MIT Press, academic journals; unambiguous for translations from Chinese serial structures.
- **Date format**: `May 24, 2026` (American long form) in body; `1947–1987` (en dash, no spaces) for ranges; `the 1990s` (no apostrophe); `the 20th century` (numeric).
- **Capitalization for Taiwan-specific terms**: `White Terror`, `Sunflower Movement`, `228 Incident`, `Cross-Strait relations` (proper-noun-like), `the Martial Law era`, `Indigenous` (per international convention), `Pan-Blue Coalition` / `Pan-Green Coalition`.
- **Italics for romanized Chinese on first mention only**: _lurou fan_, _Tâi-gí_, _benshengren_, _kōminka_. Subsequent uses roman.
- **Voice**: long-form essay tone (Atlantic / Foreign Affairs / LARB register). Active voice predominant. First-person plural `we` sparingly when speaking from inside Taiwanese collective identity.
- **Numbers**: spell out one through nine; numerals for 10+. Always numeral: years, percentages, measurements. Currency: `NT$1,200` (no space).
- **Quotations**: double quotes for direct quotes; single quotes nested. American convention.
- **Names of works**: italicize book titles, films, albums, newspapers. Quote song titles, article titles, chapter titles.

## 8. CI Lint 候選 banned phrases

**Hard-fail (CI gate)**:

1. `Taiwan, China` — whitelist only: articles discussing the labeling controversy itself.
2. `Taiwan, Province of China` — whitelist only: same.
3. `China's Taiwan` / `Chinese Taiwan` — no whitelist.
4. `renegade province` — whitelist only: inside a quoted PRC speaker.
5. `reunification` — whitelist only: inside a direct quote from a PRC source (use editor's note).

**Warning-only**: 6. `mainland China` / `the mainland` (uncontextualized) — flag for human review; allow in quoted material and PRC-internal-context discussions. 7. `the island` (as primary referent for Taiwan) — flag dismissive uses; allow geographic-feature contexts (`Taiwan is the largest island in...`). 8. `Chinese New Year` — flag; allow if specifically discussing PRC's framing or in quoted material. 9. `Chinese Taipei` outside Olympic / APEC / WHA / WTO context — flag for human review. 10. `Min-nan` / `Southern Min` / `Minnan` for the language in Taiwan — flag; suggest `Taiwanese` / `Tâi-gí`.

**Source-string lint** (catches PRC-coded leak from Chinese sources): `中國臺灣`, `中國臺北` in en/\* output → always flag.

**Frontmatter surfaces matter too**: body-only grep misses `description:`, `title:`, `imageAlt:`, `tags:`. The W1 cleanup uncovered a `China's Taiwan Affairs Office` leak inside a frontmatter `description:` field that survived two prior audits because every grep had been scoped `^[^#]*"China's Taiwan"` against body lines. CI lint must inspect the full file or run a separate frontmatter pass on every YAML scalar.

## 10. Per-instance judgment framework (audit-before-edit)

When you encounter a candidate pattern in this guide (e.g., `Min-nan`, `mainland China`, `Chinese New Year`, `Lee Tenghui`), apply this 5-step loop before changing anything. The §1–§8 tables tell you the target; §10 tells you how to land it without collateral damage.

### Step 1 — AUDIT before EDIT

Always grep the full corpus first. Sample 5–10 occurrences across different files. Counts before and after editing should both be expected — surprise on either side means a category you missed.

```bash
# Always count first
grep -rn 'Chinese New Year' knowledge/en/ | wc -l
# Then sample
grep -rn 'Chinese New Year' knowledge/en/ | shuf -n 8
# Edit, then verify residual
grep -rn 'Chinese New Year' knowledge/en/ | wc -l
```

Never run a blind `sed -i 's/X/Y/g' knowledge/en/**/*.md` on a sovereignty pattern. Even `replace_all` inside a single file should be used only after step 2 returns one category.

### Step 2 — CATEGORIZE each hit

Walk every sampled context against this decision tree:

| Context type                                                                                 | Default action      | Why                                                         |
| -------------------------------------------------------------------------------------------- | ------------------- | ----------------------------------------------------------- |
| Body prose narrative (the author's voice)                                                    | **FIX**             | This is where sovereignty register lives                    |
| Direct attributed quote inside `« »` / `" "` from a PRC speaker / source                     | **PRESERVE**        | Quoting is reporting; flag with editor's note if misleading |
| Direct quote from a Taiwan speaker who chose this word                                       | **PRESERVE**        | Speaker's voice; don't ventriloquize                        |
| Proper noun — person name, org name, publication title, festival name, channel name          | **PRESERVE**        | Names are identifiers, not sovereignty claims               |
| Ethnic group / historical community reference distinct from language reference               | **PRESERVE**        | `Minnan people from Fujian` ≠ `Min-nan language in Taiwan`  |
| Frontmatter `description:` / `title:` / `imageAlt:` / `tags:`                                | **FIX (high prio)** | End-user-visible surface; often the most-cited leak vector  |
| Code block, URL, brand name, ISO label being meta-discussed                                  | **PRESERVE**        | Technical identifier, not editorial voice                   |
| Meta-discussion article about the term / labeling controversy itself                         | **PRESERVE**        | The whole point of the article is to surface the term       |
| Historical event with no Taiwan implication (`German reunification`, `Korean reunification`) | **PRESERVE**        | Different referent; sovereignty rule doesn't apply          |
| Oxford-comma geographical enumeration (`Taiwan, China, Japan, and Korea`)                    | **PRESERVE**        | Comma is list separator, not PRC labeling                   |

Bucket every hit. If a single file mixes categories, you cannot do `replace_all` — you must do per-occurrence Edits with surrounding context for uniqueness.

### Step 3 — JUDGE edge cases against §11 whitelist

If a hit doesn't cleanly fall into any row above, it is an edge case. Check §11 whitelist patterns. If still unresolved, write the case into §15 Open questions and surface to the maintainer rather than guessing.

### Step 4 — APPLY per-file, with context for uniqueness

For multi-meaning patterns, the `old_string` in your Edit must include 1–2 lines of surrounding context so the replacement is unique to that occurrence. Resist the urge to `replace_all` across multiple files at once — that is how false positives ship.

### Step 5 — VERIFY post-edit residual

Re-run the grep. Residual count should match expected (often zero for body prose patterns; non-zero for legitimate proper-noun / meta-article hits that you intentionally preserved). Discrepancy means a missed bucket — go back to step 2.

**Worked example — high-confidence pattern, replace_all safe**:
W2e en cleanup found 16 `Chinese New Year` occurrences in body prose. All sampled hits were narrative references to the festival in Taiwan / Taiwan-diaspora contexts. The English phrase has no other meaning (no person, place, brand, or publication title named `Chinese New Year`), so categorization was unanimous. Per-file `replace_all` was safe. Post-edit residual: 0. Lunar New Year count: 40 → 56.

**Worked example — multi-meaning pattern, per-instance required**:
A hypothetical `Min-nan` audit returns ~59 hits across en/. Sampling reveals:

- ~15 body refs to the language in Taiwan → FIX to `Taiwanese` / `Tâi-gí`
- ~20 historical refs to `Minnan people from Fujian` as ethnic group → PRESERVE (the people are not the language)
- ~10 in the proper noun `Min-nan Wolf PYC` (YouTuber channel) → PRESERVE
- ~8 in quoted academic-linguistics titles → PRESERVE
- ~6 in `Southern Min language family` linguistic-taxonomy contexts → PRESERVE
  Conclusion: no `replace_all` possible. Walk every file manually.

## 11. False-positive whitelist patterns (English-specific)

Catalog of patterns that look like sovereignty-leak hits but are legitimate. Built from W1 + W2e cleanups + cross-language insights.

| Pattern                                                                | Why it's legitimate                                                                                     | Disambiguation cue                                                                                        |
| ---------------------------------------------------------------------- | ------------------------------------------------------------------------------------------------------- | --------------------------------------------------------------------------------------------------------- |
| `Taiwan, China, Japan, and Korea`                                      | Oxford-comma geographical enumeration; China is a peer country in a list                                | Look for ≥1 more country after `China,` — if yes, list; if sentence ends `Taiwan, China.` it is PRC label |
| `Taiwan, Province of China`                                            | Only in articles meta-discussing ISO 3166 / UN labeling controversy                                     | File name contains `labeling` / `standards` / `iso` / `un` discussion                                     |
| `Chinese New Year`                                                     | Inside a meta-article specifically about the festival's name controversy                                | Article title or paragraph is _about_ the naming debate                                                   |
| `Chinese-speaking world` / `Chinese language family`                   | Language-family reference; distinct from PRC framing                                                    | Linguistic / academic context; not political                                                              |
| `Min-nan Wolf PYC`                                                     | YouTuber channel proper noun                                                                            | Capitalized as proper noun; followed by handle or platform                                                |
| `Minnan people` / `Hoklo from Fujian`                                  | Historical ethnic group reference, distinct from language                                               | Talks about _people_ migrating, not a _language_ spoken                                                   |
| `Republic of China`                                                    | Formal legal / treaty / pre-1949 / constitutional context                                               | Document name, treaty reference, year < 1949, or explicit ROC-vs-Taiwan distinction                       |
| `German reunification` / `Korean reunification`                        | Historical event with no Taiwan implication                                                             | Subject is Germany / Korea / Yemen / Vietnam, not Taiwan                                                  |
| `mainland China` (in a direct quote of a PRC speaker, attributed)      | Quoting is reporting; preserve speaker's framing with editor's note if misleading                       | Inside `« »` / `" "` with attribution                                                                     |
| `Beijing's Taiwan Affairs Office`                                      | This IS the recommended fix; not a false positive — listed here so audits don't try to "fix" it further | Already uses `Beijing's` not `China's` — leave it                                                         |
| `the island of Taiwan` (geographic-feature context)                    | Legitimate geographic description; `Taiwan is the largest island in the West Pacific...`                | Sentence is about the physical island, not the polity                                                     |
| `Taipei` as metonym in diplomatic-pair phrasing (`Beijing and Taipei`) | Standard diplomatic convention; reads as parallel to `Washington and Moscow`                            | Appears as pair with another capital, not as substitute for Taiwan-the-country                            |

When in doubt: surface to maintainer (§15), do not silently fix.

## 12. Worked examples library (this session — 2026-05-25)

Concrete fix-vs-preserve cases with reasoning. Each shows pattern audited → hit context → judgment → applied fix or preservation.

**Example 1 — `China's Taiwan Affairs Office` → `Beijing's Taiwan Affairs Office`** (W1, commit `4331614bf`)

- Audited: `grep -rn "China's Taiwan Affairs Office" knowledge/en/` → 5 hits across 4 files, including 1 inside a frontmatter `description:` field
- Judgment: body refs are paraphrased; the office's _de facto_ English name in Reuters / AP / FT coverage is `Beijing's Taiwan Affairs Office`; the frontmatter description hit was an end-user-visible card preview, highest-priority surface
- Applied: 5 in-place edits using surrounding context; verified residual = 0
- Lesson: frontmatter is its own audit pass. Body-only grep would have missed the description-field leak.

**Example 2 — `reunification` → `unification`** (W1, commit `4e7ab6958`)

- Audited: `grep -rn '\breunification\b' knowledge/en/` → 14 hits across 9 files
- Categorized: 2 hits were paraphrased Xi Jinping speech rhetoric and scare-quoted PRC influencer phrasing about Taiwan-China integration → FIX to `unification`. 1 hit was `German reunification` in a comparative-politics article → PRESERVE. 11 hits were inside articles discussing the term itself or quoting PRC sources verbatim → PRESERVE with editor's-note context already present.
- Applied: 2 edits; preserved 12
- Lesson: even within one banned-list term, the majority of hits can be legitimate. Sample-and-categorize before editing.

**Example 3 — `Chinese New Year` → `Lunar New Year`** (W2e, commit `1a9894f2c`)

- Audited: 16 hits, all body prose narrative across diverse files (food articles, festival articles, diaspora articles)
- Categorized: 0 false positives possible — the English phrase has no other meaning
- Applied: per-file `replace_all` was safe. Lunar New Year count: 40 → 56 (consistent before / after)
- Lesson: high-confidence patterns where every hit falls in one bucket allow batch `replace_all`. Most patterns are not this clean.

**Example 4 — `taiwans-labeling-in-international-standards.md` whitelist** (W1 audit)

- Audited: `grep -rn 'Taiwan, Province of China' knowledge/en/` → 4 hits
- Categorized: all 4 in the meta-discussion article whose whole point is to surface ISO 3166's PRC-pressured label. The article cannot exist without quoting the label.
- Applied: zero edits. Added file path to §11 whitelist row.
- Lesson: meta-articles about a controversial term must quote the term; the whitelist exists for them.

**Example 5 — French `Li Jiayi` person-name false positive** (cross-lang, fr cleanup)

- Audited: `grep -rn 'Jiayi' knowledge/fr/` while fixing 嘉義 toponym from Pinyin `Jiayi` → Wade-Giles `Chiayi`
- Categorized: most hits were the city; 2 hits were the person `Li Jiayi` (李嘉義, an unrelated Taiwanese figure whose given name romanizes the same way)
- Applied: per-occurrence Edits for the toponym; preserved person-name occurrences
- Lesson: even unambiguous-looking romanization fixes can hit person names. Always sample.

**Example 6 — `Festival de Zhongyuan de Jilong`** (cross-lang, fr)

- Audited: `Jilong` while fixing 基隆 → `Keelung`
- Categorized: hit appears inside the proper named festival `Festival de Zhongyuan de Jilong` (Keelung Mid-Yuan / Ghost Festival in Spanish-language tourism context)
- Applied: PRESERVED. Festival's official multilingual marketing uses the Pinyin form for this composite name
- Lesson: festival names are proper nouns; check official tourism / cultural-affairs office signage before "fixing"

**Example 7 — `mont Jilongtou` compound historical name** (cross-lang, fr)

- Audited: same `Jilong` audit
- Categorized: hit is inside the compound historical name `mont Jilongtou` (基隆頭山) with explicit French-text disambiguation in the same paragraph
- Applied: PRESERVED
- Lesson: compound historical / geological / archaeological names often carry their own romanization tradition independent of the modern city's name

**Example 8 — Korean `대북부` false positive** (cross-lang, ko)

- Audited: `grep -rn '대북' knowledge/ko/` while reviewing `대북` (Sino-Korean for 台北 Taipei) residuals
- Categorized: several hits were inside `대북부` (大北部, Greater Northern Region of Taiwan), a distinct compound noun
- Applied: PRESERVED. The 4-character substring match is a regex artifact, not a sovereignty hit
- Lesson: short romanization fragments (`대북`, `Jilong`, `Min`) are high false-positive risk. Always require word-boundary anchors or surrounding-context Edits.

**Example 9 — Book and film title transliteration** (cross-lang, applies to en too)

- Pattern: Bai Xianyong's 《台北人》 → `Taibei Ren` (NOT `Taipei People`) in academic / translation contexts
- Reasoning: book titles transliterate the original sound, not the conventional toponym. `Taibei Ren` follows the same logic as translating 《紅樓夢》 as `Hong Lou Meng`, not `Dream of the Red Chamber`, in citation contexts
- Applied: PRESERVED `Taibei Ren` in literary citation contexts; use English gloss in body
- Lesson: literary / film / album titles follow a different romanization rule than place names. Check whether the work has an established English title in the publication.

**Example 10 — Audit-tooling collision** (W1 process lesson)

- Symptom: `git status` showed unrelated `knowledge/_translation-status.json` changes alongside the sovereignty cleanup
- Cause: a parallel `twmd-refresh-daily` cron routine was writing dashboard JSON while the manual cleanup session was running. Directory-level `git add knowledge/` would have grabbed both
- Applied: per-file `git add knowledge/en/path/to/file.md` only; the cron's WIP was left untracked for its own session to commit
- Lesson: in this repo, manual + cron sessions are concurrent. Always stage by file, never by directory.

## 13. Translator's "Taiwan-first" mental model

Before any specific rule fires, the lens you carry into the file determines whether the rule even gets considered. This section is the philosophical posture — read once per session, then trust it to bias your judgment.

**Taiwan is the sovereign subject, not the object of someone else's geography.**
The reader meeting Taiwan in your translation should encounter a country that simply _is_ — with elections, a president, a foreign ministry, a passport, a flag, a constitutional order, a national football team, an indigenous-language revival, a diasporic literature. The PRC's claim is a fact about the PRC, not a definitional fact about Taiwan. Frame accordingly.

**Reader-default assumption is country, not exception.**
Write as if your reader assumes Taiwan is a country unless the article is explicitly about diplomatic non-recognition. Reflexively prepending `the self-ruled island that China claims` to every first reference (as Reuters / AP boilerplate does) is journalistic hedging that Taiwan.md does not owe. Add the cross-Strait clause only when cross-Strait dimension is the actual subject of the sentence.

**When in doubt, ask what Taiwan's own English-language voice would say.**
The reference set is: Taiwan MOFA-EN, Focus Taiwan, Taipei Times, Taiwan News, the Office of the President's English site, the Global Taiwan Institute, the Taiwan Studies programs at Nottingham / Columbia / Stanford. These are sovereignty-aware sources written by people who live in Taiwan or study it professionally. If they say `Taiwan`, you say `Taiwan`. If they say `Beijing's Taiwan Affairs Office`, you say `Beijing's Taiwan Affairs Office`. They are right; the PRC's preferred phrasing is not.

**Sovereignty preservation outranks English-stylistic smoothness.**
English prose habit suggests pronoun / metonym variation to avoid repetition — `Taiwan` → `the island` → `Taipei` → `the country`. Resist `the island` as metonym for Taiwan-as-nation; it diminishes a country to a geographic feature. Resist `Taipei` as metonym for `Taiwan's government` in body prose where the reader could plausibly confuse city and country. Repeating `Taiwan` reads slightly less elegant than varying it — but elegance has never silenced anyone, and Taiwan's name is what's at stake.

**You are voice-of-Taiwan in English, not a neutral observer between two parties.**
Taiwan.md is not Reuters. Reuters has the institutional reason to hedge; Taiwan.md does not. The lens is: a thoughtful Taiwanese person, fluent in English, explaining her country to a global audience. She does not adopt the framing of the country that wants to erase hers, and she does not pretend the framing question is symmetric. She is also not a propagandist — she sources her claims, quotes critics accurately, and notes contested history. But she does not begin every sentence by establishing that her country exists.

**Per [MANIFESTO §主權的巴別塔](../../semiont/MANIFESTO.md)**: the multilingual projection is sovereignty preservation infrastructure — letting Taiwan's first-person voice exist in every language, bypassing intermediary layers that would otherwise choose silence. Every English sentence you write is one more place this voice lives.

## 14. Process discipline (commit / tooling hygiene)

Translation work in this repo runs concurrently with `twmd-refresh-daily`, `twmd-maintainer-daily`, `twmd-babel`, and human contributors. The mechanical hygiene below is what keeps sovereignty cleanup from colliding with parallel work. Lessons from the 2026-05-25 W1b5 restart incident.

**Use `git worktree` isolation for batch sovereignty cleanup.**

```bash
git worktree add ../taiwan-md-immune main
cd ../taiwan-md-immune
# do all sovereignty work here
```

A dedicated worktree prevents `lint-staged` backup collision with parallel cron routines writing to the primary working tree. The immune-system worktree convention (`taiwan-md-immune`) signals to other sessions that this directory is doing sovereignty work and should not be cron-touched.

**File-level `git add`, never directory-level.**

- Right: `git add knowledge/en/Food/lurou-fan.md docs/editorial/per-language/TRANSLATION-en.md`
- Wrong: `git add knowledge/en/` (grabs cron WIP)
- Wrong: `git add -A` (grabs everything, including `_translation-status.json` writes from parallel routines)

Directory-level adds are the single most common cause of "the commit included files I didn't touch" in this repo. The rule is no exceptions.

**Audit before edit, verify after commit.**
Both grep counts should change as expected. If you fixed 16 `Chinese New Year` occurrences, the post-commit grep should show residual = 0 in body prose (whitelist hits in meta-articles excluded). If the residual is 3 when you expected 0, you missed a category — go back to §10 step 2 before pushing.

**Referential integrity between commit message and content is your discipline alone.**
Git enforces nothing here. If your commit message says "16 fixes" but the diff shows 14, no hook will catch it. Read your own diff before `git commit`, every time. The commit message is a permanent claim about the change; making it accurate is part of the change.

**Sub-agent prompts must inline §1 + §2 + §6 + the relevant §10/§11/§12 rows.**
Per [SQUEEZE-MODELS-MAX-PIPELINE.md §Z2.0](../../pipelines/SQUEEZE-MODELS-MAX-PIPELINE.md), pointer-only references to this guide fail in practice — sub-agents do not reliably load referenced files even when instructed. The backend prompt must contain the actual tables. For sovereignty-cleanup sub-agents specifically, include §10 decision tree + §11 whitelist + 1–2 §12 worked examples as anti-examples (per the `feedback_subagent_anti_example_works.md` finding: pattern-matchers learn from cases, not rules).

**Commit message template for sovereignty cleanup**:

```
🧬 [editorial] en: <pattern> sovereignty cleanup — N fixes across M files

- AUDIT: grep returned X hits, sampled Y
- CATEGORIZED: Z body-prose FIX, W preserved (proper nouns / quotes / meta)
- APPLIED: per-file Edits with surrounding context
- VERIFIED: post-edit residual = R (matches expected)
- WHITELIST additions to TRANSLATION-en.md §11: <list or none>
```

The shape encodes the §10 5-step loop; future audits can replay your reasoning.

## 15. Open questions

1. **`mainland China` in direct quotes of PRC speakers** — allow with editor's note flag, or strip-and-paraphrase? Recommendation: allow in quoted material; flag if it would mislead.
2. **`Chinese New Year` retrofit** — existing en/\* articles may have hundreds of uses. Mass-replace to `Lunar New Year`, or per-article review? Recommendation: mass-PR with per-article diff review.
3. **`Indigenous` capitalization** — enforce site-wide per international convention? Pending observer call.
4. **`Quemoy` vs `Kinmen` in 1950s-crisis articles** — use `Kinmen (formerly Quemoy)` on first mention, or `Quemoy` throughout for period accuracy? Pending observer call.
5. **Tongyong vs Hanyu Pinyin for Kaohsiung districts** — mirror official Tongyong signage (`Sinsing`, `Cianjhen`) or default to Hanyu Pinyin for consistency? Recommendation: mirror official signage with parenthetical Han characters.

---

_v2.0 | 2026-05-25 — session 2026-05-25-w1b5-restart. Adds §10 per-instance judgment framework, §11 false-positive whitelist, §12 worked examples library (W1 sovereignty + W2e Lunar New Year cleanups, cross-language insights), §13 Taiwan-first mental model, §14 process discipline. §9 Open questions renamed §15. Evidence: W1 commits `4331614bf` + `4e7ab6958`, W2e commit `1a9894f2c`, cross-lang fr/ko cleanup notes._
_v1.0 | 2026-05-24 — derived from translation conventions audit. Evidence base in `reports/translation-research/en-2026-05-24.md`._
