# BRRK-EXHAUSTION-PULSE-0046

Status: **PREREGISTERED_NOT_RUN**

This directory is the formal `PROGRAM_GOVERNED_V1` preregistration for the single result-informed transition-pulse candidate frozen after `BRRK-EXHAUSTION-STATE-0044` PASS and `BRRK-EXHAUSTION-TRIGGER-0045` FAIL.

The exact mathematical source is `research/governance/BRRK_EXHAUSTION_PULSE_0046_DESIGN_FREEZE_2026-08-10.md`, merged in PR #162. This preregistration does not reopen design selection.

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
  -> CALIBRATION_LOCK before any event taxonomy may be loaded
  -> Transition Pulse = raw-alarm threshold upcrossing only
```

There is no Kalman/state-space smoother, raw-difference CUSUM, BOCPD, HMM, supervised classifier, S2-only rule, CORE4 duplication, persistence vote, cooldown, refractory period, recovery threshold or hysteresis state machine under this research ID.

## Information firewall

Calibration may read only timestamps and the exact frozen S1-S4 predictor path through `2026-08-02`. It may not read event labels, event dates, macro-episode IDs, downside-barrier dates or evaluation windows.

A later implementation must create a hash-bound `CALIBRATION_LOCK` containing the selected threshold and frozen calibration provenance before event taxonomy loading is possible. If fitted VAR(1) spectral radius is at least 1, the ID closes as `FAIL_NULL_MODEL_NONSTATIONARY` before outcome evaluation.

The calibration history is already researcher-exposed DEVELOPMENT. Label blindness does not make earlier history temporally unseen OOS evidence.

## Frozen hard gates

A later one-shot result can receive `PASS_FUTURE_ONLY_PULSE_VALIDATION_ELIGIBLE` only if every preregistered gate passes, including:

- primary TRUE PRE14_7 event pulse hit >= 0.50;
- primary CONTINUATION PRE14_0 false pulse <= 0.34;
- primary TRUE macro-episode hit >= 0.60;
- primary CONTINUATION macro-episode false pulse <= 0.50;
- severe TRUE PRE14_7 pulse hit >= 0.57;
- at least four primary TRUE PRE21_0 pulse onsets;
- median qualifying onset lead 7..21 sessions;
- raw alarm occupancy <= 0.175;
- median raw-alarm spell <= 7 sessions;
- 90th percentile raw-alarm spell <= 14 sessions;
- label-blind truncated ARL0 >= 365;
- no post-output design, threshold, null, seed, scale, subset, gate or pulse-rule change.

Failure of any hard gate closes the ID as `FAIL_NO_FUTURE_ONLY_PULSE_VALIDATION_ELIGIBILITY`. A PASS only permits a new separately preregistered future-only validation stage.

## Current lifecycle boundary

At this preregistration stage the following files must **not** exist:

```text
run_once.py
RUN_INTERFACE.json
CALIBRATION_LOCK
CALIBRATION_LOCK.json
PRIMARY_RESULT.json
EXECUTION.json
RUN_ONCE.marker
RESULT.md
```

`actual_variants_evaluated` remains `0`. No 0046 calibration, threshold, pulse dates or historical outcome metrics exist yet.

## Authority

This research ID defines no portfolio response and creates no dynamic-gross eligibility. Canonical BRRK-0011, Phase 6, execution configuration, leverage/short authority, signing, order submission and production authorization remain unchanged.

The exact next step after this preregistration is merged and fully green is a separate implementation-only branch. That branch must reproduce this contract exactly and establish a fully green pre-result implementation SHA before any calibration or result-bearing execution is allowed.
