#!/usr/bin/env python3
"""yt-transcript.py — YouTube 字幕 → 可讀逐字稿 一條龍（REWRITE-PIPELINE Step 1.9.3 SSOT）

把「人物 / 訪談深度文要拿 YouTube 當一手素材」的手工流程儀器化：
之前散在 — 手跑 yt-dlp 抓 .vtt + 臨時寫 python 清時間戳/dedup/[MM:SS]。本工具統一。

YouTube auto-caption（自動字幕）對人物文是最好的「主角逐字」來源，但 raw .vtt 充滿
時間戳、內聯 timing tag、rolling 重疊，不能直接讀。本工具清成連續逐字稿 + 每 ~60s 一個
[MM:SS] 錨點（腳註可精確標「塞掐 E350 @ 12:34」）。

⚠️ auto-caption 會誤植專名（人名 / 論文 / 機構），引用前**每個專名對權威源校正**，
   別逐字照抄（REWRITE-PIPELINE Step 1.9.3 + MANIFESTO §10 幻覺鐵律）。

兩個 mode：

  fetch — 給 YouTube URL（可多支）→ yt-dlp 抓字幕（預設 zh-TW,en）→ 清成逐字稿
          → 落 reports/research/{YYYY-MM}/{slug}-transcripts/{id}.{lang}.{vtt,txt}
          （.vtt raw 永不刪保留為證據鏈；.txt 是給寫作/腳註用的可讀版）

  clean — 給單一 .vtt → 印出 / 寫出 .txt（已手動抓好字幕時用）

Usage:
  # 一支或多支影片抓進某篇文章的研究資料夾
  python3 scripts/tools/yt-transcript.py fetch <URL> [<URL> ...] --slug 紀懷新
  python3 scripts/tools/yt-transcript.py fetch <URL> --slug 林琪兒 --lang zh-TW,en --month 2026-06

  # 清一個已下載的 vtt
  python3 scripts/tools/yt-transcript.py clean path/to/file.zh-TW.vtt [-o out.txt]

依賴：yt-dlp（`brew install yt-dlp` / `pip install yt-dlp`）。clean mode 無外部依賴。

誕生：2026-06-27 寫 紀懷新（Ed H. Chi）人物文時，哲宇給 4 支訪談要轉錄，臨時寫了 cleaner；
事後儀器化（REFLEXES #15 反覆浮現要儀器化 + MANIFESTO §造橋鋪路 self-apply）。
"""

import argparse
import datetime
import re
import shutil
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
TS_RE = re.compile(r"(\d{2}:\d{2}:\d{2}\.\d{3})\s*-->\s*(\d{2}:\d{2}:\d{2}\.\d{3})")
TAG_RE = re.compile(r"<[^>]+>")  # 內聯 <00:00:00.000> timing tag + <c> 標記
CJK_RE = re.compile(r"[㐀-鿿]")
ANCHOR_GAP = 60.0  # 每 ~60 秒插一個 [MM:SS] 錨點


def _parse_ts(ts: str) -> float:
    h, m, s = ts.split(":")
    return int(h) * 3600 + int(m) * 60 + float(s)


def _fmt_anchor(sec: float) -> str:
    return f"[{int(sec) // 60:02d}:{int(sec) % 60:02d}]"


def _is_cjk(text: str) -> bool:
    sample = text[:400]
    return bool(sample) and len(CJK_RE.findall(sample)) > len(sample) * 0.3


def clean_vtt(path: Path) -> str:
    """WebVTT → 連續逐字稿 + [MM:SS] 錨點。CJK 無空格 join、拉丁有空格。"""
    lines = path.read_text(encoding="utf-8", errors="replace").splitlines()
    cues: list[tuple[float, str]] = []
    i = 0
    while i < len(lines):
        m = TS_RE.match(lines[i].strip())
        if not m:
            i += 1
            continue
        start = _parse_ts(m.group(1))
        i += 1
        parts: list[str] = []
        while i < len(lines) and lines[i].strip():
            t = TAG_RE.sub("", lines[i].strip())
            t = re.sub(r"^\s*-\s*", "", t)  # 去開頭破折號（對話字幕）
            if t:
                parts.append(t)
            i += 1
        text = " ".join(parts).strip()
        if text:
            cues.append((start, text))

    # dedup：完全相同 skip；rolling auto-caption 前綴重疊（current 含 prev → 取長；prev 含 current → 棄）
    cleaned: list[tuple[float, str]] = []
    for start, text in cues:
        if cleaned:
            prev = cleaned[-1][1]
            if text == prev:
                continue
            if text.startswith(prev):
                cleaned[-1] = (cleaned[-1][0], text)
                continue
            if prev.startswith(text):
                continue
        cleaned.append((start, text))

    cjk = _is_cjk("".join(t for _, t in cleaned[:30]))
    out: list[str] = []
    para: list[str] = []
    last_anchor = -1e9

    def flush():
        if para:
            out.append(("" if cjk else " ").join(para))
            para.clear()

    for start, text in cleaned:
        if start - last_anchor >= ANCHOR_GAP:
            flush()
            out.append("")
            out.append(_fmt_anchor(start))
            last_anchor = start
        para.append(text)
    flush()
    return "\n".join(out).strip() + "\n"


def _yt(*args: str) -> subprocess.CompletedProcess:
    return subprocess.run(["yt-dlp", *args], capture_output=True, text=True)


def _require_ytdlp():
    if not shutil.which("yt-dlp"):
        sys.exit("✗ 找不到 yt-dlp。安裝：brew install yt-dlp  或  pip install yt-dlp")


def cmd_fetch(args) -> int:
    _require_ytdlp()
    month = args.month or datetime.date.today().strftime("%Y-%m")
    outdir = ROOT / "reports" / "research" / month / f"{args.slug}-transcripts"
    outdir.mkdir(parents=True, exist_ok=True)
    langs = args.lang
    print(f"📁 {outdir.relative_to(ROOT)}  (langs: {langs})\n")

    total_txt = 0
    for url in args.urls:
        meta = _yt("--skip-download", "--no-warnings", "--print",
                   "%(id)s\t%(title)s\t%(duration_string)s", url)
        line = (meta.stdout or "").strip().splitlines()
        if not line:
            print(f"  ✗ 取不到 metadata: {url}\n{meta.stderr.strip()[:200]}")
            continue
        vid, title, dur = (line[0].split("\t") + ["", "", ""])[:3]
        print(f"▶ {title}  ({dur})  [{vid}]")

        dl = _yt("--skip-download", "--write-auto-sub", "--write-sub",
                 "--sub-lang", langs, "--sub-format", "vtt", "--no-warnings",
                 "-o", str(outdir / "%(id)s.%(ext)s"), url)
        if dl.returncode != 0:
            print(f"  ⚠ yt-dlp 字幕下載非零退出：{dl.stderr.strip()[:200]}")

        vtts = sorted(outdir.glob(f"{vid}.*.vtt"))
        if not vtts:
            print("  ⚠ 無字幕可抓（這支可能沒開字幕）— skip")
            continue
        for vtt in vtts:
            txt = vtt.with_suffix(".txt")
            text = clean_vtt(vtt)
            txt.write_text(text, encoding="utf-8")
            chars = len(text.replace("\n", "").replace(" ", ""))
            total_txt += 1
            print(f"  ✓ {vtt.name} → {txt.name}  ({chars} chars)")
        print()

    print(f"✨ 完成：{total_txt} 份逐字稿落 {outdir.relative_to(ROOT)}")
    print("⚠ auto-caption 專名會誤植 — 引用前對權威源校正，別逐字照抄。")
    return 0


def cmd_clean(args) -> int:
    src = Path(args.vtt)
    if not src.exists():
        sys.exit(f"✗ 找不到 {src}")
    text = clean_vtt(src)
    if args.output:
        Path(args.output).write_text(text, encoding="utf-8")
        chars = len(text.replace("\n", "").replace(" ", ""))
        print(f"✓ {src.name} → {args.output}  ({chars} chars)")
    else:
        sys.stdout.write(text)
    return 0


def main() -> int:
    p = argparse.ArgumentParser(description="YouTube 字幕 → 可讀逐字稿（REWRITE Step 1.9.3 SSOT）")
    sub = p.add_subparsers(dest="cmd", required=True)

    f = sub.add_parser("fetch", help="抓 YouTube 字幕 + 清成逐字稿，落研究資料夾")
    f.add_argument("urls", nargs="+", help="YouTube URL（可多支）")
    f.add_argument("--slug", required=True, help="文章 slug（決定 {slug}-transcripts/ 資料夾）")
    f.add_argument("--lang", default="zh-TW,en", help="字幕語言，逗號分隔（預設 zh-TW,en）")
    f.add_argument("--month", default=None, help="reports/research/{YYYY-MM}/（預設今月）")
    f.set_defaults(func=cmd_fetch)

    c = sub.add_parser("clean", help="清單一已下載的 .vtt")
    c.add_argument("vtt", help="輸入 .vtt 路徑")
    c.add_argument("-o", "--output", default=None, help="輸出 .txt（省略則印到 stdout）")
    c.set_defaults(func=cmd_clean)

    args = p.parse_args()
    return args.func(args)


if __name__ == "__main__":
    raise SystemExit(main())
