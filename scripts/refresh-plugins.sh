#!/usr/bin/env bash
#
# refresh-plugins.sh — force-refresh locally installed Claude Code plugins to the
# latest commit on the marketplace's remote default branch.
#
# Why this exists: Claude Code's `autoUpdate: true` refreshes the marketplace git
# clone but does NOT re-install the per-plugin code cache (known bug: anthropics/
# claude-code#61854, #17361). So after you push plugin changes, the desktop app
# keeps running the old code. This script pulls the clone and rebuilds the cache.
#
# Usage:
#   scripts/refresh-plugins.sh            # refresh the "digo-labs" marketplace
#   scripts/refresh-plugins.sh <name>     # refresh a different marketplace
#
# After it runs: fully quit (Cmd+Q) and reopen the Claude Code desktop app so the
# new skills load into a fresh session.

set -euo pipefail

MARKETPLACE="${1:-digo-labs}"
ROOT="$HOME/.claude/plugins"
CLONE="$ROOT/marketplaces/$MARKETPLACE"

[ -d "$CLONE/.git" ] || { echo "error: no marketplace clone at $CLONE" >&2; exit 1; }

echo "→ Updating marketplace clone '$MARKETPLACE'…"
git -C "$CLONE" fetch origin --quiet
BRANCH="$(git -C "$CLONE" symbolic-ref --quiet --short refs/remotes/origin/HEAD 2>/dev/null | sed 's#^origin/##')"
BRANCH="${BRANCH:-main}"
git -C "$CLONE" reset --hard "origin/$BRANCH" --quiet

FULL="$(git -C "$CLONE" rev-parse HEAD)"
SHORT="$(git -C "$CLONE" rev-parse --short=12 HEAD)"
TS="$(date -u +%Y-%m-%dT%H:%M:%S.000Z)"
echo "  now at $SHORT ($BRANCH)"

echo "→ Rebuilding plugin caches + repinning install records…"
python3 - "$ROOT" "$MARKETPLACE" "$CLONE" "$FULL" "$SHORT" "$TS" <<'PY'
import json, os, shutil, sys

root, mkt, clone, full, short, ts = sys.argv[1:7]

# plugins declared in the marketplace manifest
manifest = json.load(open(os.path.join(clone, ".claude-plugin", "marketplace.json")))
plugins = {p["name"]: p.get("source", f"./plugins/{p['name']}") for p in manifest["plugins"]}

# rebuild each plugin's cache dir from the freshly-pulled clone
for name, src in plugins.items():
    src_dir = os.path.normpath(os.path.join(clone, src))
    dest = os.path.join(root, "cache", mkt, name, short)
    if os.path.isdir(dest):
        shutil.rmtree(dest)
    shutil.copytree(src_dir, dest)
    print(f"  cache/{mkt}/{name}/{short}")

# repin installed_plugins.json entries for this marketplace
ip_path = os.path.join(root, "installed_plugins.json")
ip = json.load(open(ip_path))
changed = 0
for key, recs in ip.get("plugins", {}).items():
    pname, _, m = key.partition("@")
    if m != mkt or pname not in plugins:
        continue
    for r in recs:
        r["installPath"] = os.path.join(root, "cache", mkt, pname, short)
        r["version"] = short
        r["lastUpdated"] = ts
        r["gitCommitSha"] = full
        changed += 1
json.dump(ip, open(ip_path, "w"), indent=2)
print(f"  repinned {changed} install record(s)")

# bump known_marketplaces lastUpdated
km_path = os.path.join(root, "known_marketplaces.json")
if os.path.exists(km_path):
    km = json.load(open(km_path))
    if mkt in km:
        km[mkt]["lastUpdated"] = ts
        json.dump(km, open(km_path, "w"), indent=2)
PY

echo
echo "✓ '$MARKETPLACE' refreshed to $SHORT"
echo "  Fully quit (Cmd+Q) and reopen the Claude Code desktop app to load the new skills."
