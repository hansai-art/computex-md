import { isEn, animateValue, setText } from './shared.js';

// ── Vital Signs ──
function renderVitals(v) {
  // Hero stats
  const langCount = Object.keys(v.languageCoverage).length;
  setText('hero-stat-articles', v.totalArticles);
  setText('hero-stat-languages', langCount);
  setText('hero-stat-contributors', v.contributors || '—');

  // Animate hero stats
  animateValue(
    document.getElementById('hero-stat-articles'),
    0,
    v.totalArticles,
    1200,
  );
  setTimeout(
    () =>
      animateValue(
        document.getElementById('hero-stat-languages'),
        0,
        langCount,
        800,
      ),
    200,
  );
  setTimeout(() => {
    if (typeof v.contributors === 'number') {
      animateValue(
        document.getElementById('hero-stat-contributors'),
        0,
        v.contributors,
        800,
      );
    }
  }, 400);

  // Vital cards with staggered animation
  const vitalData = [
    { id: 'vital-heartbeat', value: v.articlesLast7Days, suffix: '' },
    { id: 'vital-cells', value: v.totalArticles, suffix: '' },
    {
      id: 'vital-immunity',
      value: parseFloat(v.humanReviewedPercent),
      suffix: '%',
    },
    {
      id: 'vital-dna',
      value: null,
      text: `${langCount} ${isEn ? 'langs' : '語言'}`,
    },
    {
      id: 'vital-revision',
      value: parseFloat(v.avgRevision),
      suffix: '',
      prefix: '×',
    },
  ];

  vitalData.forEach((d, i) => {
    const el = document.getElementById(d.id);
    if (!el) return;
    if (d.value === null) {
      // non-numeric, just set text
      setTimeout(() => {
        el.textContent = d.text;
      }, i * 100);
    } else {
      setTimeout(() => {
        const prefix = d.prefix || '';
        const suffix = d.suffix || '';
        const isFloat = String(d.value).includes('.');
        const startTime = performance.now();
        function update(now) {
          const elapsed = now - startTime;
          const progress = Math.min(elapsed / 800, 1);
          const eased = 1 - (1 - progress) * (1 - progress);
          const current = d.value * eased;
          el.textContent =
            prefix +
            (isFloat ? current.toFixed(1) : Math.round(current)) +
            suffix;
          if (progress < 1) requestAnimationFrame(update);
        }
        requestAnimationFrame(update);
      }, i * 100);
    }
  });
}

export { renderVitals };
