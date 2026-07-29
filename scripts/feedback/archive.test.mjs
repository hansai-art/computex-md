/**
 * archive.test.mjs — git 主權層紀錄產生器測試。
 * 跑：node --test scripts/feedback/archive.test.mjs
 */
import { test } from 'node:test';
import assert from 'node:assert/strict';
import {
  ym,
  archiveRelPath,
  buildArchiveRecord,
  mergeComments,
} from './lib/archive.mjs';

const row = {
  id: 'aaaa-bbbb',
  created_at: '2026-06-01T09:12:00Z',
  display_name: '海邊的讀者',
  email: 'reader@example.com', // 故意放，確認 builder 不洩
  type: 'content',
  status: 'filed',
  page_kind: 'article',
  article_slug: '李安',
  article_title: '李安',
  lang: 'zh-TW',
  source_url: 'https://computex.taiwanai.ngo/people/李安#:~:text=1990',
  quote: '《臥虎藏龍》1990 年得獎',
  correct_info: '正確:2001。來源:https://oscars.org',
  triage_note: '已收到你的勘誤，已轉維護者查核。',
  issue_url: 'https://github.com/hansai-art/computex-md/issues/42',
  issue_number: 42,
};

test('ym extracts YYYY-MM', () => {
  assert.equal(ym('2026-06-01T09:12:00Z'), '2026-06');
  assert.equal(ym(''), '0000-00');
});

test('archiveRelPath: docs/feedback/archive/YYYY-MM/{id}.md', () => {
  assert.equal(
    archiveRelPath(row),
    'docs/feedback/archive/2026-06/aaaa-bbbb.md',
  );
});

test('buildArchiveRecord captures contributor/time/content + NEVER email', () => {
  const md = buildArchiveRecord(row, row.triage_note);
  assert.match(md, /contributor: "海邊的讀者"/);
  assert.match(md, /feedback_id: 'aaaa-bbbb'/);
  assert.match(md, /type: 'content'/);
  assert.match(md, /issue_number: 42/);
  assert.match(md, /回報內容/);
  assert.match(md, /選取的原文/);
  assert.match(md, /《臥虎藏龍》1990 年得獎/);
  assert.match(md, /系統初判/);
  assert.match(md, /## 溝通紀錄/);
  // 鐵律：email 永不進 git 紀錄
  assert.doesNotMatch(
    md,
    /[a-z0-9._%+-]+@[a-z0-9.-]+\.[a-z]{2,}/i,
    'email leaked',
  );
});

test('mergeComments appends new comments with markers', () => {
  const base = buildArchiveRecord(row, row.triage_note);
  const merged = mergeComments(base, [
    {
      id: 'maintainer-2026-06-01T10:00:00Z',
      author: 'maintainer',
      createdAt: '2026-06-01T10:00:00Z',
      body: '謝謝回報，已修正。',
    },
  ]);
  assert.match(merged, /<!-- comment:maintainer-2026-06-01T10:00:00Z -->/);
  assert.match(merged, /謝謝回報，已修正。/);
});

test('mergeComments dedupes on re-run (idempotent)', () => {
  const base = buildArchiveRecord(row, row.triage_note);
  const c = [
    { id: 'x-1', author: 'm', createdAt: '2026-06-01T10:00:00Z', body: 'hi' },
  ];
  const once = mergeComments(base, c);
  const twice = mergeComments(once, c);
  assert.equal(once, twice, 're-merging same comment should be a no-op');
  // 只出現一次
  assert.equal((twice.match(/<!-- comment:x-1 -->/g) || []).length, 1);
});

test('mergeComments no-op on empty', () => {
  const base = buildArchiveRecord(row, row.triage_note);
  assert.equal(mergeComments(base, []), base);
});
