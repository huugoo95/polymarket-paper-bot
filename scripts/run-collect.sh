#!/usr/bin/env bash
set -euo pipefail
source .venv/bin/activate
python src/main.py --mode collect --config config/microbankroll_50.yaml
