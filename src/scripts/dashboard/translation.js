import { LANGUAGE_DISPLAY_NAMES } from '../../config/languages.mjs';
import { isEn, categoryLabels } from './shared.js';

// ── Translation Coverage ──
// 2026-05-01 γ-late2 v2：3-state donut（fresh / stale / missing）+ (-N) deficit
// 真實 truth source = knowledge/_translation-status.json（status.py 算的）
// 舊 dashboard 把 fresh+stale 都算「已翻譯」遮蔽真實健康度；新版 surface
// 三狀態 + deficit，配合 PR #748 文件記錄的 sovereignty preservation 視角。
function renderTranslations(data, vitals) {
  const bars = document.getElementById('translation-bars');
  const langNames = LANGUAGE_DISPLAY_NAMES; // SSOT: src/config/languages.mjs（2026-07-18 去硬編碼）
  const langLabels = {
    'zh-TW': 'SSOT',
    en: '',
    es: '',
    ja: '',
    ko: '',
    fr: '',
  };
  const maxTotal = vitals.totalArticles;

  // 3-state palette（與 v1 langColors 不同 — 之前是「每語言一色」，
  // 新版改「每狀態一色」讓 fresh/stale/missing 跨語言可比）
  const STATE_COLORS = {
    fresh: '#22c55e', // green-500 — healthy
    stale: '#f59e0b', // amber-500 — warning
    missing: '#e2e8f0', // slate-200 — gap (light grey ring background)
    ssot: '#3b82f6', // blue — zh canonical
  };

  bars.innerHTML =
    '<div class="donut-row">' +
    data.languages
      .map((l) => {
        const s = data.summary[l];
        const isSsot = l === 'zh-TW';
        // freshPct = 真實健康度（只算 fresh，不含 stale）— 中央大字
        // 舊 percentage = (fresh+stale)/total，仍保留作為 sub-label
        const freshPct = s.freshPct != null ? s.freshPct : s.percentage;
        const stalePct =
          s.stale != null && maxTotal > 0
            ? parseFloat(((s.stale / maxTotal) * 100).toFixed(1))
            : 0;
        const missPct =
          s.missing != null && maxTotal > 0
            ? parseFloat(((s.missing / maxTotal) * 100).toFixed(1))
            : 0;
        const fresh = s.fresh != null ? s.fresh : s.total;
        const stale = s.stale != null ? s.stale : 0;
        const miss = s.missing != null ? s.missing : 0;
        const deficit = s.deficit != null ? s.deficit : 0;

        const label =
          langLabels[l] ||
          (isSsot
            ? 'SSOT'
            : freshPct >= 90
              ? isEn
                ? 'Full Fresh'
                : '完整最新'
              : freshPct >= 50
                ? isEn
                  ? 'Mostly Fresh'
                  : '多數最新'
                : freshPct >= 20
                  ? isEn
                    ? 'Partial'
                    : '部分覆蓋'
                  : freshPct > 0
                    ? isEn
                      ? 'Sparse'
                      : '稀疏'
                    : isEn
                      ? 'Empty'
                      : '空缺');

        // 3-segment donut: render 3 stacked SVG arcs
        // r=15.9, circumference ≈ 99.9
        // We render 3 partially-filled circles, each with strokeDasharray
        // controlling its segment length and dashoffset positioning it in sequence.
        // Segment order (clockwise from top): fresh → stale → missing-fill (light grey)
        const C = 99.9;
        const freshLen = isSsot
          ? C
          : Math.min(C, (Math.max(0, fresh) / Math.max(1, maxTotal)) * C);
        const staleLen = isSsot
          ? 0
          : Math.min(
              C - freshLen,
              (Math.max(0, stale) / Math.max(1, maxTotal)) * C,
            );
        // missing fills the rest (background ring already shows it; we draw
        // an explicit slate segment for clarity in tooltips/hover)

        // SVG dasharray pattern: "<gap> <visible> <gap>"
        // simpler: use multiple <circle> with computed dasharray + offset
        // Offset starts at 25 (12 o'clock origin in viewBox 36x36 with stroke-dashoffset=25)
        const f2 = (n) => n.toFixed(2);
        const offsetFresh = 25;
        const offsetStale = 25 - freshLen; // can be negative; SVG handles wrap
        const tooltipText = isSsot
          ? `${vitals.totalArticles} ${isEn ? 'canonical articles' : '篇 zh canonical'}`
          : `${fresh} ${isEn ? 'fresh' : '最新'} · ${stale} ${isEn ? 'stale' : '舊版'} · ${miss} ${isEn ? 'missing' : '未譯'}`;

        // central display: SSOT shows "100%"; others show fresh%
        const centerText = isSsot
          ? '100%'
          : freshPct >= 100
            ? '100%'
            : freshPct >= 10
              ? freshPct.toFixed(1) + '%'
              : freshPct.toFixed(1) + '%';

        // Below count: F+S/total + (-deficit)
        const countLine = isSsot
          ? `${vitals.totalArticles} / ${vitals.totalArticles}`
          : `${fresh + stale} / ${maxTotal}` +
            (deficit > 0
              ? ` <span class="donut-deficit">(-${deficit})</span>`
              : '');

        // 3-line breakdown strip below count
        const breakdown = isSsot
          ? ''
          : `<div class="donut-breakdown" title="${tooltipText}">
                 <span class="bd-fresh">●${fresh}</span>
                 <span class="bd-stale">●${stale}</span>
                 <span class="bd-missing">●${miss}</span>
               </div>`;

        return `<div class="donut-item" title="${tooltipText}">
          <svg viewBox="0 0 36 36" class="donut-chart">
            <!-- background: full ring grey (= missing visualisation) -->
            <circle cx="18" cy="18" r="15.9" fill="none" stroke="${STATE_COLORS.missing}" stroke-width="3"/>
            ${
              isSsot
                ? `<circle cx="18" cy="18" r="15.9" fill="none" stroke="${STATE_COLORS.ssot}" stroke-width="3"
                stroke-dasharray="${f2(C)} 0" stroke-dashoffset="${offsetFresh}"
                stroke-linecap="butt" class="donut-fill" data-state="ssot"/>`
                : `
            <!-- stale segment: amber, drawn behind so fresh draws over it -->
            <circle cx="18" cy="18" r="15.9" fill="none" stroke="${STATE_COLORS.stale}" stroke-width="3"
              stroke-dasharray="0 ${f2(C)}" data-target-len="${f2(staleLen)}"
              stroke-dashoffset="${f2(offsetStale)}" stroke-linecap="butt"
              class="donut-fill donut-fill-stale"/>
            <!-- fresh segment: green, drawn last so it's on top -->
            <circle cx="18" cy="18" r="15.9" fill="none" stroke="${STATE_COLORS.fresh}" stroke-width="3"
              stroke-dasharray="0 ${f2(C)}" data-target-len="${f2(freshLen)}"
              stroke-dashoffset="${offsetFresh}" stroke-linecap="butt"
              class="donut-fill donut-fill-fresh"/>`
            }
            <text x="18" y="20.5" text-anchor="middle" font-size="7.5" font-weight="700" fill="#1e293b">${centerText}</text>
          </svg>
          <div class="donut-label">${langNames[l] || l} <span class="trans-badge">${label}</span></div>
          <div class="donut-count">${countLine}</div>
          ${breakdown}
        </div>`;
      })
      .join('') +
    '</div>';

  // Animate 3-segment donut fills
  requestAnimationFrame(() => {
    bars.querySelectorAll('.donut-fill').forEach((el) => {
      const targetLen = el.getAttribute('data-target-len');
      const targetTotal = el.getAttribute('data-target'); // backward compat
      const C = 99.9;
      if (targetLen != null) {
        // 3-segment mode: animate just this segment to its target length
        requestAnimationFrame(() => {
          const len = parseFloat(targetLen);
          el.style.strokeDasharray = `${len.toFixed(2)} ${(C - len).toFixed(2)}`;
        });
      } else if (targetTotal != null) {
        // legacy single-color mode
        requestAnimationFrame(() => {
          const t = parseFloat(targetTotal);
          if (t >= 99) {
            el.style.strokeDasharray = '99.9 0';
          } else {
            const len = (t / 100) * 99.9;
            el.style.strokeDasharray = len.toFixed(2) + ' 99.9';
          }
        });
      }
    });
  });

  // ─ Matrix ─ per-cell now shows fresh / total + tiny stale stripe + (-N) deficit
  const cats = Object.keys(data.matrix)
    .filter((c) => c !== 'about')
    .sort();
  const thead = document.getElementById('translation-matrix-head');
  thead.innerHTML = `<tr><th>${isEn ? 'Category' : '分類'}</th>${data.languages
    .map((l) => {
      const s = data.summary[l] || {};
      const def =
        l !== 'zh-TW' && s.deficit > 0
          ? ` <span class="th-deficit">(-${s.deficit})</span>`
          : '';
      return `<th>${l}${def}</th>`;
    })
    .join('')}</tr>`;
  const tbody = document.getElementById('translation-matrix-body');
  tbody.innerHTML = cats
    .map((cat) => {
      const row = data.matrix[cat];
      const zhCount = typeof row['zh-TW'] === 'number' ? row['zh-TW'] : 0;
      return `<tr>
          <td><strong>${categoryLabels[cat] || cat}</strong></td>
          ${data.languages
            .map((l) => {
              if (l === 'zh-TW') {
                return `<td class="matrix-cell cell-ssot">${zhCount}</td>`;
              }
              const cell = row[l];
              if (!cell) {
                return `<td class="matrix-cell cell-none">0</td>`;
              }
              // cell shape: { count, fresh, stale, missing, deficit }
              const fresh = cell.fresh || 0;
              const stale = cell.stale || 0;
              const miss = cell.missing || 0;
              const deficit = cell.deficit || 0;
              const freshPct =
                zhCount > 0 ? Math.round((fresh / zhCount) * 100) : 0;
              // colour by FRESH ratio (real health), not by total
              const cls =
                freshPct >= 90
                  ? 'cell-full'
                  : freshPct >= 50
                    ? 'cell-partial'
                    : freshPct > 0
                      ? 'cell-low'
                      : 'cell-none';
              const tip = `${fresh} ${isEn ? 'fresh' : '最新'} · ${stale} ${isEn ? 'stale' : '舊'} · ${miss} ${isEn ? 'missing' : '缺'}`;
              const deficitMark =
                deficit > 0
                  ? ` <span class="cell-deficit">-${deficit}</span>`
                  : '';
              return `<td class="matrix-cell ${cls}" title="${tip}">${fresh}<span class="cell-stale-mark">/${stale}</span>${deficitMark}</td>`;
            })
            .join('')}
        </tr>`;
    })
    .join('');
}

export { renderTranslations };
