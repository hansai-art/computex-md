/**
 * dashboard-client.js — /dashboard 全部 client-side 渲染邏輯
 *
 * 2026-06-13 refactor session 從 dashboard.template.astro 抽出（原 <script
 * define:vars={{ lang }}> 內嵌 2,729 行 × 6 語言頁各一份 inline copy）。
 * 抽成 Astro-processed module 後：bundle 一份 hashed .js 六頁共用 + 瀏覽器可快取，
 * 每頁 HTML 減 ~100KB。內容 1:1 verbatim 搬運（sed 行段抽取）。
 *
 * lang 來源改變：原 define:vars 注入 → 改讀 <html lang>（Layout 設定、
 * post-build-check 每 build 驗證六語言 lang attribute 正確性）。值域相同。
 *
 * 2026-07-24 modular split：各 section 抽成 src/scripts/dashboard/*.js ES modules，
 * 本檔變 thin orchestrator（fetch 8 endpoints + steps try/catch loop）。
 * VERBATIM move，零行為改動（唯一結構調整：allArticles 改經 setter 供給）。
 */
import { renderSectionTimestamps } from './dashboard/shared.js';
import { renderVitals } from './dashboard/vitals.js';
import { renderActivityFeed } from './dashboard/activity.js';
import { renderRegistry, setRegistryArticles } from './dashboard/registry.js';
import { renderOrganism, setOrganismArticles } from './dashboard/organism.js';
import { renderTranslations } from './dashboard/translation.js';
import { renderI18nCoverage } from './dashboard/i18n-coverage.js';
import { renderImmune } from './dashboard/immune.js';
import { renderSpores } from './dashboard/spores.js';
import { renderContributors } from './dashboard/contributors.js';
import { renderGrowth } from './dashboard/growth.js';
import { renderContentAnalysis } from './dashboard/content-analysis.js';
import { renderHealthDistribution } from './dashboard/health-distribution.js';
import { renderAnalytics } from './dashboard/analytics.js';
import { renderNextSteps } from './dashboard/next-steps.js';
import { renderFooter } from './dashboard/footer.js';

// ── Fetch all data ──
Promise.all([
  fetch('/api/dashboard-articles.json').then((r) => r.json()),
  fetch('/api/dashboard-vitals.json').then((r) => r.json()),
  fetch('/api/dashboard-organism.json').then((r) => r.json()),
  fetch('/api/dashboard-translations.json').then((r) => r.json()),
  fetch('/api/dashboard-i18n.json')
    .then((r) => r.json())
    .catch(() => null),
  fetch('/api/dashboard-analytics.json')
    .then((r) => r.json())
    .catch(() => null),
  fetch('/api/dashboard-spores.json')
    .then((r) => r.json())
    .catch(() => null),
  fetch('/api/contributors.json')
    .then((r) => r.json())
    .catch(() => null),
])
  .then(
    ([
      articles,
      vitals,
      organism,
      translations,
      i18nCoverage,
      analytics,
      spores,
      contributors,
    ]) => {
      setRegistryArticles(articles);
      setOrganismArticles(articles);
      // 各 section 資料更新時間（articles 共用 vitals.lastUpdated — 同批生成）
      renderSectionTimestamps({
        vitals: vitals && vitals.lastUpdated,
        articles: vitals && vitals.lastUpdated,
        organism: organism && organism.lastUpdated,
        translations: translations && translations.lastUpdated,
        i18n: i18nCoverage && i18nCoverage.generated,
        analytics: analytics && analytics.lastUpdated,
        spores: spores && spores.lastUpdated,
        contributors: contributors && contributors.lastUpdated,
      });
      const steps = [
        () => renderVitals(vitals),
        () => renderActivityFeed(articles),
        () => renderRegistry(articles),
        () => renderHealthDistribution(articles),
        () => renderOrganism(organism),
        () => renderTranslations(translations, vitals),
        () => {
          if (i18nCoverage) renderI18nCoverage(i18nCoverage);
        },
        () => renderImmune(articles, vitals),
        () => {
          if (spores) renderSpores(spores);
        },
        () => {
          if (contributors) renderContributors(contributors);
        },
        () => renderGrowth(articles),
        () => renderContentAnalysis(articles),
        () => {
          if (analytics) renderAnalytics(analytics);
        },
        () => renderNextSteps(articles, translations),
        () => renderFooter(vitals),
      ];
      steps.forEach((fn, i) => {
        try {
          fn();
        } catch (e) {
          console.error(`Dashboard render step ${i} failed:`, e);
        }
      });
    },
  )
  .catch((e) => console.error('Dashboard fetch failed:', e));
