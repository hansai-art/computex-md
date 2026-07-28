import { isEn, categoryLabels } from './shared.js';

// ── Content Analysis ──
function renderContentAnalysis(articles) {
  const chartEl = document.getElementById('ca-category-chart');
  const statsEl = document.getElementById('ca-stats');
  if (!chartEl || !statsEl) return;

  // Count by category
  const catCounts = {};
  articles.forEach((a) => {
    const cat = a.category || 'other';
    catCounts[cat] = (catCounts[cat] || 0) + 1;
  });

  const sorted = Object.entries(catCounts)
    .filter(([cat]) => cat !== 'root' && cat !== 'resources')
    .sort((a, b) => b[1] - a[1]);

  const maxCount = sorted[0]?.[1] || 1;
  const colors = [
    '#8b5cf6',
    '#6366f1',
    '#3b82f6',
    '#06b6d4',
    '#10b981',
    '#84cc16',
    '#f59e0b',
    '#f97316',
    '#ef4444',
    '#ec4899',
    '#a855f7',
    '#14b8a6',
    '#eab308',
  ];

  chartEl.innerHTML = sorted
    .map(([cat, count], i) => {
      const pct = ((count / maxCount) * 100).toFixed(1);
      const color = colors[i % colors.length];
      const label = categoryLabels[cat.toLowerCase()] || cat;
      return `<div class="ca-bar-row">
        <span class="ca-bar-label">${label}</span>
        <div class="ca-bar-track">
          <div class="ca-bar-fill" style="width:0%;background:${color}" data-width="${pct}%">
            <span class="ca-bar-count">${count}</span>
          </div>
        </div>
      </div>`;
    })
    .join('');

  // Animate bars
  requestAnimationFrame(() => {
    chartEl.querySelectorAll('.ca-bar-fill').forEach((el, i) => {
      setTimeout(() => {
        el.style.width = el.dataset.width;
      }, i * 60);
    });
  });

  // Stats panel
  const totalCats = sorted.length;
  const totalArts = sorted.reduce((s, [, c]) => s + c, 0);
  const avgPerCat = Math.round(totalArts / totalCats);
  const largest = sorted[0];
  const largestLabel = largest
    ? categoryLabels[largest[0].toLowerCase()] || largest[0]
    : '—';

  statsEl.innerHTML = `
      <div class="ca-stat-card">
        <div class="ca-stat-number">${totalArts}</div>
        <div class="ca-stat-label">${isEn ? 'Total Articles' : '總文章數'}</div>
      </div>
      <div class="ca-stat-card">
        <div class="ca-stat-number">${totalCats}</div>
        <div class="ca-stat-label">${isEn ? 'Categories' : '分類數'}</div>
      </div>
      <div class="ca-stat-card">
        <div class="ca-stat-number">${avgPerCat}</div>
        <div class="ca-stat-label">${isEn ? 'Avg per Category' : '平均每類'}</div>
      </div>
      <div class="ca-stat-card">
        <div class="ca-stat-number">${largestLabel}</div>
        <div class="ca-stat-label">${largest ? (isEn ? 'Largest: ' + largest[1] : '最大分類: ' + largest[1] + ' 篇') : '—'}</div>
      </div>`;
}

export { renderContentAnalysis };
