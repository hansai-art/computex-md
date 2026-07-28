#!/usr/bin/env python3
"""support-funnel.py — 贊助漏斗查詢工具

背景：文章結尾「簽名檔 CTA」（分享／一起編輯／贊助維護）上線後，需要一支工具
把「讀者看到文章 → 看到簽名檔 → 點贊助連結 → 實際完成贊助」串成一條可量的漏斗。
設計脈絡見 reports/support-cta-signature-design-2026-07-16.md。

四階段定義（GA4 event / dimension ↔ transactions SSOT 對照）：

  階段 1．文章曝光
    GA4 event `page_view`，用 pagePath 對文章分類做 regex 過濾（跟
    fetch-ga4.py 的 ARTICLE_CATEGORIES 同一套）。
    原本想用 `section_view` 的 `page_type=article` 當 proxy（任務 brief 建議的
    另一條路），但實測 customEvent:page_type 對 Data API 回 400「not valid
    dimension」——雖然 register-ga4-custom-dimensions.py 的 ENGAGEMENT_DIMENSIONS
    有列這個 param，但可能還沒實際生效或需要等 propagation。pagePath regex 是
    fetch-ga4.py 已經在用、驗證過會動的路徑，所以階段 1 走這條，不走 page_type。

  階段 2．看到簽名檔
    GA4 event `section_view`，custom dimension `section` = `article_signature`
    （article.template.astro 對簽名檔區塊 fire 的 data-ga-view）。

  階段 3．點贊助連結
    GA4 event `outbound_click`，custom dimension `link_url` contains
    `portaly.cc/taiwanmd/support`。用 `section` dimension 分組即可對照各入口：
      - article_signature   文章結尾簽名檔（本次新上線的入口）
      - footer_support       頁尾
      - about_sponsors       關於頁贊助區
      - contribute_support   貢獻頁支持區
      - contribute           首頁貢獻區塊（ContributeSection.astro）
    這五個 data-ga-section 值都已在對應模板埋好（見 EventTracker.astro 對
    outbound_click 用 `closest('[data-ga-section]')` 取 section 的邏輯）。

  階段 4．實際轉換
    本地讀 data/supporters/transactions.json（SSOT，append-only 流水帳，
    每筆有 date/timestamp/amount/type/status）。只算 status == "received"
    且 date 落在查詢窗內的筆數與金額，不打任何 API。

資料尚空的注意事項：
  簽名檔 CTA（含 footer_support/about_sponsors/contribute_support 三個新埋
  的 data-ga-section）是 2026-07-16 才上線的改動，上線前的查詢窗內這些
  event/dimension 組合本來就沒有資料。查到 0 筆是預期行為，不是查詢寫錯——
  本工具會在 0 筆時印「事件剛上線，資料窗尚空」而不是報錯或留空白嚇人。

Creds/降級：
  沿用 scripts/tools/lib/sense_client.py 的 GA4 憑證慣例（沿用 ga-query.py /
  fetch-ga4.py 同一套：~/.config/taiwan-md/credentials/{.env,
  google-service-account.json} + ~/.config/taiwan-md/venv 自動 re-exec）。
  若 creds 不存在，不 crash、不印 traceback——印一行清楚說明後，只跑「階段 4：
  transactions 本地統計」那段（不需要 API），照樣 exit 0。GA4 API 呼叫本身
  失敗（權限/額度/dimension 未生效等）也各自包一層 try/except，個別階段降級
  成「查詢失敗：<原因>」，不會拖垮整支工具。

用法:
    python3 scripts/tools/support-funnel.py                  # 預設近 28 天
    python3 scripts/tools/support-funnel.py --days 7
    python3 scripts/tools/support-funnel.py --start 2026-07-01 --end 2026-07-16
    python3 scripts/tools/support-funnel.py --json            # 額外印一份機器可讀 JSON

來源: 2026-07-16 session（support-cta-f75a77 worktree），
      design: reports/support-cta-signature-design-2026-07-16.md
"""
import argparse
import json
import sys
import pathlib
from datetime import date, timedelta

# ── 沿用 ga-query.py 慣例：先掛 lib/ 到 path，reexec 進 venv 再 import google 系 ──
sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent))
from lib.sense_client import reexec_in_venv  # noqa: E402
reexec_in_venv()
from lib.sense_client import load_env, ga_run, SERVICE_ACCOUNT_FILE, ENV_FILE  # noqa: E402

REPO_ROOT = pathlib.Path(__file__).resolve().parents[2]
TRANSACTIONS_PATH = REPO_ROOT / "data" / "supporters" / "transactions.json"

# 階段 1：文章路徑分類，跟 fetch-ga4.py 的 ARTICLE_CATEGORIES 同一套 SSOT
# （沒有共用 import 是因為 fetch-ga4.py 沒把它拆成 importable 常數；
# 兩邊要改記得一起改）。
ARTICLE_CATEGORIES = (
    "food|culture|history|society|nature|technology|"
    "economy|lifestyle|people|geography|art|music"
)
ARTICLE_PATH_REGEX = rf"^/(en/|ja/|ko/|es/|fr/)?({ARTICLE_CATEGORIES})/[^/]+/?$"

# 階段 2：簽名檔區塊的 section dimension 值
SIGNATURE_SECTION = "article_signature"

# 階段 3：贊助連結的固定字串（含 utm 參數所以用 contains，不用 exact）
SUPPORT_LINK_SUBSTRING = "portaly.cc/taiwanmd/support"

# 階段 3 分組：已知入口的 data-ga-section 值 → 人話標籤
# （順序 = 漏斗設計報告裡列的順序，跟模板埋點對照見本檔頂部 docstring；
#   2026-07-16 全站盤點補 dashboard_supporters + semiont_support 兩個入口）
KNOWN_SUPPORT_SECTIONS = [
    ("article_signature", "文章結尾簽名檔"),
    ("footer_support", "頁尾"),
    ("about_sponsors", "關於頁贊助區"),
    ("contribute_support", "貢獻頁支持區"),
    ("contribute", "首頁貢獻區塊"),
    ("dashboard_supporters", "儀表板贊助時間軸"),
    ("semiont_support", "生命體頁"),
]


def check_ga4_creds():
    """檢查 GA4 creds 是否齊全，不呼叫 sense_client 那套會 sys.exit 的 fail()。

    回傳 (ok, reason)。ok=False 時 reason 是給人看的缺什麼/路徑在哪，
    讓 main() 決定要不要整段跳過 GA4 查詢、直接進 transactions-only 降級模式。
    """
    env = load_env()
    cred_path_str = env.get("GOOGLE_APPLICATION_CREDENTIALS", "").strip()
    if cred_path_str:
        cred_path = pathlib.Path(cred_path_str).expanduser()
    elif SERVICE_ACCOUNT_FILE.exists():
        cred_path = SERVICE_ACCOUNT_FILE
    else:
        return False, str(SERVICE_ACCOUNT_FILE)

    if not cred_path.exists():
        return False, str(cred_path)
    if not env.get("GA4_PROPERTY_ID", "").strip():
        return False, f"{ENV_FILE}（缺 GA4_PROPERTY_ID）"
    return True, None


def resolve_window(args):
    """算查詢窗的絕對日期字串（YYYY-MM-DD），GA4 query 跟 transactions 篩選共用
    同一組日期，避免「GA4 用相對日期、transactions 用另一套邏輯」兩邊窗口對不齊。
    """
    if args.start or args.end:
        if not (args.start and args.end):
            print("❌ --start 跟 --end 要一起給", file=sys.stderr)
            sys.exit(2)
        return args.start, args.end
    end_d = date.today()
    start_d = end_d - timedelta(days=args.days)
    return start_d.isoformat(), end_d.isoformat()


def safe_ga_total(event_name, extra_filters, start, end):
    """跑一個「只要總數」的 GA4 查詢（dims=[]），回傳 (count, error)。
    空結果視為合法的 0（資料窗尚空），不是錯誤；例外才算錯誤。
    """
    try:
        rows = ga_run(
            [], ["eventCount"], start, end,
            dim_filter=[("eventName", "exact", event_name)] + extra_filters,
        )
        if not rows:
            return 0, None
        return int(rows[0]["mets"][0]), None
    except Exception as e:  # noqa: BLE001 — 刻意廣抓，任何 API 例外都要降級不炸
        return None, f"{type(e).__name__}: {e}"


def safe_ga_group(event_name, extra_filters, group_dim, start, end):
    """跑一個「按某個 dimension 分組」的 GA4 查詢，回傳 (rows, error)。
    rows 是 [(dim值, count), ...]，依 count 由大到小。
    """
    try:
        rows = ga_run(
            [group_dim], ["eventCount"], start, end,
            dim_filter=[("eventName", "exact", event_name)] + extra_filters,
            order_by="eventCount", desc=True,
        )
        return [(r["dims"][0], int(r["mets"][0])) for r in rows], None
    except Exception as e:  # noqa: BLE001
        return None, f"{type(e).__name__}: {e}"


def load_transactions(start, end):
    """讀 transactions.json SSOT，篩出 status=received 且 date 落在 [start, end]
    的筆數。SSOT 的 date 欄本身就是 YYYY-MM-DD 字串，字典序比較剛好等於日期序，
    不用另外 parse。
    """
    if not TRANSACTIONS_PATH.exists():
        return [], f"找不到 {TRANSACTIONS_PATH}"
    try:
        data = json.loads(TRANSACTIONS_PATH.read_text())
    except Exception as e:  # noqa: BLE001
        return [], f"transactions.json 解析失敗：{type(e).__name__}: {e}"

    txs = data.get("transactions", [])
    in_window = [
        t for t in txs
        if t.get("status") == "received" and start <= t.get("date", "") <= end
    ]
    return in_window, None


def pct(numerator, denominator):
    if denominator in (None, 0):
        return "—"
    if numerator is None:
        return "—"
    return f"{numerator / denominator * 100:.1f}%"


def fmt_count(n, empty_note="事件剛上線，資料窗尚空"):
    if n is None:
        return "查詢失敗"
    if n == 0:
        return f"0（{empty_note}）"
    return f"{n:,}"


def main():
    ap = argparse.ArgumentParser(description="贊助漏斗查詢：文章曝光 → 看到簽名檔 → 點贊助 → 實際轉換")
    ap.add_argument("--days", type=int, default=28, help="查詢窗天數（預設 28，跟 --start/--end 二選一）")
    ap.add_argument("--start", default=None, help="查詢窗起日 YYYY-MM-DD（要跟 --end 一起給）")
    ap.add_argument("--end", default=None, help="查詢窗迄日 YYYY-MM-DD")
    ap.add_argument("--json", action="store_true", help="額外印一份機器可讀 JSON 到最後")
    args = ap.parse_args()

    start, end = resolve_window(args)
    print(f"贊助漏斗查詢窗：{start} ～ {end}\n")

    # 階段 4 不管 GA4 creds 在不在都要跑（本地檔案，不打 API）
    txs, tx_err = load_transactions(start, end)
    tx_count = len(txs)
    tx_amount_by_currency = {}
    for t in txs:
        cur = t.get("currency", "TWD")
        tx_amount_by_currency[cur] = tx_amount_by_currency.get(cur, 0) + t.get("amount", 0)

    result = {
        "window": {"start": start, "end": end},
        "stage4_transactions": {
            "count": tx_count,
            "amount_by_currency": tx_amount_by_currency,
            "error": tx_err,
        },
    }

    ok, reason = check_ga4_creds()
    if not ok:
        print(f"⚠️  缺 GA4 creds（路徑 {reason}），只輸出 transactions 端的統計\n")
        if tx_err:
            print(f"❌ {tx_err}")
        else:
            print("階段 4．實際轉換（transactions.json 本地統計）")
            print(f"  筆數：{tx_count}")
            if tx_amount_by_currency:
                amt_str = "、".join(f"{amt:,} {cur}" for cur, amt in tx_amount_by_currency.items())
                print(f"  金額：{amt_str}")
            else:
                print("  金額：0（查詢窗內沒有交易）")
        if args.json:
            print("\n" + json.dumps(result, ensure_ascii=False, indent=2))
        sys.exit(0)

    # ── GA4 三個階段，各自 try/except 降級，不互相拖垮 ──
    stage1, stage1_err = safe_ga_total(
        "page_view", [("pagePath", "regex", ARTICLE_PATH_REGEX)], start, end,
    )
    stage2, stage2_err = safe_ga_total(
        "section_view", [("customEvent:section", "exact", SIGNATURE_SECTION)], start, end,
    )
    stage3_rows, stage3_err = safe_ga_group(
        "outbound_click",
        [("customEvent:link_url", "contains", SUPPORT_LINK_SUBSTRING)],
        "customEvent:section", start, end,
    )
    stage3_total = None if stage3_rows is None else sum(c for _, c in stage3_rows)

    result["stage1_exposure"] = {"count": stage1, "error": stage1_err}
    result["stage2_signature_view"] = {"count": stage2, "error": stage2_err}
    result["stage3_support_click"] = {
        "count": stage3_total, "by_section": stage3_rows, "error": stage3_err,
    }

    # ── 漏斗表 ──
    print("漏斗表（各階段人次 + 相對上一階段轉換率）")
    print("-" * 60)
    print(f"1. 文章曝光（page_view）           {fmt_count(stage1, '查詢窗內沒有文章 page_view，數字異常請覆查')}")
    print(f"2. 看到簽名檔（section_view）       {fmt_count(stage2)}"
          f"    ← {pct(stage2, stage1) if stage1_err is None else '—'} of 階段 1")
    print(f"3. 點贊助連結（outbound_click）     {fmt_count(stage3_total)}"
          f"    ← {pct(stage3_total, stage2) if stage2_err is None else '—'} of 階段 2")
    print(f"4. 實際完成贊助（transactions）     {fmt_count(tx_count, '查詢窗內尚無交易')}"
          f"    ← {pct(tx_count, stage3_total) if stage3_err is None else '—'} of 階段 3")
    print("-" * 60)
    print(f"末端關鍵比率：點贊助 → 實際轉換 = {pct(tx_count, stage3_total) if stage3_err is None else '（階段 3 查詢失敗，算不出來）'}")

    for label, err in (
        ("階段 1", stage1_err), ("階段 2", stage2_err), ("階段 3", stage3_err),
    ):
        if err:
            print(f"⚠️  {label} 查詢失敗：{err}")

    # ── 各入口點擊分佈 ──
    print("\n各入口（section）點擊分佈 — 點贊助連結的 outbound_click 拆解")
    if stage3_err:
        print(f"  查詢失敗：{stage3_err}")
    elif stage3_total == 0:
        print("  0（事件剛上線，資料窗尚空——五個入口 article_signature/footer_support/"
              "about_sponsors/contribute_support/contribute 目前都還沒有點擊紀錄）")
    else:
        by_section = dict(stage3_rows)
        # 先印已知五個入口（沒資料也列出，方便看哪個入口目前掛零）
        seen = set()
        for section_key, label in KNOWN_SUPPORT_SECTIONS:
            count = by_section.get(section_key, 0)
            seen.add(section_key)
            print(f"  {label:12s}（{section_key}）  {count:>4} 次  {pct(count, stage3_total)}")
        # 再印任何不在已知清單內的 section（例如尚未 codify 進 KNOWN_SUPPORT_SECTIONS 的新入口）
        for section_key, count in stage3_rows:
            if section_key in seen:
                continue
            label = section_key if section_key else "(未標記入口 / data-ga-section 缺失)"
            print(f"  {label:12s}（{section_key or '空值'}）  {count:>4} 次  {pct(count, stage3_total)}")

    # ── 階段 4 detail：交易金額 ──
    print("\n階段 4 補充：查詢窗內實際交易明細")
    if tx_err:
        print(f"  {tx_err}")
    elif tx_count == 0:
        print("  查詢窗內沒有交易")
    else:
        if tx_amount_by_currency:
            amt_str = "、".join(f"{amt:,} {cur}" for cur, amt in tx_amount_by_currency.items())
            print(f"  {tx_count} 筆，共 {amt_str}")
        by_type = {}
        for t in txs:
            by_type[t.get("type", "unknown")] = by_type.get(t.get("type", "unknown"), 0) + 1
        type_str = "、".join(f"{k} {v} 筆" for k, v in by_type.items())
        print(f"  類型分佈：{type_str}")

    if args.json:
        print("\n" + json.dumps(result, ensure_ascii=False, indent=2))

    sys.exit(0)


if __name__ == "__main__":
    main()
