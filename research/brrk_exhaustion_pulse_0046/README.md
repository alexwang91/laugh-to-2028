# BRRK-EXHAUSTION-PULSE-0046

Status: **FAIL_NO_FUTURE_ONLY_PULSE_VALIDATION_ELIGIBILITY / CLOSED**

PR #163 formally preregistered this single `PROGRAM_GOVERNED_V1` result-informed transition-pulse candidate at merge `48a140a1d58cba859d537e7dee0ad399c541527a`. The exact mathematical design remains the PR #162 freeze in `research/governance/BRRK_EXHAUSTION_PULSE_0046_DESIGN_FREEZE_2026-08-10.md`.

The frozen candidate was implemented without reopening design selection. One first execution reached a valid label-blind calibration lock but failed during historical evaluation before any research result or artifact was released. PR #165 repaired only the already-frozen 0045-compatible session-window semantics. The subsequent controlled execution produced the single valid 0046 historical result and permanently closed this ID.

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

The implementation was split into three runtime stages:

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

`calibration.py` receives only timestamps and the frozen S1-S4 predictor artifact. It cannot call candidate detection, event classification, macro-episode assignment or outcome windows. `run_once.evaluate()` validates the lock before the evaluation module import.

## Pre-result implementation clarifications

These semantics were frozen before any 0046 calibration and remain immutable:

- synthetic `T_b` is 1-based from synthetic path session 1; detector warm-up cannot cross but remains on the ARL clock;
- if several pulses occur inside PRE21_0, the earliest pulse controls onset lead, matching 0045 scan direction;
- raw-alarm spell p90 uses empirical nearest rank `ceil(0.9*n)`;
- no-alarm paths define median and p90 spell duration as `0`;
- descriptive bootstrap intervals use 2.5% / 97.5% percentiles with median and never control gates;
- the fast 15-subset product identity and prefix-moment rolling OLS must numerically match explicit reference implementations in synthetic tests.

## Frozen hard gates

`PASS_FUTURE_ONLY_PULSE_VALIDATION_ELIGIBLE` required every preregistered point-estimate gate to pass:

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

Failure is immutable. A PASS would only have permitted a new separately preregistered future-only validation stage and would not have created dynamic-gross eligibility.

## Immutable result

The single valid historical result is GitHub Actions run `31419044159`, attempt 1, artifact `9074623455`. The immutable artifact binds the result to:

```text
result status                  FAIL_NO_FUTURE_ONLY_PULSE_VALIDATION_ELIGIBILITY
primary TRUE PRE14_7           0 / 9
primary TRUE episode PRE14_7   0 / 5
severe TRUE PRE14_7            0 / 7
qualifying PRE21_0 onsets      0
continuation false PRE14_0     0 / 6
eligible detector sessions     1026
raw-alarm sessions             19
raw-alarm occupancy            1.8518519%
raw-alarm spells               1
spell duration                 19 sessions
Transition Pulse               2026-06-03
```

The occupancy gate passed, but both preregistered spell-duration anti-stickiness gates failed because the single alarm spell lasted 19 sessions. The TRUE_EXHAUSTION sensitivity/timing gates also failed. The formal 0046 classification therefore remains FAIL.

PR #166 correctly persisted the FAIL disposition but its hand-built compact closeout summary contained artifact-derived transcription errors. The authoritative artifact evidence is reconciled by the later evidence-correction PR; this is not a rerun, retune, rescue or reclassification.

## Closed lifecycle boundary

`RUN_INTERFACE.json` remains preserved as the frozen **pre-result execution contract**; its pre-result status fields are historical contract evidence and are not rewritten after observing the result. Permanent post-result evidence is held separately in:

```text
PRIMARY_RESULT.json
EXECUTION.json
RUN_ONCE.marker
RESULT.md
```

Generated `PREDICTOR_PATH.json` and `CALIBRATION_LOCK.json` remain artifact evidence and are not committed as mutable repository runtime inputs.

Same-ID rerun, retuning and rescue are forbidden. Any future use of the exhaustion information for portfolio economics requires a new research ID and fresh preregistration; it cannot alter or reinterpret the 0046 result.

## Authority

0046 defines no portfolio response. Canonical BRRK-0011, Phase 6, leverage/short authority, signing, order submission and production authorization remain unchanged. `production_authorized=false`, `signature_authorized=false`, and `order_submission_authorized=false`.
