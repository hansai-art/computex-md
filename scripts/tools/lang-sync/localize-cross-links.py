#!/usr/bin/env python3
"""localize-cross-links.py — 站內連結在地化：把譯文裡指向中文 slug 的連結改成該語言網址。

背景：reports/cross-link-localization-2026-07-27.md。translate.py /
structured-translate.py / patch-translate.py 三個引擎都指示模型「URL 原樣保留」——
對外部引用正確，對站內連結錯誤。結果 13,155 個譯文內文連結還指著中文 slug，
線上實測全部 404（`generate-article-aliases.mjs` 的 alias 解決的是另一個方向：讀者
把中文網址加 `/en/` 前綴猜測，不涵蓋「譯文內文指向中文 slug」這類）。

純機械查表，零模型呼叫。核心判準邏輯在 `cross_link_localizer.py`（兩邊共用）：

  1. 只處理 `[文字](/path)` 形式、不含 http 的連結（外部引用不動）
  2. 從 path 取出「分類/slug」（可能已有語言前綴，也可能沒有；不論前綴是誰，一律
     剝掉重建——這篇文章本身就活在 `lang` 目錄下，內文連結該指回它自己的語言）
  3. slug 含中文 → 查 `knowledge/_translations.json` 反查索引：該 zh 檔在當前語言
     有沒有譯文？有 → 改寫成 `/{lang}/{分類小寫}/{該語言的 slug}`；查無 → 完全不動
  4. slug 是拉丁字母但缺語言前綴（如 `/music/foo`）→ 查該 slug 在當前語言是否真的
     存在（`{lang}/{Category}/{slug}.md`）；存在才補前綴，不存在就不動
  5. 已經是 `/{lang}/{分類}/{拉丁slug}` 但分類大小寫不對 → 只修大小寫
  6. 錨點（`#foo`）/ query 保留在原位；trailing slash 依原連結樣式保留（站方兩種
     都收，change 面越小越安全）
  7. `resources` 分類沒有 per-article 路由（astro `CATEGORY_MAPPING` 沒收，只有
     `/resources` 這個靜態策展頁）——改了格式也還是 404，排除在外，留著不動不會
     讓現狀更差
  8. zh 根目錄的原文（`knowledge/{Category}/*.md`，非語言子目錄）完全不碰——只掃
     `knowledge/{lang}/**/*.md`，結構上就不會touch到 zh 正本

這個 CLI 是「存量批次修復」（第一段）。第二段（防新增）在三個翻譯引擎的
body 送模型前先呼叫 `cross_link_localizer.localize_body()`——模型看到的 URL
已經是目標語言的，「URL 原樣保留」的指示對站內連結也變成對的。

用法：
    python3 localize-cross-links.py --lang en                  # dry-run（預設）
    python3 localize-cross-links.py --lang en --apply          # 真的寫檔
    python3 localize-cross-links.py --all --apply
    python3 localize-cross-links.py --lang en --apply \
        --changed-files-out /tmp/en-changed.txt                # 供後續 article-health 用
"""

from __future__ import annotations

import argparse
import re
from pathlib import Path

from cross_link_localizer import (
    KNOWLEDGE,
    LANGS,
    REPO,
    LocalizerIndex,
    localize_url,
    load_index,
)

LINK_RE = re.compile(r"\[([^\]]*)\]\((/[^)\s]+)\)")


def process_file(
    path: Path,
    lang: str,
    index: LocalizerIndex,
    apply: bool,
) -> tuple[dict[str, int], list[tuple[str, str]]]:
    text = path.read_text(encoding="utf-8")
    stats = {"rewritten": 0, "no-translation": 0, "already-correct": 0, "skip": 0}
    changes: list[tuple[str, str]] = []

    def _sub(m: re.Match) -> str:
        title, url = m.group(1), m.group(2)
        new_url, status = localize_url(url, lang, index)
        stats[status] += 1
        if status == "rewritten" and new_url:
            changes.append((url, new_url))
            return f"[{title}]({new_url})"
        return m.group(0)

    new_text = LINK_RE.sub(_sub, text)
    if apply and changes:
        path.write_text(new_text, encoding="utf-8")

    return stats, changes


def run(lang: str, index: LocalizerIndex, apply: bool, show_samples: int):
    lang_dir = KNOWLEDGE / lang
    if not lang_dir.exists():
        print(f"⚠️  {lang}: knowledge/{lang}/ 不存在，略過")
        return {"rewritten": 0, "no-translation": 0, "already-correct": 0, "skip": 0}, [], []

    total = {"rewritten": 0, "no-translation": 0, "already-correct": 0, "skip": 0}
    changed_files: list[Path] = []
    samples: list[tuple[Path, str, str]] = []

    for md in sorted(lang_dir.rglob("*.md")):
        stats, changes = process_file(md, lang, index, apply)
        for k in total:
            total[k] += stats[k]
        if changes:
            changed_files.append(md)
            for old, new in changes[:show_samples]:
                if len(samples) < show_samples:
                    samples.append((md, old, new))

    return total, changed_files, samples


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    g = ap.add_mutually_exclusive_group(required=True)
    g.add_argument("--lang", choices=sorted(LANGS), help="只處理單一語言")
    g.add_argument("--all", action="store_true", help="處理所有翻譯語言")
    ap.add_argument("--dry-run", action="store_true", help="（預設行為，此旗標僅供明示）")
    ap.add_argument("--apply", action="store_true", help="真的寫檔（預設 dry-run 不寫）")
    ap.add_argument("--show-samples", type=int, default=5, help="每語言印出幾筆改寫範例")
    ap.add_argument("--changed-files-out", type=str, default=None,
                     help="把有改動的檔案路徑（repo-relative，換行分隔）寫進這個檔案，供後續 article-health 用")
    args = ap.parse_args()

    apply = args.apply
    langs = sorted(LANGS) if args.all else [args.lang]

    index = load_index()

    print(f"{'模式：真的寫檔 --apply' if apply else '模式：dry-run（不寫檔，只統計）'}")
    print(f"分類白名單（{len(index.cat_map)}）：{', '.join(sorted(index.cat_map.values()))}")
    print()

    grand_total = {"rewritten": 0, "no-translation": 0, "already-correct": 0, "skip": 0}
    all_changed_files: list[Path] = []

    header = f"{'語言':<6}{'可改寫':>10}{'查無對應保留':>14}{'已正確':>10}{'skip':>10}"
    print(header)
    print("-" * len(header))

    for lang in langs:
        total, changed_files, samples = run(lang, index, apply, args.show_samples)
        for k in grand_total:
            grand_total[k] += total[k]
        all_changed_files.extend(changed_files)
        print(f"{lang:<6}{total['rewritten']:>10}{total['no-translation']:>14}{total['already-correct']:>10}{total['skip']:>10}"
              f"   ({len(changed_files)} 檔案有改動)")
        for md, old, new in samples:
            rel = md.relative_to(REPO)
            print(f"    {rel}: {old} → {new}")

    print("-" * len(header))
    print(f"{'合計':<6}{grand_total['rewritten']:>10}{grand_total['no-translation']:>14}{grand_total['already-correct']:>10}{grand_total['skip']:>10}"
          f"   ({len(all_changed_files)} 檔案有改動)")

    if args.changed_files_out:
        out_path = Path(args.changed_files_out)
        out_path.write_text(
            "\n".join(str(p.relative_to(REPO)) for p in all_changed_files) + ("\n" if all_changed_files else ""),
            encoding="utf-8",
        )
        print(f"\n改動檔案清單寫入：{out_path}")

    if not apply and grand_total["rewritten"] > 0:
        print("\n(dry-run 沒有寫檔。確認統計無誤後加 --apply 真的寫。)")


if __name__ == "__main__":
    main()
