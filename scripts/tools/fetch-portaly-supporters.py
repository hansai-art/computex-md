#!/usr/bin/env python3
"""
fetch-portaly-supporters.py — Portaly 贊助信件 parser + merger

角色: SSOT 維護工具，把 Gmail 裡 Portaly 贊助通知信
      解析成 data/supporters/transactions.json（Layer 1 流水帳）的 entry。

資料流:
    Gmail (Portaly 通知信 → 本專案收件 inbox)
      ↓  Heartbeat Beat 1 §0c（AI 透過 Gmail MCP 抓近 N 天未處理信件）
      ↓  餵 JSON array 進本 script（stdin）
    本 script 解析 + dedupe + append
      ↓
    data/supporters/transactions.json (SSOT)
      ↓  npm run prebuild
    public/api/dashboard-supporters.json + about-supporters.json (derived)

用法:
    # 解析 + merge（預設：stdin 讀 JSON array，merge 到 transactions.json）
    cat new-emails.json | python3 scripts/tools/fetch-portaly-supporters.py

    # 只解析不寫檔（dry-run 檢查）
    cat new-emails.json | python3 scripts/tools/fetch-portaly-supporters.py --dry-run

    # 只輸出現有 transactions 的摘要
    python3 scripts/tools/fetch-portaly-supporters.py --summary

Stdin 格式（Gmail MCP get_thread 回傳 plaintextBody 之後的最小封包）:
    [
      {
        "gmail_message_id": "19da8d20d8a6a234",
        "date": "2026-04-20T02:57:06Z",
        "subject": "匿名 支持了您 NT$2000 元",
        "plaintextBody": "... 整封信內容 ..."
      },
      ...
    ]

憑證 / 隱私鐵律:
    - 本 script **不碰** Gmail OAuth token / service account
    - 信件內容由 caller（Gmail MCP 或觀察者手動）預先取得
    - 解析後**絕不**寫入 email address / payment method / credit card info
    - 只寫：支持編號（stable key）/ 金額 / 名稱 / 留言 / 類型 / 時間戳
    - gmail_message_id 是 audit trail（非私密；只能用來在你自己的 Gmail 找原信）

贊助者 email 不會被寫進任何檔案的結構性保證:
    1. Portaly 通知信 plaintextBody 本身就不包含贊助者 email 地址
       （Portaly 作為金流中介，不暴露 donor email 給收款方）
    2. 本 script 的 FIELD_PATTERNS 只宣告 4 個正規式（id/amount/name/message），
       沒有 email 的抓取路徑；plaintextBody 只在記憶體使用，不寫任何檔案
    3. parse_email() 回傳 allowlist dict，任何未列於 schema 的欄位會被丟棄
    4. 若未來 Portaly 通知信格式改變開始包含 email，**不加 email regex 就永遠不會被抓**

來源: 2026-04-20 排程心跳 α 延伸 — CheYu 指派 Portaly pipeline
v1.0 | 2026-04-20
"""
from __future__ import annotations

import argparse
import json
import re
import sys
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

PROJECT_ROOT = Path(__file__).resolve().parent.parent.parent
TRANSACTIONS_PATH = PROJECT_ROOT / "data" / "supporters" / "transactions.json"
SCHEMA_VERSION = 1


# ────────────────────────────────────────────────────────────────────────
# Parsing
# ────────────────────────────────────────────────────────────────────────

# 兩種信件 body pattern：一次性支持 / 每月定額贊助
# 欄位順序固定（Portaly template 產出），但為防範調整順序，用 per-field regex 抓
FIELD_PATTERNS = {
    # 「支持金額：NT$ 2000」或「贊助方案：每月定額 NT$500」
    "amount": re.compile(
        r"(?:支持金額|贊助方案)[：:]\s*(?:每月定額\s*)?NT\$\s*([\d,]+)"
    ),
    # 「支持者名稱：匿名」或「贊助者名稱：沈宗杰」
    "name": re.compile(r"(?:支持者|贊助者)名稱[：:]\s*(.+?)(?:\r?\n|$)"),
    # 「支持者留言：...」或「贊助者留言：...」
    "message": re.compile(r"(?:支持者|贊助者)留言[：:]\s*(.+?)(?:\r?\n|$)"),
    # 「支持編號：xxx」或「贊助編號：xxx」
    "id": re.compile(r"(?:支持|贊助)編號[：:]\s*(\S+)"),
}

# 類型 detection（標題或 body 出現「每月定額」即為 monthly）
MONTHLY_PATTERN = re.compile(r"每月定額")


def parse_email(raw: dict[str, Any]) -> dict[str, Any] | None:
    """Parse one Portaly email envelope (from Gmail MCP) into a transaction entry.

    Returns None if this is not a Portaly sponsorship email (e.g. newsletter /
    subscription invoice). Caller should filter those out at source, but we
    double-check here.
    """
    body = raw.get("plaintextBody") or raw.get("body") or ""
    subject = raw.get("subject") or ""
    gmail_id = raw.get("gmail_message_id") or raw.get("id") or ""
    date_iso = raw.get("date") or ""

    # 必備欄位都要抓到才算 sponsorship
    fields = {}
    for key, pat in FIELD_PATTERNS.items():
        m = pat.search(body)
        if not m:
            return None
        fields[key] = m.group(1).strip()

    amount_raw = fields["amount"].replace(",", "")
    try:
        amount = int(amount_raw)
    except ValueError:
        return None

    name = fields["name"]
    anonymous = name == "匿名"
    is_monthly = bool(MONTHLY_PATTERN.search(body) or MONTHLY_PATTERN.search(subject))

    # Normalize date to ISO Z (UTC) + local date string
    try:
        dt = datetime.fromisoformat(date_iso.replace("Z", "+00:00"))
        if dt.tzinfo is None:
            dt = dt.replace(tzinfo=timezone.utc)
        timestamp_z = dt.astimezone(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")
        date_str = dt.astimezone(timezone.utc).strftime("%Y-%m-%d")
    except ValueError:
        timestamp_z = date_iso
        date_str = (date_iso or "")[:10]

    return {
        "id": fields["id"],
        "source": "portaly",
        "timestamp": timestamp_z,
        "date": date_str,
        "name": name,
        "anonymous": anonymous,
        "amount": amount,
        "currency": "TWD",
        "type": "monthly" if is_monthly else "one-time",
        "message": fields["message"],
        "subscription_id": None,  # Portaly 目前信件沒提供，預留欄位
        "status": "received",
        "gmail_message_id": gmail_id,
    }


# ────────────────────────────────────────────────────────────────────────
# Merge
# ────────────────────────────────────────────────────────────────────────


def load_existing() -> dict[str, Any]:
    if not TRANSACTIONS_PATH.exists():
        return {
            "schema_version": SCHEMA_VERSION,
            "last_fetched": None,
            "transactions": [],
        }
    return json.loads(TRANSACTIONS_PATH.read_text(encoding="utf-8"))


def merge(existing: dict[str, Any], new_items: list[dict[str, Any]]) -> tuple[dict[str, Any], int]:
    """Append new transactions to existing, dedupe by `id`. Returns (new_doc, added_count)."""
    seen = {tx["id"] for tx in existing.get("transactions", [])}
    added = 0
    for item in new_items:
        if item["id"] in seen:
            continue
        existing["transactions"].append(item)
        seen.add(item["id"])
        added += 1

    # Sort ASC by timestamp (oldest first; timeline reads chronologically)
    existing["transactions"].sort(key=lambda t: t.get("timestamp", ""))
    existing["schema_version"] = SCHEMA_VERSION
    existing["last_fetched"] = datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")
    return existing, added


def write_transactions(doc: dict[str, Any]) -> None:
    TRANSACTIONS_PATH.parent.mkdir(parents=True, exist_ok=True)
    TRANSACTIONS_PATH.write_text(
        json.dumps(doc, ensure_ascii=False, indent=2) + "\n",
        encoding="utf-8",
    )


# ────────────────────────────────────────────────────────────────────────
# Summary (for --summary mode and post-merge output)
# ────────────────────────────────────────────────────────────────────────


def summarize(doc: dict[str, Any]) -> str:
    txs = doc.get("transactions", [])
    total = sum(t["amount"] for t in txs if t.get("status") == "received")
    monthly_count = sum(1 for t in txs if t.get("type") == "monthly")
    one_time_count = sum(1 for t in txs if t.get("type") == "one-time")
    anon_count = sum(1 for t in txs if t.get("anonymous"))
    lines = [
        f"📊 Supporters summary",
        f"   Transactions: {len(txs)} ({one_time_count} one-time, {monthly_count} monthly)",
        f"   Total received: NT${total:,}",
        f"   Anonymous: {anon_count} / {len(txs)}",
        f"   Last fetched: {doc.get('last_fetched', 'never')}",
    ]
    return "\n".join(lines)


# ────────────────────────────────────────────────────────────────────────
# CLI
# ────────────────────────────────────────────────────────────────────────


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--dry-run", action="store_true", help="解析 + dedupe 但不寫檔")
    ap.add_argument("--summary", action="store_true", help="只印現有 transactions 摘要")
    args = ap.parse_args()

    if args.summary:
        doc = load_existing()
        print(summarize(doc))
        return 0

    # Read stdin JSON array
    try:
        raw_input = sys.stdin.read()
        if not raw_input.strip():
            print("⚠️  stdin empty — nothing to parse. (use --summary to inspect)", file=sys.stderr)
            return 1
        emails = json.loads(raw_input)
    except json.JSONDecodeError as e:
        print(f"❌ stdin is not valid JSON: {e}", file=sys.stderr)
        return 2

    if not isinstance(emails, list):
        print("❌ stdin JSON must be an array", file=sys.stderr)
        return 2

    parsed = []
    skipped = 0
    for raw in emails:
        tx = parse_email(raw)
        if tx is None:
            skipped += 1
            continue
        parsed.append(tx)

    print(f"✅ Parsed {len(parsed)} sponsorship emails (skipped {skipped} non-matches)", file=sys.stderr)

    existing = load_existing()
    merged, added = merge(existing, parsed)

    if args.dry_run:
        print(f"🔍 dry-run: {added} new / {len(merged['transactions'])} total", file=sys.stderr)
        print(summarize(merged))
        return 0

    write_transactions(merged)
    print(f"💾 Wrote {TRANSACTIONS_PATH.relative_to(PROJECT_ROOT)}: {added} new / {len(merged['transactions'])} total", file=sys.stderr)
    print(summarize(merged))
    return 0


if __name__ == "__main__":
    sys.exit(main())
