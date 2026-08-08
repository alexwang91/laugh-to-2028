# BRRK Current State

Last updated: 2026-08-08
Status: **authoritative current-state handoff**

## Executive state

```text
Phase 0-3                      COMPLETE / MERGED
Phase 4 leverage research      FAIL_STOP / no eligible >1 candidate
production gross cap           1.0
production_authorized_components []
P5.1 event taxonomy            COMPLETE / FROZEN
P5.2 feature evidence          COMPLETE / IMMUTABLE / DESCRIPTIVE CLOSEOUT
P5.3 V1                       COMPLETE / IMMUTABLE / ARCHITECTURE_FAIL
P5.3 V2                       COMPLETE / IMMUTABLE EVIDENCE / ARCHITECTURE_PASS
P5.4 behavior mapping          COMPLETE / FIXED 4-MAP FAMILY / PURE IMPLEMENTATION / NO SELECTION
P5.5 validation                IMPLEMENTED / R1+R2 FROZEN / RESULT NOT RUN
P5.6 integration               NOT STARTED
Phase 6 shadow                 NOT STARTED
Phase 7 limited-live readiness NOT STARTED / actual launch requires explicit approval
Phase 8 bear-short research    NOT STARTED
production authorization       NONE
```

## Frozen upstream

P5.3 V2 immutable summary SHA256: `05d5d68a59c8b13f1122d98ed75d03934defdc9d73c7dd92e038c92fd97d2e52`.

P5.4 canonical contract: `P5.4-FIXED-STATE-GROSS-BEHAVIOR-V1`; four maps `HARD_ONLY / GENTLE / BALANCED / DEFENSIVE`; pure scalar total-gross implementation only.

## P5.5 frozen research contracts

- base: `P5.5-JOINT-PROFILE-MAP-VALIDATION-V1`
- R1: frozen pre-result MaxDD sign semantics (`abs(MaxDD)` comparison)
- R2: frozen pre-result common-coverage correction

P5.5 evaluates exactly:

```text
EARLY / BALANCED / CONSERVATIVE
x
HARD_ONLY / GENTLE / BALANCED / DEFENSIVE
= 12 candidates
```

`BRRK_NO_CYCLE_CONTROL` is non-promotable comparator.

### R2 common observable window

The immutable P5.2 feature result explicitly ends `2026-02-28`; the immutable P5.3 V2 MARKET_STATE path inherits that end. Phase-4 BRRK targets/prices extend through `2026-08-02`.

Before any P5.5 candidate economics, R2 therefore freezes:

```text
authoritative economic start  2022-12-10
authoritative economic end    2026-02-28
rule                           min(BRRK target/price end, frozen MARKET_STATE end)
forward-fill MARKET_STATE      forbidden
fabricate feature/state data   forbidden
absent later state -> zero     forbidden
```

2021 remains all-event behavior diagnostics only; no 2021 BRRK economic path is fabricated.

### Economic semantics

P5.5 reuses repository-established mechanics:

- authoritative BRRK prices/targets rebuilt by `run_leverage_0040_once_r1.py`;
- `simulate_p3_3_economic_path` with drifted current weights;
- decision target held over next daily return;
- 5% L1 rebalance band;
- costs `5 / 10 / 20 / 50 bps` per executed absolute weight change;
- no funding in primary selection;
- matched unmodified BRRK comparator;
- metrics: terminal multiple, CAGR, MaxDD, Sharpe, Calmar, turnover and average gross.

### Validation/selection discipline

Hard gates remain frozen:

- terminal-event partial de-risk;
- 2021/2025 second-wind preservation;
- known 2021 false FLAT retained and finite <=10d;
- cost sensitivity and usefulness;
- start-date robustness;
- event-held-out robustness;
- adjacent-policy robustness.

Primary objective remains highest 5-bps after-cost CAGR **among all-gate passers**. No eligible candidate -> `NO_PROMOTION / FAIL_STOP`.

## Implementation state

Implemented but not run:

- `p5_5_validation.py`: pure event/economic/robustness gates + frozen selector;
- `run_p5_5_joint_validation.py`: base matched BRRK runner;
- `run_p5_5_joint_validation_r2.py`: pre-result common-coverage corrected entrypoint;
- `validate_p5_5_joint_validation_result.py`: immutable result validator;
- synthetic tests for held-out math, MaxDD R1 semantics, robustness, adjacency and near-tie selection;
- dedicated pre/post-result CI and one-time RUN_ONCE workflow.

No candidate economics has been produced at this state.

## Frozen product boundaries

- BRRK relative ranking unchanged;
- P4.1 defensive scale `[0,1]` unchanged;
- production gross cap `1.0`;
- actual zero-exposure -> risk-on remains explicit-human-gated;
- no automated withdrawals/external transfers;
- no production authorization.

## Exact next action

```text
OPEN / CI-VERIFY P5.5 IMPLEMENTATION PR
PRE-RUN GATES MUST BE GREEN
SUBMIT ONE RUN_ONCE MARKER
COMMIT / VALIDATE IMMUTABLE P5.5 RESULT
IF A CANDIDATE PASSES ALL FROZEN GATES -> P5.6 INTEGRATION ELIGIBLE
ELSE -> P5.5 NO_PROMOTION / P5.6 BLOCKED
NO PRODUCTION AUTHORIZATION
```
