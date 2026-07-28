#!/usr/bin/env python3
"""hub-translate.py — 分類 Hub 檔的出生翻譯 runner（2026-07-18 出生戰役）。

病根：`_* Hub.md` 不在 `_translation-status.json`（status 索引排除 `_` 前綴），
prepare-batch --input 對它們一律 Skipping unknown → 標準批次管線從不服務 Hub，
es/fr 當年是手工。本 runner 手構 group-entry schema 直呼 translate_one 復用
完整 cascade + 驗證 + 落檔機制。

用法：python3 scripts/tools/lang-sync/hub-translate.py <lang> [cascade]   # cascade 預設 codex,ollama
"""
import importlib.util
import subprocess
import sys
from datetime import datetime
from pathlib import Path

REPO = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(REPO / 'scripts/tools/lang-sync'))

def load(name, fname):
    spec = importlib.util.spec_from_file_location(name, REPO / 'scripts/tools/lang-sync' / fname)
    m = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(m)
    return m

tr = load('translate_mod', 'translate.py')
pb = load('prepare_mod', 'prepare-batch.py')

lang = sys.argv[1]
cascade_id = sys.argv[2] if len(sys.argv) > 2 else 'codex,ollama'
cascade = tr.build_cascade(cascade_id)

hubs = sorted(p for p in (REPO / 'knowledge').glob('*/_* Hub.md')
              if p.parts[-2] not in ('en', 'ja', 'ko', 'es', 'fr', 'vi', 'id', 'pt', 'hi', 'ar', 'ru'))
ok = fail = skip = 0
for hub in hubs:
    zh_path = str(hub.relative_to(REPO / 'knowledge'))
    cat, stem = hub.parts[-2], hub.stem
    out = REPO / 'knowledge' / lang / cat / hub.name
    if out.exists():
        skip += 1
        continue
    sha, content_hash, body_hash = pb.get_zh_meta(zh_path)
    article = {
        'zh_path': zh_path,
        'status': 'missing',
        'en_path': f'knowledge/{lang}/{cat}/{hub.name}',
        'slug': stem,
        'zh_head_sha': sha,
        'zh_content_hash': content_hash,
        'zh_body_hash': body_hash,
        'wikilink_targets': {},
        'frontmatter_placeholder': {
            'translatedFrom': zh_path,
            'sourceCommitSha': sha,
            'sourceContentHash': content_hash,
            'sourceBodyHash': body_hash,
            'translatedAt': datetime.now().astimezone().isoformat(timespec='seconds'),
        },
    }
    print(f'[{lang}] {zh_path} …', flush=True)
    success, err, backend = tr.translate_one(article, lang, cascade)
    if success:
        ok += 1
        print(f'   ✅ via {backend}', flush=True)
    else:
        fail += 1
        print(f'   ❌ {err}', flush=True)

print(f'HUBS {lang}: ok={ok} fail={fail} skip={skip}')
