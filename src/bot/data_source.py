from __future__ import annotations

import json
from pathlib import Path
from typing import List

import requests

from .models import Market


class MarketDataSource:
    def __init__(self, fixture_path: str = "data/sample_markets.json", use_live: bool = False):
        self.fixture_path = Path(fixture_path)
        self.use_live = use_live

    def fetch(self) -> List[Market]:
        if self.use_live:
            live = self._fetch_polymarket_public()
            if live:
                return live

        payload = json.loads(self.fixture_path.read_text())
        return [Market(**m) for m in payload]

    def _fetch_polymarket_public(self) -> List[Market]:
        try:
            # Public endpoint (no auth) for market snapshots
            resp = requests.get(
                "https://gamma-api.polymarket.com/markets",
                params={"closed": "false", "limit": 50},
                timeout=8,
            )
            resp.raise_for_status()
            rows = resp.json()

            markets: List[Market] = []
            for row in rows:
                # best-effort mapping, many markets won't fit filters anyway
                title = row.get("question") or row.get("description") or "Untitled market"
                market_id = str(row.get("id") or row.get("conditionId") or title)

                yes_price = _as_float(row.get("outcomePrices", [None])[0], default=0.5)
                no_price = _as_float(row.get("outcomePrices", [None, None])[1], default=max(0.0, 1 - yes_price))
                spread_pct = max(abs(1 - (yes_price + no_price)) * 100, 0.1)
                liquidity_usd = _as_float(row.get("liquidity") or row.get("volumeNum"), default=0.0)

                # v1 heuristic confidence proxy (to be replaced by actual model)
                confidence_yes = yes_price

                markets.append(
                    Market(
                        id=market_id,
                        title=title,
                        yes_price=yes_price,
                        no_price=no_price,
                        spread_pct=spread_pct,
                        liquidity_usd=liquidity_usd,
                        confidence_yes=confidence_yes,
                    )
                )

            return markets
        except Exception:
            return []


def _as_float(value, default: float) -> float:
    try:
        if value is None:
            return default
        return float(value)
    except Exception:
        return default
