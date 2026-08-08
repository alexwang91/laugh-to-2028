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
P5.3 selected profile          NONE
P5.4 behavior mapping          PREREGISTERED / IMPLEMENTED PURE SCALAR LAYER / NO SELECTION
P5.5 validation                NEXT / CONTRACT MUST FREEZE BEFORE ECONOMIC RUN
P5.6 integration               NOT STARTED
Phase 6 shadow                 NOT STARTED
Phase 7 limited-live readiness NOT STARTED / actual launch requires explicit approval
Phase 8 bear-short research    NOT STARTED
production authorization       NONE
```

## Immutable P5.3 V2 dependency

- result commit: `e732b7ebe570236bf43084caecb6ea15f7edecb8`
- summary SHA256: `05d5d68a59c8b13f1122d98ed75d03934defdc9d73c7dd92e038c92fd97d2e52`
- architecture pass only; no profile selected;
- `2021-02-23` false raw FLAT remains immutable evidence;
- MARKET_STATE has no permission-unlock authority.

## P5.4 frozen candidate family

Contract: `P5.4-FIXED-STATE-GROSS-BEHAVIOR-V1`

| state | HARD_ONLY | GENTLE | BALANCED | DEFENSIVE |
| --- | ---: | ---: | ---: | ---: |
| NORMAL_BULL | 1.00 | 1.00 | 1.00 | 1.00 |
| BTC_LEADERSHIP_MATURING | 1.00 | 1.00 | 0.98 | 0.95 |
| LATE_BULL_ROTATION | 1.00 | 0.95 | 0.90 | 0.80 |
| EXHAUSTION_WATCH | 1.00 | 0.85 | 0.75 | 0.60 |
| DE_RISK_1 | 1.00 | 0.70 | 0.55 | 0.40 |
| DE_RISK_2 | 1.00 | 0.40 | 0.25 | 0.15 |
| FLAT | 0.00 | 0.00 | 0.00 | 0.00 |

`BRRK_NO_CYCLE_CONTROL` remains a non-promotable all-1.0 comparator.

## P5.4 implementation

`research/cycle_exit/p5_4_behavior_mapping.py` is a pure mechanics layer only:

```text
adjusted_target = frozen_brrk_target * frozen_state_multiplier
```

It enforces:

- exact BTC/ETH/SOL/BNB target schema;
- long-only input;
- upstream gross <= 1.0;
- multiplier in `[0,1]`;
- adjusted gross never exceeds upstream gross;
- scalar-only transformation, preserving relative ranking/proportions whenever multiplier >0;
- FLAT and DATA_INSUFFICIENT -> zero target;
- no prices, returns, costs, selection, permission unlock or production side effects.

P5.4 still selects no winner. P5.5 evaluates the frozen 3 profiles × 4 maps = 12 combinations.

## P5.5 boundary

P5.5 must freeze its validation/economic contract before calculating candidate economics. It must reuse the repository's established target/path/cost metric semantics rather than introduce a favorable cycle-specific backtester.

Required dimensions remain: held-out events, lead/lag, false-positive duration, missed upside, drawdown avoided, terminal wealth/CAGR, turnover/cost sensitivity, second-wind preservation, 2021 terminal transition and non-top controls. If no combination is robust, fail-stop.

## Frozen product boundaries

- BRRK-0011 relative ranking unchanged;
- P4.1 defensive scale `[0,1]` unchanged;
- production gross cap `1.0`;
- actual zero-exposure -> risk-on remains explicit-human-gated;
- no automated withdrawals/external transfers;
- no production authorization.

## Exact next action

```text
CI-VERIFY / MERGE PURE P5.4 MAPPING IMPLEMENTATION
VERIFY NEW MAIN
FREEZE P5.5 VALIDATION CONTRACT BEFORE ANY ECONOMIC EVALUATION
IMPLEMENT P5.5 USING ESTABLISHED BRRK TARGET/PATH/COST METRICS
RUN ONCE / IMMUTABLE RESULT / SELECT ONLY IF ALL HARD GATES PASS
DO NOT PRODUCTION-AUTHORIZE ANYTHING
```
