# polymarket-paper-bot

Paper trading + backtesting starter for prediction-market strategies.

## What is implemented (v1 fast-track)
- Optional live market feed (Polymarket public endpoint) when credentials file exists
- Signal engine (micro-bankroll oriented mean-reversion heuristic)
- Risk sizing per signal (max risk per trade)
- Paper journal to CSV (`data/paper_trades.csv`)
- Snapshot collector (`data/live_snapshots.jsonl`)
- Backtest over collected snapshots

## Quickstart

```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
cp .env.example .env
python src/main.py --mode collect --config config/microbankroll_50.yaml
python src/main.py --mode paper --config config/microbankroll_50.yaml
python src/main.py --mode backtest --config config/microbankroll_50.yaml
```

## Credentials integration
- Credentials file is loaded from `POLYMARKET_CREDENTIALS_FILE`.
- Recommended location: outside repo (already ignored by git).
- Expected format in file:

```bash
POLYMARKET_PRIVATE_KEY=...
POLYMARKET_WALLET_ADDRESS=...
```

Or run helper scripts:

```bash
scripts/run-paper.sh
scripts/run-backtest.sh
```

## Config
Use `config/default.yaml` and adjust:
- bankroll
- max risk per trade
- min edge
- min liquidity
- max spread

## Next steps
1. Replace fixture feed with live market API adapter.
2. Add paper positions lifecycle (entry/exit/PnL).
3. Add drawdown guardrail and auto-stop.
4. Add test coverage for strategy and sizing logic.

## Safety
No real-money execution in v1.


## Fast workflow for $50 bankroll
1. Collect snapshots periodically:
   - `scripts/run-collect.sh` (run multiple times across the day)
2. Run backtest on collected snapshots:
   - `python src/main.py --mode backtest --config config/microbankroll_50.yaml`
3. Run paper mode for candidate signals:
   - `python src/main.py --mode paper --config config/microbankroll_50.yaml`
