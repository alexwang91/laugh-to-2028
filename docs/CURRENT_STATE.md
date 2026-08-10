# BRRK Current State

Last updated: 2026-08-10  
Handoff PR: **#155**
Handoff branch: `research/brrk-exhaustion-event-study-0043`
Authoritative baseline main at branch creation: `0db4f6e4ca6d8fe610e54fbb96c9240752229cfd`
Latest merged research PR at branch creation: **#153**

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

PR #155 is read-only research/governance diagnostic work. The final intended diff contains the frozen diagnostic design, implementation, permanent contract test, execution binding, compact result/summary and handoff evidence only. The temporary one-shot workflow is removed. No `execution/**`, no `research/results/**`, no canonical BRRK mathematics, no Phase-6 collection and no production authority are changed.

## Exact next task

1. Merge PR #155 only after final governance/no-drift/Phase-6/handoff CI is green and the final diff contains no temporary workflow, no `execution/**`, and no historical `research/results/**` mutation.
2. Preserve `BRRK-EXHAUSTION-EVENT-STUDY-0043` as closed DEVELOPMENT diagnostic evidence; do not prune, reweight, retune thresholds or run dynamic-gross economics under this ID.
3. If continuing the exhaustion line, create a new result-informed research ID before defining a deduplicated low-dimensional state model or trigger. Validation must be episode/block-aware because the 16 detected peaks are not fully independent macro regimes.
4. Only after a separately frozen signal stage passes should a later research ID map exhaustion state to gross exposure and evaluate portfolio economics.
5. Continue Phase-6 future-only observation independently. Production, signing and order-submission authority remain false.
