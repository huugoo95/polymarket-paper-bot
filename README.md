# polymarket-paper-bot

Paper trading + backtesting starter for prediction-market strategies.

## Scope (v1)
- Market data fetch abstraction
- Signal engine (simple edge rules)
- Paper broker (simulated execution)
- Risk manager (position sizing, max daily loss)
- Backtest runner
- Trade journal (CSV)

## Quickstart

```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
python src/main.py --mode paper
```

## Modes
- `paper`: simulate live-like decisions with fake execution
- `backtest`: replay historical snapshots

## Safety
No real-money execution in v1.
