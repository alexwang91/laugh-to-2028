# BRRK Current State

Last updated: 2026-08-14

Authoritative repository: `alexwang91/laugh-to-2028`.
Merged 0063 closeout: `b7fd66f28c8d7611cd4c71dc04b1c152bc65d62d`.
Merged 0064 DESIGN: `38b5740cb89ae16b4bc005f3d5bcb4f8e0a0181f`.
Merged 0064 preregistration: `24021324641df766da307b0ee231bb8b78920b93`.
Merged 0064 implementation: `7e771dea9355c4170e806af13b35a327beac0466`.
Merged 0064 controlled boundary: `876fdf657bd11bc4aeb9d0dcd3859886ee099568`.
0064 durable attempt commit: `51fe15adf20452d90700e9b5afa2313ee8775706`.
0064 immutable result commit: `d45e7e7e2d1a62f0243c4a1576bc4a60727d90d4`.
Merged 0064 PASS closeout: `ad8038af45bad2e25e8a7b88b569b1873635d9c2`.
0065 DESIGN branch: `research/0065-design-v1`.
0065 DESIGN commit: `530a58c0e5bfb52e5c33d3ccfeb5774351bde193`.

## Required closed-research anchors

BRRK-EXHAUSTION-EVENT-STUDY-0043 — complete diagnostic
workflow run                         31381953131 / attempt 1
7–14 day exhaustion-ranking signal appears feasible
ID 0043 is closed against result-informed pruning, reweighting, threshold rescue

## Current research state

0062 = `FAIL_NO_SIGNAL_ATLAS_FAMILY_INFORMATION / CLOSED`.
0063 = `FAIL_IDLE_CASH_SWEEP_PRIMARY_ECONOMICS / CLOSED`.
0064 = `PASS_PASSIVE_CASH_ACCRUAL_ROBUSTNESS / CLOSED TO SAME-ID RERUN`.
0065 = `DESIGN ONLY / ARCHITECTURE TOURNAMENT FROZEN / NOT PREREGISTERED / NOT RUN`.
0065 research ID = `BRRK-MULTI-ARCHITECTURE-GROSS-CONTROLLER-0065`.

0065 changes the research process from sequential one-off strategy trials to one prospectively frozen architecture tournament. It will compare eight structurally distinct combination methods over the complete 0062 Tier-A feature universe, with one common target, one common gross mapping, one common economic baseline/cost model and one exactly-once evaluation batch.

Frozen architecture classes at DESIGN:

1. A01 FAMILY_ELASTIC_NET — 17 family scores, additive shrinkage;
2. A02 RAW_ELASTIC_NET — all 185 cells, correlated raw-feature shrinkage;
3. A03 PCR_RIDGE — latent principal-component compression then ridge;
4. A04 THEORY_QUADRATIC_HESSIAN_RIDGE — second-order response surface with fixed theory interaction graph;
5. A05 GAM_SPLINE_RIDGE — smooth nonlinear family effects without cross-family interactions;
6. A06 SHALLOW_GBDT — bounded shallow tree interactions;
7. A07 HMM_REGIME_MIXTURE_RIDGE — latent regime probabilities plus state-conditional ridge;
8. A08 STACKED_ENSEMBLE — validation-only nonnegative convex stack of A01-A07.

Common supervised target at DESIGN = 20-session forward BTC log return, exactly the negative of 0062 T1 cash advantage at 20 sessions.

Common outer gross concept at DESIGN = no leverage / no shorting; ordinary or positive forecasts cannot increase risk above baseline, while sufficiently negative standardized forecasts reduce gross. Exact numerical mapping, refit cadence, hyperparameter grids, cost bps, temporal split indices, multiplicity procedure and PBO diagnostics must be frozen in PREREGISTRATION before any 0065 portfolio outcome is computed.

Feature anti-pruning rule = all eligible 185 cells / 17 family scores remain available according to architecture; no 0062 result-based family/cell deletion or favoritism.

Historical 0065 evaluation-period architecture CAGR/NAV/ranking = NOT COMPUTED.
Historical 0065 variants evaluated = 0.
RUN_ATTEMPT.marker = ABSENT.
PRIMARY_RESULT.json = ABSENT.
EVIDENCE.json = ABSENT.
EXECUTION.json = ABSENT.
RUN_ONCE.marker = ABSENT.

## 0064 frozen primary result

Mechanism = already-idle residual cash remains continuously interest-bearing; no additional sweep trade.
Primary = 50% DTB3 yield realization / 100 bps annual continuous idle-cash spread-fee.
Baseline terminal wealth = 62247.382312942056.
Primary terminal wealth = 62813.41563922909.
Baseline calendar-span CAGR = 0.6516609785339962.
Primary calendar-span CAGR = 0.6557689400699214.
CAGR improvement = +0.004107961535925217 absolute = +0.4107961535925217 percentage points.
Baseline MDD = -0.3371507034657847.
Primary MDD = -0.3366471268083583, so drawdown did not worsen.
Primary chronological recurrence = 4 / 4 positive blocks, each 333 rows.
Dependence-aware MBB = L60 / 4000 reps / seed 640064 / Type-7 q95; one-sided LCB = 3.4274270071632633e-06 > 0.
Core stress robustness = all 9 preregistered cells positive in relative terminal log growth.
G0 through G6 = PASS.
Classification = `PASS_PASSIVE_CASH_ACCRUAL_ROBUSTNESS`.

## No-drift authority

production gross cap = 1.0
production_authorized_components = []
production_authorized = false
signature_authorized = false
order_submission_authorized = false

Canonical BRRK-0011 = NO CHANGE.
0064 = NO CHANGE.
Phase 6 = NO CHANGE.

## Exact next step

Merge 0065 DESIGN after fresh standing CI. Then create the 0065 owner-first numerical/data PREREGISTRATION that freezes exact feature/data identities, temporal split indices, eight architecture hyperparameter budgets, deterministic seeds, common forecast-to-gross mapping, 0064 cash/cost economics, simultaneous eight-method inference and backtest-overfitting diagnostics. Do not compute any 0065 evaluation-period CAGR before that preregistration merges.
