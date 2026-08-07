# Next Steps

> Read canonical sources in repository-defined order. GitHub actual state wins over stale prose.

## Current dependency

```text
Validate and merge the final LEVERAGE-0040 pre-run prerequisites:
1. Hyperliquid cross-margin liquidation-distance model
2. pre-result defensive-monotone multiplier policy freeze
```

Normalized main after PR #87:

`6ba3f765fd52839e9841b299aab4a51c9a1cd523`

Current fresh candidate:

`p4-3/leverage-0040-pre-run-prereqs-v1`

## Frozen authority

```text
P4.1 defensive scaler       frozen 0 .. 1; unchanged
LEVERAGE-0039              STOPPED_PRE_RUN / NO RESULT / DO NOT REUSE
LEVERAGE-0040              PREREGISTERED / MERGED / NOT RUN
two-layer cap=1 wiring     PASS / MERGED
production gross cap       1.0 unchanged
production authorization   none
```

`production_authorized_components = []` remains unchanged.

## Candidate prerequisite 1 — liquidation model

Contract:

`research/leverage_0040/P4_3_LIQUIDATION_MODEL_V1.json`

Implementation:

`research/leverage_0040/liquidation_model.py`

Model version is standard Hyperliquid **cross margin only**. It uses the frozen pre-result margin snapshot and the official maintenance equations:

```text
MMR = 1 / (2 × tier max leverage)
maintenance margin = stressed notional × MMR − tier deduction
liquidation boundary = cross account equity <= total maintenance margin
```

It requires explicit cross-account equity and actual perp notionals. It does not assume ordinary spot is collateral and does not assume Portfolio Margin is enabled. Missing implementation accounting fails closed.

Tests lock:

- frozen snapshot/hash;
- BTC/ETH/SOL/BNB first-tier MMR;
- tier-boundary continuity;
- single-position parity with the published Hyperliquid liquidation-price formula;
- cross-asset maintenance/PnL aggregation;
- deterministic stress-ray distance;
- fail-closed malformed/unsupported inputs.

Status: **IMPLEMENTED CANDIDATE / CI PENDING**.

## Candidate prerequisite 2 — multiplier policy freeze

Pre-run addendum:

`research/leverage_0040/LEVERAGE-0040-PRE-RUN-ADDENDUM-V1.json`

Implementation:

`research/leverage_0040/multiplier_policy.py`

Frozen before any >1 historical result:

```text
leverage_multiplier = 1 + (candidate_cap - 1) × frozen_defensive_scale
final_scale = defensive_scale + (candidate_cap - 1) × defensive_scale²
```

Allowed inputs only:

```text
frozen_defensive_scale
candidate cap ∈ {1.00, 1.10, 1.20, 1.30}
```

This is threshold-free and deterministic. It preserves cap=1 identity, gives no economic exposure at defensive scale 0, fades extra leverage continuously as defensive risk reduction increases, and reaches the candidate cap only at defensive scale 1.

Forbidden as inputs: future/candidate PnL, funding signal, raw HMM tuning, P5 logic, EXPOSURE-SMOOTH-0038, short/XRP signals or historically selected thresholds.

Status: **FROZEN CANDIDATE BEFORE FIRST RESULT / CI PENDING**.

## Dedicated prerequisite CI

`.github/workflows/p4-3-pre-run-prereqs.yml`

This gate runs only liquidation-model and multiplier-policy contract tests. It does not execute any 1.10/1.20/1.30 historical candidate.

Full Phase 0, P3.2 parity/golden, P4 cap=1 parity and governance must also remain green.

## LEVERAGE-0040 gates remain unchanged

```text
research caps                1.00 / 1.10 / 1.20 / 1.30
operating MDD candidates     35% / 40% / 45% / 50%
frozen defensive tail gate  20% CVaR/CDaR
cost grid                    5 / 10 / 20 / 50 bps
catastrophe boundary         70%
```

Mandatory benchmarks remain BTC buy-and-hold, four-asset equal-weight buy-and-hold, frozen corrected BRRK and P4 candidates. Mandatory stresses remain historical windows, gaps/volatility, native funding debit spikes, degraded fills/depth/capacity and liquidation distance.

## Still blocked

```text
LEVERAGE-0040 SEARCH RUN:       NO
RESULT SELECTED:                NO
OPERATING BUDGET FROZEN:        NO
LIQUIDATION MODEL VALIDATED:    CI PENDING
>1 SELECTION ALGORITHM FROZEN:  CANDIDATE / CI PENDING
>1 PRODUCTION RUNTIME:          NO
PRODUCTION AUTHORIZED:          NO_CHANGE
```

No >1 historical candidate may be generated on this prerequisite branch.

## Project drift audit

```text
DRIFT_0
```

## Exact next action

```text
open prerequisite PR
-> dedicated prerequisite gate + Phase 0 + P3.2 parity/golden + P4 cap=1 + governance
-> same-PR fixes if required
-> final-head merge + normalization
-> fresh LEVERAGE-0040 search branch
-> execute preregistered suite exactly once with no post-result retuning
```
