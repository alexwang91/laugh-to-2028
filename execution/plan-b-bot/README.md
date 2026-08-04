# Adaptive BTC Beta Bot

A daily, low-frequency Hyperliquid execution service for the frozen asymmetric BTC beta model developed and backtested in this project.

## Safety state

The repository defaults to:

- Hyperliquid **testnet**
- **shadow** mode
- no wallet private key
- no real orders
- maximum portfolio beta 1.5
- maximum Hyperliquid leverage setting 2x

Do not put a private key in source code, GitHub, or `.env.example`. Use an approved Hyperliquid API Wallet key in encrypted deployment environment variables.

## Model

The bot currently implements the BTC execution model, not the full BRRK / PIT dynamic-universe research stack:

- completed daily BTC candles only;
- 20/60/120/240-day risk-adjusted momentum;
- 30-day realized volatility;
- defensive beta 0.18–0.65 when trend is negative;
- normal positive-trend beta cap 1.30;
- optional hard cap 1.50;
- heuristic positive-funding filter;
- 0.05 rebalance band.

The funding filter is **not** a validated historical alpha result. Historical funding backtesting remains a project backlog item.

## Endpoints

- `/api/health`: deployment health
- `/api/status`: market-only signal
- `/api/cron`: account calculation and optional execution

## Environment

See `.env.example`.

Shadow account mode requires the master/public account address and any external BTC/cash included in strategy NAV. Testnet execution additionally requires a separately approved API Wallet key and `TRADING_MODE=trade`.

## Local test

```bash
python -m venv .venv
source .venv/bin/activate
pip install -r requirements-dev.txt
pytest -q
```

Run once in shadow mode:

```bash
cp .env.example .env
set -a; source .env; set +a
python run_once.py
```

## Activation sequence

1. Confirm `/api/health` and market-only `/api/status`.
2. Add public account configuration; keep `TRADING_MODE=shadow`.
3. Compare target quantities against manual calculations.
4. Create a dedicated Hyperliquid API Wallet on testnet.
5. Add its private key only in encrypted environment variables.
6. Trade on testnet and reconcile every fill/position.
7. Do not move to mainnet until the engineering backlog in the root `docs/NEXT_STEPS.md` is closed.

## Known limitations

- order-size precision is currently hardcoded in the executor;
- reversal close is not followed by a fresh position/fill read before the new leg;
- partial-fill handling and order slicing are incomplete;
- notifications are not isolated from execution success/failure;
- persistent idempotency/audit logs are missing;
- native emergency reduce-only protection is missing;
- endpoint/security hardening is incomplete;
- this version supports BTC only.

This directory is therefore a **testnet/shadow execution implementation**, not production-ready live trading infrastructure.
