# BRRK Current State

Last updated: 2026-08-06
Status: authoritative cross-chat handoff snapshot

## Authoritative baseline

- P0.1 / P0.2: PASS / MERGED
- P1.1 through P1.8: PASS / MERGED
- Phase 1 Account and execution truth: COMPLETE
- P2.1 through P2.4: PASS / MERGED
- Phase 2 Hyperliquid instrument router: COMPLETE
- P3.1 Data contract implementation PR #68: PASS / MERGED
- Current main after P3.1: `3afbdc165f4b5bde1e1dfbed6f8ceefdbb7dd0ae`
- Full project audit: `docs/FULL_PROJECT_AUDIT_2026-08-06.md`

## Current roadmap position

```text
P3.1 Data contract: PASS / MERGED
P3.2 Target calculation API: NEXT
P3.3 Rebalance band / turnover controls: BLOCKED
P3.4 Weekly cash contribution handling: BLOCKED
P4+: BLOCKED
```

The unique next implementation task is **P3.2 Target calculation API**.

## P3.1 closure

Machine-readable authority:

```text
config/data_contract.json
contract_id = BRRK-DATA-CONTRACT-P3.1-2026-08-06
```

Implementation:

```text
execution/plan-b-bot/beta_bot/data_contract.py
execution/plan-b-bot/beta_bot/strategy_data_source.py
research/integration/p3_1_data_contract_adapter.py
```

Detailed semantics:

```text
docs/P3_1_DATA_CONTRACT.md
```

Canonical strategy-price source remains the frozen BRRK research source:

```text
Binance spot BTCUSDT / ETHUSDT / SOLUSDT / BNBUSDT
1d
explicit timeZone=0 UTC
decision boundary = 00:00:00 UTC
usable candle = close_time_ms < decision_timestamp_ms
```

Missing data is fail-closed: no forward fill, previous-close substitution, cross-venue substitution or incomplete-candle substitution. Versioned source mappings must resolve exactly once for every consumed session.

Research and live use the same canonicalizer; for identical raw observations and decision timestamp they emit byte-identical canonical JSON and SHA-256 digest. The resulting close sequence also produces identical output from the existing frozen signal component.

Router funding/basis semantics are canonicalized separately from strategy-price data:
- exact completed Hyperliquid funding-history hourly slots -> bps/hour;
- missing required slots fail closed;
- basis = `(perp_mark_price / verified_spot_price - 1) * 10000` bps;
- both observation timestamps and skew are retained.

`DATA-CONTRACT-P3.1 = IMPLEMENTATION_VERIFIED` is registered. This is data-contract engineering evidence only and does not authorize target generation or production trading.

## P3.1 evidence

Candidate head before decision/evidence writeback:

```text
cd55535cf4720e259109b0080104d642183e9efe
```

passed:
- Phase 0 baseline contract #86 / Actions `31108327909`: SUCCESS;
- execution tests: SUCCESS;
- research integration contract: SUCCESS;
- PR handoff governance #108 / Actions `31108329917`: SUCCESS.

Final implementation head:

```text
05a3216a402e161b056a452a23f984bac41c7520
```

passed:
- Phase 0 baseline contract #88 / Actions `31108606737`: SUCCESS;
- execution tests: SUCCESS;
- research integration contract: SUCCESS;
- PR handoff governance #110 / Actions `31108607058`: SUCCESS.

PR #68 squash-merged to main as:

```text
3afbdc165f4b5bde1e1dfbed6f8ceefdbb7dd0ae
```

## P3.1 self-review conclusions retained

1. Strategy signal data and execution/router observations are separate namespaces; Hyperliquid execution does not silently change the frozen Binance spot research price path.
2. Strategy-price outages fail closed rather than altering the path through imputation or cross-venue substitution.
3. Source mappings are versioned and gap/overlap/ambiguity fail closed.
4. Funding uses exact completed hourly slots and cannot consume boundary/future values early.
5. Basis preserves source timestamps/skew instead of hiding a freshness assumption.
6. Research has no independent candle-cleaning logic; it calls the same canonicalizer as live.
7. P3.1 did not implement the full P3.2 target API or later controls.

## Project drift audit

P3.1 closed as:

```text
DRIFT_0
```

Historical full-audit `DRIFT_1` remains preserved as process history; no product, universe, venue, risk, human-approval, security or production boundary changed in P3.1.

## Production authorization

```text
NO_CHANGE
production_authorized_components = []
```

## Unique next task: P3.2 Target calculation API

Input contract:
- canonical daily data from P3.1;
- account equity;
- current positions;
- approved config.

Required output:
- BRRK relative weights;
- cash share;
- base gross target;
- risk state;
- version and feature snapshot.

P3.2 must reproduce the frozen BRRK directional core from canonical input. It must not implement P3.3 rebalance/turnover bands, P3.4 contribution handling, P4 leverage-above-1 extension, P5 cycle-exit intelligence or production authorization.

## Exact next action

```text
merge P3.1 post-merge handoff
-> create fresh P3.2/target-calculation-api branch from then-current main
-> recover exact frozen BRRK allocation/risk logic from GitHub
-> implement P3.2 only
-> tests / self-review / drift audit / PR / CI / expected-head merge
```
