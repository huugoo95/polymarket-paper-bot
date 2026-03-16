#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
from datetime import datetime
from pathlib import Path

from bot.config import load_config
from bot.backtest import run_snapshot_backtest


def load_snapshots(path: Path):
    rows = []
    for line in path.read_text().splitlines():
        if line.strip():
            r = json.loads(line)
            ts = datetime.fromisoformat(r["ts"].replace("Z", "+00:00"))
            rows.append((ts, r))
    return [r for _, r in rows]


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--dataset", default="data/live_snapshots.jsonl")
    parser.add_argument("--configs", nargs="*", default=[
        "config/strategies/conservative.yaml",
        "config/strategies/balanced.yaml",
        "config/strategies/aggressive.yaml",
    ])
    args = parser.parse_args()

    dataset = Path(args.dataset)
    if not dataset.exists():
        raise SystemExit(f"Dataset not found: {dataset}")

    snapshots = load_snapshots(dataset)
    if len(snapshots) < 2:
        raise SystemExit("Not enough snapshots to benchmark")

    print(f"Dataset: {dataset} | snapshots={len(snapshots)}")
    print("strategy,trades,wins,losses,gross_pnl,fees,net_pnl")

    for c in args.configs:
        cfg = load_config(c)
        r = run_snapshot_backtest(snapshots, cfg)
        print(f"{Path(c).stem},{r.trades},{r.wins},{r.losses},{r.gross_pnl_usd},{r.fees_usd},{r.net_pnl_usd}")


if __name__ == "__main__":
    main()
