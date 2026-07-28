/**
 * widget.uxtest.mjs — FeedbackWidget UX (browser) test.
 *
 * Self-contained: spawns the mock dev server (feedback:devtest, port 4330),
 * drives the widget with Playwright chromium (the `playwright` pkg the repo
 * already uses in scripts/visual), asserts the key flows, tears down.
 *
 * Run: npm run feedback:uxtest   (or node tests/feedback/widget.uxtest.mjs)
 *
 * Flows covered:
 *   1. FAB renders
 *   2. open → article category chips (content/bug/newtopic)
 *   3. text selection → annotation pill → quote prefilled (type=content)
 *   4. lazy auth → Google + GitHub + Email options
 *   5. GitHub login → skips nickname (OAuth name) → done
 *   6. reopen → 我的回報 list shows the submission + status
 */
import { chromium } from 'playwright';
import { spawn } from 'node:child_process';
import { fileURLToPath } from 'node:url';
import { dirname, resolve } from 'node:path';

const ROOT = resolve(dirname(fileURLToPath(import.meta.url)), '../..');
const PORT = 4330;
const URL = `http://localhost:${PORT}/feedback-uxtest`;

let failures = 0;
function check(name, cond) {
  if (cond) {
    console.log(`  ✓ ${name}`);
  } else {
    console.error(`  ✗ ${name}`);
    failures++;
  }
}

function waitForServer(url, timeoutMs = 60000) {
  const start = Date.now();
  return new Promise((res, rej) => {
    const tick = async () => {
      try {
        const r = await fetch(url);
        if (r.ok) return res(true);
      } catch {
        /* not up yet */
      }
      if (Date.now() - start > timeoutMs)
        return rej(new Error('server timeout'));
      setTimeout(tick, 500);
    };
    tick();
  });
}

async function main() {
  console.log('[uxtest] starting mock dev server…');
  const server = spawn('npm', ['run', 'feedback:devtest'], {
    cwd: ROOT,
    env: { ...process.env, PUBLIC_FEEDBACK_MODE: 'mock' },
    stdio: 'ignore',
    detached: true,
  });
  let browser;
  try {
    await waitForServer(URL);
    console.log('[uxtest] server up; launching chromium…');
    browser = await chromium.launch();
    const page = await browser.newPage();
    await page.addInitScript(() => {
      try {
        localStorage.clear();
        sessionStorage.clear();
      } catch {}
    });
    await page.goto(URL, { waitUntil: 'networkidle' });

    // 1. FAB renders
    await page.waitForSelector('.twmd-fb-fab', { timeout: 10000 });
    check('1. FAB renders', !!(await page.$('.twmd-fb-fab')));

    // 2. open → article chips
    await page.click('.twmd-fb-fab');
    await page.waitForSelector('.twmd-fb-chip');
    const chipTypes = await page.$$eval('.twmd-fb-chip', (els) =>
      els.map((e) => e.getAttribute('data-type')),
    );
    check(
      '2. article chips = content/bug/newtopic',
      JSON.stringify(chipTypes) ===
        JSON.stringify(['content', 'bug', 'newtopic']),
    );

    // close, then 3. selection → pill → quote prefilled
    await page.click('.twmd-fb-x');
    const sel = await page.evaluate(async () => {
      const p = document.getElementById('para1');
      const range = document.createRange();
      range.selectNodeContents(p);
      const s = window.getSelection();
      s.removeAllRanges();
      s.addRange(range);
      document.dispatchEvent(new MouseEvent('mouseup', { bubbles: true }));
      await new Promise((r) => setTimeout(r, 150));
      return !!document.querySelector('.twmd-fb-selpill');
    });
    check('3a. selection pill appears', sel);
    await page.evaluate(() => {
      document
        .querySelector('.twmd-fb-selpill')
        ?.dispatchEvent(
          new MouseEvent('mousedown', { bubbles: true, cancelable: true }),
        );
    });
    await page.waitForSelector('.twmd-fb-quote blockquote');
    const quoteText = await page.$eval('.twmd-fb-quote blockquote', (e) =>
      e.textContent.trim(),
    );
    check('3b. quote prefilled from selection', quoteText.includes('臥虎藏龍'));
    const activeType = await page.$eval('.twmd-fb-chip.is-on', (e) =>
      e.getAttribute('data-type'),
    );
    check('3c. selection defaults type=content', activeType === 'content');

    // 4. fill body → submit → auth options
    await page.fill(
      '.twmd-fb-textarea[data-body]',
      '得獎年份應為 2001，不是 1990。',
    );
    await page.click('.twmd-fb-primary[data-submit]');
    await page.waitForSelector('[data-oauth="github"]');
    const hasGoogle = !!(await page.$('[data-oauth="google"]'));
    const hasGithub = !!(await page.$('[data-oauth="github"]'));
    const hasEmail = !!(await page.$('[data-email]'));
    check(
      '4. auth shows Google + GitHub + Email',
      hasGoogle && hasGithub && hasEmail,
    );

    // 5. GitHub login → skips nickname → done
    await page.click('[data-oauth="github"]');
    await page.waitForFunction(
      () => {
        const h = document.querySelector('.twmd-fb-panel .twmd-fb-head strong');
        return h && h.textContent.includes('🧬');
      },
      { timeout: 5000 },
    );
    const stored = await page.evaluate(() => {
      const items = JSON.parse(localStorage.getItem('twmd_fb_items') || '[]');
      const u = JSON.parse(localStorage.getItem('twmd_fb_user') || 'null');
      const r = items[items.length - 1] || {};
      return {
        count: items.length,
        type: r.type,
        pageKind: r.pageKind,
        hasFragment: (r.sourceUrl || '').includes('#:~:text='),
        email: u && u.email,
        nickname: localStorage.getItem('twmd_fb_nickname'),
      };
    });
    check(
      '5a. GitHub login skipped nickname → submitted',
      stored.count === 1 && stored.nickname === null,
    );
    check(
      '5b. quote/pageKind/fragment captured',
      stored.type === 'content' &&
        stored.pageKind === 'article' &&
        stored.hasFragment,
    );
    check(
      '5c. email captured (no email-leak path)',
      /@/.test(stored.email || ''),
    );

    // 6. reopen → 我的回報 list
    await page.click('.twmd-fb-fab'); // close done
    await page.click('.twmd-fb-fab'); // open form (logged in)
    await page.waitForSelector('[data-mine]', { timeout: 5000 });
    await page.click('[data-mine]');
    await page.waitForSelector('.twmd-fb-mineitem');
    const mineStatus = await page.$eval('.twmd-fb-minestatus', (e) =>
      e.textContent.trim(),
    );
    check('6. 我的回報 shows item with status', mineStatus.length > 0);
  } finally {
    if (browser) await browser.close();
    try {
      process.kill(-server.pid); // kill the dev-server process group
    } catch {}
  }

  console.log(
    `\n[uxtest] ${failures === 0 ? 'ALL PASS' : failures + ' FAILED'}`,
  );
  process.exit(failures === 0 ? 0 : 1);
}

main().catch((e) => {
  console.error('[uxtest] FATAL:', e);
  process.exit(1);
});
