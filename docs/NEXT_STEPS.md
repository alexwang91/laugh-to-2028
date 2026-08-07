# Next Steps

> Read canonical sources in repository-defined order. GitHub actual state wins over stale prose.

## Current dependency

```text
P3.3 rebalance / turnover controls
```

P3.2 is PASS / TESTED / CI VERIFIED / MERGED. Post-P3.2 normalization PR #77 is merged and current main is:

`4522e96ab8ff2381fb0e02f74c516a9663bf48de`

Fresh P3.3 branch:

`p3-3/rebalance-turnover-controls-v1`

## Frozen upstream target

P3.3 must consume, not recompute, the P3.2 `TargetCalculationResult`.

```text
target assets = BTC, ETH, SOL, BNB
feature-only  = XRP
P3.2 gross    <= 1
short target  forbidden
```

P3.2 target engine remains `P3.2-BRRK0011-V1`; committed target golden vectors remain unchanged.

## Registered P3.3 policy

Machine-readable policy:

`config/rebalance_policy.json`

Version:

`P3.3-L1-BAND-V1`

Routine metric/rule:

```text
L1 gap = Σ |target_weight - current_weight|
L1 < 0.05  -> suppress routine churn
L1 >= 0.05 -> post-control desired state = full P3.2 target
```

The 0.05 value is migrated from the existing Plan B execution-control continuity value. It is not sourced from the separate P3.2 internal V1 5% return-model calibration band.

Current short exposure or current gross > 1 bypasses the band and restores the P3.2 target because those current states violate frozen pre-P4 boundaries.

Legacy `$100` minimum trade notional is **not** a P3.3 portfolio gate. It remains downstream order feasibility only.

## Candidate implementation

Present on the branch:

- `config/rebalance_policy.json`
- `execution/plan-b-bot/beta_bot/rebalance_control.py`
- `execution/plan-b-bot/tests/test_rebalance_control_p3_3.py`
- `docs/P3_3_REBALANCE_CONTROL.md`
- updated `.env.example` role comments
- updated `docs/CURRENT_STATE.md`

The pure control plan exposes both theoretical and actionable state:

- immutable model target
- current positions/weights
- per-asset theoretical gaps
- aggregate L1 gap / theoretical turnover
- rebalance decision and reason
- safety override reason(s)
- post-control desired positions
- proposed control delta
- actual control turnover after band suppression
- suppressed gap when no action occurs
- upstream P3.2 digest/version
- deterministic P3.3 plan digest

## Required P3.3 acceptance evidence

Before merge require:

1. `Phase 0 baseline contract` SUCCESS on final head;
2. all P3.3 unit tests SUCCESS;
3. existing research integration remains SUCCESS;
4. P3.2 historical parity/golden remains green if the workflow is applicable/triggered;
5. `PR handoff governance` SUCCESS;
6. self-review confirms P3.3 did not mutate P3.2 target authority, P3.4, F23, P4, P5, routing/order feasibility or authorization;
7. `production_authorized_components = []`.

Key regression cases:

- exact/no-op target;
- inside-band suppression with complete deviation measurement;
- exact 5% boundary;
- multi-asset aggregate L1 boundary;
- `$60` recommended delta outside band is not suppressed by legacy `$100` min-trade;
- short and gross>1 safety-band bypass;
- unknown assets fail closed;
- upstream target is unchanged.

## Explicit exclusions

Do not add in P3.3:

- P3.4 weekly contribution handling;
- F23 funding-response redesign;
- P4 >1 leverage / operating risk budget;
- P5 exit intelligence;
- short targets;
- XRP targets;
- venue min-size enforcement;
- quantity precision;
- routing/slippage/capacity changes;
- order slicing/submission;
- production authorization.

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
self-review current P3.3 diff
-> open P3.3 PR
-> run Phase 0 / applicable P3.2 parity / PR governance
-> fix every real failure in same PR
-> final-head CI
-> record final run IDs in PR body
-> newest body-edit governance GREEN
-> expected-head squash merge
-> verify main
-> post-merge normalization
-> fresh P3.4 branch
```
