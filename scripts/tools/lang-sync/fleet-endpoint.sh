#!/usr/bin/env bash
# fleet-endpoint.sh — ask the GPU fleet for a sovereignty-safe Ollama endpoint.
#
# The hardware layer is NOT COMPUTEX.md's job. The GPU fleet (~/Projects/muse-bot/
# fleet/) already owns node registry (registry.json = SSOT), commander routing
# (fleetlib.select_machine: non-leaving → smallest-sufficient-VRAM → Gemma4-only
# for sovereignty), the Ollama-over-Tailscale work channel, and the Windows SOP.
# This adapter just ASKS it for an endpoint and exports OLLAMA_HOST/OLLAMA_MODEL;
# COMPUTEX.md keeps only the translation logic (diary-translate.py prompt + the
# integrity gate). No parallel registry, no hand-rolled tunnel, no node-selection.
#
# Fork/contributor without the fleet → exit 3, caller skips the diary sweep.
#
#   eval "$(bash fleet-endpoint.sh --export)"
#   bash diary-translate-cascade.sh --tier ollama --langs en,ja,ko,es,fr
#
# Pointer: contributor.local.yml machine_resources.gpu_fleet · fleet/README.md
set -euo pipefail

FLEET_DIR="${FLEET_DIR:-$HOME/Projects/muse-bot/fleet}"
[ -f "$FLEET_DIR/fleetlib.py" ] || { echo "no GPU fleet at $FLEET_DIR — skip diary sweep (fork/no-fleet)" >&2; exit 3; }

# refresh live status (best-effort), then let the fleet's commander pick a node
( cd "$FLEET_DIR" && ./fleetctl probe all >/dev/null 2>&1 ) || true

LINE="$(cd "$FLEET_DIR" && python3 -c "
import fleetlib as fl
reg = fl.load_registry()
order = ['gemma4:26b', 'gemma4:31b', 'gemma4:12b', 'gemma4:e4b']
def pulled(m):  # best sovereignty-safe model actually pulled on the node
    return next((x for x in order if x in m.get('models', [])), None)
# delegate routing to the fleet commander, but require the node can serve NOW
# (select_machine routes on declared sovereignty capability, not pulled models —
# e.g. it can pick a node mid-CUDA-repair with gemma4 declared but not pulled)
pick = fl.select_machine(reg, 'llm', {'sovereignty_safe': True})
if not pick or not pulled(pick):
    ready = [m for m in fl.machines(reg)
             if fl._online(m) and m.get('lifecycle') != 'retired' and pulled(m)]
    ready.sort(key=lambda m: (1 if m.get('lifecycle') == 'leaving' else 0,
                              1 if m.get('status') == 'busy' else 0,
                              order.index(pulled(m)), m.get('vram_gb', 999)))
    pick = ready[0] if ready else None
if not pick:
    raise SystemExit(1)
ip, port = pick['tailscale_ip'], pick.get('ollama_port', 11434)
print(f'http://{ip}:{port} {pulled(pick)} {pick[\"id\"]}')
" 2>/dev/null)" || { echo "fleet: no sovereignty-safe llm node ready (model pulled + online) — skip" >&2; exit 3; }

read -r HOST MODEL NODE <<<"$LINE"
[ -n "${HOST:-}" ] || { echo "fleet returned no endpoint — skip" >&2; exit 3; }

[ "${1:-}" = "--export" ] || echo "🛰  fleet → $NODE ($MODEL) @ $HOST" >&2
echo "export OLLAMA_API_URL=$HOST/api/chat OLLAMA_HOST=$HOST OLLAMA_MODEL=$MODEL"
