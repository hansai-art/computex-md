#!/usr/bin/env python3
"""submit-sitemap-sc.py — 向 Search Console 重新提交 sitemap（讓新 URL 第一時間被抓）。

背景（2026-07-17）：slug 統一改名 91 檔 + hreflang 修復後，最快讓 Google
重抓的合法路徑就是 SC sitemaps.submit（sitemap ping endpoint 2023 已棄用）。
Deploy 後跑一次；日常不需要（Google 會按 lastmod 自己回來）。

用法：
    python3 scripts/tools/submit-sitemap-sc.py            # 提交 sitemap-index.xml
    python3 scripts/tools/submit-sitemap-sc.py --list     # 列出已提交的 sitemap 與狀態

憑證：與 fetch-search-console.py 同一把 service account（~/.config/taiwan-md/
credentials/），但提交需要完整 webmasters scope——service account 在 SC 資源
上必須是「完整」以上權限（readonly 使用者會拿 403，工具會印出開通指引）。
"""
import sys
from pathlib import Path

VENV_SITE = Path.home() / ".config/taiwan-md/venv/lib"
for p in VENV_SITE.glob("python*/site-packages"):
    sys.path.insert(0, str(p))

from google.oauth2 import service_account  # noqa: E402
from googleapiclient.discovery import build  # noqa: E402
from googleapiclient.errors import HttpError  # noqa: E402

CRED_DIR = Path.home() / ".config/taiwan-md/credentials"
def _site_from_env():
    env = CRED_DIR / ".env"
    if env.exists():
        for line in env.read_text().splitlines():
            if line.startswith("SC_SITE_URL="):
                return line.split("=", 1)[1].strip().strip("'\"")
    return "https://computex-md.pages.dev/"

SITE = _site_from_env()  # 與 fetch-search-console.py 同源（.env SC_SITE_URL）
SITEMAP = "https://computex-md.pages.dev/sitemap-index.xml"


def find_key():
    # 與 fetch-search-console.py 同一把（唯一合法位置）
    key = CRED_DIR / "google-service-account.json"
    return key if key.exists() else None


def main():
    key = find_key()
    if not key:
        print(f"❌ {CRED_DIR} 找不到 service account JSON")
        return 1
    creds = service_account.Credentials.from_service_account_file(
        str(key), scopes=["https://www.googleapis.com/auth/webmasters"])
    svc = build("searchconsole", "v1", credentials=creds, cache_discovery=False)

    if "--list" in sys.argv:
        try:
            resp = svc.sitemaps().list(siteUrl=SITE).execute()
        except HttpError as e:
            if e.resp.status == 403:
                print("❌ 403 — Sitemaps API 需要 SC「完整」權限（現為受限）。")
                print("   開通：SC → 設定 → 使用者和權限 → service account → 完整")
                return 1
            raise
        for sm in resp.get("sitemap", []):
            print(f"  {sm['path']}")
            print(f"    submitted={sm.get('lastSubmitted')} "
                  f"downloaded={sm.get('lastDownloaded')} "
                  f"errors={sm.get('errors')} warnings={sm.get('warnings')}")
        return 0

    try:
        svc.sitemaps().submit(siteUrl=SITE, feedpath=SITEMAP).execute()
        print(f"✅ 已向 SC 提交 {SITEMAP}（property {SITE}）")
        print("   Google 會排程重抓；狀態用 --list 查。")
        return 0
    except HttpError as e:
        if e.resp.status == 403:
            print("❌ 403 — service account 在 SC 上只有 readonly 權限。")
            print("   開通：SC → 設定 → 使用者和權限 → 該 service account email")
            print("   權限從「受限」改「完整」，然後重跑本工具。")
        else:
            print(f"❌ {e}")
        return 1


if __name__ == "__main__":
    sys.exit(main())
