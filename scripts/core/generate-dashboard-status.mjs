#!/usr/bin/env node
/**
 * generate-dashboard-status.mjs — /dashboard 🩺 營運狀態 section 資料源
 *
 * 為什麼：reports/design-dashboard-status-section-2026-07-24.md（Mode 4
 * THINK→DIVERGE→REPORT→IMPLEMENT）定案方案 A — dashboard 新 section 呈現
 * status.claude.com 式的三語彙：routine 飛輪 operational/degraded/down、
 * 巴別塔覆蓋趨勢、最近事件。四個資料源全部已存在（零新感測器），本腳本
 * 只是把散落各處的 derived 訊號投影成單一 JSON：
 *   1. docs/semiont/routine-live-state.json（cron SSOT）×
 *      docs/semiont/memory/*.md 檔名（fire 痕跡）→ routine 狀態列 + 14 天網格
 *   2. reports/babel/progress-{月}.jsonl（時間序列快照）→ 九語覆蓋 + 節點
 *   3. public/api/dashboard-alerts.json → 最近事件
 *   4. gh run list → 最近部署（無 token/CLI 時優雅降級 null）
 *
 * 誠實性邊界（REFLEXES #82 proxy signal，per 設計報告 §二）：memory 檔存在
 * 只證明「routine fire 且走完收官寫 memory」，不是業務效果本身。routine 板
 * 與 babel 板刻意分開呈現，不混維度（REFLEXES #38）。
 *
 * 每個子板獨立 try-catch：任一資料源掛掉，對應子板降級為 null，不炸整檔。
 *
 * Usage: node scripts/core/generate-dashboard-status.mjs
 */

import { readFileSync, readdirSync, writeFileSync, mkdirSync } from 'node:fs';
import { join, dirname } from 'node:path';
import { fileURLToPath } from 'node:url';
import { execSync } from 'node:child_process';

const __filename = fileURLToPath(import.meta.url);
const __dirname = dirname(__filename);
const REPO = join(__dirname, '../..');

const ROUTINE_LIVE_STATE = join(REPO, 'docs/semiont/routine-live-state.json');
const MEMORY_DIR = join(REPO, 'docs/semiont/memory');
const BABEL_DIR = join(REPO, 'reports/babel');
const ALERTS_PATH = join(REPO, 'public/api/dashboard-alerts.json');
const OUT_PATH = join(REPO, 'public/api/dashboard-status.json');

const WEEKDAY_ZH = ['日', '一', '二', '三', '四', '五', '六'];

// ─────────────────────────── 小工具 ───────────────────────────

function readJson(p) {
  return JSON.parse(readFileSync(p, 'utf8'));
}

/** 'YYYY-MM-DD' — 用 process 本機時間（此 repo 開發機 + heartbeat 執行機皆
 * Asia/Taipei，跟 cronExpression 的 hour:min 是同一個本地時區語意，見下方
 * cadenceHuman()）。 */
function localDateStr(d) {
  const y = d.getFullYear();
  const m = String(d.getMonth() + 1).padStart(2, '0');
  const day = String(d.getDate()).padStart(2, '0');
  return `${y}-${m}-${day}`;
}

function addDays(d, n) {
  const nd = new Date(d);
  nd.setDate(nd.getDate() + n);
  return nd;
}

/** cron 5 欄 "min hour dom month dow" → dow===null 表示每天，否則 0-6（週日=0）*/
function parseCronDow(cronExpression) {
  const parts = cronExpression.trim().split(/\s+/);
  if (parts.length < 5) return { hour: 0, min: 0, dow: null };
  const [min, hour, , , dow] = parts;
  return {
    hour: parseInt(hour, 10) || 0,
    min: parseInt(min, 10) || 0,
    dow: dow === '*' ? null : parseInt(dow, 10),
  };
}

function cadenceHuman(cronExpression) {
  const { hour, min, dow } = parseCronDow(cronExpression);
  const hh = String(hour).padStart(2, '0');
  const mm = String(min).padStart(2, '0');
  if (dow === null) return `每天 ${hh}:${mm}`;
  return `每週${WEEKDAY_ZH[dow] ?? '?'} ${hh}:${mm}`;
}

/** 給定 'YYYY-MM-DD'，該天在該 cron 下是否為期望 fire 日 */
function isExpectedDate(dateStr, dow) {
  if (dow === null) return true;
  const wd = new Date(`${dateStr}T00:00:00`).getDay();
  return wd === dow;
}

// ─────────────────────────── 1. Routine 飛輪狀態板 ───────────────────────────

// taskId → 實際寫入 docs/semiont/memory/ 的 slug 別名表。多數 task 的
// taskId（去掉 taiwanmd-routine- 前綴後）跟 memory 檔名 slug 完全一致；
// 下面這幾條是 hand-tune 過的例外（2026-07-24 用
// `ls docs/semiont/memory | grep twmd-` 撈出實際 slug 家族後對照 routine-live-state
// 逐條核對得出）：
//   - twmd-maintainer-daily → 早期收官寫 twmd-maintainer-am（"am" = 晨間），
//     近期改直寫 twmd-maintainer-daily，兩種都算數
//   - twmd-weekly-report-sun → 有時省略 -sun 字尾寫 twmd-weekly-report
//   - twmd-spore-pick-daily / twmd-spore-publish-daily → 同樣有 -am / 無字尾的
//     舊寫法混跑
//   - twmd-founder-lens-weekly → FOUNDER-LENS-PIPELINE.md Stage 6 finale 明訂
//     handle 固定寫 twmd-founder-lens（不帶 -weekly，對齊該 pipeline 自己
//     reports/founder-lens-YYYY-MM-DD.md 的命名慣例），2026-07-24 補上 alias
// 找不到別名的 task 一律用「taskId 去掉 taiwanmd-routine- 前綴」精確比對，
// 不做 fuzzy family 比對（避免 twmd-rewrite-daily 誤吃 twmd-rewrite-彎彎 這類
// /twmd-rewrite 手動單篇改寫留下的同前綴 memory 檔）。
const SLUG_ALIASES = {
  'twmd-maintainer-daily': ['twmd-maintainer-daily', 'twmd-maintainer-am'],
  'twmd-weekly-report-sun': ['twmd-weekly-report-sun', 'twmd-weekly-report'],
  'twmd-spore-pick-daily': ['twmd-spore-pick-daily', 'twmd-spore-pick-am'],
  'twmd-spore-publish-daily': [
    'twmd-spore-publish-daily',
    'twmd-spore-publish',
  ],
  'twmd-founder-lens-weekly': ['twmd-founder-lens-weekly', 'twmd-founder-lens'],
};

function normalizeTaskId(taskId) {
  return taskId.startsWith('taiwanmd-routine-')
    ? taskId.slice('taiwanmd-routine-'.length)
    : taskId;
}

function slugVariantsFor(taskSlug) {
  return SLUG_ALIASES[taskSlug] || [taskSlug];
}

const MEMORY_FILE_RE = /^(\d{4}-\d{2}-\d{2})-(\d{6})-(twmd-.+)\.md$/;

function collectMemoryFires() {
  const files = readdirSync(MEMORY_DIR);
  // slug → [{date, time}]（time = HHMMSS 字串，for last_fire ISO 組字串用）
  const bySlug = new Map();
  let totalMatched30d = 0;
  const cutoff30d = localDateStr(addDays(new Date(), -30));
  for (const f of files) {
    const m = MEMORY_FILE_RE.exec(f);
    if (!m) continue;
    const [, date, time, slug] = m;
    if (!bySlug.has(slug)) bySlug.set(slug, []);
    bySlug.get(slug).push({ date, time });
    if (date >= cutoff30d) totalMatched30d++;
  }
  if (totalMatched30d === 0) {
    console.warn(
      '⚠️  generate-dashboard-status: 過去 30 天在 docs/semiont/memory/ 解析出 0 條 twmd- fire 痕跡 — regex 或目錄可能壞了，routine 板會全部顯示 down（fail-loud selftest）',
    );
  }
  return bySlug;
}

function buildRoutineBoard() {
  const liveState = readJson(ROUTINE_LIVE_STATE);
  const fetchedAt = liveState.fetched_at;
  const staleHours =
    Math.round(((Date.now() - new Date(fetchedAt).getTime()) / 3.6e6) * 10) /
    10;

  const fires = collectMemoryFires();
  const today = new Date();
  const todayStr = localDateStr(today);

  const items = (liveState.tasks || []).map((task) => {
    const taskSlug = normalizeTaskId(task.taskId);
    const { hour, min, dow } = parseCronDow(task.cronExpression);
    const variants = slugVariantsFor(taskSlug);
    // 這個 task 所有變體別名的 fire 紀錄合併成單一日期集合
    const fireDates = new Set();
    let lastFire = null; // {date, time}
    for (const v of variants) {
      for (const hit of fires.get(v) || []) {
        fireDates.add(hit.date);
        if (!lastFire || hit.date > lastFire.date) lastFire = hit;
        else if (hit.date === lastFire.date && hit.time > lastFire.time)
          lastFire = hit;
      }
    }

    // grid14：最近 14 天（含今天），oldest → newest
    const grid14 = [];
    for (let i = 13; i >= 0; i--) {
      const d = addDays(today, -i);
      const dateStr = localDateStr(d);
      const expected = isExpectedDate(dateStr, dow);
      let state;
      if (!expected) state = 'idle';
      else if (fireDates.has(dateStr)) state = 'fired';
      else if (dateStr === todayStr) {
        // 今天且排程時刻還沒到 → 還不算「miss」，先當 idle
        const now = new Date();
        const due =
          now.getHours() > hour ||
          (now.getHours() === hour && now.getMinutes() >= min);
        state = due ? 'missed' : 'idle';
      } else state = 'missed';
      grid14.push({ date: dateStr, state });
    }

    // status：從今天往回走「期望但錯過」的連續次數（不只看 14 天窗，往回
    // 找 60 天以取得準確的連續 miss 計數 — 14 天網格只是視覺化窗口，不是
    // status 判定的唯一依據，避免週排程 routine 在窗口邊界誤判）
    let status;
    if (!task.enabled) {
      status = 'disabled';
    } else {
      let consecutiveMissed = 0;
      for (let i = 0; i <= 60; i++) {
        const d = addDays(today, -i);
        const dateStr = localDateStr(d);
        if (!isExpectedDate(dateStr, dow)) continue;
        if (dateStr === todayStr) {
          const now = new Date();
          const due =
            now.getHours() > hour ||
            (now.getHours() === hour && now.getMinutes() >= min);
          if (!due) continue; // 今天還沒到點，不計入
        }
        if (fireDates.has(dateStr)) break; // 找到最近一次命中，停止累計
        consecutiveMissed++;
      }
      status =
        consecutiveMissed === 0
          ? 'operational'
          : consecutiveMissed === 1
            ? 'degraded'
            : 'down';
    }

    return {
      id: taskSlug,
      cron: task.cronExpression,
      cadence_human: cadenceHuman(task.cronExpression),
      enabled: !!task.enabled,
      status,
      last_fire: lastFire
        ? `${lastFire.date}T${lastFire.time.slice(0, 2)}:${lastFire.time.slice(2, 4)}:${lastFire.time.slice(4, 6)}+08:00`
        : null,
      grid14,
    };
  });

  return { fetched_at: fetchedAt, stale_hours: staleHours, items };
}

// ─────────────────────────── 2. 巴別塔狀態板 ───────────────────────────

function latestBabelProgressFile() {
  const files = readdirSync(BABEL_DIR).filter((f) =>
    /^progress-\d{4}-\d{2}\.jsonl$/.test(f),
  );
  if (files.length === 0)
    throw new Error('找不到 reports/babel/progress-*.jsonl');
  files.sort();
  return join(BABEL_DIR, files[files.length - 1]);
}

function readJsonlRows(path) {
  const text = readFileSync(path, 'utf8');
  const rows = [];
  for (const line of text.split('\n')) {
    const trimmed = line.trim();
    if (!trimmed) continue;
    try {
      rows.push(JSON.parse(trimmed));
    } catch {
      // 壞行跳過，不炸整個 parse
    }
  }
  return rows;
}

function totalFresh(row) {
  return Object.values(row.langs || {}).reduce(
    (sum, l) => sum + (l.fresh || 0),
    0,
  );
}

function gapTotal(row) {
  return Object.values(row.langs || {}).reduce(
    (sum, l) => sum + (l.stale || 0) + (l.missing || 0),
    0,
  );
}

function buildBabelBoard() {
  const path = latestBabelProgressFile();
  const rows = readJsonlRows(path);
  if (rows.length === 0) throw new Error(`${path} 沒有可解析的列`);

  const latest = rows[rows.length - 1];
  const previous = rows.length >= 2 ? rows[rows.length - 2] : null;

  const totalZh = latest.total_zh;
  const langs = Object.entries(latest.langs || {}).map(([lang, s]) => ({
    lang,
    fresh: s.fresh,
    stale: s.stale,
    missing: s.missing,
    coverage_pct:
      totalZh > 0
        ? Math.round(((totalZh - s.missing) / totalZh) * 1000) / 10
        : 0,
  }));

  const gap = gapTotal(latest);
  const gapDelta = previous ? gap - gapTotal(previous) : 0;

  // fresh_delta_24h：latest 總 fresh − 24h 窗內最舊一筆的總 fresh
  const latestTs = new Date(latest.ts).getTime();
  const windowStart = latestTs - 24 * 3600 * 1000;
  let earliestInWindow = latest;
  for (const row of rows) {
    const t = new Date(row.ts).getTime();
    if (t >= windowStart && t < new Date(earliestInWindow.ts).getTime()) {
      earliestInWindow = row;
    }
  }
  const freshDelta24h = totalFresh(latest) - totalFresh(earliestInWindow);

  // nodes：latest row 若沒有 nodes 欄（不是每一筆快照都帶節點資訊），往回找
  // 最近一筆有 nodes 的 row
  let nodesRow = null;
  for (let i = rows.length - 1; i >= 0; i--) {
    if (rows[i].nodes) {
      nodesRow = rows[i];
      break;
    }
  }
  const nodes = [];
  if (nodesRow) {
    for (const [key, val] of Object.entries(nodesRow.nodes)) {
      if (key.startsWith('endpoint:')) {
        nodes.push({ name: key.slice('endpoint:'.length), alive: !!val.alive });
      } else {
        nodes.push({
          name: key,
          ok: val.ok ?? 0,
          fail: val.fail ?? 0,
          avg_s: val.avg_s ?? null,
        });
      }
    }
  }

  return {
    snapshot_ts: latest.ts,
    // total_zh：橫條圖需要「全語言共用的分母」才能把 fresh/stale/missing 三段
    // 畫成同一把尺（每語言 coverage_pct 已經是 (total-missing)/total，但畫
    // stacked bar 還需要 fresh/stale 各自佔 total 的寬度）。
    total_zh: totalZh,
    langs,
    gap_total: gap,
    gap_delta_vs_prev: gapDelta,
    fresh_delta_24h: freshDelta24h,
    nodes,
  };
}

// ─────────────────────────── 3. 最近事件 ───────────────────────────

function buildIncidents() {
  const data = readJson(ALERTS_PATH);
  const alerts = [...(data.alerts || [])];
  // alerts.json 本身依 severity 排序，沒有逐條時間戳；firstSeen 是唯一可排序
  // 的時間訊號，用它當近似的「最新」排序（新 alert 的 firstSeen 較晚）。
  alerts.sort((a, b) => (b.firstSeen || '').localeCompare(a.firstSeen || ''));
  return alerts.slice(0, 8).map((a) => ({
    ts: a.firstSeen || data.lastUpdated || null,
    level: a.severity === 'red' ? 'red' : 'yellow',
    text: a.message,
    source: a.source || 'alerts',
  }));
}

// ─────────────────────────── 4. 最近部署 ───────────────────────────

function buildDeploys() {
  const raw = execSync(
    'gh run list --limit 5 --json displayTitle,conclusion,createdAt,workflowName',
    { encoding: 'utf8', timeout: 15_000 },
  );
  const runs = JSON.parse(raw);
  return runs.map((r) => ({
    ts: r.createdAt,
    conclusion: r.conclusion === 'success' ? 'success' : 'failure',
    title: `${r.workflowName}: ${r.displayTitle}`,
  }));
}

// ─────────────────────────── main ───────────────────────────

function safeBuild(name, fn) {
  try {
    return fn();
  } catch (e) {
    console.warn(
      `⚠️  generate-dashboard-status: ${name} 子板失敗 — ${e.message}`,
    );
    return null;
  }
}

function main() {
  console.log('🩺 generate-dashboard-status...');

  const routines = safeBuild('routines', buildRoutineBoard);
  const babel = safeBuild('babel', buildBabelBoard);
  const incidents = safeBuild('incidents', buildIncidents) || [];
  const deploys = safeBuild('deploys', buildDeploys);

  const output = {
    generated_at: new Date().toISOString(),
    routines,
    babel,
    incidents,
    deploys,
  };

  mkdirSync(dirname(OUT_PATH), { recursive: true });
  writeFileSync(OUT_PATH, JSON.stringify(output, null, 2) + '\n');

  const statusCounts = (routines?.items || []).reduce((acc, it) => {
    acc[it.status] = (acc[it.status] || 0) + 1;
    return acc;
  }, {});
  console.log(
    `   ✓ ${OUT_PATH} — routines=${routines?.items.length ?? 0} (${JSON.stringify(statusCounts)}), stale_hours=${routines?.stale_hours ?? 'n/a'}, babel_langs=${babel?.langs.length ?? 0}, gap_total=${babel?.gap_total ?? 'n/a'}, nodes=${babel?.nodes.length ?? 0}, incidents=${incidents.length}, deploys=${deploys ? deploys.length : 'null'}`,
  );
  return 0;
}

main();
