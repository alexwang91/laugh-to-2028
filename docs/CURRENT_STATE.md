# BRRK Current State

Last updated: 2026-08-07
Status: authoritative cross-chat handoff snapshot

## Authoritative baseline

- P0.1 / P0.2: PASS / MERGED
- P1.1 through P1.8: PASS / MERGED; Phase 1 COMPLETE
- P2.1 through P2.4: PASS / MERGED; Phase 2 COMPLETE
- P3.1 schema-v2 data contract: PASS / MERGED / validated by PR #75
- P3.2 Target calculation API: PASS / TESTED / CI VERIFIED / MERGED by PR #76
- PR #77 post-P3.2 normalization: PASS / MERGED as `4522e96ab8ff2381fb0e02f74c516a9663bf48de`
- PR #73 remains historically MERGED without a recorded green required PR-governance run before merge; do not retroactively relabel it CI VERIFIED
- PR #74 remains historically MERGED during the GitHub Actions incident without its own pre-merge workflow evidence; PR #75 subsequently validated the merged schema-v2 state
- Historical stale-main PR #70: INVALID / CLOSED / DO NOT REVIVE

## Current roadmap position

Current main / P3.3 base:

`4522e96ab8ff2381fb0e02f74c516a9663bf48de`

```text
P3.1 schema-v2 data contract           PASS / MERGED
P3.2 Target calculation API            PASS / MERGED
P3.3 rebalance / turnover controls      ACTIVE CANDIDATE
P3.4 contributions                     BLOCKED UNTIL P3.3
P4 leverage / operating risk budget     BLOCKED
P5 exit intelligence                    BLOCKED
```

Active fresh branch:

`p3-3/rebalance-turnover-controls-v1`

## Frozen upstream P3.2 authority

P3.3 consumes the existing P3.2 target without recomputing or altering it.

```text
target_assets  = BTC, ETH, SOL, BNB
feature_assets = XRP
P3.2 gross      <= 1
short targets  forbidden
```

P3.2 target engine remains `P3.2-BRRK0011-V1` / model authority `BRRK-0011`.

Committed P3.2 golden evidence remains:

`research/results/p3_2_target_parity/golden_v1.json`

No P3.2 model, HMM/PCA, defensive-scale, data-contract or golden-vector file is modified by the P3.3 candidate.

## P3.3 roadmap acceptance

Canonical roadmap section: **P3.3 Rebalance band / turnover controls**.

Acceptance:

- no unnecessary churn from tiny target changes;
- all deviations from theoretical target measurable.

P3.3 is explicitly post-target control. P3.4 weekly contribution handling is separate.

## P3.3 policy provenance

Legacy BTC execution service already carried:

```text
REBALANCE_BAND=0.05
MIN_TRADE_USD=100
```

The 0.05 band was introduced with the migrated Plan B portfolio allocator on 2026-08-04 and is also documented by the legacy BTC-only README as an execution control.

P3.3 migrates the **0.05 execution-control continuity value** into an explicit four-asset control policy. It does not derive that number from the separate P3.2 internal 5% V1 return-model calibration band.

`MIN_TRADE_USD=100` is not promoted into the P3.3 portfolio gate. Minimum notional remains downstream order feasibility only.

Machine-readable policy:

`config/rebalance_policy.json`

Policy/version:

`P3.3-L1-BAND-V1`

## P3.3 control semantics

Metric:

```text
L1 target gap = Σ |P3.2 target weight - current position weight|
```

Routine rule:

```text
L1 gap < 0.05  -> suppress routine rebalance
L1 gap >= 0.05 -> move post-control desired state to full P3.2 target
```

Theoretical per-asset and aggregate deviations remain recorded in both cases.

Safety overrides bypass the churn band if current state itself violates frozen pre-P4 boundaries:

- any current BTC/ETH/SOL/BNB position is short;
- current absolute gross exceeds 1.

These overrides restore the P3.2 target; they do not authorize shorting or leverage.

## P3.3 implementation candidate

Implemented on the active branch:

- `config/rebalance_policy.json`
- `execution/plan-b-bot/beta_bot/rebalance_control.py`
- `execution/plan-b-bot/tests/test_rebalance_control_p3_3.py`
- `docs/P3_3_REBALANCE_CONTROL.md`
- `.env.example` comments clarifying legacy-vs-canonical control roles

`calculate_rebalance_control(...)` consumes:

- immutable P3.2 `TargetCalculationResult`;
- point-in-time account equity;
- signed current BTC/ETH/SOL/BNB notionals;
- registered P3.3 policy.

It emits auditable fields including:

- upstream P3.2 target digest/version/model authority;
- immutable model target weights/notionals;
- current weights/notionals;
- theoretical gap weights/notionals;
- aggregate L1 gap and theoretical turnover;
- current/target gross and net weights;
- rebalance decision/reason and safety overrides;
- post-control desired state;
- proposed deltas and control turnover;
- suppressed gap when inside band;
- deterministic P3.3 control-plan digest;
- explicit minimum-notional downstream role;
- `production_authorized = false`.

## Candidate tests

P3.3 regression tests cover:

- exact target -> no-op;
- inside-band churn suppression while preserving theoretical gaps;
- exact 5% boundary -> rebalance;
- aggregate multi-asset L1 reaches 5% even though every individual asset gap is below 5%;
- a $60 delta outside the L1 band remains a P3.3 rebalance recommendation despite legacy `$100` min-trade;
- current short exposure bypasses band;
- current gross > 1 bypasses band;
- unknown current asset fails closed;
- upstream P3.2 target remains unchanged;
- no production authorization.

## Current P3.3 status

```text
IMPLEMENTED:           YES — candidate branch
TESTED:                PENDING PR CI
CI VERIFIED:           NO
MERGED:                NO
PRODUCTION AUTHORIZED: NO_CHANGE
```

## Explicit P3.3 exclusions

Do not add in P3.3:

- P3.4 contribution scheduling/handling;
- F23 funding-response redesign;
- P4 gross > 1 leverage or operating-risk-budget freeze;
- P5 exit intelligence;
- short targets;
- XRP targets;
- venue quantity precision;
- minimum-order enforcement;
- routing / slippage / capacity changes;
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

P3.3 is downstream of the frozen P3.2 target and introduces only the roadmap-defined rebalance/turnover control boundary.

## Exact next action

```text
self-review P3.3 diff
-> open P3.3 PR
-> Phase 0 full pytest + research integration
-> P3.2 parity/golden preservation if triggered/applicable
-> PR handoff governance
-> fix every real failure in same PR
-> final-head CI
-> write final evidence into PR body
-> newest body-edit governance GREEN
-> expected-head squash merge
-> verify main
-> post-merge normalization
-> fresh P3.4 branch
```
