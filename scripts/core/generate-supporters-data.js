#!/usr/bin/env node
/**
 * generate-supporters-data.js
 *
 * 產出兩個派生 API 檔：
 *   - public/api/dashboard-supporters.json — Dashboard 贊助時間軸視圖（含金額）
 *   - public/api/about-supporters.json     — About 個人支持者視圖（按人 group，不含金額）
 *
 * SSOT:
 *   data/supporters/transactions.json（由 fetch-portaly-supporters.py 維護）
 *
 * 為什麼存在:
 *   - 跟 knowledge/ vs src/content/ 同構 — 永遠只改 SSOT，derived 由 prebuild 重算
 *   - About / Dashboard 兩個 consumer 的資料形狀需求不同，各自派生專屬 shape
 *   - 新來源（GitHub Sponsors / Ko-fi）加進 transactions 後，無需改 UI 或消費端
 *
 * Privacy 邊界（硬規則）:
 *   - dashboard-supporters.json: 不含 message / name（只有金額 / 時間 / 類型 / anonymous 旗標）
 *   - about-supporters.json:     不含 amount（只有 display_name / message / anonymous / type）
 *   - 兩個派生都絕不含 gmail_message_id / email / subscription_id
 *
 * 聚合規則:
 *   - 實名 group by name（跨筆合併 messages，顯示最新）
 *   - 匿名一次性:  每筆獨立 card（不合併）
 *   - 匿名定額:    暫不合併（等 Portaly 提供 subscription_id 再 backfill）
 *
 * Tier（About 顯示用，v1 option C — 2026-04-20）:
 *   - 🌱 sprout:  < 1,000 TWD 累計
 *   - 🌿 grove:   1,000–4,999 TWD
 *   - 🌳 canopy:  5,000+ TWD
 *   閾值寫在 TIER_CONFIG（下方），日後好調。累計金額達到門檻即升 tier；
 *   每月定額隨時間自然升 tier（= 符合 MANIFESTO §關係創造存在的持續性優先）。
 *
 * 執行時機:
 *   - npm run prebuild（加到 package.json scripts）
 *
 * v1.0 | 2026-04-20
 */

import fs from 'node:fs';
import path from 'node:path';
import { fileURLToPath } from 'node:url';

const __filename = fileURLToPath(import.meta.url);
const __dirname = path.dirname(__filename);
const PROJECT_ROOT = path.resolve(__dirname, '../..');

const TRANSACTIONS_PATH = path.join(
  PROJECT_ROOT,
  'data/supporters/transactions.json',
);
const DASHBOARD_OUT = path.join(
  PROJECT_ROOT,
  'public/api/dashboard-supporters.json',
);
const ABOUT_OUT = path.join(PROJECT_ROOT, 'public/api/about-supporters.json');

/**
 * Tier config — About view only. Ordered high → low so first match wins.
 * 調整閾值時改這個陣列即可，無需動 UI 或 consumer。
 */
const TIER_CONFIG = [
  {
    id: 'canopy',
    emoji: '🌳',
    label: '大樹',
    label_en: 'Canopy',
    min_twd: 5000,
    desc: '累計 NT$5,000 以上',
  },
  {
    id: 'grove',
    emoji: '🌿',
    label: '小樹',
    label_en: 'Grove',
    min_twd: 1000,
    desc: '累計 NT$1,000 以上',
  },
  {
    id: 'sprout',
    emoji: '🌱',
    label: '新芽',
    label_en: 'Sprout',
    min_twd: 1,
    desc: '第一個支持',
  },
];

function pickTier(totalAmount) {
  for (const tier of TIER_CONFIG) {
    if (totalAmount >= tier.min_twd) {
      return {
        id: tier.id,
        emoji: tier.emoji,
        label: tier.label,
        label_en: tier.label_en,
      };
    }
  }
  return null;
}

function loadTransactions() {
  if (!fs.existsSync(TRANSACTIONS_PATH)) {
    console.warn(
      `⚠️  ${path.relative(PROJECT_ROOT, TRANSACTIONS_PATH)} not found — writing empty derived views`,
    );
    return { schema_version: 1, last_fetched: null, transactions: [] };
  }
  return JSON.parse(fs.readFileSync(TRANSACTIONS_PATH, 'utf8'));
}

/**
 * Build Dashboard view — chronological timeline + running total + breakdowns.
 * Privacy: no names, no messages. Only amount / type / anonymity / date.
 */
function buildDashboard(doc) {
  const txs = (doc.transactions || []).filter((t) => t.status === 'received');
  txs.sort((a, b) => (a.timestamp || '').localeCompare(b.timestamp || ''));

  const total = txs.reduce((s, t) => s + t.amount, 0);
  const transactionCount = txs.length;

  // Count unique supporters (rough heuristic):
  //   - named person: count by display name
  //   - anonymous: count each anonymous tx separately (conservative)
  const namedSet = new Set();
  let anonCount = 0;
  for (const t of txs) {
    if (t.anonymous) anonCount += 1;
    else namedSet.add(t.name);
  }
  const supporterCount = namedSet.size + anonCount;

  const monthlyCount = txs.filter((t) => t.type === 'monthly').length;
  const oneTimeCount = txs.filter((t) => t.type === 'one-time').length;

  // Timeline entries — running total alongside each tx
  let running = 0;
  const timeline = txs.map((t) => {
    running += t.amount;
    return {
      date: t.date,
      timestamp: t.timestamp,
      amount: t.amount,
      currency: t.currency,
      type: t.type,
      anonymous: t.anonymous,
      running_total: running,
    };
  });

  // Group by YYYY-MM for monthly rollup
  const byMonth = {};
  for (const t of txs) {
    const ym = (t.date || '').slice(0, 7);
    if (!ym) continue;
    byMonth[ym] = (byMonth[ym] || 0) + t.amount;
  }

  return {
    schema_version: 1,
    last_updated: new Date().toISOString(),
    last_fetched: doc.last_fetched || null,
    totals: {
      total_received_twd: total,
      transaction_count: transactionCount,
      supporter_count: supporterCount,
      monthly_subscriptions: monthlyCount,
      one_time: oneTimeCount,
      anonymous_ratio: transactionCount > 0 ? anonCount / transactionCount : 0,
    },
    first_date: txs[0]?.date || null,
    latest_date: txs[txs.length - 1]?.date || null,
    by_month: byMonth,
    timeline,
  };
}

/**
 * Build About view — supporter cards grouped by identity, with messages.
 * Privacy: no amounts. Only display name, messages, anonymity, type.
 *
 * Grouping heuristic:
 *   - Named: group by name. messages[] is all messages chronologically.
 *   - Anonymous: each transaction is its own entry (conservative; until
 *     subscription_id lets us merge recurring anonymous donors).
 */
function buildAbout(doc) {
  const txs = (doc.transactions || []).filter((t) => t.status === 'received');
  txs.sort((a, b) => (a.timestamp || '').localeCompare(b.timestamp || ''));

  /** @type {Map<string, any>} */
  const grouped = new Map();

  for (const t of txs) {
    // key: named → name; anonymous → unique per tx id
    const key = t.anonymous ? `__anon__${t.id}` : `__named__${t.name}`;
    const existing = grouped.get(key);
    const messageEntry = t.message
      ? { date: t.date, text: t.message, type: t.type }
      : null;
    if (existing) {
      if (messageEntry) existing.messages.push(messageEntry);
      existing.transaction_count += 1;
      existing.last_date = t.date;
      existing.active_monthly = existing.active_monthly || t.type === 'monthly';
      existing.__total_amount += t.amount;
    } else {
      grouped.set(key, {
        display_name: t.anonymous ? '匿名支持者' : t.name,
        anonymous: t.anonymous,
        first_date: t.date,
        last_date: t.date,
        transaction_count: 1,
        active_monthly: t.type === 'monthly',
        messages: messageEntry ? [messageEntry] : [],
        __total_amount: t.amount, // 僅用於算 tier，不進最終輸出
      });
    }
  }

  // Assign tier based on accumulated amount; then strip internal-only fields
  // so the About-facing JSON never contains raw TWD amounts (privacy design).
  const supporters = [...grouped.values()].map((s) => {
    const tier = pickTier(s.__total_amount);
    const { __total_amount, ...publicFields } = s;
    return { ...publicFields, tier };
  });

  // Sort: tier tier 高 → 低（Canopy → Grove → Sprout），同層內最新 last_date 優先
  const tierOrder = { canopy: 0, grove: 1, sprout: 2 };
  supporters.sort((a, b) => {
    const ta = tierOrder[a.tier?.id] ?? 99;
    const tb = tierOrder[b.tier?.id] ?? 99;
    if (ta !== tb) return ta - tb;
    return (b.last_date || '').localeCompare(a.last_date || '');
  });

  // Tier summary counts (for About header展示)
  const tierCounts = Object.fromEntries(TIER_CONFIG.map((c) => [c.id, 0]));
  for (const s of supporters) {
    if (s.tier) tierCounts[s.tier.id] = (tierCounts[s.tier.id] || 0) + 1;
  }

  return {
    schema_version: 1,
    last_updated: new Date().toISOString(),
    last_fetched: doc.last_fetched || null,
    supporter_count: supporters.length,
    tier_counts: tierCounts,
    tier_config: TIER_CONFIG.map(({ id, emoji, label, label_en, desc }) => ({
      id,
      emoji,
      label,
      label_en,
      desc,
    })),
    supporters,
  };
}

function writeJson(file, data) {
  fs.mkdirSync(path.dirname(file), { recursive: true });
  fs.writeFileSync(file, JSON.stringify(data, null, 2) + '\n', 'utf8');
  console.log(`  ✓ ${path.relative(PROJECT_ROOT, file)}`);
}

function main() {
  console.log('📥 generate-supporters-data.js');
  const doc = loadTransactions();
  const dashboard = buildDashboard(doc);
  const about = buildAbout(doc);

  writeJson(DASHBOARD_OUT, dashboard);
  writeJson(ABOUT_OUT, about);

  console.log(
    `  → total NT$${dashboard.totals.total_received_twd.toLocaleString()} / ${dashboard.totals.transaction_count} tx / ${about.supporter_count} supporters`,
  );
}

main();
