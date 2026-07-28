#!/usr/bin/env node
/**
 * terminology-charcheck.js — 詞庫字形層確定性 QA（用語保存計畫）
 *
 * LLM 全審（terminology-llm-review.py）對「簡體字外洩」這類 char-level 問題判斷不可靠
 * （LLM 看不太清簡繁差異）。這支用 OpenCC 做確定性字形檢查，是 LLM 審查的互補高信心層：
 *
 *   SIMPLIFIED_LEAK — display.taiwan 欄含無歧義簡體字（台灣欄應全正體）。用程式化 candidate
 *   判定（見下）扣掉台灣標準變體白名單，近零誤報，suggest = 正體形。可安全 --fix-leak。
 *
 * 只讀 data/terminology/*.yaml，不寫檔（--fix-leak 才寫）。
 *
 * 用法：
 *   node scripts/tools/terminology-charcheck.js            # 報告
 *   node scripts/tools/terminology-charcheck.js --json      # 機器可讀
 *   node scripts/tools/terminology-charcheck.js --fix-leak   # 只修 taiwan 欄簡體→正體（安全）
 */
import fs from 'fs';
import path from 'path';
import { fileURLToPath } from 'url';
import * as OpenCC from 'opencc-js';

const __dirname = path.dirname(fileURLToPath(import.meta.url));
const TERM_DIR = path.resolve(__dirname, '../../data/terminology');
const s2t = OpenCC.Converter({ from: 'cn', to: 't' }); // 簡→繁（標準字形，供 suggest）
const t2s = OpenCC.Converter({ from: 't', to: 'cn' }); // 繁→簡（判 candidate）

// 判「台灣欄含簡體字」不能只看 OpenCC 有沒有轉換：台灣標準本來就用一批「簡體長相」的
// 字（游/台/表/污/群/吃/峰/床…），OpenCC 會硬把它們「更正」成 遊/臺/錶/汙/羣/喫/峯/牀
// 造成大量誤報（全庫實測這類 dual-status 字有 12 種、真外洩只有「乌」1 種）。
//
// 正解：程式化判 candidate（s2t(C)≠C 且 t2s(C)==C ⇒ C 是某簡繁對的簡體側），再扣掉
// 「台灣標準採用的 dual-status 白名單」。白名單由全庫 taiwan 欄實際出現的 candidate 反推
// （2026-07-10），台灣人真的會這樣寫、不算外洩。留一點常見 dual-status 字前瞻。
const TW_ACCEPTED_VARIANTS = new Set(
  Array.from('群里吃台峰托雇床霉游秘采布污表制复范志于后系着克涂松咨采夹'),
);
function leakedSimplifiedChars(s) {
  const out = [];
  for (const c of s) {
    if (!/[一-鿿]/.test(c)) continue;
    if (s2t(c) !== c && t2s(c) === c && !TW_ACCEPTED_VARIANTS.has(c))
      out.push(c);
  }
  return out;
}

// 極簡 YAML 讀取：只取 display.taiwan / display.china / id（避免 PyYAML 依賴，鏡像 extract-china-terms）
function readField(text, parent, key) {
  const lines = text.split('\n');
  let inParent = false;
  for (const line of lines) {
    if (/^\S/.test(line)) inParent = line.startsWith(parent + ':');
    if (inParent && new RegExp('^\\s+' + key + ':').test(line)) {
      let v = line.split(':').slice(1).join(':').trim();
      v = v.replace(/^['"]|['"]$/g, '');
      return v;
    }
  }
  return '';
}

const args = process.argv.slice(2);
const asJson = args.includes('--json');
const fixLeak = args.includes('--fix-leak');

const files = fs
  .readdirSync(TERM_DIR)
  .filter((f) => f.endsWith('.yaml') && !f.startsWith('_'));

const leaks = [];

for (const f of files) {
  const p = path.join(TERM_DIR, f);
  const text = fs.readFileSync(p, 'utf-8');
  const tw = readField(text, 'display', 'taiwan');
  const cn = readField(text, 'display', 'china');
  if (!tw) continue;

  // SIMPLIFIED_LEAK: 台灣欄含簡體字（程式化 candidate − 台灣變體白名單）。近零誤報。
  const leakedChars = leakedSimplifiedChars(tw);
  if (leakedChars.length) {
    leaks.push({
      file: f,
      taiwan: tw,
      fixed: s2t(tw),
      china: cn,
      chars: [...new Set(leakedChars)].join(''),
    });
  }
}

if (asJson) {
  console.log(JSON.stringify({ leaks }, null, 2));
} else {
  console.log(`# 詞庫字形 QA — ${files.length} 檔\n`);
  console.log(`## SIMPLIFIED_LEAK（台灣欄含無歧義簡體字，${leaks.length}）`);
  for (const l of leaks)
    console.log(
      `  ${l.file}: 台『${l.taiwan}』簡體[${l.chars}]→ 正體『${l.fixed}』（中『${l.china}』）`,
    );
}

if (fixLeak && leaks.length) {
  let n = 0;
  for (const l of leaks) {
    const p = path.join(TERM_DIR, l.file);
    let text = fs.readFileSync(p, 'utf-8');
    // 只換 display.taiwan 那一行的值（保守：精確定位）
    const re = new RegExp(
      '(^\\s+taiwan:\\s*[\'"]?)' +
        l.taiwan.replace(/[.*+?^${}()|[\]\\]/g, '\\$&') +
        '([\'"]?\\s*$)',
      'm',
    );
    if (re.test(text)) {
      text = text.replace(re, `$1${l.fixed}$2`);
      fs.writeFileSync(p, text);
      n++;
    }
  }
  console.error(`\n[--fix-leak] 修正 ${n} 檔 taiwan 欄簡體→正體`);
}
