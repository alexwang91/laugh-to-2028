# BRRK Next Steps

Last updated: 2026-08-07

## Current instruction

**P5.1 taxonomy and P5.2 feature evidence are now frozen and reviewable. The next task is P5.3 State Model: preregister a multi-state cycle-risk structure using the immutable evidence, without moving P5.1 events, retuning P5.2 features, or fitting a one-indicator top switch.**

## Immediate state

```text
Phase 0-3                              COMPLETE / MERGED
LEVERAGE-0039                          STOPPED PRE-RUN / NO RESULT
LEVERAGE-0040                          COMPLETE / IMMUTABLE / NO_PROMOTION
LEVERAGE-0041                          COMPLETE / IMMUTABLE / NO_PROMOTION
P4.6 production leverage               NOT ENTERED / BLOCKED BY NO CANDIDATE
production gross cap                   1.0
production_authorized_components       []
P5.1 event taxonomy                    COMPLETE / MERGED / FROZEN
P5.2 feature evidence                  COMPLETE / IMMUTABLE / DESCRIPTIVE CLOSEOUT
P5.2 summary SHA256                    3f6dc3c512d22ac8f71d43ed155f2602cd40d5caf3d617c0e130e170727e0627
P5.3 state model                       NEXT
```

## P5.1 — immutable event taxonomy

Contract: `P5.1-EVENT-TAXONOMY-V1`.

P5.1 freezes the required 2021/2025 events, mechanical anchors, relative evaluation buckets and four high-volatility non-top controls. Only 2021 November is explicitly terminal in V1.

P5.3 may not move P5.1 windows/anchors after seeing P5.2 evidence.

## P5.2 — completed immutable feature evidence

Contract: `P5.2-FEATURE-FAMILIES-V1`.

Result commit:

`61d585afb64afbe3ead6422e7e62cde6c59fad40`

Summary SHA256:

`3f6dc3c512d22ac8f71d43ed155f2602cd40d5caf3d617c0e130e170727e0627`

Result meaning:

```text
29 AVAILABLE_V1 features      coverage PASS
6 requested data features     DATA_SOURCE_PENDING
feature set selected          NO
state thresholds selected     NO
production authorized         NO
```

Formal interpretation is recorded in `docs/P5_2_FEATURE_EVIDENCE_CLOSEOUT.md` and derived diagnostics under `research/analysis/p5_2_closeout/`.

### Evidence constraints carried into P5.3

#### A. Volatility = regime context, not a top switch

RV20 and RV20/RV60 separate many event contexts from high-vol controls, but the same broad pattern occurs in terminal, second-wind, nonterminal-toplike and deterioration groups.

P5.3 may use volatility to describe market texture/maturity; it must not encode low/contracting volatility alone as terminal risk.

#### B. ETH/BTC leadership requires `LATE_BULL_ROTATION`

ETH/BTC relative strength is strong near terminal, second-wind and nonterminal-toplike events. Therefore loss of BTC leadership / stronger ETH cannot automatically imply de-risk.

P5.3 must preserve a distinct state in which relative alt leadership is allowed while total cycle risk is still managed separately.

#### C. Divergence is a terminal-hazard hypothesis, not a validated terminal rule

The strongest target-lead separator for the sole 2021 terminal event is 20d price-versus-RSI rank divergence. Because P5.1 V1 has only one terminal event, P5.3 cannot fit a special threshold to that case and claim cross-cycle robustness.

#### D. Breadth trajectory matters more than a single breadth level

Breadth acceleration is elevated in terminal and other late-bull/nonterminal structures. Its transition pattern may help state classification, but it is not an exit switch by itself.

#### E. Raw RSI is insufficient

Daily/4h RSI levels are not uniquely terminal. 4h RSI is especially active in the late-2025 deterioration context. Treat RSI as exhaustion/failure evidence combined with other families.

#### F. Some discrete features need categorical treatment

Control MAD can be zero for discrete breadth/consolidation features. Undefined robust-z does not imply uselessness. Any P5.3 treatment must be preregistered rather than chosen after looking at preferred outcomes.

## P5.3 State Model — NEXT

Target vocabulary:

```text
NORMAL_BULL
BTC_LEADERSHIP_MATURING
LATE_BULL_ROTATION
EXHAUSTION_WATCH
DE_RISK_1
DE_RISK_2
FLAT
```

### P5.3 first step: preregister structure before thresholds

Before fitting numerical boundaries, freeze:

1. state semantics;
2. allowed feature families per state transition;
3. transition direction / hysteresis rules;
4. missing-data behavior;
5. how unavailable P5.2 data families remain excluded/pending;
6. state persistence / anti-churn rules;
7. which transitions can reduce gross automatically;
8. which transitions require explicit human approval to re-add risk;
9. fitting/validation split and event-level anti-overfit discipline.

### Recommended structural evidence groups

These are design inputs, **not promoted features or fixed thresholds**:

```text
REGIME_TEXTURE
  BTC RV20
  BTC RV20/RV60
  distance from trailing high

LEADERSHIP_ROTATION
  ETH/BTC 20d / 40d relative strength
  secondary BNB/SOL relative context
  canonical breadth trajectory

EXHAUSTION_TRANSITION
  price-vs-RSI rank divergence
  RSI failure / daily-vs-4h structure
  breadth acceleration / contraction

TREND_CONTEXT
  KAMA gap / selected trend-level context
  raw returns/slopes only as secondary evidence unless validation supports more
```

### Required behavior semantics

- `NORMAL_BULL`: normal BRRK directional risk subject to existing defensive layer;
- `BTC_LEADERSHIP_MATURING`: BTC structure mature/late but rotation evidence not yet sufficient for a bearish interpretation;
- `LATE_BULL_ROTATION`: ETH/alt leadership may strengthen; relative BRRK ranking remains untouched; total gross may be managed by cycle risk but rotation itself is not a bearish trigger;
- `EXHAUSTION_WATCH`: multiple-family exhaustion/deterioration evidence is accumulating;
- `DE_RISK_1`: moderate total-risk reduction;
- `DE_RISK_2`: stronger total-risk reduction;
- `FLAT`: zero directional exposure.

P5.3 should define state classification/transition evidence only. Exact gross multipliers belong to governed P5.4 behavior unless the roadmap contract explicitly couples a minimal research mapping for validation.

## P5.4 — after P5.3

Define how state changes total directional risk while preserving BRRK relative ranking.

Core rule:

```text
BRRK        = which assets / relative weights
Cycle layer = how much total directional risk
Router      = which instruments implement it
Execution   = how to reach actual target safely
```

Rotation is not automatically bearish. As hazard rises, total gross may fall; hard multi-family deterioration may eventually force FLAT.

## P5.5 validation

Use event-level / leave-one-event-out or comparable anti-overfit validation where feasible.

Required reporting:

- lead/lag distribution;
- false-positive duration;
- missed upside before exit;
- drawdown avoided;
- terminal wealth impact;
- second-wind behavior;
- state churn / persistence;
- behavior when the sole explicit terminal event is held out.

A rule that only works after tuning specifically to 2021 November or one 2025 phase fails robustness.

## P5.6 integration

Integrate the accepted cycle state layer above BRRK, without rewriting BRRK ranking or existing execution/routing truth.

## Downstream

- Phase 6 integrated live-data shadow with zero trading authority;
- Phase 7 limited-capital live only after Phase 6 acceptance + explicit production approval;
- Phase 8 bear-short research later; first short remains human-gated.

## Frozen boundaries while P5.3 proceeds

- BRRK-0011 remains canonical directional core;
- BTC/ETH/SOL/BNB remain long target universe;
- XRP remains feature-only;
- Hyperliquid remains primary venue;
- P4.1 defensive scale remains `[0,1]`;
- production gross remains `1.0`;
- LEVERAGE-0040/0041 remain immutable failed studies;
- P5.1 taxonomy remains immutable;
- P5.2 immutable result remains immutable and non-authorizing;
- BTC dominance, broad-market breadth, comparable funding, OI, basis and liquidation remain `DATA_SOURCE_PENDING` until separately validated;
- no automated withdrawals/external transfers;
- no production authorization.

## Exact next step

```text
MERGE P5.2 CLOSEOUT ONLY AFTER FRESH FINAL-HEAD CI/GOVERNANCE
VERIFY NEW MAIN
CREATE FRESH P5.3 BRANCH FROM NEW MAIN
PREREGISTER P5.3 MULTI-STATE STRUCTURE BEFORE NUMERICAL THRESHOLD FITTING
PRESERVE P5.1 + P5.2 IMMUTABLE EVIDENCE
DO NOT TURN ETH/BTC ROTATION OR RSI ALONE INTO AN EXIT SWITCH
DO NOT START P5.4/P5.5 IMPLEMENTATION UNTIL P5.3 STRUCTURE IS REVIEWABLE
```
