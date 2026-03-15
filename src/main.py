from __future__ import annotations

import argparse
from rich import print
from rich.table import Table

from bot.config import load_config
from bot.data_source import MarketDataSource
from bot.strategy import build_signals
from bot.risk import size_signal
from bot.journal import Journal


def run_paper(config_path: str):
    cfg = load_config(config_path)
    source = MarketDataSource()
    journal = Journal()

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


def run_backtest(config_path: str):
    cfg = load_config(config_path)
    source = MarketDataSource()
    markets = source.fetch()
    signals = build_signals(markets, cfg)

    print(f"[cyan]Backtest snapshot: {len(markets)} markets, {len(signals)} candidate signals[/cyan]")


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--mode", choices=["paper", "backtest"], default="paper")
    parser.add_argument("--config", default="config/default.yaml")
    args = parser.parse_args()

    if args.mode == "paper":
        run_paper(args.config)
    else:
        run_backtest(args.config)


if __name__ == "__main__":
    main()
