#!/usr/bin/env bash
set -euo pipefail

DURATION_MINUTES="${1:-180}"
INTERVAL_SECONDS="${2:-300}"
CONFIG_PATH="${3:-config/microbankroll_50.yaml}"

ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "$ROOT_DIR"

source .venv/bin/activate

mkdir -p data
RUN_TS="$(date +%Y%m%d-%H%M%S)"
LOG_FILE="data/collect_run_${RUN_TS}.log"
REPORT_FILE="data/backtest_report_${RUN_TS}.txt"

END_TS=$(( $(date +%s) + DURATION_MINUTES*60 ))

echo "[run] started at $(date -Is)" | tee -a "$LOG_FILE"
echo "[run] duration=${DURATION_MINUTES}m interval=${INTERVAL_SECONDS}s config=${CONFIG_PATH}" | tee -a "$LOG_FILE"

ITER=0
while [ "$(date +%s)" -lt "$END_TS" ]; do
  ITER=$((ITER+1))
  echo "[collect] iteration=$ITER ts=$(date -Is)" | tee -a "$LOG_FILE"
  python src/main.py --mode collect --config "$CONFIG_PATH" 2>&1 | tee -a "$LOG_FILE"
  sleep "$INTERVAL_SECONDS"
done

echo "[backtest] running at $(date -Is)" | tee -a "$LOG_FILE"
python src/main.py --mode backtest --config "$CONFIG_PATH" 2>&1 | tee "$REPORT_FILE" | tee -a "$LOG_FILE"

echo "[run] finished at $(date -Is)" | tee -a "$LOG_FILE"
echo "[run] report=$REPORT_FILE" | tee -a "$LOG_FILE"
