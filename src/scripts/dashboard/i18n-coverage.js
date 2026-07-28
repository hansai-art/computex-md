import { LANGUAGE_DISPLAY_NAMES } from '../../config/languages.mjs';
import { isEn } from './shared.js';

// ── i18n UI Coverage（2026-04-25 β7 Phase 3 #9）──
// 不同於上方 renderTranslations（文章層）— 這裡顯示 src/i18n/ 12 module
// 各語言 UI 字串 keys 的覆蓋率
function renderI18nCoverage(data) {
  const bars = document.getElementById('i18n-bars');
  const langNames = LANGUAGE_DISPLAY_NAMES; // SSOT: src/config/languages.mjs（2026-07-18 去硬編碼）
  const langColors = {
    'zh-TW': '#3b82f6',
    en: '#4ade80',
    ja: '#ec4899',
    ko: '#a855f7',
    fr: '#f97316',
    es: '#facc15',
    vi: '#14b8a6',
    id: '#ef4444',
    pt: '#22c55e',
    hi: '#f59e0b',
    // 2026-07-25: ar/ru (enabled:false birth scaffold) — explicit colors so their
    // 0%→climbing donut doesn't visually collide with zh-TW's blue fallback color.
    ar: '#8b5cf6',
    ru: '#0ea5e9',
  };
  const langs = Object.keys(data.lang_totals);
  const maxTotal = data.max_total;

  bars.innerHTML =
    '<div class="donut-row">' +
    langs
      .map((l) => {
        const t = data.lang_totals[l];
        const pct = Math.min(t.coverage_pct, 100);
        const color = langColors[l] || '#3b82f6';
        const label =
          l === 'zh-TW'
            ? 'SSOT'
            : pct >= 99
              ? isEn
                ? 'Full'
                : '完整'
              : pct >= 50
                ? isEn
                  ? 'Partial'
                  : '部分'
                : pct > 0
                  ? isEn
                    ? 'Seedling'
                    : '萌芽'
                  : isEn
                    ? 'Fallback'
                    : '依賴 Fallback';
        return `<div class="donut-item">
          <svg viewBox="0 0 36 36" class="donut-chart">
            <circle cx="18" cy="18" r="15.9" fill="none" stroke="rgba(0,0,0,0.06)" stroke-width="3"/>
            <circle cx="18" cy="18" r="15.9" fill="none" stroke="${color}" stroke-width="3"
              stroke-dasharray="0, 100" data-target="${pct}" stroke-dashoffset="25"
              stroke-linecap="round" class="donut-fill"/>
            <text x="18" y="20.5" text-anchor="middle" font-size="8" font-weight="700" fill="#1e293b">${Math.round(pct)}%</text>
          </svg>
          <div class="donut-label">${langNames[l] || l} <span class="trans-badge">${label}</span></div>
          <div class="donut-count">${t.keys} / ${maxTotal}</div>
        </div>`;
      })
      .join('') +
    '</div>';

  // Animate donut fills
  requestAnimationFrame(() => {
    bars.querySelectorAll('.donut-fill').forEach((el) => {
      const target = el.getAttribute('data-target');
      requestAnimationFrame(() => {
        // Fix v2: explicit circumference + drop threshold to ≥99 (round-cap visual overlap starts before 100%)
        // Circle r=15.9 → circumference = 2π × 15.9 ≈ 99.9
        const t = parseFloat(target);
        if (t >= 99) {
          el.style.strokeDasharray = '99.9 0';
        } else {
          const len = (t / 100) * 99.9;
          el.style.strokeDasharray = len.toFixed(2) + ' 99.9';
        }
      });
    });
  });

  // Matrix: module × lang
  const thead = document.getElementById('i18n-matrix-head');
  thead.innerHTML = `<tr><th>${isEn ? 'Module' : 'Module'}</th>${langs.map((l) => `<th>${l}</th>`).join('')}</tr>`;
  const tbody = document.getElementById('i18n-matrix-body');
  tbody.innerHTML = data.modules
    .map((m) => {
      const zhCount = m.langs['zh-TW'] || 0;
      const cells = langs
        .map((l) => {
          const c = m.langs[l] || 0;
          let cell;
          if (c === 0 && zhCount > 0) {
            cell = `<td style="color:#dc2626;">🔴 0</td>`;
          } else if (c < zhCount) {
            cell = `<td style="color:#ca8a04;">🟡 ${c}/${zhCount}</td>`;
          } else if (c > 0) {
            cell = `<td style="color:#16a34a;">✅ ${c}</td>`;
          } else {
            cell = `<td style="color:#94a3b8;">—</td>`;
          }
          return cell;
        })
        .join('');
      return `<tr><td><strong>${m.name}</strong></td>${cells}</tr>`;
    })
    .join('');
}

export { renderI18nCoverage };
