# Next Steps

> Read canonical sources in repository-defined order. GitHub actual state wins over stale prose.

## Current dependency

```text
P3.4 weekly contribution handling
```

Post-P3.3 normalization PR #79 is merged. Current main / P3.4 base:

`1d9dbebf5087936d0454f631145b176c62da4ec8`

Fresh candidate branch:

`p3-4/contribution-handling-v1`

## Exact roadmap contract

P3.4 roadmap requirement was reread before coding:

> Manual deposit is detected as equity change and included at the next daily decision.

Acceptance:

- deposit does not trigger unscheduled intraday risk increase;
- new cash allocation follows the same target engine.

## Frozen upstream interfaces

P3.4 consumes, not rewrites:

1. P3.2 `TargetCalculationResult` / `P3.2-BRRK0011-V1`;
2. P3.3 `RebalanceControlPlan` / `P3.3-L1-BAND-V1`.

Frozen role boundary:

```text
target assets = BTC, ETH, SOL, BNB
feature-only  = XRP
P3.2 gross    <= 1
short targets forbidden
P3.3 L1 band  = 0.05
```

P3.2 golden vectors and P3.3 policy semantics must remain unchanged.

## Registered P3.4 policy

Machine policy:

`config/contribution_policy.json`

Version:

`P3.4-EQUITY-CHANGE-DAILY-V1`

Semantics:

```text
reference = previous accepted daily-decision account equity
observe signed equity change without source attribution
positive change = contribution candidate, not confirmed transfer
intraday = record only, no target recalculation, no risk increase
allocation = next eligible 00:00 UTC daily decision
allocation path = P3.2 target -> P3.3 control
```

The approximately `$100/week` product assumption is not a detection threshold and is not a scheduler trigger.

## Candidate implementation

Present on branch:

- `config/contribution_policy.json`
- `execution/plan-b-bot/beta_bot/contribution_handling.py`
- `execution/plan-b-bot/tests/test_contribution_handling_p3_4.py`
- `execution/plan-b-bot/tests/test_contribution_boundary_p3_4.py`
- `docs/P3_4_CONTRIBUTION_HANDLING.md`
- updated `docs/CURRENT_STATE.md`

### Observation path

`observe_equity_change(...)` records:

- baseline/observed equity and timestamps;
- signed equity change;
- positive contribution candidate;
- no source attribution;
- next eligible daily decision;
- explicit no intraday action / no target recalculation / no risk increase;
- deterministic digest.

A future exact 00:00 observation may enter that not-yet-accepted daily decision. An observation at an already-accepted baseline 00:00 rolls to the next day and cannot replay the same daily cycle.

### Daily application path

`apply_at_daily_decision(...)` requires the scheduled 00:00 UTC decision and uses the fresh **full** account equity at that decision:

```text
P3.2 calculate_target(fresh full equity)
-> P3.3 calculate_rebalance_control(same full equity)
```

The observed contribution-candidate amount remains diagnostic; there is no separate contribution allocation formula.

## Required P3.4 acceptance evidence

Before merge require:

1. `Phase 0 baseline contract` SUCCESS on final head;
2. all P3.4 unit tests SUCCESS;
3. existing research integration SUCCESS;
4. P3.2 historical parity/golden remains green if applicable/triggered;
5. PR handoff governance SUCCESS;
6. self-review confirms no P3.2/P3.3 mutation, F23/P4/P5 leakage or production authorization;
7. `production_authorized_components = []`.

Key regression cases:

- intraday +$100 change schedules next UTC midnight and never authorizes intraday risk;
- +$37 and +$250 both follow the same detection rule;
- negative change is not a contribution candidate;
- exact future boundary eligibility;
- already-accepted boundary cannot be replayed;
- wrong/intraday application timestamp fails closed;
- fresh full daily equity is passed to P3.2 then P3.3;
- deterministic observation and daily-decision digests.

## Explicit exclusions

Do not add in P3.4:

- transfer-source attribution;
- fixed weekday or mandatory `$100` amount;
- automatic deposit scheduling;
- intraday target recalculation/risk increase;
- contribution-specific target logic;
- P3.2 target changes;
- P3.3 band/safety changes;
- F23 funding-response redesign;
- P4 >1 leverage / operating risk budget;
- P5 exit intelligence;
- short/XRP targets;
- venue min-size/precision/routing/order submission;
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
self-review P3.4 diff
-> open P3.4 PR
-> run Phase 0 / applicable P3.2 parity / research evidence / governance
-> fix every real failure in same PR
-> final-head CI
-> record exact evidence in PR body
-> newest body-edit governance GREEN
-> expected-head squash merge
-> verify main
-> post-merge normalization
-> P4 only after P3.4 closure
```
