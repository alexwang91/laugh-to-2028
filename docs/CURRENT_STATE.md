# BRRK Current State

Last updated: 2026-08-10  
Handoff PR: **#150**  
Handoff branch: `research/brrk-winner-0001-prereg`  
Authoritative baseline main at branch creation: `405d2f75221ba97734973dd9bee2df04c9ecbcd2`  
Latest merged research PR at branch creation: **#149**

Status: **authoritative current-state handoff candidate**

## Executive state

```text
Phase 0-3                         COMPLETE / MERGED
Phase 4 leverage research         FAIL_STOP / NO_PROMOTION
P5.5                              COMPLETE / IMMUTABLE / NO_PROMOTION / FAIL_STOP
F27 idle-cash measurement         R2 AUTHORITATIVE / R1 SUPERSEDED-PRESERVED
F7 metrics convergence            PARTIAL
Phase 6 ARM                       ACTIVE FUTURE-ONLY OBSERVATION
Phase 6 ARM marker                cbd58adb05187651ca72d67900a0ccbbd3e83b1e
Phase 6 daily schedule            00:00 UTC
Phase 6 live elapsed evidence     MEASUREMENT_INCONCLUSIVE_TIME_DEPENDENT
BRRK opportunity-cost audit 0042  COMPLETE DIAGNOSTIC / NO PROMOTION AUTHORITY
BRRK-WINNER-0001                  PREREGISTERED_NOT_RUN / FORMAL PATH CREATED
Program timeline dashboard        READ-ONLY V5 / PROFESSIONAL FUND TERMINAL
Phase 7                           MONITOR_ONLY / LAUNCH BLOCKED
Phase 8                           TRIGGER ABSENT / NOT RUN
Production                        NO_CHANGE
```

## Phase 6 remains frozen and independent

The canonical BRRK-0011 strategy remains unchanged while future-only Phase-6 observation continues. Genuine scheduled credit still requires a real `schedule` event plus create-only evidence and a separate hash-bound receipt. Pull-request runs, reruns, replay and manual dispatch do not create scheduled-decision credit.

Frozen acceptance remains:

```text
minimum elapsed calendar days       14
minimum genuine scheduled decisions 10
minimum emergency drills             1
critical reconciliation errors       0
unexplained target drift              0
schedule failures                     0
production_authorized              false
signature_authorized               false
order_submission_authorized        false
```

## BRRK Opportunity-Cost Audit 0042 — merged

PR #149 merged deterministic diagnostic audit at:

```text
405d2f75221ba97734973dd9bee2df04c9ecbcd2
```

Frozen diagnostic results from CI:

```text
V1 CAGR                              61.3150%
BRRK CAGR                            65.1702%
BRRK minus V1 CAGR                   +3.8551 pp
V1 max drawdown                      -37.6349%
BRRK max drawdown                    -33.7151%
BRRK MDD improvement                 +3.9198 pp
BRRK top-20 V1 growth-day capture    ~100%
alt-active days                      590
BTC >= 50% of gross on alt-active    70.1695%
V1 target-change median gap          2 days
BRRK target-change median gap        2 days
BRRK maximum target-change gap       120 days
```

Interpretation frozen for follow-up: the defensive scaler is not the first optimization target because it improved both historical CAGR and MDD while preserving V1 top-growth days. The strongest observable rigidity is portfolio construction: BTC remains at least half of gross on about 70% of alt-active days. Historical P3.2 signal-speed causality and P3.3 5% execution-band return attribution remain unavailable from frozen PIT-DISP-0015 artifacts.

The older non-promotable signal-attribution audit also established that canonical BRRK is right-tail dependent: the canonical best 20 sessions account for about 91.61% of total log growth. Any follow-up must explicitly preserve right-tail participation.

## BRRK-WINNER-0001 — formal preregistration assembled

`BRRK-WINNER-0001` is now present in `config/research_registry.json` as `PROGRAM_GOVERNED_V1`, with `actual_variants_evaluated=0`, `result_status=PREREGISTERED_NOT_RUN`, and production authorization false. The governed path now exists at:

```text
research/brrk_winner_0001/
```

No economic runner, modified NAV, candidate return, pass/fail result or promotion decision exists on this preregistration branch.

The single frozen candidate is:

```text
canonical single-alt branch: BTC 50% / sole eligible alt 50%
candidate single-alt branch: BTC 40% / sole eligible alt 60%
all signals                          UNCHANGED
multi-alt allocation                 UNCHANGED
defensive scale                      UNCHANGED
P3.3 simulator / 5 bps cost          UNCHANGED
universe                             BTC / ETH / SOL / BNB
gross cap                            <= 1.0
leverage / shorts                    NONE
```

Frozen hard success gates before any candidate economics are run:

```text
after-cost CAGR delta                 >= +3.00 pp vs canonical BRRK
max drawdown deterioration            <= 4.00 pp
Calmar                                >= canonical BRRK
canonical best-20 log-growth capture  >= 98%
turnover                              <= 1.25x canonical BRRK
long-only gross                       <= 1.0 every day
```

Any hard-gate failure means `FAIL_NO_PROMOTION` for this research ID. No same-ID rescue split such as 45/55, 35/65 or 30/70 is allowed after results are observed.

Formal frozen files:

```text
config/research_registry.json
config/dataset_exposure_registry.json
research/governance/BRRK_WINNER_0001_PREREG_DRAFT.json
research/brrk_winner_0001/README.md
research/brrk_winner_0001/PREREGISTRATION.json
```

The development dataset `BRRK-WINNER-0001-CANONICAL-HIST-V1` is explicitly `DEVELOPMENT / RESEARCHER_EXPOSED_HISTORY`; no sealed or unbiased OOS claim is made.

## Dashboard V5

Public read-only dashboard remains:

```text
https://laugh-to-2028.vercel.app/
```

## Canonical production / security authority

```text
directional core                  BRRK-0011
long universe                     BTC / ETH / SOL / BNB
XRP                               feature-only
primary venue                     Hyperliquid
decision boundary                 00:00 UTC
production gross cap              1.0
production_authorized_components = []
production_authorized             false
signature_authorized             false
order_submission_authorized      false
first real short authority        NONE
```

BRRK-WINNER-0001 preregistration changes none of these fields.

## Current drift assessment

`DRIFT_0`.

This branch freezes one research hypothesis, one variant and its dataset-exposure contract before any candidate economics are evaluated. It does not modify `execution/**`, `research/results/**`, BRRK-0011 mathematics, Phase-6 collection, immutable economic evidence or production authority.

## Exact next task

1. Require final PR #150 governance/no-drift/P3.2/Phase-6 safety CI to pass with the registered research ID and formal governed path.
2. Merge PR #150 only if the final diff remains preregistration/config/docs/tests only and no candidate economics are present.
3. After merge, create a separate result-bearing branch from the merged preregistration baseline.
4. Execute the one frozen 40/60 candidate exactly once, first requiring canonical baseline reproduction before candidate metrics are released.
5. Apply the frozen hard gates without retuning or rescue variants.
6. Continue Phase-6 future-only evidence accumulation independently.
