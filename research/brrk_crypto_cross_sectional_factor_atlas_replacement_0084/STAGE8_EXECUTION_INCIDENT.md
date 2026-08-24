# 0084 Stage8 execution incident

Research ID: `BRRK-CRYPTO-CROSS-SECTIONAL-FACTOR-ATLAS-REPLACEMENT-0084`

State: `POST_MARKER_FROZEN_EXECUTION_INTERFACE_INCOMPLETE / NO_ADMISSIBLE_SCIENTIFIC_RESULT`.

## Trigger

The durable `RUN_ATTEMPT.marker` already exists at commit `06e2244b827897a21b7156eb123f044f4f389842`, so attempt `1/1` is consumed. Before opening any authorized nested scientific payload member, the marker-bearing ancestry was re-audited against the frozen Stage3 Stage8 contract and the exact Stage6-bound Stage4/Stage5 callable blobs.

## Deterministic defect

Stage3 requires Stage4 to implement the complete end-to-end scientific execution interface before Stage5 qualification, including deterministic staged-payload parsing/read accounting, all 16 factor calculations, exact 64-trial orchestration, primary statistics, bootstrap/Holm inference, robustness partitions, G0-G11, exact counters, and create-only result persistence.

The frozen implementation does not contain a callable that transforms the authorized staged payload objects into the 64 already-computed `TrialEvidence` inputs required by `integration.integrate_trial_evidence`. The frozen modules expose individual mechanics and post-statistics integration, but the integration entry point explicitly requires `already-computed, already-staged trial evidence`. No frozen Stage8 executor/adapter exists in the bound execution identity set.

A second frozen inconsistency exists in `engine.ExecutionAccounting.execution_valid()`: it accepts `scientific_engine_calls` in `(0, 1)`, while Stage3 and `persistence.ExecutionCounters.validate_terminal()` require exactly one scientific-engine call for terminal execution.

These are pre-existing frozen implementation defects. They were not detected by synthetic qualification or Stage7 identity-only preflight. They were discovered after attempt-marker durability but before any scientific payload value read and before any scientific-engine call.

## Budgets at incident seal

- attempt: `1/1 consumed`;
- controlled scientific-history reads: `0`;
- scientific engine: `0/1`;
- Stage8 scientific source-network fetches: `0`;
- scientific values exposed: `false`;
- result bundle: absent;
- `RUN_ONCE.marker`: absent.

The GitHub Actions artifact `9495175701` was retrieved as the already-bound offline staged artifact. Reading its outer artifact/manifest identity metadata does not constitute a nested scientific payload read and does not consume the controlled scientific-history read ledger.

## Fail-closed consequence

Post-marker implementation repair, new executor code, new adapter logic, source substitution, candidate replacement, history extension, rerun, retune, rescue, or recomputation are forbidden. Therefore this same-ID Stage8 attempt cannot legally proceed to controlled payload reads or a fabricated scientific-engine invocation.

No PASS, `FAIL_NO_QUALIFIED_FACTOR`, or `INCONCLUSIVE_INSUFFICIENT_SUPPORT` scientific result is admissible. A later governance/evidence stage may package this incident and close the consumed attempt under the frozen invalid-execution semantics, but it must not manufacture 64 scientific trial rows or claim that the scientific engine ran.

Production, signature, trading, and order authority remain false.
