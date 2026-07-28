#!/usr/bin/env python3
"""script-presence-check.py — 譯文語言真偽檢查（偵測「宣稱已譯」但實際仍是英文的檔案）。

2026-07-19 讀者揭露起點：knowledge/ja/History/taiwan-democratization.md 的
translatedAt frontmatter 顯示已譯，本文卻是完全獨立措辭的英文（不是 en 檔的複製，
是另一次英文改寫）。追查擴大到 fr 10 檔 + es 14 檔，其中 6 篇（united-front-tour-
groups / complex-life-festival / taiwan-generations / huang-shan-liao /
taiwan-white-terror / psychological-warfare）三語同時中鏢——不是單一 batch script
bug（fr/es 同批 translatedAt 但 ja 是三週後的獨立 production run），比較像是特定
zh 來源文章（多為主權敏感題材：統戰/白色恐怖/心戰/認知作戰）持續讓某些 backend
「配合但用英文回答」而非依指示輸出目標語言。

translate.py 的既有 hard gate（frontmatter fence / YAML / footnote 數 / 檔案大小，
見 translate_one()）完全不驗證輸出語言本身——語意流暢的英文假翻譯會直接通過所有
既有閘門存活到 commit。這支是補上「輸出真的是目標語言」這道從未存在過的閘。

機制：依語言文字系統特性分兩種檢測法：
  (1) 非拉丁字母語言（ja/ko/hi）：目標文字系統字元數 = 0 → 幾乎確定英文殘留（強訊號，
      正常語料不可能整篇零筆）。
  (2) 有特殊變音符號的拉丁語言（fr/es/pt/vi）：全文變音符號數 = 0 且本文夠長（≥300
      字）→ 高度可疑（這幾語的長文幾乎不可能完全不含一個變音符號）。
  id（印尼文）沒有可靠變音符號區辨——用功能詞比對代替：算英文常見功能詞 vs 印尼文
  常見功能詞出現次數，英文數 ≥ 印尼文數 × 3 且英文數 ≥ 10 → 高度可疑。

用法：
    python3 script-presence-check.py --lang ja
    python3 script-presence-check.py --lang all
Exit 1 = 有可疑英文殘留檔案。
"""

from __future__ import annotations

import argparse
import re
import sys
from pathlib import Path

REPO = Path(__file__).resolve().parents[3]
KNOWLEDGE = REPO / "knowledge"

NATIVE_SCRIPT = {
    "ja": re.compile(r"[ぁ-んァ-ヶ]"),  # hiragana + katakana（漢字單獨不夠——en/zh 混排也有漢字）
    "ko": re.compile(r"[가-힣]"),
    "hi": re.compile(r"[अ-ह]"),
    # ar/ru 2026-07-25 birth: both are distinct-script (non-Latin) languages like
    # ja/ko/hi, so they get the strongest signal (0 native-script chars in a
    # non-trivial body = near-certain English leak) rather than the weaker
    # DIACRITICS heuristic used for Latin-alphabet targets.
    "ar": re.compile(r"[؀-ۿݐ-ݿﭐ-﷿ﹰ-﻿]"),  # Arabic + Arabic Supplement + Presentation Forms A/B
    "ru": re.compile(r"[а-яА-ЯёЁ]"),  # Cyrillic
}

DIACRITICS = {
    "fr": re.compile(r"[éèêëàâäùûüçôöîï]", re.I),
    "es": re.compile(r"[áéíóúñ¿¡]", re.I),
    "pt": re.compile(r"[ãõáéíóúâêôç]", re.I),
    "vi": re.compile(
        r"[ăâđêôơưàáảãạằắẳẵặầấẩẫậèéẻẽẹềếểễệìíỉĩịòóỏõọồốổỗộờớởỡợùúủũụừứửữựỳýỷỹỵ]",
        re.I,
    ),
}
DIACRITIC_MIN_BODY_LEN = 300

ID_FUNCTION_WORDS = {
    "yang", "dan", "di", "ini", "itu", "dengan", "untuk", "adalah", "dari",
    "pada", "tidak", "akan", "atau", "juga", "dalam", "ke", "oleh", "sebagai",
    "telah", "para", "dapat", "menjadi", "bisa", "karena", "saat", "setelah",
    "tahun", "orang", "yaitu", "namun", "seperti", "hingga", "antara",
}
EN_FUNCTION_WORDS = {
    "the", "and", "of", "is", "was", "that", "with", "from", "this", "these",
    "those", "has", "have", "had", "were", "are", "will", "would", "could",
    "should", "which", "who", "what", "when", "where", "why", "how", "not",
    "but", "for", "on", "in", "at", "to", "as", "by", "an", "it", "its",
}
FUNCTION_WORD_RATIO_MIN = 3
FUNCTION_WORD_EN_MIN = 10

SUPPORTED_LANGS = sorted(set(NATIVE_SCRIPT) | set(DIACRITICS) | {"id"})


def strip_frontmatter(text: str) -> str:
    m = re.match(r"^---\n.*?\n---\n", text, re.S)
    return text[m.end():] if m else text


def _word_count(pattern_words: set[str], body: str) -> int:
    total = 0
    for w in pattern_words:
        total += len(re.findall(rf"\b{re.escape(w)}\b", body, re.I))
    return total


def check_text(body: str, lang: str):
    """Return (verdict, detail) or None if clean. verdict is a short tag.

    Operates on an already-stripped body string so translate.py's hard gate
    can call this on in-memory backend output before writing to disk — same
    logic the CLI uses on committed files via check_file().
    """
    if lang in NATIVE_SCRIPT:
        count = len(NATIVE_SCRIPT[lang].findall(body))
        if count == 0 and len(body.strip()) > 50:
            return "NO_NATIVE_SCRIPT", f"0 個 {lang} 原生文字字元（本文 {len(body)} 字）"
        return None

    if lang in DIACRITICS:
        if len(body.strip()) < DIACRITIC_MIN_BODY_LEN:
            return None  # 太短的檔案（如 hub）不判定
        count = len(DIACRITICS[lang].findall(body))
        if count == 0:
            return "NO_DIACRITICS", f"0 個 {lang} 變音符號（本文 {len(body)} 字）"
        return None

    if lang == "id":
        en_count = _word_count(EN_FUNCTION_WORDS, body)
        id_count = _word_count(ID_FUNCTION_WORDS, body)
        if en_count >= FUNCTION_WORD_EN_MIN and en_count >= id_count * FUNCTION_WORD_RATIO_MIN:
            return "EN_FUNCTION_WORD_DOMINANT", f"英文功能詞 {en_count} 次 vs 印尼文功能詞 {id_count} 次"
        return None

    return None


def check_file(path: Path, lang: str):
    """Return (verdict, detail) or None if clean. Reads + strips frontmatter, then check_text()."""
    body = strip_frontmatter(path.read_text(encoding="utf-8"))
    return check_text(body, lang)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--lang", required=True, help=f"語言代碼，或 'all' 掃全部支援語言（{', '.join(SUPPORTED_LANGS)}）")
    ap.add_argument("--files", nargs="*")
    args = ap.parse_args()

    langs = SUPPORTED_LANGS if args.lang == "all" else [args.lang]

    total_hits = 0
    total_files = 0
    for lang in langs:
        if lang not in SUPPORTED_LANGS:
            print(f"⚠️  不支援的語言: {lang}（支援: {', '.join(SUPPORTED_LANGS)}）", file=sys.stderr)
            continue
        if args.files:
            files = [Path(f) for f in args.files]
        else:
            lang_dir = KNOWLEDGE / lang
            if not lang_dir.exists():
                continue
            files = sorted(lang_dir.rglob("*.md"))

        lang_hits = 0
        for f in files:
            total_files += 1
            result = check_file(f, lang)
            if result:
                lang_hits += 1
                total_hits += 1
                verdict, detail = result
                rel = f.relative_to(REPO) if f.is_absolute() else f
                print(f"⚠️  [{lang}] {rel}")
                print(f"    [{verdict}] {detail}")
        if lang_hits:
            print(f"── {lang}: {lang_hits}/{len(files)} 檔可疑英文殘留\n")

    if total_hits:
        print(f"\n❌ {total_hits} 檔可疑「宣稱已譯但實為英文」— 需人審 + 重譯")
        sys.exit(1)
    print(f"✅ {total_files} 檔語言真偽檢查通過")


if __name__ == "__main__":
    main()
