# BRRK Current State

Last updated: 2026-08-14

Authoritative repository: `alexwang91/laugh-to-2028`.
Merged 0064 PASS closeout: `ad8038af45bad2e25e8a7b88b569b1873635d9c2`.
Merged 0065 immutable closeout: `d1607277593a0c5c35bb0163e10e078f3dc85fc8`.
Merged 0066 IMPLEMENTATION: `aa55a5625f59e1f0221bf972104c96e5b709511a`.
Merged 0066 CONTROLLED-EXECUTION BOUNDARY: `b1af358577349c58a8468a3822775152b5aaad34`.
0066 unique RUN_ATTEMPT marker commit: `03e6f5a099c9163ff14c3387d4d06f0dff4f368a`.
Merged 0066 immutable execution-timeout closeout: `9a45bb5e778e21dfd30d7abc4ff7d9889542b495`.
0067 owner-first registry commit: `e584003ed04c92322c6cde87714d5cce4995b12e`.
Merged 0067 DESIGN: `f3e5adc14631d9a3ae13ba686388b7a3c189e867`.
Merged 0067 PREREGISTRATION: `062eb06c186cc54a729f0f65ae3888db0f4d2300`.

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
0066 = `INVALID_EXECUTION / CLOSED TO SAME-ID RERUN`.
0067 = `IMPLEMENTATION BUILT / QUICK EQUIVALENCE PASS / NOT FULL-SHAPE QUALIFIED / NOT RUN`.
0067 research ID = `BRRK-BTC-SOL-PATH-EVENT-EARLY-WARNING-RUNTIME-QUALIFIED-0067`.
0067 is `PROCESS_INFORMED_BY_0066_TIMEOUT / NOT_RESULT_INFORMED_BY_0066`.

## 0066 immutable execution finding

0066 historical workflow run `31806690040`, job `94787213750`, had `timeout-minutes: 350` and `cancel-in-progress: false`. Attempt 1/1 was consumed and the evaluate step was cancelled at the configured wall-clock boundary before a complete result bundle persisted.

0066 artifacts remain:
- `RUN_ATTEMPT.marker` PRESENT and immutable;
- `PRIMARY_RESULT.json` ABSENT;
- `EVIDENCE.json` ABSENT;
- `EXECUTION.json` ABSENT;
- `RUN_ONCE.marker` ABSENT.

0066 same-ID rerun/retune/rescue/recomputation is forbidden. No 0066 scientific inference exists.

## 0067 frozen scientific preregistration

Scientific semantics preserve the frozen 0066 program rather than redesigning it after the timeout:
- outcome assets BTC/SOL; BTC/ETH/SOL predictor context;
- price-only DOWN/SIDEWAYS event construction over 10/15/20/30/45/60/90/120/180/240 sessions;
- duration grades SHORT 10–20 / MEDIUM 30–60 / LONG 90–120 / SECULAR 180–240;
- targets ANY_DOWN / MAJOR_DOWN / ANY_SIDEWAYS / LONG_SIDEWAYS;
- warning leads 1/3/5/10/20; strictly future `(t,t+L]` onset label;
- 40 asset/target/lead tracks;
- unique-onset support >=8 TRAIN+VALIDATION and >=3 FINAL;
- predictor universe 185 raw cells + 17 family scores = 202 units;
- indicator atlas 8080 hypotheses;
- P03 screening VALIDATION-only: positive PR-AUC lift, >=3/4 positive blocks, max2/family, max12;
- P01 FAMILY_RIDGE_LOGIT;
- P02 RAW_ELASTIC_NET_LOGIT;
- P03 VALIDATION_SCREENED_SIGNAL_LOGIT;
- P04 PCR_LOGIT;
- P05 THEORY_QUADRATIC_LOGIT, RESULT_INFORMED from closed 0065 only, no privilege;
- P06 SHALLOW_GBDT_CLASSIFIER;
- P07 DISCRETE_TIME_HAZARD_LOGIT;
- P08 STACKED_PROBABILITY_ENSEMBLE;
- validation tuning configs = 1632;
- final predictor tracks = 64;
- final controllers = 8;
- declared model/controller variant budget = 1704;
- validation predictions 2023-01-01..2023-12-31;
- FINAL event prediction evaluation 2024-01-01..2025-11-15;
- economic evaluation 2024-01-01..2026-08-02;
- refit every 20 sessions;
- label maturity origin + L + 240 sessions strictly before refit;
- prediction after close t affects return t+1 only;
- controller thresholds frozen on VALIDATION: below p90 g=1, DOWN p90 g=.50, SIDEWAYS-only p90 g=.75, DOWN p97.5 g=.25, multiple=min g;
- no leverage, no short, no smoothing;
- outer turnover cost = 10 bps per unit multiplier change;
- benchmark = closed 0064 passive-cash path on common window;
- aligned non-circular MBB L60 / 4000 reps / scientific seed 660066 / Type-7 q95;
- PBO = 8 slices choose4 =70 where supported.

The frozen exact event thresholds/formulas, model grids, validation selection, predictive/economic gates, controller definitions, multiplicity handling, and classification enum are in `PREREGISTRATION.json`.

## 0067 frozen historical data identities

Market slice = `BRRK-LEADERSHIP-ROTATION-0048-EXPOSED-HIST-V1`.
Market evidence blob = `64ebf5c6deaf3f34dbeac715378f196ff0f4fafe`; payload SHA256 = `d1cd28bc76f2cd8ee0486287fc50b49e5451355a3e75132a2de5b30c15af3193`.
0062 feature engine blob = `cac8e946998c836d10842b9388e1e3ef345a8c0b`.
0047 loader blob = `059b55961e279dab41ba29b5b017de0922e4f33c`.
BRRK equity blob = `82c87f8cb0ff01c728ffd3b717fff17cf5a364f2`.
BRRK weights blob = `2f6c8d3a8c25d3cafeaa0128f1c425dac248370b`.
DTB3 blob = `71d50e26f8a9afb6bcb88401d20b97d5fb0a891a`; payload SHA256 = `4d8aee67dbd528ce38ff8482e9bb02dd5ccf2c6cd461f606fe90007151ab6879`.
0064 economic engine blob = `4060a307be2204c11952cb52e2fc718a5343d8e1`.
Network fetch/replacement forbidden. DEVELOPMENT history is researcher-exposed and not independent OOS.

## 0067 physical compute accounting

The preregistered workload exposes the physical estimator-fit graph explicitly:
- validation rows 365; refit blocks 19;
- nonhazard validation configs 1600;
- pooled hazard configs 32;
- validation estimator fit calls = 31,008;
- economic prediction rows 945; refit blocks 48;
- nonhazard selected asset/target/lead series 240;
- pooled hazard asset/target series 8;
- economic estimator fit calls = 11,904;
- total estimator fit calls = 42,912;
- P08 NNLS solves = 40;
- predictive bootstrap replicates = 4000;
- economic bootstrap replicates = 4000;
- PBO splits = 70.

No implementation may use the high-level 1704 variant count as a substitute for this runtime load accounting.

## 0067 full-shape qualification gate

Before any 0067 historical `RUN_ATTEMPT.marker` may exist, the exact intended implementation/environment must pass a full-shape nonhistorical qualification.

Frozen environment/limits:
- GitHub runner label `ubuntu-24.04`, x86_64;
- deterministic process worker count =4;
- Python 3.12;
- requirements blobs `df60fe952f573fc6201b16b9de6b6043fbe7dbe2` and `c48550e67350bdc1e640ac8eb5e2ea02986ad83a`;
- PYTHONHASHSEED=0 and OMP/OPENBLAS/MKL/NUMEXPR threads=1 per worker;
- synthetic qualification seed = 670067;
- synthetic calendar rows =2183 with the same temporal/load geometry but no historical values;
- all 42,912 estimator fit calls, 40 NNLS solves, 4000+4000 bootstrap replicates, and 70 PBO splits must execute; no shape reduction;
- qualification job timeout =210 minutes;
- PASS wall-clock <=180 minutes;
- historical job hard timeout remains 350 minutes;
- required margin >=170 minutes;
- process-tree peak RSS <=4 GiB AND <=60% of MemTotal;
- swap/OOM forbidden;
- zero historical payload reads, zero historical market loader calls, zero historical equity/weights/DTB3 reads, zero network fetches;
- exact/canonical reference equivalence required; floating tolerance atol 1e-12, rtol 1e-10 where exact equality is not prospectively required.

Qualification failure blocks historical access without consuming the unique historical attempt. Semantic-preserving engineering remediation may repeat synthetic qualification. Raising timeout, dropping scientific workload, loosening solver semantics, or approximation cannot turn a failure into PASS.

## 0067 zero-result assertions

Historical event atlas computed = false.
Historical classifier metrics computed = false.
Historical controller economics computed = false.
Historical validation configs evaluated = 0.
Historical model/controller variants evaluated = 0.
0067 `RUN_ATTEMPT.marker` = ABSENT.
0067 `PRIMARY_RESULT.json` = ABSENT.
0067 `EVIDENCE.json` = ABSENT.
0067 `EXECUTION.json` = ABSENT.
0067 `RUN_ONCE.marker` = ABSENT.

## No-drift authority

production gross cap = 1.0
production_authorized_components = []
production_authorized = false
signature_authorized = false
order_submission_authorized = false
Canonical BRRK-0011 = NO CHANGE.
0064 = NO CHANGE.
0065 = NO CHANGE.
0066 = NO CHANGE.
Phase 6 = NO CHANGE.

## 0067 implementation-only status

Implementation branch = `research/0067-implementation-v1`.
Scientific reference = immutable closed-0066 engine/model/event semantics; 0066 historical recomputation remains forbidden.
Runtime-only implementation changes = maturity-mask caching, pooled-hazard schedule caching, deterministic four-process validation/economic prediction execution, predictive-bootstrap parallel reduction with parent-generated frozen RNG draws, and exact economic-bootstrap vectorization.
Full-shape qualification runner = `research/brrk_btc_sol_path_event_early_warning_runtime_qualified_0067/qualification.py`.
Historical payload access remains forbidden and no 0067 historical attempt marker exists.

Quick nonhistorical reference-equivalence workflow = `31867425779`; verdict = `PASS`; 8080 indicator cells reported and all reference-equivalence fixtures passed.
Bounded implementation test workflow = `31867565008`; verdict = `PASS`.

## Exact next step

Open and merge IMPLEMENTATION-ONLY after standing CI is green. Only after implementation merge may the exact merged implementation run the preregistered full-shape nonhistorical qualification. A historical controlled-execution boundary remains forbidden until a full-shape qualification PASS is durably recorded.
