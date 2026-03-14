from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
import yaml


@dataclass
class RiskConfig:
    bankroll: float
    max_risk_per_trade_pct: float
    max_daily_drawdown_pct: float
    max_weekly_drawdown_pct: float


@dataclass
class StrategyConfig:
    min_edge_pct: float
    min_liquidity_usd: float
    max_spread_pct: float
    min_confidence: float


@dataclass
class RuntimeConfig:
    poll_seconds: int
    max_signals_per_cycle: int


@dataclass
class AppConfig:
    risk: RiskConfig
    strategy: StrategyConfig
    runtime: RuntimeConfig


def load_config(path: str) -> AppConfig:
    cfg_path = Path(path)
    data = yaml.safe_load(cfg_path.read_text())

    return AppConfig(
        risk=RiskConfig(**data["risk"]),
        strategy=StrategyConfig(**data["strategy"]),
        runtime=RuntimeConfig(**data["runtime"]),
    )
