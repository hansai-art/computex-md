#!/usr/bin/env python3
"""
lessons-distill.py — LESSONS-INBOX distill 助手（把 distill 的處理/分析/歸檔儀器化）

把 2026-06-19 完整 distill（§未消化 266→8）的手工流程固化成工具，讓未來 distill
更方便、更精煉。三個子指令對應 distill 三個吃力環節：

  audit  — distill 前「現場感知」：§未消化 count / 結構完整性 / Stage 0a housekeeping
           候選 / severity+vc 排序 / cross-check inbox-signal 門檻
  chunk  — 「分析」環節 fan-out 準備：把 §未消化 切成 N 段 line range，餵給平行
           read-only 子代聚類（few patterns × many instances）
  sweep  — 「歸檔處理」環節：deterministic keeper-based sweep，移除已 distill 的
           entry、合併多個 §未消化 section、保留 §已消化/§Defer/§歸檔 verbatim

設計原則：
- 讀（分析）平行化、寫（歸檔）deterministic。LLM 判斷不外包給 script，但聚類 prep
  + 機械 sweep 可以（REFLEXES「fan-out read + deterministic sweep」）。
- sweep dry-run by default，--apply 才寫；保留條數 0 會 refuse（防呆 — 不可能整批 drop）。
- audit 自己 cross-verify ground truth grep count（REFLEXES #65），不只信單一 regex。

canonical：docs/semiont/LESSONS-INBOX.md §Distill SOP（6-stage）+ REFLEXES #15 / #72。
"""
import argparse
import re
import sys
from pathlib import Path

REPO = Path(__file__).resolve().parents[2]
DEFAULT_LESSONS = REPO / "docs/semiont/LESSONS-INBOX.md"

UNMET_RE = re.compile(r"^## .*未消化清單")        # 只配 content section（SOP 內無此 H2）
CONSUMED_RE = re.compile(r"^## ✅ 已消化")
ARCHIVED_RE = re.compile(r"^## ❌ 已歸檔")
ENTRY_RE = re.compile(r"^### ")
H2_RE = re.compile(r"^## ")
DONE_MARKERS = re.compile(
    r"✅ DISTILLED|✅ 已 distilled|resolved_by|狀態.*✅|已 instantiate|DISTILLED ✅"
)
# 只認 metadata 行（^- **verification_count**: N），不掃 body prose——body 常引用別條
# canonical 的 vc（「節律脫鉤 verification_count 9」），greedy max 會把別人的 vc 當自己的
#（2026-07-11 dna-checkup 實測：audit 報 vc=9/5/3 的三條，metadata 實際是 2/1/2）
VC_LINE_RE = re.compile(r"^\s*-\s*\*\*verification_count\*\*[:：]\s*(\d+)")
STRUCTURAL_RE = re.compile(r"severity.{0,15}structural")


def load(path):
    return Path(path).read_text(encoding="utf-8").split("\n")


def find_all(lines, rx):
    return [i for i, l in enumerate(lines) if rx.match(l)]


def find_first(lines, rx):
    for i, l in enumerate(lines):
        if rx.match(l):
            return i
    return None


def entry_blocks(lines, start, end):
    """切出 [start,end) 內的 entries：每個 entry 從 ### 到下一個 ### / ## 之前。"""
    seg = lines[start:end]
    idxs = [k for k, l in enumerate(seg) if ENTRY_RE.match(l)]
    blocks = []
    for n, k in enumerate(idxs):
        nxt = idxs[n + 1] if n + 1 < len(idxs) else len(seg)
        blocks.append((start + k, [seg[j] for j in range(k, nxt)]))
    return blocks  # list of (abs_line, [lines])


def unmet_spans(lines):
    """回傳所有 §未消化 section 的 (header_idx, end_idx)。end = 下一個 ## 或 EOF。"""
    heads = find_all(lines, UNMET_RE)
    spans = []
    for h in heads:
        end = next((i for i in range(h + 1, len(lines)) if H2_RE.match(lines[i])), len(lines))
        spans.append((h, end))
    return spans


def all_unmet_entries(lines):
    out = []
    for h, end in unmet_spans(lines):
        out += entry_blocks(lines, h, end)
    return out


def vc_of(block):
    for l in block:
        m = VC_LINE_RE.match(l)
        if m:
            return int(m.group(1))
    return 0  # 無 metadata 行（舊格式 entry）→ 排序沉底，不 greedy 猜


# ---------------------------------------------------------------- audit
def cmd_audit(args):
    lines = load(args.file)
    spans = unmet_spans(lines)
    entries = all_unmet_entries(lines)
    n = len(entries)

    print(f"📥 LESSONS-INBOX distill audit — {args.file}")
    print(f"   §未消化 entries: {n}（門檻 200 → {'⚠️ distill due' if n >= 200 else 'ok'}）")

    # cross-verify ground truth grep count（REFLEXES #65 — 不只信 regex span）
    raw = sum(
        1
        for i, l in enumerate(lines)
        if ENTRY_RE.match(l)
        and any(h < i < e for h, e in spans)
    )
    flag = "✅ 對齊" if raw == n else f"⚠️ regex {n} vs grep {raw} 不一致"
    print(f"   ground-truth cross-check: {flag}")

    # 結構漂移：多個 §未消化 section
    if len(spans) > 1:
        hdrs = ", ".join(f"L{h+1}" for h, _ in spans)
        print(f"   🚨 結構漂移：{len(spans)} 個 §未消化 section（{hdrs}）→ sweep 會自動合併")
    else:
        print(f"   §未消化 section: 1（無漂移）")

    # Stage 0a：self-marked done 但仍在 §未消化（housekeeping 候選）
    done = [(ln, b) for ln, b in entries if any(DONE_MARKERS.search(x) for x in b)]
    print(f"\n   Stage 0a housekeeping 候選（self-marked done 仍在 §未消化）：{len(done)}")
    for ln, b in done[: args.top]:
        print(f"     L{ln+1}  {b[0][4:][:64]}")

    # severity=structural + 高 vc 優先（distill triage 順序）
    structural = [(ln, b) for ln, b in entries if any(STRUCTURAL_RE.search(x) for x in b)]
    ranked = sorted(entries, key=lambda t: vc_of(t[1]), reverse=True)
    print(f"\n   severity=structural: {len(structural)} 條")
    print(f"   高 vc top（distill 先看）：")
    for ln, b in ranked[: args.top]:
        v = vc_of(b)
        if v >= 2:
            print(f"     vc={v}  {b[0][4:][:60]}")

    if n >= 200:
        print(f"\n   → 建議：`lessons-distill.py chunk --agents N` 起 fan-out 分析（見 §Distill SOP §分析方法）")
    return 0


# ---------------------------------------------------------------- chunk
def cmd_chunk(lines_or_args):
    args = lines_or_args
    lines = load(args.file)
    entries = all_unmet_entries(lines)
    if not entries:
        print("§未消化 無 entry，不需 chunk", file=sys.stderr)
        return 1
    k = args.agents
    per = max(1, (len(entries) + k - 1) // k)
    print(f"# fan-out {k}-agent 分析 chunk（§未消化 {len(entries)} entries / ~{per} 每段）")
    print(f"# 每段派一個 read-only 子代讀 line range，回傳 cluster（pattern × instances + disposition）")
    print(f"# disposition 六桶：promote / housekeeping-done / fold→reflex / already-covered / operational→pipeline / stale")
    for a in range(0, len(entries), per):
        chunk = entries[a : a + per]
        start = chunk[0][0] + 1
        # end = 下一 chunk 第一個 entry header，或最後 entry 結尾
        nxt_idx = a + per
        if nxt_idx < len(entries):
            end = entries[nxt_idx][0]
        else:
            end = chunk[-1][0] + len(chunk[-1][1])
        print(f"  agent {a//per+1}: 讀 {Path(args.file).name} 行 {start}-{end}（{len(chunk)} entries）")
    return 0


# ---------------------------------------------------------------- sweep
def cmd_sweep(args):
    path = Path(args.file)
    lines = load(path)
    spans = unmet_spans(lines)
    if not spans:
        print("找不到 §未消化 section", file=sys.stderr)
        return 1
    i_consumed = find_first(lines, CONSUMED_RE)
    i_archived = find_first(lines, ARCHIVED_RE)
    if i_consumed is None or i_archived is None:
        print("找不到 §已消化 或 §歸檔 section（檔案結構異常）", file=sys.stderr)
        return 1

    keepers = []
    if args.keep:
        src = sys.stdin if args.keep == "-" else open(args.keep, encoding="utf-8")
        keepers = [l.strip() for l in src if l.strip() and not l.startswith("#")]

    def keep(block):
        return any(k in block[0] for k in keepers)

    entries = all_unmet_entries(lines)
    kept = [b for _, b in entries if keep(b)]
    dropped = len(entries) - len(kept)

    print(f"sweep: §未消化 {len(entries)} → keep {len(kept)} / drop {dropped}（keeper substrings: {len(keepers)}）")
    for b in kept:
        print(f"   KEEP  {b[0][4:][:64]}")

    if len(kept) == 0 and not args.force:
        print("\n🚫 保留 0 條 — 整批 drop 不合理（keeper allowlist 可能寫錯）。確定請加 --force", file=sys.stderr)
        return 2
    if not args.apply:
        print(f"\n(dry-run — 加 --apply 才寫入。會合併 {len(spans)} 個 §未消化 section 為 1)")
        return 0

    # rebuild: prefix + 第一個 §未消化 header+intro + kept entries + 中段(§已消化~§Defer) + §歸檔
    h0, e0 = spans[0]
    seg0 = lines[h0:e0]
    first_e = next((k for k, l in enumerate(seg0) if ENTRY_RE.match(l)), len(seg0))
    intro = seg0[:first_e]
    while intro and intro[-1].strip() == "":
        intro.pop()

    def strip_blanks(b):
        b = list(b)
        while b and b[-1].strip() == "":
            b.pop()
        return b

    out = lines[:h0] + intro + [""]
    for b in kept:
        out += strip_blanks(b) + [""]

    # 中段：§已消化 → §歸檔，但跳過任何夾在中間的其他 §未消化 section
    mid = []
    skip_until = None
    for i in range(i_consumed, i_archived):
        if any(i == h for h, _ in spans):  # 額外 §未消化 header → skip 整段
            skip_until = next((e for h, e in spans if h == i), i + 1)
        if skip_until is not None and i < skip_until:
            continue
        mid.append(lines[i])
    out += mid

    # 若指定 --record，把 distill traceability block append 進 §已消化（在 §Defer 之前）
    if args.record:
        rec = Path(args.record).read_text(encoding="utf-8").rstrip("\n")
        # 插在 mid 的 §Defer header 之前（mid 內第一個 ## Defer），否則 mid 結尾
        insert_at = None
        for j, l in enumerate(out):
            if j >= (len(lines[:h0]) + len(intro) + 1) and l.startswith("## Defer 給觀察者拍板（"):
                insert_at = j
                break
        block = rec.split("\n") + [""]
        if insert_at is not None:
            out = out[:insert_at] + block + out[insert_at:]
        else:
            out += [""] + block

    out += lines[i_archived:]
    path.write_text("\n".join(out), encoding="utf-8")
    print(f"\n✅ written — §未消化 {len(entries)}→{len(kept)}，{len(spans)} section 合併為 1")
    return 0


def main():
    base = argparse.ArgumentParser(add_help=False)
    base.add_argument("--file", default=str(DEFAULT_LESSONS), help="LESSONS-INBOX path")

    p = argparse.ArgumentParser(
        description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter, parents=[base]
    )
    sub = p.add_subparsers(dest="cmd", required=True)

    a = sub.add_parser("audit", parents=[base], help="§未消化 結構 + Stage 0a + triage 排序")
    a.add_argument("--top", type=int, default=12)
    a.set_defaults(fn=cmd_audit)

    c = sub.add_parser("chunk", parents=[base], help="fan-out 分析 line-range 切段")
    c.add_argument("--agents", type=int, default=6)
    c.set_defaults(fn=cmd_chunk)

    s = sub.add_parser("sweep", parents=[base], help="deterministic keeper-based sweep（dry-run default）")
    s.add_argument("--keep", help="keeper allowlist 檔（每行一個 ### header substring；- = stdin）")
    s.add_argument("--record", help="distill traceability block 檔，append 進 §已消化")
    s.add_argument("--apply", action="store_true", help="實際寫入（否則 dry-run）")
    s.add_argument("--force", action="store_true", help="允許保留 0 條（危險）")
    s.set_defaults(fn=cmd_sweep)

    args = p.parse_args()
    sys.exit(args.fn(args))


if __name__ == "__main__":
    main()
