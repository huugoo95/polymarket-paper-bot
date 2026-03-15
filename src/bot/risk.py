from __future__ import annotations

from .config import AppConfig
from .models import Signal


def size_signal(signal: Signal, cfg: AppConfig) -> Signal:
    risk_cap = cfg.risk.bankroll * (cfg.risk.max_risk_per_trade_pct / 100)
    # scale a bit by edge but cap to risk_cap
    scaled = risk_cap * min(max(signal.edge_pct / 10, 0.5), 1.0)
    signal.stake_usd = round(min(scaled, risk_cap), 2)
    return signal
