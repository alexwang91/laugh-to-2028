# Next Steps

> Read canonical sources in repository-defined order. GitHub actual state wins over stale prose.

## Current authorized task

```text
P3.2 Target calculation API
```

P0.1, P0.2, P1.1-P1.8, P2.1-P2.4 and P3.1 are PASS / MERGED.

Do not start P3.3, P3.4, P4, P5, P6, P7 or P8 early.

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

P3.2 is target calculation only. Do not add P3.3 rebalance/turnover bands, P3.4 weekly contribution handling, P4 leverage-above-1 research, P5 cycle-exit intelligence or production authorization.

## P3.1 closure baseline

Final implementation head:

```text
05a3216a402e161b056a452a23f984bac41c7520
```

Final evidence:
- Phase 0 baseline contract #88 / Actions `31108606737`: SUCCESS;
- execution tests: SUCCESS;
- research integration contract: SUCCESS;
- PR handoff governance #110 / Actions `31108607058`: SUCCESS.

PR #68 squash-merged as:

```text
3afbdc165f4b5bde1e1dfbed6f8ceefdbb7dd0ae
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
P3.2 NEXT
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

P3.1 implementation:

```text
DRIFT_0
```

Historical audit `DRIFT_1` remains recorded as process history and does not alter the current product path.

## Exact next action

After the P3.1 post-merge handoff PR is green and merged, create a fresh **P3.2 Target calculation API** branch from then-current main. Recover exact frozen BRRK allocation and defensive risk logic from GitHub before coding; do not infer or retune parameters.
