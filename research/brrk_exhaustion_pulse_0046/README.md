# BRRK-EXHAUSTION-PULSE-0046

Status: **IMPLEMENTED_PRE_RESULT_NOT_RUN**

PR #163 formally preregistered this single `PROGRAM_GOVERNED_V1` result-informed transition-pulse candidate at merge `48a140a1d58cba859d537e7dee0ad399c541527a`. The exact mathematical design remains the PR #162 freeze in `research/governance/BRRK_EXHAUSTION_PULSE_0046_DESIGN_FREEZE_2026-08-10.md`.

This implementation branch does not reopen design selection and has not executed calibration or historical outcome evaluation.

## Frozen candidate

```text
exact 0044 S1/S2/S3/S4 axes
  -> 64-session causal pre-change OLS baseline
  -> one-sided positive slope working GLR per axis
  -> equal mixture over all 15 non-empty axis subsets
  -> maximum over change ages 3..32
  -> label-blind VAR(1) null calibration
  -> circular residual-vector block bootstrap, block=7
  -> 5,000 paths, seed=460046, burn-in=256, path=1,460
  -> threshold selected for truncated model-implied ARL0 >=365
  -> CALIBRATION_LOCK before any event taxonomy may be imported
  -> Transition Pulse = raw-alarm threshold upcrossing only
```

There is no Kalman/state-space smoother, raw-difference CUSUM, BOCPD, HMM, supervised classifier, S2-only rule, CORE4 duplication, persistence vote, cooldown, refractory period, recovery threshold or hysteresis state machine under this ID.

## Enforced information firewall

The implementation is split into three runtime stages:

```text
prepare-predictors
    raw causal inputs -> create-only PREDICTOR_PATH.json
    artifact contains only timestamp + S1/S2/S3/S4

calibrate
    imports detector + predictor_io only
    does not import market/NAV loaders or taxonomy code
    -> create-only CALIBRATION_LOCK.json

evaluate
    validate lock hash + code SHA + predictor binding + ARL0 first
    -> only then dynamically import evaluation/taxonomy module
    -> exactly-once PRIMARY_RESULT output
```

`calibration.py` therefore receives only timestamps and the frozen S1-S4 predictor artifact. It cannot call candidate detection, event classification, macro-episode assignment or outcome windows. `run_once.evaluate()` validates the lock before the evaluation module import.

## Pre-result implementation clarifications frozen before any calibration

These implementation semantics are fixed now and cannot change after any 0046 output:

- synthetic `T_b` is 1-based from synthetic path session 1; detector warm-up cannot cross but remains on the ARL clock;
- if several pulses occur inside PRE21_0, the earliest pulse controls onset lead, matching 0045 scan direction;
- raw-alarm spell p90 uses empirical nearest rank `ceil(0.9*n)`;
- no-alarm paths define median and p90 spell duration as `0`;
- descriptive bootstrap intervals use 2.5% / 97.5% percentiles with median and never control gates;
- the fast 15-subset product identity and prefix-moment rolling OLS must numerically match explicit reference implementations in synthetic tests.

## Frozen hard gates

A later one-shot result can receive `PASS_FUTURE_ONLY_PULSE_VALIDATION_ELIGIBLE` only if every preregistered point-estimate gate passes:

- primary TRUE PRE14_7 event pulse hit >= 0.50;
- primary CONTINUATION PRE14_0 false pulse <= 0.34;
- primary TRUE macro-episode hit >= 0.60;
- primary CONTINUATION macro-episode false pulse <= 0.50;
- severe TRUE PRE14_7 pulse hit >= 0.57;
- at least four primary TRUE PRE21_0 pulse onsets;
- median qualifying onset lead 7..21 sessions;
- raw alarm occupancy <= 0.175;
- median raw-alarm spell <= 7 sessions;
- empirical-nearest-rank p90 raw-alarm spell <= 14 sessions;
- label-blind truncated ARL0 >= 365;
- no post-output design, threshold, null, seed, scale, subset, gate or pulse-rule change.

Failure is immutable. A PASS only permits a new separately preregistered future-only validation stage and does not create dynamic-gross eligibility.

## Current lifecycle boundary

Implementation source and `RUN_INTERFACE.json` may now exist. Generated execution evidence still must **not** exist on this pre-result branch:

```text
PREDICTOR_PATH.json
CALIBRATION_LOCK
CALIBRATION_LOCK.json
PRIMARY_RESULT.json
EXECUTION.json
RUN_ONCE.marker
RESULT.md
```

`actual_variants_evaluated` remains `0`. Threshold, pulse dates and historical outcome metrics remain nonexistent.

## Authority

This ID defines no portfolio response. Canonical BRRK-0011, Phase 6, leverage/short authority, signing, order submission and production authorization remain unchanged.

The next boundary is a fully green pre-result implementation SHA. Only after that boundary is established may the frozen predictor-materialization and label-blind calibration stages execute. Event taxonomy remains unavailable until a successful `CALIBRATION_LOCK` exists and validates.
