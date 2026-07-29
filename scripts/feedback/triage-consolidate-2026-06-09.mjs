#!/usr/bin/env node
/**
 * triage-consolidate-2026-06-09.mjs — ONE-OFF consolidation run for 2026-06-09 feedback batch.
 *
 * 為什麼存在：本日 batch 有 12 筆同一讀者（Cs Gou）對同一篇文章（國家太空中心）的
 * section-by-section 勘誤。deterministic triage.mjs 會開 12 個「標題完全相同」的
 * [Fact Check] issue（batch-boundary dedupe gap：classify.mjs isDuplicate 的
 * `title === built.title` content-dedupe 只擋「跨 run 既有 open issue」，擋不住同 batch
 * 內 distinct body-sig 的同篇 content）。Pipeline 設計意圖本來就是「一篇文章一個 fact-check
 * issue」（見 classify.mjs:191），所以正確處置 = 把 12 筆合併成 1 個 issue（逐條 verbatim
 * + 各自 feedback id provenance），bug + idea 各自開。
 *
 * 這支 script 重用 lib 函式（buildIssue / archive）保持 archive + provenance 格式一致。
 * 結構性 finding（pipeline 需內建 same-article content clustering）另走 handoff + LESSONS gate。
 *
 * 用法：node scripts/feedback/triage-consolidate-2026-06-09.mjs            # dry-run
 *       node scripts/feedback/triage-consolidate-2026-06-09.mjs --commit   # 真開 + 回寫 + archive
 */
import { readFileSync, writeFileSync, mkdirSync, existsSync } from 'node:fs';
import { dirname } from 'node:path';
import { execFileSync } from 'node:child_process';
import { buildIssue, triageNoteFor } from './lib/classify.mjs';
import { buildArchiveRecord, archiveRelPath } from './lib/archive.mjs';

const REPO = 'hansai-art/computex-md';
const COMMIT = process.argv.includes('--commit');
const rows = JSON.parse(readFileSync('/tmp/feedback-new.json', 'utf8'));

// ── partition ──────────────────────────────────────────────────────────────
const spaceRows = rows
  .filter((r) => r.article_slug === '國家太空中心' && r.type === 'content')
  .sort((a, b) => (a.created_at < b.created_at ? -1 : 1));
const otherRows = rows.filter(
  (r) => !(r.article_slug === '國家太空中心' && r.type === 'content'),
);

console.log(
  `[consolidate] space-corrections=${spaceRows.length} · other=${otherRows.length} · mode=${COMMIT ? 'COMMIT' : 'DRY-RUN'}`,
);

// ── build consolidated [Fact Check] issue for 國家太空中心 ─────────────────────
function ts(s) {
  return (s || '').slice(0, 16).replace('T', ' ');
}
const article = spaceRows[0];
const cleanUrl = 'https://computex.taiwanai.ngo/technology/國家太空中心';
const reader = article.display_name || '匿名讀者';

let body =
  `**哪篇文章 / Which article?**\n${article.article_title}\n🔗 ${cleanUrl}\n\n` +
  `本 issue 由站上回報自動彙整：同一位讀者（**${reader}**）對本篇做了 **${spaceRows.length} 處** section-by-section 勘誤/補充，` +
  `逐條 verbatim 收錄如下（每條附 feedback id provenance）。維護者請逐條查核（人工 gate）。\n\n---\n`;

spaceRows.forEach((r, i) => {
  body += `\n### 勘誤 ${i + 1}\n`;
  if (r.quote) {
    body += `\n**讀者選取的原文**\n> ${String(r.quote).replace(/\n/g, '\n> ')}\n`;
  }
  body += `\n**讀者指出 / What's wrong**\n${r.body}\n`;
  if (r.correct_info) {
    body += `\n**正確資訊 + 來源 / Correct info + source**\n${r.correct_info}\n`;
  }
  body += `\n<sub>feedback id: \`${r.id}\` · ${ts(r.created_at)}</sub>\n`;
});

body += `\n---\n> 🧬 由站上回報自動彙整轉入（twmd-feedback-triage / 2026-06-09 consolidation）· 回報者：${reader} · ${spaceRows.length} 筆 feedback 合併`;

const spaceIssue = {
  type: 'content',
  title: `[Fact Check] ${article.article_title}`,
  labels: ['needs-verification', 'from-feedback'],
  body,
};

// ── build bug + idea issues via lib ──────────────────────────────────────────
const plan = [
  { kind: 'consolidated', issue: spaceIssue, rows: spaceRows },
  ...otherRows.map((r) => ({
    kind: 'single',
    issue: buildIssue(r),
    rows: [r],
  })),
];

// ── execute ──────────────────────────────────────────────────────────────────
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
  const url = out.split('\n').pop().trim();
  const num = parseInt((url.match(/\/issues\/(\d+)/) || [])[1] || '0', 10);
  return { url, number: num };
}

async function writeBack(id, issue, note) {
  const url = process.env.SUPABASE_URL;
  const key = process.env.SUPABASE_SERVICE_KEY;
  const patch = {
    status: 'filed',
    triaged_at: new Date().toISOString(),
    issue_url: issue.url,
    issue_number: issue.number,
    triage_note: note,
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

function writeArchive(row, issue, note) {
  const rel = archiveRelPath(row);
  mkdirSync(dirname(rel), { recursive: true });
  if (!existsSync(rel)) {
    writeFileSync(
      rel,
      buildArchiveRecord(
        {
          ...row,
          status: 'filed',
          issue_url: issue.url,
          issue_number: issue.number,
        },
        note,
      ),
    );
  }
  return rel;
}

for (const p of plan) {
  console.log(`\n${p.kind.toUpperCase()} → ${p.issue.title}`);
  console.log(
    `  labels: ${p.issue.labels.join(', ')} · rows: ${p.rows.length}`,
  );
  if (!COMMIT) {
    console.log('  (dry-run; --commit to file)');
    continue;
  }
  const created = createIssue(p.issue);
  console.log(`  → ${created.url}`);
  for (const r of p.rows) {
    const note = triageNoteFor(r);
    await writeBack(r.id, created, note);
    const arch = writeArchive(r, created, note);
    console.log(`    ✓ writeback + 📁 ${arch} (${r.id.slice(0, 8)})`);
  }
}

console.log(
  `\n[consolidate] done · issues=${COMMIT ? plan.length : 0} (1 consolidated + ${otherRows.length} single) · rows-filed=${COMMIT ? rows.length : 0}`,
);
