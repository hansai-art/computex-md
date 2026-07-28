/**
 * Unit tests for lib/audit.js — Stage 3.5 Hallucination Audit detectors.
 *
 * Run with: cd cli && npx vitest run
 */

import { describe, it, expect } from 'vitest';
import fs from 'node:fs';
import path from 'node:path';
import { fileURLToPath } from 'node:url';
import {
  extractClaims,
  computeVerdict,
  AWARD_PATTERNS,
  NAME_NUMBER_PATTERNS,
  COCREATOR_PATTERNS,
} from '../src/lib/audit.js';

const __filename = fileURLToPath(import.meta.url);
const __dirname = path.dirname(__filename);

function loadFixture(name) {
  const p = path.join(__dirname, 'fixtures', name);
  const raw = fs.readFileSync(p, 'utf8');
  // strip frontmatter for body-only analysis
  const m = raw.match(/^---\s*\n[\s\S]*?\n---\s*\n([\s\S]*)$/);
  return m ? m[1] : raw;
}

describe('fixtures sanity', () => {
  it('audit-clean.md references 參考資料', () => {
    const body = loadFixture('audit-clean.md');
    expect(body).toMatch(/## 參考資料/);
  });

  it('audit-dirty.md seeds all 5 patterns', () => {
    const body = loadFixture('audit-dirty.md');
    expect(body).toMatch(/第 62 屆/);
    expect(body).toMatch(/Kasper/);
    expect(body).toMatch(/盧森堡/);
    expect(body).toMatch(/「這就是未來的樣子/);
    expect(body).toMatch(/共同創辦了某個基金會/);
  });
});

describe('extractClaims — dirty fixture', () => {
  const body = loadFixture('audit-dirty.md');
  const claims = extractClaims(body);

  it('flags award hallucinations', () => {
    expect(claims.award.length).toBeGreaterThanOrEqual(2);
    expect(claims.award.some((c) => c.text.includes('第 62 屆'))).toBe(true);
    // No footnotes in dirty → severity should be high
    expect(claims.award.every((c) => c.severity === 'high')).toBe(true);
  });

  it('flags English names + precise numbers', () => {
    expect(claims.nameNumber.length).toBeGreaterThanOrEqual(1);
    const hit = claims.nameNumber.find((c) => c.text.includes('Jediah'));
    expect(hit).toBeDefined();
    expect(hit.number).toBe('750');
    expect(hit.severity).toBe('high');
  });

  it('flags foreign city (盧森堡) without nearby footnote', () => {
    expect(claims.location.some((c) => c.text === '盧森堡')).toBe(true);
  });

  it('flags direct quotes as warn', () => {
    expect(claims.quote.length).toBeGreaterThanOrEqual(2);
    expect(claims.quote.some((c) => c.full.includes('這就是未來的樣子'))).toBe(
      true,
    );
    // no footnote nearby → warn
    expect(claims.quote.some((c) => c.severity === 'warn')).toBe(true);
  });

  it('flags co-creator omission (共同創辦了 without 跟/和/與)', () => {
    expect(claims.cocreator.length).toBeGreaterThanOrEqual(1);
    expect(
      claims.cocreator.some((c) => c.text.includes('共同創辦了某個基金會')),
    ).toBe(true);
  });
});

describe('extractClaims — clean fixture', () => {
  const body = loadFixture('audit-clean.md');
  const claims = extractClaims(body);

  it('no award flags', () => {
    expect(claims.award.length).toBe(0);
  });
  it('no name-number flags', () => {
    expect(claims.nameNumber.length).toBe(0);
  });
  it('no co-creator flags', () => {
    expect(claims.cocreator.length).toBe(0);
  });
});

describe('computeVerdict', () => {
  it('dirty fixture → fail verdict with HIGH flags', () => {
    const body = loadFixture('audit-dirty.md');
    const v = computeVerdict(extractClaims(body));
    expect(v.status).toBe('fail');
    expect(v.exitCode).toBe(1);
    expect(v.highFlags).toBeGreaterThanOrEqual(3);
  });

  it('clean fixture → pass verdict (may have zero warnings)', () => {
    const body = loadFixture('audit-clean.md');
    const v = computeVerdict(extractClaims(body));
    expect(v.exitCode).toBe(0);
    expect(v.highFlags).toBe(0);
  });

  it('strict mode turns warnings into failures', () => {
    const synthetic = {
      award: [],
      nameNumber: [],
      location: [{ line: 1, text: '巴黎', severity: 'med' }],
      quote: [],
      cocreator: [],
    };
    expect(computeVerdict(synthetic, false).status).toBe('warn');
    expect(computeVerdict(synthetic, true).status).toBe('fail');
  });
});

describe('co-creator false-positive suppression', () => {
  it('suppresses when a name appears before 共同創辦了 via 跟/和/與', () => {
    const body = '還跟林經堯共同創辦了 akaSwap 亞洲 NFT 平台。';
    const claims = extractClaims(body);
    expect(claims.cocreator.length).toBe(0);
  });

  it('does NOT suppress bare 共同創辦了', () => {
    const body = '同年他共同創辦了某個基金會，開始推廣議題。';
    const claims = extractClaims(body);
    expect(claims.cocreator.length).toBeGreaterThanOrEqual(1);
  });

  it('also handles 和 / 與 prefix', () => {
    const body1 = '他與黃豆泥共同創辦了 FAB DAO 組織';
    const body2 = '她和張三共同創辦了某協會';
    expect(extractClaims(body1).cocreator.length).toBe(0);
    expect(extractClaims(body2).cocreator.length).toBe(0);
  });
});

describe('raw pattern exports', () => {
  it('AWARD_PATTERNS matches canonical phrasings', () => {
    const samples = [
      '2024 年他獲得第 62 屆十大傑出青年',
      '第 37 屆金鐘獎最佳主持人',
      '2019 年榮獲某獎項',
    ];
    for (const s of samples) {
      const anyMatch = AWARD_PATTERNS.some((p) => {
        p.lastIndex = 0;
        return p.test(s);
      });
      expect(anyMatch).toBe(true);
    }
  });

  it('NAME_NUMBER_PATTERNS matches English name + minutes', () => {
    const p = NAME_NUMBER_PATTERNS[0];
    p.lastIndex = 0;
    expect(p.test('Jediah Coleman 在期末花了 750 分鐘')).toBe(true);
  });

  it('COCREATOR_PATTERNS matches bare 共同創辦了', () => {
    const p = COCREATOR_PATTERNS[0];
    p.lastIndex = 0;
    expect(p.test('他共同創辦了一個組織')).toBe(true);
  });
});
