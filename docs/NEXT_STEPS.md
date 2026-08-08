# BRRK Next Steps

Last updated: 2026-08-08

## Current instruction

**P5.3 V2 architecture evidence passed with exact V1 signal parity and without hiding the 2021 false FLAT. Close/merge V2, then preregister P5.4 fixed state-to-gross-risk behavior candidates. P5.4 defines candidates only; P5.5 owns joint profile/mapping robustness and economic selection.**

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
P5.3 V2 result commit                  e732b7ebe570236bf43084caecb6ea15f7edecb8
P5.3 V2 summary SHA256                 05d5d68a59c8b13f1122d98ed75d03934defdc9d73c7dd92e038c92fd97d2e52
P5.3 selected profile                  NONE
P5.4 behavior mapping                  NEXT / PREREGISTER FIXED CANDIDATES
P5.5 validation                        NOT STARTED
P5.6 integration                       NOT STARTED
```

## P5.3 V2 result interpretation

V2 is an **architecture pass only**:

- V1 normalization parity = exact;
- V1 evidence-atom parity = exact;
- V1 raw-candidate parity = exact;
- V1 final-state parity through first FLAT = exact;
- false raw FLAT on `2021-02-23` remains visible;
- MARKET_STATE later recovers and frozen later events remain observable;
- MARKET_STATE has no permission-unlock authority.

The false-FLAT episode lasted 6 days for EARLY/BALANCED and 8 days for CONSERVATIVE. It remains negative signal-quality evidence and must be charged in P5.5.

## P5.4 fixed-candidate requirements

P5.4 may now define a small, preregistered candidate family mapping the seven MARKET_STATE values to **total gross-risk multipliers**.

Hard structural rules:

- all multipliers in `[0,1]`; Phase 4 authorized no >1 leverage;
- `NORMAL_BULL = 1.0` for every mapping;
- mappings must be monotone non-increasing with market-state severity;
- `FLAT = 0.0` for mappings that use FLAT as actual zero exposure;
- `LATE_BULL_ROTATION` must not automatically be treated as bearish/zero;
- behavior layer scales total BRRK gross only;
- BRRK-0011 relative BTC/ETH/SOL/BNB ranking is unchanged;
- P4.1 defensive scale remains upstream and unchanged;
- no P5.4 winner is selected in P5.4;
- no market-state improvement automatically clears operational risk permission after an implemented zero exposure.

P5.4 candidates must be few enough to avoid an implicit grid-search/overfit rescue. Numerical candidate values must be frozen before P5.5 economic/event evaluation.

## P5.5 validation ownership

P5.5 must evaluate the Cartesian candidate set of:

```text
P5.3 profiles  EARLY / BALANCED / CONSERVATIVE
x
P5.4 fixed behavior maps
```

Required validation dimensions:

- leave-one-event-out or comparable event-held-out analysis;
- 7–14 day target lead behavior without forcing every event to fit;
- false-positive duration;
- missed upside;
- drawdown avoided;
- terminal wealth / CAGR impact;
- turnover and explicit cost sensitivity;
- second-wind preservation;
- terminal 2021 bear-transition behavior;
- non-top-control behavior including the 2021 false FLAT;
- no single-event dependency;
- broad-region/nearby-policy robustness rather than a knife-edge winner.

If no candidate is robust, P5.5 must fail-stop rather than force a selection.

## P5.6 integration boundary

Only a P5.5-selected and accepted profile/mapping may enter P5.6. P5.6 may control total gross exposure; it must not change BRRK relative asset ranking or authorize >1 leverage.

## Later roadmap

After P5.6 integration:

```text
Phase 6  integrated shadow / no signatures / no trading
Phase 7  limited-live readiness; actual real-money launch still requires explicit human approval
Phase 8  bear-short research; first real short remains human-gated
then     full Phase 0-8 drift audit / review / corrective PRs
```

## Frozen product boundaries

- BTC/ETH/SOL/BNB long universe unchanged;
- XRP feature-only;
- Hyperliquid primary venue;
- production gross cap `1.0`;
- `production_authorized_components = []`;
- actual zero-exposure -> risk-on remains human-gated;
- no withdrawal/external-transfer automation;
- no production authorization.

## Exact next step

```text
FINAL-HEAD CI / GOVERNANCE FOR P5.3 V2 RESULT
EXACT-HEAD MERGE P5.3 V2
VERIFY NEW MAIN
CREATE P5.4 PREREG BRANCH
FREEZE A SMALL FIXED STATE->GROSS CANDIDATE FAMILY
IMPLEMENT MAPPING TESTS ONLY AFTER PREREG
DO NOT SELECT A WINNER UNTIL P5.5
DO NOT PRODUCTION-AUTHORIZE ANYTHING
```
