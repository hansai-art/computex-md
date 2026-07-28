/**
 * MJS mirror of src/config/languages.ts.
 *
 * Used by Node-direct scripts and Astro config:
 *  - astro.config.mjs
 *  - scripts/core/generate-dashboard-data.js
 *  - scripts/core/build-search-index.mjs (when refactored)
 *
 * For TypeScript files, import from `./languages` (resolver picks .ts).
 *
 * ⚠️ MUST stay in sync with languages.ts.
 *    `bash scripts/tools/check-language-registry-sync.sh` enforces this.
 *
 * Why two files: Vite SSR prerender chunks bundle the .mjs file but break
 * any filesystem-relative paths (so we can't read JSON via readFileSync).
 * Inlining the data in both files is the most reliable approach.
 */

export const LANGUAGES = [
  {
    code: 'zh-TW',
    displayName: '中文',
    hreflang: 'zh-Hant',
    isDefault: true,
    enabled: true,
  },
  {
    code: 'en',
    displayName: 'English',
    hreflang: 'en',
    enabled: true,
  },
];

export const ENABLED_LANGUAGE_CODES = LANGUAGES.filter((l) => l.enabled).map(
  (l) => l.code,
);

export const ALL_LANGUAGE_CODES = LANGUAGES.map((l) => l.code);

export const DEFAULT_LANGUAGE = LANGUAGES.find((l) => l.isDefault);

export const LANGUAGE_DISPLAY_NAMES = Object.fromEntries(
  LANGUAGES.map((l) => [l.code, l.displayName]),
);

export function getLanguage(code) {
  return LANGUAGES.find((l) => l.code === code);
}
