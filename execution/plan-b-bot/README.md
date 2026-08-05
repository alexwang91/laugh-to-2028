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

## Persistent execution ledger

P1.2 stores execution truth in SQLite, keyed by the deterministic Hyperliquid CLOID. It persists the economic intent before any order submission, then persists the submission attempt/response, OID, status history, fills, fees, average fill price, remaining quantity and reconciliation timestamps.

Trade mode requires both:

- `ORDER_LEDGER_PATH` pointing to a persistent filesystem location;
- `ORDER_LEDGER_DURABLE_STORAGE=true`, which is an explicit operator assertion that the configured path really survives process/container replacement.

The Docker image declares `/data` as the intended mount point. The operator still has to attach durable storage to that path. A Docker `VOLUME` declaration alone is not production authorization.

The current local SQLite backend deliberately rejects `TRADING_MODE=trade` when `VERCEL=1`. Vercel remains usable for market/shadow endpoints, but this repository does not treat a function-local SQLite file as durable execution truth.

Restart reconciliation queries Hyperliquid `orderStatus` by CLOID and `userFillsByTime` for fill truth. Exchange facts replace conflicting local observations while preserving an audit event. Database corruption, ambiguous exchange responses, unknown CLOID after a durable submission attempt, truncated fill windows, or an exchange-filled order without complete fill evidence fail closed.

P1.2 does **not** implement the full P1.3 partial-fill lifecycle, retry policy, distributed locking, order slicing, reversal safety or production readiness.

## Endpoints

- `/api/health`: deployment health
- `/api/status`: market-only signal
- `/api/cron`: account calculation and optional execution

## Environment

See `.env.example`.

Shadow account mode requires the master/public account address and any external BTC/cash included in strategy NAV. Testnet execution additionally requires a separately approved API Wallet key, `TRADING_MODE=trade`, and a durable ledger mount.

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
5. Provision a persistent filesystem mount for `ORDER_LEDGER_PATH`; do not use Vercel function-local storage for trade mode.
6. Add the API Wallet private key only in encrypted environment variables.
7. Trade on testnet and reconcile every fill/position.
8. Do not move to mainnet until the engineering backlog in the root `docs/NEXT_STEPS.md` is closed.

## Known limitations

- order-size precision is currently hardcoded in the executor;
- the existing reversal route still does not perform a fresh position/fill read between close and open legs;
- P1.2 records partial fills but does not yet implement the P1.3 partial-fill state machine/retry lifecycle;
- simultaneous multi-process coordination/distributed locking is not implemented;
- order slicing is incomplete;
- notifications are not isolated from execution success/failure;
- native emergency reduce-only protection is missing;
- endpoint/security hardening is incomplete;
- the SQLite backend requires an operator-provided durable filesystem and is not enabled for Vercel trade mode;
- this version supports BTC only.

This directory is therefore a **testnet/shadow execution implementation**, not production-ready live trading infrastructure.
