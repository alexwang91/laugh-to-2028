# Next Steps

> Read canonical sources in repository-defined order. GitHub actual state wins over stale prose.

## Current dependency

```text
Validate the clean v2 LEVERAGE-0040 one-time-study implementation before any cap>1 result may exist.
```

Normalized main after PR #89:

`98396a5b510c5f0a717b954568921c1daef6edc8`

Current candidate:

`p4-4/leverage-0040-one-time-study-v2`

Old `p4-4/leverage-0040-one-time-study-v1` is **INVALID / ABANDONED / DO NOT MERGE / DO NOT REVIVE** after a tool-layer transient empty-file write. No PR or result was produced from it. The v2 branch was created from a clean intended tree and excludes the transient file.

## Frozen authority

```text
P4.1 defensive scaler       frozen 0 .. 1
LEVERAGE-0039              STOPPED_PRE_RUN / NO RESULT / DO NOT REUSE
LEVERAGE-0040              PREREGISTERED / MERGED / NOT RUN
cap=1 wiring/parity        PASS / MERGED
liquidation model          PASS / MERGED
>1 multiplier policy       FROZEN PRE-RESULT / MERGED
production gross cap       1.0 unchanged
production authorization   none
```

`production_authorized_components = []` remains unchanged.

## Current pre-study candidate

Files:

- `research/leverage_0040/LEVERAGE-0040-STUDY-IMPLEMENTATION-V1.json`
- `research/leverage_0040/study_core.py`
- `research/leverage_0040/run_leverage_0040_once.py`
- `research/leverage_0040/validate_leverage_0040_result.py`
- `execution/plan-b-bot/tests/test_p4_4_study_core.py`
- `.github/workflows/p4-4-leverage-0040-contract.yml`
- `.github/workflows/p4-4-leverage-0040-run-once.yml`
- `.github/workflows/p4-4-leverage-0040-result-validation.yml`

Status:

```text
implementation contract/core    IMPLEMENTED CANDIDATE / CI PENDING
one-time runner                 IMPLEMENTED CANDIDATE / CI PENDING
immutable result validator      IMPLEMENTED CANDIDATE / CI PENDING
contract + preflight workflow   IMPLEMENTED CANDIDATE / CI PENDING
RUN_ONCE marker                 ABSENT
LEVERAGE-0040 search            NOT RUN
result directory                ABSENT
```

## Frozen study semantics

The study implementation is now frozen before any >1 observation. It preserves:

```text
candidate caps             1.00 / 1.10 / 1.20 / 1.30
multiplier                 1 + (cap-1) × defensive_scale
P3.3 economic L1 band      0.05
cost grid                  5 / 10 / 20 / 50 bps
operating MDD candidates   35% / 40% / 45% / 50%
catastrophe boundary       70%
bootstrap resamples        10,000 at 7 / 21 / 63 mean block days
reference portfolio        $2,000 for route/capacity/liquidation stress
```

Mandatory comparators remain BTC B&H, four-asset equal-weight B&H, frozen legacy BRRK and matched P3.3 cap1.

Primary route economics use verified BTC spot base up to matched cap1 BTC exposure, BTC extra as perp overlay, and ETH/SOL/BNB as perp. All-perp remains a separate stress panel. Native Hyperliquid funding spikes amplify only adverse long debit; Binance remains report-only proxy evidence.

The P2 route/depth artifact is pinned by workflow run/artifact/digest and used only as point-in-time capacity evidence, never historical PIT liquidity.

## Preflight before first result

The contract workflow must run:

1. synthetic/pure contract tests;
2. runner/validator compile checks;
3. pinned route artifact download + digest validation;
4. `run_leverage_0040_once.py --preflight-only`.

`--preflight-only` may fetch the frozen historical market input and verify baseline/data/cap1/capacity integrity, but it must return before constructing any 1.10/1.20/1.30 candidate.

No RUN_ONCE marker may be created until the draft PR's final pre-result head has all applicable gates green.

## One-time execution

Marker:

`research/leverage_0040/RUN_ONCE_LEVERAGE_0040.marker`

Expected SHA-256:

`f54cdf362f60cad19d6c429ac4e008047b45d2cb537a95c96e2bc6dac5ce733a`

The marker is currently absent. Once it is created exactly once on the validated v2 branch, the dedicated workflow may execute the complete preregistered suite exactly once and commit immutable results. Result commits trigger only the result validator, not the run-once workflow.

No post-result retuning is permitted under `LEVERAGE-0040`.

## Still blocked

```text
LEVERAGE-0040 SEARCH RUN:       NO
RESULT SELECTED:                NO
OPERATING BUDGET FROZEN:        NO
RUN_ONCE MARKER:                ABSENT
PRODUCTION >1 RUNTIME:          NO
PRODUCTION AUTHORIZED:          NO_CHANGE
```

Also blocked/separate:

- any result-driven modification of study semantics under 0040;
- search >1.30 without a new experiment ID;
- EXPOSURE-SMOOTH-0038 promotion;
- F23 funding-response redesign;
- shorts / XRP target exposure;
- P5 exit intelligence;
- production leverage authorization.

## Project drift audit

```text
DRIFT_0
```

## Exact next action

```text
self-review v2 diff
-> open draft pre-study PR
-> contract synthetic tests + real preflight-only
-> Phase 0 + research + P3.2 parity/golden + P4 cap=1 + P4 prerequisite + governance
-> fix same PR if needed, still without RUN_ONCE marker
-> final pre-result head all green
-> create exact marker once
-> one-time immutable LEVERAGE-0040 result
-> validate result
-> P4.5 select/fail decision with no retuning
-> P4.6 remains separate production gate
```
