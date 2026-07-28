import {
  LANGUAGE_DISPLAY_NAMES,
  ENABLED_LANGUAGE_CODES,
  DEFAULT_LANGUAGE,
} from '../../config/languages.mjs';
import { isEn, langPrefix } from './shared.js';

// ── Next Steps ──
function renderNextSteps(articles, translations) {
  const grid = document.getElementById('nextsteps-grid');

  // Card 1: Lowest health score article
  const sorted = [...articles].sort(
    (a, b) => (a.healthScore || 0) - (b.healthScore || 0),
  );
  const worst = sorted[0];
  const worstUrl = worst
    ? langPrefix + '/' + worst.category + '/' + worst.slug
    : '#';

  // Card 2: Language with most missing translations
  // Derived from the registry, not written out: the 2026-07-18 de-hardcoding
  // pass fixed the display-names line directly below and left this array at
  // four languages, so seven later-born languages never showed up in the
  // "most missing translations" card at all.
  const langs = ENABLED_LANGUAGE_CODES.filter(
    (c) => c !== DEFAULT_LANGUAGE.code,
  );
  const langNames = LANGUAGE_DISPLAY_NAMES; // SSOT: src/config/languages.mjs（2026-07-18 去硬編碼）
  let maxMissing = 0,
    maxMissingLang = 'en';
  langs.forEach((l) => {
    const missing = articles.filter((a) => !a.translations[l]).length;
    if (missing > maxMissing) {
      maxMissing = missing;
      maxMissingLang = l;
    }
  });

  // Card 3: Oldest unreviewed article
  const unreviewed = articles
    .filter((a) => !a.lastHumanReview && a.date)
    .sort((a, b) => (a.date || '').localeCompare(b.date || ''));
  const oldest = unreviewed[0];
  const oldestUrl = oldest
    ? langPrefix + '/' + oldest.category + '/' + oldest.slug
    : '#';
  let daysSince = 0;
  if (oldest && oldest.date) {
    daysSince = Math.floor(
      (Date.now() - new Date(oldest.date)) / (1000 * 60 * 60 * 24),
    );
  }

  const contributeUrl =
    'https://github.com/hansai-art/computex-md/blob/main/CONTRIBUTING.md';

  grid.innerHTML =
    '<div class="nextstep-card">' +
    '<div class="nextstep-emoji">🔧</div>' +
    '<div class="nextstep-action">' +
    (isEn ? 'Improve' : '改善') +
    '</div>' +
    (worst
      ? '<div class="nextstep-detail"><a href="' +
        worstUrl +
        '">' +
        worst.title +
        '</a></div>' +
        '<div class="nextstep-meta">' +
        (isEn ? 'Health score: ' : '健康分數：') +
        '<strong>' +
        (worst.healthScore || 0) +
        '</strong></div>'
      : '<div class="nextstep-detail">' +
        (isEn ? 'All articles healthy!' : '所有文章都很健康！') +
        '</div>') +
    '<a href="' +
    contributeUrl +
    '" class="nextstep-link" target="_blank" rel="noopener">' +
    (isEn ? 'Contribute →' : '貢獻 →') +
    '</a>' +
    '</div>' +
    '<div class="nextstep-card">' +
    '<div class="nextstep-emoji">🌐</div>' +
    '<div class="nextstep-action">' +
    (isEn ? 'Translate' : '翻譯') +
    '</div>' +
    '<div class="nextstep-detail">' +
    (langNames[maxMissingLang] || maxMissingLang) +
    '</div>' +
    '<div class="nextstep-meta">' +
    maxMissing +
    (isEn ? ' articles missing' : ' 篇文章缺少翻譯') +
    '</div>' +
    '<a href="' +
    contributeUrl +
    '" class="nextstep-link" target="_blank" rel="noopener">' +
    (isEn ? 'Contribute →' : '貢獻 →') +
    '</a>' +
    '</div>' +
    '<div class="nextstep-card">' +
    '<div class="nextstep-emoji">📝</div>' +
    '<div class="nextstep-action">' +
    (isEn ? 'Review' : '審閱') +
    '</div>' +
    (oldest
      ? '<div class="nextstep-detail"><a href="' +
        oldestUrl +
        '">' +
        oldest.title +
        '</a></div>' +
        '<div class="nextstep-meta">' +
        daysSince +
        (isEn ? ' days since creation' : ' 天前建立') +
        '</div>'
      : '<div class="nextstep-detail">' +
        (isEn ? 'All articles reviewed!' : '所有文章已審閱！') +
        '</div>') +
    '<a href="' +
    contributeUrl +
    '" class="nextstep-link" target="_blank" rel="noopener">' +
    (isEn ? 'Contribute →' : '貢獻 →') +
    '</a>' +
    '</div>';
}

export { renderNextSteps };
