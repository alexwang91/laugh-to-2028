# BRRK Current State

Last updated: 2026-08-07
Status: authoritative cross-chat handoff snapshot

## Authoritative baseline

- P0.1 / P0.2: PASS / MERGED
- P1.1 through P1.8: PASS / MERGED; Phase 1 COMPLETE
- P2.1 through P2.4: PASS / MERGED; Phase 2 COMPLETE
- P3.1 schema-v2 data contract: PASS / MERGED / validated by PR #75
- P3.2 Target calculation API: PASS / TESTED / CI VERIFIED / MERGED by PR #76
- P3.3 rebalance / turnover controls: PASS / TESTED / CI VERIFIED / MERGED by PR #78
- PR #73 remains historically MERGED without a recorded green required PR-governance run before merge; do not retroactively relabel it CI VERIFIED
- PR #74 remains historically MERGED during the GitHub Actions incident without its own pre-merge workflow evidence; PR #75 subsequently validated the merged schema-v2 state
- Historical stale-main PR #70: INVALID / CLOSED / DO NOT REVIVE

## Current main and roadmap position

P3.3 merge commit on main:

`a503e64da4641e434620aa6a04bf9f6448d00135`

```text
P3.1 schema-v2 data contract           PASS / MERGED
P3.2 Target calculation API            PASS / MERGED
P3.3 rebalance / turnover controls      PASS / MERGED
P3.4 contributions                     UNIQUE NEXT ROADMAP IMPLEMENTATION
P4 leverage / operating risk budget     BLOCKED UNTIL P3.4
P5 exit intelligence                    BLOCKED
```

P3.4 must start from the latest main only after this post-merge normalization PR closes.

## Frozen upstream target and control chain

```text
P3.1 canonical data
-> P3.2 BRRK-0011 target
-> P3.3 explicit target-to-position control
```

Asset role remains:

```text
target assets = BTC, ETH, SOL, BNB
feature-only  = XRP
P3.2 gross    <= 1
short target  forbidden
```

P3.2 remains `P3.2-BRRK0011-V1` / BRRK-0011 with committed golden vectors at:

`research/results/p3_2_target_parity/golden_v1.json`

P3.3 does not recompute or alter the P3.2 target.

## P3.3 frozen policy now on main

Machine policy:

`config/rebalance_policy.json`

Version:

`P3.3-L1-BAND-V1`

Metric and routine rule:

```text
L1 target gap = Σ |P3.2 target weight - current position weight|
L1 gap < 0.05  -> suppress routine rebalance
L1 gap >= 0.05 -> post-control desired state = full P3.2 target
```

The 0.05 value is the migrated Plan B execution-control continuity value. It is distinct from the separate P3.2 internal 5% V1 return-model calibration band.

Runtime validation freezes the V1 policy semantics:

```text
FROZEN_REBALANCE_BAND = 0.05
current_short_position -> REBALANCE_TO_P3_2_TARGET_REGARDLESS_OF_BAND
current_gross_above_one -> REBALANCE_TO_P3_2_TARGET_REGARDLESS_OF_BAND
```

Changing the band or safety mapping requires a new policy/version.

Legacy `MIN_TRADE_USD=100` is not a P3.3 portfolio gate. Minimum notional remains downstream order feasibility only.

## P3.3 control contract

Runtime:

`execution/plan-b-bot/beta_bot/rebalance_control.py`

Contract:

`docs/P3_3_REBALANCE_CONTROL.md`

Input:

- immutable P3.2 `TargetCalculationResult`;
- point-in-time account equity;
- signed current BTC/ETH/SOL/BNB notionals;
- registered P3.3 policy.

Output preserves both theoretical and actionable state:

- upstream P3.2 target digest/version/model authority;
- immutable model target weights/notionals;
- current weights/notionals;
- theoretical per-asset gap weights/notionals;
- aggregate L1 gap / theoretical turnover;
- current/target gross and net weights;
- rebalance decision/reason and safety overrides;
- post-control desired state;
- proposed deltas / control turnover;
- suppressed gap when inside band;
- deterministic P3.3 canonical JSON / SHA-256 plan digest;
- minimum-notional downstream role;
- `production_authorized = false`.

Theoretical deviation remains measurable even when routine action is suppressed.

## PR #78 final evidence

Final head:

`53885b993b662991cd28370d4542e48a31f648b5`

Final-head evidence:

- `Phase 0 baseline contract` run `31156709738` (#113): SUCCESS
  - execution pytest: **204 passed in 7.15s**
  - research integration contract: **5 tests / OK**
- `Research evidence normalization` run `31156709594` (#24): SUCCESS
- `P3.2 target research-live parity` run `31156709586` (#11): SUCCESS
  - independent multi-date BRRK research-vs-product parity: SUCCESS
  - committed historical golden enforcement: SUCCESS
- final code/handoff governance run `31156709547` (#146): SUCCESS
- final PR-body-edit governance run `31156872098` (#147): SUCCESS
- expected-head squash merge: `a503e64da4641e434620aa6a04bf9f6448d00135`

Regression coverage includes:

- exact target no-op;
- inside-band suppression with theoretical deviation preserved;
- exact 5% boundary;
- aggregate multi-asset L1 boundary;
- `$60` recommended delta outside band not suppressed by legacy `$100` min-trade;
- current short / gross>1 safety bypass;
- unknown assets fail closed;
- immutable upstream P3.2 target;
- V1 policy band/safety lock;
- deterministic control-plan digest;
- no production authorization.

## P3.3 closure status

```text
IMPLEMENTED:           YES
TESTED:                YES
CI VERIFIED:           YES
MERGED:                YES
PRODUCTION AUTHORIZED: NO_CHANGE
```

## P3.4 boundary

P3.4 is now the unique next implementation and owns **weekly contribution handling**.

P3.4 must consume the merged P3.2 target and P3.3 control contract; it must not rewrite either layer.

Before implementation, reread the exact P3.4 roadmap acceptance contract from `docs/IMPLEMENTATION_ROADMAP_2026-08-05.md`.

P3.4 must not absorb:

- F23 funding-response redesign;
- P4 gross > 1 leverage / operating-risk-budget freeze;
- P5 exit intelligence;
- shorts;
- XRP targets;
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

P3.1 data, P3.2 target and P3.3 target-to-position control semantics are aligned, validated and merged.

## Exact next action

```text
post-merge normalization PR
-> docs-only self-review
-> applicable CI / P3.2 parity / governance
-> write final run evidence into PR metadata
-> newest governance GREEN
-> expected-head merge normalization
-> verify main
-> create fresh P3.4 branch
-> reread P3.4 roadmap acceptance contract
-> implement contribution handling only
```
