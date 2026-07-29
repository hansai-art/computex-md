/**
 * organismText.ts：/organism 的純文字雙胞胎
 *
 * /organism 的主角是一個 WebGL 線框。AI 爬蟲不執行 JS，那一頁對它們**全黑**。
 * 這一頁又剛好是整個站論點最集中的地方（「每個視覺變數都追得回一個真實欄位」），
 * 讓它對 LLM 隱形等於把最重要的一段話關在畫布裡。
 *
 * 所以 /organism.md 與 /api/organism.json 不是附屬品，是這一頁能不能被引用的
 * 前提。動 organism.template.astro 的數字時 MUST 同步動這裡：兩邊講的話不一樣
 * 的時候，被引用的一定是這一份。
 *
 * 兩份都由 src/data/organism.json 產生，跟頁面同一個資料源，不另外算。
 */
import organism from '../data/organism.json';

type Signal = {
  key: string;
  zh: string;
  en: string;
  drives_zh: string;
  drives_en: string;
  value: number | null;
  fallback?: number;
  live: boolean;
  source_zh: string;
  source_en: string;
};

type Criterion = { key: string; zh: string; en: string; layer: string };

type Cell = {
  slug: string;
  name: string;
  hall: number;
  booth: string;
  area: string;
  editions: number;
  first_year: number;
  last_year: number;
  vitality: number;
  have: string[];
  missing: string[];
  last_verified: string | null;
};

const { summary, criteria, cells, heartbeat, shape } = organism as unknown as {
  summary: Record<string, number | number[] | string[]>;
  criteria: Criterion[];
  cells: Cell[];
  heartbeat: { date: string; commits: number }[];
  shape: Record<string, Signal>;
};

const signals = Object.values(shape);
const num = (n: unknown) => Number(n ?? 0);

/** .md 與 .json 共用的「已達成幾個條目」統計 */
function perCriterion() {
  return criteria.map((c) => ({
    ...c,
    count: cells.filter((cell) => cell.have.includes(c.key)).length,
  }));
}

export function buildOrganismJson() {
  return {
    _about:
      'COMPUTEX.md organism readout. Every visual variable on /organism maps to one field here; nothing on that page is decorative. Source: scripts/tools/generate-organism.py',
    _page: 'https://computex.taiwanai.ngo/organism',
    _markdown: 'https://computex.taiwanai.ngo/organism.md',
    _license: 'CC BY-SA 4.0',
    summary,
    shape,
    criteria: perCriterion(),
    heartbeat,
    cells,
  };
}

export function buildOrganismMarkdown(lang: 'zh-TW' | 'en'): string {
  const zh = lang === 'zh-TW';
  const per = perCriterion();
  const facts = per.filter((c) => c.layer === 'fact');
  const curation = per.filter((c) => c.layer === 'curation');
  const totalCommits = heartbeat.reduce((n, d) => n + d.commits, 0);
  const cellCount = num(summary.cells);
  const vitality = num(summary.vitality);

  const L: string[] = [];
  const p = (s = '') => L.push(s);

  if (zh) {
    p('# COMPUTEX.md 生命體');
    p();
    p(
      `此刻狀態：${cellCount} 個條目，整體生命力 ${vitality}%。這是 https://computex.taiwanai.ngo/organism 的純文字版本，數字與該頁同一個資料源。`,
    );
    p();
    p(
      '這個站不是一個資料收集網站，是一個會長大的檔案庫：有人補進一項可查證的事實，它就長大一點。/organism 上那個線框不是插圖，它的每一個視覺變數都對應下面表格裡的一個真實欄位。',
    );
    p();
    p('## 形狀是怎麼算出來的');
    p();
    p('| 指標 | 決定 | 目前值 | 狀態 | 來源 |');
    p('| --- | --- | --- | --- | --- |');
    for (const s of signals) {
      const val = s.live ? String(s.value) : `未接（暫用 ${s.fallback ?? 0}）`;
      p(
        `| ${s.zh} | ${s.drives_zh} | ${val} | ${s.live ? '已接' : '未接'} | ${s.source_zh} |`,
      );
    }
    p();
    p(
      `六項裡有 ${signals.filter((s) => s.live).length} 項已接上資料源。還沒接上的兩項就照實標「未接」，形狀用一個寫死的暫用值撐著，不會補一個看起來合理的假數字。這一頁的整個論點就是每個數字都追得回一個欄位，補假數字等於當場推翻它自己。`,
    );
    p();
    p('## 生命力怎麼算（十項機械計分，演算法公開）');
    p();
    p(
      `每個條目跑十項檢查，答對幾項就是幾分。分成兩層：**事實層**（廠商可自行 PR 修改，每項宣稱要能被第三方查證）與**策展層**（只有中立編輯能寫：這家在產業裡的位置、跟誰競爭、今年跟去年比變了什麼）。文案吹捧一個字都不加分。`,
    );
    p();
    p('### 事實層');
    p();
    p('| 檢查項 | 已達成 |');
    p('| --- | --- |');
    for (const c of facts) p(`| ${c.zh} | ${c.count} / ${cellCount} |`);
    p();
    p('### 策展層');
    p();
    p('| 檢查項 | 已達成 |');
    p('| --- | --- |');
    for (const c of curation) p(`| ${c.zh} | ${c.count} / ${cellCount} |`);
    p();
    p(
      `整片看起來是半亮的，因為它就是半亮的：事實層已填 ${num(summary.facts_filled)} / ${num(summary.facts_possible)} 格，策展層全站 ${num(summary.curated)} 格。這不是要修的 bug，這正是這一頁要講的話：它被餵了事實，還沒有人替它想過。任何讓分數好看一點的加權都是對讀者說謊。`,
    );
    p();
    p('## 心跳');
    p();
    p(
      `目前有紀錄的活躍日 ${heartbeat.length} 天，累計 ${totalCommits} 次 commit。心跳來自真實的 git 節奏，不是動畫。`,
    );
    p();
    p('## 最需要補資料的條目');
    p();
    p('| 條目 | 攤位 | 屆數 | 生命力 | 缺 |');
    p('| --- | --- | --- | --- | --- |');
    for (const c of [...cells]
      .sort(
        (a, b) =>
          b.missing.length - a.missing.length || b.editions - a.editions,
      )
      .slice(0, 12)) {
      p(
        `| ${c.name} | ${c.booth} | ${c.editions} | ${c.vitality}% | ${c.missing.length} 項 |`,
      );
    }
    p();
    p('## 完整資料');
    p();
    p(
      '全部 ' +
        cellCount +
        ' 個條目的逐項分數、攤位座標與缺漏清單：https://computex.taiwanai.ngo/api/organism.json（CC BY-SA 4.0，可自由取用，請標明來源）。',
    );
    p();
    p('---');
    p();
    p(
      '本頁由 scripts/tools/generate-organism.py 產生。授權 CC BY-SA 4.0。COMPUTEX.md 是台灣 AI 硬體產業的活體年鑑，taiwan.md 的衍生專案。',
    );
  } else {
    p('# The COMPUTEX.md Organism');
    p();
    p(
      `Current state: ${cellCount} entries at ${vitality}% overall vitality. This is the plain-text twin of https://computex.taiwanai.ngo/en/organism and reads from the same data source.`,
    );
    p();
    p(
      'This site is not a collection of pages, it is an archive that grows: add one verifiable fact and it gets a little bigger. The wireframe on /organism is not an illustration. Every visual variable maps to a real field in the table below.',
    );
    p();
    p('## How the shape is computed');
    p();
    p('| Metric | Drives | Current value | Status | Source |');
    p('| --- | --- | --- | --- | --- |');
    for (const s of signals) {
      const val = s.live
        ? String(s.value)
        : `not wired (placeholder ${s.fallback ?? 0})`;
      p(
        `| ${s.en} | ${s.drives_en} | ${val} | ${s.live ? 'live' : 'not wired'} | ${s.source_en} |`,
      );
    }
    p();
    p(
      `${signals.filter((s) => s.live).length} of six metrics are wired to a real source. The other two are labelled "not wired" on the page and use a hardcoded placeholder to hold the shape. They are never filled with a plausible-looking invented number: the entire argument of this page is that every value traces back to a field, and a fabricated one would refute it on the spot.`,
    );
    p();
    p('## How vitality is scored (ten mechanical checks, algorithm public)');
    p();
    p(
      'Each entry runs ten checks; the score is how many it passes. Two layers: the **fact layer** (vendors may edit it directly by pull request, every claim must be third-party verifiable) and the **curation layer** (neutral editors only: where this company sits in the industry, who it competes with, what changed since last year). Marketing copy scores zero.',
    );
    p();
    p('### Fact layer');
    p();
    p('| Check | Passing |');
    p('| --- | --- |');
    for (const c of facts) p(`| ${c.en} | ${c.count} / ${cellCount} |`);
    p();
    p('### Curation layer');
    p();
    p('| Check | Passing |');
    p('| --- | --- |');
    for (const c of curation) p(`| ${c.en} | ${c.count} / ${cellCount} |`);
    p();
    p(
      `The whole thing reads as half-lit because it is half-lit: ${num(summary.facts_filled)} of ${num(summary.facts_possible)} fact-layer cells are filled, and the curation layer is at ${num(summary.curated)} site-wide. That is not a bug to fix, it is the point of the page: it has been fed facts, nobody has thought about it yet. Any weighting that made the score look better would be a lie to the reader.`,
    );
    p();
    p('## Heartbeat');
    p();
    p(
      `${heartbeat.length} active days on record, ${totalCommits} commits in total. The pulse comes from the real git rhythm, not from an animation curve.`,
    );
    p();
    p('## Entries most in need of data');
    p();
    p('| Entry | Booth | Editions | Vitality | Missing |');
    p('| --- | --- | --- | --- | --- |');
    for (const c of [...cells]
      .sort(
        (a, b) =>
          b.missing.length - a.missing.length || b.editions - a.editions,
      )
      .slice(0, 12)) {
      p(
        `| ${c.name} | ${c.booth} | ${c.editions} | ${c.vitality}% | ${c.missing.length} checks |`,
      );
    }
    p();
    p('## Full data');
    p();
    p(
      `Per-check scores, booth coordinates and gap lists for all ${cellCount} entries: https://computex.taiwanai.ngo/api/organism.json (CC BY-SA 4.0, free to use with attribution).`,
    );
    p();
    p('---');
    p();
    p(
      'Generated by scripts/tools/generate-organism.py. Licensed CC BY-SA 4.0. COMPUTEX.md is a living almanac of the Taiwanese AI hardware industry, speciated from taiwan.md.',
    );
  }

  return L.join('\n') + '\n';
}

/** .md 路由用。text/markdown 而不是 text/plain：讓抓取端知道這是結構化文件。 */
export const ORGANISM_MD_HEADERS = {
  'Content-Type': 'text/markdown; charset=utf-8',
  'Cache-Control': 'public, max-age=3600',
  'X-Content-Type-Options': 'nosniff',
};

export const ORGANISM_JSON_HEADERS = {
  'Content-Type': 'application/json; charset=utf-8',
  'Cache-Control': 'public, max-age=3600',
  'Access-Control-Allow-Origin': '*',
  'X-Content-Type-Options': 'nosniff',
};
