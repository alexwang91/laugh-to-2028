# Next Steps

> Read canonical sources in repository-defined order. GitHub actual state wins over stale prose.

## Current dependency

```text
P3.2 Target calculation API
```

PR #75 restored real P3.1 schema-v2 validation evidence and merged as:

`c25b64fd42043bbaa61e264a8591bfdc813f5e40`

Final #75 evidence:

- Phase 0 #101 / run `31152649985`: SUCCESS, 187 execution tests passed and research integration SUCCESS
- Research evidence normalization #13 / run `31152649957`: SUCCESS
- final PR governance #133 / run `31152716966`: SUCCESS

P3.2 is now active on fresh branch:

`p3-2/target-calculation-api-v3`

## Frozen input role boundary

```text
target_assets  = BTC, ETH, SOL, BNB
feature_assets = XRP
strategy-signal daily payload = BTC, ETH, SOL, BNB, XRP
router-eligible assets         = BTC, ETH, SOL, BNB only
```

XRP remains feature-only and cannot receive target exposure.

## P3.2 contract

Input:

- schema-v2 canonical strategy-signal daily data
- account equity
- current positions
- approved ProductConfig

Output:

- BTC/ETH/SOL/BNB target weights
- risky-sleeve relative weights
- cash share
- base gross target <= 1
- semantic risk state and posterior
- corrected defensive scale / risk-off probability / meta scale
- regime refit session
- feature snapshot
- model, target-engine and data-contract versions
- canonical data digest

Timing:

- decision at D 00:00 UTC consumes completed data exactly through D-1
- current V1 row at D-1 becomes decision-D target
- defensive scale is the most recent frozen 30-calendar-day BRRK refit active on D-1

Frozen chain:

```text
four-asset V1
-> gross normalization <= 1
-> price-only five-series regime features (XRP feature-only)
-> RobustScaler + PCA4 + sticky VariationalGaussianHMM
-> filtered posterior
-> state-conditioned internally-banded V1 return distribution
-> 5000 x 20d Student-t paths
-> corrected CVaR/CDaR scale
-> final_scale = 1 - P(RISK_OFF) * (1 - meta_scale)
-> target = V1 raw target * final_scale
```

The internal 5% V1 band is only a frozen BRRK return-model calibration input. P3.2 does not use current positions to band or throttle the emitted target.

## Current implementation

Already present on the P3.2 branch:

- `execution/plan-b-bot/beta_bot/target_math.py`
- `execution/plan-b-bot/beta_bot/target_engine.py`
- pinned scientific runtime dependencies
- `execution/plan-b-bot/tests/test_target_engine_p3_2.py`
- `research/integration/p3_2_target_parity.py`
- `.github/workflows/p3-2-target-parity.yml`
- updated `docs/CURRENT_STATE.md`

## Required acceptance evidence

Open one P3.2 PR and require all of the following on its final head:

1. `Phase 0 baseline contract` SUCCESS
   - full execution pytest
   - existing research integration contract
2. `P3.2 target research-live parity` SUCCESS
   - 2021 V1-only historical parity before a legal BRRK regime refit exists
   - multiple full BRRK historical decisions from late 2022 through 2026
   - compare per-asset target, gross, cash, refit date, semantic posterior/state, meta scale, defensive scale and feature snapshot
3. `PR handoff governance` SUCCESS
4. self-review confirms no P3.3/P3.4/P4/P5 scope leakage
5. `production_authorized_components = []`

If parity dates do not demonstrate materially different state/exposure regimes, use the first CI report to replace/add **predeclared historical dates** that broaden coverage. Do not retune model parameters or thresholds on the same historical window.

## Explicit exclusions

Do not add:

- P3.3 target-vs-held rebalance / turnover bands
- P3.4 contribution handling
- F23 funding-response redesign
- P4 leverage above 1 or operating-risk-budget freeze
- P5 exit intelligence
- short targets
- XRP targets
- production authorization

## Production authorization

```text
NO_CHANGE
production_authorized_components = []
```

## Project drift audit

```text
DRIFT_0
```

## Exact next action

```text
self-review current P3.2 diff
-> open P3.2 PR
-> run Phase 0 + P3.2 parity + PR governance
-> fix every real failure in same PR
-> inspect historical parity coverage
-> final-head CI
-> update PR body with exact evidence
-> newest governance GREEN
-> expected-head squash merge
-> verify main
-> post-merge normalization
-> fresh P3.3 branch
```
