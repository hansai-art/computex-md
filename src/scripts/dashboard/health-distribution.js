import { isEn } from './shared.js';

// ── Health Distribution Histogram ──
function renderHealthDistribution(articles) {
  const container = document.getElementById('health-chart');
  const summaryEl = document.getElementById('health-summary');

  // Bucket articles into score ranges
  const ranges = [
    { label: '0-20', min: 0, max: 20, color: '#ef4444' },
    { label: '20-40', min: 20, max: 40, color: '#f97316' },
    { label: '40-60', min: 40, max: 60, color: '#eab308' },
    { label: '60-80', min: 60, max: 80, color: '#86efac' },
    { label: '80-100', min: 80, max: 101, color: '#22c55e' },
  ];

  const buckets = ranges.map((r) => ({
    ...r,
    count: articles.filter(
      (a) => (a.healthScore || 0) >= r.min && (a.healthScore || 0) < r.max,
    ).length,
  }));

  const maxCount = Math.max(...buckets.map((b) => b.count), 1);

  // SVG dimensions
  const w = 600,
    h = 260;
  const padL = 50,
    padR = 20,
    padT = 30,
    padB = 40;
  const plotW = w - padL - padR;
  const plotH = h - padT - padB;
  const barW = plotW / buckets.length;
  const barGap = 12;

  // Y axis ticks
  const yTickCount = 4;
  const yStep = Math.ceil(maxCount / yTickCount / 5) * 5 || 1;
  const yMax = yStep * yTickCount;
  function yPos(v) {
    return padT + plotH - (v / yMax) * plotH;
  }

  let yLines = '';
  for (let t = 0; t <= yTickCount; t++) {
    const val = t * yStep;
    const y = yPos(val);
    yLines +=
      '<line x1="' +
      padL +
      '" x2="' +
      (w - padR) +
      '" y1="' +
      y.toFixed(1) +
      '" y2="' +
      y.toFixed(1) +
      '" stroke="rgba(0,0,0,0.06)" />';
    yLines +=
      '<text x="' +
      (padL - 8) +
      '" y="' +
      (y + 4).toFixed(1) +
      '" text-anchor="end" class="health-svg-label">' +
      val +
      '</text>';
  }

  let bars = '';
  buckets.forEach((b, i) => {
    const x = padL + i * barW + barGap / 2;
    const bw = barW - barGap;
    const barH = b.count > 0 ? (b.count / yMax) * plotH : 0;
    const y = padT + plotH - barH;
    bars +=
      '<rect x="' +
      x.toFixed(1) +
      '" y="' +
      y.toFixed(1) +
      '" width="' +
      bw.toFixed(1) +
      '" height="' +
      barH.toFixed(1) +
      '" rx="4" fill="' +
      b.color +
      '" opacity="0.85"><animate attributeName="height" from="0" to="' +
      barH.toFixed(1) +
      '" dur="0.6s" fill="freeze" /><animate attributeName="y" from="' +
      (padT + plotH).toFixed(1) +
      '" to="' +
      y.toFixed(1) +
      '" dur="0.6s" fill="freeze" /></rect>';
    // Count label on top
    if (b.count > 0) {
      bars +=
        '<text x="' +
        (x + bw / 2).toFixed(1) +
        '" y="' +
        (y - 6).toFixed(1) +
        '" text-anchor="middle" class="health-bar-count">' +
        b.count +
        '</text>';
    }
    // X label
    bars +=
      '<text x="' +
      (x + bw / 2).toFixed(1) +
      '" y="' +
      (h - 8) +
      '" text-anchor="middle" class="health-svg-label">' +
      b.label +
      '</text>';
  });

  container.innerHTML =
    '<svg viewBox="0 0 ' +
    w +
    ' ' +
    h +
    '" width="100%" height="' +
    h +
    '" class="health-svg">' +
    yLines +
    bars +
    '</svg>';

  // Summary line
  const needsAttention = articles.filter(
    (a) => (a.healthScore || 0) < 40,
  ).length;
  if (needsAttention > 0) {
    summaryEl.textContent = isEn
      ? '\uD83D\uDD34 ' +
        needsAttention +
        ' articles need attention (score < 40)'
      : '\uD83D\uDD34 ' + needsAttention + ' 篇文章需要關注（分數 < 40）';
  } else {
    summaryEl.textContent = isEn
      ? '\uD83D\uDFE2 All articles are in good health!'
      : '\uD83D\uDFE2 所有文章健康狀態良好！';
  }
}

export { renderHealthDistribution };
