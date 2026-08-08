# BRRK Next Steps

Last updated: 2026-08-08

## Current instruction

**P5.4 fixed behavior candidates are preregistered and the pure scalar mapping mechanics are implemented. Merge only after final-head CI, then freeze P5.5 validation/economic rules before computing any candidate return/cost result.**

## Immediate state

```text
Phase 0-3                              COMPLETE / MERGED
Phase 4 leverage research              FAIL_STOP
production gross cap                   1.0
production_authorized_components       []
P5.1 event taxonomy                    COMPLETE / FROZEN
P5.2 feature evidence                  COMPLETE / IMMUTABLE
P5.3 V1                               IMMUTABLE / ARCHITECTURE_FAIL
P5.3 V2                               IMMUTABLE EVIDENCE / ARCHITECTURE_PASS
P5.4 fixed candidates                  PREREGISTERED
P5.4 pure mapping mechanics            IMPLEMENTED / NO ECONOMIC SELECTION
P5.5 validation                        NEXT / CONTRACT FIRST
P5.6 integration                       NOT STARTED
Phase 6-8                              NOT STARTED
```

## P5.4 implementation boundary

The implementation performs only:

```text
cycle_adjusted_target(asset,t)
  = frozen_brrk_target(asset,t)
  * frozen_multiplier(market_state,t)
```

It cannot increase gross, cannot alter relative BTC/ETH/SOL/BNB ranking, cannot introduce shorts or XRP targets, and has no permission or production side effects. `FLAT` and `DATA_INSUFFICIENT` map to zero in the overlay candidates.

## P5.5 contract must freeze before economics

P5.5 must evaluate exactly 12 preregistered combinations:

```text
EARLY / BALANCED / CONSERVATIVE
x
HARD_ONLY / GENTLE / BALANCED / DEFENSIVE
```

plus the non-promotable `BRRK_NO_CYCLE_CONTROL` comparator.

Before any candidate economics, freeze:

- exact historical input/target source and digest;
- exact simulation timing convention;
- cost grid and turnover convention;
- metrics: terminal multiple, CAGR, MaxDD, Sharpe, Calmar, turnover;
- event-level lead/lag, false-positive duration, missed upside and avoided drawdown definitions;
- second-wind and non-top-control gates;
- leave-one-event-out or comparable event-held-out procedure;
- no-single-event-dependency rule;
- selection objective/tie-breaks;
- fail-stop rule if no robust combination exists.

Reuse established repository path/cost semantics where applicable; do not create a more favorable cycle-specific accounting convention.

## P5.6 and later

Only a P5.5-selected robust combination may be integrated. P5.6 controls total gross only. Phase 6 remains shadow/no signatures, Phase 7 actual capital launch remains explicit-human-approved, and Phase 8 first actual short remains human-gated.

## Exact next step

```text
FINAL-HEAD CI/GOVERNANCE FOR P5.4 IMPLEMENTATION
EXACT-HEAD MERGE
VERIFY NEW MAIN
PREREGISTER P5.5 VALIDATION + ECONOMIC SELECTION CONTRACT
ONLY THEN RUN P5.5 EVIDENCE ONCE
```
