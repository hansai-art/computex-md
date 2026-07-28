#!/usr/bin/env python3
"""
terminology-llm-review.py — 用語詞庫 LLM 全審器（用語保存計畫品質器官）

哲宇 2026-07-10 /goal：「用本地的模型或是 Haiku 或是 Sonnet 完整的重看一次所有的詞庫，
對一些看起來很奇怪的或是覺得可能有錯誤的做標記，然後再來做審覈跟修訂。」

設計（sovereignty-safe 兩層審查）：
  Tier 1（本工具）：本地 Ollama 模型完整掃過 data/terminology/*.yaml 每一筆，
                    判 verdict + issue_type + reason + suggest。本地模型無 content filter，
                    不會對「屏蔽/翻牆/戒嚴」等主權敏感詞 refuse（cloud free tier 會）——
                    對照 2026-06-13 audit：Opus agent summary 被 content filter 擋下的教訓。
  Tier 2（主 session 人在迴路）：對 Tier 1 flag 的子集逐條 adjudicate + 修訂。

為什麼不用 Haiku/Sonnet 做 Tier 1：(1) 2,334 筆 API 成本；(2) 敏感詞 content-filter 風險；
(3) 本地模型零成本零出境（主權對齊，MACHINE GPU 軍團）。qwen3.6:35b 冒煙測試已驗證能
正確 flag 「一鍵→單鍵」錯配 + 「乍母朗瑪峰」亂碼譯名、放行「軟體/網路/8位元」。

用法：
  python3 scripts/tools/terminology-llm-review.py                 # 全審（resumable）
  python3 scripts/tools/terminology-llm-review.py --limit 60      # 前 60 筆（冒煙）
  python3 scripts/tools/terminology-llm-review.py --batch 12      # 每批筆數
  python3 scripts/tools/terminology-llm-review.py --model X       # 換模型
  python3 scripts/tools/terminology-llm-review.py --resume        # 續跑（讀 checkpoint 跳過已審）
  OLLAMA_HOST=http://<fleet>:11434 ... 走 fleet GPU（見 lang-sync/fleet-endpoint.sh）

輸出：
  reports/terminology-review/<date>/results.jsonl   # 每筆一行（含 OK），append-only checkpoint
  reports/terminology-review/<date>/flagged.md      # 只列 flag（給 Tier 2 adjudicate）
"""
from __future__ import annotations
import os, sys, glob, json, re, time, argparse, urllib.request, datetime
from collections import Counter

BASE = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
TERM_DIR = os.path.join(BASE, "data", "terminology")
OLLAMA = os.environ.get("OLLAMA_HOST", "http://127.0.0.1:11434").rstrip("/")
DEFAULT_MODEL = os.environ.get("OLLAMA_MODEL", "qwen3.6:35b-a3b-coding-nvfp4")

try:
    import yaml
except ImportError:
    print("需要 PyYAML"); sys.exit(1)

SYSTEM = """你是台灣本土語言與兩岸用語差異的資深審查專家，母語是台灣華語，同時熟悉中國大陸的用詞。
你在審查一個「台灣用語 vs 中國用語」對照詞庫，用途是保存台灣的語言主權。

最重要的校準原則：**這個詞庫絕大多數對照是正確的。你的預設判斷是 OK。**
只有當你**很有把握**某筆有明顯問題時才 flag。不要因為你對某個學術或技術譯詞不熟，
就把它判成錯配或方向相反——台灣的學術／技術譯名跟中國不同是常態，那正是這個詞庫要保存的東西。

以下這些都是**正確對照，一律判 OK**（示範你不該誤殺的類型）：
- 亂數 / 隨機數（random number）、事前機率 / 先驗機率（prior）、事後機率 / 後驗機率（posterior）
- 互斥或 / 異或（XOR）、程式 / 程序、資料庫 / 數據庫、演算法 / 算法、伺服器 / 服務器
- 網路 / 網絡、軟體 / 軟件、影片 / 視頻、記憶體 / 內存、硬碟 / 硬盤、滑鼠 / 鼠標
只要「台灣欄是台灣合理說法、中國欄是中國合理說法、兩者確有差異」就是 OK，不用追求完美。"""

RUBRIC = """對每一筆判一個 verdict：

- OK         = 對照合理（**這是預設；有疑但說得通就給 OK**）
- SUSPICIOUS = 你覺得可能有問題但沒把握（方向或許顛倒、語感存疑、可能過時）——交人工看，不要自己斷定
- WRONG      = 你**很有把握**是明顯錯誤

只把 WRONG 留給下面這幾種「一眼看得出」的明顯問題（issue_type）：
- GARBLED         亂碼／錯字／劣質音譯（例：珠穆朗瑪峰寫成「乍母朗瑪峰」、岡比亞寫成「乾比亞」）
- SIMPLIFIED_LEAK 台灣欄裡出現簡體字（台灣欄應該全是正體字）
- SAME_WORD       台灣欄與中國欄其實同一個詞（只差簡繁也算），沒有真正差異
- NOT_DISTINCT    中國欄其實台灣也一樣常用，不算中國特有說法（例：Android/安卓、品牌英文名）
- CRUFT           機械展開的無意義條目（例：31位元、60位元 這種根本不存在的規格；8/16/32/64位元是真的別動）

其他情況（你覺得配對怪、方向可能反、但不確定）一律用 SUSPICIOUS + issue_type=MAPPING_WRONG 或 DUBIOUS，
**不要用 WRONG**。FORK_TYPE_WRONG 只在你確定分類錯時用 SUSPICIOUS。

規則：
- 政治/主權敏感詞（屏蔽、翻牆、戒嚴 等）照常審，不迴避、不拒答，只判用語品質不評政治。
- suggest 欄：能給修正就寫一句（正確的詞 / 建議刪除）；否則留空。
- reason 用繁體中文一句話講清楚疑點。
- OK 的 issue_type 填 ""。

只輸出一個 JSON array，長度等於輸入筆數，每元素：
{"n": <輸入編號>, "verdict": "...", "issue_type": "...", "reason": "...", "suggest": "..."}
不要輸出 JSON 以外任何文字、不要 markdown code fence。"""


def load_terms(limit=None):
    files = sorted(glob.glob(os.path.join(TERM_DIR, "*.yaml")))
    out = []
    for f in files:
        base = os.path.basename(f)
        if base.startswith("_"):
            continue
        try:
            d = yaml.safe_load(open(f, encoding="utf-8"))
        except Exception:
            continue
        if not isinstance(d, dict):
            continue
        tw = ((d.get("display") or {}).get("taiwan")) or d.get("taiwan")
        cn = ((d.get("display") or {}).get("china")) or d.get("china")
        if not tw or not cn:
            continue  # 需 tw+cn 才有對照可審
        etym = d.get("etymology") or {}
        notes = d.get("notes") or ""
        if str(notes).strip() in ("台灣用法", "中國用法", "台灣用語", "中國用語"):
            notes = ""
        out.append({
            "file": base,
            "id": d.get("id") or base[:-5],
            "taiwan": str(tw), "china": str(cn),
            "fork_type": d.get("fork_type") or "?",
            "category": d.get("category") or "?",
            "english": d.get("english") or "",
            "origin": str(etym.get("origin") or "")[:160],
            "notes": str(notes)[:160],
        })
    if limit:
        out = out[:limit]
    return out


def build_user(batch):
    lines = ["以下 %d 筆，逐筆審查：\n" % len(batch)]
    for i, t in enumerate(batch, 1):
        extra = []
        if t["english"]:
            extra.append("英=%s" % t["english"])
        if t["origin"]:
            extra.append("詞源=%s" % t["origin"])
        if t["notes"]:
            extra.append("註=%s" % t["notes"])
        tail = ("｜" + "｜".join(extra)) if extra else ""
        lines.append("%d. 台灣「%s」/ 中國「%s」｜分類=%s｜fork_type=%s%s"
                     % (i, t["taiwan"], t["china"], t["category"], t["fork_type"], tail))
    return "\n".join(lines) + "\n\n" + RUBRIC


def call_ollama(model, system, user, timeout=300):
    body = json.dumps({
        "model": model,
        "prompt": user,
        "system": system,
        "stream": False,
        "think": False,
        "options": {"temperature": 0.1, "num_predict": 2400, "num_ctx": 8192},
    }).encode()
    req = urllib.request.Request(OLLAMA + "/api/generate", data=body,
                                 headers={"Content-Type": "application/json"})
    r = json.loads(urllib.request.urlopen(req, timeout=timeout).read())
    return r.get("response", "")


def parse_json_array(text):
    text = text.strip()
    # strip code fences if any
    text = re.sub(r"^```(?:json)?\s*", "", text)
    text = re.sub(r"\s*```$", "", text)
    # find outermost [...]
    s = text.find("[")
    e = text.rfind("]")
    if s == -1 or e == -1 or e <= s:
        return None
    frag = text[s:e + 1]
    try:
        return json.loads(frag)
    except Exception:
        # try to repair trailing commas
        frag2 = re.sub(r",\s*([\]}])", r"\1", frag)
        try:
            return json.loads(frag2)
        except Exception:
            return None


def review_batch(model, batch, retries=2):
    """Return list of verdict dicts aligned to batch, or None on hard failure."""
    user = build_user(batch)
    for attempt in range(retries + 1):
        try:
            resp = call_ollama(model, SYSTEM, user)
        except Exception as ex:
            if attempt < retries:
                time.sleep(2); continue
            return None
        arr = parse_json_array(resp)
        if arr and len(arr) == len(batch):
            return arr
        # count mismatch or parse fail → retry once, then split
        if attempt < retries:
            time.sleep(1); continue
    # final fallback: split batch in half (recursion) if >1
    if len(batch) > 1:
        mid = len(batch) // 2
        left = review_batch(model, batch[:mid], retries=1)
        right = review_batch(model, batch[mid:], retries=1)
        if left is not None and right is not None:
            return left + right
    return None


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--model", default=DEFAULT_MODEL)
    ap.add_argument("--batch", type=int, default=12)
    ap.add_argument("--limit", type=int, default=None)
    ap.add_argument("--resume", action="store_true")
    ap.add_argument("--date", default=datetime.date.today().isoformat())
    args = ap.parse_args()

    outdir = os.path.join(BASE, "reports", "terminology-review", args.date)
    os.makedirs(outdir, exist_ok=True)
    results_path = os.path.join(outdir, "results.jsonl")

    done_files = set()
    if args.resume and os.path.exists(results_path):
        for line in open(results_path, encoding="utf-8"):
            try:
                done_files.add(json.loads(line)["file"])
            except Exception:
                pass
        print("[resume] 已審 %d 筆，跳過" % len(done_files))

    terms = load_terms(limit=args.limit)
    todo = [t for t in terms if t["file"] not in done_files]
    print("[review] 詞庫 %d 筆，待審 %d 筆，model=%s，batch=%d，host=%s"
          % (len(terms), len(todo), args.model, args.batch, OLLAMA))

    rf = open(results_path, "a", encoding="utf-8")
    t0 = time.time()
    n_ok = n_flag = n_fail = 0
    for bi in range(0, len(todo), args.batch):
        batch = todo[bi:bi + args.batch]
        verds = review_batch(args.model, batch)
        if verds is None:
            # record as review-failed so resume can retry
            for t in batch:
                rec = dict(t, verdict="REVIEW_FAILED", issue_type="", reason="model 無有效輸出", suggest="")
                rf.write(json.dumps(rec, ensure_ascii=False) + "\n"); n_fail += 1
            rf.flush()
            print("  batch %d-%d FAILED" % (bi, bi + len(batch)))
            continue
        for t, v in zip(batch, verds):
            verdict = (v.get("verdict") or "OK").upper()
            rec = dict(t, verdict=verdict,
                       issue_type=v.get("issue_type") or "",
                       reason=v.get("reason") or "",
                       suggest=v.get("suggest") or "")
            rf.write(json.dumps(rec, ensure_ascii=False) + "\n")
            if verdict == "OK":
                n_ok += 1
            else:
                n_flag += 1
        rf.flush()
        rate = (bi + len(batch)) / max(time.time() - t0, 0.1)
        eta = (len(todo) - bi - len(batch)) / max(rate, 0.01)
        print("  %d/%d  ok=%d flag=%d fail=%d  %.1f/s  eta=%.0fs"
              % (bi + len(batch), len(todo), n_ok, n_flag, n_fail, rate, eta), flush=True)
    rf.close()
    print("[done] 耗時 %.0fs" % (time.time() - t0))
    write_flagged(outdir, results_path)


def write_flagged(outdir, results_path):
    recs = [json.loads(l) for l in open(results_path, encoding="utf-8")]
    flagged = [r for r in recs if r.get("verdict") not in ("OK",)]
    by_issue = Counter(r.get("issue_type", "") for r in flagged if r.get("verdict") != "REVIEW_FAILED")
    by_verdict = Counter(r.get("verdict", "") for r in recs)
    md = [f"# 詞庫 LLM 全審 — flag 清單（{os.path.basename(outdir)}）\n",
          f"總審 **{len(recs)}** 筆　OK {by_verdict.get('OK',0)}　"
          f"WRONG {by_verdict.get('WRONG',0)}　SUSPICIOUS {by_verdict.get('SUSPICIOUS',0)}　"
          f"REVIEW_FAILED {by_verdict.get('REVIEW_FAILED',0)}\n",
          "## issue_type 分布\n"]
    for k, v in by_issue.most_common():
        md.append(f"- `{k or '(空)'}` × {v}")
    md.append("\n## flag 明細（WRONG 先，依 issue_type 分組）\n")
    order = ["WRONG", "SUSPICIOUS", "REVIEW_FAILED"]
    for verdict in order:
        grp = [r for r in flagged if r.get("verdict") == verdict]
        if not grp:
            continue
        md.append(f"\n### {verdict}（{len(grp)}）\n")
        md.append("| file | 台灣 | 中國 | fork | issue | reason | suggest |")
        md.append("| --- | --- | --- | --- | --- | --- | --- |")
        for r in sorted(grp, key=lambda x: x.get("issue_type", "")):
            md.append("| %s | %s | %s | %s | %s | %s | %s |" % (
                r["file"], r["taiwan"], r["china"], r.get("fork_type", ""),
                r.get("issue_type", ""), (r.get("reason", "") or "").replace("|", "／"),
                (r.get("suggest", "") or "").replace("|", "／")))
    open(os.path.join(outdir, "flagged.md"), "w", encoding="utf-8").write("\n".join(md))
    print("[flagged] %d flagged → %s/flagged.md" % (len(flagged), outdir))


if __name__ == "__main__":
    main()
