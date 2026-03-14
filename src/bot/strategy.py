from __future__ import annotations

from typing import List

from .config import AppConfig
from .models import Market, Signal


def build_signals(markets: List[Market], cfg: AppConfig) -> List[Signal]:
    """
    Micro-bankroll friendly heuristic strategy (fast v1):
    - Filters low liquidity / wide spread
    - Mean-reversion around 0.50 probability band
    - Emits YES/NO signals with edge/confidence scores
    """
    signals: List[Signal] = []
    total_cost_pct = ((cfg.costs.fee_bps + cfg.costs.slippage_bps) / 100.0) + cfg.strategy.min_net_edge_buffer_pct

    for m in markets:
        if m.liquidity_usd < cfg.strategy.min_liquidity_usd:
            continue
        if m.spread_pct > cfg.strategy.max_spread_pct:
            continue

        yes = m.yes_price
        no = m.no_price

        # Avoid extremes where reversion odds are worse for this simple model
        if yes < 0.05 or yes > 0.95:
            continue

        # YES side: oversold region
        if yes <= 0.47:
            edge = (0.50 - yes) * 100
            confidence = 0.52 + max(0.0, 0.47 - yes)
            if edge >= cfg.strategy.min_edge_pct and edge >= total_cost_pct and confidence >= cfg.strategy.min_confidence:
                signals.append(
                    Signal(
                        market_id=m.id,
                        title=m.title,
                        side="YES",
                        edge_pct=round(edge, 2),
                        confidence=round(min(confidence, 0.80), 3),
                        stake_usd=0.0,
                        reason="Mean-reversion: YES priced below fair band",
                    )
                )
                continue

        # NO side: overbought YES region
        if yes >= 0.53:
            edge = (yes - 0.50) * 100
            confidence = 0.52 + max(0.0, yes - 0.53)
            if edge >= cfg.strategy.min_edge_pct and edge >= total_cost_pct and confidence >= cfg.strategy.min_confidence:
                signals.append(
                    Signal(
                        market_id=m.id,
                        title=m.title,
                        side="NO",
                        edge_pct=round(edge, 2),
                        confidence=round(min(confidence, 0.80), 3),
                        stake_usd=0.0,
                        reason="Mean-reversion: YES priced above fair band",
                    )
                )

    # rank by edge then confidence
    signals.sort(key=lambda s: (s.edge_pct, s.confidence), reverse=True)
    return signals
