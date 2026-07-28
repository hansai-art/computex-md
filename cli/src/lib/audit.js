/**
 * lib/audit.js — Stage 3.5 Hallucination Audit detectors
 *
 * Pure functions for pattern detection. Extracted from commands/audit.js
 * so vitest can import and unit-test them directly.
 *
 * Reference: MANIFESTO §10 幻覺鐵律 + REWRITE-PIPELINE Stage 3.5.
 * 5 hallucination patterns:
 *   1. Award hallucination
 *   2. Names + precise numbers
 *   3. Location displacement
 *   4. Fabricated direct quotes
 *   5. Co-creator omission
 */

export const AWARD_PATTERNS = [
  // 第 N 屆 XX 獎 / 第 N 屆 XX (十大傑出青年 style — no 獎 suffix)
  /第\s*(?:\d+|[一二三四五六七八九十百]+)\s*屆[^。\n]{0,30}?(?:獎|傑出青年|名人堂|殿堂|得主|入圍)/g,
  /第\s*(?:\d+|[一二三四五六七八九十百]+)\s*次[^。\n]{0,30}?獎/g,
  // YYYY 年 ... 獲 ... 獎 / 傑出青年 / 得主
  /\d{4}\s*年[^。\n]{0,25}?(?:獲|榮獲|得獎|首獎|入圍|拿下)[^。\n]{0,30}?(?:獎|傑出青年|名人堂|殿堂|得主)/g,
];

export const NAME_NUMBER_PATTERNS = [
  // English name + (within one sentence, allowing Chinese comma) + NNN 分鐘/mins
  // Use [\s\S] to allow 「，」「、」while capping total distance.
  /([A-Z][a-z]+(?:\s[A-Z][a-z]+)*)[\s\S]{1,80}?(\d{2,4})\s*(?:分鐘|mins?|minutes)/g,
  // English name + (跟了/陪了/花了) + N 學期/週/次 (allow Chinese numerals 兩/三/四 etc.)
  /([A-Z][a-z]+)[\s\S]{0,40}?(?:跟了|陪了|花了)[\s\S]{0,15}?(\d+|[一二三四五六七八九十兩])\s*(?:學期|週|次)/g,
];

export const FOREIGN_CITIES = [
  '盧森堡',
  '米蘭',
  '巴黎',
  '柏林',
  '倫敦',
  '紐約',
  '東京',
  '首爾',
  '阿姆斯特丹',
  '斯德哥爾摩',
  '維也納',
  '蘇黎世',
  '布魯塞爾',
  '哥本哈根',
  '赫爾辛基',
  '布拉格',
  '華沙',
  '雅典',
  '羅馬',
];

export const QUOTE_PATTERNS = [/「[^」]{15,200}」/g];

export const COCREATOR_PATTERNS = [
  /共同創辦了\s*(?!.*?(?:和|與|及))[^，。\n]{0,40}/g,
  /共同創立了\s*(?!.*?(?:和|與|及))[^，。\n]{0,40}/g,
  /聯合發起了\s*(?!.*?(?:和|與|及))[^，。\n]{0,40}/g,
];

/** Line number (1-indexed) for a byte offset in body. */
export function getLineNumber(body, matchIndex) {
  return body.slice(0, matchIndex).split('\n').length;
}

/** True if body has [^N] footnote within `window` chars around matchIndex. */
export function hasNearbyFootnote(body, matchIndex, windowSize = 200) {
  const start = Math.max(0, matchIndex - windowSize);
  const end = Math.min(body.length, matchIndex + windowSize);
  return /\[\^[\w-]+\]/.test(body.slice(start, end));
}

/**
 * Extract all potentially hallucinated claims from an article body.
 * Returns a grouped claim object keyed by pattern type.
 */
export function extractClaims(body) {
  const claims = {
    award: [],
    nameNumber: [],
    location: [],
    quote: [],
    cocreator: [],
  };

  for (const pattern of AWARD_PATTERNS) {
    pattern.lastIndex = 0;
    let m;
    while ((m = pattern.exec(body)) !== null) {
      const line = getLineNumber(body, m.index);
      const hasFootnote = hasNearbyFootnote(body, m.index);
      claims.award.push({
        line,
        text: m[0].trim(),
        hasFootnote,
        severity: hasFootnote ? 'warn' : 'high',
      });
    }
  }

  for (const pattern of NAME_NUMBER_PATTERNS) {
    pattern.lastIndex = 0;
    let m;
    while ((m = pattern.exec(body)) !== null) {
      const line = getLineNumber(body, m.index);
      const hasFootnote = hasNearbyFootnote(body, m.index);
      claims.nameNumber.push({
        line,
        text: m[0].trim().slice(0, 100),
        name: m[1],
        number: m[2],
        hasFootnote,
        severity: hasFootnote ? 'warn' : 'high',
      });
    }
  }

  for (const city of FOREIGN_CITIES) {
    const regex = new RegExp(city, 'g');
    let m;
    while ((m = regex.exec(body)) !== null) {
      const line = getLineNumber(body, m.index);
      const hasFootnote = hasNearbyFootnote(body, m.index, 150);
      if (!hasFootnote) {
        claims.location.push({
          line,
          text: city,
          context: body.slice(Math.max(0, m.index - 30), m.index + 30).trim(),
          severity: 'med',
        });
      }
    }
  }

  for (const pattern of QUOTE_PATTERNS) {
    pattern.lastIndex = 0;
    let m;
    while ((m = pattern.exec(body)) !== null) {
      const line = getLineNumber(body, m.index);
      const hasFootnote = hasNearbyFootnote(body, m.index, 100);
      claims.quote.push({
        line,
        text: m[0].slice(0, 60) + (m[0].length > 60 ? '...」' : ''),
        full: m[0],
        hasFootnote,
        severity: hasFootnote ? 'info' : 'warn',
      });
    }
  }

  for (const pattern of COCREATOR_PATTERNS) {
    pattern.lastIndex = 0;
    let m;
    while ((m = pattern.exec(body)) !== null) {
      const line = getLineNumber(body, m.index);
      // Suppress if name appears before 「共同創辦了」via 「跟/和/與/及」
      const contextBefore = body.slice(Math.max(0, m.index - 40), m.index);
      if (/(?:跟|和|與|及)[\u4e00-\u9fff\w]{1,15}$/.test(contextBefore)) {
        continue;
      }
      claims.cocreator.push({
        line,
        text: m[0].trim(),
        severity: 'high',
      });
    }
  }

  return claims;
}

/** Compute pass/warn/fail verdict from claim counts. */
export function computeVerdict(claims, strict = false) {
  const highFlags =
    claims.award.filter((c) => c.severity === 'high').length +
    claims.nameNumber.filter((c) => c.severity === 'high').length +
    claims.cocreator.filter((c) => c.severity === 'high').length;
  const warnFlags =
    claims.award.filter((c) => c.severity === 'warn').length +
    claims.nameNumber.filter((c) => c.severity === 'warn').length +
    claims.quote.filter((c) => c.severity === 'warn').length +
    claims.location.length;

  if (highFlags > 0) {
    return {
      status: 'fail',
      label: '❌ HIGH-severity flags detected — do not merge',
      exitCode: 1,
      highFlags,
      warnFlags,
    };
  }
  if (strict && warnFlags > 0) {
    return {
      status: 'fail',
      label: '⚠️  Strict mode: warnings treated as failures',
      exitCode: 1,
      highFlags,
      warnFlags,
    };
  }
  if (warnFlags > 0) {
    return {
      status: 'warn',
      label: '⚠️  Warnings — review before merge',
      exitCode: 0,
      highFlags,
      warnFlags,
    };
  }
  return {
    status: 'pass',
    label: '✅ No hallucination patterns detected',
    exitCode: 0,
    highFlags,
    warnFlags,
  };
}
