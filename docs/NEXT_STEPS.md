# BRRK Next Steps

Last updated: 2026-08-08

## Current instruction

**P5.3 V2 is complete immutable `ARCHITECTURE_PASS` with no profile selected. P5.4 now preregisters exactly three fixed state-to-total-gross behavior maps before any economic evaluation. Validate/merge the P5.4 contract, then implement the mapping mechanics only. P5.5 owns all joint profile/map economics and winner selection.**

## Immediate state

```text
Phase 0-3                              COMPLETE / MERGED
LEVERAGE-0040 / 0041                   COMPLETE / IMMUTABLE / NO_PROMOTION
Phase 4 leverage research              FAIL_STOP
production gross cap                   1.0
production_authorized_components       []
P5.1 event taxonomy                    COMPLETE / FROZEN
P5.2 feature evidence                  COMPLETE / IMMUTABLE / DESCRIPTIVE CLOSEOUT
P5.3 V1                               COMPLETE / IMMUTABLE / ARCHITECTURE_FAIL
P5.3 V2                               COMPLETE / IMMUTABLE EVIDENCE / ARCHITECTURE_PASS
P5.3 selected profile                  NONE
P5.4 contract                          P5.4-FIXED-GROSS-BEHAVIOR-CANDIDATES-V1
P5.4 fixed behavior maps               PREREGISTERED / NO ECONOMIC EVALUATION
P5.4 selected map                      NONE
P5.5 validation                        NOT STARTED
P5.6 integration                       NOT STARTED
```

## Frozen P5.4 candidate family

State order:

```text
NORMAL_BULL
BTC_LEADERSHIP_MATURING
LATE_BULL_ROTATION
EXHAUSTION_WATCH
DE_RISK_1
DE_RISK_2
FLAT
```

Maps:

| State | DE_RISK_ONLY | PROGRESSIVE | EARLY_DEFENSIVE |
| --- | ---: | ---: | ---: |
| NORMAL_BULL | 1.00 | 1.00 | 1.00 |
| BTC_LEADERSHIP_MATURING | 1.00 | 1.00 | 0.95 |
| LATE_BULL_ROTATION | 1.00 | 0.95 | 0.90 |
| EXHAUSTION_WATCH | 1.00 | 0.80 | 0.70 |
| DE_RISK_1 | 0.65 | 0.55 | 0.45 |
| DE_RISK_2 | 0.30 | 0.25 | 0.20 |
| FLAT | 0.00 | 0.00 | 0.00 |

No fourth map may be added after P5.5 economics. Dense/continuous multiplier search is forbidden.

## Frozen composition

```text
P5.4 target asset weight
= frozen upstream P4.1/BRRK target asset weight
x fixed cycle gross multiplier(MARKET_STATE)
```

This guarantees:

- P5.4 can only preserve/reduce existing gross;
- every multiplier is in `[0,1]`;
- no >1 leverage is introduced;
- BRRK relative asset ranking is unchanged;
- no shorts are added;
- freed risk moves to cash/stablecoin.

`DATA_INSUFFICIENT` has no map. P5.5 matched economic evaluation starts on `2021-01-17`, the common P5.3 initialization date.

## Permission boundary

`FLAT=0` is a research target-gross rule. An actual integrated system that reaches zero exposure must remain:

```text
LOCKED_PENDING_HUMAN_APPROVAL
```

MARKET_STATE recovery cannot unlock it.

For P5.5 historical signal economics, a post-FLAT positive target may be computed only as `RESEARCH_HYPOTHETICAL_REENTRY`. That does not authorize a live order.

## P5.5 frozen candidate set

P5.5 must evaluate exactly:

```text
3 frozen P5.3 profiles
x
3 frozen P5.4 maps
=
9 joint candidates
```

plus the required upstream baseline without a cycle overlay.

P5.5 owns:

- event-held-out/leave-one-event-out robustness;
- 7–14 day lead behavior;
- false-positive duration;
- missed upside;
- drawdown avoided;
- terminal wealth / CAGR;
- turnover and explicit cost sensitivity;
- second-wind preservation;
- terminal 2021 bear-transition behavior;
- non-top controls including the 2021 false FLAT;
- no single-event dependency;
- nearby-policy robustness.

No P5.4 winner may be chosen before those tests. If no candidate is robust, fail-stop.

## Frozen product boundaries

- BRRK-0011 relative ranking unchanged;
- BTC/ETH/SOL/BNB long universe unchanged;
- XRP feature-only;
- Hyperliquid primary venue;
- P4.1 defensive scaler `[0,1]` unchanged;
- production gross `1.0`;
- actual re-risk after implemented zero exposure remains human-gated;
- no withdrawal/external-transfer automation;
- no production authorization.

## Exact next step

```text
RUN FRESH P5.4 PREREG CI / GOVERNANCE
IF GREEN, EXACT-HEAD MERGE THE PREREGISTRATION
VERIFY NEW MAIN
CREATE FRESH P5.4 IMPLEMENTATION BRANCH
IMPLEMENT THE THREE FIXED MAPS EXACTLY
TEST MONOTONICITY / GROSS-ONLY SCALING / RELATIVE-RANKING PARITY / FLAT=0
DO NOT RUN P5.5 ECONOMICS UNTIL P5.4 IMPLEMENTATION GATES ARE GREEN
DO NOT SELECT A WINNER
DO NOT PRODUCTION-AUTHORIZE ANYTHING
```
