/**
 * 站內連結一律輸出帶結尾斜線的形式。
 *
 * 為什麼（2026-07-30 量到）
 *   本站的 canonical 是 `https://computex.taiwanai.ngo/about/`（帶斜線）、
 *   sitemap 也是帶斜線，因為 Astro 的 build.format 預設是 'directory'
 *   （產出 about/index.html），Cloudflare Pages 對這種產物會把 /about
 *   用 308 轉到 /about/。
 *
 *   可是站內連結產出的是不帶斜線的形式：dist 掃出來 11,346 條不帶斜線
 *   對 1,129 條帶斜線，也就是九成的內鏈每一次點擊都先吃一個 308。
 *   爬蟲預算雙倍消耗，連 301/308 等於白丟一次權重。
 *
 *   同一類問題在 aiterms 是反過來（canonical 不帶斜線、Cloudflare 預設
 *   帶斜線），那邊是用 wrangler 的 assets.html_handling 修的；這邊
 *   canonical 與 sitemap 本來就對，所以修連結端就好，NEVER 反過來動
 *   canonical —— 那些網址已經被索引了。
 *
 * 不加斜線的情況
 *   - 空字串或 '/'：本來就是根
 *   - 帶副檔名（/llms.txt、/rss.xml、/foo.md）：那是檔案不是目錄
 *   - 已經有斜線
 *   - 不是以 '/' 開頭（相對路徑、外部網址、mailto: 之類）
 * hash 與 query 會先切下來，補完斜線再接回去。
 */
export function withTrailingSlash(path: string): string {
  if (!path.startsWith('/')) return path;

  const hashAt = path.indexOf('#');
  const queryAt = path.indexOf('?');
  let cut = -1;
  if (hashAt >= 0 && queryAt >= 0) cut = Math.min(hashAt, queryAt);
  else if (hashAt >= 0) cut = hashAt;
  else if (queryAt >= 0) cut = queryAt;

  const pathname = cut >= 0 ? path.slice(0, cut) : path;
  const rest = cut >= 0 ? path.slice(cut) : '';

  if (pathname === '' || pathname === '/') return path;
  if (pathname.endsWith('/')) return path;

  const lastSeg = pathname.slice(pathname.lastIndexOf('/') + 1);
  if (/\.[a-zA-Z0-9]{2,5}$/.test(lastSeg)) return path;

  return `${pathname}/${rest}`;
}
