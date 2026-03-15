#!/usr/bin/env bash
set -euo pipefail

INTERVAL_SECONDS="${1:-300}"
CONFIG_PATH="${2:-config/microbankroll_50.yaml}"

ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "$ROOT_DIR"

source .venv/bin/activate
mkdir -p data

LOG_FILE="data/collector_daemon.log"

echo "[daemon] start $(date -Is) interval=${INTERVAL_SECONDS}s config=${CONFIG_PATH}" | tee -a "$LOG_FILE"

while true; do
  python src/main.py --mode collect --config "$CONFIG_PATH" 2>&1 | tee -a "$LOG_FILE"
  sleep "$INTERVAL_SECONDS"
done
