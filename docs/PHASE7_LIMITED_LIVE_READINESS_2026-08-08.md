# Phase 7 — Limited-Live Readiness Gate

Date: 2026-08-08

## Status

`IMPLEMENTATION READINESS ONLY / LAUNCH BLOCKED / NO PRODUCTION AUTHORIZATION`

The Phase 7 code in this change is an authorization-policy layer, not an execution path. It does not import the executor, signer, exchange client or credentials and cannot place orders.

## Launch checklist

All items are fail-closed:

- Phase 6 implementation/replay PASS;
- Phase 6 real elapsed shadow evidence PASS;
- production release frozen;
- Trading Agent credential only;
- master wallet private key absent from bot;
- withdrawal/transfer automation absent;
- hard production gross cap exactly 1.0;
- kill switch tested;
- startup reconciliation passed;
- monitoring active;
- explicit owner approval for the requested transition.

Current project evidence does **not** satisfy the Phase 6 elapsed-time requirement and no launch approval record is created here. Therefore current state remains `MONITOR_ONLY`.

## Explicit human boundaries

Separate approval is required for:

```text
MONITOR_ONLY -> ACTIVE
FLAT -> LONG
FLAT -> SHORT
first short exposure of a new bear phase
```

The gate supports these checks so that a future operator cannot accidentally treat a generic deployment approval as approval for a first bear short.

## Normal autonomy

Only after a separately approved ACTIVE long program may the execution system perform the roadmap's normal autonomous actions inside approved limits: rebalance, approved leverage changes, routing, risk reduction and emergency FLAT. This document does not activate that state.

## Scale-up

No capital scale-up is authorized. Any future scale-up must review realized slippage, funding, reconciliation history, uptime/data quality, drawdown behavior, target fidelity and operational incidents.
