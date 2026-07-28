/**
 * selection.ts — 文章內文選字 → 浮出「🧬 勘誤這段」藥丸 → 回呼帶 quote + 深連結 anchor。
 *
 * 只在 article 頁啟用。anchor 用 W3C Text Fragment（`#:~:text=…`），維護者點 issue
 * 連結就自動捲到並高亮那段原文。短選取整段當 textStart；長選取用前後各 ~24 字
 * （`text=start,end`）提高命中率。任何錯誤都 swallow，不影響閱讀。
 */

export interface SelectionResult {
  quote: string;
  anchorUrl: string; // 該頁 URL + #:~:text=…
}

const MIN_LEN = 8; // 太短不觸發（避免誤觸）
const MAX_LEN = 1000;

function buildTextFragment(href: string, text: string): string {
  const clean = text.replace(/\s+/g, ' ').trim();
  const url = href.split('#')[0];
  const enc = (s: string) => encodeURIComponent(s.trim());
  if (clean.length <= 60) return `${url}#:~:text=${enc(clean)}`;
  const start = clean.slice(0, 24);
  const end = clean.slice(-24);
  return `${url}#:~:text=${enc(start)},${enc(end)}`;
}

export function initSelectionAnnotation(
  bodySelector: string,
  pillLabel: string,
  onPick: (r: SelectionResult) => void,
): void {
  try {
    const body = document.querySelector(bodySelector);
    if (!body) return;

    let pill: HTMLButtonElement | null = null;
    const removePill = () => {
      pill?.remove();
      pill = null;
    };

    const showPill = (x: number, y: number, result: SelectionResult) => {
      removePill();
      pill = document.createElement('button');
      pill.type = 'button';
      pill.className = 'twmd-fb-selpill';
      pill.textContent = pillLabel;
      pill.style.left = `${x}px`;
      pill.style.top = `${y}px`;
      pill.addEventListener('mousedown', (e) => {
        e.preventDefault(); // 保留選取、不讓 input 失焦
        e.stopPropagation();
        try {
          onPick(result);
        } catch {
          /* ignore */
        }
        removePill();
        window.getSelection()?.removeAllRanges();
      });
      document.body.appendChild(pill);
    };

    document.addEventListener('mouseup', (e) => {
      if (pill && e.target === pill) return;
      setTimeout(() => {
        try {
          const sel = window.getSelection();
          const text = (sel?.toString() || '').trim();
          if (!sel || sel.rangeCount === 0 || text.length < MIN_LEN) {
            removePill();
            return;
          }
          const range = sel.getRangeAt(0);
          if (!body.contains(range.commonAncestorContainer)) {
            removePill();
            return;
          }
          const rect = range.getBoundingClientRect();
          const quote = text.slice(0, MAX_LEN);
          const result: SelectionResult = {
            quote,
            anchorUrl: buildTextFragment(location.href, quote),
          };
          const x = Math.max(8, Math.min(rect.left, window.innerWidth - 130));
          const y = Math.max(8, rect.top - 40);
          showPill(x + window.scrollX, y + window.scrollY, result);
        } catch {
          removePill();
        }
      }, 0);
    });

    document.addEventListener('scroll', removePill, { passive: true });
    document.addEventListener('mousedown', (e) => {
      if (pill && e.target !== pill) removePill();
    });
  } catch {
    /* selection annotation 是 enhancement，壞掉不影響閱讀 */
  }
}
