#!/usr/bin/env python3
"""article-depth-audit.py — 全站深度基準審核（2026-07-16 inbox-audit session 手工方法論的儀器化）

以「近期文章」的字數/腳註分佈為動態基準，找出嚴重低於基準的存量文章，
輸出排序清單供 ARTICLE-INBOX 深度重建 batch 補輪。

方法論 SSOT：reports/article-quality-audit-2026-07-16.md
資料源：public/api/dashboard-articles.json（wordCount / fnCount 由 prebuild 儀器化）
      + git log 首 commit 日期與首作者（--authors 時）

用法：
  python3 scripts/tools/article-depth-audit.py                 # 嚴重層（預設門檻）
  python3 scripts/tools/article-depth-audit.py --tier next    # 次一級門檻
  python3 scripts/tools/article-depth-audit.py --json         # 機器可讀
  python3 scripts/tools/article-depth-audit.py --authors      # 附首作者（較慢，跑 git log）

門檻不寫死絕對值：--wc/--fn 可覆蓋；預設「嚴重」= 字數 < 2500 且腳註 < 5
（= 近期 p25 兩維度同時失守，2026-07-16 校準），「next」= 3500 / 8。
"""
import argparse
import collections
import json
import statistics
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
DASHBOARD = ROOT / 'public/api/dashboard-articles.json'
RECENT_WINDOW_DAYS = 45  # 「近期基準」取 date 距今 45 天內的文章分佈


def load_rows():
    rows = [r for r in json.loads(DASHBOARD.read_text()) if r.get('date')]
    if not rows:
        sys.exit('dashboard-articles.json 空的——先跑 npm run prebuild')
    return rows


def recent_baseline(rows, today):
    import datetime as dt
    cutoff = (dt.date.fromisoformat(today) - dt.timedelta(days=RECENT_WINDOW_DAYS)).isoformat()
    recent = [r for r in rows if r['date'] >= cutoff]
    if len(recent) < 20:  # 樣本太少退回全站最新 60 篇
        recent = sorted(rows, key=lambda r: r['date'])[-60:]
    wc = sorted(r['wordCount'] for r in recent)
    fn = sorted(r['fnCount'] for r in recent)
    return {
        'n': len(recent), 'since': cutoff,
        'wc_median': statistics.median(wc), 'wc_p25': wc[len(wc) // 4],
        'fn_median': statistics.median(fn), 'fn_p25': fn[len(fn) // 4],
    }


def first_authors():
    """一次 git log 全樹掃描：每篇 zh 文章的首 commit 作者（newest-first 迭代，最後值 = 最舊）。"""
    out = subprocess.run(
        ['git', 'log', '--format=%x01%aN', '--name-only', '--', 'knowledge/'],
        capture_output=True, text=True, cwd=ROOT).stdout
    fa = {}
    cur = None
    for ln in out.split('\n'):
        if ln.startswith('\x01'):
            cur = ln[1:]
        elif ln.strip() and cur:
            p = ln.strip().split('/')
            if len(p) == 3 and p[0] == 'knowledge' and p[1] not in ('en', 'ja', 'ko', 'es', 'fr', 'all') and ln.endswith('.md'):
                fa[p[2][:-3]] = cur
    return fa


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument('--tier', choices=['severe', 'next'], default='severe')
    ap.add_argument('--wc', type=int, help='字數門檻覆蓋')
    ap.add_argument('--fn', type=int, help='腳註門檻覆蓋')
    ap.add_argument('--json', action='store_true')
    ap.add_argument('--authors', action='store_true', help='附首作者欄（跑 git log，較慢）')
    ap.add_argument('--today', default=None, help='YYYY-MM-DD（測試用）')
    args = ap.parse_args()

    import datetime as dt
    today = args.today or dt.date.today().isoformat()
    wc_t = args.wc or (2500 if args.tier == 'severe' else 3500)
    fn_t = args.fn or (5 if args.tier == 'severe' else 8)

    rows = load_rows()
    base = recent_baseline(rows, today)
    fa = first_authors() if args.authors else {}

    hits = []
    for r in rows:
        if r.get('category') == 'about':
            continue
        if r['wordCount'] < wc_t and r['fnCount'] < fn_t:
            hits.append({
                'slug': r['slug'], 'category': r['category'], 'date': r['date'],
                'wordCount': r['wordCount'], 'fnCount': r['fnCount'],
                'healthScore': r.get('healthScore'),
                'lastHumanReview': str(r.get('lastHumanReview')),
                'firstAuthor': fa.get(r['slug'], ''),
            })
    hits.sort(key=lambda x: x['wordCount'] + x['fnCount'] * 150)

    if args.json:
        print(json.dumps({'baseline': base, 'threshold': {'wc': wc_t, 'fn': fn_t},
                          'count': len(hits), 'hits': hits}, ensure_ascii=False, indent=1))
        return

    print(f"# article-depth-audit — {today}（tier={args.tier}：字數<{wc_t} 且 腳註<{fn_t}）")
    print(f"近期基準（{base['since']} 起 n={base['n']}）：字數中位 {base['wc_median']:.0f}／p25 {base['wc_p25']}"
          f"｜腳註中位 {base['fn_median']:.0f}／p25 {base['fn_p25']}")
    print(f"命中：{len(hits)} 篇\n")
    bycat = collections.Counter(h['category'] for h in hits)
    print('分類分佈：' + '、'.join(f'{c} {n}' for c, n in bycat.most_common()))
    print()
    for h in hits:
        a = f"／首作者 {h['firstAuthor']}" if h['firstAuthor'] else ''
        print(f"  {h['wordCount']:5d} 字｜{h['fnCount']:2d} 註｜{h['date']}｜{h['category']:12s}{a}｜{h['slug']}")
    print('\n消化去處：ARTICLE-INBOX「早期/貢獻者單薄文章 深度重建 batch」（哲宇 2026-07-16 directive）')


if __name__ == '__main__':
    main()
