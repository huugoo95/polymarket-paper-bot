from __future__ import annotations

import json
from pathlib import Path
from typing import List

from .models import Market


class MarketDataSource:
    def __init__(self, fixture_path: str = "data/sample_markets.json"):
        self.fixture_path = Path(fixture_path)

    def fetch(self) -> List[Market]:
        # v1: local fixture-based feed (safe + deterministic)
        payload = json.loads(self.fixture_path.read_text())
        return [Market(**m) for m in payload]
