# BRRK Current State

Last updated: 2026-08-10  
Handoff PR: **PENDING RESULT PR**  
Handoff branch: `research/brrk-winner-0001-runonce`  
Authoritative baseline main at branch creation: `da4bad159819b71c245ff5a6f9976edc7ab94dbc`  
Latest merged research PR at branch creation: **#150**

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
BRRK-WINNER-0001                  ONE-SHOT PASS / ROBUSTNESS STAGE ELIGIBLE
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

## BRRK-WINNER-0001 — one-shot development result

The preregistered 40/60 single-alt candidate executed exactly once in GitHub Actions run `31364706555` after canonical matched-P3.3 baseline reproduction passed. No nearby split was evaluated.

```text
canonical CAGR                         65.3057%
candidate CAGR                         69.6917%
CAGR delta                             +4.3860 pp
canonical max drawdown                 -33.5292%
candidate max drawdown                 -33.4499%
canonical Calmar                       1.9477
candidate Calmar                       2.0835
best-20 log-growth capture             103.5595%
turnover ratio                         1.1229x
single-alt decision rows changed       301 / 1333
all frozen hard gates                  PASS
result_status                          PASS_ROBUSTNESS_STAGE_ELIGIBLE
```

This is researcher-exposed DEVELOPMENT evidence only. It does not change canonical BRRK-0011, Phase 6, Phase 7, execution authority, leverage, shorts, signing or production authorization. A next robustness study requires a new preregistered research ID before any additional allocation variant is evaluated.

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

BRRK-WINNER-0001 development PASS changes none of these fields.

## Current drift assessment

`DRIFT_0`.

This branch records exactly one preregistered development run and its immutable PASS result. It does not modify `execution/**`, `research/results/**`, BRRK-0011 mathematics, Phase-6 collection or production authority.

## Exact next task

1. Merge this one-shot result only after governance/no-drift/P3.2/Phase-6 safety CI is green.
2. Do not evaluate any second BRRK-WINNER-0001 allocation split.
3. If the owner wants to continue this mechanism, preregister a new robustness research ID before any additional economics.
4. Continue Phase-6 future-only observation independently.
