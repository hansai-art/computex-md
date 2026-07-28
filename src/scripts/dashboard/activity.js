import { isEn, langPrefix } from './shared.js';

// ── Activity Feed ──
function renderActivityFeed(articles) {
  const feed = document.getElementById('activity-feed');
  // Sort by lastModified descending (git commit date), take top 10
  const recent = [...articles]
    .filter((a) => a.lastModified)
    .sort((a, b) => b.lastModified.localeCompare(a.lastModified))
    .slice(0, 10);

  if (recent.length === 0) {
    feed.textContent = isEn ? 'No recent activity' : '暫無最近活動';
    return;
  }

  feed.innerHTML = recent
    .map((a) => {
      const emoji = (a.revision || 0) > 1 ? '✏️' : '📄';
      const articleUrl = langPrefix + '/' + a.category + '/' + a.slug;
      const dateStr = a.lastModified || a.date || '';
      const subject = a.commitSubject || '';
      // Extract short action label from commit subject (e.g. "rewrite:", "fix:", "translate:")
      const actionMatch = subject.match(/^[🧬\s]*(?:\[semiont\]\s*)?(\w+):/);
      const actionLabel = actionMatch ? actionMatch[1] : '';
      const badgeHtml = actionLabel
        ? '<span class="feed-badge feed-badge-' +
          actionLabel +
          '">' +
          actionLabel +
          '</span>'
        : '';
      return (
        '<div class="feed-item">' +
        '<span class="feed-emoji">' +
        emoji +
        '</span>' +
        '<a href="' +
        articleUrl +
        '" target="_blank" rel="noopener" class="feed-title">' +
        a.title +
        '</a>' +
        badgeHtml +
        '<span class="feed-date">' +
        dateStr +
        '</span>' +
        '</div>'
      );
    })
    .join('');
}

export { renderActivityFeed };
