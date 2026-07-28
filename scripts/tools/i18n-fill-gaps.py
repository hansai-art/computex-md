#!/usr/bin/env python3
"""
i18n-fill-gaps.py — 補 src/i18n/ 既有 lang block 的「部分缺漏」key（merge 模式）

i18n-translate.py 只在 target lang block 不存在時整塊新增；當 block 已存在但
key 不齊（en 後來新增了 key），它會 skip。本工具補這個缺口：

  1. 抽 en block 的 key 順序 + value
  2. 抽 target lang block 既有 key
  3. missing = en_keys - target_keys（保留 en 順序）
  4. 只把 missing 的 en value 丟 owl-alpha 翻成 target（與既有翻譯同一條 path 保一致）
  5. 把翻好的 missing pair splice 進 target block 結尾（既有 key 一律不動）

複用 i18n-translate.py 的 parser / owl 呼叫，避免邏輯漂移。

Usage:
  python3 scripts/tools/i18n-fill-gaps.py --module semiont --target ja
  python3 scripts/tools/i18n-fill-gaps.py --module about   --target fr --dry-run
"""
import argparse, importlib.util, json, re, sys
from pathlib import Path

REPO = Path(__file__).resolve().parent.parent.parent
I18N_DIR = REPO / "src/i18n"

# Reuse helpers from i18n-translate.py (hyphenated filename → importlib)
_spec = importlib.util.spec_from_file_location(
    "i18n_translate", Path(__file__).parent / "i18n-translate.py")
_t = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(_t)


def _chunk_translate(missing_json, target_lang, api_key):
    """Translate {key: en_value} via owl-alpha, chunked. Returns {key: translated}."""
    system = (
        f"You are a UI string translator for COMPUTEX.md.\n\n"
        f"Translate this JSON of English UI strings to {_t.LANG_NAMES.get(target_lang, target_lang)}.\n\n"
        "CRITICAL rules:\n"
        "1. Output ONLY a JSON object, no markdown wrapper, no explanation\n"
        "2. Keep all keys EXACTLY as input (don't translate keys)\n"
        f"3. Translate values to {_t.LANG_NAMES.get(target_lang, target_lang)} preserving meaning + tone\n"
        "4. Keep proper nouns (Taiwan, Mazu, Audrey Tang, Semiont, etc.) appropriately rendered\n"
        "5. Keep emoji + numbers + URL references unchanged\n"
        "6. Strings with HTML / markdown markup: preserve markup, only translate text\n"
        "7. Keep punctuation appropriate to target language\n"
        "8. Keep length similar — UI space is constrained\n"
    )
    items = list(missing_json.items())
    chunk_size = 75
    chunks = [dict(items[i:i+chunk_size]) for i in range(0, len(items), chunk_size)] or [{}]
    out = {}
    for ci, chunk in enumerate(chunks):
        user = (f"Source language: English\nTarget language: {_t.LANG_NAMES.get(target_lang, target_lang)}\n\n"
                f"JSON to translate:\n```json\n{json.dumps(chunk, ensure_ascii=False, indent=2)}\n```\n\n"
                "Output ONLY the translated JSON object.")
        got = None
        for attempt in range(3):
            try:
                res = _t.call_owl(api_key, system, user).strip()
            except Exception as e:
                print(f"    chunk {ci+1}: API err {e}", flush=True); continue
            if res.startswith("```"):
                res = re.sub(r"^```(?:json)?\n", "", res); res = re.sub(r"\n```$", "", res)
            try:
                got = json.loads(res); break
            except json.JSONDecodeError as e:
                print(f"    chunk {ci+1} attempt {attempt+1}: JSON fail {e}", flush=True)
        if got:
            out.update(got)
            print(f"    chunk {ci+1}/{len(chunks)} ✓ ({len(got)} keys)", flush=True)
    return out


def fill_module(module, target_lang, api_key, dry_run=False):
    f = I18N_DIR / f"{module}.ts"
    if not f.exists():
        print(f"  ❌ {module}.ts not found"); return False
    content = f.read_text()

    en_start, en_end, en_body = _t.extract_lang_block(content, "en")
    if en_start == -1:
        print(f"  ❌ {module}: no en block"); return False
    t_start, t_end, t_body = _t.extract_lang_block(content, target_lang)
    if t_start == -1:
        print(f"  ⏭  {module}/{target_lang}: block missing — use i18n-translate.py (full add), not this"); return False

    en_pairs = _t.parse_kv_pairs(en_body)
    t_keys = {k for k, _ in _t.parse_kv_pairs(t_body)}
    missing = [(k, v) for k, v in en_pairs if k not in t_keys]
    if not missing:
        print(f"  ✅ {module}/{target_lang}: already complete ({len(t_keys)}/{len(en_pairs)})"); return True
    print(f"  → {module}/{target_lang}: {len(missing)} missing of {len(en_pairs)}", flush=True)
    if dry_run:
        for k, _ in missing[:8]:
            print(f"      · {k}")
        if len(missing) > 8:
            print(f"      … +{len(missing)-8} more")
        return True

    translated = _chunk_translate({k: v for k, v in missing}, target_lang, api_key)
    if len(translated) != len(missing):
        print(f"  ⚠️  {module}/{target_lang}: got {len(translated)}/{len(missing)} — partial, aborting splice (no half-writes)")
        return False

    # Build new key lines (en order), splice before the target block's close brace (t_end)
    new_lines = []
    for k, _ in missing:
        quoted = json.dumps(str(translated[k]), ensure_ascii=False)
        new_lines.append(f"    '{k}': {quoted},")
    content_lines = content.split("\n")
    # t_end is the line index of the target block's `  },` / `  }` — insert before it
    content_lines[t_end:t_end] = new_lines
    f.write_text("\n".join(content_lines))
    print(f"  ✅ {module}/{target_lang}: spliced {len(new_lines)} keys → {len(t_keys)+len(new_lines)}/{len(en_pairs)}")
    return True


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--module", required=True)
    ap.add_argument("--target", required=True)
    ap.add_argument("--dry-run", action="store_true")
    args = ap.parse_args()
    api_key = _t.get_api_key()
    ok = fill_module(args.module, args.target, api_key, args.dry_run)
    sys.exit(0 if ok else 1)


if __name__ == "__main__":
    main()
