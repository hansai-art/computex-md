import { isEn } from './shared.js';

// ── Reproduction System — Spores (2026-04-18 δ-late) ──
function renderSpores(s) {
  if (!s) return;

  // Helper
  const fmt = (n) => {
    if (n == null || isNaN(n)) return '—';
    if (n >= 1000000) return (n / 1000000).toFixed(1) + 'M';
    if (n >= 1000) return Math.round(n / 1000) + 'K';
    return String(n);
  };

  // 2.1 Overview tiles
  const overview = document.getElementById('spores-overview');
  if (overview) {
    const totalReach = (s.topPerformers || []).reduce(
      (sum, p) => sum + (p.views || 0),
      0,
    );
    const top = (s.topPerformers || [])[0] || null;
    const warningCount = (s.backfillWarnings || []).filter(
      (w) => w.status === 'OVERDUE',
    ).length;
    overview.innerHTML = [
      '<div class="spore-tile">',
      '<div class="spore-tile-value">' + (s.totals.count || 0) + '</div>',
      '<div class="spore-tile-label">' +
        (isEn ? 'Total Spores' : '發過孢子數') +
        '</div>',
      '</div>',
      '<div class="spore-tile">',
      '<div class="spore-tile-value">' + fmt(totalReach) + '</div>',
      '<div class="spore-tile-label">' +
        (isEn ? 'Top-5 Total Reach' : 'Top5 總觸及') +
        '</div>',
      '</div>',
      '<div class="spore-tile">',
      '<div class="spore-tile-value">' +
        (top ? (top.badge || '⭐') + ' ' + fmt(top.views) : '—') +
        '</div>',
      '<div class="spore-tile-label">' +
        (isEn ? 'Strongest Spore' : '最強孢子') +
        (top
          ? ' (#' + top.n + ' ' + (top.article || '').slice(0, 10) + ')'
          : '') +
        '</div>',
      '</div>',
      '<div class="spore-tile' +
        (warningCount > 0 ? ' spore-tile-warn' : '') +
        '">',
      '<div class="spore-tile-value">' + warningCount + '</div>',
      '<div class="spore-tile-label">' +
        (isEn ? 'Backfill Overdue' : '回填 OVERDUE') +
        '</div>',
      '</div>',
    ].join('');
  }

  // 2.2 Top Performers table
  const top = document.getElementById('spores-top');
  if (top) {
    const rows = (s.topPerformers || [])
      .slice(0, 8)
      .map((p) => {
        const articleClean = (p.article || '').replace(/^[🌋🔥⭐\s]+/, '');
        const url = p.url || '';
        // Whole row opens the spore post in a new tab; the title is also a real
        // anchor so keyboard / middle-click work (the row handler ignores clicks
        // that land on the anchor to avoid opening twice).
        const articleCell = url
          ? '<a href="' +
            url +
            '" target="_blank" rel="noopener noreferrer">' +
            articleClean +
            '</a>'
          : articleClean;
        return (
          '<tr' +
          (url
            ? ' class="spore-row-link" data-url="' +
              url +
              '" style="cursor:pointer"'
            : '') +
          '>' +
          '<td class="spore-badge">' +
          (p.badge || '') +
          ' #' +
          p.n +
          '</td>' +
          '<td>' +
          articleCell +
          '</td>' +
          '<td><span class="platform-' +
          (p.platform || 'other') +
          '">' +
          (p.platform || '—').toUpperCase() +
          '</span></td>' +
          '<td class="num">' +
          fmt(p.views) +
          '</td>' +
          '<td class="num">' +
          (p.rate != null ? p.rate.toFixed(2) + '%' : '—') +
          '</td>' +
          '<td class="num">' +
          fmt(p.engagements) +
          '</td>' +
          '</tr>'
        );
      })
      .join('');
    top.innerHTML =
      '<table class="spore-table"><thead><tr>' +
      '<th>#</th>' +
      '<th>' +
      (isEn ? 'Article' : '文章') +
      '</th>' +
      '<th>' +
      (isEn ? 'Platform' : '平台') +
      '</th>' +
      '<th class="num">Views</th>' +
      '<th class="num">Rate</th>' +
      '<th class="num">' +
      (isEn ? 'Engagements' : '互動') +
      '</th>' +
      '</tr></thead><tbody>' +
      (rows || '<tr><td colspan="6">—</td></tr>') +
      '</tbody></table>';
    top.querySelectorAll('tr.spore-row-link').forEach((tr) => {
      tr.addEventListener('click', (e) => {
        if (e.target.closest('a')) return; // anchor handles its own click
        const u = tr.getAttribute('data-url');
        if (u) window.open(u, '_blank', 'noopener');
      });
    });
  }

  // 2.3 Amplification horizontal bars
  const amp = document.getElementById('spores-amplification');
  if (amp) {
    const items = (s.amplification || [])
      .filter((a) => a.multiplier || a.ga_7d_after)
      .slice(0, 8);
    if (items.length === 0) {
      amp.innerHTML =
        '<p class="muted">' +
        (isEn ? 'No amplification data yet.' : '尚未累積放大倍數資料。') +
        '</p>';
    } else {
      // 決定 bar 長度的 metric：優先用 multiplier（有 ga_before 基線的），
      // fallback 用 ga_7d_after（絕對 GA 7d views）—— 這確保長度反映真實量級差異
      const hasAnyMul = items.some((i) => i.multiplier);
      const maxMetric = hasAnyMul
        ? Math.max(...items.map((i) => i.multiplier || 0), 1)
        : Math.max(...items.map((i) => i.ga_7d_after || 0), 1);
      amp.innerHTML =
        '<div class="spore-amp-list">' +
        items
          .map((i) => {
            const metric = hasAnyMul ? i.multiplier || 0 : i.ga_7d_after || 0;
            // log scale for ga_7d_after（因為差 100x 常見，linear 會讓小的看不見）
            const pct = hasAnyMul
              ? Math.min((metric / maxMetric) * 100, 100)
              : Math.min(
                  (Math.log(Math.max(metric, 1)) /
                    Math.log(Math.max(maxMetric, 2))) *
                    100,
                  100,
                );
            const label = i.multiplier
              ? i.multiplier +
                'x (' +
                (i.ga_before || '?') +
                ' → ' +
                (i.ga_7d_after || '?') +
                ')'
              : fmt(i.ga_7d_after) + ' views/7d';
            return (
              '<div class="spore-amp-row">' +
              '<div class="spore-amp-name">' +
              (i.article || '').slice(0, 20) +
              '</div>' +
              '<div class="spore-amp-bar"><div class="spore-amp-fill" style="width:' +
              pct +
              '%"></div></div>' +
              '<div class="spore-amp-value">' +
              label +
              '</div>' +
              '</div>'
            );
          })
          .join('') +
        '</div>';
    }
  }

  // 2.4 Platform comparison donut/table
  const plat = document.getElementById('spores-platforms');
  if (plat) {
    const p = s.platformComparison || {};
    const platformKeys = Object.keys(p);
    if (platformKeys.length === 0) {
      plat.innerHTML = '<p class="muted">—</p>';
    } else {
      plat.innerHTML =
        '<table class="spore-table"><thead><tr>' +
        '<th>' +
        (isEn ? 'Platform' : '平台') +
        '</th>' +
        '<th class="num">' +
        (isEn ? 'Count' : '發過') +
        '</th>' +
        '<th class="num">' +
        (isEn ? 'Avg Views' : '平均觸及') +
        '</th>' +
        '<th class="num">' +
        (isEn ? 'Max Views' : '最高') +
        '</th>' +
        '<th class="num">' +
        (isEn ? 'Avg Rate' : '平均互動率') +
        '</th>' +
        '<th class="num">' +
        (isEn ? 'Max Rate' : '最高互動率') +
        '</th>' +
        '</tr></thead><tbody>' +
        platformKeys
          .map(
            (k) =>
              '<tr>' +
              '<td><span class="platform-' +
              k +
              '">' +
              k.toUpperCase() +
              '</span></td>' +
              '<td class="num">' +
              p[k].count +
              '</td>' +
              '<td class="num">' +
              fmt(p[k].avgViews) +
              '</td>' +
              '<td class="num">' +
              fmt(p[k].maxViews) +
              '</td>' +
              '<td class="num">' +
              (p[k].avgRate != null ? p[k].avgRate.toFixed(2) + '%' : '—') +
              '</td>' +
              '<td class="num">' +
              (p[k].maxRate != null ? p[k].maxRate.toFixed(2) + '%' : '—') +
              '</td>' +
              '</tr>',
          )
          .join('') +
        '</tbody></table>';
    }
  }

  // 2.5 Backfill warnings + no-URL historical footer
  const bf = document.getElementById('spores-backfill');
  if (bf) {
    const warnings = (s.backfillWarnings || []).slice(0, 10);
    const noUrl = s.noUrlHistorical || [];
    const noUrlFooter =
      noUrl.length > 0
        ? '<p class="muted" style="margin-top:0.8rem;font-size:0.8rem">🔒 ' +
          (isEn
            ? noUrl.length +
              ' historical spore(s) lack URL (permanent harvest gap): '
            : noUrl.length + ' 筆歷史孢子缺 URL（永久 harvest 缺口）：') +
          noUrl
            .map((w) => '#' + w.n + ' ' + (w.article || '').slice(0, 10))
            .join(' / ') +
          '</p>'
        : '';
    if (warnings.length === 0) {
      bf.innerHTML =
        '<p class="muted">' +
        (isEn ? 'All caught up.' : '全部回填完畢。') +
        '</p>' +
        noUrlFooter;
    } else {
      bf.innerHTML =
        '<ul class="spore-backfill-list">' +
        warnings
          .map((w) => {
            const color =
              w.status === 'OVERDUE'
                ? '🔴'
                : w.publishedDays >= 3
                  ? '🟡'
                  : '🟢';
            return (
              '<li>' +
              color +
              ' <strong>#' +
              w.n +
              ' ' +
              (w.article || '').slice(0, 20) +
              '</strong>' +
              ' <span class="platform-' +
              (w.platform || 'other') +
              '">' +
              (w.platform || '').toUpperCase() +
              '</span>' +
              ' <span class="muted">' +
              w.publishedDays +
              (isEn ? 'd ago' : ' 天前') +
              '</span>' +
              ' — ' +
              w.status +
              '</li>'
            );
          })
          .join('') +
        '</ul>' +
        noUrlFooter;
    }
  }

  // 2.6 Weekly pulse sparkline
  const wk = document.getElementById('spores-weekly');
  if (wk) {
    const weeks = s.weeklyPulse || [];
    if (weeks.length === 0) {
      wk.innerHTML = '<p class="muted">—</p>';
    } else {
      const maxPub = Math.max(...weeks.map((w) => w.published), 1);
      wk.innerHTML =
        '<div class="spore-weekly">' +
        weeks
          .map((w) => {
            const h = Math.max((w.published / maxPub) * 100, 5);
            return (
              '<div class="spore-week">' +
              '<div class="spore-week-bar-wrap">' +
              '<div class="spore-week-bar" style="height:' +
              h +
              '%"></div>' +
              '</div>' +
              '<div class="spore-week-count">' +
              w.published +
              '</div>' +
              '<div class="spore-week-label">' +
              w.week.slice(-3) +
              '</div>' +
              '</div>'
            );
          })
          .join('') +
        '</div>';
    }
  }
}

export { renderSpores };
