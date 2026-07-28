/**
 * resolve-redirect-targets.mjs — 轉址目標 existence-aware 解析。
 *
 * 為什麼存在（2026-07-24）：astro.config 的合併轉址表生成 meta-refresh stub
 * 頁，stub 的 canonical 指向轉址目標。巴別塔行軍期間 quarantine 會反覆暫時
 * 刪除個別語言譯文——任何轉址目標的譯文被隔離，stub canonical 就變死鏈，
 * check-url-contract --strict 直接紅 CI（實例：en transportation-system 與
 * en industrial-transformation-from-manufacturing-to-innovation 同日被
 * quarantine，連炸四次部署）。
 *
 * 解法：build 時逐條檢查「語言文章型」目標是否真的存在（prebuilt
 * lang-switch-map registry = 磁碟真相的投影）。目標譯文不存在 → 用其他語言
 * 的 canonical-slug 別名反查 zh URL（zh canonical 永遠存在）退回 zh 版；
 * 反查不到 → drop + 警告。譯文之後被艦隊補回來，下一次 build 自動恢復直達。
 * 非文章型目標（/en/about、/map、錨點）原樣保留，不碰。
 */
import { readFileSync, readdirSync, existsSync } from 'node:fs';
import { join } from 'node:path';

export function resolveRedirectTargets(redirects, repoRoot = process.cwd()) {
  let map = null;
  try {
    map = JSON.parse(
      readFileSync(join(repoRoot, 'public/api/lang-switch-map.json'), 'utf-8'),
    );
  } catch {
    // fresh clone / prebuild 還沒跑 — 無從判斷存在性，原樣返回
    return redirects;
  }
  const registry = map.registry || {};
  const langs = map.languages || [];

  let folderBySlug = {};
  try {
    const folders = readdirSync(join(repoRoot, 'knowledge'), {
      withFileTypes: true,
    })
      .filter((e) => e.isDirectory() && /^[A-Z]/.test(e.name))
      .map((e) => e.name);
    folderBySlug = Object.fromEntries(folders.map((f) => [f.toLowerCase(), f]));
  } catch {
    return redirects;
  }

  const norm = (p) => {
    let s;
    try {
      s = decodeURIComponent(p);
    } catch {
      s = p;
    }
    if (s.length > 1 && s.endsWith('/')) s = s.slice(0, -1);
    return s;
  };

  const zhExists = (zhUrl) => {
    const parts = norm(zhUrl).split('/').filter(Boolean);
    if (parts.length !== 2) return false;
    const folder = folderBySlug[parts[0]];
    if (!folder) return false;
    return existsSync(join(repoRoot, 'knowledge', folder, parts[1] + '.md'));
  };

  // 目標長得像 /{lang}/{categorySlug}/{slug} 才做存在檢查
  const parseLangArticle = (target) => {
    const parts = norm(target).split('/').filter(Boolean);
    if (parts.length !== 3) return null;
    if (!langs.includes(parts[0])) return null;
    if (!folderBySlug[parts[1]]) return null;
    return { lang: parts[0], cat: parts[1], slug: parts[2] };
  };

  const langTargetExists = (lang, target) => {
    const reg = registry[lang];
    if (!reg) return false;
    return norm(target) in reg.toZh;
  };

  // 任一語言的同 cat/slug 別名 → zh URL（zh 檔還在才算）
  const zhFallbackFor = ({ cat, slug }) => {
    for (const L of langs) {
      const reg = registry[L];
      if (!reg) continue;
      const hit = reg.toZh[`/${L}/${cat}/${slug}`];
      if (hit && zhExists(hit)) return norm(hit) + '/';
    }
    return null;
  };

  const out = {};
  let kept = 0,
    rewritten = 0,
    dropped = 0;
  for (const [from, to] of Object.entries(redirects)) {
    const parsed = parseLangArticle(to);
    if (!parsed) {
      out[from] = to; // zh 目標與非文章型目標：手維時已驗證，原樣保留
      kept++;
      continue;
    }
    if (langTargetExists(parsed.lang, to)) {
      out[from] = to;
      kept++;
      continue;
    }
    const fb = zhFallbackFor(parsed);
    if (fb) {
      out[from] = fb;
      rewritten++;
      console.warn(
        `[redirects] ${parsed.lang} 目標譯文缺席，退 zh：${from} → ${fb}`,
      );
    } else {
      dropped++;
      console.warn(`[redirects] 目標無法解析，移除：${from} → ${to}`);
    }
  }
  if (rewritten || dropped) {
    console.warn(
      `[redirects] existence-aware：kept=${kept} rewritten=${rewritten} dropped=${dropped}`,
    );
  }
  return out;
}
