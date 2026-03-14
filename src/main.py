from __future__ import annotations

import argparse
from rich import print
from rich.table import Table
from dotenv import load_dotenv

from bot.config import load_config
from bot.credentials import load_credentials
from bot.data_source import MarketDataSource
from bot.strategy import build_signals
from bot.risk import size_signal
from bot.journal import Journal
from bot.snapshots import append_snapshot, load_snapshots
from bot.backtest import run_snapshot_backtest


def run_paper(config_path: str):
    cfg = load_config(config_path)
    creds = load_credentials()
    source = MarketDataSource(use_live=bool(creds.private_key and creds.wallet_address))
    journal = Journal()

    if creds.private_key and creds.wallet_address:
        print("[green]Polymarket wallet credentials loaded (live feed enabled)[/green]")
    else:
        print("[yellow]No complete Polymarket wallet credentials found (using fixture feed)[/yellow]")

    markets = source.fetch()
    signals = build_signals(markets, cfg)
    sized = [size_signal(s, cfg) for s in signals][: cfg.runtime.max_signals_per_cycle]

    if not sized:
        print("[yellow]No signals this cycle[/yellow]")
        return

    table = Table(title="Paper Signals")
    table.add_column("Market")
    table.add_column("Side")
    table.add_column("Edge %")
    table.add_column("Confidence")
    table.add_column("Stake $")

    for s in sized:
        journal.write(s)
        table.add_row(s.title, s.side, str(s.edge_pct), str(s.confidence), str(s.stake_usd))

    print(table)
    print("[green]Signals logged to data/paper_trades.csv[/green]")


def run_collect(config_path: str):
    _ = load_config(config_path)
    creds = load_credentials()
    source = MarketDataSource(use_live=bool(creds.private_key and creds.wallet_address))
    markets = source.fetch()
    path = append_snapshot(markets)
    print(f"[green]Snapshot saved[/green] -> {path} ({len(markets)} markets)")


def run_backtest(config_path: str):
    cfg = load_config(config_path)
    snapshots = load_snapshots()

    if len(snapshots) < 2:
        print("[yellow]Not enough snapshots for backtest.[/yellow]")
        print("Run collect mode multiple times first:")
        print("  python src/main.py --mode collect")
        return

    result = run_snapshot_backtest(snapshots, cfg)
    winrate = (result.wins / result.trades * 100) if result.trades else 0.0
    print(f"[cyan]Backtest over {len(snapshots)} snapshots[/cyan]")
    print(f"Trades: {result.trades} | Wins: {result.wins} | Losses: {result.losses} | Winrate: {winrate:.1f}%")
    print(f"PnL: ${result.pnl_usd}")


def main():
    load_dotenv()
    parser = argparse.ArgumentParser()
    parser.add_argument("--mode", choices=["paper", "backtest", "collect"], default="paper")
    parser.add_argument("--config", default="config/default.yaml")
    args = parser.parse_args()

    if args.mode == "paper":
        run_paper(args.config)
    elif args.mode == "collect":
        run_collect(args.config)
    else:
        run_backtest(args.config)


if __name__ == "__main__":
    main()
