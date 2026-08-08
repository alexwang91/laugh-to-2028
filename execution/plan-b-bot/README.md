# Adaptive BTC Beta Bot — Legacy Execution Service

This directory contains the project's older BTC-only Hyperliquid execution service. It is retained for execution-safety, ledger, reconciliation and emergency-control tests, but it is **not** the canonical BRRK multi-asset production authority.

## Safety state

The repository defaults to:

- Hyperliquid **testnet**;
- **shadow** mode;
- no wallet private key;
- no real orders;
- production-facing legacy beta cap **1.0**;
- maximum Hyperliquid platform leverage setting 2x;
- **legacy normal-service new-risk authority disabled**.

`TRADING_MODE=trade`, credentials, a durable ledger, or the historical mainnet confirmation string only configure execution plumbing. They do **not** authorize new directional production risk. The current legacy service blocks risk-increasing normal orders through `beta_bot.production_authority`; same-direction risk reduction remains available.

Do not put a private key in source code, GitHub, or `.env.example`. Use an approved Trading Agent/API Wallet key only in an encrypted deployment environment and only after the canonical Phase 6/7 evidence and explicit owner gates have been satisfied.

## Legacy model

This service implements an older BTC execution model, not the full canonical BRRK target authority:

- completed daily BTC candles only;
- 20/60/120/240-day risk-adjusted momentum;
- 30-day realized volatility;
- defensive beta logic from the legacy model;
- production-facing normal beta capped at 1.0;
- heuristic positive-funding filter;
- 0.05 rebalance band.

The funding filter is **not** a validated historical alpha result. Do not treat this service as a substitute for the frozen P3.2/P3.3 BRRK target/rebalance chain.

## Persistent execution ledger

P1.2 stores execution truth in SQLite, keyed by deterministic Hyperliquid CLOID. It persists economic intent before submission, submission attempt/response, OID, status history, fills, fees, average fill price, remaining quantity and reconciliation timestamps.

Trade plumbing requires both:

- `ORDER_LEDGER_PATH` on persistent storage;
- `ORDER_LEDGER_DURABLE_STORAGE=true` only when that storage genuinely survives process/container replacement.

The current SQLite backend rejects `TRADING_MODE=trade` on Vercel. Restart reconciliation queries Hyperliquid order/fill truth and fails closed on ambiguous or incomplete evidence.

These engineering controls still do not constitute production authorization.

## Endpoints

- `/api/health`: deployment health
- `/api/status`: legacy market-only signal
- `/api/cron`: legacy account calculation and, only where authority permits, execution plumbing

## Environment

See `.env.example`. The example intentionally caps `NORMAL_BETA_CAP=1.0` and keeps shadow/testnet defaults.

## Local test

```bash
python -m venv .venv
source .venv/bin/activate
pip install -r requirements-dev.txt
pytest -q
```

## Activation boundary

There is currently **no supported sequence in this directory that turns the legacy BTC-only service into an authorized production BRRK system**. Testnet engineering exercises may be performed with separately approved test credentials, but mainnet/new-risk production launch must instead satisfy the canonical Phase 6 elapsed-shadow evidence, Phase 7 readiness checklist, production release freeze and explicit owner transition approval.

The following remain explicit human boundaries:

```text
MONITOR_ONLY -> ACTIVE
FLAT -> LONG
FLAT -> SHORT
first short exposure of a new bear phase
```

## Known limitations

- this service is BTC-only and is not the canonical BRRK multi-asset path;
- order-size precision remains legacy executor behavior;
- reversal/execution lifecycle remains an engineering risk surface;
- distributed locking/order slicing are incomplete;
- SQLite needs operator-provided durable storage;
- production authority is intentionally fail-closed for normal risk increases.

This directory is therefore a **legacy testnet/shadow and risk-reduction execution implementation**, not production-ready BRRK live infrastructure.
