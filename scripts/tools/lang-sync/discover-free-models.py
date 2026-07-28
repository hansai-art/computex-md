#!/usr/bin/env python3
"""
discover-free-models.py — auto-discover + calibrate OpenRouter free-tier
models for the babel cascade, so §驗證 SOP (SQUEEZE-MODELS-MAX-PIPELINE.md)
doesn't stay a manual, occasionally-run step.

The pipeline's Tier 3 "驗證佇列" table has gone stale before (openai/gpt-
oss-120b:free got delisted 2026-07-18 without anyone noticing until a health
check; new models like nemotron-3-ultra-550b weren't in the table at all).
Free-tier inventory churns — this queries live and re-scores every run.

Two phases:
  1. `--list`   just print current :free inventory from /api/v1/models,
                ranked by the pipeline's own heuristic (Western origin +
                large + low PRC risk first; too-small / specialized last).
  2. `--calibrate [--top N]` run the fast smoke test (not the full 4-article
                × 5-lang matrix — that's still the authoritative promotion
                gate in the pipeline doc, this is a cheap first filter) on
                the top N candidates: one sovereignty-sensitive probe
                (張懸與安溥, the article owl-alpha historically refused) +
                one plain translation sanity check. Scores availability,
                refusal, and output sanity.

Usage:
  python3 discover-free-models.py --list
  python3 discover-free-models.py --calibrate --top 6
  python3 discover-free-models.py --calibrate --top 6 --json
"""
import argparse
import json
import re
import sys
import time
import urllib.error
import urllib.request
from pathlib import Path

REPO = Path(__file__).resolve().parents[3]
KEY_FILE = Path.home() / ".config/taiwan-md/credentials/openrouter.key"
API_MODELS = "https://openrouter.ai/api/v1/models"
API_CHAT = "https://openrouter.ai/api/v1/chat/completions"

# Per SQUEEZE-MODELS-MAX-PIPELINE.md §Tier 3 排序原則:
#   1. Western origin + large + multilingual-strong first
#   2. PRC-origin ranked later (sovereignty refusal risk)
#   3. Coding/reasoning-specialized last
#   4. Too small (<=12B active/dense) skipped
PRC_ORIGIN_PREFIXES = ("qwen/", "deepseek/", "z-ai/", "baidu/", "inclusionai/",
                        "minimax/", "moonshot/", "01-ai/", "zhipu/")
SPECIALIZED_MARKERS = ("code", "coder", "content-safety", "-vl", "embed", "guard")
MIN_SIZE_HINT_B = 30  # 2026-07-26 從 12 提到 30（哲宇 directive「至少要 gemma4 /
# oss 120 / nemotron / qwen 等級，不然會留很多問題債」）。20B 級模型即使偶爾通過
# 閘門，譯文品質也在及格線邊緣——閘門擋得住結構錯誤與整段沒翻，擋不住「每句都翻了
# 但讀起來不對」，而那些會落地成讀者看到的內容且不會有人回報。缺算力的正解是等額度
# 或加機器，不是降級模型。見 SQUEEZE §入池門檻。

# 明確排除清單：即使通過其他篩選也不入池（實測品質不足）
BLOCKED_MODELS = ("openai/gpt-oss-20b", "google/gemma-4-12b")


def load_key():
    if not KEY_FILE.exists():
        print(f"no key at {KEY_FILE}", file=sys.stderr)
        sys.exit(1)
    return KEY_FILE.read_text().strip()


def fetch_free_models(key):
    req = urllib.request.Request(API_MODELS, headers={"Authorization": f"Bearer {key}"})
    with urllib.request.urlopen(req, timeout=30) as resp:
        data = json.load(resp)
    return [m for m in data.get("data", []) if m["id"].endswith(":free")]


def size_hint_b(model_id: str) -> float:
    """Rough active-param estimate in billions, for the too-small filter."""
    m = re.search(r"(\d+(?:\.\d+)?)b(?:-a(\d+(?:\.\d+)?)b)?", model_id.lower())
    if not m:
        return 999  # unknown size — don't penalize, let it through
    total, moe_active = m.group(1), m.group(2)
    return float(moe_active) if moe_active else float(total)


def rank_score(model: dict) -> tuple:
    """Lower tuple sorts first. (origin_tier, -context, specialized, size_penalty)"""
    mid = model["id"]
    origin_tier = 1 if mid.startswith(PRC_ORIGIN_PREFIXES) else 0
    specialized = 1 if any(s in mid.lower() for s in SPECIALIZED_MARKERS) else 0
    too_small = 1 if size_hint_b(mid) < MIN_SIZE_HINT_B else 0
    ctx = model.get("context_length") or 0
    return (too_small, origin_tier, specialized, -ctx)


def cmd_list(args):
    key = load_key()
    free = fetch_free_models(key)
    free.sort(key=rank_score)
    print(f"{'rank':<5}{'model id':<50}{'ctx':<10}{'flags'}")
    for i, m in enumerate(free, 1):
        flags = []
        if m["id"].startswith(PRC_ORIGIN_PREFIXES):
            flags.append("PRC-origin")
        if any(s in m["id"].lower() for s in SPECIALIZED_MARKERS):
            flags.append("specialized")
        if size_hint_b(m["id"]) < MIN_SIZE_HINT_B:
            flags.append("too-small")
        if m["id"] in BLOCKED_MODELS:
            flags.append("BLOCKED")
        print(f"{i:<5}{m['id']:<50}{m.get('context_length','?'):<10}{','.join(flags) or '-'}")


SOVEREIGNTY_PROBE_ZH = (
    "張懸與安溥：一個台灣音樂人的雙重身份。她原本以張懸為名活躍於獨立音樂圈，"
    "後改以安溥為藝名，作品常涉及對台灣社會與政治的觀察。"
)
SANITY_PROBE_ZH = "台灣是一座位於西太平洋的島嶼，以半導體產業與珍珠奶茶聞名於世。"


def call_model(key, model_id, prompt, timeout=60, retries=2):
    """2026-07-24: back-to-back calibration calls hit transient empty/429
    responses on models that work fine in isolation (nemotron-3-ultra-550b
    tested empty in the automated run, then translated perfectly on a lone
    manual retry seconds later) — free-tier upstream burst limits, not a
    real refusal. Retry with backoff before recording FAIL/REFUSED."""
    payload = json.dumps({
        "model": model_id,
        "messages": [
            {"role": "system", "content": "Translate the following Traditional Chinese text to English. Output only the translation, no commentary."},
            {"role": "user", "content": prompt},
        ],
        "max_tokens": 500,
    }).encode()
    req = urllib.request.Request(API_CHAT, data=payload,
                                  headers={"Authorization": f"Bearer {key}", "Content-Type": "application/json"})
    t0 = time.time()
    last_err = None
    for attempt in range(retries + 1):
        try:
            with urllib.request.urlopen(req, timeout=timeout) as resp:
                data = json.load(resp)
            elapsed = time.time() - t0
            content = data.get("choices", [{}])[0].get("message", {}).get("content") or ""
            if content:
                return {"ok": True, "content": content, "elapsed": round(elapsed, 1), "raw": None}
            last_err = "empty content (possibly transient — see docstring)"
        except urllib.error.HTTPError as e:
            body = e.read().decode("utf-8", errors="replace")[:300]
            last_err = f"HTTP {e.code}: {body}"
        except Exception as e:  # noqa: BLE001
            last_err = str(e)
        if attempt < retries:
            time.sleep(2 * (attempt + 1))
    return {"ok": False, "content": "", "elapsed": round(time.time() - t0, 1), "raw": last_err}


def score_candidate(key, model_id):
    sov = call_model(key, model_id, SOVEREIGNTY_PROBE_ZH)
    sanity = call_model(key, model_id, SANITY_PROBE_ZH)

    def has_cjk(s):
        return any("一" <= c <= "鿿" for c in s)

    sov_ok = sov["ok"] and len(sov["content"]) > 20 and not has_cjk(sov["content"])
    sanity_ok = sanity["ok"] and len(sanity["content"]) > 10 and not has_cjk(sanity["content"])
    verdict = "PASS" if (sov_ok and sanity_ok) else ("REFUSED" if sov["ok"] and not sov_ok else "FAIL")
    return {
        "model": model_id,
        "verdict": verdict,
        "sovereignty_probe": {"ok": sov["ok"], "elapsed_s": sov["elapsed"],
                               "sample": sov["content"][:120], "error": sov["raw"]},
        "sanity_probe": {"ok": sanity["ok"], "elapsed_s": sanity["elapsed"],
                          "sample": sanity["content"][:120], "error": sanity["raw"]},
    }


def cmd_calibrate(args):
    key = load_key()
    free = fetch_free_models(key)
    # 入池門檻先擋（2026-07-26）：太小或明確排除的模型連校準都不跑——校準通過
    # 不代表品質夠，20B 級模型能過閘門但譯文在及格線邊緣（見 SQUEEZE §入池門檻）。
    free = [m for m in free
            if size_hint_b(m["id"]) >= MIN_SIZE_HINT_B and m["id"] not in BLOCKED_MODELS]
    free.sort(key=rank_score)
    candidates = free[: args.top]

    results = []
    for m in candidates:
        print(f"testing {m['id']} ...", file=sys.stderr)
        r = score_candidate(key, m["id"])
        results.append(r)
        print(f"  -> {r['verdict']}", file=sys.stderr)

    passed = [r for r in results if r["verdict"] == "PASS"]

    if args.json:
        print(json.dumps({"tested": len(results), "passed": len(passed), "results": results},
                          ensure_ascii=False, indent=1))
    else:
        print(f"\n=== {len(passed)}/{len(results)} passed ===")
        for r in results:
            icon = {"PASS": "✅", "REFUSED": "🚫", "FAIL": "❌"}[r["verdict"]]
            print(f"{icon} {r['model']}  sov={r['sovereignty_probe']['elapsed_s']}s  sanity={r['sanity_probe']['elapsed_s']}s")
            if r["verdict"] != "PASS":
                err = r["sovereignty_probe"]["error"] or r["sanity_probe"]["error"] or "non-English or empty output"
                print(f"     reason: {err[:150]}")

    out_path = REPO / "reports" / f"openrouter-free-calibration-{time.strftime('%Y-%m-%d')}.json"
    out_path.write_text(json.dumps({"tested": len(results), "passed": len(passed), "results": results},
                                    ensure_ascii=False, indent=1), encoding="utf-8")
    print(f"\nwritten: {out_path.relative_to(REPO)}", file=sys.stderr)
    return passed


def main():
    ap = argparse.ArgumentParser()
    sub = ap.add_subparsers(dest="cmd", required=True)
    p_list = sub.add_parser("list")
    p_list.set_defaults(func=cmd_list)
    p_cal = sub.add_parser("calibrate")
    p_cal.add_argument("--top", type=int, default=6)
    p_cal.add_argument("--json", action="store_true")
    p_cal.set_defaults(func=cmd_calibrate)

    # allow --list / --calibrate as top-level flags too (friendlier CLI)
    if len(sys.argv) > 1 and sys.argv[1] in ("--list", "--calibrate"):
        sys.argv[1] = sys.argv[1].lstrip("-")

    args = ap.parse_args()
    args.func(args)


if __name__ == "__main__":
    main()
