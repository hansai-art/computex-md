#!/usr/bin/env python3
"""ui-bundle-translate.py — src/i18n/ bundle 的新語言 block 產線。

2026-07-18 vi/id/pt/hi 出生戰役造橋：BIRTH-CHECKLIST v2.0 Stage 4 的「UI bundle
翻譯產線」儀器化（此前 ko 出生時 1,743 keys 手補、es/fr 靠人肉，第四次不要再手工）。

用法：
    python3 ui-bundle-translate.py --file src/i18n/latest.ts --lang vi --backend codex --apply
    python3 ui-bundle-translate.py --file src/i18n/ui.ts --lang hi --backend ollama  # dry-run

機制：
  1. 找 zh-TW block（SSOT）與目標語 block（已存在則 skip）
  2. zh block 按 top-level key 行切 chunk（≤ --chunk-chars），逐 chunk 丟 backend
     翻「值」不翻「鍵」；行數與鍵序 mismatch 自動重試一次，再敗換 fallback backend
  3. 新 block 插在 zh-TW block 之前（維持 zh-TW 殿後慣例）
  4. 檔級驗證：鍵數對齊 zh + esbuild 語法檢查（hard gate：任一敗 = 不寫檔）

主權防護：inline 該語言指南（docs/editorial/per-language/TRANSLATION-{lang}.md）
的 ## TL;DR 段進 system prompt（跟文章翻譯的 Z2.0 hard gate 同源，縮小版）。
"""

from __future__ import annotations

import argparse
import re
import subprocess
import sys
from pathlib import Path

REPO = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(Path(__file__).parent))

from backends import CodexBackend, OllamaBackend, LANG_NAMES  # noqa: E402


def load_guide_tldr(lang: str, max_chars: int = 3500) -> str:
    guide = REPO / "docs/editorial/per-language" / f"TRANSLATION-{lang}.md"
    if not guide.exists():
        return ""
    for block in re.split(r"\n(?=## )", guide.read_text(encoding="utf-8")):
        if block.lstrip().startswith("## TL;DR"):
            return block.strip()[:max_chars]
    return ""


def find_block(text: str, lang: str):
    """回傳 (start, end) 涵蓋 `  lang: { ... },`（含尾逗號）。字串感知括號配對。"""
    pat = re.compile(rf"^  '?{re.escape(lang)}'?:\s*\{{", re.M)
    m = pat.search(text)
    if not m:
        return None
    i = text.index("{", m.start())
    depth = 0
    in_str = None
    escape = False
    while i < len(text):
        c = text[i]
        if in_str:
            if escape:
                escape = False
            elif c == "\\":
                escape = True
            elif c == in_str:
                in_str = None
        else:
            if c in ("'", '"', "`"):
                in_str = c
            elif c == "{":
                depth += 1
            elif c == "}":
                depth -= 1
                if depth == 0:
                    j = i + 1
                    if j < len(text) and text[j] == ",":
                        j += 1
                    if j < len(text) and text[j] == "\n":
                        j += 1
                    return (m.start(), j)
        i += 1
    raise SystemExit(f"❌ {lang} block 括號不平衡（parser bug 或檔案損壞）")


KEY_RE = re.compile(r"^\s+'([^']+)':", re.M)


def keys_of(body: str):
    return KEY_RE.findall(body)


def chunk_body(body_lines, max_chars):
    chunks, cur, size = [], [], 0
    for line in body_lines:
        is_key = re.match(r"^\s+'[^']+':", line)
        if cur and size + len(line) > max_chars and is_key:
            chunks.append("\n".join(cur))
            cur, size = [], 0
        cur.append(line)
        size += len(line) + 1
    if cur:
        chunks.append("\n".join(cur))
    return chunks


def make_backend(name: str):
    if name == "codex":
        return CodexBackend()
    if name == "ollama":
        return OllamaBackend()
    raise SystemExit(f"❌ 未知 backend: {name}")


def translate_chunk(backend, lang, chunk, guide_tldr):
    system = (
        f"You translate UI strings for computex.md (Taiwan knowledge base, Taiwan's own voice).\n"
        f"Task: translate ONLY the string VALUES from Traditional Chinese (zh-TW) to "
        f"{LANG_NAMES.get(lang, lang)}.\n"
        "HARD RULES:\n"
        "1. Output ONLY the translated TypeScript lines. No code fences, no commentary.\n"
        "2. Keys, indentation, quotes, commas and `//` comment lines stay byte-identical "
        "(comment lines are NOT translated).\n"
        "3. Same number of lines in = lines out. Never merge, drop or add lines.\n"
        "4. Brand/product names (COMPUTEX.md, computex.md, GitHub, Threads, X, Astro, Ollama, "
        "CC BY-SA…) stay as-is.\n"
        "5. Numbers, URLs, emoji, placeholder tokens stay as-is.\n"
        + (f"\nSOVEREIGNTY RULES (from TRANSLATION-{lang}.md):\n{guide_tldr}\n" if guide_tldr else "")
    )
    return backend.translate(system, chunk, max_tokens=16000)


def clean_output(raw: str, chunk: str = "") -> str:
    txt = raw.strip()
    txt = re.sub(r"^```[a-z]*\n", "", txt)
    txt = re.sub(r"\n```$", "", txt)
    # codex 常 strip 首行縮排（2026-07-18 dogfood：'nav.latest' 因此漏出 KEY_RE），
    # 用 chunk 首行的縮排還原
    if chunk:
        m = re.match(r"^(\s+)", chunk)
        if m and txt and not txt.startswith((" ", "\t")):
            txt = m.group(1) + txt
    return txt


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--file", required=True)
    ap.add_argument("--lang", required=True)
    ap.add_argument("--backend", default="codex", help="primary backend (codex|ollama)")
    ap.add_argument("--fallback", default="ollama", help="fallback backend, '' 停用")
    ap.add_argument("--chunk-chars", type=int, default=5000)
    ap.add_argument("--apply", action="store_true")
    args = ap.parse_args()

    path = REPO / args.file
    text = path.read_text(encoding="utf-8")

    if find_block(text, args.lang):
        print(f"⏭️  {args.file} 已有 {args.lang} block — skip")
        return

    zh = find_block(text, "zh-TW")
    if not zh:
        raise SystemExit(f"❌ {args.file} 找不到 zh-TW block")
    zh_start, zh_end = zh
    zh_block = text[zh_start:zh_end]
    # body = block 去頭行與尾行
    zh_lines = zh_block.splitlines()
    head, tail = zh_lines[0], zh_lines[-1]
    body_lines = zh_lines[1:-1]
    zh_keys = keys_of("\n".join(body_lines))

    guide_tldr = load_guide_tldr(args.lang)
    if not guide_tldr:
        print(f"⚠️  無 TRANSLATION-{args.lang}.md TL;DR — 主權 mini-rules 缺位（guide 未落檔？）")

    primary = make_backend(args.backend)
    fallback = make_backend(args.fallback) if args.fallback else None

    chunks = chunk_body(body_lines, args.chunk_chars)
    print(f"🔧 {args.file} → {args.lang}: {len(zh_keys)} keys / {len(chunks)} chunks / backend={args.backend}")

    out_parts = []
    for idx, chunk in enumerate(chunks, 1):
        want_keys = keys_of(chunk)
        got = None
        for attempt, be in [(1, primary), (2, primary)] + ([(3, fallback)] if fallback else []):
            try:
                raw = translate_chunk(be, args.lang, chunk, guide_tldr)
            except Exception as e:  # noqa: BLE001
                print(f"   chunk {idx} attempt {attempt} backend error: {e}")
                continue
            cand = clean_output(raw, chunk)
            if keys_of(cand) == want_keys:
                got = cand
                break
            print(f"   chunk {idx} attempt {attempt}: key mismatch "
                  f"({len(keys_of(cand))} vs {len(want_keys)}) — retry")
        if got is None:
            raise SystemExit(f"❌ chunk {idx} 全部 attempt 失敗 — 不寫檔（partial block 比沒有更危險）")
        out_parts.append(got)
        print(f"   ✅ chunk {idx}/{len(chunks)}")

    new_body = "\n".join(out_parts)
    new_keys = keys_of(new_body)
    if new_keys != zh_keys:
        raise SystemExit(f"❌ 檔級鍵序 mismatch：zh {len(zh_keys)} vs {args.lang} {len(new_keys)}")

    indent_head = re.sub(r"'?zh-TW'?", args.lang, head, count=1)
    new_block = f"{indent_head}\n{new_body}\n{tail}\n"
    new_text = text[:zh_start] + new_block + text[zh_start:]

    tmp = REPO / "tmp" / f"ui-bundle-{Path(args.file).stem}-{args.lang}.ts"
    tmp.parent.mkdir(exist_ok=True)
    tmp.write_text(new_text, encoding="utf-8")

    # esbuild 語法閘
    es = subprocess.run(
        ["npx", "esbuild", str(tmp), "--loader:.ts=ts", "--outfile=/dev/null"],
        capture_output=True, text=True, cwd=REPO,
    )
    if es.returncode != 0:
        raise SystemExit(f"❌ esbuild 語法檢查 fail：{es.stderr[:400]}\n（產物留在 {tmp}）")

    if args.apply:
        path.write_text(new_text, encoding="utf-8")
        print(f"✅ {args.file} +{args.lang} block（{len(new_keys)} keys，esbuild PASS）")
    else:
        print(f"🔎 dry-run OK（{len(new_keys)} keys，esbuild PASS）→ {tmp}；加 --apply 寫回")


if __name__ == "__main__":
    main()
