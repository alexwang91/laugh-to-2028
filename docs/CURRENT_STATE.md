# BRRK Current State

Last updated: 2026-08-08
Status: **authoritative current-state handoff**

## Executive state

```text
Phase 0                         COMPLETE / MERGED
Phase 1                         COMPLETE / MERGED
Phase 2                         COMPLETE / MERGED
Phase 3                         COMPLETE / MERGED
P4.1 defensive scaler          COMPLETE / MERGED / frozen [0,1]
LEVERAGE-0040 / 0041           COMPLETE / IMMUTABLE / NO_PROMOTION
Phase 4 leverage research      FAIL_STOP / no eligible >1 candidate
P4.6 production leverage gate  BLOCKED
P5.1 event taxonomy            COMPLETE / MERGED / FROZEN
P5.2 feature families          COMPLETE / IMMUTABLE / DESCRIPTIVE CLOSEOUT
P5.3 V1 state model            COMPLETE / IMMUTABLE / NO_PROMOTION / ARCHITECTURE_FAIL
P5.3 V2 architecture           COMPLETE / IMMUTABLE EVIDENCE / ARCHITECTURE_PASS
P5.3 selected profile          NONE
P5.4 behavior candidates       PREREGISTERED / FIXED / NO ECONOMIC EVALUATION
P5.4 selected map              NONE
P5.5 validation                NOT STARTED
P5.6 integration               NOT STARTED
Phase 6 integrated shadow      NOT STARTED
Phase 7 limited live long      NOT STARTED / actual launch requires explicit approval
Phase 8 bear-short research    NOT STARTED
production authorization       NONE
```

`production_authorized_components = []`

Current production gross cap remains `1.0`.

## Immutable P5.3 handoff

P5.3 V1 is immutable `NO_PROMOTION / ARCHITECTURE_FAIL`.

P5.3 V2 architecture result:

```text
architecture contract    P5.3-MARKET-STATE-PERMISSION-SEPARATION-V2
evidence contract        P5.3-V2-MARKET-STATE-PATH-EVIDENCE-V1
result commit            e732b7ebe570236bf43084caecb6ea15f7edecb8
summary SHA256           05d5d68a59c8b13f1122d98ed75d03934defdc9d73c7dd92e038c92fd97d2e52
architecture_pass        true
selected profile         NONE
production authorization NONE
```

V2 preserves exact V1 signal parity and the `2021-02-23` false raw FLAT, while making later MARKET_STATE history observable. Operational re-risk permission remains separate and explicit-human-gated.

Formal closeout: `docs/P5_3_V2_MARKET_STATE_CLOSEOUT.md`.

## P5.4 frozen preregistration

Contract: `P5.4-FIXED-GROSS-BEHAVIOR-CANDIDATES-V1`  
Documentation: `docs/P5_4_FIXED_GROSS_BEHAVIOR_PREREG.md`  
Status: `FROZEN_BEFORE_P5_4_ECONOMIC_EVALUATION`

P5.4 defines exactly three behavior maps over the frozen MARKET_STATE order:

```text
state order:
NORMAL_BULL
BTC_LEADERSHIP_MATURING
LATE_BULL_ROTATION
EXHAUSTION_WATCH
DE_RISK_1
DE_RISK_2
FLAT
```

Frozen multipliers:

```text
DE_RISK_ONLY     1.00  1.00  1.00  1.00  0.65  0.30  0.00
PROGRESSIVE      1.00  1.00  0.95  0.80  0.55  0.25  0.00
EARLY_DEFENSIVE  1.00  0.95  0.90  0.70  0.45  0.20  0.00
```

These values are fixed before P5.5 economics and are not a dense optimization grid.

### Composition

For each risky asset:

```text
P5.4 target weight
= frozen upstream P4.1/BRRK target weight
x cycle gross multiplier(MARKET_STATE)
```

Therefore P5.4:

- can only preserve/reduce upstream gross;
- cannot exceed gross multiplier `1.0`;
- cannot introduce >1 leverage;
- does not change relative BTC/ETH/SOL/BNB ranking;
- does not add shorts;
- sends freed risk budget to cash/stablecoin.

`DATA_INSUFFICIENT` has no P5.4 mapping. P5.5 matched evaluation starts on common P5.3 initialization date `2021-01-17`.

### Permission boundary

All candidate maps set `FLAT=0.0`, but MARKET_STATE recovery does not authorize live re-risk.

An actual zero-exposure implementation must remain `LOCKED_PENDING_HUMAN_APPROVAL` until explicit human approval.

P5.5 may compute post-FLAT positive targets only as `RESEARCH_HYPOTHETICAL_REENTRY` for historical economics; this has no production execution authority.

## P5.5 frozen handoff from P5.4

P5.5 candidate set is exactly:

```text
EARLY / BALANCED / CONSERVATIVE
x
DE_RISK_ONLY / PROGRESSIVE / EARLY_DEFENSIVE
=
9 joint candidates
```

A baseline without the cycle overlay is required.

P5.5 owns joint profile/map selection and must evaluate leave-one-event-out robustness, lead/lag, false-positive duration, missed upside, drawdown avoided, terminal wealth/CAGR, turnover/cost sensitivity, second-wind preservation, terminal 2021 behavior, non-top controls including the false FLAT, no single-event dependency and nearby-policy robustness.

If no candidate is robust, P5.5 must fail-stop.

## Frozen product boundaries

- BRRK-0011 relative ranking unchanged;
- BTC/ETH/SOL/BNB long universe unchanged;
- XRP feature-only;
- Hyperliquid primary venue;
- P4.1 defensive scale `[0,1]` unchanged;
- production gross `1.0`;
- actual zero-exposure -> risk-on remains human-gated;
- no automated withdrawals/external transfers;
- no production authorization.

## Exact next action

```text
RUN FRESH P5.4 PREREG CONTRACT CI / GOVERNANCE
VERIFY IMMUTABLE P5.3 V2 VALIDATOR
VERIFY NO P5.5 ECONOMIC RESULT EXISTS
IF GREEN, MERGE P5.4 PREREGISTRATION
CREATE FRESH P5.4 IMPLEMENTATION BRANCH
IMPLEMENT DETERMINISTIC STATE->GROSS MAPPING ONLY
DO NOT RUN P5.5 ECONOMICS UNTIL IMPLEMENTATION PARITY IS GREEN
DO NOT SELECT A WINNER IN P5.4
DO NOT PRODUCTION-AUTHORIZE ANYTHING
```
