from __future__ import annotations

from dataclasses import dataclass


@dataclass
class Market:
    id: str
    title: str
    yes_price: float
    no_price: float
    spread_pct: float
    liquidity_usd: float
    confidence_yes: float


@dataclass
class Signal:
    market_id: str
    title: str
    side: str
    edge_pct: float
    confidence: float
    stake_usd: float
    reason: str
