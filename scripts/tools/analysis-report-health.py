#!/usr/bin/env python3
"""analysis-report-health.py — 分析報告誠實 gate linter（ANALYSIS-PIPELINE Stage 6）

把「防分析幻覺」的判斷從『我這次記得做』變成『不做就紅燈』。鏡像 research-report-health.py
的架構（stdlib-only / 退出碼 / --json / 可接 CI），但檢的是**數據分析報告**的誠實脊椎，
不是 Stage 1 研究報告的搜尋軌跡。

對應 design report §三 分析幻覺失敗模式目錄 H1-H9：
  window-defined      → 沒框窗口/邊界 = H4/H6 混淆波/新鮮感失守
  confounder-section  → 沒列 confounder = H2/H3/H8 沒排除
  raw-archived        → 沒歸檔 raw = 不可重現
  falsification       → 沒證偽段 = H7 自我驗證偏誤
  scope-disambig      → 講停留/avgSessionDuration 沒分 session/page 級 = H1（最致命）
  rate-vs-count       → 沒率量紀律 = H2
  verdict             → 沒明確結論

用法:
  analysis-report-health.py reports/homepage-redesign-impact-D+10-2026-06-05.md
  analysis-report-health.py {file} --tier=deep      # 預設，全 5 hard
  analysis-report-health.py {file} --tier=light     # 只 raw-archived hard
  analysis-report-health.py {file} --json
退出碼: 0 PASS / 1 FAIL（hard 未過）/ 2 檔案問題。

來源: 2026-06-05 ANALYSIS-PIPELINE 造橋（design §四 + §七.1 結構性 gate）。
"""
import argparse
import json
import re
import sys
from pathlib import Path


def load(path):
    p = Path(path)
    if not p.exists():
        print(f"❌ 檔案不存在: {path}", file=sys.stderr)
        sys.exit(2)
    return p.read_text(encoding="utf-8")


def has(text, *patterns):
    return any(re.search(p, text, re.I) for p in patterns)


def check_window(t):
    ok = has(t, r"^windows:", r"\bBEFORE\b", r"\bAFTER\b", r"窗口", r"boundary",
             r"分界", r"before/after", r"D\+\d+") and \
        len(re.findall(r"20\d\d-\d\d-\d\d|\d{1,2}/\d{1,2}", t)) >= 2
    return ok, "需定義分析窗口/邊界（兩個以上日期 + BEFORE/AFTER 或 attribution 分界）"


def check_confounder(t):
    ok = has(t, r"confounder", r"混淆", r"但書", r"caveat", r"\bH[1-9]\b",
             r"排除", r"lag", r"attribution.lag", r"流量混入", r"爬蟲", r"crawler")
    return ok, "需有 confounder / 但書段（列出並處理混淆源，至少 attribution lag / 流量混入 / 爬蟲其一）"


def check_raw(t):
    ok = has(t, r"reports/research", r"raw.*json", r"\.json", r"原始數據", r"附錄.*數據", r"raw dump")
    return ok, "需指向歸檔的 raw 查詢資料（reports/research/*.json）以保可重現"


def check_falsify(t):
    # falsification can be framed as: explicit counter-explanation (impact reports)
    # OR anti-over-attribution / anti-bias self-check (attribution reports). Both守 H7.
    ok = has(t, r"反例", r"反解釋", r"證偽", r"falsif", r"自我驗證", r"最強反",
             r"無法.{0,6}排除", r"也可能是", r"counter", r"anti-bias", r"自檢",
             r"不要把.{0,8}(全給|講大|過頭)", r"別把.{0,12}(講大|講過頭|全給)",
             r"誠實的故事", r"把數據講準", r"不亂歸因", r"過度歸因", r"Q13")
    return ok, "需有證偽/反解釋段（最強反解釋+為何不成立，或反過度歸因/anti-bias 自檢，守 H7 自我驗證偏誤）"


def check_scope(t):
    # only fires if the report talks about dwell / session duration
    mentions_dwell = has(t, r"avgSessionDuration", r"averageSessionDuration", r"停留",
                         r"session\s*dur", r"engagementDuration", r"dwell")
    if not mentions_dwell:
        return True, "(不涉及停留指標，scope 檢查不適用)"
    disambig = has(t, r"session\s*級", r"page\s*級", r"user\s*級", r"session-scoped",
                   r"page-scoped", r"userEngagementDuration", r"每人", r"per.user",
                   r"session 變深", r"尺度")
    return disambig, "講停留/avgSessionDuration 必須區分 session 級 vs page 級（H1 最致命：+334% session 級 ≠ page 級停留）"


def check_rate(t):
    ok = has(t, r"engagementRate", r"bounceRate", r"看率", r"率.{0,4}量", r"不用.{0,4}絕對",
             r"跳出率", r"互動率", r"per-user", r"每人")
    return ok, "需有率 vs 量紀律（用 engagementRate/bounce/page 級，當 user 量變動時不用絕對數）"


def check_verdict(t):
    ok = has(t, r"verdict", r"結論", r"判定", r"## .*結論", r"TL;DR", r"一句話結論")
    return ok, "需有明確 verdict / 結論"


def check_prereg(t):
    # v1.1：預先註冊紀律 — 報告有沒有明說它的假設 + 成功/證偽判準（對付 H7 搬龍門）
    ok = has(t, r"假設", r"成功判準", r"證偽判準", r"預先註冊", r"pre.?reg",
             r"hypothesis", r"^windows:", r"成功/?證偽", r"判準")
    return ok, "(v1.1) 宜先宣告假設 + 成功/證偽判準（pre-registration，對付 H7 事後搬龍門）"


def check_mission(t):
    # v1.1：Goodhart / 使命對齊 — 優化型分析有沒有問「這指標服務 MANIFESTO 還是 goodhart 一個代理」
    optimization = has(t, r"改版", r"優化", r"轉換率", r"提升.{0,4}engagement", r"建議.{0,8}(上移|重設計|加)", r"feature")
    if not optimization:
        return True, "(非優化型分析，使命對齊檢查不適用)"
    ok = has(t, r"Goodhart", r"使命", r"代理指標", r"proxy", r"MANIFESTO", r"clickbait",
             r"靈魂", r"背叛", r"策展.{0,4}靈魂", r"局部.{0,2}最高")
    return ok, "(v1.1) 優化型分析宜問：這個指標服務 MANIFESTO，還是 goodhart 一個代理（engagement↑但靈魂↓）"


CHECKS = [
    ("window-defined", "hard", check_window),
    ("confounder-section", "hard", check_confounder),
    ("raw-archived", "hard", check_raw),
    ("falsification", "hard", check_falsify),
    ("scope-disambig", "hard", check_scope),
    ("rate-vs-count", "warn", check_rate),
    ("verdict", "warn", check_verdict),
    ("pre-registration", "warn", check_prereg),
    ("mission-alignment", "warn", check_mission),
]

LIGHT_HARD = {"raw-archived"}  # light tier: only require reproducibility


def main():
    ap = argparse.ArgumentParser(description="Analysis-report honesty-gate linter")
    ap.add_argument("file")
    ap.add_argument("--tier", choices=["deep", "light"], default="deep")
    ap.add_argument("--json", action="store_true")
    a = ap.parse_args()
    t = load(a.file)

    results = []
    hard_fail = 0
    for cid, sev, fn in CHECKS:
        ok, msg = fn(t)
        eff = sev
        if a.tier == "light" and sev == "hard" and cid not in LIGHT_HARD:
            eff = "warn"
        status = "PASS" if ok else ("FAIL" if eff == "hard" else "WARN")
        if not ok and eff == "hard":
            hard_fail += 1
        results.append({"check": cid, "severity": eff, "status": status, "detail": msg if not ok else ""})

    passed = hard_fail == 0
    if a.json:
        print(json.dumps({"file": a.file, "tier": a.tier, "passed": passed,
                          "hard_fail": hard_fail, "checks": results}, ensure_ascii=False, indent=2))
        sys.exit(0 if passed else 1)

    icon = {"PASS": "✅", "WARN": "⚠️ ", "FAIL": "❌"}
    print(f"🧬 analysis-report-health [{a.tier}] {a.file}")
    for r in results:
        line = f"   {icon[r['status']]} {r['check']:<20} {r['status']}"
        if r["detail"]:
            line += f" — {r['detail']}"
        print(line)
    print(f"\n{'✅ PASS' if passed else '❌ FAIL'}  (hard_fail={hard_fail})")
    sys.exit(0 if passed else 1)


if __name__ == "__main__":
    main()
