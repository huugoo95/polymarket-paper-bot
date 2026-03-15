from __future__ import annotations

from dataclasses import dataclass
from typing import Dict, List, Tuple

from .config import AppConfig
from .models import Market, Signal
from .strategy import build_signals
from .risk import size_signal


@dataclass
class BacktestResult:
    trades: int
    wins: int
    losses: int
    pnl_usd: float


def run_snapshot_backtest(snapshots: List[dict], cfg: AppConfig) -> BacktestResult:
    if len(snapshots) < 2:
        return BacktestResult(trades=0, wins=0, losses=0, pnl_usd=0.0)

    wins = losses = trades = 0
    pnl = 0.0

    # evaluate signal at t with exit at t+1
    for i in range(len(snapshots) - 1):
        cur = snapshots[i]["markets"]
        nxt = snapshots[i + 1]["markets"]

        cur_markets = [_to_market(m) for m in cur]
        next_by_id: Dict[str, Market] = {m["id"]: _to_market(m) for m in nxt}

        signals = build_signals(cur_markets, cfg)[: cfg.runtime.max_signals_per_cycle]

        for sig in signals:
            if sig.market_id not in next_by_id:
                continue
            s = size_signal(sig, cfg)
            entry = next((m for m in cur_markets if m.id == s.market_id), None)
            exit_m = next_by_id[s.market_id]
            if entry is None:
                continue

            trade_pnl = _pnl_from_move(s, entry, exit_m)
            pnl += trade_pnl
            trades += 1
            if trade_pnl >= 0:
                wins += 1
            else:
                losses += 1

    return BacktestResult(
        trades=trades,
        wins=wins,
        losses=losses,
        pnl_usd=round(pnl, 2),
    )


def _pnl_from_move(signal: Signal, entry: Market, exit_m: Market) -> float:
    stake = max(signal.stake_usd, 0.01)
    if signal.side == "YES":
        if entry.yes_price <= 0:
            return 0.0
        shares = stake / entry.yes_price
        return shares * (exit_m.yes_price - entry.yes_price)

    # NO side
    entry_no = max(entry.no_price, 1e-6)
    exit_no = max(exit_m.no_price, 1e-6)
    shares = stake / entry_no
    return shares * (exit_no - entry_no)


def _to_market(row: dict) -> Market:
    return Market(
        id=str(row["id"]),
        title=row["title"],
        yes_price=float(row["yes_price"]),
        no_price=float(row["no_price"]),
        spread_pct=float(row["spread_pct"]),
        liquidity_usd=float(row["liquidity_usd"]),
        confidence_yes=float(row.get("confidence_yes", row["yes_price"])),
    )
