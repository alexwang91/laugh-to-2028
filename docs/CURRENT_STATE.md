# BRRK Current State

Last updated: 2026-08-14

Authoritative repository: `alexwang91/laugh-to-2028`.
Merged 0064 PASS closeout: `ad8038af45bad2e25e8a7b88b569b1873635d9c2`.
Merged 0065 immutable closeout: `d1607277593a0c5c35bb0163e10e078f3dc85fc8`.
Merged 0066 DESIGN: `b42f1d9dcc0574f185e04aad3bc8eca61fd2531d`.
0066 owner-first registry commit: `44f8df24538216b9b83466522fc8efb209b3082a`.

## Required closed-research anchors

BRRK-EXHAUSTION-EVENT-STUDY-0043 — complete diagnostic
workflow run                         31381953131 / attempt 1
7–14 day exhaustion-ranking signal appears feasible
ID 0043 is closed against result-informed pruning, reweighting, threshold rescue

## Current research state

0062 = `FAIL_NO_SIGNAL_ATLAS_FAMILY_INFORMATION / CLOSED`.
0063 = `FAIL_IDLE_CASH_SWEEP_PRIMARY_ECONOMICS / CLOSED`.
0064 = `PASS_PASSIVE_CASH_ACCRUAL_ROBUSTNESS / CLOSED TO SAME-ID RERUN`.
0065 = `FAIL_NO_ROBUST_MULTI_ARCHITECTURE_IMPROVEMENT / CLOSED TO SAME-ID RERUN`.
0066 = `PREREGISTERED / IMPLEMENTATION ABSENT / NOT RUN`.
0066 research ID = `BRRK-BTC-SOL-PATH-EVENT-EARLY-WARNING-0066`.

## 0066 frozen event-first program

Price-only outcome assets = BTC / SOL.
Market scan horizons = 10/15/20/30/45/60/90/120/180/240 sessions.
Event types = DOWN / SIDEWAYS.
Duration grades = SHORT 10-20 / MEDIUM 30-60 / LONG 90-120 / SECULAR 180-240.
Decline severity additionally uses volatility-normalized maximum adverse excursion.
Indicators may not alter event definitions, thresholds, grades, onset extraction, suppression intervals or support.

Warning targets per asset = ANY_DOWN / MAJOR_DOWN / ANY_SIDEWAYS / LONG_SIDEWAYS.
Warning horizons = 1/3/5/10/20 sessions.
A positive warning label at date t means a qualifying unique onset occurs inside strictly future window `(t,t+L]`; it does not mean exactly L sessions later.
Dates inside an already-started event suppression interval are excluded from the classifier risk set.
Total asset/target/horizon tracks = 40.
Support is counted by unique underlying onsets: >=8 TRAIN+VALIDATION and >=3 FINAL required for confirmatory status.

Complete frozen 0062 Tier-A predictor universe remains mandatory: 185 raw cells + 17 family scores = 202 signal units.
Indicator-atlas hypothesis cell count = 202 * 40 = 8080. FINAL atlas multiplicity uses one-sided Mann-Whitney U tests for TRAIN-oriented ROC-AUC >0.50 with Holm-Bonferroni FWER=0.05 across all supported cells; PR-AUC lift, Brier and block metrics remain mandatory outputs. No FINAL sign flip or post-hoc screen.

Frozen predictor architectures:
1. P01 FAMILY_RIDGE_LOGIT;
2. P02 RAW_ELASTIC_NET_LOGIT;
3. P03 VALIDATION_SCREENED_SIGNAL_LOGIT;
4. P04 PCR_LOGIT;
5. P05 THEORY_QUADRATIC_LOGIT — explicitly RESULT_INFORMED from closed 0065, no privilege;
6. P06 SHALLOW_GBDT_CLASSIFIER;
7. P07 DISCRETE_TIME_HAZARD_LOGIT;
8. P08 STACKED_PROBABILITY_ENSEMBLE.

Frozen tuning accounting:
- P01 160 validation tuning executions;
- P02 360;
- P03 120;
- P04 480;
- P05 160;
- P06 320;
- P07 32;
- P08 0;
- validation tuning total = 1632;
- final predictor tracks = 64;
- final economic controllers = 8;
- declared model/controller variant budget = 1704;
- actual variants evaluated = 0.

Validation prediction window = 2023-01-01..2023-12-31.
FINAL event-prediction evaluation = 2024-01-01..2025-11-15.
Economic evaluation = 2024-01-01..2026-08-02.
At each refit, warning-horizon L labels may enter training only if prediction origin + L + 240 sessions is strictly earlier than refit date.
Refit cadence = 20 sessions.
Prediction after close t may affect only return row t+1.

Frozen economic controllers:
1. C01 BTC_ANY_DOWN_5D;
2. C02 SOL_ANY_DOWN_5D;
3. C03 MAX_BTC_SOL_ANY_DOWN_5D;
4. C04 BTC_MAJOR_DOWN_10D;
5. C05 MAX_BTC_SOL_MAJOR_DOWN_10D;
6. C06 MULTILEAD_DOWN_BLEND_3_5_10;
7. C07 DOWN_PLUS_SIDEWAYS;
8. C08 STACKED_EVENT_RISK.

Probability thresholds are calibrated on VALIDATION probabilities only: below p90 g=1; DOWN >=p90 g=.50; SIDEWAYS-only >=p90 g=.75; DOWN >=p97.5 g=.25; multiple rules use minimum g. No leverage, shorting or smoothing.
Outer turnover cost = 10 bps per unit change in outer multiplier.
Benchmark = closed 0064 passive-cash path reconstructed on common economic subwindow 2024-01-01..2026-08-02.

Confirmatory predictor and economic simultaneous inference = aligned non-circular MBB L60 / 4000 reps / seed660066 / Type-7 q95. Indicator-atlas multiplicity is the separate Holm-Bonferroni family described above.
PBO diagnostic = 8 contiguous slices / choose 4 = 70 splits across the 8 controllers where support permits.

Historical 0066 event atlas computed = false.
Historical 0066 indicator/event association computed = false.
Historical 0066 classifier metrics computed = false.
Historical 0066 controller CAGR/NAV/MDD computed = false.
Historical actual variants evaluated = 0 / 1704.
RUN_ATTEMPT.marker = ABSENT.
PRIMARY_RESULT.json = ABSENT.
EVIDENCE.json = ABSENT.
EXECUTION.json = ABSENT.
RUN_ONCE.marker = ABSENT.

## Frozen data identities

Market slice = `BRRK-LEADERSHIP-ROTATION-0048-EXPOSED-HIST-V1`.
Market evidence blob = `64ebf5c6deaf3f34dbeac715378f196ff0f4fafe`; payload SHA256 = `d1cd28bc76f2cd8ee0486287fc50b49e5451355a3e75132a2de5b30c15af3193`.
0062 feature engine blob = `cac8e946998c836d10842b9388e1e3ef345a8c0b`.
0062 loader blob = `059b55961e279dab41ba29b5b017de0922e4f33c`.
BRRK equity blob = `82c87f8cb0ff01c728ffd3b717fff17cf5a364f2`.
BRRK weights blob = `2f6c8d3a8c25d3cafeaa0128f1c425dac248370b`.
DTB3 blob = `71d50e26f8a9afb6bcb88401d20b97d5fb0a891a`; payload SHA256 = `4d8aee67dbd528ce38ff8482e9bb02dd5ccf2c6cd461f606fe90007151ab6879`.
0064 economic engine blob = `4060a307be2204c11952cb52e2fc718a5343d8e1`.
Network fetch = forbidden; replacement = forbidden; independent OOS = false.

## No-drift authority

production gross cap = 1.0
production_authorized_components = []
production_authorized = false
signature_authorized = false
order_submission_authorized = false
Canonical BRRK-0011 = NO CHANGE.
0064 = NO CHANGE.
0065 = NO CHANGE.
Phase 6 = NO CHANGE.

## Exact next step

Merge 0066 numerical/data PREREGISTRATION after fresh standing CI. Only then begin IMPLEMENTATION-ONLY using synthetic/artificial data; do not read 0066 historical outcomes or compute event counts, indicator associations, classifier metrics or portfolio economics during implementation.
