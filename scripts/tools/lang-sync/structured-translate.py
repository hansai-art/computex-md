#!/usr/bin/env python3
"""
structured-translate.py — Structured segmented translation engine (pilot, 2026-07-25).

哲宇 2026-07-25 directive: 前期預防取代事後修補。今天的三大 fail 家族——passthrough
欄位漏抄（category 被模型憑空改寫）、腳註編號飄移、引號跳出炸 YAML——全部源自「整篇
丟給模型，模型順便重排/漏抄結構」。

核心原則：**模型只翻文字，結構由工具持有。**

    - Frontmatter：passthrough 欄位（author/date/category/... 見 PASSTHROUGH，讀
      verify-translation.py 同源）工具機械複製，根本不進 prompt；只有 title/
      description/tags（+ subcategory 缺 i18n 對照時）送模型。YAML 由工具組裝
      （單引號 + 撇號雙寫跳脫），模型只回一段 JSON。
    - Footnotes：URL 與編號永遠不進 prompt，工具原樣保留；模型只收 {n, title, desc}
      JSON 陣列，只回 title/desc 譯文。條數 / URL byte-equal / 編號集合在構造上保證
      相等，不是驗證出來的。
    - Body：去除 frontmatter 與腳註定義行後，按 H2 切塊（無 H2 或塊 >6000 字元則
      退化為段落切塊，見 chunk_body()）。每塊獨立翻譯、獨立驗證（腳註引用集合 /
      cjk-leak-check / 字元 ratio 0.8-4.0），fail 只重翻該塊（最多 2 次重試），不是
      整篇重來——這是省算力的關鍵，也是跟舊 translate.py 整篇式最大的差異。
    - Assembly：工具拼三段 + prettier normalize + 跑現有三個驗證工具（verify-
      translation.py / cjk-leak-check.py / article-health.py --profile=pre-commit）
      當最後一道防線，不是主力——結構類錯誤在構造上已不可能發生。

Usage:
    python3 structured-translate.py Food/台灣咖啡文化.md --lang vi \\
        --backend openrouter:nvidia/nemotron-3-ultra-550b-a55b:free

    python3 structured-translate.py Food/台灣咖啡文化.md --lang vi \\
        --backend ollama:qwen3.6:35b-a3b-coding-nvfp4 --out /tmp/test.md

Backends reuse scripts/tools/lang-sync/backends/（OpenRouterBackend 有 5-key
rotation on 429；ollama 走本機 sovereignty backbone）。Prompt 素材（LANG_NAMES /
load_lang_guide_sections 動態抽 TRANSLATION-<lang>.md TL;DR）reuse自
openrouter-translate.py，避免另開一份會漂移的副本。

Pilot 產物 canonical 記錄：reports/structured-translation-pilot-2026-07-25.md
"""
from __future__ import annotations

import argparse
import datetime as _dt
import hashlib
import json
import re
import subprocess
import sys
import tempfile
import time
from datetime import datetime, timezone
from pathlib import Path
from typing import Optional

import yaml

SCRIPT_DIR = Path(__file__).resolve().parent           # scripts/tools/lang-sync
REPO = SCRIPT_DIR.parent.parent.parent
KNOWLEDGE = REPO / "knowledge"

sys.path.insert(0, str(SCRIPT_DIR))
from backends import (  # noqa: E402
    CodexBackend,
    GeminiBackend,
    OllamaBackend,
    OpenRouterBackend,
)
from importlib import import_module as _import_module  # noqa: E402

_or = _import_module("openrouter-translate")
load_lang_guide_sections = _or.load_lang_guide_sections
LANG_NAMES = _or.LANG_NAMES

_verify = _import_module("verify-translation")
PASSTHROUGH = _verify.PASSTHROUGH  # 同源 SSOT — author/date/featured/readingTime/
# lastVerified/lastHumanReview/category/image/imageCredit/difficulty

cjkleak = _import_module("cjk-leak-check")

import cross_link_localizer as _xlink  # noqa: E402 — 站內連結在地化（防新增，見 main() Phase B 前置處理）


# ────────────────── shared regex / constants ──────────────────

FN_DEF_RE = re.compile(r"(?m)^\[\^([^\]]+)\]:\s*(.*)$")
FN_CANON_RE = re.compile(r"^\[([^\]]+)\]\(([^)]+)\)(?:\s*—\s*(.*))?$")
INLINE_FN_REF_RE = re.compile(r"\[\^([^\]]+)\]")
MD_LINK_URL_RE = re.compile(r"\]\(([^)\s]+)\)")
EMBEDDED_LINK_RE = re.compile(r"\[([^\]]*)\]\(([^)]+)\)")

TRANSLATABLE_FM_FIELDS = ["title", "description", "tags"]

PILOT_ROOT = Path("/tmp/structured-pilot")


# ────────────────── backend selection ──────────────────

def build_backend(spec: str):
    """`<name>[:option]` → concrete backend instance (single backend, not a cascade —
    pilot wants isolated per-phase timing for ONE model, not cascade fallback noise)."""
    name, _, opt = spec.partition(":")
    name = name.strip()
    opt = opt.strip()
    if name == "openrouter":
        return OpenRouterBackend(model=opt or "openrouter/owl-alpha")
    if name == "ollama":
        return OllamaBackend(model=opt or None)
    if name == "codex":
        return CodexBackend()
    if name == "gemini":
        return GeminiBackend(model=opt) if opt else GeminiBackend()
    raise ValueError(f"unknown backend spec: {spec!r} (want openrouter:<model> | ollama:<model> | codex | gemini)")


# ────────────────── generic JSON-call helper (Phase F / N) ──────────────────

def _strip_fence(text: str) -> str:
    t = text.strip()
    if t.startswith("```"):
        t = re.sub(r"^```[a-zA-Z]*\n?", "", t, count=1)
        if t.endswith("```"):
            t = t[:-3]
    return t.strip()


# 2026-07-25 pilot 發現：nvidia/nemotron-3-ultra 系列是 reasoning 模型，不明確禁止
# 的話會把整段思考過程當 content 吐出來（15 條腳註的 batch 實測吐了 9000+ 字元的
# 「"著" -> "hệ thống" 好的...」式逐詞碎念，budget 燒光在思考、最終 JSON 被截斷），
# 而非單純「AI 加了 markdown fence」那種好處理的雜訊。系統層沒有 reasoning-exclude
# 開關（OpenRouterBackend 目前不透傳 reasoning 參數），所以在 prompt 層雙重防禦：
# (1) 明講「不要展示推理過程」；(2) parse 失敗時退化用括號配對法在雜訊中撈出最後一段
# 合法 JSON，而不是直接判失敗——這比單純 strip code fence 更能扛住 reasoning 模型。
_NO_REASONING_SUFFIX = (
    " Do not show your reasoning, chain-of-thought, or any explanation of your "
    "translation choices — output ONLY the final JSON, nothing else before or after it."
)


def _extract_json_loose(text: str):
    """json.loads 直接失敗時的退路：從文字裡找「最後一段」括號配對完整的 [...] 或
    {...} 子字串（reasoning 模型常把真正答案放在碎念之後）。找不到就讓例外往上拋，
    交給呼叫端的重試機制處理。"""
    for open_ch, close_ch in (("[", "]"), ("{", "}")):
        start = text.rfind(open_ch)
        while start != -1:
            depth = 0
            for i in range(start, len(text)):
                if text[i] == open_ch:
                    depth += 1
                elif text[i] == close_ch:
                    depth -= 1
                    if depth == 0:
                        candidate = text[start:i + 1]
                        try:
                            return json.loads(candidate)
                        except json.JSONDecodeError:
                            break
            start = text.rfind(open_ch, 0, start)
    raise json.JSONDecodeError("no balanced JSON substring found", text, 0)


def call_json(backend, system: str, user: str, *, max_tokens: int, timeout: int,
              max_attempts: int, metrics: dict, label: str):
    """Call backend, strip fence, parse JSON. Retries on parse failure (spec:
    「parse 失敗重試一次」→ max_attempts=2 covers 1 original + 1 retry)."""
    system = system + _NO_REASONING_SUFFIX
    last_err = None
    for attempt in range(1, max_attempts + 1):
        t0 = time.time()
        call_record = {"label": label, "attempt": attempt}
        try:
            raw = backend.translate(system, user, max_tokens=max_tokens, timeout=timeout)
        except Exception as e:  # noqa: BLE001 — any BackendError family
            last_err = f"backend error: {e}"
            call_record.update(ok=False, error=last_err, elapsed_s=round(time.time() - t0, 1))
            metrics.setdefault("calls", []).append(call_record)
            continue
        elapsed = round(time.time() - t0, 1)
        cleaned = _strip_fence(raw)
        try:
            data = json.loads(cleaned)
        except json.JSONDecodeError:
            try:
                data = _extract_json_loose(cleaned)
            except json.JSONDecodeError as e:
                last_err = f"JSON parse fail: {e}"
                call_record.update(ok=False, error=last_err, elapsed_s=elapsed)
                metrics.setdefault("calls", []).append(call_record)
                continue
        call_record.update(ok=True, elapsed_s=elapsed)
        metrics.setdefault("calls", []).append(call_record)
        return data
    raise RuntimeError(f"{label}: failed after {max_attempts} attempt(s) — {last_err}")


# ════════════════════════ Phase F — frontmatter ════════════════════════

def parse_zh_frontmatter(zh_content: str) -> tuple[dict, str]:
    """Returns (parsed_fm_dict_in_source_order, body_after_fm)."""
    if not zh_content.startswith("---"):
        raise ValueError("zh source missing opening frontmatter fence")
    end = zh_content.find("\n---", 3)
    if end == -1:
        raise ValueError("zh source missing closing frontmatter fence")
    fm_text = zh_content[3:end].strip("\n")
    body = zh_content[end + 4:]
    fm = yaml.safe_load(fm_text)
    if not isinstance(fm, dict):
        raise ValueError("zh frontmatter did not parse to a mapping")
    return fm, body


def yaml_single_quote(value) -> str:
    """單引號風格 + 撇號雙寫跳脫（129 檔 silent-OG-break 的教訓 — 這條規則本身就是
    今天要防的三大 fail 家族之一，本工具把它變成工具持有的機械操作，不靠模型遵守）。"""
    s = str(value)
    escaped = s.replace("'", "''")
    return f"'{escaped}'"


def render_scalar(value) -> str:
    """Passthrough 欄位機械複製：bool/int/float/date 保持裸值型別，字串走單引號跳脫。
    刻意不用 yaml.dump()（它的引號/換行風格跟本專案慣例不一致），手動組裝才能保證
    輸出跟 zh 來源同型別、同語意。"""
    if isinstance(value, bool):
        return "true" if value else "false"
    if isinstance(value, (int, float)):
        return str(value)
    if isinstance(value, _dt.date):
        return value.isoformat()
    if isinstance(value, list):
        # list 欄位（relatedDiary 等）逐元素跳脫成 inline flow list——
        # 2026-07-26 前這裡 fallthrough 到 yaml_single_quote(str(list))，
        # 產出 '[''a'', ''b'']' 這種「長得像 list 的單一字串」。不炸 YAML、
        # 不觸發 verify 的 PASSTHROUGH 檢查（未涵蓋 relatedDiary），是會
        # 靜默存活的型別走樣；裝甲常駐化後每次翻譯都會經過，重啟產線前必修。
        return "[" + ", ".join(render_scalar(v) for v in value) + "]"
    return yaml_single_quote(value)


def load_subcategory_i18n() -> dict:
    p = REPO / "src/data/subcategory-i18n.json"
    if not p.exists():
        return {}
    try:
        return json.loads(p.read_text(encoding="utf-8")).get("map", {})
    except Exception:  # noqa: BLE001
        return {}


def git_short_sha(zh_rel_path: str) -> str:
    try:
        r = subprocess.run(
            ["git", "log", "-1", "--format=%h", "--", f"knowledge/{zh_rel_path}"],
            cwd=REPO, capture_output=True, text=True, timeout=15,
        )
        sha = r.stdout.strip()
        return sha if sha else "pre-toolkit"
    except Exception:  # noqa: BLE001
        return "pre-toolkit"


def translate_frontmatter(zh_fm: dict, zh_content: str, zh_path: str, lang: str,
                           backend, metrics: dict) -> str:
    """Phase F. 只把 title/description/tags（+ subcategory 缺 i18n 對照時）送模型；
    其餘欄位工具機械複製，永遠不進 prompt。回傳組好的 YAML frontmatter 區塊文字
    （不含前後 --- fence，main() 負責包）。"""
    sub_i18n = load_subcategory_i18n()

    payload = {}
    for k in TRANSLATABLE_FM_FIELDS:
        if zh_fm.get(k) is not None:
            payload[k] = zh_fm[k]

    subcat_source = zh_fm.get("subcategory")
    subcat_mode = None       # 'i18n' (deterministic lookup) | 'model' (缺對照表, fallback)
    subcat_final = None
    if subcat_source:
        mapped = sub_i18n.get(subcat_source, {}).get(lang)
        if mapped:
            subcat_mode = "i18n"
            subcat_final = mapped
        else:
            # src/data/subcategory-i18n.json 目前只覆蓋 en/ja/ko/es/fr/vi/id/pt/hi
            # 9 語，ar/ru 是缺口（2026-07-25 pilot 發現）。缺對照表時退化成跟
            # title/description 同待遇送模型翻，而不是靜默留 zh 原文
            # （既有 pipeline 在 hi/Food/taiwan-coffee-culture.md 就留了一個
            # 「飲品文化」verbatim 沒翻的活案例 — 明明 i18n 表裡有 hi 對照）。
            subcat_mode = "model"
            payload["subcategory"] = subcat_source

    lang_name = LANG_NAMES.get(lang, lang)
    system = (
        f"You are translating ONLY the VALUES of specific frontmatter fields from "
        f"zh-TW to {lang_name} for COMPUTEX.md, an open-source curated knowledge base "
        "about Taiwan.\n\n"
        "Input is a JSON object. Return a JSON object with EXACTLY the same keys, "
        "same types (string stays string, array stays array with identical length "
        "and order), values translated to the target language. No commentary, no "
        "markdown code fence — JSON only, nothing else.\n"
        "- 'title'/'description': natural accurate translation, no machine-translate "
        "tells, no added or invented facts.\n"
        "- 'tags': translate each tag value; the array length MUST stay identical.\n"
        "- 'subcategory' (if present): a short category label (1-3 words), same "
        "register as 'tags'.\n"
    )
    user = json.dumps(payload, ensure_ascii=False)

    # 2026-07-25 pilot 發現（賴和.md → vi 重跑）：description 出現「đối抗」這種單字
    # 級 CJK 殘留（「抗」黏在越南文字尾），validate_frontmatter_block() 抓得到，但
    # 舊版只在 call_json 內對「JSON parse 失敗」重試，語意層的殘留字完全沒有回饋
    # 迴路。這裡補上跟 Phase B 一樣的「驗證 → 帶著問題重翻」迴圈，而不是驗完就算了。
    content_retry_system = system
    for content_attempt in range(1, 3):
        data = call_json(backend, content_retry_system, user, max_tokens=4000, timeout=180,
                          max_attempts=2, metrics=metrics, label=f"phase-F-content{content_attempt}")

        for k in payload:
            if k not in data:
                raise RuntimeError(f"phase-F: model response missing key {k!r}")
        if "tags" in payload:
            if not isinstance(data["tags"], list) or len(data["tags"]) != len(payload["tags"]):
                raise RuntimeError(
                    f"phase-F: tags length mismatch (zh={len(payload['tags'])}, "
                    f"out={len(data.get('tags', [])) if isinstance(data.get('tags'), list) else 'non-list'})"
                )

        leaks = []
        if lang not in ("ja", "ko"):
            for fk in ("title", "description"):
                if fk in data and _verify.has_cjk(str(data[fk])):
                    leaks.append(fk)
            if "tags" in data and any(_verify.has_cjk(str(t)) for t in data.get("tags", [])):
                leaks.append("tags")
        if not leaks or content_attempt == 2:
            break
        content_retry_system = system + (
            f"\n\nYour previous answer left untranslated zh-TW characters inside: "
            f"{', '.join(leaks)}. Re-translate ALL fields fully into {lang_name} — "
            "no Chinese characters should remain anywhere in the output."
        )

    if subcat_mode == "model":
        subcat_final = str(data.get("subcategory", subcat_source))

    lines: list[str] = []
    for key in zh_fm.keys():
        if key == "title":
            lines.append(f"title: {yaml_single_quote(str(data['title']))}")
        elif key == "description":
            lines.append(f"description: {yaml_single_quote(str(data['description']))}")
        elif key == "tags":
            lines.append("tags:")
            lines.append("  [")
            for t in data.get("tags", []):
                lines.append(f"    {yaml_single_quote(str(t))},")
            lines.append("  ]")
        elif key == "subcategory":
            lines.append(f"subcategory: {yaml_single_quote(str(subcat_final))}")
        elif key in PASSTHROUGH:
            lines.append(f"{key}: {render_scalar(zh_fm[key])}")
        else:
            # 沒被明確歸類的欄位（既有 schema 之外）— 安全網機械複製，
            # 寧可過度保留也不要靜默丟欄位。
            lines.append(f"{key}: {render_scalar(zh_fm[key])}")

    lines.append(f"translatedFrom: {yaml_single_quote(zh_path)}")
    lines.append(f"sourceCommitSha: {yaml_single_quote(git_short_sha(zh_path))}")
    content_hash = hashlib.sha256(zh_content.encode("utf-8")).hexdigest()[:16]
    lines.append(f"sourceContentHash: 'sha256:{content_hash}'")
    lines.append(f"translatedAt: {yaml_single_quote(datetime.now(timezone.utc).isoformat())}")

    return "\n".join(lines)


def validate_frontmatter_block(fm_block_text: str, lang: str) -> list[str]:
    """yaml.safe_load 可解析 + title/description 非空 + 非 ja/ko 時不含 CJK。"""
    problems = []
    try:
        parsed = yaml.safe_load(fm_block_text)
    except Exception as e:  # noqa: BLE001
        return [f"YAML parse fail: {e}"]
    if not isinstance(parsed, dict):
        return ["YAML did not parse to a mapping"]
    title = str(parsed.get("title", ""))
    desc = str(parsed.get("description", ""))
    if not title.strip():
        problems.append("title empty")
    if not desc.strip():
        problems.append("description empty")
    if lang not in ("ja", "ko"):
        if _verify.has_cjk(title):
            problems.append("title contains CJK")
        if _verify.has_cjk(desc):
            problems.append("description contains CJK")
    return problems


# ════════════════════════ Phase N — footnotes ════════════════════════

def _protect_embedded_links(text: str) -> tuple[str, list[tuple[str, str]]]:
    """desc 內偶有第二個 markdown 連結（例如賴和.md [^3] 同時引 臺灣記憶 + Open
    Museum 兩個來源）——FN_CANON_RE 只保護「第一個」[title](url)，第二個連結的 URL
    會被當成普通文字送進 desc payload。這裡把 desc 內所有殘留連結的 URL 也用
    token 保護起來，翻完再原樣還原，不靠模型遵守指令。"""
    items: list[tuple[str, str]] = []

    def repl(m: re.Match) -> str:
        idx = len(items)
        token = f"@@LINK{idx}@@"
        items.append((token, m.group(2)))
        return f"[{m.group(1)}]({token})"

    protected = EMBEDDED_LINK_RE.sub(repl, text)
    return protected, items


def _restore_embedded_links(text: str, items: list[tuple[str, str]]) -> str:
    for token, url in items:
        text = text.replace(token, url)
    return text


def extract_footnote_defs(body: str) -> list[dict]:
    """Regex 抽出所有 [^N]: ... 定義行，解析成 {n, title, url, desc}（canonical 格式
    參考 footnote-format-fix.py）。保留原始文件出現順序（賴和.md 的定義行不是照
    數字序排的，重組時要照抄這個順序，不是照 n 排序）。"""
    defs = []
    for m in FN_DEF_RE.finditer(body):
        n = m.group(1)
        rest = m.group(2).strip()
        canon = FN_CANON_RE.match(rest)
        if canon:
            title, url, desc = canon.group(1), canon.group(2), (canon.group(3) or "")
        else:
            url_m = re.search(r"https?://\S+", rest)
            url = url_m.group(0).rstrip(".,，。、") if url_m else ""
            title = rest[: url_m.start()].strip(" —-") if url_m else rest
            desc = ""
        desc_protected, link_restore = _protect_embedded_links(desc)
        defs.append({
            "n": n,
            "title": title.strip(),
            "url": url.strip(),
            "desc": desc_protected.strip(),
            "_link_restore": link_restore,
        })
    return defs


def translate_footnotes(defs: list[dict], lang: str, backend, metrics: dict) -> dict:
    """模型只收 JSON 陣列的 {n, title, desc}；URL 與編號工具原樣保留，永遠不進
    prompt。一批最多 15 條，超過分批（spec 硬性要求）。"""
    if not defs:
        return {}
    lang_name = LANG_NAMES.get(lang, lang)
    out: dict[str, dict] = {}
    batch_size = 15
    n_batches = (len(defs) + batch_size - 1) // batch_size
    for bi in range(n_batches):
        batch = defs[bi * batch_size: (bi + 1) * batch_size]
        payload = [{"n": d["n"], "title": d["title"], "desc": d["desc"]} for d in batch]
        system = (
            f"Translate ONLY the 'title' and 'desc' fields of each footnote source "
            f"entry from zh-TW to {lang_name}, for COMPUTEX.md (open-source Taiwan "
            "knowledge base). Keep 'n' UNCHANGED — it is an id, not content, copy it "
            "verbatim. Any token shaped like @@LINKn@@ inside 'desc' is a protected "
            "URL placeholder — keep it byte-for-byte unchanged, do not translate or "
            "remove it.\n"
            "Return a JSON array, same length and same order as the input array, each "
            "object with EXACTLY the keys 'n', 'title', 'desc'. No commentary, no "
            "markdown code fence — JSON only.\n"
            "- 'title': the source's title, translated (keep proper nouns / "
            "publication names recognizable).\n"
            "- 'desc': a short one-line description of what the source documents."
        )
        user = json.dumps(payload, ensure_ascii=False)
        data = call_json(backend, system, user, max_tokens=8000, timeout=240,
                          max_attempts=2, metrics=metrics, label=f"phase-N-batch{bi}")
        # 模型常把正確陣列包成 `{"footnotes": [...]}` / `{"translations": [...]}`。
        # v1.6 fallback 實績 4 篇在這裡被判成「got dict」，但內容沒有機會進入
        # 後面的長度與 ID 驗證。只接受「物件內恰好一個 list」這個高信心形狀；
        # 多個 list、任意 mapping 仍拒收，避免猜錯欄位後靜默對位。
        if isinstance(data, dict):
            list_values = [value for value in data.values() if isinstance(value, list)]
            if len(list_values) == 1:
                data = list_values[0]
        if not isinstance(data, list) or len(data) != len(batch):
            raise RuntimeError(
                f"phase-N batch {bi}: length mismatch (want {len(batch)}, "
                f"got {len(data) if isinstance(data, list) else type(data).__name__})"
            )
        by_n = {str(item.get("n")): item for item in data if isinstance(item, dict)}
        for idx, d in enumerate(batch):
            item = by_n.get(str(d["n"]))
            if item is None:
                item = data[idx] if idx < len(data) and isinstance(data[idx], dict) else {}
            title = str(item.get("title", d["title"]))
            desc = str(item.get("desc", d["desc"]))
            desc = _restore_embedded_links(desc, d["_link_restore"])
            out[d["n"]] = {"title": title, "desc": desc}
    return out


def validate_footnotes(defs: list[dict], translated: dict) -> list[str]:
    """條數相等 / URL byte-equal（保證成立，因為 url 從沒進 prompt）/ 編號集合相等
    ——構造上保證，這裡是雙重確認不是主要防線。"""
    problems = []
    if len(translated) != len(defs):
        problems.append(f"count mismatch: zh={len(defs)} translated={len(translated)}")
    orig_ids = {d["n"] for d in defs}
    trans_ids = set(translated.keys())
    if orig_ids != trans_ids:
        problems.append(f"id set mismatch: missing={orig_ids - trans_ids} extra={trans_ids - orig_ids}")
    return problems


def assemble_footnote_defs(defs: list[dict], translated: dict) -> str:
    lines = []
    for d in defs:
        t = translated.get(d["n"], {"title": d["title"], "desc": d["desc"]})
        title, desc = t["title"], t["desc"]
        if not d["url"]:
            # 2026-07-25 pilot 發現（台灣咖啡文化.md [^3]/[^7]/[^9] 等）：來源本來
            # 就是純文字引註，沒有 URL（「散見於台灣飲食文化研究及地方誌」這種泛引）
            # ——硬包成 [title]() 會產生殘破的空連結。原樣保留純文字格式，不強加
            # markdown link 容器。
            lines.append(f"[^{d['n']}]: {title}" + (f" — {desc}" if desc else ""))
        elif desc:
            lines.append(f"[^{d['n']}]: [{title}]({d['url']}) — {desc}")
        else:
            lines.append(f"[^{d['n']}]: [{title}]({d['url']})")
    return "\n\n".join(lines)


# ════════════════════════ Phase B — body ════════════════════════

def strip_footnote_defs(body: str) -> str:
    return FN_DEF_RE.sub("", body)


def _split_paragraphs(text: str, max_chars: int) -> list[str]:
    """段落切塊 + bin-packing：累積段落直到接近 max_chars 才切下一塊，避免小文章
    被拆成一堆浪費呼叫次數的微型 chunk。"""
    paras = re.split(r"\n{2,}", text)
    chunks: list[str] = []
    buf: list[str] = []
    buf_len = 0
    for p in paras:
        if not p.strip():
            continue
        p_len = len(p) + 2
        if buf and buf_len + p_len > max_chars:
            chunks.append("\n\n".join(buf))
            buf, buf_len = [], 0
        buf.append(p)
        buf_len += p_len
    if buf:
        chunks.append("\n\n".join(buf))
    return [c for c in chunks if c.strip()]


def chunk_body(body: str, max_chars: int = 6000) -> list[str]:
    """按 H2（## ）切塊；無 H2 或塊 >6000 字元則退化為段落切塊。"""
    h2_positions = [m.start() for m in re.finditer(r"(?m)^## ", body)]
    if not h2_positions:
        return _split_paragraphs(body, max_chars)

    blocks = []
    if h2_positions[0] > 0:
        head = body[: h2_positions[0]]
        if head.strip():
            blocks.append(head)
    bounds = h2_positions + [len(body)]
    for i in range(len(h2_positions)):
        blocks.append(body[bounds[i]: bounds[i + 1]])

    final: list[str] = []
    for b in blocks:
        if len(b) > max_chars:
            final.extend(_split_paragraphs(b, max_chars))
        else:
            final.append(b)
    final = [b for b in final if b.strip()]

    # 2026-07-25 pilot 發現（台灣咖啡文化.md → vi）：文末「## 參考資料」單獨成一個
    # H2 chunk 時 zh 只有 ~40 字元，翻譯輸出自然也很短——OpenRouterBackend 對
    # <100 字元輸出有一個「疑似 refusal」的保守判定（設計是給整篇翻譯用的，沒預期
    # chunk 級別呼叫），把合法的短輸出誤判成拒答，整個 heading 因此從輸出消失。
    # 把過小的 chunk（<300 字元，通常就是孤立的標題行）併回前一塊，結構性地
    # 避免孤立小塊觸發這個誤判，而不是每次都要靠重試僥倖過關。
    MIN_CHUNK_CHARS = 300
    merged: list[str] = []
    for b in final:
        if merged and len(b) < MIN_CHUNK_CHARS:
            merged[-1] = merged[-1].rstrip("\n") + "\n\n" + b.lstrip("\n")
        else:
            merged.append(b)
    return merged


def _cjk_leak_hits(text: str, lang: str, tmp_dir: Path) -> list[str]:
    """Reuse cjk-leak-check.py 的 scan_file（不重寫偵測邏輯）。寫到一個固定暫存檔
    （每次覆寫），path 含 knowledge/<lang>/ 讓它自己的 detect_lang 也答對，但這裡
    直接傳 lang= 顯式覆寫，不依賴路徑猜測。"""
    tmp_file = tmp_dir / "knowledge" / lang / "_chunk" / "chunk.md"
    tmp_file.parent.mkdir(parents=True, exist_ok=True)
    tmp_file.write_text(text, encoding="utf-8")
    return cjkleak.scan_file(tmp_file, lang=lang)


def _validate_chunk(zh_chunk: str, out: str, zh_refs: set, lang: str, tmp_dir: Path) -> list[str]:
    issues = []
    if not out.strip():
        return ["empty output"]
    out_refs = set(INLINE_FN_REF_RE.findall(out))
    if out_refs != zh_refs:
        issues.append(f"footnote ref set mismatch: zh={sorted(zh_refs)} out={sorted(out_refs)}")
    # 2026-07-25 pilot 發現（地震.md → vi）：body chunk 送進模型前已經把所有
    # [^N]: 定義行剝掉（Phase N 專屬），但某次輸出裡模型自己「腦補」出兩行假的
    # `[^9]: 腳註內容將在最終輸出中保留原位` 之類的偽定義——不是抄漏，是純幻覺，
    # 組裝後跟 Phase N 真定義重複，footnote count 從 20 變 22。zh_chunk 依構造
    # 保證不含任何 [^N]: 定義行，output 若出現就是模型無中生有，這裡直接攔。
    if FN_DEF_RE.search(out):
        issues.append("hallucinated footnote definition line(s) in body output (should only contain reference markers)")
    ratio = len(out) / max(len(zh_chunk), 1)
    if not (0.8 <= ratio <= 4.0):
        issues.append(f"ratio out of band [0.8,4.0]: {ratio:.2f}")
    hits = _cjk_leak_hits(out, lang, tmp_dir)
    if hits:
        issues.append(f"cjk leak: {hits[0]}")
    # 2026-07-25 production 首小時發現（張雨生 → hi 等 4 例 verify=1）：模型會
    # 掉「行內 markdown 連結」——zh 15 個 URL 譯文只剩 9 個。腳註引用有集合
    # 驗證、URL 沒有，正是設計還沒收編的最後一類結構物。用 multiset 比對
    # （同一 URL 可合法出現多次），少一個都擋下重試。
    from collections import Counter
    zh_urls = Counter(MD_LINK_URL_RE.findall(zh_chunk))
    out_urls = Counter(MD_LINK_URL_RE.findall(out))
    if zh_urls != out_urls:
        missing = list((zh_urls - out_urls).keys())[:3]
        extra = list((out_urls - zh_urls).keys())[:3]
        issues.append(f"inline link URL mismatch: missing={missing} extra={extra}")
    return issues


def translate_body_chunks(chunks: list[str], lang: str, backend, fn_glossary: dict,
                           metrics: dict) -> tuple[list[str], list[dict]]:
    guide = load_lang_guide_sections(lang, max_chars=6000)
    glossary_text = ""
    if fn_glossary:
        titles = [v["title"] for v in fn_glossary.values() if v.get("title")]
        if titles:
            glossary_text = (
                "已翻譯的腳註來源標題（術語一致性參考，不必逐字套用）：\n"
                + "\n".join(f"- {t}" for t in titles[:40])
            )

    lang_name = LANG_NAMES.get(lang, lang)
    base_system = (
        f"You are translating an article body from zh-TW to {lang_name} for "
        "COMPUTEX.md, an open-source curated knowledge base about Taiwan.\n\n"
        "HARD RULES (structural — follow exactly, these are checked mechanically):\n"
        "1. Footnote reference markers like [^3] or [^12] must be preserved VERBATIM "
        "— same marker text, same position relative to the sentence they cite. Never "
        "add, remove, or renumber them.\n"
        "2. In markdown links [text](URL), the URL portion must be preserved "
        "VERBATIM; only the link text may be translated.\n"
        "3. Content inside 《...》 or 「...」 (work titles / direct quotes) may stay "
        "in the original zh-TW if there's no natural equivalent — don't force a bad "
        "translation of a proper noun or a quoted utterance.\n"
        "4. Don't add or remove headings, table rows, or list items. Translate "
        "markdown structure markers (#, ##, |, -, >) as-is; only translate the "
        "prose/text content.\n"
        "5. Output ONLY the translated markdown. No commentary, no code fence, no "
        "explanation, no reasoning/chain-of-thought before or after the translation "
        "— just the translated markdown body, nothing else.\n\n"
        f"Target-language rules (extracted from docs/editorial/per-language/"
        f"TRANSLATION-{lang}.md):\n{guide}\n\n{glossary_text}"
    )

    tmp_dir = Path(tempfile.mkdtemp(prefix="structured-translate-chunk-"))
    translated_chunks: list[str] = []
    chunk_reports: list[dict] = []
    max_attempts = 3  # 1 原譯 + 最多 2 次重試（spec 硬性上限，省算力）

    for idx, zh_chunk in enumerate(chunks):
        zh_refs = set(INLINE_FN_REF_RE.findall(zh_chunk))
        system = base_system
        last_output, last_issues = "", ["not attempted"]
        attempts_used = 0
        for attempt in range(1, max_attempts + 1):
            attempts_used = attempt
            t0 = time.time()
            try:
                raw = backend.translate(system, zh_chunk, max_tokens=6000, timeout=240)
            except Exception as e:  # noqa: BLE001
                elapsed = round(time.time() - t0, 1)
                last_issues = [f"backend error: {e}"]
                metrics.setdefault("calls", []).append({
                    "label": f"phase-B-chunk{idx}", "attempt": attempt, "ok": False,
                    "error": str(e), "elapsed_s": elapsed,
                })
                last_output = ""
                continue
            elapsed = round(time.time() - t0, 1)
            out = _strip_fence(raw)
            issues = _validate_chunk(zh_chunk, out, zh_refs, lang, tmp_dir)
            metrics.setdefault("calls", []).append({
                "label": f"phase-B-chunk{idx}", "attempt": attempt, "ok": not issues,
                "elapsed_s": elapsed, "issues": issues,
            })
            last_output, last_issues = out, issues
            if not issues:
                break
            system = base_system + (
                "\n\nYour previous attempt had these problems — fix them and "
                f"re-translate the SAME source text: {'; '.join(issues)}"
            )

        chunk_reports.append({
            "index": idx,
            "zh_chars": len(zh_chunk),
            "out_chars": len(last_output),
            "attempts": attempts_used,
            "retries": attempts_used - 1,
            "status": "OK" if not last_issues else "FAILED_VALIDATION",
            "issues": last_issues,
        })
        translated_chunks.append(last_output)

    return translated_chunks, chunk_reports


# ════════════════════════ Phase A — assembly ════════════════════════

def assemble_article(fm_block: str, translated_chunks: list[str], fn_defs_text: str) -> str:
    body = "\n\n".join(c.strip("\n") for c in translated_chunks if c.strip())
    parts = [f"---\n{fm_block}\n---", body.strip()]
    if fn_defs_text.strip():
        parts.append(fn_defs_text.strip())
    return "\n\n".join(p for p in parts if p.strip()) + "\n"


def run_prettier(path: Path) -> tuple[bool, str]:
    try:
        r = subprocess.run(["npx", "prettier", "--write", str(path)], cwd=REPO,
                            capture_output=True, text=True, timeout=60)
        return r.returncode == 0, (r.stdout + r.stderr)[-500:]
    except Exception as e:  # noqa: BLE001
        return False, str(e)


def _ensure_repo_symlink_for_pilot() -> Path:
    """verify-translation.py 的 ratio-check 子檢查用 en_full.relative_to(REPO)——絕對
    路徑在 /tmp 下會直接 ValueError 炸掉整支 script（連後面 9-16 項檢查都拿不到）。
    在 repo 內已 gitignore 的 tmp/ 底下放一個指回 /tmp/structured-pilot 的 symlink，
    讓傳給 verify-translation.py 的路徑「lexically」落在 REPO 底下，同時實際位元組
    仍然只放在系統 /tmp（不寫 knowledge/，符合 pilot 要求）。cjk-leak-check.py /
    article-health.py 用的是 Path.parts 找「knowledge」子字串，不受影響，兩種路徑
    都能正常運作，不需要這個 symlink。"""
    link_parent = REPO / "tmp"
    link_parent.mkdir(exist_ok=True)
    link = link_parent / "structured-pilot"
    if link.is_symlink() or link.exists():
        if not (link.is_symlink() and link.resolve() == PILOT_ROOT.resolve()):
            link.unlink()
            link.symlink_to(PILOT_ROOT)
    else:
        link.symlink_to(PILOT_ROOT)
    return link


def _verify_arg_path(out_path: Path) -> Path:
    try:
        rel = out_path.relative_to(PILOT_ROOT)
    except ValueError:
        return out_path
    link = _ensure_repo_symlink_for_pilot()
    return link / rel


def run_verify_translation(zh_path: str, out_path: Path) -> dict:
    script = SCRIPT_DIR / "verify-translation.py"
    arg_path = _verify_arg_path(out_path)
    r = subprocess.run(
        [sys.executable, str(script), zh_path, str(arg_path), "--json"],
        cwd=REPO, capture_output=True, text=True, timeout=60,
    )
    try:
        data = json.loads(r.stdout)
    except Exception:  # noqa: BLE001
        data = {"error": "non-JSON output", "stdout": r.stdout[-1200:], "stderr": r.stderr[-1200:]}
    data["exit_code"] = r.returncode
    return data


def run_cjk_leak_check(out_path: Path, lang: str) -> dict:
    hits = cjkleak.scan_file(out_path, lang=lang)
    return {"flagged": bool(hits), "hits": hits}


def run_article_health(out_path: Path) -> dict:
    script = REPO / "scripts/tools/article-health.py"
    r = subprocess.run(
        [sys.executable, str(script), str(out_path), "--profile=pre-commit", "--output=json"],
        cwd=REPO, capture_output=True, text=True, timeout=120,
    )
    try:
        data = json.loads(r.stdout)
    except Exception:  # noqa: BLE001
        data = {"error": "non-JSON output", "stdout": r.stdout[-1500:], "stderr": r.stderr[-1500:]}
    data["exit_code"] = r.returncode
    return data


# ════════════════════════ slug / output path resolution ════════════════════════

def resolve_slug(zh_path: str, lang: str) -> str:
    trans_path = KNOWLEDGE / "_translations.json"
    trans = json.loads(trans_path.read_text(encoding="utf-8")) if trans_path.exists() else {}
    # 先看目標語言自己是否已有這篇的 slug
    for k, v in trans.items():
        if v == zh_path and k.startswith(f"{lang}/"):
            return Path(k).stem
    # 沿用 prepare-batch.py 的邏輯：任何語言已存在的翻譯，slug 視為 canonical，
    # 沿用它而不是讓每個語言各自發明一個新 slug（避免同一篇文章多語言 slug 分裂）。
    for k, v in trans.items():
        if v == zh_path:
            return Path(k).stem
    # Fallback：兩篇 pilot 素材都已有既有翻譯可沿用，不會走到這裡；留一個保守
    # fallback 避免工具在其他輸入上直接炸掉。
    stem = Path(zh_path).stem
    ascii_stem = re.sub(r"[^a-zA-Z0-9-]+", "-", stem).strip("-").lower()
    return ascii_stem or "untitled"


def resolve_out_path(zh_path: str, lang: str, out_arg: Optional[str]) -> Path:
    if out_arg:
        return Path(out_arg)
    category = zh_path.split("/")[0]
    slug = resolve_slug(zh_path, lang)
    return KNOWLEDGE / lang / category / f"{slug}.md"


# ════════════════════════ CLI ════════════════════════

def main():
    ap = argparse.ArgumentParser(description=__doc__.split("\n\n")[0])
    ap.add_argument("zh_path", help="zh-TW source path relative to knowledge/, e.g. Food/台灣咖啡文化.md")
    ap.add_argument("--lang", required=True, help="target language code (vi/ar/en/...)")
    ap.add_argument("--backend", required=True, help="openrouter:<model> | ollama:<model> | codex | gemini")
    ap.add_argument("--out", help="override output path (default: knowledge/<lang>/<category>/<slug>.md)")
    ap.add_argument("--metrics-out", help="also write phase-timing metrics JSON to this path")
    ap.add_argument("--skip-validators", action="store_true",
                    help="skip verify-translation.py / cjk-leak-check.py / article-health.py (faster iteration)")
    args = ap.parse_args()

    zh_full = KNOWLEDGE / args.zh_path
    if not zh_full.exists():
        print(f"❌ zh source not found: {zh_full}", file=sys.stderr)
        sys.exit(2)
    zh_content = zh_full.read_text(encoding="utf-8")

    backend = build_backend(args.backend)
    print(f"📋 {args.zh_path} → {args.lang} via {backend.name}")

    metrics: dict = {
        "zh_path": args.zh_path, "lang": args.lang, "backend": args.backend,
        "backend_name": backend.name, "phases": {},
    }
    t_total0 = time.time()

    # ── Phase F ──
    t0 = time.time()
    zh_fm, body = parse_zh_frontmatter(zh_content)

    # 站內連結在地化（防新增，reports/cross-link-localization-2026-07-27.md 第二段）：
    # 在 body 進 Phase N/B 之前，把 `[文字](/分類/中文slug)` 這類站內連結改成
    # `args.lang` 的譯文網址（查無對應保守不動）。這樣 base_system 裡「URL 原樣
    # 保留 VERBATIM」的指示對站內連結也是對的——模型看到的已經是目標網址，
    # 不必再靠 prompt 猜它是站內還是站外連結。在 Phase N（footnote 抽取）之前做，
    # 兩邊都吃得到改好的版本；純字串替換不加減行數，不影響任何行號依賴的邏輯。
    body, _xlink_count = _xlink.localize_body(body, args.lang)
    metrics["cross_links_localized"] = _xlink_count

    f_metrics: dict = {}
    fm_block = translate_frontmatter(zh_fm, zh_content, args.zh_path, args.lang, backend, f_metrics)
    fm_problems = validate_frontmatter_block(fm_block, args.lang)
    f_calls = f_metrics.get("calls", [])
    metrics["phases"]["F"] = {
        "elapsed_s": round(time.time() - t0, 1),
        "retries": sum(1 for c in f_calls if not c.get("ok")),
        "calls": f_calls,
        "validation_problems": fm_problems,
    }
    print(f"  Phase F (frontmatter): {metrics['phases']['F']['elapsed_s']}s, "
          f"{len(fm_problems)} problem(s)")

    # ── Phase N ──
    t0 = time.time()
    defs = extract_footnote_defs(body)
    n_metrics: dict = {}
    translated_fn = translate_footnotes(defs, args.lang, backend, n_metrics)
    fn_problems = validate_footnotes(defs, translated_fn)
    fn_defs_text = assemble_footnote_defs(defs, translated_fn)
    n_calls = n_metrics.get("calls", [])
    metrics["phases"]["N"] = {
        "elapsed_s": round(time.time() - t0, 1),
        "footnote_count": len(defs),
        "retries": sum(1 for c in n_calls if not c.get("ok")),
        "calls": n_calls,
        "validation_problems": fn_problems,
    }
    print(f"  Phase N (footnotes): {metrics['phases']['N']['elapsed_s']}s, "
          f"{len(defs)} defs, {len(fn_problems)} problem(s)")

    # ── Phase B ──
    t0 = time.time()
    body_no_fn = strip_footnote_defs(body)
    chunks = chunk_body(body_no_fn)
    b_metrics: dict = {}
    translated_chunks, chunk_reports = translate_body_chunks(
        chunks, args.lang, backend, translated_fn, b_metrics)
    b_calls = b_metrics.get("calls", [])
    failed_chunks = [c for c in chunk_reports if c["status"] != "OK"]
    metrics["phases"]["B"] = {
        "elapsed_s": round(time.time() - t0, 1),
        "chunk_count": len(chunks),
        "chunks": chunk_reports,
        "retries": sum(c["retries"] for c in chunk_reports),
        "failed_chunk_count": len(failed_chunks),
        "calls": b_calls,
    }
    print(f"  Phase B (body): {metrics['phases']['B']['elapsed_s']}s, "
          f"{len(chunks)} chunk(s), {len(failed_chunks)} still failing after retries")

    # 2026-07-25 production 首小時裁決：重試耗盡仍 fail 的 chunk 原本「照樣
    # 組裝、讓下游 gate 攔」——結果 dispatcher 白跑 verify trio、寫 quarantine
    # corpse、HEAD-restore 一整套（leak×5 + health×10 大多源於此）。知道自己
    # 有病還把成品送檢，是把診斷成本外包給下游。改硬中止：不寫輸出，exit 1，
    # dispatcher 端走「no output」路徑（保留舊版、退避重排），省整輪 gate。
    if failed_chunks:
        print(f"❌ {len(failed_chunks)} chunk(s) failed after retries — aborting, no output written")
        if args.metrics_out:
            Path(args.metrics_out).write_text(json.dumps(metrics, ensure_ascii=False, indent=2))
        return 1

    # ── Phase A ──
    t0 = time.time()
    assembled = assemble_article(fm_block, translated_chunks, fn_defs_text)
    out_path = resolve_out_path(args.zh_path, args.lang, args.out)
    out_path.parent.mkdir(parents=True, exist_ok=True)
    out_path.write_text(assembled, encoding="utf-8")

    prettier_ok, prettier_msg = run_prettier(out_path)

    if args.skip_validators:
        verify_result = {"skipped": True}
        cjk_result = {"skipped": True}
        health_result = {"skipped": True}
    else:
        verify_result = run_verify_translation(args.zh_path, out_path)
        cjk_result = run_cjk_leak_check(out_path, args.lang)
        health_result = run_article_health(out_path)

    metrics["phases"]["A"] = {
        "elapsed_s": round(time.time() - t0, 1),
        "prettier_ok": prettier_ok,
        "prettier_msg": prettier_msg,
        "verify_translation": verify_result,
        "cjk_leak_check": cjk_result,
        "article_health": health_result,
    }
    metrics["total_elapsed_s"] = round(time.time() - t_total0, 1)
    metrics["out_path"] = str(out_path)

    print(f"  Phase A (assembly): {metrics['phases']['A']['elapsed_s']}s, "
          f"prettier={'ok' if prettier_ok else 'FAIL'}, "
          f"verify_fails={verify_result.get('fails', '?')}, "
          f"cjk_flagged={cjk_result.get('flagged', '?')}")
    print(f"✅ done in {metrics['total_elapsed_s']}s → {out_path}")

    metrics_out = Path(args.metrics_out) if args.metrics_out else out_path.with_suffix(".metrics.json")
    metrics_out.write_text(json.dumps(metrics, ensure_ascii=False, indent=2), encoding="utf-8")
    print(f"📊 metrics → {metrics_out}")


if __name__ == "__main__":
    # sys.exit 包住——沒有它 return 1 不會變成 exit code，dispatcher 端
    # 看到 exit 0 + 無輸出會誤判（今天第 N 次：訊號斷在最後一哩）。
    sys.exit(main())
