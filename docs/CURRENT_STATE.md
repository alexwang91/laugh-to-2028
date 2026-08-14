# BRRK Current State

Last updated: 2026-08-14

Authoritative repository: `alexwang91/laugh-to-2028`.
Merged 0064 PASS closeout: `ad8038af45bad2e25e8a7b88b569b1873635d9c2`.
Merged 0065 DESIGN: `09f9afc69183387afaabfe540394eb01989df148`.
Merged 0065 preregistration: `7b71c9f3394be17e5fd10ec08147207d268fc00a`.
Merged 0065 implementation: `c3305eec933bb4d48ca14ec40765b798d50f836f`.
0065 owner-first commit: `a717d1d359e1b980a7c727e48ec26a1ffb0fc3a6`.
0065 scientific engine blob: `762b608dd9eb5feedc06867ce07f02d0de8ea928`.
0065 exactly-once runner blob: `0a81c3ac98420e86786a81bb15b7547d71b27460`.
0065 full synthetic tournament validation run: `31787644804`.

## Required closed-research anchors

BRRK-EXHAUSTION-EVENT-STUDY-0043 — complete diagnostic
workflow run                         31381953131 / attempt 1
7–14 day exhaustion-ranking signal appears feasible
ID 0043 is closed against result-informed pruning, reweighting, threshold rescue

## Current research state

0062 = `FAIL_NO_SIGNAL_ATLAS_FAMILY_INFORMATION / CLOSED`.
0063 = `FAIL_IDLE_CASH_SWEEP_PRIMARY_ECONOMICS / CLOSED`.
0064 = `PASS_PASSIVE_CASH_ACCRUAL_ROBUSTNESS / CLOSED TO SAME-ID RERUN`.
0065 = `IMPLEMENTED / CONTROLLED EXECUTION BOUNDARY FROZEN / NOT RUN`.
0065 research ID = `BRRK-MULTI-ARCHITECTURE-GROSS-CONTROLLER-0065`.

0065 is one prospectively frozen architecture tournament, not sequential one-off strategy search. Historical 0065 portfolio CAGR/NAV/ranking has not been computed.

### Frozen and implemented method set

1. A01 FAMILY_ELASTIC_NET — 17 family scores;
2. A02 RAW_ELASTIC_NET — 185 cells;
3. A03 PCR_RIDGE — PCA latent factors + ridge;
4. A04 THEORY_QUADRATIC_HESSIAN_RIDGE — 17 linear + 17 squared + 10 theory interactions;
5. A05 GAM_SPLINE_RIDGE — additive cubic splines + ridge;
6. A06 SHALLOW_GBDT — bounded depth 1/2 boosting;
7. A07 HMM_REGIME_MIXTURE_RIDGE — 2/3-state Gaussian HMM + state-specific ridge with causal forward-filtered evaluation probabilities;
8. A08 STACKED_ENSEMBLE — validation-only nonnegative convex NNLS stack of A01-A07.

Frozen validation tuning config count = 63.
Frozen final architecture count = 8.
Declared total research variant budget = 71.
Actual historical variants evaluated = 0.

### Frozen common scientific contract

Feature universe = complete 0062 Tier-A atlas: 185 cells / 17 family scores; no result-informed pruning.
Target = 20-session forward BTC log return.
TRAIN origins end = 2021-12-31.
VALIDATION origins = 2022-01-01 through 2022-11-19.
Portfolio evaluation = 2022-12-10 through 2026-08-02.
Validation and evaluation refit cadence = every 20 sessions.
At every refit, only origins whose 20-session labels have fully matured strictly before the refit date are eligible.
Forecast after close t may affect only next portfolio return row t+1.
Common gross map = `g=clip(1+0.25*z,0,1)` where z uses fit-sample prediction median and `1.4826*MAD`; no smoothing, leverage or shorting.
Economic benchmark = frozen 0064 primary: 50% DTB3 realization / 100 bps annual continuous cash fee.
Outer overlay cost = 10 bps per unit outer gross turnover.
Forcing g=1 must reconstruct 0064 primary within frozen numerical tolerance.
Four count-balanced contiguous evaluation blocks.
Simultaneous inference = aligned non-circular MBB L60 / 4000 reps / seed 650065 / Type-7 q95 across all valid final architectures.
PBO diagnostic = 8 contiguous slices / choose 4 = 70 CSCV splits.
Deflated-Sharpe-style diagnostic uses declared trial count 71 and is diagnostic only.

A scientific winner must beat 0064 in terminal wealth and CAGR, have noninferior MDD, >=3/4 positive blocks, simultaneous one-sided LCB >0, and pass cost/timing/identity contracts.

### Controlled execution boundary

RUN_INTERFACE blob = `0e13a536ca4ee2bc9de4cdf2bcbfe8cd1392b18b`.
RESULT_SCHEMA blob = `05dd87cd6f820a8573ff434d8cda21656fa164fd`.
run_once.py blob = `0a81c3ac98420e86786a81bb15b7547d71b27460`.
PREREGISTRATION blob = `5e98ae3c384d75a970b87f5ceb9fb893e3967acd`.
DATASET_DECLARATION blob = `031ed9a5d00526029825ad82b0183a09db8e6149`.
IMPLEMENTATION_CONTRACT blob = `508c909eedeff79796fec05fbbb125d1015fe962`.

Preflight is Git-identity + runtime-artifact absence only: historical content reads=0, loader calls=0, engine calls=0.
Unique execution requires a durable RUN_ATTEMPT commit before any historical content read.
Unique execution budget: market/equity/weights/DTB3 each read once; market loader once; scientific engine once; network fetches=0.
All 63 tuning configs and all 8 final architectures execute inside that one scientific engine call.
Partial-result automatic recomputation is forbidden. Finalize has zero historical reads and zero scientific calls.

### Implementation validation

Dedicated synthetic unit suite passed for all seven base model fit/predict interfaces, 44-column quadratic/Hessian expansion, causal HMM filtering, NNLS stack, common gross map, outer-turnover cost, g=1 passive-cash reconstruction algebra, simultaneous MBB determinism, 70-split PBO and deflated-Sharpe diagnostic.
Full synthetic 2020-08-11..2026-08-02 tournament integration run `31787644804` completed the entire 185-cell construction -> 63 validation tuning configurations -> 8 final methods -> evaluation gross paths -> portfolio economics -> simultaneous inference/PBO pipeline successfully on artificial data.
Historical 0065 portfolio content reads during implementation = 0.
Historical 0065 CAGR computed during implementation = false.

### Frozen data identities

0062 market payload blob = `64ebf5c6deaf3f34dbeac715378f196ff0f4fafe`; payload SHA256 = `d1cd28bc76f2cd8ee0486287fc50b49e5451355a3e75132a2de5b30c15af3193`.
0062 feature engine blob = `cac8e946998c836d10842b9388e1e3ef345a8c0b`.
0062 loader blob = `059b55961e279dab41ba29b5b017de0922e4f33c`.
BRRK equity blob = `82c87f8cb0ff01c728ffd3b717fff17cf5a364f2`.
BRRK weights blob = `2f6c8d3a8c25d3cafeaa0128f1c425dac248370b`.
DTB3 blob = `71d50e26f8a9afb6bcb88401d20b97d5fb0a891a`; payload SHA256 = `4d8aee67dbd528ce38ff8482e9bb02dd5ccf2c6cd461f606fe90007151ab6879`.
0064 economic engine blob = `4060a307be2204c11952cb52e2fc718a5343d8e1`.

RUN_ATTEMPT.marker = ABSENT.
PRIMARY_RESULT.json = ABSENT.
EVIDENCE.json = ABSENT.
EXECUTION.json = ABSENT.
RUN_ONCE.marker = ABSENT.

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

Run zero-result boundary validation plus synthetic exactly-once persistence tests and fresh standing CI. After controlled-boundary merge, rerun Git-only preflight on the exact merged boundary SHA. Only if it passes may the single historical tournament attempt create and durably persist RUN_ATTEMPT.marker, then read the four frozen historical inputs exactly once and call the tournament engine exactly once.
