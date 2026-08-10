# BRRK-BETA-HANDOFF-EVENT-STUDY-0047

Status: **PREREGISTERED_NOT_RUN / PREREGISTRATION-ONLY CANDIDATE**

This directory formalizes the exact design frozen in:

`research/governance/BRRK_BETA_HANDOFF_EVENT_STUDY_0047_DESIGN_FREEZE_2026-08-11.md`

The design boundary merged to `main` at:

`398b7ec3f78f602461787b1b45e8d5041729e126`

## Question

After the canonical BTC fast trend becomes positive, does researcher-exposed BTC/ETH/SOL history contain recurrent, duration-aware handoffs in which ETH or SOL becomes a unique durable relative leader?

0047 is **not** a portfolio optimization study. It does not answer how much to allocate after a handoff.

## Frozen anatomy

- universe: BTC / ETH / SOL only;
- BTC-positive episode: maximal contiguous common sessions with canonical `BTC_TREND_FAST >= 0`;
- exact V1 horizons: 20 / 60 / 120 / 240;
- exact V1 fast weights: 0.15 / 0.25 / 0.30 / 0.30;
- exact V1 slow weights: 0.10 / 0.20 / 0.30 / 0.40;
- causal ETH/BTC and SOL/BTC fast/slow relative trend;
- relative acceleration = fast minus slow;
- Beta breadth = share of ETH/SOL with absolute-fast > 0 and relative-fast > 0;
- trade participation = `log(1+trades)` minus trailing-60 median;
- raw state age since BTC-positive episode start;
- realized handoff target: same Beta asset uniquely beats BTC and the competing Beta at both +20 and +60 sessions, while BTC itself is positive on both horizons;
- unavailable +60 target is censored, not negative;
- only the earliest durable handoff is primary within an episode;
- cross-correlation lags -14..+14, episode-preserving;
- pooled episode-preserving VAR(7) with episode intercepts;
- all six directed Granger/Wald diagnostics;
- generalized BTC-shock IRFs at horizons 0..14;
- complete-episode bootstrap: 10,000 replicates, seed 470047;
- one-switch BTC→ETH/SOL oracle is hindsight opportunity bound only.

## Frozen Stage-1 gates

A later valid run can receive `PASS_DURATION_AWARE_HANDOFF_MODEL_STAGE_ELIGIBLE` only if:

1. at least 5 distinct target-eligible BTC-positive episodes exist;
2. at least 3 distinct episodes contain a primary durable handoff;
3. episode-level durable handoff prevalence is at least 0.50;
4. at least one ETH-cause episode exists;
5. at least one SOL-cause episode exists;
6. all labels/censoring/episode boundaries are mechanical with zero manual relabeling;
7. scientific definitions remain unchanged after any 0047 output;
8. BRRK, Phase 6 and all production/security authority remain unchanged.

PASS means only that the exposed history contains enough recurrent and cross-cause handoff structure to justify a **new separately preregistered duration-aware model study**. It does not prove predictability or CAGR improvement.

## Explicitly forbidden in 0047

- no 40/60, 20/80, 0/100 or other allocation test;
- no CAGR/Sharpe/Calmar/MDD optimization;
- no hazard/semi-Markov model fit under this ID;
- no HMM/classifier/boosting/neural-net candidate;
- no fixed N-day switch-delay search;
- no BOCPD rescue;
- no BNB/other-alt expansion after result;
- no alternate 20/60 target horizon after output review;
- no oracle-informed feature/label/model/allocation selection;
- no canonical BRRK, Phase-6, leverage, shorting, signing, order-submission or production change.

## Current lifecycle

```text
design boundary                      MERGED / 398b7ec3f78f602461787b1b45e8d5041729e126
formal preregistration               CANDIDATE ON PREREG BRANCH
PROGRAM_GOVERNED_V1                  TO BE REGISTERED IN SAME PR
dataset slice                        TO BE REGISTERED IN SAME PR / DEVELOPMENT EXPOSED
declared variants                    1
actual variants evaluated            0
runner                               NOT CREATED
historical result                    NONE
portfolio economics                  FORBIDDEN
production_authorized                false
signature_authorized                 false
order_submission_authorized          false
```

The only permitted next step after this preregistration is merged is a separate implementation-only branch that mechanically implements the frozen anatomy. No historical output may be released before the preregistration and implementation boundaries are both merged and green.