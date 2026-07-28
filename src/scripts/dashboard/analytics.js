import { isEn } from './shared.js';

// ── GA4 Analytics ──
// Wait for d3 + d3-cloud to be available on window (they're loaded via
// `<script is:inline defer>` tags in the head, so they finish asynchronously).
// Returns a promise that resolves when both are ready, or rejects after timeout.
function waitForD3(timeoutMs = 5000) {
  return new Promise((resolve, reject) => {
    const start = Date.now();
    const check = () => {
      if (
        typeof window.d3 !== 'undefined' &&
        window.d3.layout &&
        window.d3.layout.cloud
      ) {
        resolve(window.d3);
      } else if (Date.now() - start > timeoutMs) {
        reject(
          new Error('d3 + d3-cloud failed to load within ' + timeoutMs + 'ms'),
        );
      } else {
        setTimeout(check, 50);
      }
    };
    check();
  });
}

// Render a d3-cloud SVG into the given container. Responsive: 16:9 max aspect
// ratio, uses the container's own width. Based on
// https://observablehq.com/@d3/word-cloud
function renderWordCloudSvg(container, wordCloudData, isEn) {
  if (!container || !wordCloudData || !wordCloudData.length) return;

  waitForD3()
    .then((d3) => {
      const parentWidth =
        container.clientWidth || container.parentElement?.clientWidth || 800;
      // Max 16:9 aspect; scale height from width, bounded between 320 and 720
      const width = Math.max(320, Math.min(1200, parentWidth));
      const height = Math.max(320, Math.min(720, Math.round((width * 9) / 16)));

      // Log-scaled font-size with a wide dynamic range so the long tail is
      // visibly smaller than the top queries:
      //   range: 9px → 78px (≈8.7x ratio)
      //   1-impression query lands at exactly the minimum (t=0)
      //   top query lands at maximum (t=1)
      const maxImp = wordCloudData[0]?.impressions || 1;
      const logMax = Math.log(Math.max(maxImp, 2));
      const FONT_MIN = 9;
      const FONT_MAX = 78;
      const fontSizeFor = (imp) => {
        if (logMax === 0) return Math.round((FONT_MIN + FONT_MAX) / 2);
        // Math.max(imp, 1) ensures log is defined; log(1)=0 lands at FONT_MIN
        const t = Math.log(Math.max(imp, 1)) / logMax;
        return Math.round(FONT_MIN + (FONT_MAX - FONT_MIN) * t);
      };

      const words = wordCloudData.map((w) => ({
        text: w.query,
        size: fontSizeFor(w.impressions),
        impressions: w.impressions,
        clicks: w.clicks,
      }));

      // Fixed seed so layout is stable across renders (less jarring on refresh)
      let seed = 1;
      const seededRandom = () => {
        seed = (seed * 9301 + 49297) % 233280;
        return seed / 233280;
      };

      d3.layout
        .cloud()
        .size([width, height])
        .words(words)
        .padding(2)
        .rotate(() => 0)
        .font('"Noto Sans TC", "Source Han Sans TC", system-ui, sans-serif')
        .fontSize((d) => d.size)
        .random(seededRandom)
        .spiral('archimedean')
        .on('end', (laidOut) => {
          drawWordCloud(container, laidOut, width, height, isEn);
        })
        .start();
    })
    .catch((err) => {
      console.warn('[dashboard] word cloud fallback:', err.message);
      container.innerHTML = `<div class="sc-wordcloud-fallback">${isEn ? 'Word cloud unavailable' : '文字雲載入失敗'}</div>`;
      container.removeAttribute('aria-busy');
    });
}

// Draw the laid-out word cloud into the container as an SVG. d3-cloud has
// positioned each word; we just translate to those coordinates.
function drawWordCloud(container, words, width, height, isEn) {
  const svgNS = 'http://www.w3.org/2000/svg';
  const svg = document.createElementNS(svgNS, 'svg');
  svg.setAttribute('viewBox', `0 0 ${width} ${height}`);
  svg.setAttribute('preserveAspectRatio', 'xMidYMid meet');
  svg.setAttribute('class', 'sc-wordcloud-svg');
  svg.setAttribute('role', 'img');
  svg.setAttribute(
    'aria-label',
    isEn ? 'Search Console query word cloud' : 'Search Console 關鍵字文字雲',
  );

  const g = document.createElementNS(svgNS, 'g');
  g.setAttribute('transform', `translate(${width / 2}, ${height / 2})`);
  svg.appendChild(g);

  for (const w of words) {
    const text = document.createElementNS(svgNS, 'text');
    text.setAttribute('text-anchor', 'middle');
    text.setAttribute(
      'transform',
      `translate(${w.x.toFixed(1)}, ${w.y.toFixed(1)}) rotate(${w.rotate})`,
    );
    text.setAttribute('font-size', String(w.size));
    text.setAttribute(
      'font-family',
      '"Noto Sans TC", "Source Han Sans TC", system-ui, sans-serif',
    );
    text.setAttribute('fill', w.clicks > 0 ? '#6366f1' : '#94a3b8');
    text.setAttribute('font-weight', w.clicks > 0 ? '600' : '500');
    text.setAttribute(
      'class',
      w.clicks > 0 ? 'sc-word sc-word-clicked' : 'sc-word',
    );
    text.textContent = w.text;

    const titleEl = document.createElementNS(svgNS, 'title');
    titleEl.textContent =
      w.clicks > 0
        ? `${w.text} — ${w.impressions} ${isEn ? 'impressions' : '曝光'} · ${w.clicks} ${isEn ? 'clicks' : '點擊'}`
        : `${w.text} — ${w.impressions} ${isEn ? 'impressions' : '曝光'}`;
    text.appendChild(titleEl);

    g.appendChild(text);
  }

  container.innerHTML = '';
  container.appendChild(svg);
  // d3-cloud can place word glyphs beyond its nominal canvas (it positions
  // centers, not bounding boxes), which clipped edge words. Re-fit the
  // viewBox to the real ink extents now that the SVG is measurable.
  try {
    const b = g.getBBox();
    if (b.width && b.height) {
      const pad = 6;
      svg.setAttribute(
        'viewBox',
        `${(b.x + width / 2 - pad).toFixed(1)} ${(b.y + height / 2 - pad).toFixed(1)} ${(b.width + pad * 2).toFixed(1)} ${(b.height + pad * 2).toFixed(1)}`,
      );
    }
  } catch {
    /* getBBox throws on detached/hidden SVG in some engines — keep nominal viewBox */
  }
  container.removeAttribute('aria-busy');
}

function renderAnalytics(data) {
  const totalsEl = document.getElementById('analytics-totals');
  const insightsEl = document.getElementById('analytics-insights');
  const pagesEl = document.getElementById('analytics-pages');
  const articles7dEl = document.getElementById('analytics-articles-7d');
  const searchEl = document.getElementById('analytics-search');
  const crawlersEl = document.getElementById('analytics-crawlers');
  const countriesEl = document.getElementById('analytics-countries');
  if (!totalsEl) return;

  const ga = data.ga || {};
  const gaDays = ga.days || 28;
  const search = data.searchConsole7d || data.searchConsole24h || {};
  const searchPeriodDays = data.searchConsole7d ? 7 : 1;
  // Prefer cloudflare7d (fresh from CF cache, 7-day window) over the older
  // cloudflare24h which stayed hand-curated with the last known aiCrawlers
  // breakdown. aiCrawlers is carried forward from cloudflare24h by the
  // generator since Free tier can't refresh it.
  const cloudflare = data.cloudflare7d || data.cloudflare24h || {};
  const cloudflareDays = cloudflare.days || (data.cloudflare7d ? 7 : 1);
  const t = ga.totals || data.totals || {};
  const fmtNum = (n) => (typeof n === 'number' ? n.toLocaleString() : n);
  const fmtPct = (n) =>
    typeof n === 'number' && Number.isFinite(n) ? `${n.toFixed(1)}%` : n;
  const fmtRank = (n) =>
    typeof n === 'number' && Number.isFinite(n) ? n.toFixed(2) : n;
  const gaHighlights = ga.highlights || [];
  const topPages = ga.topPages || data.topPages || [];
  const topArticles7d = ga.topArticles7d || [];
  const topQueries = search.topQueries || [];
  const opportunities = search.opportunities || [];
  const crawlers = cloudflare.aiCrawlers?.crawlers || [];
  const topCountries = cloudflare.traffic?.topCountries || data.countries || [];

  // Totals row
  totalsEl.innerHTML = [
    {
      icon: '👁️',
      value: fmtNum(t.activeUsers),
      label: isEn ? 'Active Users (GA)' : '活躍使用者（GA）',
    },
    {
      icon: '🆕',
      value: fmtNum(t.newUsers),
      label: isEn ? 'New Users (GA)' : '新使用者（GA）',
    },
    {
      icon: '⏱️',
      value:
        typeof t.avgEngagementSeconds === 'number'
          ? `${Math.round(t.avgEngagementSeconds)}s`
          : `${Math.round(parseFloat(t.avgSessionDuration || 0))}s`,
      label: isEn ? 'Avg Engagement' : '平均互動',
    },
    {
      icon: '⚡',
      value: fmtNum(t.events),
      label: isEn ? 'Events (GA)' : '事件數（GA）',
    },
    {
      icon: '🔎',
      value: fmtNum(search.totals?.clicks),
      label: isEn
        ? `Search Clicks (${searchPeriodDays}d)`
        : `搜尋點擊（近 ${searchPeriodDays} 天）`,
    },
    {
      icon: '🤖',
      value: fmtNum(cloudflare.aiCrawlers?.detectedRequests),
      label: isEn ? 'AI Crawls' : 'AI 爬取',
    },
  ]
    .map(
      (m) => `<div class="ga-stat-card">
      <div class="ga-stat-icon">${m.icon}</div>
      <div class="ga-stat-value" data-count="${typeof m.value === 'string' ? m.value.replace(/[^0-9.]/g, '') : m.value}">${m.value}</div>
      <div class="ga-stat-label">${m.label}</div>
    </div>`,
    )
    .join('');

  // Multi-source summary
  if (insightsEl) {
    const brandShare =
      search.totals?.clicks > 0
        ? Math.round(((search.brand?.clicks || 0) / search.totals.clicks) * 100)
        : 0;
    const successfulCrawls = cloudflare.aiCrawlers?.http200 || 0;
    insightsEl.innerHTML =
      `<h3 class="subsection-title">${isEn ? '🧭 Signal Readout' : '🧭 訊號判讀'}</h3>` +
      '<div class="ga-callouts">' +
      [
        {
          title: isEn ? 'Behavior' : '站內行為',
          body: isEn
            ? `${ga.label || 'Recent GA window'} shows home still dominates, while graph/dashboard/map are sticky utility pages.`
            : `${ga.label || '最近 GA 觀測窗'} 顯示首頁仍是主漏斗，但圖譜、Dashboard、地圖已是高黏著工具頁。`,
          meta:
            gaHighlights
              .slice(0, 2)
              .map((item) => `${item.title} ${fmtNum(item.views)}`)
              .join(' · ') || '',
        },
        {
          title: isEn ? 'Search' : '搜尋意圖',
          body: isEn
            ? `Only ${fmtNum(search.totals?.clicks)} clicks came in over the last 24h, and ${brandShare}% were brand searches. Discovery is still ahead of capture.`
            : `過去 24 小時只有 ${fmtNum(search.totals?.clicks)} 次點擊，其中 ${brandShare}% 仍是品牌詞。被看見的速度，仍快於被接住的速度。`,
          meta: opportunities[0]
            ? `${opportunities[0].query} · ${fmtNum(opportunities[0].impressions)} imp · #${fmtRank(opportunities[0].position)}`
            : '',
        },
        {
          title: isEn ? 'Edge + AI' : '邊緣與 AI',
          body: isEn
            ? `${fmtNum(cloudflare.aiCrawlers?.detectedRequests)} AI crawler requests arrived in the last 24h; ${fmtNum(successfulCrawls)} returned HTTP 200.`
            : `過去 24 小時 Cloudflare 看見 ${fmtNum(cloudflare.aiCrawlers?.detectedRequests)} 次 AI crawler 請求，其中 ${fmtNum(successfulCrawls)} 次成功拿到 HTTP 200。`,
          meta: cloudflare.aiCrawlers?.topCrawler
            ? `${cloudflare.aiCrawlers.topCrawler.name} ${fmtNum(cloudflare.aiCrawlers.topCrawler.requests)} · ${cloudflare.aiCrawlers.topPath?.path || ''}`
            : '',
        },
      ]
        .map(
          (item) => `<div class="ga-callout">
              <div class="ga-callout-title">${item.title}</div>
              <div class="ga-callout-body">${item.body}</div>
              <div class="ga-callout-meta">${item.meta}</div>
            </div>`,
        )
        .join('') +
      '</div>';
  }

  // Helper: render a GA page/article list (clickable rows → new tab, 2-col layout)
  const renderGaList = (rows, titleText) => {
    const items = rows.slice(0, 20);
    const mid = Math.ceil(items.length / 2);
    const leftItems = items.slice(0, mid);
    const rightItems = items.slice(mid);

    const renderItem = (p, i) => {
      const rawTitle = p.title
        ? p.title.replace(/\s+\|\s+Taiwan\.md$/, '')
        : '';
      const fallbackName =
        p.path === '/' || p.path === ''
          ? isEn
            ? 'Home'
            : '首頁'
          : decodeURIComponent((p.path || '').replace(/^\/|\/$/g, ''));
      const name = rawTitle || fallbackName;
      const href = p.path || '/';
      return `<a class="ga-page-row ga-page-row-link" href="${href}" target="_blank" rel="noopener noreferrer">
            <span class="ga-page-rank">${i + 1}</span>
            <span class="ga-page-name">${name}</span>
            <span class="ga-page-pv">${fmtNum(p.views || p.pageViews)} ${isEn ? 'views' : '瀏覽'}</span>
          </a>`;
    };

    return (
      `<h3 class="subsection-title">${titleText}</h3>` +
      '<div class="ga-pages-list-2col">' +
      '<div class="ga-pages-list-col">' +
      leftItems.map((p, i) => renderItem(p, i)).join('') +
      '</div>' +
      '<div class="ga-pages-list-col">' +
      rightItems.map((p, i) => renderItem(p, i + mid)).join('') +
      '</div>' +
      '</div>'
    );
  };

  // GA top pages — top 20 pages (28d window, deduped by normalized path)
  if (pagesEl && topPages.length) {
    const pagesTitle = isEn
      ? `🏆 GA Top Pages (last ${gaDays}d)`
      : `🏆 GA 熱門頁面（近 ${gaDays} 天）`;
    pagesEl.innerHTML = renderGaList(topPages, pagesTitle);
  }

  // GA top articles — last 7 days, excludes hubs/meta pages via regex filter
  if (articles7dEl && topArticles7d.length) {
    const articlesTitle = isEn
      ? '📰 GA Top Articles (last 7d)'
      : '📰 GA 熱門文章（近 7 天）';
    articles7dEl.innerHTML = renderGaList(topArticles7d, articlesTitle);
  }

  // Search Console — 7-day data (falls back to 24h if 7d not present)
  if (searchEl && topQueries.length) {
    const scLabel = isEn
      ? `🔎 Search Console (${searchPeriodDays}d)`
      : `🔎 Search Console（近 ${searchPeriodDays} 天）`;

    // Word cloud: all queries with ≥1 impression. Rendered via d3-cloud
    // layout (see https://observablehq.com/@d3/word-cloud) into an SVG
    // with max 16:9 aspect ratio. The actual d3.layout.cloud() call happens
    // after the innerHTML is set (see renderWordCloudSvg below).
    const wordCloud = search.wordCloud || [];
    let wordCloudHtml = '';
    if (wordCloud.length) {
      const cloudTitle = isEn
        ? `☁️ All Queries (${wordCloud.length})`
        : `☁️ 所有關鍵字（${wordCloud.length} 個）`;
      wordCloudHtml =
        `<h4 class="ga-block-title">${cloudTitle}</h4>` +
        `<div class="sc-wordcloud-container" aria-busy="true">
             <div class="sc-wordcloud-loading">${isEn ? 'Building cloud…' : '計算中⋯'}</div>
           </div>`;
    }

    // Brand vs non-brand breakdown (2026-04-17 δ — REFLEXES #24 第 5 種儀器化)
    const brandBreakdown = search.brandBreakdown || null;
    const brandSplitHtml = brandBreakdown
      ? `<div class="sc-brand-split">
            <div class="sc-brand-pill sc-brand-pill-brand">
              <span class="sc-brand-label">${isEn ? 'Brand' : '品牌'}</span>
              <span class="sc-brand-value">${fmtNum(brandBreakdown.brand.clicks)}/${fmtNum(brandBreakdown.brand.impressions)}</span>
              <span class="sc-brand-ctr">CTR ${fmtPct(brandBreakdown.brand.ctr)}</span>
            </div>
            <div class="sc-brand-pill sc-brand-pill-nonbrand">
              <span class="sc-brand-label">${isEn ? 'Non-brand' : '非品牌'}</span>
              <span class="sc-brand-value">${fmtNum(brandBreakdown.nonBrand.clicks)}/${fmtNum(brandBreakdown.nonBrand.impressions)}</span>
              <span class="sc-brand-ctr">CTR ${fmtPct(brandBreakdown.nonBrand.ctr)}</span>
            </div>
            <div class="sc-brand-note">${isEn ? 'Total CTR aggregates both. Non-brand CTR is the real external discoverability.' : '總 CTR 加權掩蓋分層真相；非品牌 CTR 才是真實搜尋可見度'}</div>
          </div>`
      : '';

    searchEl.innerHTML =
      `<h3 class="subsection-title">${scLabel}</h3>` +
      `<div class="ga-subtle">${
        isEn
          ? `${fmtNum(search.totals?.impressions)} impressions · ${fmtNum(search.totals?.clicks)} clicks · ${fmtPct(search.totals?.ctr)} CTR`
          : `${fmtNum(search.totals?.impressions)} 曝光 · ${fmtNum(search.totals?.clicks)} 點擊 · ${fmtPct(search.totals?.ctr)} CTR`
      }</div>` +
      brandSplitHtml +
      (() => {
        const qItems = topQueries.slice(0, 20);
        const qMid = Math.ceil(qItems.length / 2);
        const renderQ = (q, i) => `<div class="sc-query-row">
              <span class="sc-query-rank">${i + 1}</span>
              <span class="sc-query-label">${q.query}</span>
              <span class="sc-query-clicks">${fmtNum(q.clicks)} ${isEn ? 'clicks' : '點擊'}</span>
              <span class="sc-query-impr">${fmtNum(q.impressions)} ${isEn ? 'impr' : '曝光'}</span>
              <span class="sc-query-ctr">${fmtPct(q.ctr)}</span>
              <span class="sc-query-pos">#${fmtRank(q.position)}</span>
            </div>`;
        return (
          '<div class="sc-queries-grid">' +
          '<div class="sc-queries-col">' +
          qItems
            .slice(0, qMid)
            .map((q, i) => renderQ(q, i))
            .join('') +
          '</div>' +
          '<div class="sc-queries-col">' +
          qItems
            .slice(qMid)
            .map((q, i) => renderQ(q, i + qMid))
            .join('') +
          '</div>' +
          '</div>'
        );
      })() +
      (opportunities.length
        ? `<h4 class="ga-block-title">${isEn ? 'Best Next Fixes' : '優先補洞'}</h4>` +
          '<div class="ga-mini-list">' +
          opportunities
            .slice(0, 5)
            .map(
              (q) => `<div class="ga-mini-row">
                  <span class="ga-mini-label">${q.query}</span>
                  <span class="ga-mini-meta">${fmtNum(q.impressions)}i / #${fmtRank(q.position)}</span>
                </div>`,
            )
            .join('') +
          '</div>'
        : '') +
      wordCloudHtml;

    // Now the container exists in the DOM — render the d3-cloud SVG into it.
    // Runs async (waits for d3 CDN scripts to finish loading).
    if (wordCloud.length) {
      renderWordCloudSvg(
        searchEl.querySelector('.sc-wordcloud-container'),
        wordCloud,
        isEn,
      );
    }
  }

  // Cloudflare AI crawler watch
  if (crawlersEl && crawlers.length) {
    const maxRequests = crawlers[0]?.requests || 1;
    crawlersEl.innerHTML =
      `<h3 class="subsection-title">${isEn ? '🤖 AI Crawl Watch' : '🤖 AI 爬行監測'}${cloudflare.aiCrawlersStale ? ' <span class="ga-stale-hint" title="Last refreshed snapshot — Free tier cannot auto-fetch user-agent breakdown">●</span>' : ''}</h3>` +
      `<div class="ga-kpi-strip">
          <span>${isEn ? 'Allowed' : '允許'} ${fmtNum(cloudflare.aiCrawlers?.allowedRequests)}</span>
          <span>HTTP 200 ${fmtNum(cloudflare.aiCrawlers?.http200)}</span>
          <span>${isEn ? 'Failed' : '失敗'} ${fmtNum(cloudflare.aiCrawlers?.unsuccessfulRequests)}</span>
        </div>` +
      crawlers
        .slice(0, 8)
        .map((crawler) => {
          const pct = ((crawler.requests / maxRequests) * 100).toFixed(0);
          return `<div class="ga-source-row">
              <span class="ga-source-name">${crawler.name}</span>
              <div class="ga-source-bar-track">
                <div class="ga-source-bar-fill" style="width:${pct}%"></div>
              </div>
              <span class="ga-source-count">${fmtNum(crawler.requests)}</span>
            </div>`;
        })
        .join('');
  }

  // Countries / regions
  if (countriesEl && topCountries.length) {
    const countryFlags = {
      Taiwan: '🇹🇼',
      'United States': '🇺🇸',
      Japan: '🇯🇵',
      Australia: '🇦🇺',
      Singapore: '🇸🇬',
      Canada: '🇨🇦',
      'Hong Kong': '🇭🇰',
      'United Kingdom': '🇬🇧',
      Germany: '🇩🇪',
      Malaysia: '🇲🇾',
      France: '🇫🇷',
      'South Korea': '🇰🇷',
      Thailand: '🇹🇭',
      Netherlands: '🇳🇱',
      Indonesia: '🇮🇩',
      Philippines: '🇵🇭',
      Brazil: '🇧🇷',
      India: '🇮🇳',
      Vietnam: '🇻🇳',
      'New Zealand': '🇳🇿',
      China: '🇨🇳',
      Mexico: '🇲🇽',
      Spain: '🇪🇸',
      Italy: '🇮🇹',
    };
    const maxUsers = topCountries[0]?.requests || topCountries[0]?.users || 1;
    countriesEl.innerHTML =
      `<h3 class="subsection-title">${isEn ? `🌍 Edge Geography (${cloudflareDays}d)` : `🌍 邊緣流量地理（近 ${cloudflareDays} 天）`}</h3>` +
      '<div class="ga-countries-list">' +
      topCountries
        .slice(0, 8)
        .map((c) => {
          const flag = countryFlags[c.country] || '🌐';
          const count = c.requests || c.users;
          const pct = ((count / maxUsers) * 100).toFixed(0);
          return `<div class="ga-country-row">
            <span class="ga-country-flag">${flag}</span>
            <span class="ga-country-name">${c.country}</span>
            <div class="ga-country-bar-track">
              <div class="ga-country-bar-fill" style="width:${pct}%"></div>
            </div>
            <span class="ga-country-count">${fmtNum(count)}</span>
          </div>`;
        })
        .join('') +
      '</div>';
  }
}

export { renderAnalytics };
