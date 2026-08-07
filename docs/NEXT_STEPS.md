# Next Steps

> Read canonical sources in repository-defined order. GitHub actual state wins over stale prose.

## Current dependency

```text
Final-head revalidation + merge of the last LEVERAGE-0040 pre-run prerequisites:
1. Hyperliquid cross-margin liquidation-distance model
2. pre-result defensive-monotone multiplier policy freeze
```

Normalized main after PR #87:

`6ba3f765fd52839e9841b299aab4a51c9a1cd523`

Current PR:

`#88 — p4-3/leverage-0040-pre-run-prereqs-v1`

Initial validated checkpoint:

`b6b309a5eb9ba4a876b67f631576b608eaa4c8e2`

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

## Prerequisite 1 — liquidation model

`research/leverage_0040/P4_3_LIQUIDATION_MODEL_V1.json`

`research/leverage_0040/liquidation_model.py`

Scope: standard Hyperliquid **cross margin only**, using the frozen pre-result margin snapshot.

```text
MMR = 1 / (2 × tier max leverage)
maintenance margin = stressed notional × MMR − tier deduction
liquidation boundary = cross account equity <= total maintenance margin
```

Inputs must explicitly provide cross-account equity and actual perp notionals. Ordinary spot is not assumed cross collateral; Portfolio Margin is not assumed. Missing implementation accounting fails closed.

Initial checkpoint status: **IMPLEMENTED / TESTED / CI VERIFIED CANDIDATE; MERGE PENDING**.

## Prerequisite 2 — multiplier policy freeze

`research/leverage_0040/LEVERAGE-0040-PRE-RUN-ADDENDUM-V1.json`

`research/leverage_0040/multiplier_policy.py`

Frozen before any >1 historical observation:

```text
leverage_multiplier = 1 + (candidate_cap - 1) × frozen_defensive_scale
final_scale = defensive_scale + (candidate_cap - 1) × defensive_scale²
```

Allowed inputs only:

```text
frozen_defensive_scale
candidate cap ∈ {1.00, 1.10, 1.20, 1.30}
```

No future/candidate PnL, funding signal, raw HMM tuning, P5, EXPOSURE-SMOOTH-0038, short/XRP signal or historically selected threshold may enter the policy.

Initial checkpoint status: **FROZEN BEFORE FIRST RESULT / TESTED / CI VERIFIED CANDIDATE; MERGE PENDING**.

## #88 checkpoint evidence

Head `b6b309a5eb9ba4a876b67f631576b608eaa4c8e2`:

- dedicated prerequisite #1 / `31177869882`: SUCCESS, 14 passed
- Phase 0 #146 / `31177869757`: SUCCESS, 257 passed + 5/5 integration
- Research evidence #52 / `31177869856`: SUCCESS
- P3.2 parity/golden #39 / `31177869824`: SUCCESS
- P4 cap=1 parity #5 / `31177869840`: SUCCESS
- governance #204 / `31177869853`: SUCCESS

The current handoff/checklist commits create a new final head and must receive the same final-head gates. No >1 candidate was run at the checkpoint.

## LEVERAGE-0040 gates unchanged

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
LIQUIDATION MODEL:              CI-VERIFIED CANDIDATE / MERGE PENDING
>1 SELECTION POLICY:            CI-VERIFIED PRE-RESULT FREEZE / MERGE PENDING
>1 PRODUCTION RUNTIME:          NO
PRODUCTION AUTHORIZED:          NO_CHANGE
```

No 1.10/1.20/1.30 historical candidate may be generated before #88 merges and is normalized.

## Project drift audit

```text
DRIFT_0
```

## Exact next action

```text
final-head CI for #88
-> final PR evidence / ready
-> latest governance
-> expected-head squash merge
-> post-merge normalization
-> fresh LEVERAGE-0040 search branch
-> execute preregistered suite exactly once with no post-result retuning
```
