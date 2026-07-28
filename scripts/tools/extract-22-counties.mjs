#!/usr/bin/env node
/**
 * extract-22-counties.mjs
 *
 * 讀 22 個 knowledge/Geography/{縣市}.md frontmatter，
 * 合併 hand-coded core_contradiction（來自 DONE-LOG），
 * 輸出 src/data/counties-22.json 給 map.template.astro 使用。
 *
 * 為什麼是 hand-coded：核心矛盾在 22 篇文章的 prose 裡，沒寫進 frontmatter。
 * 第二輪 evolution 可改成從 frontmatter 自動抽取（per evolution report Tier 2）。
 */
import { readFile, writeFile, readdir } from 'node:fs/promises';
import { join, dirname } from 'node:path';
import { fileURLToPath } from 'node:url';
import matter from 'gray-matter';

const __dirname = dirname(fileURLToPath(import.meta.url));
const REPO_ROOT = join(__dirname, '..', '..');

// 22 縣市核心矛盾（hand-curated from ARTICLE-DONE-LOG.md）
const CORE_CONTRADICTIONS = {
  基隆市: '離台北最近的港口，最被台北看不見',
  嘉義市: '被皇帝賜名嘉義，卻成了最容易被略過的省轄市',
  連江縣: '離台灣最遠的縣，是離冷戰最近的縣',
  澎湖縣: '兩次拒博弈，澎湖選擇的不是清貧，是主張自己要成為什麼',
  宜蘭縣: '兩次選擇了自己的命運，蘭陽平原從此沒回頭',
  苗栗縣: '客家硬頸的縣，用八年選出讓縣庫翻倍負債的縣長',
  新竹縣: '235 年的義民信仰，與全台第一的人均所得，住在同一條頭前溪',
  嘉義縣: '49 萬人把全國的臉都借給了阿里山，自己卻找不到臉',
  屏東縣: '國家命運轉折發生在這裡，台北從來沒怎麼記得',
  花蓮縣: '129 年隱身的撒奇萊雅族，用正名換回的太魯閣，0403 地震又讓它遠去',
  臺東縣: '兩個離島，一個關了三十六年政治犯，一個存了四十二年核廢料',
  彰化縣: '打敗過杜邦，留不住年輕人的農業大縣',
  雲林縣: '宜蘭選擇不要的，雲林用三十年的肺換下來',
  金門縣: '1949 年那 56 小時，決定了金門 75 年的命運——也決定了台灣',
  南投縣:
    '台灣最深的傷口都在這裡，震央在集集，賽德克的血在霧社，省政府的形在中興新村',
  新竹市:
    '1733 年種竹為城的竹塹，1980 年長出台積電的搖籃，同一座風城，差了 247 年',
  桃園市: '台灣的進出口、最多的客家人、最多的移工，全在這塊台地上',
  臺南市: '261 年首府、400 年古蹟、21 世紀晶片，疊在同一片土地上',
  高雄市: '1979 同一年升格直轄市，也爆發了美麗島事件',
  臺北市: '萬華 1738 / 大稻埕 1885 / 信義 2004——12 個區活在不同的世紀',
  臺中市: '1887 年差點當首都，2010 年才升格直轄市，等了 123 年',
  新北市: '包圍台北的環狀都會，但 1629 年的紅毛城比台北建城早 200 年',
};

// 別名映射（台 ↔ 臺 等異體字）→ canonical name
const NAME_ALIASES = {
  台北市: '臺北市',
  台中市: '臺中市',
  台南市: '臺南市',
  台東縣: '臺東縣',
};

const canonicalName = (name) => NAME_ALIASES[name] || name;

// 簡短描述（從 description 提取 1-2 句，<= 80 chars，避免 sidebar 過長）
const summarize = (desc, maxLen = 80) => {
  if (!desc) return '';
  // 取第一句到第二句
  const sentences = desc.split(/[。！？]/).filter((s) => s.trim());
  let summary = sentences[0] || '';
  if (summary.length < 40 && sentences[1]) {
    summary += '。' + sentences[1];
  }
  if (summary.length > maxLen) {
    summary = summary.slice(0, maxLen - 1) + '…';
  }
  return summary.trim() + (summary.endsWith('…') ? '' : '。');
};

const SHIP_ORDER = [
  '基隆市',
  '嘉義市',
  '連江縣',
  '澎湖縣',
  '宜蘭縣',
  '苗栗縣',
  '新竹縣',
  '嘉義縣',
  '屏東縣',
  '花蓮縣',
  '臺東縣',
  '彰化縣',
  '雲林縣',
  '金門縣',
  '南投縣',
  '新竹市',
  '桃園市',
  '臺南市',
  '高雄市',
  '臺北市',
  '臺中市',
  '新北市',
];

const orderCounties = (counties) => {
  const ordered = {};
  for (const name of SHIP_ORDER) {
    if (counties[name]) ordered[name] = counties[name];
  }
  return ordered;
};

/** 從 ko 文章 title 抽出核心矛盾（冒號後或 em dash 前） */
const extractKoContradiction = (title) => {
  if (!title) return '';
  if (title.includes(':')) {
    return title.split(':').slice(1).join(':').trim();
  }
  if (title.includes(' — ')) {
    return title.split(' — ')[0].trim();
  }
  return title.trim();
};

/** 側欄 / route 顯示用韓文縣市名 */
const extractKoDisplayName = (title, tags = []) => {
  if (!title) {
    return tags.find((t) => /(시|현)$/.test(t)) || tags[0] || '';
  }
  if (title.includes(':')) {
    return title.split(':')[0].trim();
  }
  if (title.includes(' — ')) {
    const tail = title.split(' — ')[1] || '';
    const stripped = tail.replace(/\([^)]+\)/g, '').trim();
    if (stripped)
      return stripped.endsWith('시') || stripped.endsWith('현')
        ? stripped
        : `${stripped}시`;
    return tags.find((t) => /(시|현)$/.test(t)) || tags[0] || '';
  }
  return tags.find((t) => /(시|현)$/.test(t)) || tags[0] || title.trim();
};

const zhSourceFromTranslated = (translatedFrom) => {
  if (!translatedFrom || typeof translatedFrom !== 'string') return null;
  const base = translatedFrom.replace(/^Geography\//, '').replace(/\.md$/, '');
  return canonicalName(base);
};

async function buildZhCounties() {
  const geoDir = join(REPO_ROOT, 'knowledge', 'Geography');
  const files = await readdir(geoDir);
  const counties = {};

  for (const file of files) {
    if (!file.endsWith('.md')) continue;
    const slug = file.replace(/\.md$/, '');
    const canonical = canonicalName(slug);
    if (!(canonical in CORE_CONTRADICTIONS)) continue;

    const content = await readFile(join(geoDir, file), 'utf-8');
    const { data } = matter(content);

    counties[canonical] = {
      slug,
      title: data.title || '',
      description: data.description || '',
      shortDesc: summarize(data.description),
      core_contradiction: CORE_CONTRADICTIONS[canonical],
      hero: data.image || '',
      heroCredit: data.imageCredit || '',
      heroLicense: data.imageLicense || '',
      heroSource: data.imageSource || '',
      link: `/geography/${slug}`,
      tags: data.tags || [],
      readingTime: data.readingTime || null,
      series: data.series || '22 縣市系列',
    };
  }

  return orderCounties(counties);
}

async function buildKoCounties() {
  const geoDir = join(REPO_ROOT, 'knowledge', 'ko', 'Geography');
  const files = await readdir(geoDir);
  const counties = {};

  for (const file of files) {
    if (!file.endsWith('.md')) continue;
    const slug = file.replace(/\.md$/, '');
    const content = await readFile(join(geoDir, file), 'utf-8');
    const { data } = matter(content);
    const canonical = zhSourceFromTranslated(data.translatedFrom);
    if (!canonical || !(canonical in CORE_CONTRADICTIONS)) continue;

    const title = data.title || '';
    counties[canonical] = {
      slug,
      displayName: extractKoDisplayName(title, data.tags || []),
      title,
      description: data.description || '',
      shortDesc: summarize(data.description),
      core_contradiction: extractKoContradiction(title),
      hero: data.image || '',
      heroCredit: data.imageCredit || '',
      heroLicense: data.imageLicense || '',
      heroSource: data.imageSource || '',
      link: `/ko/geography/${slug}`,
      tags: data.tags || [],
      readingTime: data.readingTime || null,
      series: data.series || '22현시 시리즈',
    };
  }

  return orderCounties(counties);
}

async function main() {
  const zh = await buildZhCounties();
  const ko = await buildKoCounties();

  // ko frontmatter 常缺 hero 圖 — 沿用 zh 縣市條目的 Wikimedia hero
  for (const name of SHIP_ORDER) {
    if (ko[name] && zh[name]?.hero && !ko[name].hero) {
      ko[name].hero = zh[name].hero;
      ko[name].heroCredit = zh[name].heroCredit;
      ko[name].heroLicense = zh[name].heroLicense;
      ko[name].heroSource = zh[name].heroSource;
    }
  }

  const missingZh = SHIP_ORDER.filter((n) => !zh[n]);
  if (missingZh.length > 0) {
    console.warn(`⚠️  zh 缺少 ${missingZh.length} 篇：${missingZh.join(', ')}`);
  }

  const missingKo = SHIP_ORDER.filter((n) => !ko[n]);
  if (missingKo.length > 0) {
    console.warn(`⚠️  ko 缺少 ${missingKo.length} 篇：${missingKo.join(', ')}`);
  }

  const zhPath = join(REPO_ROOT, 'src', 'data', 'counties-22.json');
  const koPath = join(REPO_ROOT, 'src', 'data', 'counties-22.ko.json');
  await writeFile(zhPath, JSON.stringify(zh, null, 2));
  await writeFile(koPath, JSON.stringify(ko, null, 2));
  console.log(`✅ 寫出 ${Object.keys(zh).length}/22 縣市 → ${zhPath}`);
  console.log(`✅ 寫出 ${Object.keys(ko).length}/22 縣市 → ${koPath}`);
}

main().catch((err) => {
  console.error(err);
  process.exit(1);
});
