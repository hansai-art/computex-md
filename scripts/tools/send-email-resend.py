#!/usr/bin/env python3
"""
send-email-resend.py — Resend API 寄信 helper

從 ~/.config/taiwan-md/credentials/resend.key 讀 API key（永遠不從 stdin 接、不複述、
不寫進 log），把 markdown 檔轉成 HTML email 寄出。

Usage（單收件人，向後相容）:
    python3 scripts/tools/send-email-resend.py \\
        --to <email> --subject <text> --markdown <path>

Usage（BCC 廣播給共生圈，v2）:
    python3 scripts/tools/send-email-resend.py \\
        --to <email> --subject <text> --markdown <path> \\
        --bcc-from-json ~/.config/taiwan-md/weekly-report/recipients-latest.json \\
        --reply-to <email> --audience-footer

Env override:
    RESEND_API_KEY  (取代讀檔；CI/Routine 用)
    RESEND_FROM     (取代預設 onboarding@resend.dev)

Exit code: 0 = sent（或 --dry-run 成功渲染），非 0 = fail（含 Resend response body 寫 stderr）
"""

import argparse
import json
import os
import posixpath
import re
import sys
import urllib.request
import urllib.error
from datetime import datetime, timedelta, timezone
from pathlib import Path

DEFAULT_FROM = 'COMPUTEX.md <onboarding@resend.dev>'
KEY_PATH = Path.home() / ".config/taiwan-md/credentials/resend.key"
RESEND_ENDPOINT = "https://api.resend.com/emails"

# 連結改寫預設值（見 --link-base-repo / --site-base / --md-dir）
DEFAULT_LINK_BASE_REPO = "https://github.com/frank890417/taiwan-md/blob/main"
DEFAULT_SITE_BASE = "https://computex-md.pages.dev"
DEFAULT_MD_DIR = "reports/weekly"

# Resend 單次 API call 的 BCC 上限（保守值，非官方硬限制）
MAX_BCC_PER_CHUNK = 40
# --bcc-from-json 的新鮮度窗口
BCC_FRESHNESS_HOURS = 48

# --audience-footer 附加的固定 markdown 區塊（一字不改，見 WEEKLY-REPORT-PIPELINE §5）
AUDIENCE_FOOTER_MD = (
    "\n---\n\n"
    "_你會收到這封信，是因為過去三個月你在 GitHub 上參與過 COMPUTEX.md"
    "（commit / PR / issue / 留言）。謝謝你，這個計畫因為你們而活著。_\n\n"
    "_不想再收到週報？直接回覆這封信說一聲，或開 PR 把自己的 GitHub 帳號加進"
    " [weekly-report-optout.json]"
    "(https://github.com/frank890417/taiwan-md/blob/main/docs/community/weekly-report-optout.json)。_\n\n"
    "_🧬 COMPUTEX.md · [computex.md](https://computex-md.pages.dev) ·"
    " [GitHub](https://github.com/frank890417/taiwan-md)_\n"
)


def load_key() -> str:
    env = os.environ.get("RESEND_API_KEY", "").strip()
    if env:
        return env
    if not KEY_PATH.exists():
        print(f"❌ Resend key not found: {KEY_PATH}", file=sys.stderr)
        print("   Set RESEND_API_KEY env or place key at the path above (chmod 600).", file=sys.stderr)
        sys.exit(2)
    if KEY_PATH.stat().st_mode & 0o077:
        print(f"⚠️  {KEY_PATH} 權限太寬 — 建議 chmod 600", file=sys.stderr)
    return KEY_PATH.read_text().strip()


# ─────────────────────────────────────────────────────────
# 連結改寫（相對路徑 → repo blob URL / 站內路徑 → 網站絕對網址）
# ─────────────────────────────────────────────────────────


def rewrite_href(href: str, link_base_repo: str, site_base: str, md_dir: str) -> str:
    """把一個 markdown 連結的 href 改寫成信箱裡點得開的絕對網址。

    - http(s):// / mailto: / # 開頭 → 原樣不動
    - 開頭是 / → 視為站內 site-root path，接到 site_base 後面
    - 其他（repo 相對路徑，例如 ../evolution-roadmap-2026-07-10.md）→
      以 md_dir 為基準（郵寄的 markdown 檔實際所在目錄）解出相對路徑，
      再接到 link_base_repo 後面變成 GitHub blob URL。
    """
    if href.startswith(("http://", "https://", "mailto:", "#")):
        return href
    if href.startswith("/"):
        return f"{site_base}{href}"

    joined = posixpath.normpath(posixpath.join(md_dir, href))
    parts = [p for p in joined.split("/") if p not in ("", ".")]
    # 保守處理：正規化後如果還往 repo root 之上跑，直接砍掉逃逸的 ../ 片段
    while parts and parts[0] == "..":
        parts.pop(0)
    normalized = "/".join(parts)
    return f"{link_base_repo}/{normalized}"


# 保護區塊：已經是 <a ...>...</a> 或 <code ...>...</code> 的內容不再二次 autolink
_PROTECTED_HTML_RE = re.compile(
    r"(<a\b[^>]*>.*?</a>|<code\b[^>]*>.*?</code>)", re.IGNORECASE | re.DOTALL
)
_BARE_URL_RE = re.compile(r'https?://[^\s<>"]+')
# 裸網址尾端常見標點：不算網址的一部分（中英文標點都含）
_TRAILING_PUNCT = "),.;:。，、）」』"


def _strip_trailing_punct(url: str) -> tuple[str, str]:
    trailing_chars: list[str] = []
    while url and url[-1] in _TRAILING_PUNCT:
        trailing_chars.append(url[-1])
        url = url[:-1]
    return url, "".join(reversed(trailing_chars))


def _autolink_one(m: "re.Match[str]") -> str:
    raw = m.group(0)
    url, trailing = _strip_trailing_punct(raw)
    if not url:
        return raw
    return f'<a href="{url}" style="color:#2563eb;text-decoration:underline">{url}</a>{trailing}'


def autolink_bare_urls(s: str) -> str:
    """把裸網址包成 <a>，跳過已經在 <a>/<code> 裡面的片段（避免雙重包裝）。"""
    parts = _PROTECTED_HTML_RE.split(s)
    for i in range(0, len(parts), 2):  # 偶數 index = 未受保護的一般文字
        parts[i] = _BARE_URL_RE.sub(_autolink_one, parts[i])
    return "".join(parts)


# ─────────────────────────────────────────────────────────
# Minimal markdown → HTML（依賴零，足夠 email 排版）
# ─────────────────────────────────────────────────────────


def md_to_html(
    md: str,
    *,
    link_base_repo: str = DEFAULT_LINK_BASE_REPO,
    site_base: str = DEFAULT_SITE_BASE,
    md_dir: str = DEFAULT_MD_DIR,
) -> str:
    """Tiny converter: heading / bold / italic / list / link / code / hr / paragraph."""
    out: list[str] = []
    in_ul = False
    in_table = False
    table_rows: list[str] = []

    def flush_table():
        nonlocal in_table, table_rows
        if not table_rows:
            return
        rows = table_rows
        # First row = header, second row = separator (skip), rest = body
        head = rows[0]
        body = rows[2:] if len(rows) >= 2 else []
        out.append('<table style="border-collapse:collapse;margin:8px 0">')
        cells = [c.strip() for c in head.strip("|").split("|")]
        out.append("<thead><tr>")
        for c in cells:
            out.append(
                f'<th style="border:1px solid #ddd;padding:4px 8px;background:#f7f7f7;text-align:left">{inline(c)}</th>'
            )
        out.append("</tr></thead><tbody>")
        for r in body:
            cells = [c.strip() for c in r.strip("|").split("|")]
            out.append("<tr>")
            for c in cells:
                out.append(
                    f'<td style="border:1px solid #ddd;padding:4px 8px">{inline(c)}</td>'
                )
            out.append("</tr>")
        out.append("</tbody></table>")
        in_table = False
        table_rows = []

    def inline(s: str) -> str:
        # escape first
        s = s.replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")
        # **bold**
        s = re.sub(r"\*\*([^*]+)\*\*", r"<strong>\1</strong>", s)
        # *italic*
        s = re.sub(r"(?<!\*)\*([^*\n]+)\*(?!\*)", r"<em>\1</em>", s)
        # `code`
        s = re.sub(
            r"`([^`]+)`",
            r'<code style="background:#f3f3f3;padding:1px 4px;border-radius:3px;font-family:monospace">\1</code>',
            s,
        )

        # [text](url) — href 先過 rewrite_href 再組 <a>
        def _link_sub(m: "re.Match[str]") -> str:
            text, href = m.group(1), m.group(2)
            href = rewrite_href(href, link_base_repo, site_base, md_dir)
            return f'<a href="{href}" style="color:#2563eb;text-decoration:underline">{text}</a>'

        s = re.sub(r"\[([^\]]+)\]\(([^)]+)\)", _link_sub, s)

        # 裸網址自動超連結（略過已經在 <a>/<code> 裡的片段）
        s = autolink_bare_urls(s)
        return s

    for line in md.split("\n"):
        # Tables
        if line.startswith("|") and line.endswith("|"):
            if not in_table:
                in_table = True
                table_rows = []
            table_rows.append(line)
            continue
        if in_table:
            flush_table()

        if line.startswith("# "):
            if in_ul:
                out.append("</ul>")
                in_ul = False
            out.append(f"<h1 style=\"font-size:22px;margin:16px 0 8px\">{inline(line[2:])}</h1>")
        elif line.startswith("## "):
            if in_ul:
                out.append("</ul>")
                in_ul = False
            out.append(f"<h2 style=\"font-size:18px;margin:14px 0 6px;color:#111\">{inline(line[3:])}</h2>")
        elif line.startswith("### "):
            if in_ul:
                out.append("</ul>")
                in_ul = False
            out.append(f"<h3 style=\"font-size:15px;margin:10px 0 4px;color:#333\">{inline(line[4:])}</h3>")
        elif line.startswith("- "):
            if not in_ul:
                out.append("<ul style=\"margin:6px 0;padding-left:22px\">")
                in_ul = True
            out.append(f"<li style=\"margin:2px 0\">{inline(line[2:])}</li>")
        elif line.strip() == "---":
            if in_ul:
                out.append("</ul>")
                in_ul = False
            out.append("<hr style=\"border:none;border-top:1px solid #ddd;margin:14px 0\">")
        elif line.strip() == "":
            if in_ul:
                out.append("</ul>")
                in_ul = False
            # blank → paragraph break
        else:
            if in_ul:
                out.append("</ul>")
                in_ul = False
            stripped = line.strip()
            # italic-only line (e.g., footer _v1.0 ..._)
            if stripped.startswith("_") and stripped.endswith("_") and stripped.count("_") >= 2:
                out.append(
                    f"<p style=\"color:#666;font-size:12px;margin:8px 0\"><em>{inline(stripped[1:-1])}</em></p>"
                )
            else:
                out.append(f"<p style=\"margin:6px 0;line-height:1.6\">{inline(line)}</p>")
    if in_ul:
        out.append("</ul>")
    if in_table:
        flush_table()
    body = "\n".join(out)
    wrapped = (
        '<div style="font-family:-apple-system,BlinkMacSystemFont,\'Noto Sans TC\',sans-serif;'
        "max-width:720px;margin:0 auto;padding:16px;color:#222\">"
        f"{body}"
        "</div>"
    )
    return wrapped


# ─────────────────────────────────────────────────────────
# BCC 名單解析（--bcc / --bcc-from-json）
# ─────────────────────────────────────────────────────────


def _parse_iso8601(ts: str) -> datetime:
    ts = ts.strip()
    if ts.endswith("Z"):
        ts = ts[:-1] + "+00:00"
    dt = datetime.fromisoformat(ts)
    if dt.tzinfo is None:
        dt = dt.replace(tzinfo=timezone.utc)
    return dt


def load_bcc_from_json(path_str: str, allow_empty_bcc: bool, allow_stale: bool) -> list[str]:
    """讀 weekly-report-recipients.py 產出的 JSON，回傳乾淨的 bcc email list。

    Fail-loud（exit 2）：檔案不存在 / 不是合法 JSON / bcc 缺漏或為空
    （除非 --allow-empty-bcc）/ generated_at 超過 48 小時（除非 --allow-stale）。
    """
    path = Path(path_str).expanduser()
    if not path.exists():
        print(f"❌ --bcc-from-json file not found: {path}", file=sys.stderr)
        sys.exit(2)
    try:
        data = json.loads(path.read_text())
    except (json.JSONDecodeError, UnicodeDecodeError, OSError) as e:
        print(f"❌ --bcc-from-json file unreadable / invalid JSON: {path} ({e})", file=sys.stderr)
        sys.exit(2)

    raw_bcc = data.get("bcc")
    if raw_bcc is None or not isinstance(raw_bcc, list):
        raw_bcc = []
    bcc = [e.strip() for e in raw_bcc if isinstance(e, str) and e.strip()]

    if not bcc:
        if allow_empty_bcc:
            print(
                f"⚠️  --bcc-from-json: 'bcc' 是空的或缺漏 ({path}) — 因為有 --allow-empty-bcc 所以繼續（0 recipients）",
                file=sys.stderr,
            )
            return []
        print(f"❌ --bcc-from-json: 檔案沒有 'bcc' 陣列或是空的: {path}", file=sys.stderr)
        print("   加 --allow-empty-bcc 可以硬繼續。", file=sys.stderr)
        sys.exit(2)

    generated_at = data.get("generated_at")
    stale = True
    age_desc = "generated_at 缺漏"
    if generated_at:
        try:
            gen_dt = _parse_iso8601(str(generated_at))
            age = datetime.now(timezone.utc) - gen_dt
            age_desc = f"generated_at={generated_at} age={age}"
            stale = age > timedelta(hours=BCC_FRESHNESS_HOURS)
        except ValueError:
            stale = True
            age_desc = f"generated_at 無法解析: {generated_at!r}"

    if stale:
        if allow_stale:
            print(
                f"⚠️  --bcc-from-json 名單看起來過期或無法驗證新鮮度（{age_desc}）— 因為有 --allow-stale 所以繼續",
                file=sys.stderr,
            )
        else:
            print(
                f"❌ --bcc-from-json 名單過期或無法驗證新鮮度（{age_desc}，檔案={path}）。",
                file=sys.stderr,
            )
            print(
                "   請先重跑 weekly-report-recipients.py 更新名單，或加 --allow-stale 硬寄。",
                file=sys.stderr,
            )
            sys.exit(2)

    return bcc


def resolve_bcc(args: argparse.Namespace) -> list[str]:
    bcc_list: list[str] = []
    if args.bcc:
        bcc_list.extend(e.strip() for e in args.bcc.split(",") if e.strip())
    if args.bcc_from_json:
        bcc_list.extend(
            load_bcc_from_json(args.bcc_from_json, args.allow_empty_bcc, args.allow_stale)
        )
    # dedupe，保留原順序
    seen: set[str] = set()
    deduped: list[str] = []
    for e in bcc_list:
        if e not in seen:
            seen.add(e)
            deduped.append(e)
    return deduped


# ─────────────────────────────────────────────────────────
# Resend POST
# ─────────────────────────────────────────────────────────


def send(
    api_key: str,
    to: str,
    from_: str,
    subject: str,
    html: str,
    text: str,
    reply_to: str | None = None,
    bcc: list[str] | None = None,
) -> dict:
    payload = {
        "from": from_,
        "to": [to],
        "subject": subject,
        "html": html,
        "text": text,
    }
    if bcc:
        payload["bcc"] = bcc
    if reply_to:
        payload["reply_to"] = reply_to
    req = urllib.request.Request(
        RESEND_ENDPOINT,
        data=json.dumps(payload).encode("utf-8"),
        method="POST",
        headers={
            "Authorization": f"Bearer {api_key}",
            "Content-Type": "application/json",
            # Resend's Cloudflare edge blocks default Python-urllib UA (returns 1010).
            # Identify cleanly so the proxy lets us through.
            "User-Agent": "taiwan-md-weekly-report/1.0 (+https://computex-md.pages.dev)",
            "Accept": "application/json",
        },
    )
    try:
        with urllib.request.urlopen(req, timeout=30) as resp:
            return {"status": resp.status, "body": json.loads(resp.read().decode())}
    except urllib.error.HTTPError as e:
        body = e.read().decode("utf-8", errors="replace")
        return {"status": e.code, "body": body, "error": str(e)}
    except Exception as e:
        return {"status": -1, "body": "", "error": str(e)}


def _chunk_list(items: list[str], size: int):
    for i in range(0, len(items), size):
        yield items[i : i + size]


def send_broadcast(
    api_key: str,
    to: str,
    from_: str,
    subject: str,
    html: str,
    text: str,
    reply_to: str | None,
    bcc_list: list[str],
) -> tuple[list[dict], bool]:
    """依 MAX_BCC_PER_CHUNK 分批寄送。回傳 (每批 result, 是否有任何一批失敗)。"""
    chunks = list(_chunk_list(bcc_list, MAX_BCC_PER_CHUNK)) if bcc_list else [[]]
    total = len(chunks)
    results: list[dict] = []
    any_failed = False
    for idx, chunk in enumerate(chunks, start=1):
        if idx > 1:
            print(
                f"[send-email] ⚠️  chunk {idx}/{total}: Resend 沒有純 bcc 寄送模式，"
                f"這批會重複寄一封給主收件人 {to!r}（預期內的重複遞送）",
                file=sys.stderr,
            )
        result = send(api_key, to, from_, subject, html, text, reply_to=reply_to, bcc=chunk)
        status = result.get("status")
        body = result.get("body")
        msg_id = body.get("id") if isinstance(body, dict) else None
        print(f"[send-email] chunk {idx}/{total} status={status} id={msg_id}", file=sys.stderr)
        if status not in (200, 201, 202):
            any_failed = True
            print(f"[send-email] chunk {idx}/{total} FAILED response: {body}", file=sys.stderr)
        results.append(result)
    return results, any_failed


# ─────────────────────────────────────────────────────────
# CLI
# ─────────────────────────────────────────────────────────


def main():
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--to", required=True)
    ap.add_argument("--subject", required=True)
    ap.add_argument("--markdown", required=True, help="Path to markdown file")
    ap.add_argument("--from", dest="from_", default=os.environ.get("RESEND_FROM", DEFAULT_FROM))
    ap.add_argument("--bcc", help="Comma-separated BCC recipients, e.g. a@x.com,b@y.com")
    ap.add_argument(
        "--bcc-from-json",
        help="Path to recipients JSON from weekly-report-recipients.py "
        "(uses its top-level 'bcc' array; ~ expanded)",
    )
    ap.add_argument(
        "--allow-empty-bcc",
        action="store_true",
        help="Don't fail if --bcc-from-json has no/empty 'bcc' key",
    )
    ap.add_argument(
        "--allow-stale",
        action="store_true",
        help="Don't fail if --bcc-from-json's generated_at is older than 48h",
    )
    ap.add_argument("--reply-to", help="Adds reply_to to the Resend payload")
    ap.add_argument(
        "--audience-footer",
        action="store_true",
        help="Append the standard '為什麼收到這封信 + 怎麼退訂' footer before md→HTML conversion",
    )
    ap.add_argument(
        "--link-base-repo",
        default=DEFAULT_LINK_BASE_REPO,
        help=f"Base URL for rewriting relative repo links (default: {DEFAULT_LINK_BASE_REPO})",
    )
    ap.add_argument(
        "--site-base",
        default=DEFAULT_SITE_BASE,
        help=f"Base URL for rewriting site-root '/...' links (default: {DEFAULT_SITE_BASE})",
    )
    ap.add_argument(
        "--md-dir",
        default=DEFAULT_MD_DIR,
        help="Repo-relative dir the emailed markdown lives in, used as the base "
        f"for resolving relative links (default: {DEFAULT_MD_DIR})",
    )
    ap.add_argument(
        "--dry-run",
        metavar="OUT.html",
        default=None,
        help="Render the final HTML to OUT.html and print a payload summary; "
        "exit 0 WITHOUT calling the Resend API",
    )
    ap.add_argument(
        "--web-url",
        default=None,
        help="Web edition URL of this email's content; inserted as a "
        "'🌐 在網頁上讀這份週報' line at the top of the email "
        "(weekly report → https://computex-md.pages.dev/semiont/weekly/YYYY-MM-DD)",
    )
    args = ap.parse_args()

    md_path = Path(args.markdown)
    if not md_path.exists():
        print(f"❌ markdown file not found: {md_path}", file=sys.stderr)
        sys.exit(2)
    md = md_path.read_text()

    if args.web_url:
        # 轉換器沒有 blockquote 分支，用獨立粗體段落 + 分隔線
        md = f"**🌐 [在網頁上讀這份週報]({args.web_url})**\n\n---\n\n" + md

    if args.audience_footer:
        md = md.rstrip("\n") + "\n" + AUDIENCE_FOOTER_MD

    bcc_list = resolve_bcc(args)

    html = md_to_html(
        md,
        link_base_repo=args.link_base_repo,
        site_base=args.site_base,
        md_dir=args.md_dir,
    )

    print(
        f"[send-email] to={args.to} subject={args.subject!r} from={args.from_!r} "
        f"reply_to={args.reply_to!r} bcc={len(bcc_list)} recipients",
        file=sys.stderr,
    )

    if args.dry_run:
        out_path = Path(args.dry_run)
        html_bytes = len(html.encode("utf-8"))
        out_path.write_text(html, encoding="utf-8")
        print(
            f"[send-email] DRY RUN — no Resend API call made; "
            f"wrote html_bytes={html_bytes} to {out_path}",
            file=sys.stderr,
        )
        sys.exit(0)

    api_key = load_key()
    _results, any_failed = send_broadcast(
        api_key, args.to, args.from_, args.subject, html, md, args.reply_to, bcc_list
    )
    if any_failed:
        sys.exit(1)


if __name__ == "__main__":
    main()
