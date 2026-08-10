# BRRK Current State

Last updated: 2026-08-10
Handoff PR: **#159**
Handoff branch: `research/brrk-exhaustion-trigger-0045-runonce`
Authoritative baseline main at branch creation: `c48577bb95c9fc78e5d0d78b86f30905b3636503`
Latest merged research PR at branch creation: **#158**

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
BRRK-WINNER-0001                  ONE-SHOT PASS / CLOSED
BRRK-WINNER-ROBUSTNESS-0002       ONE-SHOT PASS / FUTURE-ONLY VALIDATION ELIGIBLE / CLOSED
BRRK exhaustion event study 0043 COMPLETE DIAGNOSTIC / 7-14D SIGNAL FEASIBLE / TRIGGER NOT READY
BRRK exhaustion state 0044       PASS / TRIGGER STAGE ELIGIBLE / CLOSED
BRRK exhaustion trigger 0045     FAIL / NO DYNAMIC-GROSS ELIGIBILITY / CLOSED
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

PR #149 merged deterministic diagnostic audit at `405d2f75221ba97734973dd9bee2df04c9ecbcd2`.

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

Interpretation remains frozen: the defensive scaler is not the first optimization target because it improved both historical CAGR and MDD while preserving V1 top-growth days. The strongest observable rigidity is portfolio construction: BTC remains at least half of gross on about 70% of alt-active days.

## BRRK-WINNER-0001 — closed development PASS

PR #151 merged the exactly-once 40/60 single-alt development candidate. It remains researcher-exposed DEVELOPMENT evidence and must not run again.

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
all frozen hard gates                  PASS
result_status                          PASS_ROBUSTNESS_STAGE_ELIGIBLE
```

No canonical BRRK, Phase 6 or production authority changed.

## BRRK-WINNER-ROBUSTNESS-0002 — closed robustness PASS

PR #152 merged the preregistration. PR #153 executed the frozen robustness panel exactly once after the pre-result green baseline `561ecee69d30253aa398caf51d589cb03b5cfe47`. The unique economic run was GitHub Actions `31374176442`, attempt 1, from trigger SHA `346e26e3906df2416a21a40223e8791c3dfef86a`.

Evidence binding:

```text
artifact id                        9057294415
artifact digest                    sha256:8eb08d0080fae185953ae50a15b05bc9994d6c06da33761bd2125dc89037313c
PRIMARY_RESULT SHA256              cf149308df5aea1a0cc1315432a7effd0e163cda21e6df0b8f39cf0b6ce6fdf0
baseline reproduced before release true
actual variants evaluated          1
retuning performed                 false
```

Frozen 5 bps primary reproduction remained unchanged:

```text
canonical CAGR                     65.3057%
candidate CAGR                     69.6917%
canonical MDD                      -33.5292%
candidate MDD                      -33.4499%
canonical Calmar                   1.9477
candidate Calmar                   2.0835
right-tail capture                 103.5595%
turnover ratio                     1.1229x
```

Temporal robustness at 5 bps:

```text
T1  candidate CAGR delta  +22.5832 pp   PASS
    MDD deterioration       1.7459 pp   PASS
T2  candidate CAGR delta   -1.7365 pp   NEGATIVE EVIDENCE / CAGR GATE FAIL
    MDD deterioration       0.0000 pp   PASS
T3  candidate CAGR delta   +2.3255 pp   PASS
    MDD deterioration      ~0.0000 pp   PASS
aggregate CAGR gate         2 / 3       PASS
```

T2 is retained as negative evidence. It may not be removed, relabeled or used to justify same-ID rescue tuning.

Transaction-cost robustness on the full 1,332-session path:

```text
10 bps  canonical CAGR 63.2574%   candidate 67.3311%   +4.0737 pp
        canonical Calmar 1.8583   candidate 1.9805     PASS
20 bps  canonical CAGR 59.2440%   candidate 62.7142%   +3.4702 pp
        canonical Calmar 1.6910   candidate 1.7888     PASS
        MDD deterioration 0.0244 pp                         PASS
```

All preregistered temporal aggregate, drawdown, 10/20 bps CAGR/Calmar, right-tail, turnover, long-only and gross-cap gates passed. Final classification:

```text
PASS_FUTURE_ONLY_VALIDATION_STAGE_ELIGIBLE
```

This result is still result-informed, researcher-exposed DEVELOPMENT robustness evidence. It is not independent OOS evidence and does not create temporal novelty.

`RUN_ONCE.marker` is permanent. `BRRK-WINNER-ROBUSTNESS-0002` is closed and may not run again. No 45/55, 35/65, 30/70 or other rescue split, alternative temporal partition, transaction-cost grid or hard-gate change is permitted under this ID.

## BRRK-EXHAUSTION-EVENT-STUDY-0043 — complete diagnostic

PR #155 is a read-only DEVELOPMENT diagnostic created after merged PR #153. It mechanically separates genuine local exhaustion tops from ordinary pullbacks / continuation false tops and measures causal 7–14 day deterioration signals. User-provided dates are sanity checks only and do not define labels, thresholds, or score weights.

Unique execution and evidence binding:

```text
workflow run                         31381953131 / attempt 1
artifact id                          9060216534
artifact digest                      sha256:6df40bbe0112082f045cd4da7b461753382c6980a348609a35bed9967f1520c4
full result SHA256                   1ca030e544d6e3391143c9ec47e202f9585ce8a846e0e46be583c31258958b43
source summary SHA256                82579688952e990809a01044378b40cd44ceba84142307686cfa8ae05158c278
historical sessions                  1332
mechanically detected peak candidates 16
portfolio economics executed         false
```

Primary `-15%` competing-barrier panel:

```text
TRUE_EXHAUSTION / CONTINUATION / AMBIGUOUS     9 / 6 / 1
PRE14_7 total EXHAUSTION_SCORE AUC             0.7333
PRE14_7 F7 BRRK disagreement AUC               0.7556
PRE14_7 F4 volatility/downside AUC             0.7111
PRE14_7 F1 momentum decay AUC                  0.6889
PRE14_7 F2 price structure AUC                 0.6889
PRE7_0 F4 volatility/downside AUC              0.8444
PRE7_0 F7 BRRK disagreement AUC                0.8222
```

Severe `-20%` panel strengthens the one-to-two-week signal:

```text
TRUE_EXHAUSTION / CONTINUATION / AMBIGUOUS     7 / 6 / 3
PRE14_7 total EXHAUSTION_SCORE AUC             0.8571
PRE14_7 F7 BRRK disagreement AUC               0.8000
PRE14_7 F2 price structure AUC                 0.7714
PRE14_7 F4 volatility/downside AUC             0.7714
```

Important negative evidence remains binding: the frozen equal-weight absolute threshold is too insensitive. The 80th-percentile / 3-day rule catches only `2/9` primary true events, although it produces `0/6` continuation false triggers; those two hits lead by 10 and 21 days. No threshold is selected or rescued under ID 0043.

The 48 oriented raw features collapse to about `7.2046` effective dimensions; 14 pairs have `|corr| >= 0.85`, including one exact duplicate between F1 and F7. Future work must deduplicate rather than count technical indicators as independent votes.

Anchor sanity checks remain result-neutral: 2023-12-25 and 2024-03-31 are mechanically TRUE_EXHAUSTION; the January-2025 region maps to 2025-01-18 TRUE_EXHAUSTION; the October-2025 region maps to the nearby higher 2025-10-08 TRUE_EXHAUSTION. The 2024-11-24 region maps to 2024-11-22 and is AMBIGUOUS under the primary `-15% / 60-session` rule (`-11.77%` minimum), but TRUE_EXHAUSTION in the frozen `-10%` panel. The taxonomy is not altered to force the anchor to pass.

Interpretation: a 7–14 day exhaustion-ranking signal appears feasible, especially for severe drawdowns, but the first equal-weight absolute trigger is not operationally ready. ID 0043 is closed against result-informed pruning, reweighting, threshold rescue, dynamic-gross mapping, or portfolio-economic counterfactual. Any continuation requires a new research ID with deduplicated state dimensions and episode/block-aware validation.

Canonical BRRK-0011, Phase 6 and all production/security authority remain unchanged.

## BRRK-EXHAUSTION-STATE-0044 — PASS, closed

PR #156 froze 0044 before result release. PR #157 implemented the frozen runner and released exactly one valid result after a fully green pre-result baseline. The historical evidence remains researcher-exposed DEVELOPMENT evidence, not independent OOS.

Execution binding:

```text
pre-result green SHA                 f6fd1fc3425fefdc6bd024fa032a065accab7c6e
pre-result failed workflow run       31387906469 / NO DIAGNOSTIC / NO RESULT
unique valid result workflow run     31388103016 / run number 2 / attempt 1
trigger head SHA                     9affc7572dd0feefb14fe41e2aea7904c3a132ba
artifact id                          9062525981
artifact digest                      sha256:b109b610710b00904c924680a63305579f3f3c4c799d539906e0853629ddd378
full result SHA256                   687ff49d8db8baf54a1cfafcf8863c848011800b6c74689ab0534796ac86ff29
source taxonomy reproduction         MATCHED 0043 EXACTLY
```

Frozen CORE4 gate result:

```text
usable macro episodes                         7   PASS
TRUE / CONTINUATION episode coverage        5 / 4 PASS
15% PRE14_7 cross-episode AUC              0.750 PASS
15% PRE14_7 event AUC                      0.778 PASS
20% PRE14_7 cross-episode AUC              0.750 PASS
LOEO minimum / median AUC                  0.654 / 0.739 PASS
result_status                              PASS_TRIGGER_STAGE_ELIGIBLE
```

Result-informed component evidence is preserved without same-ID reweighting. S2 trend disagreement was strongest (`0.744` cross-episode AUC at PRE14_7, `0.893` at PRE7_0, `0.833` for severe PRE14_7). Secondary S5 volume confirmation was negative evidence: adding it reduced CORE4 cross-episode AUC from `0.750` to `0.676` at PRE14_7 and from `0.736` to `0.606` at PRE7_0; S5 alone was `0.500` at primary PRE14_7.

0044 therefore establishes that a frozen low-dimensional exhaustion state retains useful advance discrimination after macro-episode dependence control. It **does not** define a trading trigger or gross-risk response. `RUN_ONCE.marker` is permanent and 0044 may not be rerun, reweighted, pruned, rescued or used for same-ID threshold/gross search.

The only authorized research continuation is a new, separately preregistered trigger-stage ID. Canonical BRRK-0011, the 40/60 winner lineage, Phase 6 and all production/security authority remain unchanged.

## BRRK-EXHAUSTION-TRIGGER-0045 — FAIL, closed

PR #158 froze one trigger candidate before any result. PR #159 implemented it and released exactly one valid result after a fully green pre-result baseline. The historical evidence remains researcher-exposed DEVELOPMENT evidence, not independent OOS.

Execution binding:

```text
pre-result green SHA                 669942a4bef3f32894f616b9b28e5001d81e82b9
pre-result failed workflow run       31390711467 / NO DIAGNOSTIC / NO RESULT
unique valid result workflow run     31391109057 / run number 2 / attempt 1
trigger head SHA                     f9d4fba80bd07b8a5c67c5c3928f9081332809c7
artifact id                          9063704951
artifact digest                      sha256:0f8cd31ca3905d798194387622456fc8e59cb786376e57a6c135bdb2867c9c04
full result SHA256                   06714848cbb8c812a655700c29362487fc9e77ef2638f57547c7340ee10a2682
source taxonomy reproduction         MATCHED 0043 EXACTLY
parent 0044                          PASS_TRIGGER_STAGE_ELIGIBLE
```

Frozen trigger result:

```text
primary TRUE PRE14_7 WATCH/RISK            3 / 9 = 33.3% FAIL
primary CONT PRE14_0 false WATCH/RISK       0 / 6 = 0.0%  PASS
primary TRUE episode hit                    2 / 5 = 40.0% FAIL
primary CONT episode false                  0 / 5 = 0.0%  PASS
severe TRUE PRE14_7 WATCH/RISK              3 / 7 = 42.9% FAIL
severe TRUE PRE7_POST3 RISK                 2 / 7 = 28.6% FAIL
primary CONT PRE14_POST3 RISK               0 / 6 = 0.0%  PASS
qualifying TRUE PRE21_0 transition onsets             0    FAIL
premature-clear gate                         no denominator FAIL
result_status                       FAIL_NO_DYNAMIC_GROSS_STAGE_ELIGIBILITY
```

The candidate is specific but too insensitive and too persistent for the requested one-to-two-week action trigger. WATCH plus RISK occupies about `34.38%` of the 1,332-session history, while non-HEALTHY states occupy about `52.70%`. The three primary TRUE PRE14_7 hits were `2024-06-05`, `2024-07-21`, and `2025-10-08`; important genuine exhaustion events `2023-12-25`, `2024-03-31`, and `2025-01-18` were missed. `2025-10-08` was WATCH/RISK in PRE14_7 but did not confirm RISK in PRE7_POST3.

The zero PRE21_0 onset count is binding negative evidence: captured events were already in WATCH/RISK before the frozen lead window, so this machine acts more like a sticky risk regime than a precise 7–14 day transition trigger. No same-ID threshold, persistence, onset-window, S2-only, CORE4-weight or hysteresis rescue is allowed.

0045 is permanently closed and **does not authorize a dynamic-gross stage**. 0044's underlying state-discrimination PASS remains valid; what failed is this particular state-to-trigger translation. Any alternative trigger architecture requires a fresh result-informed research ID before evaluation.

Canonical BRRK-0011, the winner lineage, Phase 6, signing, order submission and production authority remain unchanged.

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

The BRRK-WINNER development and robustness PASS results do not change any of these fields.

## Current drift assessment

`DRIFT_0`.

PR #159 closes a research-only trigger diagnostic with a binding FAIL. It adds immutable 0045 evidence and advances research lifecycle metadata only. No `execution/**`, canonical BRRK mathematics, Phase-6 observation, leverage/shorting, signing, order submission or production authority changes occur.

## Exact next task

1. Merge PR #159 only after the temporary 0045 one-shot/finalizer workflows are removed and final governance/no-drift/P3.2/Phase-6/handoff CI is green.
2. Preserve `BRRK-EXHAUSTION-TRIGGER-0045` as closed `FAIL_NO_DYNAMIC_GROSS_STAGE_ELIGIBILITY`; never rerun, retune or rescue it.
3. Do **not** create or run `BRRK-DYNAMIC-GROSS-0046` from this lineage; 0045 did not earn eligibility.
4. Preserve the distinction: 0044 confirms useful exhaustion-state discrimination, while 0045 shows this first absolute percentile/persistence/hysteresis trigger translation is inadequate.
5. Any future alternative trigger architecture must be a new result-informed preregistration, explicitly acknowledging 0045's sensitivity failure, sticky WATCH/RISK occupancy and zero PRE21_0 onset evidence before evaluation.
6. Continue Phase-6 future-only observation independently. All production, signing and order-submission authority remains false.
