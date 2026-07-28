/**
 * data-client.js — /data 人口金字塔（Population Pyramid）client-side 渲染邏輯
 *
 * 2026-06-13 refactor session 從 data.template.astro 抽出（原 <script
 * define:vars={{ lang }}> 內嵌 477 行，每語言頁各一份 inline copy）。
 * 抽成 Astro-processed module 後 bundle 一份 hashed .js 共用 + 瀏覽器可快取。
 * 內容 1:1 verbatim 搬運（sed 行段抽取，僅整段 dedent 4 空格）。
 *
 * lang 來源：原 define:vars 注入 → 下行 shim 改讀 <html lang>（Layout 設定，值域相同）。
 * 註：本段實際以 document.documentElement.lang 判斷語言（langIsEn），shim 僅維持原契約。
 */
const lang = document.documentElement.getAttribute('lang') || 'zh-TW';

// Population data (estimated based on research)
const populationData = {
  2000: {
    male: [
      650000, 680000, 720000, 750000, 800000, 820000, 750000, 680000, 620000,
      550000, 480000, 420000, 350000, 280000, 220000, 160000, 120000, 80000,
    ],
    female: [
      620000, 650000, 680000, 710000, 760000, 780000, 720000, 650000, 590000,
      530000, 460000, 400000, 340000, 280000, 230000, 180000, 140000, 100000,
    ],
    totalPop: 22270000,
    medianAge: 30,
    elderlyRatio: 8.6,
    youthRatio: 20.1,
  },
  2010: {
    male: [
      520000, 540000, 580000, 650000, 720000, 750000, 820000, 800000, 750000,
      680000, 620000, 550000, 480000, 420000, 350000, 280000, 220000, 160000,
    ],
    female: [
      490000, 510000, 550000, 620000, 680000, 720000, 780000, 760000, 720000,
      650000, 590000, 530000, 460000, 400000, 340000, 280000, 230000, 180000,
    ],
    totalPop: 23160000,
    medianAge: 37,
    elderlyRatio: 10.7,
    youthRatio: 15.6,
  },
  2025: {
    male: [
      420000, 450000, 480000, 520000, 580000, 650000, 720000, 750000, 820000,
      800000, 750000, 680000, 620000, 550000, 480000, 420000, 350000, 280000,
    ],
    female: [
      400000, 430000, 460000, 490000, 550000, 620000, 680000, 720000, 780000,
      760000, 720000, 650000, 590000, 530000, 460000, 400000, 340000, 280000,
    ],
    totalPop: 23300000,
    medianAge: 43,
    elderlyRatio: 18.0,
    youthRatio: 11.5,
  },
  2050: {
    male: [
      320000, 340000, 360000, 380000, 420000, 480000, 520000, 580000, 650000,
      720000, 750000, 820000, 800000, 750000, 680000, 620000, 550000, 480000,
    ],
    female: [
      300000, 320000, 340000, 360000, 400000, 460000, 490000, 550000, 620000,
      680000, 720000, 780000, 760000, 720000, 650000, 590000, 530000, 460000,
    ],
    totalPop: 19800000,
    medianAge: 57,
    elderlyRatio: 38.0,
    youthRatio: 9.2,
  },
};

const ageGroups = [
  '0-4',
  '5-9',
  '10-14',
  '15-19',
  '20-24',
  '25-29',
  '30-34',
  '35-39',
  '40-44',
  '45-49',
  '50-54',
  '55-59',
  '60-64',
  '65-69',
  '70-74',
  '75-79',
  '80-84',
  '85+',
];

// Load D3 and initialize population pyramid
const pyramidScript = document.createElement('script');
pyramidScript.src = 'https://d3js.org/d3.v7.min.js';
pyramidScript.onload = () => initPopulationPyramid();
document.head.appendChild(pyramidScript);

function initPopulationPyramid() {
  const container = document.getElementById('population-pyramid');
  const height = 600;
  const maxWidth = 800;
  let width = Math.min(container.clientWidth, maxWidth);
  let margin = getPyramidMargin(width);
  let chartWidth = width - margin.left - margin.right;
  let chartHeight = height - margin.top - margin.bottom;

  let currentYear = 2025;

  function getPyramidMargin(containerWidth) {
    if (containerWidth <= 480) {
      return { top: 68, right: 16, bottom: 20, left: 16 };
    }

    if (containerWidth <= 768) {
      return { top: 64, right: 24, bottom: 24, left: 24 };
    }

    return { top: 64, right: 40, bottom: 28, left: 100 };
  }

  function getInfoBoxMetrics(innerWidth) {
    const boxWidth = Math.max(136, Math.min(180, innerWidth * 0.28));
    const boxHeight = innerWidth <= 480 ? 92 : 100;
    const boxX = Math.max(innerWidth - boxWidth - 8, innerWidth / 2 + 8);
    const fontSize = innerWidth <= 480 ? 10 : 12;
    const lineStep = innerWidth <= 480 ? 13 : 15;

    return { boxWidth, boxHeight, boxX, fontSize, lineStep };
  }

  const svg = d3
    .select('#population-pyramid')
    .append('svg')
    .attr('width', width)
    .attr('height', height)
    .attr('viewBox', `0 0 ${width} ${height}`)
    .attr('preserveAspectRatio', 'xMidYMid meet');

  const pyramidGroup = svg
    .append('g')
    .attr('transform', `translate(${margin.left}, ${margin.top})`);

  // Scales
  const xScale = d3.scaleLinear().range([0, chartWidth / 2]);

  const yScale = d3
    .scaleBand()
    .domain(ageGroups)
    .range([chartHeight, 0])
    .padding(0.1);

  // Create gradient colors for age groups
  const ageColorScale = d3
    .scaleSequential()
    .domain([0, ageGroups.length - 1])
    .interpolator(d3.interpolateViridis);

  // Y axis (age groups)
  const yAxis = pyramidGroup
    .append('g')
    .attr('class', 'y-axis')
    .attr('transform', `translate(${chartWidth / 2}, 0)`);

  // Male bars (left side)
  const maleBars = pyramidGroup
    .selectAll('.male-bar')
    .data(ageGroups)
    .join('rect')
    .attr('class', 'male-bar')
    .attr('y', (d) => yScale(d))
    .attr('height', yScale.bandwidth())
    .attr('fill', (d, i) => ageColorScale(i))
    .attr('opacity', 0.8);

  // Female bars (right side)
  const femaleBars = pyramidGroup
    .selectAll('.female-bar')
    .data(ageGroups)
    .join('rect')
    .attr('class', 'female-bar')
    .attr('x', chartWidth / 2)
    .attr('y', (d) => yScale(d))
    .attr('height', yScale.bandwidth())
    .attr('fill', (d, i) => ageColorScale(i))
    .attr('opacity', 0.8);

  // Labels for male/female
  const maleTitle = pyramidGroup
    .append('text')
    .attr('class', 'male-title')
    .attr('text-anchor', 'middle')
    .attr('x', chartWidth / 4)
    .attr('y', -20)
    .attr('fill', '#cbd5e1')
    .attr('font-weight', 'bold')
    .text('男性 Male');

  const femaleTitle = pyramidGroup
    .append('text')
    .attr('class', 'female-title')
    .attr('text-anchor', 'middle')
    .attr('x', (chartWidth / 4) * 3)
    .attr('y', -20)
    .attr('fill', '#cbd5e1')
    .attr('font-weight', 'bold')
    .text('女性 Female');

  // Population info box
  const infoBox = pyramidGroup
    .append('g')
    .attr('class', 'info-box')
    .attr('transform', 'translate(0, 20)');

  const infoBoxRect = infoBox
    .append('rect')
    .attr('fill', 'rgba(255, 255, 255, 0.05)')
    .attr('stroke', 'rgba(255, 255, 255, 0.1)')
    .attr('rx', 8);

  const infoText = infoBox
    .append('text')
    .attr('x', 10)
    .attr('y', 20)
    .attr('fill', '#e2e8f0');

  function applyPyramidLayout() {
    width = Math.min(container.clientWidth, maxWidth);
    margin = getPyramidMargin(width);
    chartWidth = width - margin.left - margin.right;
    chartHeight = height - margin.top - margin.bottom;

    svg
      .attr('width', width)
      .attr('height', height)
      .attr('viewBox', `0 0 ${width} ${height}`);

    pyramidGroup.attr('transform', `translate(${margin.left}, ${margin.top})`);

    xScale.range([0, chartWidth / 2]);
    yScale.range([chartHeight, 0]);

    yAxis.attr('transform', `translate(${chartWidth / 2}, 0)`);
    femaleBars.attr('x', chartWidth / 2);

    maleTitle.attr('x', chartWidth / 4).attr('y', -20);

    femaleTitle.attr('x', (chartWidth / 4) * 3).attr('y', -20);

    const infoMetrics = getInfoBoxMetrics(chartWidth);
    infoBox.attr('transform', `translate(${infoMetrics.boxX}, 20)`);
    infoBoxRect
      .attr('width', infoMetrics.boxWidth)
      .attr('height', infoMetrics.boxHeight);
    infoText.attr('font-size', `${infoMetrics.fontSize}px`);
  }

  function updatePyramid(year) {
    const data = populationData[year];
    const maxPop = Math.max(...data.male, ...data.female);
    const infoMetrics = getInfoBoxMetrics(chartWidth);

    xScale.domain([0, maxPop]);

    // Update male bars
    maleBars
      .transition()
      .duration(500)
      .attr('y', (d) => yScale(d))
      .attr('height', yScale.bandwidth())
      .attr('x', (d, i) => chartWidth / 2 - xScale(data.male[i]))
      .attr('width', (d, i) => xScale(data.male[i]));

    // Update female bars
    femaleBars
      .transition()
      .duration(500)
      .attr('x', chartWidth / 2)
      .attr('y', (d) => yScale(d))
      .attr('height', yScale.bandwidth())
      .attr('width', (d, i) => xScale(data.female[i]));

    // Update Y axis
    yAxis.selectAll('text').remove();

    yAxis
      .selectAll('.age-label')
      .data(ageGroups)
      .join('text')
      .attr('class', 'age-label')
      .attr('text-anchor', 'middle')
      .attr('x', 0)
      .attr('y', (d) => yScale(d) + yScale.bandwidth() / 2)
      .attr('dy', '0.35em')
      .attr('fill', '#cbd5e1')
      .attr('font-size', chartWidth <= 360 ? '10px' : '11px')
      .text((d) => d);

    // Update info box
    infoText.selectAll('*').remove();

    infoText
      .append('tspan')
      .attr('x', 10)
      .attr('dy', 0)
      .attr('font-weight', 'bold')
      .attr('fill', '#60a5fa')
      .text(`${year} 年`);

    infoText
      .append('tspan')
      .attr('x', 10)
      .attr('dy', 18)
      .attr('fill', '#f8fafc')
      .text(`總人口：${(data.totalPop / 10000).toFixed(0)}萬人`);

    infoText
      .append('tspan')
      .attr('x', 10)
      .attr('dy', infoMetrics.lineStep)
      .text(`中位數年齡：${data.medianAge}歲`);

    infoText
      .append('tspan')
      .attr('x', 10)
      .attr('dy', infoMetrics.lineStep)
      .text(`老年佔比：${data.elderlyRatio}%`);

    infoText
      .append('tspan')
      .attr('x', 10)
      .attr('dy', infoMetrics.lineStep)
      .text(`幼年佔比：${data.youthRatio}%`);
  }

  // Insight card data per year
  const insightData = {
    2000: {
      medianAge: '30',
      birthRate: '1.68',
      elderlyPct: '8.6%',
      totalPop: '2,227',
    },
    2010: {
      medianAge: '37',
      birthRate: '0.90',
      elderlyPct: '10.7%',
      totalPop: '2,316',
    },
    2025: {
      medianAge: '43',
      birthRate: '0.87',
      elderlyPct: '18%',
      totalPop: '2,340',
    },
    2050: {
      medianAge: '57',
      birthRate: '0.74',
      elderlyPct: '38%',
      totalPop: '<2,000',
    },
  };

  const langIsEn =
    document.documentElement.lang === 'en' ||
    window.location.pathname.startsWith('/en');
  const unitAge = langIsEn ? ' yrs' : ' 歲';
  const unitPop = langIsEn ? ' (10K)' : ' 萬人';

  function updateInsightCards(year) {
    const d = insightData[year];
    if (!d) return;
    const v1 = document.getElementById('insightValue1');
    const v2 = document.getElementById('insightValue2');
    const v3 = document.getElementById('insightValue3');
    const v4 = document.getElementById('insightValue4');
    const u4 = document.getElementById('insightUnit4');
    if (v1) v1.textContent = d.medianAge + unitAge;
    if (v2) v2.textContent = d.birthRate;
    if (v3) v3.textContent = d.elderlyPct;
    if (v4) v4.textContent = d.totalPop;
    if (u4) u4.textContent = unitPop;
  }

  // Initialize with 2025 data
  applyPyramidLayout();
  updatePyramid(currentYear);
  updateInsightCards(currentYear);

  // Slider implementation
  const slider = document.querySelector('.slider-track');
  const thumb = document.getElementById('yearThumb');
  const currentYearLabel = document.getElementById('currentYear');
  const years = [2000, 2010, 2025, 2050];

  let isDragging = false;
  let sliderRect;

  function updateSliderPosition() {
    const yearIndex = years.indexOf(currentYear);
    const percentage = yearIndex / (years.length - 1);
    thumb.style.left = `calc(${percentage * 100}% - 12px)`;
    currentYearLabel.textContent = currentYear;
  }

  function handleSliderUpdate(clientX) {
    const rect = sliderRect || slider.getBoundingClientRect();
    const percentage = Math.max(
      0,
      Math.min(1, (clientX - rect.left) / rect.width),
    );
    const yearIndex = Math.round(percentage * (years.length - 1));
    const newYear = years[yearIndex];

    if (newYear !== currentYear) {
      currentYear = newYear;
      updateSliderPosition();
      updatePyramid(currentYear);
      updateInsightCards(currentYear);
    }
  }

  thumb.addEventListener('mousedown', (e) => {
    isDragging = true;
    sliderRect = slider.getBoundingClientRect();
    document.addEventListener('mousemove', onMouseMove);
    document.addEventListener('mouseup', onMouseUp);
    e.preventDefault();
  });

  function onMouseMove(e) {
    if (isDragging) {
      handleSliderUpdate(e.clientX);
    }
  }

  function onMouseUp() {
    isDragging = false;
    document.removeEventListener('mousemove', onMouseMove);
    document.removeEventListener('mouseup', onMouseUp);
  }

  slider.addEventListener('click', (e) => {
    if (e.target !== thumb) {
      sliderRect = slider.getBoundingClientRect();
      handleSliderUpdate(e.clientX);
    }
  });

  // Touch events for mobile
  thumb.addEventListener('touchstart', (e) => {
    isDragging = true;
    sliderRect = slider.getBoundingClientRect();
    e.preventDefault();
  });

  document.addEventListener('touchmove', (e) => {
    if (isDragging) {
      const touch = e.touches[0];
      handleSliderUpdate(touch.clientX);
      e.preventDefault();
    }
  });

  document.addEventListener('touchend', () => {
    isDragging = false;
  });

  updateSliderPosition();

  // Responsive handling
  window.addEventListener('resize', () => {
    sliderRect = null;
    applyPyramidLayout();
    updatePyramid(currentYear);
  });
}
