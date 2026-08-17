# BRRK-SOL-LONG-SIDEWAYS-EARLY-WARNING-EPISODE-ROBUSTNESS-0070 — IMMUTABLE CLOSEOUT

Status: `PASS_LOCKED_EPISODE_ROBUSTNESS_REPLICATION / CLOSED TO SAME-ID RERUN`

Date: 2026-08-17

## Terminal classification

0070 is immutably closed after its single prospectively authorized controlled development-history attempt completed with `execution_valid=true` and scientific classification `PASS_LOCKED_EPISODE_ROBUSTNESS_REPLICATION`.

The result establishes the narrow preregistered claim only: the frozen 0069 primary `P02_RAW_ELASTIC_NET_LOGIT|SOL|T4_LONG_SIDEWAYS` warning at exactly 10 sessions remains robust when each of the seven unique final SOL T4_LONG_SIDEWAYS event onsets is removed in turn under the locked LOEO definition, and the frozen P03/P08 dependent corroborative cluster remains supportive. No controller, portfolio, CAGR, NAV, drawdown or production claim is established by 0070.

This evidence is researcher-exposed DEVELOPMENT history, not independent OOS evidence, and creates no production authority.

## Frozen lineage

- research ID: `BRRK-SOL-LONG-SIDEWAYS-EARLY-WARNING-EPISODE-ROBUSTNESS-0070`
- owner-first registry commit: `28be2794f8471e400fe70196460eed744cce694c`
- merged DESIGN: `828e90fa4b48ecb2ddc297d3b798e918601af2e9`
- merged PREREGISTRATION: `b00dd5e50401fd0b35c57d962d0625fa5790792f`
- merged IMPLEMENTATION: `378c0a0098d9a508c20a0e0bb891a503e2357f2e`
- merged QUALIFICATION EVIDENCE: `709903bf5443cbb3b1fbd9d2c588db94b5566c6a`
- qualification result blob: `8ad8cc764407f954da7c82e06ad5fa0cb3b97ca1`
- merged CONTROLLED-EXECUTION BOUNDARY: `0c5a6affc2243a0fdaf621f7801e1870657f1254`
- exact merged-boundary zero-result preflight: PASS
- unique controlled workflow: `32040286477` = PASS
- finalized immutable result branch head before handoff-only documentation: `a62ffbe3557530beb6aae24c94975ac1f1041fe3`
- merged immutable result bundle: `174a30dc4950e7351f3a746edc8f581b8f12e6d3`
- controlled development-history attempt budget: `1`
- controlled development-history attempt consumed: `1/1`

## Frozen scientific contract

Primary:
- `P02_RAW_ELASTIC_NET_LOGIT|SOL|T4_LONG_SIDEWAYS`
- warning lead: exactly `10` sessions
- frozen 0069 full-window PR-AUC: `0.7974030713822858`
- frozen prevalence: `0.45544554455445546`
- frozen PR-AUC lift: `0.34195752682783037`
- frozen ROC-AUC: `0.7913043478260869`
- final unique onset count: exactly `7`

Dependent corroborative cluster:
- `P03_VALIDATION_SCREENED_SIGNAL_LOGIT|SOL|T4_LONG_SIDEWAYS`
- `P08_STACKED_PROBABILITY_ENSEMBLE|SOL|T4_LONG_SIDEWAYS`
- P03/P08 are one dependent corroborative cluster, not two independent confirmations.

LOEO semantics:
- positive Y10 rows map deterministically to the earliest qualifying SOL T4 onset in `(t,t+10]`;
- exactly seven folds are formed;
- each fold removes all positive rows assigned to one onset while retaining all other rows;
- no retraining, reselection, recalibration, threshold change, hyperparameter change or alternate fold definition is allowed.

## Historical scientific result

Persisted classification: `PASS_LOCKED_EPISODE_ROBUSTNESS_REPLICATION`.

Required reproduction and support:
- full-window reproduction: PASS at absolute tolerance `1e-12`;
- exactly seven preregistered onsets/folds are defined;
- P02 PR-AUC lift remains positive in every fold;
- P02 ROC-AUC remains above `0.50` in every fold;
- P02 median PR-lift retention = `0.9823275624`;
- P02 fold count with retention >= `0.50` = `7/7`;
- frozen P03/P08 dependent corroborative-cluster gate = PASS.

The result exceeds the preregistered P02 gates of median retention >=0.75 and at least 6/7 folds with retention >=0.50 while satisfying the every-fold discrimination requirements. This statement records the already-persisted 0070 result; the closeout performs no recomputation.

## Exactly-once execution evidence

The controlled execution completed under the frozen 0070 boundary contract.

- durable `RUN_ATTEMPT.marker` existed on the result branch before the first permitted controlled source-content read;
- attempt marker binds attempt 1/1 to boundary `0c5a6affc2243a0fdaf621f7801e1870657f1254` and workflow `32040286477`;
- controlled source reads: 0069 `PRIMARY_RESULT` = `1`, 0069 `EVIDENCE` = `1`, `MARKET_EVIDENCE` = `1`;
- market-loader calls = `1`;
- frozen prediction reconstruction calls = `1`;
- validation tuning calls = `0`;
- model reselection calls = `0`;
- LOEO retraining calls = `0`;
- network fetches = `0`;
- create-only `PRIMARY_RESULT.json`, `EVIDENCE.json`, and `EXECUTION.json` were hash-bound to the attempt;
- marker-only finalization performed zero controlled-source rereads and zero additional reconstruction;
- `RUN_ONCE.marker` was durably persisted and seals the attempt;
- same-ID rerun, retune and rescue are false.

## Evidence boundary and limitations

0070 does not create independent OOS evidence because the underlying history is researcher-exposed DEVELOPMENT history inherited from the closed 0069 lineage.

0070 does not evaluate:
- controller thresholds or exposure mappings;
- transaction-cost economics;
- CAGR, Sharpe, Sortino, drawdown, Calmar or NAV;
- portfolio integration;
- carry, trend, cross-sectional or option strategies;
- production execution.

Any economic/controller investigation prompted by this PASS requires a new owner-first research ID with a new prospective DESIGN and PREREGISTRATION. The intended immediate successor may be `BRRK-SOL-LONG-SIDEWAYS-CONTROLLER-INTEGRATION-0071`, but this closeout itself does not register or authorize 0071.

## Scientific no-drift

No target, signal, horizon, feature universe, architecture, frozen validation selection, hyperparameter, onset assignment, LOEO definition, robustness threshold, evidence identity, historical data identity, controller/economic rule, canonical BRRK strategy, or production/signature/order authority changed after preregistration.

No same-ID controlled rerun, retune, rescue or recomputation occurred.

## Terminal governance

0070 is permanently closed to same-ID controlled development-history execution. Attempt 1/1 is consumed. No cancellation, retrigger, rerun, retune, rescue, recomputation, alternate threshold, alternate onset mapping or scientific reinterpretation is legal for this research ID.

Any future economic controller, alternate warning target, alternate horizon, alternate signal, independent-OOS evaluation or portfolio integration must use a new prospective owner-first research ID.

## No-drift authority

- `production_authorized = false`
- `signature_authorized = false`
- `order_submission_authorized = false`
- production authorized components: `[]`
- Canonical BRRK-0011: NO CHANGE
- closed 0064: NO CHANGE
- closed 0065: NO CHANGE
- closed 0066: NO CHANGE
- closed 0067: NO CHANGE
- closed 0068: NO CHANGE
- closed 0069: NO CHANGE
- Phase 6: NO CHANGE

This closeout performs no controlled historical measurement, evidence-content reread, model tuning, scientific recomputation or production authorization.
