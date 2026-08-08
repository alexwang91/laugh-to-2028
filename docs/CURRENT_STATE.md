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
P5.4 behavior mapping          PREREGISTERED / FIXED CANDIDATES / NO SELECTION
P5.5 validation                NEXT AFTER P5.4 IMPLEMENTATION
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

## P5.4 preregistration

Contract: `P5.4-FIXED-STATE-GROSS-BEHAVIOR-V1`

P5.4 freezes four overlay candidates before any P5.5 economics:

| state | HARD_ONLY | GENTLE | BALANCED | DEFENSIVE |
| --- | ---: | ---: | ---: | ---: |
| NORMAL_BULL | 1.00 | 1.00 | 1.00 | 1.00 |
| BTC_LEADERSHIP_MATURING | 1.00 | 1.00 | 0.98 | 0.95 |
| LATE_BULL_ROTATION | 1.00 | 0.95 | 0.90 | 0.80 |
| EXHAUSTION_WATCH | 1.00 | 0.85 | 0.75 | 0.60 |
| DE_RISK_1 | 1.00 | 0.70 | 0.55 | 0.40 |
| DE_RISK_2 | 1.00 | 0.40 | 0.25 | 0.15 |
| FLAT | 0.00 | 0.00 | 0.00 | 0.00 |

`BRRK_NO_CYCLE_CONTROL` is a non-promotable comparator with multiplier `1.0` in every state.

Hard P5.4 rules:

- all overlay multipliers are in `[0,1]`;
- monotone non-increasing with state severity;
- late-bull rotation is not automatically bearish/zero;
- mapping scales total frozen BRRK target only;
- relative BTC/ETH/SOL/BNB ranking is unchanged;
- XRP remains feature-only;
- no shorts and no >1 leverage;
- P5.4 selects no winner;
- P5.5 evaluates 3 frozen P5.3 profiles × 4 behavior maps = 12 candidate combinations;
- counterfactual research re-entry after FLAT does not unlock operational RISK_PERMISSION_LOCK.

## P5.5 boundary

P5.5 owns economic/robustness selection. It must include held-out event analysis, cost sensitivity, missed-upside, drawdown avoided, terminal wealth/CAGR, turnover, second-wind behavior, terminal 2021 behavior and non-top-control false positives. If no combination is robust, P5.5 must fail-stop.

## Frozen product boundaries

- BRRK-0011 relative ranking unchanged;
- P4.1 defensive scale `[0,1]` unchanged;
- production gross cap `1.0`;
- actual zero-exposure -> risk-on remains explicit-human-gated;
- no automated withdrawals/external transfers;
- no production authorization.

## Exact next action

```text
CI-VERIFY / MERGE P5.4 PREREGISTRATION
IMPLEMENT PURE STATE->GROSS MAPPING MECHANICS
VERIFY NO RELATIVE-RANKING CHANGE AND NO >1 GROSS
FREEZE P5.5 VALIDATION CONTRACT BEFORE ECONOMIC EVALUATION
DO NOT SELECT A P5.4 WINNER
DO NOT PRODUCTION-AUTHORIZE ANYTHING
```
