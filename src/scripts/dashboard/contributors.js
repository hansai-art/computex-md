import { isEn } from './shared.js';

// ── Contribution Leaderboard (2026-04-19 β) ──
function renderContributors(c) {
  if (!c) return;

  // Overview — 4 stat cards
  const overview = document.getElementById('contributors-overview');
  if (overview) {
    overview.innerHTML =
      '<div class="contributors-stats">' +
      [
        ['👥 ' + (isEn ? 'Total' : '總貢獻者'), c.totals.contributors],
        ['🔥 ' + (isEn ? 'Weekly active' : '週活躍'), c.weeklyActive],
        ['📅 ' + (isEn ? 'Monthly active' : '月活躍'), c.monthlyActive],
        [
          '🌱 ' + (isEn ? 'New (30d)' : '新人（30 天）'),
          c.recentlyJoined.length,
        ],
      ]
        .map(
          ([l, v]) =>
            '<div class="contributors-stat"><div class="contributors-stat-num">' +
            v +
            '</div><div class="contributors-stat-label">' +
            l +
            '</div></div>',
        )
        .join('') +
      '</div>';
  }

  // Leaderboard — top 20 card grid
  const board = document.getElementById('contributors-leaderboard');
  if (board) {
    const areaLabel = (a) => {
      const labels = isEn
        ? {
            content: '📝 Content',
            system: '⚙️ System',
            translation: '🌐 Translation',
            other: '• Other',
          }
        : {
            content: '📝 內容',
            system: '⚙️ 系統',
            translation: '🌐 翻譯',
            other: '• 其他',
          };
      return labels[a.primaryArea] || '—';
    };
    board.innerHTML =
      '<ol class="contributors-board">' +
      c.leaderboard
        .map((a, i) => {
          const rankBadge =
            i === 0 ? '🥇' : i === 1 ? '🥈' : i === 2 ? '🥉' : '#' + (i + 1);
          return (
            '<li class="contributors-row">' +
            '<span class="contributors-rank">' +
            rankBadge +
            '</span>' +
            '<a href="' +
            a.profileUrl +
            '" target="_blank" rel="noopener" class="contributors-person">' +
            '<img src="' +
            a.avatarUrl +
            '" alt="' +
            a.login +
            '" class="contributors-avatar" loading="lazy" />' +
            '<span class="contributors-login">' +
            a.login +
            '</span>' +
            '</a>' +
            '<span class="contributors-commits">' +
            a.commits.toLocaleString() +
            '<span class="contributors-unit"> ' +
            (isEn ? 'commits' : '次') +
            '</span></span>' +
            '<span class="contributors-area contributors-area-' +
            a.primaryArea +
            '">' +
            areaLabel(a) +
            '</span>' +
            '</li>'
          );
        })
        .join('') +
      '</ol>';
  }

  // Top by primary area (3 columns)
  const areas = document.getElementById('contributors-areas');
  if (areas) {
    const col = (title, emoji, list) =>
      '<div class="contributors-area-col">' +
      '<h4>' +
      emoji +
      ' ' +
      title +
      '</h4>' +
      (list.length > 0
        ? '<ol class="contributors-area-list">' +
          list
            .map(
              (a) =>
                '<li><a href="' +
                a.profileUrl +
                '" target="_blank" rel="noopener"><img src="' +
                a.avatarUrl +
                '" alt="" loading="lazy" /><span>' +
                a.login +
                '</span><span class="contributors-area-count">' +
                (a.breakdown
                  ? a.breakdown[
                      a.primaryArea === 'content'
                        ? 'content'
                        : a.primaryArea === 'system'
                          ? 'system'
                          : 'translation'
                    ]
                  : a.commits) +
                '</span></a></li>',
            )
            .join('') +
          '</ol>'
        : '<p class="contributors-empty">—</p>') +
      '</div>';
    areas.innerHTML =
      '<div class="contributors-areas-grid">' +
      col(isEn ? 'Content' : '內容', '📝', c.topContent) +
      col(isEn ? 'System' : '系統', '⚙️', c.topSystem) +
      col(isEn ? 'Translation' : '翻譯', '🌐', c.topTranslation) +
      '</div>';
  }

  // Recently joined
  const recent = document.getElementById('contributors-recent');
  if (recent) {
    if (c.recentlyJoined.length === 0) {
      recent.innerHTML =
        '<p class="contributors-empty">' +
        (isEn
          ? 'No new contributors in the last 30 days.'
          : '過去 30 天沒有新貢獻者。') +
        '</p>';
    } else {
      recent.innerHTML =
        '<div class="contributors-recent-grid">' +
        c.recentlyJoined
          .map((a) => {
            const dateStr = a.firstCommitAt
              ? a.firstCommitAt.slice(0, 10)
              : '—';
            return (
              '<a href="' +
              a.profileUrl +
              '" target="_blank" rel="noopener" class="contributors-recent-card">' +
              '<img src="' +
              a.avatarUrl +
              '" alt="' +
              a.login +
              '" loading="lazy" />' +
              '<div class="contributors-recent-meta">' +
              '<div class="contributors-recent-login">' +
              a.login +
              '</div>' +
              '<div class="contributors-recent-date">' +
              (isEn ? 'Joined ' : '加入於 ') +
              dateStr +
              '</div>' +
              '</div></a>'
            );
          })
          .join('') +
        '</div>';
    }
  }
}

export { renderContributors };
