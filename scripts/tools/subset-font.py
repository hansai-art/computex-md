#!/usr/bin/env python3
"""思源黑體（Noto Sans TC）子集化 + 缺字守門員。

為什麼要自己託管字體
────────────────────
2026-07-30 之前，字體鏈的第一順位是 'IBM Plex Sans'，但站上**從來沒有載入過
這個字體**（沒有 @font-face、沒有任何 CDN）。也就是說每一台沒裝 Plex 的機器
都是靜默 fallback 到系統字。開發者的 Mac 裝了 Noto Sans TC，所以他看到的是
思源黑體；訪客看到的是各自系統的預設字。「全站統一」在那個狀態下只在一台
機器上成立。

要讓它對所有人都成立，只有自己託管一途。全站 201 頁只用到約 1000 個字符，
子集化之後是幾十 KB，比外部請求便宜也比外部請求可靠。

為什麼是變數字體
────────────────
NotoSansTC[wght].ttf 一個檔涵蓋 100 到 900 全部字重。子集化之後仍然保留
wght 軸，所以 @font-face 只需要一條，粗體細體都從同一個檔來，不必為每個
字重各下載一次。

授權
────
Noto Sans TC 是 SIL Open Font License 1.1，明文允許子集化與網頁嵌入。
本腳本會把字體內嵌的授權字串印出來，不要跳過那一行。

用法
────
    # 產生子集（讀 dist/ 的實際用字）
    python3 scripts/tools/subset-font.py --build

    # 守門：檢查 dist/ 有沒有字體涵蓋不到的字（build 流程會跑）
    python3 scripts/tools/subset-font.py --check

需要 fonttools + brotli。系統 python 受 PEP 668 保護不能直接 pip install，
所以用 venv：

    python3 -m venv .venv-fonts
    .venv-fonts/bin/pip install fonttools brotli
    .venv-fonts/bin/python scripts/tools/subset-font.py --build
"""

import argparse
import pathlib
import re
import sys

ROOT = pathlib.Path(__file__).resolve().parents[2]
DIST = ROOT / 'dist'
OUT = ROOT / 'public' / 'fonts' / 'noto-sans-tc-subset.woff2'
MANIFEST = ROOT / 'scripts' / 'tools' / 'font-coverage.json'

# 來源字體。使用者自行安裝的 Google Noto 正式版（SIL OFL）。
SOURCES = [
    pathlib.Path.home() / 'Library/Fonts/NotoSansTC[wght].ttf',
    ROOT / 'vendor/fonts/NotoSansTC[wght].ttf',
]

# 一定要收進來的字，不管目前內容有沒有用到。理由：這些是排版與 UI 隨時
# 可能生出來的字符（數字、標點、箭頭、全形符號），漏掉會在某一頁突然破圖。
ALWAYS = set(
    ''.join(
        [
            ''.join(chr(c) for c in range(0x20, 0x7F)),  # 可見 ASCII 全部
            '　、。〈〉《》「」『』【】〔〕・…—～‧',  # 中文標點
            '‘’“”′″†‡§¶©®™°±×÷≈≠≤≥←↑→↓↔⇄∞',  # 常見符號
            '０１２３４５６７８９',  # 全形數字
            '％＋－＝／＼（）［］｛｝：；，．？！＃＆＠',  # 全形符號
        ]
    )
)

TAG_RE = re.compile(r'<script[^>]*>.*?</script>|<style[^>]*>.*?</style>|<[^>]+>', re.S)


def glyphs_in_dist() -> set:
    """dist/ 裡所有 HTML 的可見文字用到的字符集合。"""
    if not DIST.exists():
        sys.exit('✗ 找不到 dist/，請先 npm run build')
    chars = set()
    for f in DIST.rglob('*.html'):
        text = TAG_RE.sub(' ', f.read_text(encoding='utf-8', errors='ignore'))
        chars |= set(text)
    # 控制字元不需要字形
    return {c for c in chars if c.isprintable() and not c.isspace()} | ALWAYS


def find_source() -> pathlib.Path:
    for p in SOURCES:
        if p.exists():
            return p
    sys.exit(
        '✗ 找不到來源字體 NotoSansTC[wght].ttf。\n'
        '  從 https://fonts.google.com/noto/specimen/Noto+Sans+TC 下載，\n'
        '  放到 ~/Library/Fonts/ 或 vendor/fonts/ 任一處。'
    )


def build() -> None:
    from fontTools import subset
    from fontTools.ttLib import TTFont

    src = find_source()
    wanted = glyphs_in_dist()

    # 授權必須看過。子集化是再散布，不是本機使用。
    lic = TTFont(src)['name'].getDebugName(13) or '(字體沒有內嵌授權字串)'
    print(f'來源：{src}')
    print(f'授權：{lic[:110]}')

    OUT.parent.mkdir(parents=True, exist_ok=True)

    opts = subset.Options()
    opts.flavor = 'woff2'
    opts.desubroutinize = False
    # 保留變數軸：一個檔供應 100 到 900 全部字重
    opts.retain_gids = False
    opts.layout_features = ['*']
    opts.name_IDs = ['*']
    opts.notdef_outline = True

    font = subset.load_font(str(src), opts)
    subsetter = subset.Subsetter(options=opts)
    subsetter.populate(text=''.join(sorted(wanted)))
    subsetter.subset(font)

    # 兩件事一起做：
    #
    # 1. NotoSansTC[wght].ttf 的變數軸預設值是 100（Thin），不是 400。只要有
    #    任何一條路徑沒有明確指定字重（local() 命中、@font-face 的 font-weight
    #    描述子被忽略、字體被當成靜態字體處理），整頁就會變成髮絲細體。把預設
    #    釘在 400，「沒指定」的結果就是 Regular。
    #
    # 2. 全站實際只用到 400/500/600/700/800/900（grep 過），100-300 那一段的
    #    差異資料是純浪費。把軸裁成 400-900，檔案小一截，仍然是一個檔供應
    #    全部會用到的字重。
    #    ⚠️ 之後若有人寫 font-weight:300，會被夾到 400，不會壞版但會比預期粗。
    #       真的需要細體時把下界改回來並重跑本腳本。
    from fontTools.varLib import instancer

    instancer.instantiateVariableFont(font, {'wght': (400, 400, 900)}, inplace=True)

    subset.save_font(font, str(OUT), opts)

    size = OUT.stat().st_size
    print(f'字符數：{len(wanted)}')
    print(f'輸出：{OUT.relative_to(ROOT)}  {size / 1024:.1f} KB')
    if size > 900_000:
        sys.exit(f'✗ 子集 {size / 1024:.0f} KB 過大，首屏會被拖慢，檢查是否漏了子集化')

    # 把「這份子集涵蓋哪些字」寫成 manifest 給 build 用。
    #
    # 為什麼不讓 build 直接讀 woff2：那需要 fonttools，而 fonttools 裝在 venv 裡
    # （系統 python 受 PEP 668 擋著）。build 是 Node，不該依賴一個要手動建的
    # Python 環境 —— 那種相依性遲早會在某台機器上壞掉，然後守門員就被拿掉了。
    #
    # manifest 內含 woff2 的 sha256。Node 端會重算並比對，所以「有人換了字體檔
    # 卻沒重跑本腳本」會被抓到，manifest 不可能悄悄跟字體檔失聯。
    import hashlib
    import json

    digest = hashlib.sha256(OUT.read_bytes()).hexdigest()
    MANIFEST.write_text(
        json.dumps(
            {
                '_comment': '由 scripts/tools/subset-font.py --build 產生，不要手改',
                'font': str(OUT.relative_to(ROOT)),
                'sha256': digest,
                'bytes': size,
                'codepoints': sorted(ord(c) for c in wanted),
            },
            ensure_ascii=False,
        ),
        encoding='utf-8',
    )
    print(f'manifest：{MANIFEST.relative_to(ROOT)}（sha256 {digest[:12]}…）')
    print('✅ [font-subset] 完成')


def check() -> None:
    """守門員：內容長出字體沒有的字時，讓 build 紅燈，而不是靜默 fallback。

    這是整套自我託管方案的關鍵。子集是「照今天的內容」切的，明天多一家廠商
    就可能多出幾個字。沒有這道檢查的話，那幾個字會安靜地掉回系統字，畫面上
    看起來只是「有一個字長得不太一樣」，沒有人會發現。
    """
    from fontTools.ttLib import TTFont

    if not OUT.exists():
        sys.exit(f'✗ 找不到 {OUT.relative_to(ROOT)}，請先跑 --build')

    covered = set()
    for table in TTFont(OUT)['cmap'].tables:
        covered |= {chr(cp) for cp in table.cmap}

    missing = sorted(c for c in glyphs_in_dist() if c not in covered)
    if missing:
        shown = ''.join(missing[:60])
        sys.exit(
            f'✗ [font-subset] 有 {len(missing)} 個字不在子集裡，'
            f'這些字會掉回系統字：\n  {shown}\n'
            f'  修法：重跑 scripts/tools/subset-font.py --build 並 commit 新的 woff2'
        )
    print(f'✅ [font-subset] {len(covered)} 個字形涵蓋 dist 全部用字，無 fallback 破口')


if __name__ == '__main__':
    ap = argparse.ArgumentParser()
    ap.add_argument('--build', action='store_true')
    ap.add_argument('--check', action='store_true')
    a = ap.parse_args()
    if a.build:
        build()
    elif a.check:
        check()
    else:
        ap.error('需要 --build 或 --check')
