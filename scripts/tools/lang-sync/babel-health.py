#!/usr/bin/env python3
"""babel-health.py — 巴別塔多語器官健檢儀器（WARN 級，不設 gate）。

把 2026-07-18 首次完整巴別塔健檢（reports/babel-health-2026-07-18.md）的
六個掃描維度收成一支可重跑的指令。輸出診斷摘要，永遠 exit 0——
這是黃燈路線儀器（先 WARN 收數據，要升 HARD gate 需哲宇拍板 threshold）。

維度：
  coverage    — fresh/stale/metadata-stale/missing per lang（讀 _translation-status.json）
  yaml        — frontmatter YAML parse fail（含撇號家族分類）＋必填欄位＋translatedFrom 斷鏈
  footnote    — zh [^n]: 定義數 vs 各語翻譯（流失／完全歸零）
  ratio       — bytes 比實測百分位＋ <0.5 CRITICAL 截斷嫌疑
  zombie      — 同語言內 translatedFrom 被 ≥2 檔宣告（殭屍重複對）
  stub        — <1KB 檔（refusal 殘留）

用法：
  python3 scripts/tools/lang-sync/babel-health.py            # 全維度 markdown 摘要
  python3 scripts/tools/lang-sync/babel-health.py --json     # 機器可讀
  python3 scripts/tools/lang-sync/babel-health.py --dim yaml # 單維度
"""
from __future__ import annotations

import argparse
import json
import re
import sys
from collections import defaultdict
from pathlib import Path

ROOT = Path(__file__).resolve().parents[3]
KNOW = ROOT / "knowledge"

sys.path.insert(0, str(Path(__file__).resolve().parent))
from langs import ENABLED_TRANSLATION_LANGS  # noqa: E402

LANGS = ENABLED_TRANSLATION_LANGS

FM_RE = re.compile(r"^---\n(.*?)\n---\n", re.S)
TF_RE = re.compile(r"^translatedFrom:\s*['\"]?(.+?)['\"]?\s*$", re.M)
FN_DEF_RE = re.compile(r"^\[\^[^\]]+\]:", re.M)
REQUIRED_FIELDS = ["title", "description", "category", "translatedFrom"]
# 單引號值內含未跳脫撇號（'' 合法雙寫跳脫除外；\' 是非法 YAML 跳脫也算病）
APOS_LINE_RE = re.compile(r"^[A-Za-z_]+:\s*'(?:[^']|'')*[^'\s]'.*'|\\'")


def iter_lang_files(lang: str):
    d = KNOW / lang
    if d.is_dir():
        yield from sorted(d.rglob("*.md"))


def read(p: Path) -> str:
    try:
        return p.read_text(errors="ignore")
    except OSError:
        return ""


def scan_coverage() -> dict:
    status = KNOW / "_translation-status.json"
    if not status.exists():
        return {"error": "no _translation-status.json (跑 status.py 先)"}
    d = json.loads(status.read_text())
    return d.get("_meta", {}).get("summary", {})


def _is_apostrophe_family(fm: str) -> bool:
    for line in fm.splitlines():
        stripped = line.strip()
        if "\\'" in stripped:
            return True
        m = re.match(r"^[\w.-]+:\s*'(.*)$", stripped)
        if m:
            body = m.group(1)
            # 去掉合法的 '' 雙寫後，內部仍殘留奇數單引號 = 撇號病
            if "'" in body[:-1].replace("''", ""):
                return True
    return False


def scan_yaml() -> dict:
    try:
        import yaml  # noqa: PLC0415
    except ImportError:
        return {"error": "pyyaml unavailable"}
    out = {}
    for lang in LANGS:
        fail, apos, missing_fields, broken_tf = [], [], [], []
        total = 0
        for p in iter_lang_files(lang):
            total += 1
            txt = read(p)
            m = FM_RE.match(txt)
            rel = str(p.relative_to(KNOW))
            if not m:
                fail.append(rel)
                continue
            fm = m.group(1)
            try:
                data = yaml.safe_load(fm) or {}
            except Exception:
                fail.append(rel)
                if _is_apostrophe_family(fm):
                    apos.append(rel)
                continue
            missing = [f for f in REQUIRED_FIELDS if not data.get(f)]
            if missing:
                missing_fields.append(f"{rel} 缺 {','.join(missing)}")
            tf = data.get("translatedFrom")
            if tf and not (KNOW / str(tf)).exists():
                broken_tf.append(f"{rel} → {tf}")
        out[lang] = {
            "total": total,
            "yaml_fail": len(fail),
            "apostrophe_family": len(apos),
            "missing_fields": len(missing_fields),
            "broken_translatedFrom": len(broken_tf),
            "yaml_fail_files": fail,
            "broken_translatedFrom_files": broken_tf,
        }
    return out


def _tf_map(lang: str) -> dict[str, Path]:
    """translatedFrom zh path → translation file（後到者覆蓋，殭屍另掃）。"""
    m = {}
    for p in iter_lang_files(lang):
        mt = TF_RE.search(read(p)[:4000])
        if mt:
            m[mt.group(1)] = p
    return m


def iter_zh_files():
    for cat in sorted(KNOW.iterdir()):
        if not cat.is_dir() or cat.name in LANGS or cat.name.startswith(("_", ".")) or cat.name == "resources":
            continue
        for p in sorted(cat.glob("*.md")):
            if not p.name.startswith("_"):
                yield p


def scan_footnote() -> dict:
    out = {}
    maps = {lang: _tf_map(lang) for lang in LANGS}
    for lang in LANGS:
        loss, zero = [], []
        lost_total = 0
        for zh in iter_zh_files():
            zh_rel = str(zh.relative_to(KNOW))
            zh_defs = len(FN_DEF_RE.findall(read(zh)))
            if zh_defs == 0:
                continue
            tp = maps[lang].get(zh_rel)
            if tp is None:
                continue
            t_defs = len(FN_DEF_RE.findall(read(tp)))
            if t_defs < zh_defs:
                loss.append(f"{zh_rel} zh={zh_defs} {lang}={t_defs}")
                lost_total += zh_defs - t_defs
                if zh_defs >= 5 and t_defs == 0:
                    zero.append(zh_rel)
        out[lang] = {
            "loss_files": len(loss),
            "lost_defs_total": lost_total,
            "zeroed": len(zero),
            "zeroed_files": zero,
            "loss_detail": loss,
        }
    return out


def scan_ratio() -> dict:
    out = {}
    for lang in LANGS:
        ratios, critical = [], []
        for p in iter_lang_files(lang):
            mt = TF_RE.search(read(p)[:4000])
            if not mt:
                continue
            src = KNOW / mt.group(1)
            if not src.exists() or src.stat().st_size == 0:
                continue
            r = p.stat().st_size / src.stat().st_size
            ratios.append(r)
            if r < 0.5:
                critical.append(f"{p.relative_to(KNOW)} ratio={r:.3f}")
        ratios.sort()
        n = len(ratios)

        def pct(q):
            return round(ratios[min(n - 1, int(q * n))], 2) if n else None

        out[lang] = {
            "n": n,
            "p5": pct(0.05),
            "median": pct(0.5),
            "p95": pct(0.95),
            "critical_lt_0.5": len(critical),
            "critical_files": critical,
        }
    return out


def scan_zombie() -> dict:
    out = {}
    for lang in LANGS:
        claims = defaultdict(list)
        for p in iter_lang_files(lang):
            mt = TF_RE.search(read(p)[:4000])
            if mt:
                claims[mt.group(1)].append(str(p.relative_to(KNOW)))
        dupes = {k: v for k, v in claims.items() if len(v) > 1}
        out[lang] = {"zombie_groups": len(dupes), "detail": dupes}
    return out


def scan_stub() -> dict:
    out = {}
    for lang in LANGS:
        stubs = [str(p.relative_to(KNOW)) for p in iter_lang_files(lang) if p.stat().st_size < 1000]
        out[lang] = {"stubs": len(stubs), "files": stubs}
    return out


DIMS = {
    "coverage": scan_coverage,
    "yaml": scan_yaml,
    "footnote": scan_footnote,
    "ratio": scan_ratio,
    "zombie": scan_zombie,
    "stub": scan_stub,
}


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("--json", action="store_true")
    ap.add_argument("--dim", choices=sorted(DIMS), help="只跑單一維度")
    args = ap.parse_args()

    dims = [args.dim] if args.dim else list(DIMS)
    result = {d: DIMS[d]() for d in dims}

    if args.json:
        print(json.dumps(result, ensure_ascii=False, indent=1))
        return 0

    print("🧬 babel-health（WARN 級儀器，exit 永遠 0）")
    for dim, data in result.items():
        print(f"\n== {dim} ==")
        if "error" in data:
            print("  ⚠️", data["error"])
            continue
        for lang, v in data.items():
            if dim == "coverage":
                print(f"  {lang}: {v}")
            elif dim == "yaml":
                mark = "⚠️" if v["yaml_fail"] else "✅"
                print(
                    f"  {mark} {lang}: total={v['total']} yaml-fail={v['yaml_fail']}"
                    f" (撇號家族 {v['apostrophe_family']}) 缺欄位={v['missing_fields']}"
                    f" translatedFrom斷鏈={v['broken_translatedFrom']}"
                )
            elif dim == "footnote":
                mark = "⚠️" if v["zeroed"] else "✅"
                print(
                    f"  {mark} {lang}: 流失檔={v['loss_files']} 流失定義={v['lost_defs_total']}"
                    f" 完全歸零={v['zeroed']}"
                )
            elif dim == "ratio":
                mark = "⚠️" if v["critical_lt_0.5"] else "✅"
                print(
                    f"  {mark} {lang}: n={v['n']} p5={v['p5']} median={v['median']}"
                    f" p95={v['p95']} CRITICAL(<0.5)={v['critical_lt_0.5']}"
                )
            elif dim == "zombie":
                mark = "⚠️" if v["zombie_groups"] else "✅"
                print(f"  {mark} {lang}: 殭屍組={v['zombie_groups']} {v['detail'] if v['zombie_groups'] else ''}")
            elif dim == "stub":
                mark = "⚠️" if v["stubs"] else "✅"
                print(f"  {mark} {lang}: stub(<1KB)={v['stubs']} {v['files'] if v['stubs'] else ''}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
