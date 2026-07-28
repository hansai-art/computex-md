---
title: 'TRANSLATION-ko'
description: '韓文翻譯規範 — 대만 vs 타이완 SSOT + sovereignty-avoid 詞庫 + 한자 → 한글 romanization 規則 + 판단 framework + 화이트리스트 + worked examples + 번역자 mental model'
type: 'editorial-canonical'
status: 'canonical'
current_version: 'v2.0'
last_updated: 2026-05-25
last_session: '2026-05-25-twmd-translation-ko-augment'
sister_docs:
  - 'TRANSLATION-en.md'
  - 'TRANSLATION-ja.md'
  - 'TRANSLATION-es.md'
  - 'TRANSLATION-fr.md'
upstream_canonical:
  - '../EDITORIAL.md'
  - '../TERMINOLOGY.md'
  - '../../pipelines/TRANSLATION-PIPELINE.md'
  - '../../pipelines/SQUEEZE-MODELS-MAX-PIPELINE.md'
research_evidence: '../../../reports/translation-research/ko-2026-05-24.md'
audience: 'translator (human + AI)'
---

# TRANSLATION-ko — Taiwan.md 韓國語翻譯規範

> 완전한 근거와 소스 citation 은 [reports/translation-research/ko-2026-05-24.md](../../../reports/translation-research/ko-2026-05-24.md) 참조. 본 문서는 canonical actionable guide, 매 번역 전 로드.

## TL;DR — 5 條最高優先規則

**핵심 결정: 타이완 primary / 대만 secondary acceptable in informal context**
(rationale: NIKL 외래어표기법 가 타이완을 권장; 한국민족문화대백과사전, 한국 위키, KCI 학술 논문 모두 타이완 을 표제어로 사용. 베이징/상하이/도쿄 와 같은 현대 자국어 자칭 존중 원칙.)

1. **국명: `타이완` 을 1순위로 사용**. `대만` 은 informal / headline / 독자 친화 맥락에서 secondary 로 허용. 현재 사이트 데이터 14,740 (대만) vs 4,427 (타이완) 비율은 학술·encyclopedic register 기준에서 표준 미달. 한국 전문 번역가의 callout 이 정확한 지적.

2. **인명: 1911 신해혁명 이후 인물은 Pinyin 기반 한글 표기**. 차이잉원(蔡英文) / 라이칭더(賴清德) / 리덩후이(李登輝, 구 이등휘). 1911 이전 인물 (鄭成功 → 정성공) 은 한국어 한자음. 蔣介石 = 장제스 (NOT 장개석); 鄧麗君 = 덩리쥔 (NOT 등려군) 가 현대 표준.

3. **지명: NIKL Pinyin 형 통일 사용**. 타이베이 / 가오슝 / 타이중 / 타이난 / 신주 / 신베이 / 타오위안 / 지룽 / 화롄 / 타이둥. 한국어 한자음 (대북·고웅·대중·대남) 은 deprecated. `대중(臺中)` 은 동음이의 (general public) 위험으로 반드시 회피.

4. **PRC-coded 표현 금지**: `중국 대만`, `중국 타이베이`, `중국의 한 성/지방인 대만`, `대만 지구`, 무맥락 `대륙` 사용 금지. `타이완` 또는 `대만` 단독, `중국 / 중국 대륙` 으로 대체. 「양안 통일」「조국 통일」 등 단일 telos 프레임 회피.

5. **문체: 해라체 (`한다/이다/이었다`) 통일**, encyclopedic register 매칭. 합니다체 (광고 / 정부 발표 톤) 와 해요체 (블로그 톤) 회피. 1인칭 집합 `우리` 사용 금지 — `대만 사회는`, `대만인들은`, `이 글에서는` 으로 recast. 한 글 안에서 문체 혼재 절대 불가.

---

## 1. 국명 / 지역 지칭 (必查)

| zh-TW source              | Recommended Korean                          | When to use                                       | Never use                               | Notes                                                                       |
| ------------------------- | ------------------------------------------- | ------------------------------------------------- | --------------------------------------- | --------------------------------------------------------------------------- |
| 台灣 / 臺灣               | **타이완** (primary) / 대만 (secondary)     | 본문, 학술, encyclopedic, sovereignty-context     | `중국 대만`, `중국 타이완`, `대만 지구` | NIKL 권장 타이완; 베이징·상하이 원칙 일치                                   |
| 中華民國                  | **중화민국 (ROC)**                          | 헌법·법적·제도적 맥락 (中華民國 총통/헌법/외교부) | 일반 시사 글 전체                       | 첫 등장시 `(ROC, Republic of China)` 글로스                                 |
| 中華台北                  | **중화 타이베이**                           | 올림픽/WHO/ICAO 맥락 한정                         | 일반 글, headline                       | PRC 압박 임시명. 첫 등장시 "PRC 압박으로 강제된 명칭" caveat                |
| 自由中國                  | 자유중국                                    | 1992 한·중수교 이전 역사 맥락 한정                | 현재형 글                               | 냉전기 한국이 ROC 를 부르던 호칭                                            |
| 兩岸 / 海峽兩岸           | **양안** / 해협 양안                        | 양안관계·양안정책 정확 호명                       | "PRC-Taiwan" 일반 의미                  | 일반 의미는 `중국과 대만` 으로. `양안` 은 bilateral-within-one-China 프레임 |
| 中國大陸                  | **중국 / 중국 대륙 / 중국 본토**            | PRC 가리킬 때                                     | 무맥락 `대륙` 단독                      | 단독 `대륙` 은 ROC 내부 시점 import                                         |
| 中國                      | **중국 / 중화인민공화국**                   | PRC 지칭                                          | `조국` (Taiwan 맥락에서)                |                                                                             |
| 我國 (zh-TW 의 1인칭 ROC) | **대만 / 타이완 / 중화민국** (3인칭 recast) | 항상                                              | `우리 나라`                             | 1인칭 집합 회피                                                             |
| 一個中國                  | **하나의 중국 (PRC 의 ~ 원칙)**             | 항상 attribution 명시                             | bare `하나의 중국`                      | "PRC 의 원칙" 으로 attribute                                                |
| 九二共識                  | **92 공식 (九二共識)**                      | 항상 글로스                                       | 무 글로스                               | 한국 독자 미인지                                                            |
| 一邊一國                  | 일변일국 / 한쪽씩 한 나라                   | 천수이볜 정권 정책 인용                           |                                         | 첫 등장 글로스                                                              |
| 一中各表                  | 일중각표 / 하나의 중국 각자 해석            |                                                   |                                         | 첫 등장 글로스                                                              |

**전환 정책 (이미 published 된 대만 표기)**: 신규 번역은 타이완 1순위 적용. 기존 14,740 건의 일괄 regex 치환은 maintainer 결정 사항 (§9 참조).

---

## 2. 인명 romanization — 1911 신해혁명 cutoff 규칙

**NIKL 외래어 표기법 §4 제2장**: 1911 신해혁명 이전 인물 = 한국어 한자음 / 이후 인물 = Pinyin 기반 한글 표기. 1986 codified.

**Format 규칙**: 첫 등장시 `차이잉원(蔡英文)` 형식. 두 번째부터 한글만.

| zh-TW           | Korean (canonical)                     | 구 형식 (deprecated, 글로스만 허용)        | 시대       |
| --------------- | -------------------------------------- | ------------------------------------------ | ---------- |
| 蔡英文          | **차이잉원**                           | —                                          | post-1911  |
| 賴清德          | **라이칭더**                           | —                                          | post-1911  |
| 李登輝          | **리덩후이**                           | (이등휘) — 역사 long-form 첫 등장만 글로스 | post-1911  |
| 馬英九          | **마잉주**                             | —                                          | post-1911  |
| 陳水扁          | **천수이볜**                           | —                                          | post-1911  |
| 蔣中正 / 蔣介石 | **장제스**                             | (장개석) — 보수 매체 잔존, 회피            | post-1911  |
| 蔣經國          | **장징궈**                             | —                                          | post-1911  |
| 唐鳳            | **탕펑**                               | —                                          | post-1911  |
| 吳釗燮          | **우자오셰**                           | —                                          | post-1911  |
| 蕭美琴          | **샤오메이친**                         | —                                          | post-1911  |
| 張忠謀          | **장중머우**                           | —                                          | post-1911  |
| 黃仁勳          | **황런쉰**                             | —                                          | post-1911  |
| 李安            | **리안**                               | —                                          | post-1911  |
| 侯孝賢          | **허우샤오셴**                         | —                                          | post-1911  |
| 楊德昌          | **양더창**                             | —                                          | post-1911  |
| 林懷民          | **린화이민**                           | —                                          | post-1911  |
| 鄧麗君          | **덩리쥔**                             | (등려군) — 회피                            | post-1911  |
| 張惠妹          | **장후이메이**                         | —                                          | post-1911  |
| 阿信 (五月天)   | **아신**                               | —                                          | post-1911  |
| 張懸 / 安溥     | **장쉬안** (구 예명) / **안푸** (현재) | (안서경 등 한자음 회피)                    | post-1911  |
| 周杰倫          | **저우제룬**                           | —                                          | post-1911  |
| 王力宏          | **왕리훙**                             | —                                          | post-1911  |
| 林志玲          | **린즈링**                             | —                                          | post-1911  |
| 孫文 / 孫中山   | **쑨원 / 쑨중산**                      | (손문/손중산 — 노년기 인물, 양용 가능)     | borderline |
| 鄭成功          | **정성공**                             | — Sino-Korean 고정                         | pre-1911   |
| 林則徐          | **임칙서**                             | — Sino-Korean                              | pre-1911   |

**전환기 인물 (1911 직전 출생, post-1911 활동)**: 기본 Pinyin. 林獻堂 → 린셴탕 / 蔣渭水 → 장웨이수이. 깊은 한국 역사학 선행 사용이 있을 때만 한자음 유지.

**원주민 인명**: Mandarin 한자 reading 이 아닌 **Austronesian 원어 발음** 에서 한글 표기. e.g., Iwan Nawi → 이완 나위.

**Hokkien/Hakka 인명**: 현대 인물은 본인 self-romanization (영어권 사용 형) 미러링. 역사 인물은 기본 Mandarin Pinyin, Hokkien/Hakka 문헌 형 documented 시 우선.

---

## 3. 지명 romanization

**NIKL 정책**: Pinyin 기반 형과 한국어 한자음 alternate 공존 허용. **Taiwan.md 는 Pinyin 형 통일** (타이완 1순위 결정과 일관).

### 주요 도시

| zh-TW | Korean (canonical) | Sino-Korean (deprecated)                           |
| ----- | ------------------ | -------------------------------------------------- |
| 臺北  | **타이베이**       | 대북                                               |
| 高雄  | **가오슝**         | 고웅                                               |
| 臺中  | **타이중**         | 대중 (동음이의 "general public" 위험, 반드시 회피) |
| 臺南  | **타이난**         | 대남                                               |
| 新北  | **신베이**         | 신북                                               |
| 桃園  | **타오위안**       | 도원                                               |
| 新竹  | **신주**           | 신죽                                               |
| 基隆  | **지룽**           | 기륭                                               |
| 嘉義  | **자이**           | 가의                                               |
| 屏東  | **핑둥**           | 병동                                               |
| 宜蘭  | **이란**           | 의란                                               |
| 花蓮  | **화롄**           | 화련                                               |
| 臺東  | **타이둥**         | 대동                                               |
| 苗栗  | **먀오리**         | 묘률                                               |
| 彰化  | **장화**           | (동일)                                             |
| 雲林  | **윈린**           | 운림                                               |
| 南投  | **난터우**         | 남투                                               |

### 구 / 시 / 현 suffix

Pinyin + 한국어 행정단위 suffix (`구` / `시` / `현`).

| zh-TW  | Korean                           |
| ------ | -------------------------------- |
| 信義區 | 신이구                           |
| 大安區 | 다안구                           |
| 中山區 | 중산구                           |
| 萬華區 | 완화구                           |
| 西門町 | 시먼딩 (町 transliteration 보존) |

### 산 / 강 / 도서

| zh-TW       | Korean (canonical)       | Sino-Korean (deprecated)                       |
| ----------- | ------------------------ | ---------------------------------------------- |
| 玉山        | **위산**                 | 옥산                                           |
| 阿里山      | **아리산**               | (동일)                                         |
| 太魯閣      | **타이루거**             | 태로각                                         |
| 日月潭      | **르웨탄**               | 일월담                                         |
| 淡水河      | **단수이허 / 단수이강**  | 담수강                                         |
| 雪山        | **쉐산**                 | 설산                                           |
| 合歡山      | **허환산**               | 합환산                                         |
| 龜山島      | **구이산다오**           | 귀산도                                         |
| 蘭嶼        | **란위** (Orchid Island) | 난서                                           |
| 綠島        | **뤼다오**               | 녹도                                           |
| 澎湖        | **펑후**                 | 팽호                                           |
| 金門        | **진먼**                 | 금문                                           |
| 馬祖 (열도) | **마쭈**                 | 마조 (媽祖 여신과 한자 동일, Pinyin 으로 구분) |
| 北回歸線    | 북회귀선                 | (universal 지리 용어)                          |

---

## 4. 문화 어휘

### 음식

Pinyin 표기 + 첫 등장 한자 글로스. 한국 naturalized 형 (버블티 등) 은 dual 형식.

| zh-TW      | Korean                            | Note                                    |
| ---------- | --------------------------------- | --------------------------------------- |
| 滷肉飯     | **루러우판** (滷肉飯)             | "다진 돼지고기 덮밥" 글로스 가능        |
| 牛肉麵     | **뉴러우몐**                      | 老 우육면 deprecated                    |
| 珍珠奶茶   | **전주나이차** (珍珠奶茶, 버블티) | dual 첫 등장; 이후 버블티 or 전주나이차 |
| 鳳梨酥     | **펑리수**                        | universal                               |
| 蚵仔煎     | **어아젠** (蚵仔煎, 굴전)         | Hokkien-derived                         |
| 小籠包     | **샤오룽바오**                    | universal                               |
| 臭豆腐     | **처우더우푸**                    | (취두부 노년기 잔존)                    |
| 雞排       | **지파이**                        | Taiwanese fried chicken cutlet          |
| 刈包       | **과바오**                        | Hokkien-derived                         |
| 蔥油餅     | **충유빙**                        |                                         |
| 麻油雞     | **마유지**                        |                                         |
| 三杯雞     | **싼베이지**                      |                                         |
| 擔仔麵     | **단자이몐**                      |                                         |
| 肉圓       | **러우위안**                      |                                         |
| 滷味       | **루웨이**                        |                                         |
| 大腸包小腸 | **다창바오샤오창**                | Pinyin + brief 글로스                   |
| 夜市       | **야시장**                        | 한국어 직역; 예쉬 transliterate 금지    |

### 종교

| zh-TW       | Korean                                       |
| ----------- | -------------------------------------------- |
| 媽祖        | **마쭈** (媽祖) — Wiki 표준; 마조 deprecated |
| 關公 / 關帝 | 관공 / 관제                                  |
| 土地公      | 투디공                                       |
| 城隍        | 청황 (성황 한국 민속과 구분)                 |
| 道教        | 도교                                         |
| 佛教        | 불교                                         |
| 一貫道      | 일관도                                       |

### 명절

한국 독자 공유 문화 — Taiwan 맥락에서 한자어 형 우선, 한국 토착명 글로스.

| zh-TW  | Korean                                              |
| ------ | --------------------------------------------------- |
| 春節   | **춘절** (설)                                       |
| 元宵節 | **원소절** (정월 대보름)                            |
| 端午節 | **단오** / 단오절                                   |
| 中元節 | **중원절** (음력 7월 보름; 한국 백중과 다름 글로스) |
| 中秋節 | **중추절** (추석)                                   |
| 清明節 | **청명절** (한식)                                   |
| 鬼月   | **귀월(鬼月)** — 음력 7월. 한국 전통 차이 글로스    |

### 언어

| zh-TW              | Korean                                 | Note                                     |
| ------------------ | -------------------------------------- | ---------------------------------------- |
| 國語 (Taiwan 맥락) | **중국어 (대만 표준) / 대만 화어**     | bare `국어` 회피                         |
| 普通話 (PRC 맥락)  | **중국어 (표준 중국어) / 베이징 화어** |                                          |
| 閩南語 / 台語      | **대만어 / 타이완어 / 민난어**         | "대만어/타이완어" sovereignty-respecting |
| 客家話             | 객가어 / 하카어                        |                                          |
| 注音符號           | 주음 부호                              |                                          |
| 繁體字             | 번체자 (정체자)                        |                                          |

### 원주민

| zh-TW           | Korean (canonical)         |
| --------------- | -------------------------- |
| 原住民          | **원주민** (토착민 회피)   |
| 阿美族          | 아메이족 (Amis)            |
| 排灣族          | 파이완족 (Paiwan)          |
| 布農族          | 부눙족 (Bunun)             |
| 泰雅族          | 타이야족 (Atayal)          |
| 達悟族 / 雅美族 | 다우족 / 야미족 (Yami/Tao) |
| 賽夏族          | 사이샤족 (Saisiyat)        |
| 鄒族            | 저우족 (Tsou)              |
| 魯凱族          | 루카이족 (Rukai)           |
| 卑南族          | 베이난족 (Puyuma)          |
| 撒奇萊雅族      | 사키자야족 (Sakizaya)      |
| 噶瑪蘭族        | 가마란족 (Kavalan)         |

---

## 5. 정치 / 역사 sensitive terms

| zh-TW                | Korean (canonical)                                     | Convention                                        |
| -------------------- | ------------------------------------------------------ | ------------------------------------------------- |
| 二二八事件           | **2·28 사건**                                          | 항상 middle dot. 이이팔 음독 금지                 |
| 白色恐怖             | **백색 테러** (Wiki 표준) / 백색 공포 (직역)           | 두 형 공존; 백색 테러 권장                        |
| 戒嚴 / 戒嚴令        | **계엄 / 계엄령**                                      | 한국 독자 친숙 (5·18)                             |
| 解嚴 (1987)          | **계엄 해제 (1987년)**                                 |                                                   |
| 民國紀年 (民國 N 年) | **민국 N 년 (서기 YYYY년)**                            | 항상 서기 변환; ROC 문서 인용시만 민국 병기       |
| 本省人               | **본성인** (本省人, 1949 국부천대 이전 한족 후손)      | 첫 등장 글로스                                    |
| 外省人               | **외성인** (外省人, 1949 국부천대 시기 대륙 이주 한족) | 첫 등장 글로스                                    |
| 新住民               | **신주민** (新住民)                                    |                                                   |
| 國府遷臺             | **국부천대** (1949)                                    | 첫 등장시 "1949 중화민국 정부의 대만 이전" 글로스 |
| 黨外運動             | **당외 운동**                                          | 첫 등장 글로스                                    |
| 美麗島事件           | **메이리다오 사건** (美麗島, Formosa Incident)         | Pinyin + 글로스                                   |
| 太陽花學運 (2014)    | **해바라기 학생 운동** / 해바라기 운동                 | 한국어 직역                                       |
| 反送中 (2019, HK)    | 송환법 반대 운동                                       | 대만 글 referenced 시                             |
| 反分裂國家法         | 반분열 국가법                                          | PRC 2005 법                                       |
| 一邊一國             | 일변일국 / 한쪽씩 한 나라                              | 천수이볜 정책 인용                                |
| 臺灣獨立             | **타이완 독립 / 대만 독립**                            | 타이완 형 권장                                    |
| 中華民國在臺灣       | 타이완의 중화민국                                      | 리덩후이 공식; 글로스                             |
| 國民黨 / KMT         | **국민당** (中國國民黨)                                |                                                   |
| 民進黨 / DPP         | **민진당** (민주진보당)                                |                                                   |
| 民眾黨 / TPP         | **민중당** (대만 민중당)                               |                                                   |
| 時代力量 / NPP       | 시대역량 / 시대역량당                                  |                                                   |

---

## 6. Sovereignty-avoid lexicon (PRC-coded → 대체)

핵심 원칙: **`타이완` 자체는 PRC-coded 가 아니다** (Mandarin self-naming 존중). 진짜 위험은 `중국 + 타이완` 결합 구조와 ROC-internal viewpoint 잔존 어휘.

| AVOID (PRC-coded / 회피)                          | USE INSTEAD                                              | Why                                                                                                                  |
| ------------------------------------------------- | -------------------------------------------------------- | -------------------------------------------------------------------------------------------------------------------- |
| 중국 대만 / 중국의 대만                           | **대만** / **타이완** 단독                               | PRC 플랫폼이 대만 아티스트/기업에 강제하는 형식; import 시 framing 도 import                                         |
| 중국 타이베이 (colloquial)                        | **타이베이** 단독 / 중화 타이베이 (올림픽 한정 + caveat) | "중국 타이베이" 가 PRC subordination 주장을 자연화                                                                   |
| 대만성 / 중국의 한 성/지방인 대만                 | **타이완** / **대만** (polity 로 호명)                   | PRC 영토 주장을 사실로 채택                                                                                          |
| 대만 지구 (台灣地區)                              | **대만** / **타이완**                                    | "지구/地區" 는 PRC + ROC 헌법 sub-national 잔존                                                                      |
| 대륙 (무맥락 단독, PRC 지칭)                      | **중국** / **중국 대륙** / **중국 본토**                 | bare `대륙` 은 within-one-China 시점 import                                                                          |
| 본토 / 중국 본토 (Taiwan-centric 의미로)          | **중국**                                                 | within-one-China 함의 회피                                                                                           |
| 광복 (1945 ROC takeover 의미)                     | 1945년 일본 항복 후 중화민국 정부 접수 (descriptive)     | "광복" 은 ROC arrival 을 "조국 회귀" 로 frame, 대만 sovereignty discourse 와 충돌. 한국어 1945 광복 의미와 혼동 위험 |
| 조국 (PRC 지칭)                                   | **중국** / **중화인민공화국**                            | 통일 narrative loaded                                                                                                |
| 회귀 (回歸)                                       | (대만 맥락에서 회피)                                     | HK/Macau 1997/1999 unification language                                                                              |
| 양안 통일 / 조국 통일 (단일 telos)                | 양안 정책 / 통일 또는 독립 논쟁                          | 통일을 자연 endpoint 로 presenting 회피                                                                              |
| 普通話 (Taiwan 화어 가리킬 때)                    | **대만 화어** / 중국어 (대만 표준)                       | PRC 표준어 명칭을 Taiwan 변종에 적용                                                                                 |
| 閩南語 (Taiwan 맥락)                              | **대만어** / **타이완어** / 민난어                       | Taiwan-internal identity 존중                                                                                        |
| 화교 (Taiwan-origin people 의 경우)               | **대만 출신** / **대교**                                 | 화교 = PRC-centered diaspora 함의                                                                                    |
| 인민 / 백성 (PRC-style 어휘)                      | 시민 / 국민 / 대만인                                     | PRC 정치 어휘 register 회피                                                                                          |
| 우리 (we, 1인칭 집합)                             | 대만 / 대만 사회 / 대만인 / 이 글에서는                  | 공공 지식 플랫폼에 ethnic-collective voice 부적절                                                                    |
| 이등휘 / 등려군 / 장개석 (구 Sino-Korean)         | 리덩후이 / 덩리쥔 / 장제스                               | Pinyin 현대 표준                                                                                                     |
| 대북 / 고웅 / 대중 / 대남 (구 Sino-Korean 도시명) | 타이베이 / 가오슝 / 타이중 / 타이난                      | NIKL Pinyin 표준                                                                                                     |
| 일월담 / 옥산 (구 형)                             | 르웨탄 / 위산                                            | Pinyin 일관성                                                                                                        |
| 자유중국 (현재형 사용)                            | 대만 / 타이완                                            | 1992 이전 냉전 호칭                                                                                                  |

---

## 7. 문체 & 등록 (Register) 규칙

- **해라체 (`한다` / `이다` / `이었다` / `있다` / `없다`)** 가 표준. encyclopedic, journalistic, academic prose 의 한국어 default. 한국 위키·KCI 학술 논문 일치.
- **장 단위 통일 / 혼재 절대 불가**. 한 글 안에서 해라체 + 합니다체 mixing 금지.
- **회피 register**: 합니다체 / 하십시오체 (광고·정부 announcement 톤), 해체 / 해요체 (블로그 톤).
- **호칭**: 역사 인물은 호칭 없음 또는 `씨`; 현대 인물은 한국 미디어 관례 (총통/장관/감독 등 직함). `라이칭더 총통`, `허우샤오셴 감독`.
- **연도**: 서기 1순위. 민국 연도는 ROC 문서 인용시만 `2024년(민국 113년)` 첫 등장 병기, 이후 서기만.
- **한자 병기**: 첫 등장시 `(蔡英文)` 형식. 두 번째부터 한글만. 정치·역사·문화 specialized 용어는 한자 글로스 권장 (`본성인(本省人)`, `백색 테러(白色恐怖)`). 자연화된 어휘 (중국, 일본, 대만) 는 한자 불필요.
- **1인칭 집합 회피**: `우리` 금지. 3인칭 recast (`대만 사회는`, `대만인들은`, `이 글에서는`). 한국어 주어 생략 허용 시 drop.
- **인용**: Mandarin 직접 인용은 자연스러운 한국어로 번역 후 원문 괄호 또는 각주. 음성 word-by-word transliteration 금지.
- **통화**: 신타이완 달러 (TWD) / 대만 달러 / NTD. 첫 등장 spell out, 이후 `달러` 또는 `NT$`.
- **Hokkien loanword**: Mandarin source 에 Hokkien 인용 시 Hokkien 발음 한글 + 한자 + 글로스 (`아공(阿公, 대만어로 할아버지)`). Hokkien → Mandarin Pinyin auto-conversion 금지.

---

## 8. CI Lint 候補 banned phrases

CI hard-fail 또는 maintainer review flag 후보 (whitelist 가능 맥락 명시).

| Banned phrase                              | Action          | Whitelist context             |
| ------------------------------------------ | --------------- | ----------------------------- |
| `중국 대만`                                | hard-fail       | (없음)                        |
| `중국 타이완`                              | hard-fail       | (없음)                        |
| `중국 타이베이`                            | flag for review | 올림픽·WHO 맥락 + caveat 명시 |
| `대만 지구`                                | hard-fail       | (없음)                        |
| `대만성`                                   | hard-fail       | 역사적 청 제국 시기 인용 한정 |
| `중국의 한 성` (대만 인접 시)              | hard-fail       | (없음)                        |
| `조국 통일`                                | flag for review | PRC 발화 직접 인용 한정       |
| `양안 통일` (단일 telos 로)                | flag for review | 정책 명칭 인용 한정           |
| `회귀` (대만 맥락)                         | hard-fail       | HK/Macau 1997/1999 비교 한정  |
| `이등휘` / `등려군` / `장개석` (본문)      | flag for review | 구 한국 매체 형 글로스 한정   |
| `대북` / `고웅` / `대중` / `대남` (도시명) | flag for review | 역사 인용 한정                |

---

## 10. Per-instance judgment framework — 감사 → 분류 → 판단 → 적용 → 검증

§1-§8 의 table 은 sufficient 하지 않다. table 은 "X → Y" 의 일률적 rule 이지만 실제 corpus 에는 **false positive**, **historical compound names**, **verbatim citation context**, **동음이의 위험** 이 산재한다. 단순 grep + sed 는 collateral damage 를 낸다. 매 패턴마다 5-step decision tree 를 강제한다.

### Step 1: 감사 (audit) — corpus 전수조사

```bash
# 본문 + frontmatter 따로 보기 (필수)
grep -rn '패턴' knowledge/ko/                      # 전 corpus, count + path 확보
grep -rn '패턴' knowledge/ko/ | wc -l              # 총 hit 수
grep -rn 'description:.*패턴\|title:.*패턴' knowledge/ko/  # frontmatter 별도 audit
```

- 5-10 개 sample 의 ±2 줄 context 를 Read 로 확인 — pure grep count 만으로 판단 금지
- 단일 file 내에서 multiple hit 이면 동일 file 의 모든 occurrence 를 한 번에 본다 (context 일관성)
- frontmatter (`description`, `title`, `imageAlt`, `tags`) 는 body-only grep 으로 안 잡힌다 — **별도 audit pass 필수**

### Step 2: 분류 (categorize) — 각 hit 를 6 buckets 로 sort

| Bucket                       | Disposition  | Korean-specific examples                                                                                                                |
| ---------------------------- | ------------ | --------------------------------------------------------------------------------------------------------------------------------------- |
| **본문 narrative**           | likely FIX   | "신죽 과학단지" → "신주 과학단지" (Hsinchu Science Park modern reference)                                                               |
| **직접 인용 「" "」**        | PRESERVE     | 한국 미디어 headline 을 verbatim 인용 시 그 매체의 "대만" 표기 보존; 화자 발화 verbatim 보존                                            |
| **고유 명사 (institution)**  | PRESERVE     | 《대북인 (台北人)》 1971 바이셴융 책 제목; 「신죽음사 (新竹吟社)」 1752 시사; 「대만성 정부」 1949-1998 ROC 행정 단위; 「화교」 generic |
| **동음이의 위험**            | DISAMBIGUATE | 대중 = 台中(Taichung) or 大眾(general public) 매 occurrence 문맥 확인                                                                   |
| **Historical compound name** | PRESERVE     | "양안 통일전선" (united-front 통전) ≠ "양안 통일" (unification); "백색 테러" vs "백색 공포" 둘 다 standard                              |
| **메타 토론 of term itself** | PRESERVE     | `taiwans-labeling-in-international-standards.md`, `taiwan-unification-independence-spectrum.md` — 용어 자체를 분석하는 글               |

### Step 3: 판단 (judge) — edge case 는 §11 화이트리스트 대조

명확하지 않으면 **§11 false-positive whitelist** 와 비교. 거기에 없는 새 edge case 면:

- §15 Open questions 에 후보로 노트
- conservative default = preserve (사실 leak 보다 silent loss-of-meaning 이 더 deep damage)
- 哲宇 review 후 patterns 가 stabilize 되면 §11 에 incorporate

### Step 4: 적용 (apply) — per-file 문맥-anchored Edit

```bash
# ❌ 금지: 전 corpus sed 일괄 치환
find knowledge/ko/ -name '*.md' -exec sed -i '' 's/중국 본토/중국/g' {} +

# ✅ 권장: per-file 문맥 anchored Edit (Edit tool 의 old_string 에 ±1 줄 context 포함)
# old_string: "...중국 본토에서 이주한 한족..."
# new_string: "...중국에서 이주한 한족..."
```

**조사 agreement (Korean-specific 鐵則)**: 한국어는 받침 (consonant-final) vs 모음 (vowel-final) 에 따라 후행 助詞가 변한다. **"중국 본토" → "중국" 치환은 vowel-final 「토」가 consonant-final 「ㄱ」으로 바뀌므로 모든 후행 조사를 재검증해야 한다**:

| 受詞 / 主格 / 連結   | 본토 (vowel-final) | 중국 (consonant-final) | 변환      |
| -------------------- | ------------------ | ---------------------- | --------- |
| 主格                 | 본토**가**         | 중국**이**             | 가 → 이   |
| 受詞                 | 본토**를**         | 중국**을**             | 를 → 을   |
| 連結 (and)           | 본토**와**         | 중국**과**             | 와 → 과   |
| Tool / Path / Method | 본토**로**         | 중국**으로**           | 로 → 으로 |
| Topic marker         | 본토**는**         | 중국**은**             | 는 → 은   |
| Possessive / Belongs | 본토**의**         | 중국**의**             | (불변)    |

W1 cleanup 에서 70 개 본토 → 중국 치환 후 9 개 file 에 助詞 mismatch 가 남았다 — followup commit 필요했음. **post-edit 즉시 grep agreement 검증** 이 본질적 step 이지 optional 이 아니다.

### Step 5: 검증 (verify) — 3 가지 post-edit gate

```bash
# 1. 잔존 count 확인 (whitelist 외 zero?)
grep -rn '패턴' knowledge/ko/ | wc -l

# 2. 助詞 agreement 검증 (vowel→consonant 치환 시 필수)
grep -rn '중국가\|중국를\|중국와\|중국로\|중국는' knowledge/ko/

# 3. build verification — preview 가 깨지지 않았는가
npm run build 2>&1 | grep -i error
```

### Korean-specific worked examples

#### Example A: 신죽 → 신주 (W2f, 2026-05-25)

- **감사**: `grep -rn '신죽' knowledge/ko/` → 8 hits across 2 files
- **분류**:
  - 7 hits in `hsinchu-science-park.md` body → modern Hsinchu Science Park reference → FIX
  - 1 hit in `history-of-taiwanese-literature.md` line 67 → "1752년의 신죽음사(新竹吟社)" → 史実 poetry society 고유 명사 → PRESERVE
- **판단**: §11 에 institutional name preservation 규칙 있음
- **적용**: per-file Edit, 1752 잔존 보존
- **검증**: `grep -rn '신죽[^음]' knowledge/ko/` → zero (음사 제외 모두 fixed)
- **결과**: 7 fix / 1 preserve. straight-line case.

#### Example B: 중국 본토 → 중국 (W1, 2026-05-24)

- **감사**: 76 hits across 19 files
- **분류**:
  - 70 hits in body narrative voice → FIX ("중국 본토 = 중국 + within-one-China 함의 import")
  - 6 hits in BBC article verbatim citation context (`hsinchu-city.md` 99/235 + 기타) → 원문 中國大陸 verbatim → **PRESERVE as 「중국 대륙」** (citation fidelity > policy)
- **판단**: 직접 인용 verbatim preservation > sovereignty cleanup (per §11 whitelist rule)
- **적용**: 70 file-by-file Edit
- **검증 누락**: post-edit 조사 agreement check 빠뜨림 — 9 개 file 에 「중국가/중국를/중국와/중국로」 잔존 → followup commit 필요
- **교훈**: Step 5 助詞 grep 은 protocol 화. skip 시 followup 1 commit cost.

#### Example C: 대북 → 타이베이 (zero fix possible)

- **감사**: 4 hits across 4 files
- **분류** (10/10 모두 false positive):
  - 3 hits = 《대북인 (台北人)》 바이셴융 1971 책 제목 → PRESERVE (작품 원제 transliteration)
  - 1 hit = `tectonic-plates-and-seismic-activity.md` 82 "대만 북동부 지역, 대북부 지역을 포함하여" → 대북부 = 大北部 (Greater Northern Region) ≠ 台北
- **판단**: 4/4 false positive. 0 fix possible.
- **교훈**: grep count 만 보고 "4 fixes 대기 중" 으로 진입했으면 collateral damage. Step 1 의 ±2 줄 context Read 가 false positive 를 잡아냄.

#### Example D: 중국 대만 → 대만 (W1, 2026-05-24)

- **감사**: 5-6 hits across 5 files
- **분류**:
  - 5 hits body narrative → FIX ("중국 대만" = PRC subordination framing, hard-fail per §8)
  - 1 hit in `taiwans-labeling-in-international-standards.md` discussing the term itself → PRESERVE (메타 토론)
- **적용**: "중국 대만판무국" / "중국 대만판" 같은 translation error 2 instance 도 함께 발견 → "중국 국대판" (中國國民黨臺灣省黨部 → KMT Taiwan branch, correct form) 으로 수정
- **검증**: `grep -rn '중국 대만\|중국의 대만\|중국대만' knowledge/ko/` → whitelist 외 zero

---

## 11. False-positive whitelist patterns (Korean-specific)

다음 패턴은 grep 으로 잡히지만 **수정 금지** (이유 명시 + 매번 §10 Step 2 분류에서 PRESERVE bucket 으로 sort). 새 false positive 발견 시 PR 로 이 table 에 추가.

| Pattern                                             | Why PRESERVE                                                                           | Reference                                                  |
| --------------------------------------------------- | -------------------------------------------------------------------------------------- | ---------------------------------------------------------- |
| `대북부 (大北部)`                                   | Greater Northern Region 지리 행정 region 명, NOT 台北                                  | `Geography/tectonic-plates-and-seismic-activity.md:82`     |
| `대중 (大眾)` 일반 대중                             | general public, NOT 台中 — 매 occurrence 문맥 확인                                     | (corpus 전반)                                              |
| `《대북인 (台北人)》`                               | 바이셴융 1971 단편집 책 제목 transliteration of 原題                                   | `Art/postwar-taiwanese-literature.md:68,199,201`           |
| `신죽음사 (新竹吟社)`                               | 1752 historical 시사 compound 고유 명사                                                | `Art/history-of-taiwanese-literature.md:67`                |
| `양안 통일전선` / `통전`                            | united-front 공작 (work), NOT 양안 통일 (unification)                                  | `Society/falun-gong-in-taiwan.md:68`                       |
| `중국 대륙` in verbatim citation                    | BBC 등 원문 中國大陸 verbatim 인용 시 출처 충실성 우선                                 | `Geography/hsinchu-city.md:99,235` etc.                    |
| `대만성 정부 / 대만성 의회`                         | 1949-1998 ROC 행정 단위 史実 institutional name                                        | History 시리즈 전반                                        |
| `화교 (華僑)` generic context                       | 일반 중국계 디아스포라 context (≠ Taiwan-diaspora specifically)                        | Migration/Diaspora 문서                                    |
| `taiwans-labeling-in-international-standards.md`    | 메타 토론 of term itself — 용어 자체가 주제                                            | (article 전체)                                             |
| `poisoned-potato-cognitive-warfare-taiwan.md`       | 認知戰 메타 토론 — PRC framing 자체가 분석 대상                                        | (article 전체)                                             |
| `taiwan-unification-independence-spectrum.md`       | 통일/독립 spectrum 메타 분석 — 양 극단 용어 모두 cite                                  | (article 전체)                                             |
| 한국 媒體 headline verbatim 「대만」                | 직접 인용 시 매체 표기 보존 (translator's voice ≠ source voice)                        | RTI / 한겨레 / SBS 등 quote                                |
| `이등휘` in long-form lee-teng-hui article          | author 의 의도적 Sino-Korean choice — 38 instances 일괄 변경 = editorial decision 필요 | `People/lee-teng-hui.md` (38 instances; §15 open question) |
| Frontmatter `description / title / imageAlt / tags` | body-only grep 으로 안 잡힘 — 별도 audit pass 필수                                     | (모든 file)                                                |

**원칙**: false positive 가 1개라도 발견되면 그 패턴은 더 이상 "regex-safe" 가 아니다. §10 5-step framework 강제. Whitelist 는 자라는 SSOT (living document).

---

## 12. Worked examples library (this session)

W1 (2026-05-24) + W2f (2026-05-25) 에서 ship 한 ko cleanup commit (`c2d7633e0` / `06fd23be3` / `d1f99beee`) 에서 추출한 patterns. 각 example 은 future agent 가 같은 종류의 cleanup 을 만났을 때 §10 framework 의 concrete instantiation 으로 사용.

### Pattern 1: PRC-coded "본토" mass cleanup

```
Before: 「외성인 (外省人) 은 1949년 중국 본토에서 이주한 한족 후손이다.」
After:  「외성인 (外省人) 은 1949년 중국에서 이주한 한족 후손이다.」
```

- count: 70 instances replaced
- 助詞 followup: 9 file 에 「중국가/중국를/중국와/중국로」 mismatch 정리 (Korean consonant-final agreement)
- 보존 6 instance: BBC article verbatim citation context — 원문 中國大陸 → 「중국 대륙」 fidelity

### Pattern 2: "중국 대만" hard-fail cleanup

```
Before: 「2020 도쿄 올림픽에서 중국 대만 팀이 금메달을 획득했다.」
After:  「2020 도쿄 올림픽에서 중화 타이베이 팀이 금메달을 획득했다.」 (올림픽 맥락 — 중화 타이베이 official)
```

```
Before: 「중국의 대만 정책은 1949 이후 변화해왔다.」
After:  「중국의 대 대만 정책은 1949 이후 변화해왔다.」 (recast: 「대만에 대한 정책」 = "policy toward Taiwan", not "Taiwan policy of China")
```

- count: 6 instance recast in 5 files

### Pattern 3: Translation error "중국 대만판무국" → "중국 국대판"

```
Before: 「국민당 (中國國民黨) 대만판무국 운영」
After:  「국민당 (中國國民黨) 대만 지부 / 중국 국대판 운영」
```

- "대만판무국" 은 일본 통치기 「臺灣總督府」 의 오역. 올바른 form: 「대만 지부」 or 「국대판」 (KMT 中國國民黨)
- 2 instance fixed; future translator 가 「판무국」 보면 always flag for editorial review

### Pattern 4: "양안 통일 지지" hedge

```
Before: 「양안 통일을 지지했으며」
After:  「통일을 지지했으며」
```

- 「양안 통일」 = 단일 telos 표현. drop 「양안」 prefix; "unification" 단독 도 충분히 historical-figure stance 표현
- 1 instance recast

### Pattern 5: BBC citation 「중국 대륙」 보존

```
Context: BBC 한국어판 article 인용. 원문 中國大陸 verbatim.
Before: 「BBC 보도에 따르면, 신주 과학단지는 "중국 본토" 기업과 협력 관계를 유지한다.」
After:  「BBC 보도에 따르면, 신주 과학단지는 "중국 대륙" 기업과 협력 관계를 유지한다.」
```

- BBC 원문 中國大陸 → 「중국 대륙」 fidelity (translator 가 source 의 표기를 임의 sovereignty-correct 하면 reporting accuracy 손상)
- 6 instance preserved in `hsinchu-city.md` lines 99/235 + 기타

### Pattern 6: 신죽 → 신주 (Sino-Korean leftover, modern Hsinchu)

```
Before: 「신죽 과학단지는 1980년 설립되어 TSMC 본사가 위치한다.」
After:  「신주 과학단지는 1980년 설립되어 TSMC 본사가 위치한다.」
```

- count: 7 fix in `hsinchu-science-park.md` + 기타
- preserve 1: 1752 「신죽음사(新竹吟社)」 historical 시사 compound 고유 명사

### Pattern 7: False positive — 대북 → 타이베이 시도

```
Context: 「대만 북동부 지역, 대북부 지역을 포함하여...」
Misread: "대북부" 의 "대북" 을 taipei 로 오인 가능
실제: 「대북부 (大北部) 지역」 = Greater Northern Region (台北 ≠)
처치: PRESERVE
```

- 4 instance corpus-wide, 4/4 모두 false positive (3 = 《대북인 (台北人)》 + 1 = 대북부)
- 0 fix possible — pattern 자체가 fundamentally collide 不 safe

---

## 13. Translator's "Taiwan-first" mental model — 한국어 버전

한국 독자 다수는 대만에 대해 일정한 친숙도 (음식 / 야시장 / TSMC / 2024 대선 / 한국 매체 빈번 보도) 를 갖지만, **NIKL 외래어 표기법 (post-1911 Pinyin) vs Sino-Korean 한자음 reading 의 registry 차이는 의식하지 못한다**. 한국 독자에게 "타이완" 은 좀 더 학술적 / 거리감 있는 form 으로 들리고 "대만" 은 친근한 form 으로 들린다. 그러나 Taiwan.md 의 register 는 encyclopedic / 학술 / 주권 존중이다 — 韓国民族文化大百科事典 register, NOT 韓國 MOFA / 대중 매체 headline register.

번역자는 다음 5 가지 mental model 을 매 paragraph 마다 활성화한다:

### 1. 타이완을 독립적 polity 로 그린다

- NOT "중국의 한 성" / NOT "양안의 한 쪽" / NOT "중국에 속한 지방"
- "대만은", "타이완 정부는", "타이완 사회는" 의 주어 frame 으로 작성
- 「양안 (兩岸)」는 cross-Strait policy 토론 시에만 사용 — generic "PRC와 Taiwan" 으로는 「중국과 대만」

### 2. NIKL 외래어 표기법 1911 신해혁명 cutoff 의 logic 을 이해한다

- 베이징 (NOT 북경), 상하이 (NOT 상해), 도쿄 (NOT 동경) — 같은 logic
- 자국어 self-naming 존중 = sovereignty preservation
- 타이완 = 自國 Mandarin self-naming 韓글 transliteration; 대만 = Sino-Korean 漢字音 (한국이 한자 통해 부르던 historical 호칭)
- 어느 form 도 자체로 PRC-coded 는 아니다. 위험은 「중국 + 타이완」 / 「중국 + 대만」 의 combinatorial PRC framing

### 3. 한국 위키 / 한국민족문화대백과사전 의 학술/encyclopedic register 를 model 로 한다

- NOT 한국 주요 media headline 의 콜로키얼 default 「대만」
- NOT 한국 MOFA 정부 default 「대만」 (1992 한·중수교 이후 정책 default)
- 한국 academic Taiwan studies (한국대만학회, KCI 지표 논문) 은 「타이완」 우세

### 4. PRC-default 어휘를 의식적으로 피한다

§6 sovereignty-avoid lexicon 의 全항목을 매 paragraph 마다 활성화. 특히:

- 「중국 본토」 (uncontextualized) — within-one-China 시점 import
- 「중국 대륙」 (uncontextualized narrative voice) — same
- 「양안 통일」「조국 통일」 (단일 telos frame) — 통일을 자연 endpoint 로 presenting
- 「중국 타이베이」 (올림픽 외) — PRC subordination 자연화
- 「대만 지구」「대만성」 (현대 sovereignty 맥락) — sub-national 잔존 어휘
- 「광복 (1945 ROC takeover 의미)」 — ROC 도착을 "조국 회귀" 로 frame, 대만 sovereignty discourse 와 충돌

### 5. 번역자는 한국어 안에서의 "Taiwan voice" 이다

- 양안 중립 관찰자가 아니다. 한국어 reader 에게 Taiwan-perspective 를 전달하는 voice
- 1인칭 집합 「우리」 (we) 사용 금지 — 공공 지식 플랫폼의 multi-cultural readership 에 ethnic-collective voice 부적절
- 3인칭 recast: 「대만 사회는」, 「대만인들은」, 「이 글에서는」 / 한국어 주어 생략 허용 시 drop

### 문체 / 등록 보충

- **해라체 (한다/이다/이었다)** default for 학술/encyclopedic article body
- **합니다체** for spore / SNS / guide 안내문 (드물게 — guide-level instruction)
- **장 단위 통일 / 한 글 안에서 혼재 절대 불가** (§7 rule 재강조)
- **첫 등장 한자 병기** for 정치/역사/문화 specialized 용어 — 한자가 의미를 clarify 하는 경우만
- **연도**: 서기 1순위 / 民國 N년 → 「2024년 (민국 113년)」 첫 등장 병기, 이후 서기만

이 5 가지 model 을 매 paragraph 마다 활성화하지 않으면 LLM default 가 PRC-friendly form 으로 drift 한다 (실제 W1 audit 결과 14,740 「대만」 vs 4,427 「타이완」 76/23 imbalance 가 그 drift 의 결과). **Conscious activation 이 instrumentation 이다**.

---

## 14. Process discipline (commit / tooling hygiene) — Korean-specific

§10 5-step framework 외에, ko cleanup 작업 자체의 hygiene rule. ko 는 助詞 agreement 의 Korean-specific 요구 사항 때문에 다른 언어보다 process discipline 이 더 엄격하다.

### 14.1 Worktree isolation

- ko cleanup 은 다른 lang cleanup 과 separate worktree 에서 작업 (W1 = `20260524-translation-audit` / W2f = `20260525-ko-sino-korean-leftover`)
- knowledge/ko/ 만 touch — 다른 lang 은 不 touch
- multi-lang batch 는 SQUEEZE-MODELS-MAX-PIPELINE 별도 SOP

### 14.2 File-level git add (NOT git add -A)

```bash
# ❌ 금지
git add -A

# ✅ 권장
git add knowledge/ko/Geography/hsinchu-city.md
git add knowledge/ko/History/koxinga.md
# ... explicit file list
```

- 대량 corpus edit 시 unintended file 이 staging 되는 risk
- per-file diff review pass 가 forces 문맥 검증

### 14.3 助詞 agreement post-edit grep (Korean-specific 필수 step)

vowel-final → consonant-final 단어 치환 시 (예: 본토 → 중국, 대륙 → 중국) **반드시** 후속 grep 으로 助詞 mismatch 검사:

```bash
# 「중국」 (consonant-final) 후행 助詞 검사
grep -rn '중국가\|중국를\|중국와\|중국로\|중국는' knowledge/ko/

# 「대만」 (vowel-final) 후행 助詞 검사
grep -rn '대만이\|대만을\|대만과\|대만으로\|대만은' knowledge/ko/
```

mismatch 발견 시 followup Edit + commit. **이 step skip = "cleanup 끝났음" 으로 close 했다가 1-2 일 후 다른 reviewer 가 발견 = 신뢰 cost**.

### 14.4 Commit message 의 referential integrity

```
✅ 좋은 commit message:
[ko cleanup] 중국 본토 → 중국 70 instances + 助詞 agreement 9 files

per §10 framework Step 4-5:
- 70 본문 narrative instances replaced
- 6 BBC citation instances preserved (per §11 whitelist)
- 9 file followup for 가→이 / 를→을 / 와→과 / 로→으로 agreement
```

```
❌ 나쁜 commit message:
ko cleanup
```

- 첫 commit message 가 future agent 의 referential anchor 가 된다 — §10 framework 의 어느 step 인지, 몇 instance 인지, whitelist preserve 했는지 명시

### 14.5 Sub-agent prompt 에 inline guide 직접 첨부

per [REFLEXES #42](../../../docs/semiont/REFLEXES.md) sub-agent 三偷吃步 교훈:

- Sub-agent 에게 ko cleanup 위임 시 「TRANSLATION-ko.md 참고」 같은 pointer ONLY 는 부족
- guide 의 §1 + §6 + §10 + §11 + §14.3 (助詞 agreement) 을 **inline 으로** sub-agent system message 에 첨부
- Sub-agent 는 file 을 안 읽는 경향이 있다 — inline 만이 enforceable

### 14.6 「我熟了不用讀」 self-deception 의 Korean variant

ko cleanup 의 가장 common failure mode = "助詞 agreement 은 obvious 라서 grep 안 해도 된다" — actual W1 case 에서 9 file mismatch 누락. **Step 5 grep 은 protocol, not optional**. 「熟了不用讀」 는 §10 framework 自体를 bypass 하는 최빈 변명 (per REFLEXES #15).

---

## 15. Open questions

### 15.1 전환 전략 (existing 14,740 대만 / 4,427 타이완)

maintainer 결정 사항. 옵션:

- (a) **gradual shift**: 신규 번역만 타이완 1순위, 기존 미수정 (low risk / slow convergence)
- (b) **bulk regex + manual review**: 14,740 일괄 치환 후 sovereignty-context 수동 점검 (high throughput / collateral risk; §10 framework 강제 필요)
- (c) **dual usage accept**: 현 상태 공식 인정, headline 「대만」 / body 「타이완」 한국 미디어 관례 mirroring (status quo / no-op)

哲宇 review pending. 본 guide 의 default 권고: **(a) gradual shift** — §10 framework 강제로 LLM-translated new content 부터 타이완 1순위, 기존 14,740 은 future quarterly audit 의 candidate.

### 15.2 이등휘 / 리덩후이 (Lee Teng-hui) 전체 변환

`People/lee-teng-hui.md` article 전체가 「이등휘」 38 instance 사용 — author 의 의도적 Sino-Korean choice 인지, LLM drift 인지 불명. options:

- (a) 전체 article 을 「리덩후이」 로 rewrite (NIKL post-1911 cutoff rule 적용)
- (b) author intentional Sino-Korean form 으로 preserve (older Korean historiography style)
- (c) 본문은 「리덩후이」 로 통일, 첫 등장만 「(구 이등휘)」 글로스 (compromise)

editorial decision 필요. default 권고: **(c) compromise** — Korean Wikipedia 의 현재 headword 가 「리덩후이」이므로 align, 但 long-form 첫 등장에서 historical 한국 매체 form 의 reader bridge 제공.

### 15.3 한국 전문 번역가 callout 의 정확한 dimension

2026-05-23 talk 에서 "표준 전문가 선택이 아니다" 라고 했는데 가장 가능성 높은 타겟 = 대만 dominance. 다른 specifics (sentence-ending 문체 / 특정 인명 / 음식명 / 助詞 agreement) 가 있었는지 직접 confirm 권장. follow-up 연락 가능하면 specifics 수집 후 §10-§14 incorporate.

### 15.4 원주민 인명 / 종족명 정책

현 Korean convention = Mandarin 한자 reading (阿美族 → 아메이족). Indigenous-respect 시 Austronesian endonym (Pangcah → 팡차흐) 가 better. Taiwan.md 가 explicit policy 채택 필요. 다른 lang 의 indigenous endonym 정책과 cross-lang align 권장.

### 15.5 Hokkien 음식명 일관성

蚵仔煎 (Hokkien → 어아젠) vs 滷肉飯 (Mandarin → 루러우판) 혼재. per-dish rationale documentation 필요. 결정 기준 candidates:

- (a) self-romanization 우선 (메뉴 board / 餐廳 사용 form)
- (b) Mandarin Pinyin 일률 (NIKL 표준 align)
- (c) per-dish historical etymology 별 결정 (本地 Hokkien-derived vs Mandarin-introduced)

### 15.6 대만 불교 인물 (證嚴/星雲/聖嚴 법사)

Pinyin-Korean 현대 표준이나 노년 한국 불교 문헌은 Sino-Korean 형 잔존. per-figure 확인 필요.

### 15.7 「대중 (大眾)」 동음이의 sweep

「대중」 = 台中 (Taichung) or 大眾 (general public) 동음이의. 현 corpus 전수조사 필요 — 「대중」 occurrence 의 몇 %가 Taichung 의미인지, 「타이중」 으로 치환 가능한지 audit candidate.

### 15.8 Frontmatter audit 별도 pass

§10 Step 1 에서 frontmatter (`description`, `title`, `imageAlt`, `tags`) 는 body-only grep 으로 안 잡힌다고 명시 — 但 별도 frontmatter audit 가 실제 run 된 적 없음. quarterly maintenance 의 candidate.

### 15.9 助詞 agreement 자동화

§10 Step 5 / §14.3 의 助詞 agreement post-edit grep 을 `article-health.py --check=ko-josa-agreement` plugin gate 로 자동화. consonant-final 한국어 단어 + 후행 vowel-final 조사 의 mismatch 패턴 catalogue 후 CI gate.

---

_v2.0 | 2026-05-25 — augmented with §10 per-instance judgment framework (감사→분류→판단→적용→검증 5-step + 助詞 agreement Korean-specific 鐵則) + §11 false-positive whitelist (12+ patterns from W1/W2f corpus audit) + §12 worked examples library (7 patterns shipped 2026-05-24/25 commits c2d7633e0 + 06fd23be3 + d1f99beee) + §13 Taiwan-first mental model 한국어 버전 (5 activation points) + §14 process discipline (worktree isolation / file-level git add / 助詞 grep protocol / commit message referential integrity / sub-agent inline guide). §15 expanded from 5 to 9 open questions including 이등휘/리덩후이 전체 변환, 대중 동음이의 sweep, frontmatter audit, 助詞 자동화. 觸發: 哲宇 2026-05-25 augmentation directive after W1/W2f ko cleanup ship — codify hard-won lessons before they drift._

_v1.0 | 2026-05-24 — derived from translation conventions audit triggered by Korean professional translator's callout at observer's talk. Evidence base in [reports/translation-research/ko-2026-05-24.md](../../../reports/translation-research/ko-2026-05-24.md)._
