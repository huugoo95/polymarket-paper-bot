from __future__ import annotations

from pathlib import Path
import csv
from datetime import datetime, timezone

from .models import Signal


class Journal:
    def __init__(self, path: str = "data/paper_trades.csv"):
        self.path = Path(path)
        if not self.path.exists():
            self.path.parent.mkdir(parents=True, exist_ok=True)
            with self.path.open("w", newline="") as f:
                writer = csv.writer(f)
                writer.writerow([
                    "ts_utc",
                    "market_id",
                    "title",
                    "side",
                    "edge_pct",
                    "confidence",
                    "stake_usd",
                    "reason",
                ])

    def write(self, signal: Signal) -> None:
        with self.path.open("a", newline="") as f:
            writer = csv.writer(f)
            writer.writerow([
                datetime.now(timezone.utc).isoformat(),
                signal.market_id,
                signal.title,
                signal.side,
                signal.edge_pct,
                signal.confidence,
                signal.stake_usd,
                signal.reason,
            ])
