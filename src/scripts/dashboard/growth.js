import { isEn } from './shared.js';

// ── Growth Timeline (SVG area chart) ──
function renderGrowth(articles) {
  const container = document.getElementById('growth-chart');
  const byDate = {};
  articles.forEach((a) => {
    if (a.date) {
      const dateKey = a.date.slice(0, 10);
      byDate[dateKey] = (byDate[dateKey] || 0) + 1;
    }
  });
  const dates = Object.keys(byDate).sort();
  if (dates.length === 0) {
    container.textContent = 'No data';
    return;
  }

  // Build cumulative data
  const data = [];
  let cumulative = 0;
  dates.forEach((d) => {
    cumulative += byDate[d];
    data.push({ date: d, daily: byDate[d], cumulative });
  });

  const milestones = [
    { date: '2025-03-17', emoji: '🚀', label: isEn ? 'Launch' : '上線' },
    { date: '2025-03-18', emoji: '📰', label: isEn ? 'Media' : '媒體報導' },
    { date: '2025-03-19', emoji: '📈', label: isEn ? 'Peak' : '高峰' },
    {
      date: '2025-03-21',
      emoji: '🌱',
      label: isEn ? 'Gardener' : '園丁模式',
    },
  ];

  const chartH = 280;
  const padL = 52,
    padR = 16,
    padT = 30,
    padB = 40;
  const w = container.clientWidth || 800;
  const plotW = w - padL - padR;
  const plotH = chartH - padT - padB;
  const maxY = data[data.length - 1].cumulative;
  const n = data.length;

  // Determine nice Y ticks
  const yTickCount = 5;
  const yStep = Math.ceil(maxY / yTickCount / 10) * 10 || 1;
  const yMax = yStep * yTickCount;

  function xPos(i) {
    return padL + (i / Math.max(n - 1, 1)) * plotW;
  }
  function yPos(v) {
    return padT + plotH - (v / yMax) * plotH;
  }

  // Build line path and area path
  const linePoints = data.map(
    (d, i) => `${xPos(i).toFixed(1)},${yPos(d.cumulative).toFixed(1)}`,
  );
  const linePath = 'M' + linePoints.join(' L');
  const areaPath =
    linePath +
    ` L${xPos(n - 1).toFixed(1)},${(padT + plotH).toFixed(1)} L${xPos(0).toFixed(1)},${(padT + plotH).toFixed(1)} Z`;

  // X labels: thin to what the plot width can actually fit (a "MM/DD" label
  // needs ~48px of breathing room) instead of a hardcoded stride — the old
  // every-3rd rule crowded ~43 labels at desktop widths and let the forced
  // last label collide with its stride neighbour.
  const LABEL_SPACING = 48;
  const maxLabels = Math.max(2, Math.floor(plotW / LABEL_SPACING));
  const labelEvery = Math.max(1, Math.ceil((n - 1) / (maxLabels - 1)));

  let xLabels = '';
  data.forEach((d, i) => {
    // Stride labels, skipping any that would crowd the always-drawn last label
    const isStride = i % labelEvery === 0 && n - 1 - i >= labelEvery * 0.6;
    if (isStride || i === n - 1) {
      const mmdd = d.date.slice(5).replace('-', '/');
      xLabels += `<text x="${xPos(i).toFixed(1)}" y="${chartH - 4}" text-anchor="middle" class="growth-svg-label">${mmdd}</text>`;
    }
  });

  // Y axis ticks
  let yLabels = '';
  for (let t = 0; t <= yTickCount; t++) {
    const val = t * yStep;
    const y = yPos(val);
    yLabels += `<line x1="${padL}" x2="${w - padR}" y1="${y.toFixed(1)}" y2="${y.toFixed(1)}" stroke="rgba(0,0,0,0.06)" />`;
    yLabels += `<text x="${padL - 8}" y="${(y + 4).toFixed(1)}" text-anchor="end" class="growth-svg-label">${val}</text>`;
  }

  // Data point circles + invisible hover targets
  let circles = '';
  data.forEach((d, i) => {
    const cx = xPos(i).toFixed(1);
    const cy = yPos(d.cumulative).toFixed(1);
    circles += `<circle cx="${cx}" cy="${cy}" r="3" fill="#8b5cf6" class="growth-dot" />`;
    circles += `<circle cx="${cx}" cy="${cy}" r="12" fill="transparent" class="growth-dot-hover" data-idx="${i}" />`;
  });

  // Milestone markers
  let milestonesSvg = '';
  const milestoneOffsets = [-40, -60, -40, -60];
  milestones.forEach((m, mi) => {
    const idx = data.findIndex((d) => d.date === m.date);
    if (idx === -1) return;
    const cx = xPos(idx).toFixed(1);
    const cy = parseFloat(yPos(data[idx].cumulative).toFixed(1));
    const offset = milestoneOffsets[mi] || -40;
    const labelY = Math.max(padT + 6, cy + offset);
    const lineEndY = labelY + 6;
    milestonesSvg += `<line x1="${cx}" y1="${lineEndY}" x2="${cx}" y2="${cy - 6}" stroke="#8b5cf6" stroke-width="1" stroke-dasharray="3,2" opacity="0.5" />`;
    milestonesSvg += `<circle cx="${cx}" cy="${cy}" r="5" fill="#8b5cf6" stroke="#fff" stroke-width="2" />`;
    milestonesSvg += `<text x="${cx}" y="${labelY}" text-anchor="middle" class="growth-milestone-label">${m.emoji} ${m.label}</text>`;
  });

  // Tooltip element (HTML overlay)
  container.innerHTML = `
      <div class="growth-area-wrapper" style="position:relative">
        <svg viewBox="0 0 ${w} ${chartH}" width="100%" height="${chartH}" class="growth-svg">
          <defs>
            <linearGradient id="areaGrad" x1="0" y1="0" x2="0" y2="1">
              <stop offset="0%" stop-color="rgba(139,92,246,0.3)" />
              <stop offset="100%" stop-color="rgba(139,92,246,0.02)" />
            </linearGradient>
          </defs>
          ${yLabels}
          <path d="${areaPath}" fill="url(#areaGrad)" />
          <path d="${linePath}" fill="none" stroke="#8b5cf6" stroke-width="2" stroke-linejoin="round" />
          ${circles}
          ${milestonesSvg}
          ${xLabels}
        </svg>
        <div class="growth-tooltip" id="growth-tooltip" style="display:none"></div>
      </div>`;

  // Tooltip interaction
  const tooltip = document.getElementById('growth-tooltip');
  const tooltipMargin = 12;
  container.querySelectorAll('.growth-dot-hover').forEach((el) => {
    el.addEventListener('mouseenter', function (e) {
      const idx = parseInt(this.dataset.idx, 10);
      const d = data[idx];
      const mmdd = d.date.slice(5).replace('-', '/');
      tooltip.innerHTML = `<strong>${mmdd}</strong><br>+${d.daily} ${isEn ? 'new' : '新增'}<br>${isEn ? 'Total' : '累計'}: ${d.cumulative}`;
      tooltip.style.display = 'block';
      tooltip.style.visibility = 'hidden';
      const cx = xPos(idx);
      const cy = yPos(d.cumulative);
      const tooltipWidth = tooltip.offsetWidth;
      const tooltipHeight = tooltip.offsetHeight;
      const minLeft = container.scrollLeft + tooltipMargin;
      const maxLeft =
        container.scrollLeft +
        container.clientWidth -
        tooltipWidth -
        tooltipMargin;
      const preferredLeft = cx + tooltipMargin;
      const left = Math.max(minLeft, Math.min(preferredLeft, maxLeft));
      const minTop = tooltipMargin;
      const maxTop = chartH - tooltipHeight - tooltipMargin;
      const preferredTop = cy - tooltipHeight - tooltipMargin;
      const top =
        preferredTop >= minTop
          ? preferredTop
          : Math.min(cy + tooltipMargin, maxTop);
      tooltip.style.left = `${left}px`;
      tooltip.style.top = `${Math.max(minTop, top)}px`;
      tooltip.style.visibility = 'visible';
    });
    el.addEventListener('mouseleave', () => {
      tooltip.style.display = 'none';
      tooltip.style.visibility = 'visible';
    });
  });
}

export { renderGrowth };
