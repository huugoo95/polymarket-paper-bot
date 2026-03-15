#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
from dataclasses import dataclass
from pathlib import Path
from typing import Iterable


@dataclass
class ScanStats:
    snapshots: int = 0
    markets_seen: int = 0
    candidates: int = 0
    executable: int = 0
    expected_gross_usd: float = 0.0
    expected_fees_usd: float = 0.0
    expected_net_usd: float = 0.0


def iter_snapshots(path: Path) -> Iterable[dict]:
    for line in path.read_text().splitlines():
        if line.strip():
            yield json.loads(line)


def main():
    parser = argparse.ArgumentParser(description="Parity scanner over stored snapshots")
    parser.add_argument("--dataset", default="data/live_snapshots.jsonl")
    parser.add_argument("--stake", type=float, default=1.0, help="USD stake per YES and per NO leg")
    parser.add_argument("--fee-bps", type=float, default=10.0)
    parser.add_argument("--slippage-bps", type=float, default=12.0)
    parser.add_argument("--min-net-edge-pct", type=float, default=0.2)
    args = parser.parse_args()

    ds = Path(args.dataset)
    if not ds.exists():
        raise SystemExit(f"Dataset not found: {ds}")

    total_cost_rate = (args.fee_bps + args.slippage_bps) / 10000.0

    stats = ScanStats()

    for snap in iter_snapshots(ds):
        stats.snapshots += 1
        markets = snap.get("markets", [])
        for m in markets:
            stats.markets_seen += 1
            yes = float(m.get("yes_price", 0.0) or 0.0)
            no = float(m.get("no_price", 0.0) or 0.0)
            liq = float(m.get("liquidity_usd", 0.0) or 0.0)
            spread = float(m.get("spread_pct", 999.0) or 999.0)

            # Basic execution sanity
            if yes <= 0 or no <= 0:
                continue
            if liq < 15000:
                continue
            if spread > 3.0:
                continue

            stats.candidates += 1

            pair_cost = yes + no
            gross_edge_pct = (1.0 - pair_cost) * 100.0

            # costs for two legs at stake each
            notional = args.stake * 2.0
            fees_usd = notional * total_cost_rate
            gross_usd = args.stake * max(1.0 - pair_cost, 0.0)
            net_usd = gross_usd - fees_usd
            net_edge_pct = (net_usd / notional) * 100.0 if notional > 0 else 0.0

            if net_edge_pct >= args.min_net_edge_pct:
                stats.executable += 1
                stats.expected_gross_usd += gross_usd
                stats.expected_fees_usd += fees_usd
                stats.expected_net_usd += net_usd

    print(f"dataset={ds}")
    print(f"snapshots={stats.snapshots} markets_seen={stats.markets_seen}")
    print(f"candidates={stats.candidates} executable={stats.executable}")
    print(f"expected_gross_usd={stats.expected_gross_usd:.4f}")
    print(f"expected_fees_usd={stats.expected_fees_usd:.4f}")
    print(f"expected_net_usd={stats.expected_net_usd:.4f}")


if __name__ == "__main__":
    main()
