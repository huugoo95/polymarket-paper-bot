#!/usr/bin/env bash
set -euo pipefail

ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "$ROOT_DIR"

mkdir -p data/datasets
STAMP="$(date +%Y%m%d-%H%M%S)"
SRC="data/live_snapshots.jsonl"
DST="data/datasets/snapshots_${STAMP}.jsonl"

if [[ ! -f "$SRC" ]]; then
  echo "No live snapshots file found at $SRC"
  exit 1
fi

cp "$SRC" "$DST"
echo "$DST"
