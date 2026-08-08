# Phase 6 — Canonical Integrated Shadow Contract

Date: 2026-08-08

## Status

`IMPLEMENTATION_AND_REPLAY_PENDING / ZERO TRADING AUTHORITY`

Phase 5 is closed with P5.5 `NO_PROMOTION`; P5.6 is blocked. Phase 6 therefore shadows the frozen BRRK-0011 long baseline only. It does not carry a cycle-exit overlay forward and does not reinterpret a failed P5 candidate as production logic.

## Canonical chain

```text
P3.1 canonical daily data
  -> P3.2 BRRK-0011 target authority
  -> P3.3 rebalance control
  -> read-only router projection
  -> Phase 6 hypothetical orders + reconciliation/audit
```

The Phase 6 orchestration module does **not** import the executor, signer, Hyperliquid `Exchange`, account key material, withdrawal or transfer code. It may consume real read-only account/market/order-book/funding observations, but its terminal output is an immutable hypothetical-order/audit record only.

## Frozen safety boundaries

- Long universe remains BTC/ETH/SOL/BNB.
- XRP remains feature-only.
- Gross target and post-control desired gross must remain `<= 1.0`.
- Cycle layer is `NONE_P5_6_BLOCKED`.
- Production authorization is false.
- Signature authorization is false.
- Order-submission authorization is false.
- Any missing data, target/reference mismatch, instrument identity mismatch, cost-model error, unexplained state transition, schedule drift or unusable route fails closed and discards the entire hypothetical-order set.
- Emergency mode may compute a hypothetical flattening intent but cannot submit it.

## P6.1 daily shadow evidence

Each scheduled decision must retain:

- BRRK target weights;
- cycle-layer status;
- gross/leverage target;
- current and desired position weights;
- L1 target gap;
- route projections and reason codes;
- hypothetical order side/notional/instrument;
- expected route cost;
- offline-reference target drift;
- emergency hypothetical action;
- alerts and deterministic audit digest.

If an incumbent ACTIVE release exists, comparison may be attached as read-only evidence; its absence does not authorize a new ACTIVE release.

## P6.2 drift checks

The shadow decision fails closed on:

1. feature-reference mismatch;
2. target-reference mismatch;
3. incomplete/missing canonical input;
4. instrument identity mismatch;
5. cost-model error;
6. unexplained state transition;
7. daily schedule drift;
8. route/capacity unavailability for any non-zero hypothetical delta.

## P6.3 acceptance split

### A. Implementation/replay evidence

CI may establish only:

- exact canonical gross and long-only invariants;
- deterministic target/current reconciliation;
- atomic fail-closed behavior;
- emergency hypothetical flatten behavior;
- complete audit serialization/digest;
- zero signer/executor/import path.

A green replay earns `PASS_SHADOW_ONLY_IMPLEMENTATION_REPLAY`, not production authorization.

### B. Time-dependent live-shadow evidence

Actual live-shadow acceptance additionally requires **both**:

- at least 14 elapsed calendar days; and
- at least 10 scheduled decisions;

plus at least one emergency drill, zero critical reconciliation errors, zero unexplained target drift and zero schedule failures.

Until that real elapsed evidence exists, status remains:

`MEASUREMENT_INCONCLUSIVE_TIME_DEPENDENT`

Historical replay or CI must never backfill this clock.

## Phase 7 boundary

Phase 7 readiness work may be implemented and tested without trading authority, but `MONITOR_ONLY -> ACTIVE`, `FLAT -> LONG`, `FLAT -> SHORT`, and the first bear short remain explicit human approval boundaries. No Phase 6 artifact changes those boundaries.
