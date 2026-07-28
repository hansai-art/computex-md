#!/usr/bin/env python3
"""heal-passthrough-fields.py — 把 zh 的 passthrough 欄位機械性補回譯文。

為什麼存在（2026-07-25）：翻譯模型常漏抄 frontmatter 的 passthrough 欄位
（image / imageCredit / author / date / lastVerified …）。這些欄位**本來就
不該翻譯**，逐字照抄即可，模型漏掉純粹是它在長 prompt 裡的疏忽。但
verify-translation.py 把它算 hard fail，於是整篇好譯文被退掉重翻——一次
2-5 分鐘的 GPU 或 API 呼叫白費，而且下一輪模型很可能再漏一次同一欄。

實測（本輪 40 分鐘）：verify=1 占 21 次 fail，抽查全是 image/imageCredit
掉失；跨 es/fr/ko 三語同一篇同時中鏢，證明是模型的共同行為不是個案。
2026-07-24 也發生過同型事件，當時是手動 heal 八篇——沒有結構解，於是復發。

MANIFESTO §14 的直接延伸：能機械化檢查的就該能機械化修復。判斷力該用在
「這段翻譯好不好」，不是「這個 URL 有沒有被複製過去」。

用法：
  python3 heal-passthrough-fields.py <zh_path> <trans_path>        # 修一篇
  python3 heal-passthrough-fields.py <zh_path> <trans_path> --check # 只報不改
  python3 heal-passthrough-fields.py --lang es --all               # 掃全語言

exit code：0 = 無需修或已修好；1 = 有問題無法修（缺檔／YAML 壞）。
"""
from __future__ import annotations

import argparse
import re
import sys
from pathlib import Path

REPO = Path(__file__).resolve().parents[3]
KNOWLEDGE = REPO / "knowledge"

# 跟 verify-translation.py PASSTHROUGH 同一份清單（改那邊要改這邊——
# 兩處分歧正是今晚 leak-check 四個假陽性家族的根因，見 LESSONS 2026-07-25）
PASSTHROUGH = [
    "author", "date", "featured", "readingTime",
    "lastVerified", "lastHumanReview", "category",
    "image", "imageCredit", "difficulty",
]

FM_RE = re.compile(r"^(---\n)(.*?)(\n---\n)", re.S)


def parse_fm(text: str) -> tuple[str, str, str] | None:
    m = FM_RE.match(text)
    if not m:
        return None
    return m.group(1), m.group(2), m.group(3)


def field_value(fm_body: str, key: str) -> str | None:
    """單行純量欄位的原始字串（保留引號原樣——寫回時不改既有格式）。"""
    m = re.search(rf"^{re.escape(key)}:[ \t]*(.*)$", fm_body, re.M)
    if not m:
        return None
    v = m.group(1).rstrip()
    return v if v else None


def norm(v: str | None):
    """語意正規化後再比較——這支工具的判準必須跟 verify-translation.py 一致。

    2026-07-25 第一版用原始字串比，把 `category: 'Art'` 與 `category: Art`
    判成 drift，全站掃出約 2,400 篇「需要 heal」，其中大量是引號差異的假陽性。
    verify 用 yaml.safe_load 做語意比較，這裡不跟它同一把尺就會憑空造出工作
    ——正是今天四個 gate 假陽性家族的同型病，只是這次病在我自己剛寫的工具上。
    """
    if v is None:
        return None
    try:
        import yaml
        return yaml.safe_load(v)
    except Exception:
        return v.strip().strip("'\"")


def heal(zh_path: Path, trans_path: Path, check_only: bool = False) -> tuple[int, list]:
    if not zh_path.exists() or not trans_path.exists():
        return 1, [f"缺檔：{zh_path if not zh_path.exists() else trans_path}"]
    zh_parts = parse_fm(zh_path.read_text(encoding="utf-8"))
    tr_text = trans_path.read_text(encoding="utf-8")
    tr_parts = parse_fm(tr_text)
    if not zh_parts or not tr_parts:
        # 分清是哪一邊壞——2026-07-25 存量清償時五語各報一篇「解析失敗」，
        # 追下去全是同一個 zh 源（About/台灣官方網站資源.md，全站唯一無
        # frontmatter 的歷史遺留特例）。訊息不指名哪邊，讀起來像譯文壞了，
        # 差點往錯的方向修。
        side = "zh 源" if not zh_parts else "譯文"
        return 1, [f"frontmatter 解析失敗（{side}：{zh_path.name if not zh_parts else trans_path.name}）"]
    _, zh_body, _ = zh_parts
    head, tr_body, tail = tr_parts

    fixed = []
    new_body = tr_body
    for key in PASSTHROUGH:
        zh_v = field_value(zh_body, key)
        if zh_v is None:
            continue                      # zh 自己沒有這欄 → 譯文也不該有
        tr_v = field_value(new_body, key)
        if norm(tr_v) == norm(zh_v):
            continue                      # 語意已一致（引號/型別差異不算 drift）
        if tr_v is None:
            # 整欄缺失 → 補在 frontmatter 末尾
            new_body = new_body.rstrip() + f"\n{key}: {zh_v}"
            fixed.append(f"{key}（補回）")
        else:
            new_body = re.sub(rf"^{re.escape(key)}:[ \t]*.*$",
                              f"{key}: {zh_v}", new_body, count=1, flags=re.M)
            fixed.append(f"{key}（{tr_v[:20]} → zh 值）")

    if fixed and not check_only:
        trans_path.write_text(head + new_body + tail + tr_text[len(head + tr_body + tail):],
                              encoding="utf-8")
    return 0, fixed


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("zh_path", nargs="?")
    ap.add_argument("trans_path", nargs="?")
    ap.add_argument("--check", action="store_true")
    ap.add_argument("--lang")
    ap.add_argument("--all", action="store_true")
    args = ap.parse_args()

    if args.lang and args.all:
        import json
        tmap = json.loads((KNOWLEDGE / "_translations.json").read_text())
        total = healed = 0
        for lf, zf in sorted(tmap.items()):
            if not lf.startswith(f"{args.lang}/"):
                continue
            total += 1
            rc, fixed = heal(KNOWLEDGE / zf, KNOWLEDGE / lf, args.check)
            if fixed:
                healed += 1
                print(f"{'[dry] ' if args.check else ''}{lf}: {', '.join(fixed)}")
        print(f"\n{healed}/{total} 篇需要 heal（{args.lang}）")
        return 0

    if not args.zh_path or not args.trans_path:
        ap.error("需要 <zh_path> <trans_path> 或 --lang X --all")
    # 路徑慣例（跟 verify-translation.py / dispatcher 一致）：zh_path 相對
    # knowledge/（"Geography/花蓮縣.md"），trans_path 相對 repo 根
    # （"knowledge/es/..."）。2026-07-25 首版把 zh_path 也當相對 repo 根，
    # 於是 dispatcher 每次呼叫都找不到檔案 —— 而且 dispatcher 那端只看
    # stdout 不看 returncode，失敗被靜默吞掉，heal 掛了一整輪沒人發現。
    def resolve(raw: str, knowledge_relative: bool) -> Path:
        p = Path(raw)
        if p.is_absolute():
            return p
        if (REPO / raw).exists():
            return REPO / raw
        if knowledge_relative and (KNOWLEDGE / raw).exists():
            return KNOWLEDGE / raw
        return KNOWLEDGE / raw if knowledge_relative else REPO / raw

    rc, fixed = heal(resolve(args.zh_path, True), resolve(args.trans_path, False), args.check)
    if fixed:
        print(("需修：" if args.check else "已修：") + "、".join(fixed))
    return rc


if __name__ == "__main__":
    sys.exit(main())
