# BRRK Current State

Last updated: 2026-08-10  
Handoff PR: **#153**  
Handoff branch: `research/brrk-winner-robustness-0002-runonce`  
Authoritative baseline main at branch creation: `11c7967e4d22766b3abee33d382ab2912c16f5cb`  
Latest merged research PR at branch creation: **#152**

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
BRRK-WINNER-ROBUSTNESS-0002       RUN INTERFACE FROZEN / NOT RUN
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

## BRRK-WINNER-0001 — merged one-shot development result

PR #151 merged the preregistered 40/60 single-alt candidate after it executed exactly once in GitHub Actions run `31364706555` and canonical matched-P3.3 baseline reproduction passed. No nearby split was evaluated.

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

This is researcher-exposed DEVELOPMENT evidence only. It does not change canonical BRRK-0011, Phase 6, Phase 7, execution authority, leverage, shorts, signing or production authorization. `BRRK-WINNER-0001` is closed and must not run again.

## BRRK-WINNER-ROBUSTNESS-0002 — prereg merged, run interface frozen

PR #152 merged the result-informed robustness preregistration at `11c7967e4d22766b3abee33d382ab2912c16f5cb`. PR #153 now freezes the run interface and runner before the single permitted robustness execution. `RUN_ONCE.marker` does not yet exist, so no robustness economics have been executed on this branch.

Frozen reproduction gate:

```text
source result                         BRRK-WINNER-0001 PRIMARY_RESULT
primary cost                          5 bps
absolute reproduction tolerance       5e-10
metric payload reproduction           canonical + candidate
exact target-frame hash reproduction  canonical + candidate
robustness metrics before reproduction FORBIDDEN
```

Frozen temporal panel at 5 bps:

```text
T1  2022-12-10 .. 2024-02-26   444 sessions
T2  2024-02-27 .. 2025-05-15   444 sessions
T3  2025-05-16 .. 2026-08-02   444 sessions
```

Implementation semantics are now frozen before results: simulate one continuous full-horizon 5 bps P3.3 path, preserve economic position continuity across all dates, then slice realized session returns into the three blocks. Each block renormalizes its sliced NAV to 1 only for subperiod CAGR and drawdown calculation. There is no boundary position reset and no artificial boundary rebalance.

Frozen transaction-cost stress panel on the complete 1,332-session horizon:

```text
10 bps
20 bps
```

Each cost stress replays the identical full canonical and 40/60 target paths from the normal initial zero position with only `cost_bps` changed. The P3.3 5% L1 band, fill fraction, transaction-cost multiplier, target authority and funding semantics remain unchanged.

The runner imports the already-closed `BRRK-WINNER-0001` 40/60 candidate constructor. It does not contain a second allocation search or alternative split implementation. No 45/55, 35/65, 30/70 or other rescue split is permitted.

A robustness PASS still requires the preregistered temporal, cost-stress, drawdown, Calmar, right-tail, turnover and authority gates. Even a full PASS only makes a new separately preregistered future-only validation stage eligible. It does not promote 40/60 into canonical BRRK and does not create production authority.

The study reuses `BRRK-WINNER-0001-CANONICAL-HIST-V1`, which is already consumed and researcher-exposed DEVELOPMENT history. Therefore BRRK-WINNER-ROBUSTNESS-0002 cannot claim independent OOS evidence or temporal novelty.

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

Neither BRRK-WINNER-0001 development PASS nor BRRK-WINNER-ROBUSTNESS-0002 preregistration/run interface changes any of these fields.

## Current drift assessment

`DRIFT_0`.

This branch adds the frozen BRRK-WINNER-ROBUSTNESS-0002 run interface, research-only runner, permanent interface tests and a temporary marker-triggered GitHub Actions workflow. It does not modify `execution/**`, `research/results/**`, BRRK-0011 mathematics, Phase-6 collection or production authority. The marker is absent and robustness economics remain unexecuted.

## Exact next task

1. Require PR #153 governance/no-drift/P3.2/Phase-6 safety/baseline CI to pass against the frozen interface and runner without executing economics.
2. Only after those checks pass, add exactly one `research/brrk_winner_robustness_0002/RUN_ONCE.marker` commit to trigger the one permitted robustness run.
3. Reproduction must pass before any robustness result artifact is written. A reproduction failure stops the ID; a proven workflow-startup failure before economics begin may be classified separately from a variant evaluation.
4. After the single valid run, preserve its immutable artifact, register evidence/result status, remove the temporary workflow, close the research ID and rerun all governance checks.
5. Continue Phase-6 future-only observation independently. A robustness PASS can only make a separately preregistered future-only validation stage eligible.
