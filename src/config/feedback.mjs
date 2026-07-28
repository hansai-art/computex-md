/**
 * feedback.mjs — Feedback 子系統設定（client-side，build 時由 Vite inline）。
 *
 * 設計：feedback 是「隔離失敗域」。本檔只決定 widget 用哪種 backend + 降級行為，
 * 任何錯誤都不該 bubble 到主站 render。所有值都是 PUBLIC（anon key 設計上可公開，
 * 真正的權限由 Supabase RLS 把關；service key 永遠不進前端）。
 *
 * 模式（PUBLIC_FEEDBACK_MODE）：
 *   - 'off'         → widget 完全不出現
 *   - 'github-only' → 只出現一顆「用 GitHub 回報」按鈕（純靜態 fallback，零 backend，永遠安全）
 *   - 'mock'        → 用瀏覽器內 MockBackend（localStorage），給 preview / e2e 測試用
 *   - 'supabase'    → 正式 backend（需 PUBLIC_SUPABASE_URL + PUBLIC_SUPABASE_ANON_KEY）
 *
 * 預設 'github-only'：哲宇還沒 provision Supabase 之前 ship 到 production 也 100% 安全
 * （讀者點回饋 → 連到既有 GitHub issue template）。哲宇 ratify 後設 PUBLIC_FEEDBACK_MODE=supabase
 * + 兩把 key 即上線，主站 build 不用改。
 */

// Vite/Astro 注入 import.meta.env；node 直跑時 fallback 成空物件。
const env =
  (typeof import.meta !== 'undefined' && import.meta && import.meta.env) || {};

export const FEEDBACK_MODE = env.PUBLIC_FEEDBACK_MODE || 'github-only';

export const SUPABASE_URL = env.PUBLIC_SUPABASE_URL || '';
export const SUPABASE_ANON_KEY = env.PUBLIC_SUPABASE_ANON_KEY || '';

/** 啟用哪些登入方式（順序 = UI 顯示順序）。email 一定保底（拿得到 email + 無需外部 OAuth app）。 */
export const FEEDBACK_PROVIDERS = (
  env.PUBLIC_FEEDBACK_PROVIDERS || 'google,github,email'
)
  .split(',')
  .map((s) => s.trim())
  .filter(Boolean);

export const GITHUB_REPO = 'frank890417/taiwan-md';
export const GITHUB_NEW_ISSUE_URL = `https://github.com/${GITHUB_REPO}/issues/new/choose`;

/**
 * 解析實際生效的 backend 種類（把「設了 supabase 但沒填 key」這種半成品狀態
 * 安全降級成 github-only）。
 */
export function resolveBackendKind() {
  if (FEEDBACK_MODE === 'off') return 'off';
  if (FEEDBACK_MODE === 'mock') return 'mock';
  if (FEEDBACK_MODE === 'supabase') {
    return SUPABASE_URL && SUPABASE_ANON_KEY ? 'supabase' : 'github-only';
  }
  return 'github-only';
}
