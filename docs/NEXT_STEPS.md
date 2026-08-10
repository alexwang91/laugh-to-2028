# BRRK Next Steps

Last updated: 2026-08-10

## Current instruction

**Phase-6 ARM remains active, automatic and independent. `BRRK-EXHAUSTION-PULSE-0046` is now formally preregistered on `main` by PR #163 / squash `48a140a1d58cba859d537e7dee0ad399c541527a`. PR #164 is implementation-only: establish a fully green pre-result code boundary without generating the predictor artifact, fitting the historical VAR, selecting a threshold, loading the event taxonomy, or releasing any 0046 result. Only after the implementation PR is merged may a separate controlled execution stage materialize S1-S4, perform label-blind calibration, write/hash-bind `CALIBRATION_LOCK`, and then permit exactly-once historical evaluation.**

## Immediate live state

```text
Phase 6 ARM                          ACTIVE FUTURE-ONLY OBSERVATION
Phase 6 ARM marker                   cbd58adb05187651ca72d67900a0ccbbd3e83b1e
Phase 6 schedule                     00:00 UTC
Phase 6 genuine scheduled decisions  1 / >=10
Phase 6 emergency drills             0 / >=1
critical reconciliation errors       0 observed
unexplained target drift             0 observed
schedule failures                    0 observed
Phase 6 elapsed result               MEASUREMENT_INCONCLUSIVE_TIME_DEPENDENT
Phase 7                              MONITOR_ONLY / LAUNCH BLOCKED
production gross cap                 1.0
production_authorized_components     []
production_authorized                false
signature_authorized                 false
order_submission_authorized          false

0044                                 PASS_TRIGGER_STAGE_ELIGIBLE / CLOSED / IMMUTABLE
0045                                 FAIL_NO_DYNAMIC_GROSS_STAGE_ELIGIBILITY / CLOSED / IMMUTABLE
0046 exact design                    MERGED / FROZEN / PR #162
0046 formal preregistration          MERGED / PR #163 / 48a140a1d58cba859d537e7dee0ad399c541527a
0046 implementation                 PR #164 CANDIDATE / IMPLEMENTED_PRE_RESULT_NOT_RUN
0046 declared variants              1
0046 actual variants evaluated      0
0046 PREDICTOR_PATH                 NOT CREATED
0046 historical VAR fit             NOT RUN
0046 CALIBRATION_LOCK               NOT CREATED
0046 threshold                      NONE
0046 event taxonomy loaded          FALSE
0046 historical result              NONE
0046 portfolio economics            FORBIDDEN
0046 dynamic-gross eligibility      FALSE
```

## Phase-6 accounting remains independent

The first genuine scheduled decision is still the existing durable evidence for `2026-08-10T00:00:00Z`, GitHub Actions run `31346545269`, attempt 1. Its evidence and separate receipt remain authoritative; the repository ledger is only an accounting index.

```text
evidence artifact id       9047515515
evidence digest            sha256:35324a527eec2e10c44ad8ccd124c0074a3b23f64be4352651037b4209a811a3
receipt artifact id        9047516114
receipt digest             sha256:f2299a0dca868c3fcedc4cafd561104930f8b8f52e8ba71d88e0f423d4461380
target reference parity    PASS
max target-weight drift    0.0
offline reference L1 drift 0.0
shadow alerts              []
```

Never backfill a missed Phase-6 timestamp. Manual dispatch, replay, rerun and duplicate timestamp remain non-crediting. One separately evidenced emergency drill is still required before Phase-6 closeout.

Frozen Phase-6 acceptance remains:

```text
minimum elapsed calendar days       14
minimum genuine scheduled decisions 10
minimum emergency drills             1
critical reconciliation errors       0
unexplained target drift              0
schedule failures                     0
```

## Immutable parent research

`BRRK-EXHAUSTION-STATE-0044` remains a closed state-discrimination PASS. The frozen CORE4 result retained macro-episode discrimination, including primary PRE14_7 cross-episode AUC `0.750`; S2 was strongest exposed axis and S5 volume confirmation remained negative evidence.

`BRRK-EXHAUSTION-TRIGGER-0045` remains a closed trigger FAIL. Binding negatives include:

```text
primary TRUE PRE14_7 WATCH/RISK     3 / 9
primary TRUE episode hit            2 / 5
severe TRUE PRE14_7                 3 / 7
severe PRE7_POST3 RISK              2 / 7
qualifying TRUE PRE21_0 onsets      0
WATCH+RISK occupancy                ~34.38%
```

No 0044/0045 rerun, threshold rescue, S2-only rescue, state-machine rescue or dynamic-gross stage is authorized.

## 0046 frozen contract

The exact design is frozen in:

```text
research/governance/BRRK_EXHAUSTION_PULSE_0046_DESIGN_FREEZE_2026-08-10.md
```

The formal preregistration is:

```text
research/brrk_exhaustion_pulse_0046/PREREGISTRATION.json
research/brrk_exhaustion_pulse_0046/DATASET_DECLARATION.json
```

Primary detector remains exactly:

```text
S1/S2/S3/S4 exactly from 0044
 -> 64-session causal pre-change OLS baseline
 -> one-sided positive slope working GLR per axis
 -> equal mixture over all 15 non-empty axis subsets
 -> multiscale maximum over change ages 3..32
 -> label-blind VAR(1) null
 -> intact 4D residual-vector circular moving blocks, block=7
 -> 5,000 null paths / seed 460046
 -> burn-in 256 / post-burn path 1,460
 -> truncated ARL0 target >=365
 -> 60-iteration deterministic bisection
 -> CALIBRATION_LOCK before taxonomy access
 -> Transition Pulse = threshold upcrossing only
```

There is one candidate only. No Kalman/state-space smoother, raw-difference CUSUM, BOCPD, HMM, classifier, S2-only rescue, CORE4 duplication, cooldown, refractory period, persistence vote or hysteresis rescue exists under this ID.

Frozen hard gates remain:

```text
primary TRUE PRE14_7 event pulse hit          >=0.50
primary CONT PRE14_0 false pulse              <=0.34
primary TRUE episode pulse hit                >=0.60
primary CONT episode false pulse              <=0.50
severe TRUE PRE14_7 pulse hit                 >=0.57
qualifying primary TRUE PRE21_0 onsets        >=4
median qualifying onset lead                  7..21 sessions
raw alarm occupancy                           <=0.175
median raw-alarm spell                        <=7 sessions
empirical-nearest-rank p90 alarm spell        <=14 sessions
label-blind truncated ARL0                    >=365
```

A PASS can only create eligibility for a separately preregistered future-only pulse-validation stage. It cannot create dynamic-gross eligibility.

## PR #164 pre-result implementation

The implementation is deliberately split by an information firewall:

```text
prepare-predictors
  raw causal inputs -> create-only PREDICTOR_PATH.json
  payload = timestamp + S1/S2/S3/S4 only

calibrate
  input = PREDICTOR_PATH only
  no raw market/NAV loader
  no taxonomy/event/episode/window import
  -> create-only CALIBRATION_LOCK.json

evaluate
  validate lock hash + code SHA + predictor binding + ARL0 first
  only then dynamically import evaluation/taxonomy module
  -> exactly-once PRIMARY_RESULT
```

The implementation freezes these previously operationally unspecified details **before any calibration output**:

1. synthetic stopping time is 1-based from synthetic path session 1; initial detector warm-up cannot cross but remains on the ARL clock;
2. if several pulses occur in PRE21_0, the earliest pulse controls onset lead, matching 0045 scan direction;
3. alarm-spell p90 uses empirical nearest rank `ceil(0.9*n)`;
4. no alarm spells means median/p90 spell duration `0`;
5. descriptive bootstrap intervals use 2.5% / 97.5% percentiles plus median and never control hard gates;
6. daily block-bootstrap spell statistics are measured on the concatenated circular block-bootstrap path;
7. optimized rolling OLS and subset-mixture algebra are accepted only because standing CI verifies equality to explicit reference implementations.

## Pre-result falsification completed on PR #164

A standing-CI bridge under `research/governance/` makes the immutable governance workflow execute the 0046 synthetic suites. This avoids modifying `.github/workflows/**` merely to obtain a green check.

On head `6c6c7ef54a661ceaf57a41b2d761c9479ac839da`, `Research governance core` ran:

```text
python -m unittest discover -s research/governance -p 'test_*.py'
Ran 162 tests
OK
```

The 0046 suites included:

- prefix-moment 64-session OLS versus explicit `numpy.linalg.lstsq`;
- fast equal-15-subset identity versus explicit subset enumeration;
- linear/no-acceleration, positive deterioration, negative/improving one-sided behavior and smallest-age tie semantics;
- first-valid-session no-pulse rule and empirical-nearest-rank spell p90;
- calibration source prohibition on raw market/NAV and taxonomy/event/window imports;
- exact S1-S4 feature binding to immutable 0044 constants;
- `validate_lock` before dynamic evaluation import;
- deterministic VAR/bootstrap toy checks and stopping-time clock;
- pre-result zero-authority lifecycle and absence of generated predictor/lock/result evidence.

The same run also passed future-policy enforcement, final no-drift, deterministic audit and Phase-6 live-observation safety. These are implementation validations only; they are not historical 0046 evidence.

## Production/security boundary

Nothing in PR #164 changes:

```text
canonical directional core          BRRK-0011
long universe                       BTC / ETH / SOL / BNB
XRP                                 feature-only
primary venue                       Hyperliquid
decision boundary                   00:00 UTC
production gross cap                1.0
production_authorized_components    []
production_authorized               false
signature_authorized                false
order_submission_authorized         false
first real short authority          NONE
```

## Exact next steps

1. Add/update the final `CURRENT_STATE` handoff for PR #164 and require PR handoff governance to pass.
2. Re-run all standing checks after the handoff; require Research governance core, future-policy, no-drift, P3.2 parity, Phase-0 baseline, Phase-6 shadow safety and continuity to remain green.
3. Final-audit PR #164: only 0046 implementation/tests, the standing-CI test bridge and status handoff may differ; generated predictor/lock/result evidence must remain absent.
4. Merge PR #164 as **implementation-only** and verify live `main` moved to the resulting SHA.
5. Treat that merged fully green SHA as the pre-result code boundary. Do not change detector, calibration, hard gates, seeds, pulse semantics or implementation clarifications afterward.
6. Create a separate controlled execution branch from that exact SHA.
7. Materialize the create-only predictor artifact and verify it contains only timestamps plus frozen S1-S4.
8. Run label-blind calibration once. If VAR spectral radius is `>=1`, close 0046 as `FAIL_NULL_MODEL_NONSTATIONARY` before labels. Otherwise write/hash-bind `CALIBRATION_LOCK` with the threshold and calibration provenance.
9. Only after the lock validates may 0046 load the immutable 0043/0044 taxonomy and execute the historical evaluation exactly once.
10. Retain PASS or FAIL without same-ID rescue. Do not map dynamic gross, run portfolio economics, alter canonical BRRK, alter Phase 6, or confer any production/security authority.
