#!/usr/bin/env node
/**
 * triage.mjs — Feedback → GitHub issue（cron routine twmd-feedback-triage 的執行體）。
 *
 * 流程：讀新回報 → spam/dedupe/分類（classify.mjs 純函式）→ 開 GitHub issue
 *       （對齊既有 template,只放 display_name 不放 email）→ 回寫 status。
 *
 * §自主權邊界：本 script 只做「把讀者原話機械性 routing 成 issue」（= 代讀者填表單,
 * verbatim + 署名 + provenance）。**不**以維護者身份回覆 / close / merge —— 那留給
 * MAINTAINER-PIPELINE 的人類 gate。
 *
 * 安全預設：--dry-run 是 DEFAULT。要真的開 issue + 回寫必須顯式 --commit。
 *
 * 用法：
 *   node scripts/feedback/triage.mjs                      # dry-run,讀 Supabase（需 env）
 *   node scripts/feedback/triage.mjs --seed <file.json>   # dry-run,讀 JSON fixture（離線測試）
 *   node scripts/feedback/triage.mjs --commit             # 真的開 issue + 回寫（routine 用）
 *
 * env（正式跑才需要,放 ~/.taiwanmd-feedback.env 或環境變數）：
 *   SUPABASE_URL, SUPABASE_SERVICE_KEY
 */
import {
  readFileSync,
  writeFileSync,
  mkdirSync,
  existsSync,
  readdirSync,
} from 'node:fs';
import { dirname, join } from 'node:path';
import { execFileSync } from 'node:child_process';
import { triageBatch } from './lib/classify.mjs';
import {
  buildArchiveRecord,
  mergeComments,
  archiveRelPath,
} from './lib/archive.mjs';

const ARCHIVE_ROOT = 'docs/feedback/archive';

const REPO = 'frank890417/taiwan-md';

function parseArgs(argv) {
  const a = { commit: false, seed: null, limit: 50 };
  for (let i = 2; i < argv.length; i++) {
    const v = argv[i];
    if (v === '--commit') a.commit = true;
    else if (v === '--dry-run') a.commit = false;
    else if (v === '--seed') a.seed = argv[++i];
    else if (v === '--limit') a.limit = parseInt(argv[++i], 10) || 50;
  }
  return a;
}

// ── data source ───────────────────────────────────────────────────────────────
function loadEnvFile() {
  // 讀 ~/.taiwanmd-feedback.env（KEY=VALUE 一行一條）進 process.env(不覆蓋已存在)。
  try {
    const home = process.env.HOME || '';
    const txt = readFileSync(`${home}/.taiwanmd-feedback.env`, 'utf8');
    for (const line of txt.split('\n')) {
      const m = line.match(/^\s*([A-Z0-9_]+)\s*=\s*(.*)\s*$/);
      if (m && !process.env[m[1]])
        process.env[m[1]] = m[2].replace(/^["']|["']$/g, '');
    }
  } catch {
    /* 沒有就算了 */
  }
}

async function fetchNewFeedback(limit) {
  loadEnvFile();
  const url = process.env.SUPABASE_URL;
  const key = process.env.SUPABASE_SERVICE_KEY;
  if (!url || !key) {
    throw new Error(
      'SUPABASE_URL / SUPABASE_SERVICE_KEY 未設定（放 ~/.taiwanmd-feedback.env）。離線測試請用 --seed。',
    );
  }
  const endpoint = `${url}/rest/v1/feedback?status=eq.new&order=created_at.asc&limit=${limit}`;
  const res = await fetch(endpoint, {
    headers: { apikey: key, Authorization: `Bearer ${key}` },
  });
  if (!res.ok)
    throw new Error(`Supabase REST ${res.status}: ${await res.text()}`);
  return res.json();
}

async function writeBackStatus(id, status, issue, note) {
  const url = process.env.SUPABASE_URL;
  const key = process.env.SUPABASE_SERVICE_KEY;
  const patch = {
    status,
    triaged_at: new Date().toISOString(),
    ...(issue ? { issue_url: issue.url, issue_number: issue.number } : {}),
    ...(note ? { triage_note: note } : {}),
  };
  const res = await fetch(`${url}/rest/v1/feedback?id=eq.${id}`, {
    method: 'PATCH',
    headers: {
      apikey: key,
      Authorization: `Bearer ${key}`,
      'Content-Type': 'application/json',
      Prefer: 'return=minimal',
    },
    body: JSON.stringify(patch),
  });
  if (!res.ok) throw new Error(`write-back ${res.status}: ${await res.text()}`);
}

// ── github ────────────────────────────────────────────────────────────────────
function listOpenIssues() {
  try {
    const out = execFileSync(
      'gh',
      [
        'issue',
        'list',
        '--repo',
        REPO,
        '--state',
        'open',
        '--limit',
        '200',
        '--json',
        'title,body,number',
      ],
      { encoding: 'utf8' },
    );
    return JSON.parse(out);
  } catch (e) {
    console.warn(
      '[triage] gh issue list failed, dedupe vs existing skipped:',
      e.message,
    );
    return [];
  }
}

function createIssue(issue) {
  const args = [
    'issue',
    'create',
    '--repo',
    REPO,
    '--title',
    issue.title,
    '--body',
    issue.body,
  ];
  for (const l of issue.labels) args.push('--label', l);
  const out = execFileSync('gh', args, { encoding: 'utf8' }).trim();
  // gh prints the issue URL on success
  const url = out.split('\n').pop().trim();
  const num = parseInt((url.match(/\/issues\/(\d+)/) || [])[1] || '0', 10);
  return { url, number: num };
}

// ── batch-cluster consolidated report（同 slug ≥ 閾值 → 1 份 artifact 給維護者）──
function writeClusterReport(slug, held, mode) {
  const date = new Date().toISOString().slice(0, 10);
  const safe = slug.replace(/[^\w一-鿿-]+/g, '_');
  const rel = `reports/feedback-clusters/${date}-${safe}.md`;
  if (mode !== 'COMMIT') return rel;
  try {
    mkdirSync(dirname(rel), { recursive: true });
    if (existsSync(rel)) return rel; // 同日重跑不重寫(回報維持 new 會再 hold 一次)
    const rows = held.map((h, i) => {
      const r = h.row;
      const quote = r.quote
        ? `\n   > 選取原文：${String(r.quote).replace(/\n/g, ' ')}`
        : '';
      const fix = r.correct_info ? `\n   - 更正建議：${r.correct_info}` : '';
      return `${i + 1}. **${r.display_name || '匿名讀者'}** (${(r.created_at || '').slice(0, 16)}) · feedback id \`${r.id}\`${quote}\n   - 回報：${r.body}${fix}`;
    });
    writeFileSync(
      rel,
      `# Feedback cluster hold：${slug}（${held.length} 筆，${date}）\n\n` +
        `> 同一篇文章單一 batch ≥ ${held.length} 筆非 spam 回報，batch-cluster guard 自動 hold。\n` +
        `> 全部回報維持 Supabase status=new（不逐筆開 issue）。維護者決策後：開 1 個\n` +
        `> consolidated issue 或直接走 REWRITE 修文，再把這批標 filed/rejected。\n\n` +
        rows.join('\n') +
        `\n\n---\n_由 twmd-feedback-triage batch-cluster guard 產出（classify.mjs BATCH_CLUSTER_THRESHOLD）_\n`,
    );
  } catch (e) {
    console.warn(
      `[triage] cluster report write failed for ${slug}:`,
      e.message,
    );
  }
  return rel;
}

// ── git archive（主權層：feedback + 溝通紀錄落進 repo）──────────────────────────
function writeArchive(row, note) {
  const rel = archiveRelPath(row);
  try {
    mkdirSync(dirname(rel), { recursive: true });
    if (!existsSync(rel)) {
      writeFileSync(
        rel,
        buildArchiveRecord({ ...row, triage_note: note }, note),
      );
    }
    return rel;
  } catch (e) {
    console.warn(`[triage] archive write failed for ${row.id}:`, e.message);
    return null;
  }
}

function fetchIssueComments(issueNumber) {
  try {
    const out = execFileSync(
      'gh',
      [
        'issue',
        'view',
        String(issueNumber),
        '--repo',
        REPO,
        '--json',
        'comments',
      ],
      { encoding: 'utf8' },
    );
    const data = JSON.parse(out);
    return (data.comments || []).map((c) => ({
      id: `${c.author?.login || '?'}-${c.createdAt}`,
      author: c.author?.login || '?',
      createdAt: c.createdAt,
      body: c.body,
    }));
  } catch {
    return [];
  }
}

// 掃 archive dir，把每筆已 filed 紀錄的 issue 新留言 sync 進 §溝通紀錄（人類維護者
// 的回覆也進 git）。回傳更新的檔數。
// 回傳 { scanned, synced }：synced 單獨看是 proxy 訊號 — 0 分不出「掃了 36 檔都沒新留言」
// 跟「一檔都沒掃到（目錄消失／權限壞）」。scanned 讓收官數字是量出來的，不是手數的。
function syncArchiveComments() {
  if (!existsSync(ARCHIVE_ROOT)) return { scanned: 0, synced: 0 };
  let scanned = 0;
  let synced = 0;
  for (const m of readdirSync(ARCHIVE_ROOT)) {
    const dir = join(ARCHIVE_ROOT, m);
    let files = [];
    try {
      files = readdirSync(dir).filter((f) => f.endsWith('.md'));
    } catch {
      continue;
    }
    for (const f of files) {
      const path = join(dir, f);
      let content;
      try {
        content = readFileSync(path, 'utf8');
      } catch {
        continue;
      }
      scanned++;
      const num = (content.match(/^issue_number:\s*(\d+)/m) || [])[1];
      if (!num) continue;
      const merged = mergeComments(content, fetchIssueComments(num));
      if (merged !== content) {
        writeFileSync(path, merged);
        synced++;
      }
    }
  }
  return { scanned, synced };
}

// ── main ──────────────────────────────────────────────────────────────────────
async function main() {
  const args = parseArgs(process.argv);
  const mode = args.commit ? 'COMMIT' : 'DRY-RUN';

  let rows;
  if (args.seed) {
    rows = JSON.parse(readFileSync(args.seed, 'utf8'));
    console.log(
      `[triage] seed=${args.seed} (${rows.length} rows) · mode=${mode}`,
    );
  } else {
    rows = await fetchNewFeedback(args.limit);
    console.log(`[triage] fetched ${rows.length} new feedback · mode=${mode}`);
  }

  const existing = args.commit ? listOpenIssues() : [];
  const results = triageBatch(rows, existing);

  const summary = { file: 0, reject: 0, skip: 0, hold: 0 };
  for (const r of results) {
    summary[r.decision]++;
    const tag = r.decision.toUpperCase().padEnd(6);
    if (r.decision === 'hold') {
      console.log(`  ${tag} id=${r.row.id} · ${r.reason}`);
      continue; // status 不回寫(維持 new);cluster report 統一在迴圈後寫
    }
    if (r.decision === 'file') {
      console.log(`  ${tag} [${r.issue.type}] ${r.issue.title}`);
      console.log(`         labels: ${r.issue.labels.join(', ')}`);
      if (args.commit) {
        const created = createIssue(r.issue);
        await writeBackStatus(r.row.id, 'filed', created, r.note);
        const arch = writeArchive(
          {
            ...r.row,
            status: 'filed',
            issue_url: created.url,
            issue_number: created.number,
          },
          r.note,
        );
        console.log(`         → ${created.url}${arch ? ` · 📁 ${arch}` : ''}`);
      } else {
        console.log(`         (dry-run; --commit to file)`);
      }
    } else {
      console.log(`  ${tag} id=${r.row.id} · ${r.reason}`);
      if (args.commit && r.decision === 'reject') {
        await writeBackStatus(r.row.id, 'rejected', null, r.note);
      }
      // skip(dup) 不改 status:留著下次再判（避免漏接真不同的回報）
    }
  }

  // batch-cluster：每個 held slug 產 1 份 consolidated report 給維護者決策。
  const clusters = new Map();
  for (const r of results) {
    if (r.decision !== 'hold') continue;
    if (!clusters.has(r.cluster)) clusters.set(r.cluster, []);
    clusters.get(r.cluster).push(r);
  }
  for (const [slug, held] of clusters) {
    const rel = writeClusterReport(slug, held, mode);
    console.log(
      `  HOLD→  cluster「${slug}」 ${held.length} 筆 → ${rel}${mode === 'COMMIT' ? '' : ' (dry-run)'}`,
    );
  }

  // sync 既有 filed 紀錄的 issue 新留言（維護者回覆）進 git archive。
  // dry-run 不跑真實 scan，故印 skipped 而非 0——避免「沒掃」被讀成「掃過沒事」。
  const arch = args.commit ? syncArchiveComments() : null;

  console.log(
    `\n[triage] done · file=${summary.file} reject=${summary.reject} skip=${summary.skip} hold=${summary.hold} · ` +
      (arch
        ? `archive-scanned=${arch.scanned} archive-comments-synced=${arch.synced}`
        : `archive-scan=skipped (dry-run)`),
  );
  return summary;
}

main().catch((e) => {
  console.error('[triage] FATAL:', e.message);
  process.exit(1);
});
