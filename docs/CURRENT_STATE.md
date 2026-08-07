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
- PR #79 post-P3.3 normalization: PASS / MERGED as `1d9dbebf5087936d0454f631145b176c62da4ec8`
- PR #73 remains historically MERGED without a recorded green required PR-governance run before merge; do not retroactively relabel it CI VERIFIED
- PR #74 remains historically MERGED during the GitHub Actions incident without its own pre-merge workflow evidence; PR #75 subsequently validated the merged schema-v2 state
- Historical stale-main PR #70: INVALID / CLOSED / DO NOT REVIVE

## Current roadmap position

Current main / P3.4 base:

`1d9dbebf5087936d0454f631145b176c62da4ec8`

```text
P3.1 schema-v2 data contract           PASS / MERGED
P3.2 Target calculation API            PASS / MERGED
P3.3 rebalance / turnover controls     PASS / MERGED
P3.4 weekly contribution handling      IMPLEMENTED / TESTED / CI-VERIFIED CANDIDATE IN PR #80
P4 leverage / operating risk budget    BLOCKED UNTIL P3.4 MERGES + NORMALIZES
P5 exit intelligence                   BLOCKED
```

Active PR / branch:

- PR: `#80`
- branch: `p3-4/contribution-handling-v1`
- fresh base: `1d9dbebf5087936d0454f631145b176c62da4ec8`
- latest fully validated implementation checkpoint before this handoff update: `ec641f555826ae3484fa1ef52cd2f90d05e43fa7`

## Frozen upstream chain

P3.4 consumes, and must not rewrite:

```text
P3.1 canonical daily data
-> P3.2-BRRK0011-V1 target
-> P3.3-L1-BAND-V1 target-to-position control
-> P3.4 contribution timing/equity handling
```

Frozen boundaries remain:

```text
target assets = BTC, ETH, SOL, BNB
feature-only  = XRP
P3.2 gross    <= 1
short targets forbidden
P3.3 routine L1 band = 0.05
```

P3.2 committed golden vectors remain unchanged at `research/results/p3_2_target_parity/golden_v1.json`.

## P3.4 roadmap authority

Exact roadmap requirement reread before coding:

> Manual deposit is detected as equity change and included at the next daily decision.

Acceptance:

- deposit does not trigger unscheduled intraday risk increase;
- new cash allocation follows the same target engine.

P3.4 does not require a fixed weekday, does not require an exact `$100` contribution and does not create a contribution-specific allocation model.

## P3.4 machine policy

Machine policy: `config/contribution_policy.json`

Version: `P3.4-EQUITY-CHANGE-DAILY-V1`

Frozen semantics:

```text
equity reference:
  previous accepted daily-decision account equity

detection:
  observe signed account-equity change without source attribution

positive change:
  contribution candidate, not confirmed transfer attribution

intraday:
  record only
  no target recalculation
  no risk increase

application:
  next eligible 00:00 UTC daily decision
  P3.2-BRRK0011-V1 -> P3.3-L1-BAND-V1

weekly ~$100:
  product assumption only
  not a detection threshold
  not a scheduling trigger
```

Account equity alone is not used to claim whether a positive change came from a deposit or PnL. Positive change is deliberately a contribution candidate rather than confirmed source attribution.

## P3.4 timing and allocation semantics

Example intraday observation:

```text
previous accepted decision: 2026-08-07 00:00 UTC
positive equity change:     2026-08-07 13:45 UTC
next eligible allocation:   2026-08-08 00:00 UTC
```

The intraday observation can never invoke P3.2/P3.3 or authorize increased risk.

If a change is observed exactly at a future 00:00 boundary before that boundary is accepted, it may enter that decision. If the observation timestamp equals an already-accepted baseline decision, P3.4 rolls it to the following day rather than replaying the same daily decision.

At the scheduled daily decision P3.4 uses **fresh full account equity**, not merely the observed contribution-candidate amount:

```text
calculate_target(... fresh account equity ...)
-> calculate_rebalance_control(... same fresh account equity ...)
```

Thus new cash follows the same BRRK target engine and the same P3.3 control. Contribution amount is diagnostic only. P3.4 does not bypass P3.3 merely because cash was added.

## P3.4 implementation candidate

Implemented in PR #80:

- `config/contribution_policy.json`
- `execution/plan-b-bot/beta_bot/contribution_handling.py`
- `execution/plan-b-bot/tests/test_contribution_handling_p3_4.py`
- `execution/plan-b-bot/tests/test_contribution_boundary_p3_4.py`
- `docs/P3_4_CONTRIBUTION_HANDLING.md`

Observation output records previous accepted decision/equity, observed timestamp/equity, signed equity change, contribution-candidate amount, no-source-attribution classification, scheduled decision, explicit intraday prohibitions and deterministic digest.

Daily-decision output records observation digest, contribution candidate, fresh full decision equity, P3.2 version/digest/result, P3.3 version/digest/plan, deterministic P3.4 digest and `production_authorized = false`.

## P3.4 regression coverage

Tests cover:

- frozen P3.4 daily-only policy and P3.2 -> P3.3 allocation path;
- policy timing/allocation path cannot silently drift under V1;
- intraday positive change schedules next UTC midnight and has no intraday risk permission;
- +$37 and +$250 both detected, proving `$100/week` is not a threshold;
- negative equity change is not a contribution candidate;
- future exact 00:00 observation may enter that boundary;
- an already-accepted baseline 00:00 cannot be replayed;
- wrong/intraday application timestamp fails closed;
- fresh full daily equity is passed through the same P3.2 target engine and P3.3 control;
- observation and contribution-aware decision digests are deterministic;
- canonical approved product ID is used consistently in the P3.4 chain fixture;
- no production authorization.

## P3.4 validated implementation checkpoint

Checkpoint head:

`ec641f555826ae3484fa1ef52cd2f90d05e43fa7`

Evidence:

- `Phase 0 baseline contract` run `31159462257` (#119): **SUCCESS**
  - execution pytest: **215 passed in 6.27s**
  - research integration contract: **5 tests / OK**
- `Research evidence normalization` run `31159462313` (#30): **SUCCESS**
- `P3.2 target research-live parity` run `31159463430` (#17): **SUCCESS**
  - independent multi-date BRRK target parity: SUCCESS
  - committed historical golden enforcement: SUCCESS
- latest `PR handoff governance` on this checkpoint: run `31159462403` (#155): **SUCCESS**

History of same-PR corrections:

1. Initial PR head `5c3c126434eb7490c9c66b9e85bd241407aed51a` had one Phase-0 test failure: a chain assertion hard-coded `BRRK-PLAN-B` while the canonical product ID is `brkk-laugh-to-2028`. Result: **214 passed / 1 failed**. Runtime implementation was unchanged.
2. The assertion was corrected in the same PR; checkpoint `e8a03a18727d04e654ffc01a050adceb798af4f3` passed **215 tests + 5/5 integration** and all upstream gates.
3. Final self-review found the synthetic `TargetCalculationResult` fixture still carried the old product-ID label even though it did not affect runtime behavior. The fixture was aligned to canonical `brkk-laugh-to-2028`; checkpoint `ec641f55...` then re-passed all four gates above.

## Checkpoint self-review

Versus fresh base `1d9dbebf5087936d0454f631145b176c62da4ec8`:

- scope remains exactly 7 changed files;
- only P3.4 policy/module/tests/contract/handoff changed;
- no P3.2/P3.3 runtime or golden mutation;
- no router/executor/product-config/decision-registry/authorization mutation;
- no F23/P4/P5 behavior introduced.

```text
DRIFT_0
```

## Candidate status

```text
IMPLEMENTED:           YES
TESTED:                YES
CI VERIFIED:           YES at checkpoint ec641f55...
MERGED:                NO
PRODUCTION AUTHORIZED: NO_CHANGE
```

This handoff update itself moves the PR head. That new final handoff head must re-run the normal PR workflows. No further branch-file mutation is planned after this update. Only after final-head CI is fully green may PR metadata be updated and expected-head merge occur.

## Explicit P3.4 exclusions

Do not add in P3.4:

- transfer-source attribution;
- automatic contribution scheduling or fixed weekday;
- mandatory `$100` amount;
- intraday target calculation or intraday risk increase;
- contribution-specific alpha/target sleeve;
- changes to P3.2 target semantics;
- changes to P3.3 band/safety semantics;
- F23 funding-response redesign;
- P4 gross > 1 leverage or operating-risk-budget freeze;
- P5 exit intelligence;
- shorts;
- XRP targets;
- venue min-order/precision/routing/order submission;
- production authorization.

## Production authorization

```text
NO_CHANGE
production_authorized_components = []
```

## Exact next action

```text
final-head Phase 0 + research evidence + P3.2 parity/golden + PR governance
-> all GREEN
-> final diff self-review
-> update PR #80 body with exact final-head run IDs/results
-> require newest body-edit governance GREEN
-> re-fetch PR and verify head unchanged
-> expected-head squash merge #80
-> verify new main
-> fresh docs-only post-merge normalization PR
-> merge normalization
-> reread exact P4 roadmap before any P4 implementation
```
