/**
 * archive.mjs — 把讀者回報 + 溝通紀錄落進 git repo（主權層，純函式）。
 *
 * 為什麼：feedback 的 live 資料在外掛 BaaS（Supabase），但 canonical 紀錄要進 git
 * （per MANIFESTO 知識在 git 不在黑箱 / 分散式不可殺滅）。BaaS 哪天死了，所有回報 +
 * 維護者溝通仍完整留在 repo 的 markdown 裡，可 diff、可匯出、可 grep。
 *
 * PII 鐵律：只存 display_name（暱稱/回退名，= 已公開在 issue 的），**永遠不存 email**。
 *
 * 純函式（無 IO）；triage.mjs 負責讀寫檔案。
 *   - archiveRelPath(row)              → docs/feedback/archive/YYYY-MM/{id}.md
 *   - buildArchiveRecord(row, note)    → 初始 markdown（含 frontmatter + 內容 + 空溝通紀錄）
 *   - mergeComments(content, comments) → 把 issue 新留言 append 進 §溝通紀錄（去重）
 *
 * ⚠️ source_url / body / quote / correct_info 是讀者欄位,可能夾帶 OAuth token / JWT
 *    （登入讀者貼網址列的 Supabase auth fragment）。落 git 前都過 scrubSecrets()
 *    （同 classify.mjs issue body 第二道 PII 閘）。觸發 2026-06-16 feedback 8f2f8908。
 */

import { scrubSecrets } from './classify.mjs';

function fm(v) {
  if (v === null || v === undefined || v === '') return '';
  return String(v).replace(/\n/g, ' ').replace(/"/g, "'");
}

export function ym(createdAt) {
  const s = String(createdAt || '');
  const m = s.match(/^(\d{4})-(\d{2})/);
  return m ? `${m[1]}-${m[2]}` : '0000-00';
}

export function archiveRelPath(row) {
  return `docs/feedback/archive/${ym(row.created_at)}/${row.id}.md`;
}

const COMMENTS_HEADING = '## 溝通紀錄';

export function buildArchiveRecord(row, note) {
  const who = row.display_name || '匿名讀者';
  const target =
    row.article_title || row.article_slug || row.page_kind || '(站上)';
  const front = [
    '---',
    `feedback_id: '${fm(row.id)}'`,
    `created_at: '${fm(row.created_at)}'`,
    `contributor: "${fm(who)}"`, // display_name only — 無 email
    `type: '${fm(row.type)}'`,
    `status: '${fm(row.status || 'new')}'`,
    `page_kind: '${fm(row.page_kind)}'`,
    `article_slug: "${fm(row.article_slug)}"`,
    `lang: '${fm(row.lang)}'`,
    `source_url: "${fm(scrubSecrets(row.source_url))}"`,
    `issue_url: "${fm(row.issue_url)}"`,
    `issue_number: ${row.issue_number || 'null'}`,
    '---',
  ].join('\n');

  const parts = [front, '', `# Feedback — ${row.type} · ${target}`, ''];
  parts.push(`**回報者**：${who}`, `**時間**：${row.created_at || ''}`, '');
  parts.push('**回報內容**', scrubSecrets(row.body) || '', '');
  if (row.quote) {
    parts.push(
      '**選取的原文**',
      `> ${scrubSecrets(String(row.quote)).replace(/\n/g, '\n> ')}`,
      '',
    );
  }
  if (row.correct_info) {
    parts.push('**正確資訊 + 來源**', scrubSecrets(row.correct_info), '');
  }
  if (note || row.triage_note) {
    parts.push('**系統初判**', note || row.triage_note, '');
  }
  if (row.issue_url) {
    parts.push(`**GitHub issue**：${row.issue_url}`, '');
  }
  parts.push(COMMENTS_HEADING, '');
  parts.push('<!-- issue 留言由 twmd-feedback-triage 定期 sync 到這裡 -->', '');
  return parts.join('\n');
}

/**
 * 把 issue 新留言 append 進 §溝通紀錄。comments: [{id, author, createdAt, body}]。
 * 用 `<!-- comment:<id> -->` marker 去重，re-run 不重複。
 */
export function mergeComments(content, comments) {
  if (!comments || !comments.length) return content;
  const existing = new Set(
    [...content.matchAll(/<!-- comment:([^\s]+) -->/g)].map((m) => m[1]),
  );
  const fresh = comments.filter((c) => c && !existing.has(String(c.id)));
  if (!fresh.length) return content;

  const blocks = fresh
    .map((c) => {
      const when = (c.createdAt || '').slice(0, 16).replace('T', ' ');
      return `<!-- comment:${c.id} -->\n**${c.author || '?'}**${when ? ` · ${when}` : ''}\n\n${(c.body || '').trim()}\n`;
    })
    .join('\n');

  const idx = content.indexOf(COMMENTS_HEADING);
  if (idx === -1) {
    return `${content.trimEnd()}\n\n${COMMENTS_HEADING}\n\n${blocks}\n`;
  }
  // 插在 heading 區塊尾端（append）。
  return `${content.trimEnd()}\n\n${blocks}\n`;
}
