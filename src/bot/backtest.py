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
    gross_pnl_usd: float
    fees_usd: float
    net_pnl_usd: float


def run_snapshot_backtest(snapshots: List[dict], cfg: AppConfig) -> BacktestResult:
    if len(snapshots) < 2:
        return BacktestResult(trades=0, wins=0, losses=0, gross_pnl_usd=0.0, fees_usd=0.0, net_pnl_usd=0.0)

    wins = losses = trades = 0
    gross_pnl = 0.0
    total_fees = 0.0

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

            trade_gross = _pnl_from_move(s, entry, exit_m)
            trade_fees = _estimate_fees(s.stake_usd, cfg)
            trade_net = trade_gross - trade_fees

            gross_pnl += trade_gross
            total_fees += trade_fees
            trades += 1
            if trade_net >= 0:
                wins += 1
            else:
                losses += 1

    return BacktestResult(
        trades=trades,
        wins=wins,
        losses=losses,
        gross_pnl_usd=round(gross_pnl, 2),
        fees_usd=round(total_fees, 2),
        net_pnl_usd=round(gross_pnl - total_fees, 2),
    )


def _estimate_fees(stake_usd: float, cfg: AppConfig) -> float:
    # entry + exit costs
    total_bps = (cfg.costs.fee_bps + cfg.costs.slippage_bps) * 2
    return max(stake_usd, 0.0) * (total_bps / 10000)


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
