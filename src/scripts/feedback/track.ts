/**
 * track.ts — feedback widget GA4 事件（safe gtag wrapper）。
 *
 * 對齊 Layout.astro 的 GA4 bootstrap（G-JGC5W00N7T）+ EventTracker 範式：
 * 所有事件 prefix `feedback_`，gtag 不在（ad blocker / private / 本機）→ silent no-op，
 * 全 try/catch 永不擋使用者動作。
 *
 * 用途：數據驅動自我進化飛輪 —— 事件流進 GA4 → EVOLVE / news-lens routine 讀
 * dashboard-analytics.json → 知道讀者怎麼用回報、哪類最多、哪種登入摩擦最低，
 * 回頭校正 widget + 內容優先序。
 *
 * 事件 taxonomy（stable，改名要同步更新 GA4 explorations）：
 *   feedback_open          { source: fab|selection, page_kind }
 *   feedback_selection_pill{ page_kind }
 *   feedback_type_select   { type, page_kind }
 *   feedback_login         { provider: google|github|email, page_kind }
 *   feedback_submit        { type, page_kind, has_quote, login_method }
 *   feedback_done          { type, page_kind }
 *   feedback_my_view       { }
 *   feedback_degraded      { reason: backend-null|submit-error|github-only }
 */
export function track(
  event: string,
  params: Record<string, unknown> = {},
): void {
  try {
    const g = (window as unknown as { gtag?: (...a: unknown[]) => void }).gtag;
    if (typeof g === 'function') g('event', `feedback_${event}`, params);
  } catch {
    /* GA 失敗不影響 widget */
  }
}
