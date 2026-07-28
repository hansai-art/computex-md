#!/usr/bin/env python3
"""
terminology-apply.py — 詞庫審修安全執行器（用語保存計畫 Tier 2 落地）

讀一份 decisions（TSV：file<TAB>action<TAB>value），對 data/terminology/*.yaml 施作。
每一筆 decision 都是主 session（人在迴路）逐條 adjudicate 過的，不是 LLM 直接套用。
預設 dry-run，--apply 才寫。git 可逆，一個 commit 收攏方便觀察者 review/revert。

action：
  fix-taiwan   把 display.taiwan 改成 value（修亂碼/錯字，value = 正確台灣詞）
  fix-china    把 display.china 改成 value
  neutralize   把 display.china 設成 = display.taiwan（getStaticPaths 要求 china≠taiwan，
               因此該條被過濾、不再產生 nonsense 頁；非破壞、可逆，優於直接刪）
  delete       rm 該檔（僅限機械 cruft，保守使用）

用法：
  python3 scripts/tools/terminology-apply.py decisions.tsv          # dry-run
  python3 scripts/tools/terminology-apply.py decisions.tsv --apply  # 施作
"""
import sys, os, re, datetime

BASE = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
TERM_DIR = os.path.join(BASE, "data", "terminology")
TODAY = datetime.date.today().isoformat()


def set_display_line(text, key, value):
    """把 display.{key} 那一行的值換成 value（保留縮排/引號風格）。"""
    lines = text.split("\n")
    in_display = False
    for i, line in enumerate(lines):
        if re.match(r"^\S", line):
            in_display = line.startswith("display:")
        if in_display and re.match(rf"^\s+{key}:", line):
            indent = re.match(r"^(\s+)", line).group(1)
            # 保留原引號風格
            m = re.search(r":\s*(['\"]?)", line)
            q = m.group(1) if m else ""
            lines[i] = f"{indent}{key}: {q}{value}{q}"
            return "\n".join(lines), True
    return text, False


def get_display(text, key):
    lines = text.split("\n")
    in_display = False
    for line in lines:
        if re.match(r"^\S", line):
            in_display = line.startswith("display:")
        if in_display and re.match(rf"^\s+{key}:", line):
            v = line.split(":", 1)[1].strip()
            return v.strip("'\"")
    return ""


def bump_updated(text):
    if re.search(r"^updated:", text, re.M):
        return re.sub(r"^updated:.*$", f'updated: "{TODAY}"', text, flags=re.M)
    return text


def main():
    if len(sys.argv) < 2:
        print(__doc__); sys.exit(1)
    dfile = sys.argv[1]
    apply = "--apply" in sys.argv
    rows = []
    for ln in open(dfile, encoding="utf-8"):
        ln = ln.rstrip("\n")
        if not ln or ln.startswith("#"):
            continue
        parts = ln.split("\t")
        rows.append(parts + [""] * (3 - len(parts)))

    n_ok = n_skip = 0
    for f, action, value in rows:
        p = os.path.join(TERM_DIR, f)
        if not os.path.exists(p):
            print(f"  SKIP {f}: 檔不存在"); n_skip += 1; continue
        if action == "delete":
            print(f"  {'DELETE' if apply else 'would delete'} {f}")
            if apply:
                os.remove(p)
            n_ok += 1
            continue
        text = open(p, encoding="utf-8").read()
        tw = get_display(text, "taiwan")
        cn = get_display(text, "china")
        if action == "fix-taiwan":
            new, ok = set_display_line(text, "taiwan", value)
            desc = f"taiwan『{tw}』→『{value}』"
        elif action == "fix-china":
            new, ok = set_display_line(text, "china", value)
            desc = f"china『{cn}』→『{value}』"
        elif action == "neutralize":
            new, ok = set_display_line(text, "china", tw)
            desc = f"neutralize china『{cn}』→『{tw}』(=taiwan, 將被過濾)"
        else:
            print(f"  SKIP {f}: 未知 action {action}"); n_skip += 1; continue
        if not ok:
            print(f"  SKIP {f}: 找不到 display.{ 'china' if 'china' in action or action=='neutralize' else 'taiwan'} 行")
            n_skip += 1; continue
        new = bump_updated(new)
        print(f"  {'APPLY' if apply else 'dry '} {f}: {desc}")
        if apply:
            open(p, "w", encoding="utf-8").write(new)
        n_ok += 1

    print(f"\n{'[applied]' if apply else '[dry-run]'} ok={n_ok} skip={n_skip}"
          + ("" if apply else "  → 加 --apply 施作"))


if __name__ == "__main__":
    main()
