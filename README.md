# polymarket-paper-bot

Paper trading + backtesting starter for prediction-market strategies.

## What is implemented (v1)
- Fixture-based market feed (`data/sample_markets.json`)
- Signal engine with edge + liquidity + spread filters
- Risk sizing per signal (max risk per trade)
- Paper journal to CSV (`data/paper_trades.csv`)
- Backtest snapshot mode

## Quickstart

```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
cp .env.example .env
python src/main.py --mode paper
python src/main.py --mode backtest
```

## Credentials integration
- Credentials file is loaded from `POLYMARKET_CREDENTIALS_FILE`.
- Recommended location: outside repo (already ignored by git).
- Expected format in file:

```bash
POLYMARKET_API_KEY=...
POLYMARKET_API_SECRET=...
POLYMARKET_PASSPHRASE=...
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
