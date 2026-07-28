#!/usr/bin/env python3
"""
register-ga4-custom-dimensions.py — GA4 event-param custom dimension SSOT（一鍵註冊 + 對齊）

這份是「所有 instrumentation event param → custom dimension」的 single source of truth。
每次埋新 gtag event param，把它加進對應 *_DIMENSIONS list 再跑一次（idempotent，skip 已存在）。

背景：
  2026-04-13 γ session 上線 search event 追蹤；GA4 event param 必須註冊為 custom
  dimension 後才能在 Explore / Data API group by。2026-04-18 δ 用 Admin API 一鍵註冊 7
  個 search dim。2026-05-27 首頁 Wave 1+2+3 改版埋 6 個 homepage dim（當時走 Chrome MCP
  手動點，沒進這份 SSOT）。2026-05-29 D+2 watch 發現兩個 gap：
    (1) homepage_scroll_depth fire `depth_pct` 但只註冊了 `pct` → scroll attribution 全 (not set)
    (2) homepage_click fire `link_url` 但從沒註冊 → click 目的地 attribution 拿不到
  → 把 6 個 homepage dim 補進這份 SSOT（造橋：手動 Chrome 工作 codify 成可重跑的 code），
    並補 depth_pct + link_url，archive 死掉的 pct。

需要的權限：
  服務帳號 taiwan-md-reader@taiwan-md-sense.iam.gserviceaccount.com
  必須在 GA4 property 528789281 具備 **Editor** 角色（原先可能只是 Viewer）。
  若跑出 PermissionDenied → 到 GA4 Admin → Account/Property access management 升級角色。

資料保留：
  註冊後只有「之後的」事件會帶這些維度。歷史事件參數無法回補。

用法:
    python3 scripts/tools/register-ga4-custom-dimensions.py [--dry-run]
"""
import argparse
import os
import sys
from pathlib import Path

CONFIG_DIR = Path.home() / ".config" / "taiwan-md"
CREDENTIALS_DIR = CONFIG_DIR / "credentials"
VENV_DIR = CONFIG_DIR / "venv"

if VENV_DIR.exists() and sys.prefix != str(VENV_DIR):
    venv_python = VENV_DIR / "bin" / "python3"
    if venv_python.exists() and __name__ == "__main__":
        os.execv(str(venv_python), [str(venv_python), __file__, *sys.argv[1:]])


# ── search events（2026-04-13 上線，2026-04-18 δ 註冊）─────────────────────
SEARCH_DIMENSIONS = [
    ("search_term", "Search Term", "讀者在站內搜尋的 query 字串"),
    ("results_count", "Search Results Count", "該次搜尋回傳的結果筆數"),
    ("search_lang", "Search Language", "搜尋發生的語言介面 zh/en/ja/ko"),
    ("search_mode", "Search Mode", "搜尋模式 instant / submit / etc"),
    ("click_title", "Clicked Result Title", "從搜尋結果點擊的文章標題"),
    ("click_url", "Clicked Result URL", "從搜尋結果點擊的文章 URL"),
    ("click_position", "Clicked Result Position", "點擊結果在列表中的位置（1-based）"),
]

# ── engagement events（2026-05-27 Wave 1+2+3 homepage 上線；2026-06-14 改 EventTracker
#    跨頁共用 generic events scroll_depth / section_view / content_click /
#    outbound_click / time_milestone，全帶 page_type；homepage_* 事件改名）──
# param 名以 src/components/EventTracker.astro 實際 _fire() 送的為準（SSOT 對齊用）。
ENGAGEMENT_DIMENSIONS = [
    ("page_type", "Page Type", "事件發生在哪種頁型 home/article/category/latest...（2026-06-14 跨頁追蹤）"),
    ("section", "Engagement Section", "section_view / content_click 發生在哪個 landmark（related_articles/latest_rail/footnotes...）"),
    ("label", "Click Label", "content_click 子項 label（view_all_category/random_explore...）"),
    ("link_url", "Click URL", "content_click / outbound_click 點擊的目的地 URL"),
    ("page_lang", "Page Language", "事件發生的語言介面 zh-TW/en/ja/ko/es/fr"),
    ("seconds", "Time Milestone Seconds", "time_milestone 階段 30/60/180/600"),
    ("elapsed_ms", "Elapsed MS", "section 第一次進 viewport 距 page load 的毫秒"),
    ("depth_pct", "Scroll Depth Percent", "scroll_depth 階段 25/50/75/100（取代死掉的 pct）"),
]

# ── page-level events（404.astro page_404）────────────────────────────────
# 2026-05-29 instrumentation-audit 抓到：page_404 fire 5 param 但全沒註冊。
# page_lang 統一用 HOMEPAGE_DIMENSIONS 那個（404.astro 已從 page_language 改名對齊）。
# 注意：GA4 display_name 必須以字母開頭（不能 "404 ..."）。
PAGE_DIMENSIONS = [
    ("failed_path", "Failed Path 404", "page_404 命中的不存在路徑（先前 fetch-ga4 query 一直 try/except 吞掉）"),
    ("failed_url", "Failed URL 404", "page_404 完整 URL（含 query/hash）"),
    ("referrer", "Referrer 404", "從哪裡連到 404（內部斷鏈 vs 外部，direct = 直接輸入）"),
    ("had_suggestion", "Had Suggestion 404", "smart-404 是否找到鄰近文章建議 true/false"),
]

# ── converter events（2026-06-13 上線，terminology/converter.astro CONV-1）──
# param 名以 converter.astro track() 實際送的為準（SSOT 對齊用）。
# 餵 scripts/tools/converter-demand.py 的需求飛輪查詢。
CONVERTER_DIMENSIONS = [
    ("term_id", "Converter Term ID", "converter_term_lookup 被查的詞條 id（= YAML id，需求飛輪主訊號）"),
    ("direction", "Converter Direction", "converter_convert 轉換方向 cn2tw / tw2cn"),
    ("category", "Converter Category", "term_lookup 詞條分類 / example_click 範例分類 tech/life/..."),
    ("fork_type", "Converter Fork Type", "term_lookup 詞條分支類型 A-F"),
    ("to", "Converter Toggle Target", "converter_direction_toggle 切到的方向 cn2tw/tw2cn"),
]

# ── soundscape events（2026-07-18 /soundscape EVOLVE：21 錄音的播放量測）──
# param 名以 src/templates/soundscape.template.astro sound_play script 實際送的為準。
SOUNDSCAPE_DIMENSIONS = [
    ("sound_file", "Soundscape Sound File", "sound_play 播放的錄音檔名（/assets/sounds/ 下）"),
    ("sound_category", "Soundscape Category", "sound_play 錄音所屬分類 urban/mrt-soundscape/sacred/indigenous/nature/vanishing"),
]

DIMENSIONS = (
    SEARCH_DIMENSIONS
    + ENGAGEMENT_DIMENSIONS
    + PAGE_DIMENSIONS
    + CONVERTER_DIMENSIONS
    + SOUNDSCAPE_DIMENSIONS
)

# ── 廢棄維度（archive 而非刪除，GA4 archive 可重建）──────────────────────────
# pct: 2026-05-27 誤註冊。HomeEventTracker scroll_depth 實際 fire `depth_pct`，
# 沒有任何 gtag 送 `pct` → 此 dim 永遠 (not set)。2026-05-29 D+2 watch 抓到。
DEPRECATED_DIMENSIONS = ["pct"]


def fail(msg):
    print(f"❌ {msg}", file=sys.stderr)
    sys.exit(1)


def load_property_id():
    env_path = CREDENTIALS_DIR / ".env"
    for line in env_path.read_text().splitlines():
        if line.startswith("GA4_PROPERTY_ID="):
            return line.split("=", 1)[1].strip().strip('"').strip("'")
    fail("GA4_PROPERTY_ID not found")


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--dry-run", action="store_true")
    args = parser.parse_args()

    from google.analytics.admin_v1beta import AnalyticsAdminServiceClient
    from google.analytics.admin_v1beta.types import CustomDimension
    from google.oauth2 import service_account
    from google.api_core.exceptions import AlreadyExists, PermissionDenied

    sa_path = CREDENTIALS_DIR / "google-service-account.json"
    creds = service_account.Credentials.from_service_account_file(
        str(sa_path),
        scopes=["https://www.googleapis.com/auth/analytics.edit"],
    )
    client = AnalyticsAdminServiceClient(credentials=creds)
    property_id = load_property_id()
    parent = f"properties/{property_id}"

    print(f"📝 Registering {len(DIMENSIONS)} custom dimensions on {parent}")
    if args.dry_run:
        for p, name, desc in DIMENSIONS:
            print(f"  [dry-run] register {p} → {name}")
        for p in DEPRECATED_DIMENSIONS:
            print(f"  [dry-run] archive {p}")
        return

    # List existing (keep full objects so we can resolve names for archive)
    try:
        existing_objs = list(client.list_custom_dimensions(parent=parent))
    except PermissionDenied as e:
        fail(
            f"PermissionDenied: service account缺 Editor 角色\n"
            f"→ GA4 Admin → Property access management → "
            f"taiwan-md-reader@taiwan-md-sense.iam.gserviceaccount.com 升級為 Editor\n"
            f"詳細: {e}"
        )
    existing = {cd.parameter_name for cd in existing_objs}
    by_param = {cd.parameter_name: cd for cd in existing_objs}

    created, skipped = 0, 0
    for param_name, display_name, description in DIMENSIONS:
        if param_name in existing:
            print(f"  ⏭  {param_name} already exists")
            skipped += 1
            continue
        cd = CustomDimension(
            parameter_name=param_name,
            display_name=display_name,
            description=description,
            scope=CustomDimension.DimensionScope.EVENT,
        )
        try:
            result = client.create_custom_dimension(parent=parent, custom_dimension=cd)
            print(f"  ✅ {param_name} → {result.name}")
            created += 1
        except AlreadyExists:
            print(f"  ⏭  {param_name} (AlreadyExists race)")
            skipped += 1

    # Archive deprecated dims (reversible — GA4 archive can be undone by recreate)
    archived = 0
    for param_name in DEPRECATED_DIMENSIONS:
        cd = by_param.get(param_name)
        if not cd:
            print(f"  ⏭  {param_name} not present (already archived?)")
            continue
        try:
            client.archive_custom_dimension(name=cd.name)
            print(f"  🗄  archived {param_name} ({cd.name})")
            archived += 1
        except Exception as e:  # noqa: BLE001 — log + continue, archive 非關鍵路徑
            print(f"  ⚠️  archive {param_name} failed: {type(e).__name__}: {e}")

    print(f"\n✅ Done: {created} created, {skipped} skipped, {archived} archived")
    print("\n⏱  資料可用時間：新事件開始帶維度，歷史無法回補。")
    print("   sanity query: scripts/tools/fetch-ga4.py 或 reports/scratch d2-watch query.")


if __name__ == "__main__":
    main()
