#!/usr/bin/env python3
"""unify-translation-slugs.py — 非中文語言的翻譯檔統一使用 en slug。

背景（2026-07-17 哲宇 directive）：同一篇文章的 slug 在各語言理論上應該
一致（en slug = canonical，per getLangSwitchPath 原始設計）。巴別塔免費
模型翻譯時自作主張取名，累積 41 篇 / 98 檔漂移，是 hreflang / 切換器
死鏈家族的土壤。本工具把 ja/ko/es/fr（與 en 自身以外語言）檔名改成
en slug，並輸出 301 redirect 條目保住舊 URL 的搜尋權益。

防呆兩道：
  1. token 零重疊：en slug 與其他語言多數 slug 完全無共同字詞 → 疑似
     translatedFrom 錯指的殭屍對，跳過並列入 review 清單（不盲改）。
  2. 目標碰撞：該語言目錄已有同名檔 → 跳過並列入 review。

用法：
    python3 scripts/tools/unify-translation-slugs.py           # dry-run
    python3 scripts/tools/unify-translation-slugs.py --apply   # 執行 git mv
"""
import json
import subprocess
import sys
from collections import defaultdict
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
LANGS = ["en", "ja", "ko", "es", "fr"]
CAT_SLUG = {
    "History": "history", "Geography": "geography", "Culture": "culture",
    "Food": "food", "Art": "art", "Music": "music", "Technology": "technology",
    "Nature": "nature", "People": "people", "Society": "society",
    "Economy": "economy", "Lifestyle": "lifestyle", "About": "about",
    "Resources": "resources",
}


def tokens(slug):
    return set(t for t in slug.lower().replace("_", "-").split("-") if len(t) > 2)


def main():
    apply = "--apply" in sys.argv
    tr = json.loads((ROOT / "knowledge/_translations.json").read_text())

    by_zh = defaultdict(dict)  # zh path -> {lang: (Category, slug)}
    for langfile, zh in tr.items():
        parts = langfile.split("/")
        if len(parts) >= 3 and parts[0] in LANGS:
            by_zh[zh][parts[0]] = (parts[1], parts[2].removesuffix(".md"))

    renames = []   # (lang, cat, old_slug, new_slug)
    review = []    # (reason, zh, detail)

    for zh, entries in sorted(by_zh.items()):
        en = entries.get("en")
        if not en:
            continue
        en_cat, en_slug = en
        divergent = [(l, c, s) for l, (c, s) in entries.items()
                     if l != "en" and s != en_slug]
        if not divergent:
            continue

        other_slugs = [s for _, _, s in divergent]
        majority = max(set(other_slugs), key=other_slugs.count)
        if not (tokens(en_slug) & tokens(majority)):
            review.append(("token-零重疊（疑殭屍對）", zh,
                           f"en={en_slug} vs 多數={majority}"))
            continue

        for lang, cat, old_slug in divergent:
            target = ROOT / "knowledge" / lang / cat / f"{en_slug}.md"
            if target.exists():
                review.append(("目標碰撞", zh, f"{lang}/{cat}/{en_slug}.md 已存在"))
                continue
            renames.append((lang, cat, old_slug, en_slug))

    print(f"改名 {len(renames)} 檔 / review 跳過 {len(review)} 案")
    for reason, zh, detail in review:
        print(f"  ⚠️  [{reason}] {zh} — {detail}")

    redirect_lines = []
    for lang, cat, old, new in renames:
        cs = CAT_SLUG.get(cat, cat.lower())
        from urllib.parse import quote
        redirect_lines.append(
            f"/{lang}/{cs}/{quote(old)} /{lang}/{cs}/{quote(new)} 301")

    if not apply:
        for lang, cat, old, new in renames[:15]:
            print(f"  {lang}/{cat}/{old} → {new}")
        if len(renames) > 15:
            print(f"  …共 {len(renames)} 條（dry-run，--apply 執行）")
        return

    for lang, cat, old, new in renames:
        src = f"knowledge/{lang}/{cat}/{old}.md"
        dst = f"knowledge/{lang}/{cat}/{new}.md"
        subprocess.run(["git", "mv", src, dst], cwd=ROOT, check=True)
    print(f"✅ git mv {len(renames)} 檔完成")

    manual = ROOT / "config/redirects-manual.txt"
    marker = "# ── slug 統一改名"
    text = manual.read_text()
    if marker not in text:
        text += (
            f"\n{marker}（2026-07-17，巴別塔模型自作主張取名的歷史清償；"
            "en slug = canonical）──\n" + "\n".join(redirect_lines) + "\n")
        manual.write_text(text)
        print(f"✅ {len(redirect_lines)} 條 301 寫入 config/redirects-manual.txt")


if __name__ == "__main__":
    main()
