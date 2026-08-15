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

## Root-cause hypothesis to test

The 0067 qualification generator forced synthetic support for every track and constructed labels so every scored block contained both classes. The implementation selects classifier/hazard tracks for downstream use only when validation metrics return `status == OK`; P08 is solved only when eligible base predictions exist. Therefore downstream economic work and P08 work are data-dependent even when the scientific selection rules are frozen.

The old qualification tested one all-supported synthetic regime and then froze its downstream physical counts as if those counts were invariant under historical support/missingness/class-definition outcomes. The historical run can therefore follow the same scientific code and still generate a smaller eligible downstream graph.

This hypothesis explains the observed signature without requiring a validation-path divergence: validation work remains structurally complete at 31,008 fits while economic/P08 work contracts after validation eligibility is known.

## Required falsification tests before any new historical attempt

0068 must run nonhistorical qualification across multiple deterministic support regimes, including full support, partial support, single-class/undefined tracks, missing eligible base predictions, and mixed P07/P08 eligibility. Each regime must prove that qualification and controlled execution use the same graph-construction code and produce the same ordered work manifest and trace hash for the same synthetic inputs.

The successor must not require one fixed historical economic-fit count or one fixed historical NNLS count unless those quantities are proven structurally invariant under all preregistered eligibility regimes. Instead it must freeze the graph-construction rule and verify complete consumption of the graph produced prospectively inside the single authorized execution.

## Scientific no-drift rule

0068 may change execution assurance, graph accounting, trace instrumentation, and qualification coverage only. It must not change event definitions, features, P01-P08 model semantics, grids, hyperparameter selection, horizons, controllers, economics, bootstrap/PBO definitions, classification gates, or production authority.