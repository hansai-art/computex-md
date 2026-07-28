#!/usr/bin/env python3
"""agent-report-health.py — 委派 agent 分部報告收件品質閘門（receipt gate）

姊妹儀器 research-report-health.py 驗「組裝後的主 report SSOT」；本儀器驗更上游的
「單一 agent 回來的分部報告」——orchestrator 收到 task-notification 落檔後、開始任何
合成之前跑。回答三個問題：**這份是不是壓縮過的摘要？存放位置合不合法？結構完不完整？**

誕生背景（2026-07-05 柯智棠健檢，哲宇 directive「儀器化分部報告品質硬門檻 + 通知呼叫
session 疑慮/為什麼/思考方向」）：柯智棠 EVOLVE 的 4 隻研究 agent 各回 ~20KB 逐條軌跡，
orchestrator 收到後壓成 ~6KB 主題摘要存 scratchpad，report §8 蒸發，gate v1 照樣 PASS。
同病三例（柯智棠救回 / 蘇打綠救回 / 台灣醫療 5 份 raw 永久遺失）。斷點在收件那 30 秒，
所以閘門也要站在收件那 30 秒。

閾值校準（2026-07-05 真實 corpus dogfood，REFLEXES #66）：
  該攔（orchestrator 壓縮版 aggregate ×4）: 5-6KB / 軌跡 2-9 行 / 宣稱 28-61 次搜尋
  該過（agent 真 final message ×8）:       14-38KB / 軌跡 13-62 行
  → 體積分界 8KB、軌跡分界 10 行，兩側都有 ≥2x margin

v2（2026-07-06 施振榮 corpus）：搜尋日誌有四種合法格式（inline 箭頭 / 編號 WebSearch /
  編號 WebFetch / markdown 表），v1 軌跡 parser 只認箭頭 → §A/§B/§C/§D（33-77KB 完整報告）
  全被誤判「軌跡 0-3 行 = 壓縮 FAIL」。兩處修：(1) 軌跡 parser section-scoped + 四格式通吃；
  (2) 加「內容密集反訊號」——體積 ≥2×min_kb + 結構 ≥4/5 + (URL≥10 或「」引語≥30) 成立時，
  軌跡類疑慮降 hard→warn（體積 gate 與存放位置維持 hard，真 stub<8KB 照樣 FAIL，柯智棠防護不動）。

v3（2026-07-12 台灣茶文化 corpus，哲宇 callout「footnote 會寫不精準」）：來源溯源率 gate——
  agent 交叉驗證真的做了，但把多來源壓成「WebSearch 綜合（站名、站名）」aggregate 標籤轉錄：
  逐字引語活著、URL 蒸發，writer 的 [^n]: [Title](URL) footnote 斷源。這是鐵律 8 的 sub-agent 版
  （來源在 agent 轉錄那 30 秒蒸發，不是 orchestrator 收件那 30 秒）。v2 只驗 URL 總數 ≥5，
  rawA 有 6 條 URL 就穿透。校準：該攔 rawA 38% / rawB 36%（aggregate 斷源 15/18 條）；
  該過（帶警）rawC 67%。→ 來源行 ≥5 時：可溯率 <60% = hard，<85% = warn。
  可溯 = 完整 URL / repo 路徑 / 正式書目（《刊名》+期/頁）/ 同上前引。bare domain（站名）不算——
  footnote 需要能 Ctrl-F 驗證的完整 URL。契約 canonical：REWRITE-PIPELINE Step 1.8-ter。

輸出 = 給呼叫 session 的疑慮通知：每條疑慮附「為什麼」+「可能的思考方向」。
stdlib-only。

用法:
  python3 scripts/tools/agent-report-health.py reports/research/2026-07/{slug}-research-A.md
  python3 scripts/tools/agent-report-health.py {file} --claimed 60     # prompt 給的搜尋配額 / agent 宣稱數
  python3 scripts/tools/agent-report-health.py {file} --min-kb 8 --min-trail 10
  python3 scripts/tools/agent-report-health.py {file} --json
退出碼: 0 = PASS, 1 = FAIL (hard 疑慮), 2 = 檔案問題, 3 = CONCERN (僅 warn 疑慮)
"""
import argparse
import json
import re
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[2]

# ── 訊號 regex ───────────────────────────────────────────────────────
TRAIL_SECTION_RE = re.compile(
    r"#+\s*.*(搜尋(軌跡|紀錄|記錄|日誌)|軌跡|search\s*(log|trail)|query\s*log|逐條)", re.IGNORECASE)
# 搜尋日誌「一條 query」可能長成四種樣子（2026-07-06 施振榮 corpus 校準）：
#   inline 箭頭：  - query → 一句話發現 → [source](URL)     （canonical）
#   編號工具呼叫： 1. WebSearch「台積電 市值」               （§D）
#   編號 fetch：   2. **WebFetch https://…**                （§A）
#   markdown 表：  | 20 | WebFetch | verse.com.tw… |          （§C）
# entry = 條目起手式（編號 / bullet / 表列）；signal = 帶搜尋語意的證據。兩者皆備才算一條軌跡。
TRAIL_ENTRY_RE = re.compile(r"^\s*(?:\d+[\.、\)]|[-*]|\|)")
QUERY_SIGNAL_RE = re.compile(r"→|「|https?://|WebSearch|WebFetch|\bquery\b|搜尋", re.IGNORECASE)
QUOTE_RE = re.compile(r"「")
CLAIMED_RE = re.compile(r"(\d+)\s*(?:次搜尋|次 web|searches|search(?:es)?\b|queries)", re.IGNORECASE)
EPHEMERAL_RE = re.compile(r"/private/tmp/claude|/tmp/claude-|scratchpad/")
URL_RE = re.compile(r"https?://[^\s\)\]\>\"'，。、；]+")
BARE_DOMAIN_RE = re.compile(r"\b[a-z0-9][a-z0-9-]*(?:\.[a-z0-9-]+)+\.(?:tw|com|org|net|cn|jp|kr|io|cc|news)\b")
# ── v3 來源溯源率（2026-07-12 茶文化 corpus）────────────────────────────
SOURCE_LINE_RE = re.compile(r"【來源[^】]*】")
REPO_PATH_RE = re.compile(r"\b(?:knowledge|reports|docs|scripts|public)/[^\s】)]+")
FORMAL_CITE_RE = re.compile(r"《[^》]{2,60}》|頁\s*\d+|第?\s*\d+\s*期")  # 正式書目：刊名/頁碼/期數
SAME_AS_ABOVE_RE = re.compile(r"同上|見上|前引")
AGGREGATE_LABEL_RE = re.compile(
    r"(?:WebSearch|WebFetch|搜尋)[^】\n]{0,14}(?:綜合|摘要|多輪)|多來源|多站交叉|綜合多個")


def _source_traceable(line: str) -> bool:
    """一條【來源】行是否可溯源到 footnote 能用的層級。
    bare domain（站名）不算——footnote 需要能 Ctrl-F 驗證的完整 URL。"""
    return bool(URL_RE.search(line) or REPO_PATH_RE.search(line)
                or FORMAL_CITE_RE.search(line) or SAME_AS_ABOVE_RE.search(line))
EXPECTED_SECTIONS = (
    ("搜尋軌跡/紀錄", TRAIL_SECTION_RE),
    ("Findings", re.compile(r"#+\s*.*findings|#+\s*.*發現", re.IGNORECASE)),
    ("引語庫", re.compile(r"#+\s*.*(引語|verbatim|quote)", re.IGNORECASE)),
    ("negative findings", re.compile(r"#+\s*.*(negative|沒找到|查無)", re.IGNORECASE)),
    ("質地素材", re.compile(r"#+\s*.*(質地|素材|texture|給 writer)", re.IGNORECASE)),
)


def _trail_section_lines(lines):
    """抓出「搜尋軌跡/日誌」section 的內容行（header 之後到下一個同級或更高級 heading）。
    section-scoped 計數避免把 Findings/引語庫 的表列誤當軌跡（whole-file 計數會虛胖）。"""
    start_i, level = None, 2
    for i, l in enumerate(lines):
        if TRAIL_SECTION_RE.search(l):
            hm = re.match(r"^\s*(#+)", l)
            if hm:  # 必須是 heading 行才算 section 起點
                start_i, level = i, len(hm.group(1))
                break
    if start_i is None:
        return []
    out = []
    for l in lines[start_i + 1:]:
        hm = re.match(r"^\s*(#+)\s", l)
        if hm and len(hm.group(1)) <= level:
            break
        out.append(l)
    return out


def analyze(path: Path):
    txt = path.read_text(encoding="utf-8", errors="ignore")
    lines = txt.split("\n")
    size_kb = len(txt.encode("utf-8")) / 1024
    # 軌跡計數：section-scoped + 四格式通吃（編號/bullet/表列 + 搜尋語意）
    section_lines = _trail_section_lines(lines)
    trail_lines = sum(1 for l in section_lines
                      if TRAIL_ENTRY_RE.match(l) and QUERY_SIGNAL_RE.search(l))
    quotes = len(QUOTE_RE.findall(txt))  # 「」verbatim 引語密度 = 抗壓縮的內容訊號
    has_trail_section = bool(TRAIL_SECTION_RE.search(txt))
    claimed_m = CLAIMED_RE.search(txt)
    claimed = int(claimed_m.group(1)) if claimed_m else None
    ephemeral = len(EPHEMERAL_RE.findall(txt))
    urls = len(set(URL_RE.findall(txt)) | set(BARE_DOMAIN_RE.findall(txt)))
    # v3 來源溯源率：逐條【來源】行判可溯與否
    src_lines = [l for l in lines if SOURCE_LINE_RE.search(l)]
    traceable = sum(1 for l in src_lines if _source_traceable(l))
    agg_untraceable = sum(1 for l in src_lines
                          if AGGREGATE_LABEL_RE.search(l) and not _source_traceable(l))
    sections = [name for name, r in EXPECTED_SECTIONS if r.search(txt)]
    # 存放位置
    try:
        resolved = path.resolve()
        in_repo = REPO_ROOT in resolved.parents or resolved == REPO_ROOT
        path_ephemeral = bool(EPHEMERAL_RE.search(str(resolved))) or str(resolved).startswith(("/tmp/", "/private/tmp/", "/var/folders/"))
    except OSError:
        in_repo, path_ephemeral = False, True
    return dict(
        size_kb=round(size_kb, 1), trail_lines=trail_lines,
        has_trail_section=has_trail_section, claimed=claimed,
        ephemeral_refs=ephemeral, urls=urls, quotes=quotes,
        source_lines=len(src_lines), traceable_sources=traceable,
        aggregate_untraceable=agg_untraceable,
        source_coverage=(round(traceable / len(src_lines), 2) if src_lines else None),
        sections=sections, sections_count=len(sections),
        in_repo=in_repo, path_ephemeral=path_ephemeral,
        path=str(path),
    )


def grade(m, min_kb: float, min_trail: int, claimed_override):
    """回傳 concerns list。每條: (check, severity hard|warn, got, expect, why, directions[])"""
    concerns = []
    claimed = claimed_override or m["claimed"]

    # ── 抗壓縮反訊號（v2, 2026-07-06 施振榮 corpus 修）──────────────────────
    # 病灶：v1 只用「軌跡行數」判壓縮，但 agent 的搜尋日誌有四種合法格式（inline 箭頭 /
    # 編號 WebSearch / 編號 WebFetch / markdown 表），後三種軌跡計數天生偏低 → 38KB 的
    # 完整報告被誤判「壓縮鐵證 FAIL」（§B/§D 實例）。修法：先把軌跡 parser 放寬（analyze
    # 已做），再加一道反訊號——一份「體積 ≥2×min_kb + 結構 ≥4/5 + 內容密集（URL≥10 或
    # 「」引語≥30）」的報告，體積本身已排除柯智棠病（整份 stub 成 6KB）；此時軌跡稀疏多半
    # 是 agent 摘要/改格式 query-trail、findings 完好 → 把軌跡類疑慮降 hard→warn（仍提醒補
    # 軌跡，但不擋合成）。體積 gate 與存放位置維持 hard——真 stub（<8KB）照樣 FAIL，柯智棠
    # 防護不鬆動。
    substantive = (m["size_kb"] >= 2 * min_kb and m["sections_count"] >= 4
                   and (m["urls"] >= 10 or m.get("quotes", 0) >= 30))
    trail_sev = "warn" if substantive else "hard"
    rich_note = (f"（本份 {m['size_kb']}KB / 結構 {m['sections_count']}/5 / "
                 f"URL {m['urls']} / 「」{m.get('quotes', 0)} = 內容密集反訊號成立，"
                 f"軌跡稀疏判為『agent 摘要 query-trail』非『整份 stub』，降 warn）"
                 if substantive else "")

    if m["path_ephemeral"] or not m["in_repo"]:
        concerns.append((
            "存放位置在 repo 外（tmp / scratchpad / 其他）", "hard",
            m["path"], "repo 內（如 reports/research/{YYYY-MM}/）",
            "tmp 與 scratchpad 是倒數計時的刪除佇列。台灣醫療與全民健保的 5 份 raw 寫著「永久存放於 /tmp」，一個月後全數蒸發、無法救回",
            ["立即把檔案移入 reports/research/{YYYY-MM}/ 並納入 commit",
             "如果內容來自 task-notification，直接把 <result> verbatim 寫到 repo 路徑",
             "檢查同 session 其他 agent 的落檔位置是否同病"],
        ))
    if m["size_kb"] < min_kb:
        concerns.append((
            f"體積 {m['size_kb']}KB 低於分界 {min_kb}KB", "hard",
            f"{m['size_kb']}KB", f"≥ {min_kb}KB",
            "研究 agent 真實 final message 實測 14-38KB；orchestrator 壓縮版 aggregate 實測 5-6KB。體積落在壓縮版級距 = 這份極可能已被摘要過（柯智棠病）",
            ["回頭找 task-notification 的 <result> 原文比對長度——如果原文更長，這份是收件後壓縮版，用原文覆蓋",
             "如果 notification 也這麼短，檢查 subagent transcript（output_file symlink）撈完整 final message",
             "如果 agent 真的只回這麼少，用 SendMessage 要求 agent 補完整逐條軌跡",
             "窄子題 agent 的合法短回報可用 --min-kb 調低，但先排除前三種可能"],
        ))
    if not m["has_trail_section"]:
        concerns.append((
            "缺「搜尋軌跡」section", trail_sev,
            "無", "五段回報結構第一段",
            "逐條 query→發現→URL 是分部報告的骨架；缺席通常是被重新組織成主題式摘要的簽名（壓縮的第一個犧牲品就是軌跡）" + rich_note,
            ["確認 spawn prompt 是否要求五段結構——沒要求就是 prompt 退化，補 Step 1.8-bis 模板",
             "從 notification / subagent transcript 找原始軌跡",
             "要求 agent 重報：只補「§X 搜尋軌跡（逐條）」段即可"],
        ))
    if m["trail_lines"] < min_trail:
        concerns.append((
            f"逐條軌跡 {m['trail_lines']} 行低於分界 {min_trail} 行", trail_sev,
            str(m["trail_lines"]), f"≥ {min_trail}",
            "真實 final message 實測 13-62 行軌跡；壓縮版實測 2-9 行。軌跡行數是「壓縮與否」最直接的尺（但四種搜尋日誌格式中僅 inline 箭頭型行數高，編號/表列/prose 型天生偏低）" + rich_note,
            ["同上——先驗 notification / transcript 是否有更完整版本",
             "對照宣稱搜尋數：宣稱高而軌跡少 = 壓縮或截斷的鐵證"],
        ))
    if claimed and m["trail_lines"] < claimed * 0.5:
        concerns.append((
            f"宣稱 {claimed} 次搜尋但軌跡只記錄 {m['trail_lines']} 行（{round(m['trail_lines']/claimed*100)}%）", "warn",
            f"{m['trail_lines']}/{claimed}", "≥ 50%",
            "宣稱數與記錄數的落差是三種病的共同症狀：agent 自行摘要、orchestrator 收件後壓縮、通知截斷。柯智棠 aggregate 宣稱 60 次只留 9 行（15%）",
            ["用 subagent transcript 實數 tool calls 當外部尺（REFLEXES #69），別信宣稱數",
             "落差確認後按體積/軌跡的 directions 救援"],
        ))
    if m["sections_count"] < 4:
        concerns.append((
            f"五段回報結構只偵測到 {m['sections_count']}/5（{('、'.join(m['sections']) or '無')}）", "warn",
            f"{m['sections_count']}/5", "≥ 4/5",
            "缺段可能是壓縮（negative findings 與質地素材最常被吃掉），也可能是 agent 沒照模板",
            ["對照 Step 1.8-bis 五段模板檢查缺哪段、去 notification 原文找",
             "negative findings 缺席特別危險——「搜了沒找到」的紀錄防止下輪重搜與幻覺補洞"],
        ))
    if m["ephemeral_refs"] > 0:
        concerns.append((
            f"內文引用 ephemeral 路徑 {m['ephemeral_refs']} 處", "warn",
            str(m["ephemeral_refs"]), "0",
            "分部報告內再指向 tmp/scratchpad = 又一層會蒸發的依賴",
            ["把被指向的內容也 verbatim 收進 repo，或改指 repo 內路徑"],
        ))
    if m["urls"] < 5:
        concerns.append((
            f"來源 URL/網域僅 {m['urls']} 個", "warn",
            str(m["urls"]), "≥ 5",
            "研究型分部報告每條軌跡都該帶來源；來源稀少可能是壓縮掉了，也可能該 agent 任務本來就非搜尋型（如 persona 發散）",
            ["非搜尋型 agent（persona / writer / verifier 回報）本檢查可忽略",
             "搜尋型 agent 來源少 → 回 notification 原文找被刪的 URL"],
        ))
    # ── v3 來源溯源率 gate（2026-07-12 茶文化 corpus，哲宇 callout「footnote 會寫不精準」）──
    if m["source_lines"] >= 5:
        cov = m["traceable_sources"] / m["source_lines"]
        if cov < 0.85:
            sev = "hard" if cov < 0.6 else "warn"
            concerns.append((
                f"來源溯源率 {round(cov*100)}%（{m['traceable_sources']}/{m['source_lines']} 條可溯，"
                f"aggregate 斷源 {m['aggregate_untraceable']} 條）", sev,
                f"{round(cov*100)}%", "≥ 85%（<60% = hard）",
                "「WebSearch 綜合（站名、站名）」不是來源——逐字引語活著、URL 蒸發，writer 的 "
                "[^n]: [Title](URL) footnote 無法精準落地，verifier 也無法 Ctrl-F。這是鐵律 8 的 "
                "sub-agent 版：來源在 agent 轉錄那 30 秒蒸發（2026-07-12 茶文化 rawA/B 實例：交叉"
                "驗證真做了、84 條來源行僅 ~35% 帶 URL）",
                ["逐條回到 WebSearch 結果把依賴的 URL 列出——搜尋工具回傳本身帶連結，蒸發發生在轉錄",
                 "URL 找不回 → WebFetch 重新定位該 claim 的來源頁，補 URL + 逐字",
                 "真的無法溯源 → 該來源行改標【無法溯源】，finding 降級為線索，禁止進 footnote / 引語庫",
                 "契約 canonical：REWRITE-PIPELINE Step 1.8-ter（每來源一行、禁 aggregate 標籤）"],
            ))
    return concerns


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("report")
    ap.add_argument("--claimed", type=int, default=None,
                    help="prompt 配額 / agent 宣稱的搜尋數（不給則從內文 parse）")
    ap.add_argument("--min-kb", type=float, default=8.0)
    ap.add_argument("--min-trail", type=int, default=10)
    ap.add_argument("--json", action="store_true")
    args = ap.parse_args()

    p = Path(args.report)
    if not p.is_file():
        print(f"❌ 找不到分部報告: {p}", file=sys.stderr)
        sys.exit(2)

    m = analyze(p)
    concerns = grade(m, args.min_kb, args.min_trail, args.claimed)
    hard = sum(1 for c in concerns if c[1] == "hard")
    warn = sum(1 for c in concerns if c[1] == "warn")
    verdict = "FAIL" if hard else ("CONCERN" if warn else "PASS")

    if args.json:
        print(json.dumps(dict(
            file=str(p), metrics=m, verdict=verdict, hard=hard, warn=warn,
            concerns=[dict(check=c, severity=s, got=g, expect=e, why=w, directions=d)
                      for c, s, g, e, w, d in concerns]),
            ensure_ascii=False, indent=2))
        sys.exit(0 if verdict == "PASS" else (1 if verdict == "FAIL" else 3))

    print(f"🔬 agent-report-health  {p}")
    cov_str = (f"{round(m['source_coverage']*100)}%" if m['source_coverage'] is not None else "—")
    print(f"   {m['size_kb']}KB / 軌跡 {m['trail_lines']} 行 / 來源 {m['urls']} / "
          f"溯源 {m['traceable_sources']}/{m['source_lines']}({cov_str}) / "
          f"「」{m['quotes']} / 結構 {m['sections_count']}/5 / 宣稱搜尋 {args.claimed or m['claimed'] or '—'}")
    if not concerns:
        print("   ✅ 無疑慮：體積、軌跡密度、結構、存放位置皆在真實 final message 級距")
    for check, sev, got, expect, why, directions in concerns:
        icon = "🔴" if sev == "hard" else "⚠️ "
        print(f"\n   {icon} [{check}]")
        print(f"      為什麼：{why}")
        print(f"      思考方向：")
        for i, d in enumerate(directions, 1):
            print(f"        ({i}) {d}")
    print(f"\n   Verdict: {verdict}  (hard={hard} warn={warn})")
    if verdict == "FAIL":
        print("   ⛔ 收件不合格 = 不准開始合成 §6 / 不進 Stage 2。先照思考方向救回 raw。")
    elif verdict == "CONCERN":
        print("   🟡 可續行，但每條疑慮需在 orchestrator 回報裡明示處置（採信 / 救援 / 忽略理由）。")
    sys.exit(0 if verdict == "PASS" else (1 if verdict == "FAIL" else 3))


if __name__ == "__main__":
    main()
