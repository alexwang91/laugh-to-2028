# Next Steps

> Read canonical sources in repository-defined order. GitHub actual state wins over stale prose.

## Current roadmap task

```text
P3.2 Target calculation API
```

P0.1, P0.2, P1.1-P1.8, P2.1-P2.4 and P3.1 are PASS / MERGED.

P3.2 remains the unique next roadmap implementation. Before coding it, close the audit-discovered legacy backlog/handoff corrections recorded in `docs/CURRENT_STATE.md` and `docs/BACKLOG_ROADMAP_CROSSWALK_2026-08-06.md`.

Do not start P3.3, P3.4, P4, P5, P6, P7 or P8 early.

## Pre-P3.2 correction gate

The correction gate does not advance roadmap scope and does not authorize production. It closes residual findings that predate the Master Plan:

- F17 residual failure-notification gap;
- F19 target-unreachable semantics;
- F20 HTTP cron authorization / error redaction;
- F21 unregistered strong-beta 1.50 runtime branch;
- F22 remaining 01:10 UTC operational schedule drift;
- legacy backlog ↔ roadmap reconciliation so old acceptance items cannot disappear by omission;
- a separate narrow evidence normalization for EXPOSURE-SMOOTH-0038 and F27 measurement bookkeeping.

## P3.2 acceptance boundary

Input:
- canonical daily data from P3.1;
- account equity;
- current positions;
- approved config.

Output:
- BRRK relative weights;
- cash share;
- base gross target;
- risk state;
- version and feature snapshot.

The implementation must reproduce the frozen BRRK directional core from the same canonical historical input. It must expose deterministic/versioned output suitable for research/live comparison.

P3.2 is target calculation only. Do not add:
- P3.3 rebalance/turnover bands;
- P3.4 weekly contribution handling;
- F23 funding-response redesign;
- P4 leverage-above-1 research;
- P5 cycle-exit intelligence;
- production authorization.

`EXPOSURE-SMOOTH-0038` is not the P3.2 baseline. It is a mechanism-validation result that was not promoted. ASYM-BETA-0024 is also not P3.2 authority.

## P3.1 closure baseline

Final implementation head:

```text
05a3216a402e161b056a452a23f984bac41c7520
```

PR #68 squash-merged as:

```text
3afbdc165f4b5bde1e1dfbed6f8ceefdbb7dd0ae
```

P3.1 post-merge handoff PR #69 advanced authoritative main to:

```text
34165f8481b8c38f7f824b2f18f7592da731223b
```

`DATA-CONTRACT-P3.1 = IMPLEMENTATION_VERIFIED`.

Canonical P3.1 boundary:

```text
strategy price = frozen Binance spot UTC 1d BTC/ETH/SOL/BNB series
missing data   = fail closed, no forward fill or cross-venue substitution
mapping        = explicit versioned source mapping
funding        = exact completed Hyperliquid hourly slots, bps/hour
basis          = verified spot/perp basis in bps with timestamps/skew retained
```

Research/live share one canonicalizer and produce byte-identical canonical payloads for the same observations.

## Ordered forward program

```text
P1.1-P1.8 COMPLETE
P2.1-P2.4 COMPLETE
P3.1 COMPLETE
AUDIT CORRECTIONS -> CLOSE FIRST
P3.2 NEXT ROADMAP IMPLEMENTATION
P3.3 BLOCKED ON P3.2
P3.4 BLOCKED
P4   BLOCKED
P5   BLOCKED
P6   BLOCKED
P7   BLOCKED
P8   BLOCKED
```

## Production authorization

```text
NO_CHANGE
production_authorized_components = []
```

## Project drift audit

Current audit finding:

```text
DRIFT_1
```

This is implementation/handoff debt from the pre-Master-Plan backlog transition. No product objective, universe, venue, risk philosophy, human-approval, wallet/security or production-authorization assumption changed.

## Exact next action

```text
close current audit correction with tests / self-review / CI / merge
-> close narrow EXPOSURE-SMOOTH-0038 + F27 evidence-normalization correction from fresh main
-> create a fresh P3.2 target-calculation branch from then-current main
-> recover exact frozen BRRK allocation/risk logic from GitHub
-> implement P3.2 only
-> tests / self-review / drift audit / PR / CI / expected-head merge
```
