#!/usr/bin/env python3
"""punct-cleanup.py — 標點淨化 campaign 的工作清單產生器 + 事實保真驗證器。

2026-07-19 哲宇選項3 legacy campaign 工具。144 篇 legacy（破折號>15 或全形分號>12）
要交給 codex (sol/luna/terra) + ollama 協作清標點。核心風險：外部 agent 看不到當初
的對話，可能在「改標點」時不小心改到事實。這支把「只改標點、零事實漂移」變成機械
可驗證的閘，不靠 agent 自律。

兩個 mode：

  # 產生工作清單（144 篇 + 每篇破折號/分號數 + category + featured）
  python3 scripts/tools/punct-cleanup.py --worklist

  # 驗證一篇清完的檔 vs git HEAD（改前）——事實保真 + gate pass
  python3 scripts/tools/punct-cleanup.py --verify knowledge/Society/認知作戰.md

--verify 檢查（任一 FAIL = 這次清理動到不該動的東西，必須 revert 重做）：
  1. frontmatter 逐字節不變
  2. 腳註 marker 集合 + 定義數不變（45/45 這種）
  3. 所有數字串（年份/金額/里程/統計）multiset 不變 —— 抓改到數字的事實漂移
  4. 所有「」『』引號內容 multiset 不變 —— 抓改到引語
  5. 所有 [連結文字](url) 的 url 不變 —— 抓改到來源
  6. em-dash ≤ 15 且 全形分號（正文，排除腳註）≤ 12 —— 達標
  7. article-health --profile=pre-commit hard=0 —— 過觸檔即硬 gate + 所有其他 hard 檢查

門檻說明：清理目標是「過未來的全站 hard gate」= em-dash ≤ 15、分號 ≤ 12。
能再往 EDITORIAL 理想（破折號 ≤ 4-8、分號 ≤ 3）更好，但**寧可少改也不要為了壓數字
而改到語意或事實**。#6 只要求達到 gate 門檻，不強迫壓到理想值。
"""

from __future__ import annotations

import argparse
import re
import subprocess
import sys
from pathlib import Path

REPO = Path(__file__).resolve().parents[2]
KNOWLEDGE = REPO / "knowledge"

# SSOT：破折號/分號的「可編輯正文」判定跟 prose-health gate 共用同一 predicate，兩邊不漂
# （2026-07-19 campaign 揭：raw 全 body 計數會把 blockquote/腳註/圖說/書名/參考裝置等
#  鐵律禁改的合法區也數進去，引用/書名多的文章正文清乾淨也過不了 → gate 與 verifier 都改
#  只數可編輯正文的修辭性用法）。
sys.path.insert(0, str(Path(__file__).resolve().parent))
from lib.article_health.checks.prose_health import _uneditable_punct_predicate as _uneditable

# gate 門檻（跟 article-health.config.toml pre-commit override 對齊）
EMDASH_MAX = 15
SEMICOLON_MAX = 12

_RE_EMDASH = re.compile(r"——")
_RE_SEMICOLON = re.compile(r"；")
_RE_FN_MARKER = re.compile(r"\[\^[0-9A-Za-z_-]+\]")
_RE_FN_DEF = re.compile(r"(?m)^\[\^[0-9A-Za-z_-]+\]:")
_RE_DIGITS = re.compile(r"\d+(?:[.,]\d+)*")
_RE_QUOTE = re.compile(r"[「『]([^「」『』]*)[」』]")
_RE_MD_URL = re.compile(r"\]\((https?://[^)]+)\)")
_RE_FM = re.compile(r"^---\n.*?\n---\n", re.S)


def _strip_fm(text: str) -> str:
    m = _RE_FM.match(text)
    return text[m.end():] if m else text


def _fm_block(text: str) -> str:
    m = _RE_FM.match(text)
    return text[: m.end()] if m else ""


def _editable_counts(text: str) -> tuple[int, int]:
    """(可編輯正文破折號數, 分號數)。跟 prose-health gate 用同一 predicate，只數修辭性用法。

    先移除 frontmatter + code fence + HTML 區塊（近似 prose-health 的 body_without_protected），
    再用共用 predicate 排除 blockquote/腳註/圖說/書名/參考裝置。與 gate 計數對齊。
    """
    body = _strip_fm(text)
    body = re.sub(r"```.*?```", "", body, flags=re.S)
    body = re.sub(r"<(div|iframe)[\s\S]*?</\1>", "", body)
    is_un = _uneditable(body)
    dash = sum(1 for m in _RE_EMDASH.finditer(body) if not is_un(m.start()))
    semi = sum(1 for m in _RE_SEMICOLON.finditer(body) if not is_un(m.start()))
    return dash, semi


# ── worklist ──────────────────────────────────────────────────────────────

def _iter_zh_articles():
    for cat in sorted(KNOWLEDGE.iterdir()):
        if not cat.is_dir() or cat.name.startswith((".", "_")):
            continue
        # skip translation dirs (2-letter lang codes)
        if len(cat.name) <= 3 and cat.name.islower():
            continue
        for f in sorted(cat.glob("*.md")):
            if f.name.startswith("_"):
                continue
            yield f


def worklist():
    rows = []
    for f in _iter_zh_articles():
        text = f.read_text(encoding="utf-8")
        body = _strip_fm(text)
        # em-dash: exclude the 《…——…》 book-title & quote-attribution lines is hard to do
        # generically; count raw and let the agent apply the known exceptions.
        dash, semi = _editable_counts(text)
        if dash > EMDASH_MAX or semi > SEMICOLON_MAX:
            featured = bool(re.search(r"(?m)^featured:\s*true", text))
            rows.append((f.relative_to(REPO), dash, semi, f.parent.name, featured))
    rows.sort(key=lambda r: -(r[1] + r[2]))
    print(f"# 標點淨化 campaign 工作清單 — {len(rows)} 篇（破折號>{EMDASH_MAX} 或 分號>{SEMICOLON_MAX}）")
    print(f"# 產生：punct-cleanup.py --worklist")
    print(f"# 欄位：path\\tem_dash\\tsemicolon\\tcategory\\tfeatured")
    for path, dash, semi, cat, feat in rows:
        print(f"{path}\t{dash}\t{semi}\t{cat}\t{'featured' if feat else '-'}")
    return rows


# ── verify ────────────────────────────────────────────────────────────────

def _git_head(path: Path) -> str | None:
    rel = path.relative_to(REPO) if path.is_absolute() else path
    try:
        out = subprocess.run(
            ["git", "-C", str(REPO), "show", f"HEAD:{rel}"],
            capture_output=True, text=True, timeout=30,
        )
        return out.stdout if out.returncode == 0 else None
    except Exception:
        return None


def _multiset_diff(old_list, new_list):
    """回傳 (只在 old 缺的, 只在 new 多的)。用 Counter。"""
    from collections import Counter
    co, cn = Counter(old_list), Counter(new_list)
    missing = list((co - cn).elements())
    added = list((cn - co).elements())
    return missing, added


def verify(path: Path) -> bool:
    path = path if path.is_absolute() else (REPO / path)
    new = path.read_text(encoding="utf-8")
    old = _git_head(path)
    fails = []

    if old is None:
        print(f"⚠️  {path.name}: git HEAD 無此檔（新檔？）— 只能跑達標 + gate 檢查，跳過事實比對")
    else:
        # 1. frontmatter 逐字節
        if _fm_block(old) != _fm_block(new):
            fails.append("frontmatter 被改動（campaign 只准動正文標點）")
        # 2. 腳註
        old_fn = _RE_FN_MARKER.findall(old); new_fn = _RE_FN_MARKER.findall(new)
        miss, add = _multiset_diff(old_fn, new_fn)
        if miss or add:
            fails.append(f"腳註 marker 變動：缺 {miss[:5]} 多 {add[:5]}")
        if len(_RE_FN_DEF.findall(old)) != len(_RE_FN_DEF.findall(new)):
            fails.append(f"腳註定義數變動：{len(_RE_FN_DEF.findall(old))}→{len(_RE_FN_DEF.findall(new))}")
        # 3. 數字 multiset
        miss, add = _multiset_diff(_RE_DIGITS.findall(old), _RE_DIGITS.findall(new))
        if miss or add:
            fails.append(f"數字變動（事實漂移！）：缺 {miss[:8]} 多 {add[:8]}")
        # 4. 引號內容 multiset
        miss, add = _multiset_diff(_RE_QUOTE.findall(old), _RE_QUOTE.findall(new))
        if miss or add:
            fails.append(f"引號內容變動（引語漂移！）：缺 {[m[:20] for m in miss[:5]]} 多 {[a[:20] for a in add[:5]]}")
        # 5. URL
        miss, add = _multiset_diff(_RE_MD_URL.findall(old), _RE_MD_URL.findall(new))
        if miss or add:
            fails.append(f"連結 URL 變動：缺 {miss[:3]} 多 {add[:3]}")

    # 6. 達標（可編輯正文修辭性用法；禁改合法區不計）
    dash, semi = _editable_counts(new)
    if dash > EMDASH_MAX:
        fails.append(f"破折號 {dash} > {EMDASH_MAX}（可編輯正文仍超，繼續清；書名/引語出處/blockquote/腳註已不計）")
    if semi > SEMICOLON_MAX:
        fails.append(f"全形分號 {semi} > {SEMICOLON_MAX}（可編輯正文仍超，繼續清）")

    # 7. article-health pre-commit hard gate
    try:
        out = subprocess.run(
            ["python3", str(REPO / "scripts/tools/article-health.py"),
             str(path), "--profile=pre-commit", "--quiet"],
            capture_output=True, text=True, timeout=120,
        )
        if out.returncode != 0:
            tail = (out.stdout or out.stderr).strip().splitlines()[-6:]
            fails.append("article-health pre-commit hard fail:\n      " + "\n      ".join(tail))
    except Exception as e:
        fails.append(f"article-health 跑不起來：{e}")

    if fails:
        print(f"❌ {path.name} — {len(fails)} 項未過：")
        for x in fails:
            print(f"   • {x}")
        return False
    print(f"✅ {path.name} — 事實保真 + 達標 + pre-commit hard gate 全過（破折號 {dash} / 分號 {semi}）")
    return True


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--worklist", action="store_true", help="產生 144 篇工作清單")
    ap.add_argument("--verify", metavar="FILE", help="驗證一篇清完的檔 vs git HEAD")
    args = ap.parse_args()
    if args.worklist:
        worklist()
    elif args.verify:
        sys.exit(0 if verify(Path(args.verify)) else 1)
    else:
        ap.error("--worklist 或 --verify FILE")


if __name__ == "__main__":
    main()
