#!/usr/bin/env python3
"""person-fidelity-check.py — 譯文重要政治人物張冠李戴偵測。

2026-07-18 出生戰役：id/taiwan-democratization 把「陳水扁」（美麗島大審辯護律師、
2000 首位政黨輪替總統）系統性譯成「Tsai Ing-wen」——蔡英文 1980 年還是學生。這是
讀者級事實錯誤（懂台灣史的人一眼看破），geo-fidelity 抓不到（不是地點）。

機制（同 geo-fidelity 的「譯文有、源頭零」強訊號）：譯文若出現某總統的羅馬拼音，
但 zh 源完全沒有對應漢字名 → 疑似張冠李戴，flag 人審對照。只收台灣最易混淆、
一旦錯最傷的政治人物（總統群），保守設計避免正常提及的誤報。

用法：python3 person-fidelity-check.py --lang vi
Exit 1 = 有可疑替換。
"""

from __future__ import annotations

import argparse
import re
import sys
from pathlib import Path

REPO = Path(__file__).resolve().parents[3]
KNOWLEDGE = REPO / "knowledge"

# (漢字名, [羅馬拼音變體 regex])。最易混淆的台灣總統群——錯了最傷可信度。
FIGURES = [
    # ar/ru 2026-07-25 birth: canonical forms sourced from TRANSLATION-ar.md §2 /
    # TRANSLATION-ru.md §2 (both cross-verified against ≥1 real source this
    # session). 蔣經國/蔣介石 is the exact confusion-family trap flagged by both
    # guides — kept as separate FIGURES rows below per the existing pattern.
    ("蔡英文", r"Tsai Ing-wen|Thái Anh Văn|त्साई इंग-वेन|تساي إنغ ون|Цай Инвэнь"),
    ("陳水扁", r"Chen Shui-bian|Trần Thủy Biển|चेन शुई-बियान|تشن شوي بيان|Чэнь Шуйбянь"),
    ("馬英九", r"Ma Ying-jeou|Mã Anh Cửu|मा यिंग-जेउ|ما يينغ جيو|Ма Инцзю"),
    ("李登輝", r"Lee Teng-hui|Lý Đăng Huy|ली तेंग-हुई|لي تنغ هوي|Ли Дэнхуэй"),
    ("蔣經國", r"Chiang Ching-kuo|Tưởng Kinh Quốc|चियांग चिंग-कुओ|تشيانغ تشينغ كو|Цзян Цзинго"),
    ("蔣介石", r"Chiang Kai-shek|Tưởng Giới Thạch|चियांग काई-शेक|تشيانغ كاي شيك|Чан Кайши"),
    ("賴清德", r"Lai Ching-te|Lại Thanh Đức|William Lai|लाई चिंग-ते|لاي تشينغ تي|Лай Циндэ"),
    ("馬英九", r"Ma Ying-jeou"),
]


def strip_frontmatter(text: str) -> str:
    m = re.match(r"^---\n.*?\n---\n", text, re.S)
    return text[m.end():] if m else text


def find_zh_source(trans_path: Path):
    text = trans_path.read_text(encoding="utf-8")
    m = re.search(r"^translatedFrom:\s*['\"]?([^'\"\n]+)['\"]?", text, re.M)
    if not m:
        return None
    p = KNOWLEDGE / m.group(1).strip()
    return p if p.exists() else None


def check_file(trans_path: Path):
    zh_path = find_zh_source(trans_path)
    if zh_path is None:
        return []
    zh_body = strip_frontmatter(zh_path.read_text(encoding="utf-8"))
    trans_text = trans_path.read_text(encoding="utf-8")
    trans_body = strip_frontmatter(trans_text)
    offset = trans_text[: len(trans_text) - len(trans_body)].count("\n")

    # 紀念堂/紀念館/機場/路名 等以人名命名的地標合法（中正紀念堂 = Chiang Kai-shek
    # Memorial，zh 源用「中正」不含「蔣介石」，會誤報）
    LANDMARK = re.compile(
        r"memorial|mausol|monument|tưởng niệm|aula|balai|स्मारक|"
        r"airport|sân bay|bandara|हवाई अड्डा|統一大道|avenida|jalan|đường",
        re.I,
    )
    # 同人異名變體：蔣介石=蔣中正（官章名）、兩蔣（父子合稱，譯文合理展開成兩全名）
    # 2026-07-18 id agent 揭露：金馬獎/白色恐怖 zh 源用「蔣中正」「兩蔣」，checker 只比對
    # 「蔣介石」字面 → 誤 flag 正確譯文
    ALIASES = {
        "蔣介石": ["蔣介石", "蔣中正", "兩蔣", "蒋介石", "蒋中正"],
        "蔣經國": ["蔣經國", "兩蔣", "蒋经国"],
    }
    hits = []
    for han, romaji in FIGURES:
        zh_names = ALIASES.get(han, [han])
        if any(n in zh_body for n in zh_names):
            continue  # zh 源真有這個人（含異名變體）→ 合法
        pat = re.compile(romaji, re.I)
        for i, line in enumerate(trans_body.splitlines(), start=offset + 1):
            if pat.search(line) and not LANDMARK.search(line):
                hits.append((han, i, line.strip()[:90]))
    return hits


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--lang")
    ap.add_argument("--files", nargs="*")
    args = ap.parse_args()

    if args.files:
        files = [Path(f) for f in args.files]
    elif args.lang:
        files = sorted((KNOWLEDGE / args.lang).rglob("*.md"))
    else:
        ap.error("--lang or --files required")

    total = 0
    for f in files:
        hits = check_file(f)
        if hits:
            total += len(hits)
            rel = f.relative_to(REPO) if f.is_absolute() else f
            print(f"⚠️  {rel}")
            for han, line_no, ctx in hits[:6]:
                print(f"    [zh 源無「{han}」] L{line_no}: {ctx}")
    if total:
        print(f"\n❌ {total} 處疑似人物張冠李戴（譯文提某總統但 zh 源無其名）— 需人審")
        sys.exit(1)
    print(f"✅ {len(files)} 檔無可疑人物替換")


if __name__ == "__main__":
    main()
