# 0067 Execution-Path Forensics

Research successor: `BRRK-BTC-SOL-PATH-EVENT-EXECUTION-EQUIVALENCE-0068`

## Scope

This document records engineering/process information learned from the closed 0067 execution. It does not reinterpret, rescue, rerun, recompute, or scientifically retune 0067.

## Observed 0067 accounting

- validation estimator fit attempts: 31,008 / 31,008
- economic estimator fit attempts: 5,808 / 11,904 frozen requirement
- total estimator fit attempts: 36,816 / 42,912 frozen requirement
- P08 stacking NNLS solves: 20 / 40 frozen requirement
- process workers: 4 / 4

The nonhistorical full-shape qualification produced 31,008 validation fits, 11,904 economic fits and 40 NNLS solves.

## Root cause

The 0067 qualification generator forced synthetic support for every track and constructed labels so every scored block contained both classes. The implementation selects classifier/hazard tracks for downstream use only when validation metrics return `status == OK`; P08 is solved only when eligible base predictions exist. Therefore downstream economic work and P08 work are data-dependent even when the scientific selection rules are frozen.

The economic window uses a 20-session refit cadence and contains 48 refit blocks. In the full-support regime there are 240 selected P01-P06 asset/target/horizon tasks plus 8 pooled P07 asset/target tasks, for 248 downstream fit tasks. `248 × 48 = 11,904`, exactly the frozen qualification count.

The historical run recorded 5,808 economic fit attempts. `5,808 / 48 = 121`, so the historical validation output generated 121 eligible downstream fit tasks and the runner consumed those tasks completely. This is consistent with the frozen implementation's `selected_params.get(...); if params is None: continue` graph construction.

P08 has `2 assets × 4 targets × 5 warning horizons = 40` possible stack locations. The historical run recorded exactly 20 NNLS solves. This is consistent with the implementation's rule that a stack is solved only when at least one eligible base validation prediction exists.

Validation remained 31,008 / 31,008 because validation tuning enumerates the full frozen configuration graph before downstream eligibility is known.

Therefore the 0067 accounting signature is explained by a boundary-model error: the controlled boundary treated the nonhistorical all-supported downstream graph as a historical invariant. The runner did not omit an arbitrary subset of required downstream work; it generated a smaller lawful downstream graph from frozen validation-eligibility rules and then failed only because the boundary required the synthetic full-support count.

## Required falsification tests before any new historical attempt

0068 must run nonhistorical qualification across multiple deterministic support regimes, including full support, partial support, single-class/undefined tracks, missing eligible base predictions, and mixed P07/P08 eligibility. Each regime must prove that qualification and controlled execution use the same graph-construction code and produce the same ordered work manifest and trace hash for the same synthetic inputs.

The successor must not require one fixed historical economic-fit count or one fixed historical NNLS count unless those quantities are proven structurally invariant under all preregistered eligibility regimes. Instead it must freeze the graph-construction rule and verify complete consumption of the graph produced prospectively inside the single authorized execution.

For economic estimator accounting, the manifest must record the expected refit count for each eligible high-level task and compare the sum of expected physical fit calls with observed fit attempts. Counting only high-level tasks is insufficient.

## Scientific no-drift rule

0068 may change execution assurance, graph accounting, trace instrumentation, and qualification coverage only. It must not change event definitions, features, P01-P08 model semantics, grids, hyperparameter selection, horizons, controllers, economics, bootstrap/PBO definitions, classification gates, or production authority.