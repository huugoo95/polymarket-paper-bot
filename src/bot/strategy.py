from __future__ import annotations

from typing import List

from .config import AppConfig
from .models import Market, Signal


def build_signals(markets: List[Market], cfg: AppConfig) -> List[Signal]:
    signals: List[Signal] = []

    for m in markets:
        if m.liquidity_usd < cfg.strategy.min_liquidity_usd:
            continue
        if m.spread_pct > cfg.strategy.max_spread_pct:
            continue

        implied_yes = m.yes_price
        model_yes = m.confidence_yes
        edge_yes = (model_yes - implied_yes) * 100

        if model_yes >= cfg.strategy.min_confidence and edge_yes >= cfg.strategy.min_edge_pct:
            signals.append(
                Signal(
                    market_id=m.id,
                    title=m.title,
                    side="YES",
                    edge_pct=round(edge_yes, 2),
                    confidence=round(model_yes, 3),
                    stake_usd=0.0,
                    reason="Model confidence above threshold and positive edge",
                )
            )

    return signals
