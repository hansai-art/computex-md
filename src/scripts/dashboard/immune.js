import { isEn, categoryLabels, langPrefix } from './shared.js';

// ── Immune System ──
function renderImmune(articles, vitals) {
  const overview = document.getElementById('immune-overview');
  const reviewedCount = articles.filter((a) => a.lastHumanReview).length;
  const featuredCount = articles.filter((a) => a.featured).length;
  const verifiedCount = articles.filter((a) => a.lastVerified).length;
  const total = articles.length;

  const immuneMetrics = [
    {
      label: isEn ? 'Human Reviewed' : '人工審閱',
      count: reviewedCount,
      total,
      color: '#4ade80',
    },
    {
      label: isEn ? 'Featured' : '精選文章',
      count: featuredCount,
      total,
      color: '#f59e0b',
    },
    {
      label: isEn ? 'Verified' : '已驗證',
      count: verifiedCount,
      total,
      color: '#3b82f6',
    },
  ];

  overview.innerHTML =
    '<div class="donut-row">' +
    immuneMetrics
      .map((m) => {
        const pct = Math.round((m.count / m.total) * 100);
        return `<div class="donut-item">
          <svg viewBox="0 0 36 36" class="donut-chart">
            <circle cx="18" cy="18" r="15.9" fill="none" stroke="rgba(0,0,0,0.06)" stroke-width="3"/>
            <circle cx="18" cy="18" r="15.9" fill="none" stroke="${m.color}" stroke-width="3"
              stroke-dasharray="0, 100" data-target="${pct}" stroke-dashoffset="25"
              stroke-linecap="round" class="donut-fill"/>
            <text x="18" y="20.5" text-anchor="middle" font-size="8" font-weight="700" fill="#1e293b">${pct}%</text>
          </svg>
          <div class="donut-label">${m.label}</div>
          <div class="donut-count">${m.count} / ${m.total}</div>
        </div>`;
      })
      .join('') +
    '</div>';

  // Animate donut fills
  requestAnimationFrame(() => {
    overview.querySelectorAll('.donut-fill').forEach((el) => {
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

  // Citation health
  const citEl = document.getElementById('citation-health');
  if (citEl) {
    const withFn = articles.filter((a) => (a.fnCount || 0) > 0).length;
    const withOverview = articles.filter((a) => a.hasOverview).length;
    const withReading = articles.filter((a) => a.hasReading).length;
    const fnPct = Math.round((withFn / total) * 100);
    const ovPct = Math.round((withOverview / total) * 100);
    const rdPct = Math.round((withReading / total) * 100);
    citEl.innerHTML = `<div class="citation-stats">
        <div class="cit-stat">
          <span class="cit-num ${fnPct < 10 ? 'cit-danger' : ''}">${fnPct}%</span>
          <span class="cit-label">${isEn ? 'Has Footnotes' : '有腳註'}</span>
          <span class="cit-detail">${withFn} / ${total}</span>
        </div>
        <div class="cit-stat">
          <span class="cit-num ${ovPct < 50 ? 'cit-warn' : ''}">${ovPct}%</span>
          <span class="cit-label">${isEn ? '30s Overview' : '30 秒概覽'}</span>
          <span class="cit-detail">${withOverview} / ${total}</span>
        </div>
        <div class="cit-stat">
          <span class="cit-num ${rdPct < 10 ? 'cit-danger' : ''}">${rdPct}%</span>
          <span class="cit-label">${isEn ? 'Extended Reading' : '延伸閱讀'}</span>
          <span class="cit-detail">${withReading} / ${total}</span>
        </div>
      </div>`;
  }

  // Queue: unreviewed articles, oldest first
  const unreviewed = articles.filter((a) => !a.lastHumanReview);
  const queue = [...unreviewed]
    .sort((a, b) => (a.date || '').localeCompare(b.date || ''))
    .slice(0, 15);

  const queueHeader = document.querySelector('.queue-desc');
  if (queueHeader) {
    queueHeader.textContent += ` (${unreviewed.length} ${isEn ? 'total' : '篇待審'})`;
  }

  const QUEUE_COLLAPSE_LIMIT = 5;
  const queueEl = document.getElementById('immune-queue');
  const queueItems = queue.map(
    (a) => `<a href="${langPrefix}/${a.category}/${a.slug}" class="queue-item">
        <span class="queue-cat cat-${a.category}">${categoryLabels[a.category] || a.category}</span>
        <span class="queue-title">${a.title}</span>
        <span class="queue-date">${a.date || '—'}</span>
      </a>`,
  );

  if (queue.length > QUEUE_COLLAPSE_LIMIT) {
    const visibleItems = queueItems.slice(0, QUEUE_COLLAPSE_LIMIT).join('');
    const hiddenItems = queueItems.slice(QUEUE_COLLAPSE_LIMIT).join('');
    queueEl.innerHTML =
      visibleItems +
      `<div class="queue-hidden" id="queue-hidden" style="display:none">${hiddenItems}</div>` +
      `<button class="queue-toggle-btn" id="queue-toggle-btn">${isEn ? 'Show all (' + queue.length + ' total)' : '顯示全部 (' + queue.length + ' 篇)'}</button>`;

    document
      .getElementById('queue-toggle-btn')
      .addEventListener('click', function () {
        const hidden = document.getElementById('queue-hidden');
        const expanded = hidden.style.display !== 'none';
        hidden.style.display = expanded ? 'none' : 'grid';
        this.textContent = expanded
          ? isEn
            ? 'Show all (' + queue.length + ' total)'
            : '顯示全部 (' + queue.length + ' 篇)'
          : isEn
            ? 'Collapse'
            : '收合';
        this.classList.toggle('expanded', !expanded);
      });
  } else {
    queueEl.innerHTML = queueItems.join('');
  }
}

export { renderImmune };
