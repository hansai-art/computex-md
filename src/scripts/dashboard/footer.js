import { isEn } from './shared.js';

// ── Footer ──
function renderFooter(vitals) {
  const el = document.getElementById('dashboard-footer');
  if (!el) return;
  const d = new Date(vitals.lastUpdated || Date.now());
  const formatted = d.toLocaleDateString(isEn ? 'en-US' : 'zh-TW', {
    year: 'numeric',
    month: 'long',
    day: 'numeric',
    hour: '2-digit',
    minute: '2-digit',
  });
  el.textContent = `${isEn ? 'Data generated' : '數據產生於'} ${formatted}`;
}

export { renderFooter };
