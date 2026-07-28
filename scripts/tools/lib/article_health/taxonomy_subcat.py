"""taxonomy_subcat — subcategory inference for frontmatter auto-heal.

Loads allowed subcategories from docs/taxonomy/SUBCATEGORY.md (when present)
and scores candidates against title / tags / filename / body keywords.

Used by frontmatter_format.fix() and contributor-pr-heal.

Design (2026-07-23 idlccp1984 instrument evolution):
  warn + lint + auto-heal + advanced-review-required
  - high confidence (≥0.55 unique) → auto-assign
  - medium → surface top-3 in WARN message, no write
  - no match → WARN missing only
"""

from __future__ import annotations

import re
from pathlib import Path
from typing import Any

_TAXONOMY_PATH = Path("docs/taxonomy/SUBCATEGORY.md")

# Keyword → subcategory boosts per category (complement taxonomy table).
# Keys matched against title + tags + filename + first 800 chars of body.
_KEYWORD_BOOSTS: dict[str, list[tuple[str, list[str]]]] = {
    "History": [
        ("殖民與帝國", ["荷西", "明鄭", "清治", "日治", "牡丹社", "羅發號", "李仙得", "開山撫番", "琉球"]),
        ("戰後與威權", ["戒嚴", "白色恐怖", "國府", "遷台", "美麗島", "綠島"]),
        ("民主與治理", ["民主", "選舉", "兩岸", "台海", "邦交", "聯合國", "北韓", "北朝鮮", "外交"]),
        ("軍事歷史", ["軍事", "金門", "馬祖", "湖口", "兵役", "漢光"]),
        ("史前與原住民", ["史前", "原住民", "考古"]),
        ("經濟發展史", ["經濟奇蹟", "產業", "四小龍"]),
        ("社會與日常史", ["眷村", "鐵道", "日常", "習俗"]),
        ("史觀與方法論", ["島史觀", "史觀"]),
    ],
    "Culture": [
        ("節慶與禮俗", ["節慶", "端午", "中元", "農曆", "普渡", "鬼月", "七月", "禮俗", "婚喪"]),
        ("宗教與民俗", ["廟", "媽祖", "信仰", "陣頭", "擲筊", "宗教"]),
        ("網路文化", ["迷因", "PTT", "VTuber", "YouTuber", "Komica", "鄉民", "網路"]),
        ("族群文化", ["原住民", "客家", "族群"]),
        ("語言與文字", ["語言", "母語", "注音", "外來語"]),
        ("工藝與美學", ["花布", "工藝", "茶道", "製香"]),
        ("出版與媒體", ["雜誌", "漫畫", "媒體"]),
        ("老街與商圈", ["老街"]),
        ("運動文化", ["棒球", "巧固球"]),
    ],
    "Economy": [
        ("企業列傳", ["企業", "公司", "品牌", "台積電", "鴻海", "萊爾富", "NET", "超商", "門市"]),
        ("經濟發展", ["產業", "轉型", "紡織", "製造", "傳產", "機械", "奧運", "機能"]),
        ("能源與永續", ["循環經濟", "綠能", "能源", "減碳", "回收"]),
        ("貿易與全球化", ["外貿", "供應鏈", "出口", "貿易"]),
        ("金融與科技", ["金融", "fintech", "支付", "銀行"]),
        ("農業經濟", ["農業", "農村"]),
        ("新創經濟", ["新創", "startup"]),
        ("文化產業", ["動畫", "文創"]),
        ("庶民經濟", ["夜市"]),
    ],
    "Society": [
        ("社會制度", ["兵役", "當兵", "義務役", "役男", "教召", "金馬獎", "替代役", "制度", "颱風假"]),
        ("民主與政治", ["選舉", "政治", "太陽花", "野百合", "民主"]),
        ("國際關係", ["邦交", "外交", "國際"]),
        ("媒體與言論", ["媒體", "新聞", "言論", "迷因"]),
        ("人權與平等", ["人權", "同婚", "性別", "移工"]),
        ("社會運動", ["社運", "公民", "抗議"]),
        ("社區與日常", ["社區", "里長", "阿姨", "日常"]),
        ("教育", ["教育", "升學", "學校"]),
        ("社會福利", ["長照", "社會住宅", "福利"]),
        ("社會韌性", ["災難", "志工", "韌性", "國防"]),
    ],
    "Lifestyle": [
        ("城市生活", ["便利商店", "超商", "垃圾車", "騎樓", "小綠人"]),
        ("交通與移動", ["捷運", "機車", "交通", "高鐵"]),
        ("醫療與健保", ["健保", "醫療"]),
    ],
    "Geography": [
        ("島嶼與海洋", ["離島", "島嶼", "海洋"]),
        ("地標", ["101", "地標"]),
        ("交通與基礎設施", ["交通", "基建", "基礎設施"]),
    ],
    "Technology": [
        ("網路與社群", ["PTT", "批踢踢", "社群", "網路"]),
    ],
    "Food": [
        ("經典小吃", ["小吃", "夜市", "滷肉", "牛肉麵"]),
        ("飲品文化", ["珍奶", "手搖", "咖啡", "豆漿"]),
    ],
    "People": [
        ("政治人物", ["總統", "市長", "立委", "政治"]),
        ("企業家", ["創辦人", "董事長", "企業家"]),
    ],
    "Nature": [
        ("生態保育", ["保育", "生態", "瀕危"]),
        ("地質地形", ["地質", "地形", "火山", "溫泉"]),
    ],
    "Music": [
        ("流行音樂", ["流行", "歌手", "樂團"]),
        ("原住民音樂", ["原住民"]),
    ],
    "Art": [
        ("文學", ["文學", "小說", "詩"]),
        ("視覺藝術", ["繪畫", "藝術家", "美術館"]),
    ],
}


def _parse_taxonomy_file() -> dict[str, list[str]]:
    """category → list of subcategory names from SUBCATEGORY.md tables."""
    if not _TAXONOMY_PATH.exists():
        return {}
    text = _TAXONOMY_PATH.read_text(encoding="utf-8")
    result: dict[str, list[str]] = {}
    current: str | None = None
    # ### 📜 History（歷史） or ### History
    header_re = re.compile(
        r"^###\s+(?:[^\w]*\s*)?([A-Za-z]+)(?:（[^）]+）)?\s*$",
        re.MULTILINE,
    )
    # | 子分類名 | 說明 |
    row_re = re.compile(r"^\|\s*([^|]+?)\s*\|\s*([^|]*?)\s*\|")

    for line in text.splitlines():
        hm = header_re.match(line.strip())
        if hm:
            current = hm.group(1).strip()
            result.setdefault(current, [])
            continue
        if current is None:
            continue
        if not line.startswith("|"):
            continue
        rm = row_re.match(line)
        if not rm:
            continue
        name = rm.group(1).strip()
        if name in ("Sub-Category", "子分類", "---", "----") or set(name) <= {"-", " "}:
            continue
        if name.startswith("-") or "Sub-Category" in name:
            continue
        # skip separator rows like | --- |
        if re.fullmatch(r"[-: ]+", name):
            continue
        if name not in result[current]:
            result[current].append(name)
    return result


def allowed_subcategories(category: str) -> list[str]:
    tax = _parse_taxonomy_file()
    names = list(tax.get(category, []))
    # Always include keyword-boost labels even if taxonomy parse missed them
    for sub, _ in _KEYWORD_BOOSTS.get(category, []):
        if sub not in names:
            names.append(sub)
    return names


def suggest_subcategory(
    category: str,
    *,
    title: str = "",
    tags: list[str] | None = None,
    filename: str = "",
    body: str = "",
    top_n: int = 3,
) -> list[tuple[str, float, str]]:
    """Return [(subcategory, score, reason), ...] sorted by score desc."""
    tags = tags or []
    hay = " ".join(
        [
            title or "",
            filename or "",
            " ".join(str(t) for t in tags),
            (body or "")[:1200],
        ]
    )
    scores: dict[str, float] = {}
    reasons: dict[str, str] = {}

    for sub, kws in _KEYWORD_BOOSTS.get(category, []):
        hits = [kw for kw in kws if kw and kw in hay]
        if not hits:
            continue
        # base 0.35 + 0.12 per hit, cap 0.95
        score = min(0.95, 0.35 + 0.12 * len(hits))
        # filename exact-ish boost
        if any(kw in (filename or "") for kw in kws):
            score = min(0.98, score + 0.15)
        if score > scores.get(sub, 0):
            scores[sub] = score
            reasons[sub] = "keywords: " + "、".join(hits[:4])

    # Also score against taxonomy names appearing literally in title/filename
    for sub in allowed_subcategories(category):
        if sub in (title or "") or sub in (filename or ""):
            scores[sub] = max(scores.get(sub, 0), 0.8)
            reasons[sub] = reasons.get(sub, "literal name in title/filename")

    ranked = sorted(scores.items(), key=lambda x: (-x[1], x[0]))
    return [(s, sc, reasons.get(s, "")) for s, sc in ranked[:top_n]]


def pick_auto_subcategory(
    category: str,
    **kwargs: Any,
) -> tuple[str, float, str] | None:
    """High-confidence pick for auto-heal, or None.

    Requires top score ≥ 0.55 and either unique or margin ≥ 0.08 over #2.
    """
    ranked = suggest_subcategory(category, top_n=3, **kwargs)
    if not ranked:
        return None
    top_sub, top_score, reason = ranked[0]
    if top_score < 0.55:
        return None
    if len(ranked) >= 2 and (top_score - ranked[1][1]) < 0.08:
        return None  # ambiguous — advanced review
    return top_sub, top_score, reason
