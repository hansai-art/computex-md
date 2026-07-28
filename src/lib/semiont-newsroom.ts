/**
 * semiont-newsroom.ts — Parser for per-article "making-of" pages
 *
 * Reads production-line artifacts at build time:
 *   - reports/article-projection/{slug}.md   (投影藍圖：論點／骨架／減法)
 *   - reports/editorial-room/*.md            (編輯室席位審查：projection + prose-structure rounds)
 *
 * These files are hand-written by different agents across many sessions,
 * so headings/frontmatter shapes drift. Every extraction step is best-effort:
 * a missing section yields `null` (or an empty array), never a thrown error.
 * A malformed individual file must never break the whole build — see the
 * per-file try/catch in loadProjection()/loadReviews().
 */

import { readdir, readFile } from 'node:fs/promises';
import { resolve, join, basename } from 'node:path';
import matter from 'gray-matter';
import { marked } from 'marked';

// ── Types ──────────────────────────────────────────────

export interface ProjectionData {
  article?: string;
  researchReport?: string;
  spineType?: string;
  date?: string;
  /** Rendered HTML of the "## ...論點..." section. */
  thesisHtml: string | null;
  /** Rendered HTML of the "## ...骨架..." section. */
  skeletonHtml: string | null;
  /** Rendered HTML of the "## ...減法..." section. */
  subtractionHtml: string | null;
}

export interface ReviewSeat {
  /** Seat name as written in the H3 heading, e.g. "結構主編". */
  name: string;
  /** Raw verdict text, e.g. "pass" or "revise（序：機制在身世前）". */
  verdict: string;
  /** Rendered HTML of the seat's findings/evidence body (verdict line stripped). */
  findingsHtml: string;
}

export interface ReviewDebateItem {
  challenge: string;
  defense: string;
  ruling: string;
}

export interface ReviewData {
  /** Repo-relative path to the source file, for footer links. */
  file: string;
  room: string;
  date: string;
  overall: string;
  rounds: string;
  seats: ReviewSeat[];
  mustFix: string[];
  debate: ReviewDebateItem[] | null;
  rulingHtml: string | null;
}

export interface MakingOf {
  slug: string;
  /** Repo-relative path to the projection file, if one exists. */
  projectionFile: string | null;
  projection: ProjectionData | null;
  reviews: ReviewData[];
}

// ── Paths ──────────────────────────────────────────────

const PROJECTION_DIR = resolve(process.cwd(), 'reports/article-projection');
const ROOM_DIR = resolve(process.cwd(), 'reports/editorial-room');

const ROOM_ORDER: Record<string, number> = {
  projection: 1,
  'prose-structure': 2,
  chief: 3,
};

// ── Markdown rendering (mirrors src/lib/semiont-diary.ts conventions) ──

function createRenderer(): marked.Renderer {
  const renderer = new marked.Renderer();

  renderer.heading = ({ text, depth }) => {
    const id = text
      .toLowerCase()
      .replace(/\s+/g, '-')
      .replace(/[^\w一-鿿-]/g, '')
      .slice(0, 60);
    return `<h${depth} id="${id}">${text}</h${depth}>\n`;
  };

  renderer.link = ({ href, title, text }) => {
    const isExternal =
      href?.startsWith('http://') || href?.startsWith('https://');
    const titleAttr = title ? ` title="${title}"` : '';
    const targetAttr = isExternal
      ? ' target="_blank" rel="noopener noreferrer"'
      : '';
    return `<a href="${href}"${titleAttr}${targetAttr}>${text}</a>`;
  };

  return renderer;
}

const renderer = createRenderer();

function escapeHtml(s: string): string {
  return s.replace(/&/g, '&amp;').replace(/</g, '&lt;').replace(/>/g, '&gt;');
}

function renderMarkdown(md: string | undefined | null): string {
  if (!md || !md.trim()) return '';
  try {
    return marked.parse(md, { renderer, breaks: true }) as string;
  } catch (err) {
    console.error('[semiont-newsroom] markdown render failed:', err);
    return `<p>${escapeHtml(md)}</p>`;
  }
}

function renderInline(md: string | undefined | null): string {
  if (!md || !md.trim()) return '';
  try {
    return marked.parseInline(md, { renderer }) as string;
  } catch (err) {
    console.error('[semiont-newsroom] inline markdown render failed:', err);
    return escapeHtml(md);
  }
}

// ── Frontmatter helpers ────────────────────────────────

function toDateStr(v: unknown): string | undefined {
  if (v instanceof Date) return v.toISOString().slice(0, 10);
  if (typeof v === 'string') return v;
  if (typeof v === 'number') return String(v);
  return undefined;
}

function toStr(v: unknown): string | undefined {
  if (typeof v === 'string') return v;
  if (typeof v === 'number') return String(v);
  return undefined;
}

// ── Section splitting (H2 / H3 based) ──────────────────

interface Section {
  heading: string;
  body: string;
}

/** Split markdown into sections keyed by top-level "## " headings (exactly 2 hashes). */
function splitSections(markdown: string, hashes: 2 | 3): Section[] {
  const marker = '#'.repeat(hashes);
  const re = new RegExp(`^${marker}(?!#)\\s+(.*)$`);
  const lines = markdown.split('\n');
  const sections: Section[] = [];
  let currentHeading: string | null = null;
  let buffer: string[] = [];

  for (const line of lines) {
    const m = line.match(re);
    if (m) {
      if (currentHeading !== null) {
        sections.push({
          heading: currentHeading,
          body: buffer.join('\n').trim(),
        });
      }
      currentHeading = m[1].trim();
      buffer = [];
    } else {
      buffer.push(line);
    }
  }
  if (currentHeading !== null) {
    sections.push({ heading: currentHeading, body: buffer.join('\n').trim() });
  }
  return sections;
}

function findFirstSection(
  sections: Section[],
  pattern: RegExp,
): Section | null {
  for (const s of sections) if (pattern.test(s.heading)) return s;
  return null;
}

function findLastSection(sections: Section[], pattern: RegExp): Section | null {
  let found: Section | null = null;
  for (const s of sections) if (pattern.test(s.heading)) found = s;
  return found;
}

// ── Seat parsing (## 各席 → ### {席名}) ─────────────────

function parseSeats(body: string): ReviewSeat[] {
  const subsections = splitSections(body, 3);
  return subsections.map(({ heading, body: seatBody }) => {
    const verdictMatch = seatBody.match(/^-\s*verdict:\s*(.+)$/im);
    const verdict = verdictMatch ? verdictMatch[1].trim() : '';
    const cleaned = seatBody.replace(/^-\s*verdict:.*$/im, '').trim();
    return {
      name: heading,
      verdict,
      findingsHtml: renderMarkdown(cleaned),
    };
  });
}

// ── 必改清單 parsing (numbered / checkbox list → string[] of inline HTML) ──

function parseMustFix(body: string): string[] {
  const trimmed = body.trim();
  if (!trimmed) return [];
  if (/^[（(]\s*(無|不擋|N\/?A)/i.test(trimmed)) return [];

  const lines = trimmed.split('\n');
  const items: string[] = [];
  let buffer: string[] = [];

  const flush = () => {
    if (buffer.length) {
      const text = buffer.join(' ').trim();
      if (text) items.push(renderInline(text));
      buffer = [];
    }
  };

  for (const line of lines) {
    const numbered = line.match(/^\s*\d+\.\s*(?:\[[ xX]\]\s*)?(.+)$/);
    const bulleted =
      !numbered && line.match(/^\s*[-*]\s*(?:\[[ xX]\]\s*)?(.+)$/);
    if (numbered) {
      flush();
      buffer.push(numbered[1]);
    } else if (bulleted) {
      flush();
      buffer.push(bulleted[1]);
    } else if (line.trim() === '') {
      flush();
    } else if (buffer.length) {
      buffer.push(line.trim());
    }
  }
  flush();
  return items;
}

// ── 攻防 parsing (best-effort; no observed fixture as of 2026-07-16) ────

function extractLabeledField(
  text: string,
  labelPattern: string,
): string | null {
  const re = new RegExp(
    `^[-*]?\\s*\\**(?:${labelPattern})\\**\\s*[:：]\\s*(.*)$`,
    'im',
  );
  const m = text.match(re);
  return m ? renderInline(m[1].trim()) : null;
}

function parseDebate(body: string): ReviewDebateItem[] | null {
  if (!body.trim()) return null;
  const subsections = splitSections(body, 3);
  const groups = subsections.length ? subsections.map((s) => s.body) : [body];
  const items: ReviewDebateItem[] = [];

  for (const group of groups) {
    const challenge = extractLabeledField(group, 'challenge|質疑|挑戰');
    const defense = extractLabeledField(group, 'defense|回應|辯護|防守');
    const ruling = extractLabeledField(group, 'ruling|裁決|判決');
    if (challenge || defense || ruling) {
      items.push({
        challenge: challenge ?? '',
        defense: defense ?? '',
        ruling: ruling ?? '',
      });
    }
  }
  return items.length ? items : null;
}

// ── Projection loader ───────────────────────────────────

async function loadProjection(slug: string): Promise<ProjectionData | null> {
  const filePath = join(PROJECTION_DIR, `${slug}.md`);
  let raw: string;
  try {
    raw = await readFile(filePath, 'utf-8');
  } catch {
    return null;
  }

  try {
    const { data, content } = matter(raw);
    const sections = splitSections(content, 2);

    const thesisSection = findFirstSection(sections, /論點/);
    const skeletonSection = findFirstSection(sections, /骨架/);
    const subtractionSection = findFirstSection(sections, /減法/);

    return {
      article: toStr(data.article),
      researchReport: toStr(data.researchReport),
      spineType: toStr(data.spine_type),
      date: toDateStr(data.date),
      thesisHtml: thesisSection ? renderMarkdown(thesisSection.body) : null,
      skeletonHtml: skeletonSection
        ? renderMarkdown(skeletonSection.body)
        : null,
      subtractionHtml: subtractionSection
        ? renderMarkdown(subtractionSection.body)
        : null,
    };
  } catch (err) {
    console.error(
      `[semiont-newsroom] failed to parse projection for "${slug}":`,
      err,
    );
    return null;
  }
}

// ── Review loader ────────────────────────────────────────

function stripReviewSuffix(name: string): string {
  return name
    .replace(/-projection-review(-r\d+)?$/i, '')
    .replace(/-prose-structure-review(-r\d+)?$/i, '')
    .replace(/-chief-review(-r\d+)?$/i, '');
}

function isSkippedRoomFile(filename: string): boolean {
  return (
    filename.startsWith('_') ||
    filename.startsWith('dogfood-') ||
    filename.startsWith('full-cycle')
  );
}

async function deriveRoomSlug(
  filename: string,
  data: Record<string, unknown>,
): Promise<string | null> {
  const fmSlug = toStr(data.slug);
  if (fmSlug && fmSlug.trim()) return fmSlug.trim().normalize('NFC');
  const stem = basename(filename, '.md');
  const stripped = stripReviewSuffix(stem);
  // 無 frontmatter slug 且檔名不含已知 review 尾綴（如 closeout 類收尾報告）：
  // 不自成 making-of 頁（避免孤兒頁）；有 article: 指標就折回母文章 slug。
  if (stripped === stem) {
    const art = toStr(data.article);
    const m = art?.match(/knowledge\/[^/]+\/(.+)\.md$/);
    return m ? m[1].normalize('NFC') : null;
  }
  return stripped.normalize('NFC');
}

function parseReviewFile(
  file: string,
  data: Record<string, unknown>,
  content: string,
): ReviewData {
  const sections = splitSections(content, 2);

  const seatsSection = findFirstSection(sections, /各席/);
  const seats = seatsSection ? parseSeats(seatsSection.body) : [];

  const mustFixSection = findLastSection(sections, /必改清單/);
  const mustFix = mustFixSection ? parseMustFix(mustFixSection.body) : [];

  const debateSection = findFirstSection(sections, /攻防/);
  const debate = debateSection ? parseDebate(debateSection.body) : null;

  const rulingSection = findLastSection(sections, /主編裁決/);
  const rulingHtml = rulingSection ? renderMarkdown(rulingSection.body) : null;

  return {
    file: `reports/editorial-room/${file}`,
    room: toStr(data.room) ?? '',
    date: toDateStr(data.date) ?? '',
    overall: toStr(data.overall) ?? '',
    rounds: toStr(data.rounds) ?? '',
    seats,
    mustFix,
    debate,
    rulingHtml,
  };
}

async function loadReviews(slug: string): Promise<ReviewData[]> {
  const normalizedSlug = slug.normalize('NFC');
  let files: string[] = [];
  try {
    files = await readdir(ROOM_DIR);
  } catch {
    return [];
  }

  const candidates = files
    .filter((f) => f.endsWith('.md'))
    .map((f) => f.normalize('NFC'))
    .filter((f) => !isSkippedRoomFile(f));

  const matched: {
    file: string;
    rev: number;
    roomOrder: number;
    review: ReviewData;
  }[] = [];

  for (const file of candidates) {
    try {
      const raw = await readFile(join(ROOM_DIR, file), 'utf-8');
      const { data, content } = matter(raw);
      const fileSlug = await deriveRoomSlug(file, data);
      if (fileSlug !== normalizedSlug) continue;

      const review = parseReviewFile(file, data, content);
      const revMatch = file.match(/-r(\d+)\.md$/i);
      const rev = revMatch ? parseInt(revMatch[1], 10) : 1;
      const roomOrder = ROOM_ORDER[toStr(data.room) ?? ''] ?? 50;
      matched.push({ file, rev, roomOrder, review });
    } catch (err) {
      console.error(
        `[semiont-newsroom] failed to parse review file "${file}":`,
        err,
      );
    }
  }

  matched.sort(
    (a, b) =>
      a.roomOrder - b.roomOrder ||
      a.rev - b.rev ||
      a.file.localeCompare(b.file),
  );
  return matched.map((m) => m.review);
}

// ── Public API ─────────────────────────────────────────

export async function getMakingOfSlugs(): Promise<string[]> {
  const slugs = new Set<string>();

  let projFiles: string[] = [];
  try {
    projFiles = await readdir(PROJECTION_DIR);
  } catch {
    projFiles = [];
  }
  for (const f of projFiles) {
    if (!f.endsWith('.md')) continue;
    const name = f.normalize('NFC');
    if (name.startsWith('_')) continue;
    slugs.add(basename(name, '.md'));
  }

  let roomFiles: string[] = [];
  try {
    roomFiles = await readdir(ROOM_DIR);
  } catch {
    roomFiles = [];
  }
  for (const f of roomFiles) {
    if (!f.endsWith('.md')) continue;
    const name = f.normalize('NFC');
    if (isSkippedRoomFile(name)) continue;
    try {
      const raw = await readFile(join(ROOM_DIR, name), 'utf-8');
      const { data } = matter(raw);
      const slug = await deriveRoomSlug(name, data);
      if (slug) slugs.add(slug);
    } catch (err) {
      console.error(
        `[semiont-newsroom] failed to derive slug for "${name}":`,
        err,
      );
    }
  }

  return Array.from(slugs).sort((a, b) => a.localeCompare(b, 'zh-Hant'));
}

export async function getMakingOf(slug: string): Promise<MakingOf> {
  const normalizedSlug = slug.normalize('NFC');

  let projection: ProjectionData | null = null;
  try {
    projection = await loadProjection(normalizedSlug);
  } catch (err) {
    console.error(
      `[semiont-newsroom] projection load threw for "${normalizedSlug}":`,
      err,
    );
  }

  let reviews: ReviewData[] = [];
  try {
    reviews = await loadReviews(normalizedSlug);
  } catch (err) {
    console.error(
      `[semiont-newsroom] reviews load threw for "${normalizedSlug}":`,
      err,
    );
  }

  return {
    slug: normalizedSlug,
    projectionFile: projection
      ? `reports/article-projection/${normalizedSlug}.md`
      : null,
    projection,
    reviews,
  };
}
