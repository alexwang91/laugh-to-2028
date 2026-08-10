# BRRK Current State

Last updated: 2026-08-10
Last merged research-governance PR: **#163**
Current working branch: `research/brrk-exhaustion-pulse-0046-runonce`
Authoritative baseline main at branch creation: `48a140a1d58cba859d537e7dee0ad399c541527a`
Latest merged research execution PR: **#159**
Current implementation PR: **#164**

Status: **authoritative current-state update candidate**

## Executive state

```text
Phase 0-3                         COMPLETE / MERGED
Phase 4 leverage research         FAIL_STOP / NO_PROMOTION
P5.5                              COMPLETE / IMMUTABLE / NO_PROMOTION / FAIL_STOP
F27 idle-cash measurement         R2 AUTHORITATIVE / R1 SUPERSEDED-PRESERVED
F7 metrics convergence            PARTIAL
Phase 6 ARM                       ACTIVE FUTURE-ONLY OBSERVATION
Phase 6 ARM marker                cbd58adb05187651ca72d67900a0ccbbd3e83b1e
Phase 6 daily schedule            00:00 UTC
Phase 6 genuine scheduled credit  1 / >=10
Phase 6 emergency drills          0 / >=1
Phase 6 live elapsed evidence     MEASUREMENT_INCONCLUSIVE_TIME_DEPENDENT
BRRK opportunity-cost audit 0042  COMPLETE DIAGNOSTIC / NO PROMOTION AUTHORITY
BRRK-WINNER-0001                  ONE-SHOT PASS / CLOSED
BRRK-WINNER-ROBUSTNESS-0002       ONE-SHOT PASS / FUTURE-ONLY VALIDATION ELIGIBLE / CLOSED
BRRK exhaustion event study 0043 COMPLETE DIAGNOSTIC / 7-14D SIGNAL FEASIBLE / TRIGGER NOT READY
BRRK exhaustion state 0044       PASS / TRIGGER STAGE ELIGIBLE / CLOSED
BRRK exhaustion trigger 0045     FAIL / NO DYNAMIC-GROSS ELIGIBILITY / CLOSED
BRRK exhaustion pulse 0046       IMPLEMENTED_PRE_RESULT_NOT_RUN / PR #164 CANDIDATE
Program timeline dashboard        READ-ONLY V5 / PROFESSIONAL FUND TERMINAL
Phase 7                           MONITOR_ONLY / LAUNCH BLOCKED
Phase 8                           TRIGGER ABSENT / NOT RUN
Production                        NO_CHANGE
```

## Phase 6 remains frozen and independent

The canonical BRRK-0011 strategy remains unchanged while future-only Phase-6 observation continues. Genuine scheduled credit requires a real `schedule` event plus create-only evidence and a separate hash-bound receipt. Pull-request runs, reruns, replay and manual dispatch do not create scheduled-decision credit.

Frozen acceptance remains:

```text
minimum elapsed calendar days       14
minimum genuine scheduled decisions 10
minimum emergency drills             1
critical reconciliation errors       0
unexplained target drift              0
schedule failures                     0
production_authorized              false
signature_authorized               false
order_submission_authorized        false
```

The first rule-eligible scheduled decision remains `2026-08-10T00:00:00Z`, GitHub Actions run `31346545269`, attempt 1.

```text
observed_at                        2026-08-10T01:14:21Z
workflow SHA                       405d2f75221ba97734973dd9bee2df04c9ecbcd2
evidence artifact id              9047515515
evidence artifact digest          sha256:35324a527eec2e10c44ad8ccd124c0074a3b23f64be4352651037b4209a811a3
receipt artifact id               9047516114
receipt artifact digest           sha256:f2299a0dca868c3fcedc4cafd561104930f8b8f52e8ba71d88e0f423d4461380
evidence object digest            6e0f090101c37724c1b2eaccea77358028a4f3f72dd9e397e3526211145377d5
input provenance digest           813ab7ed64b2c50504371c698c7f100e227851f40c28c0dde6e9415b6694307b
shadow record digest              23b4eba438f66b38fdfb0af1661eddfe44d0139424d709a4e3ced3547dff1585
shadow status                     SHADOW_COMPUTED_NO_AUTHORITY
shadow alerts                     []
target reference parity           PASS
target gross absolute difference  0.0
max target-weight abs difference  0.0
offline reference L1 drift        0.0
```

Current Phase-6 progress:

```text
genuine scheduled decisions          1 / >=10
emergency drills                     0 / >=1
distinct credited decision dates     1
critical reconciliation errors       0 observed
unexplained target drift              0 observed
schedule failures                     0 observed
elapsed requirement                  NOT MET
live acceptance                      MEASUREMENT_INCONCLUSIVE_TIME_DEPENDENT
```

PR #161 merged the fail-closed accounting index at `c1308fa20e85de69cfa0acf3decb56619d74df58`. `research/governance/phase6_observation_ledger.json` remains an accounting index only; the durable Actions evidence plus separate receipt remain the authority. Never backfill a missed timestamp or count replay/manual dispatch as scheduled credit.

## BRRK Opportunity-Cost Audit 0042 — immutable diagnostic

PR #149 merged the deterministic audit at `405d2f75221ba97734973dd9bee2df04c9ecbcd2`.

```text
V1 CAGR                              61.3150%
BRRK CAGR                            65.1702%
BRRK minus V1 CAGR                   +3.8551 pp
V1 max drawdown                      -37.6349%
BRRK max drawdown                    -33.7151%
BRRK MDD improvement                 +3.9198 pp
BRRK top-20 V1 growth-day capture    ~100%
alt-active days                      590
BTC >= 50% of gross on alt-active    70.1695%
V1 target-change median gap          2 days
BRRK target-change median gap        2 days
BRRK maximum target-change gap       120 days
```

The defensive scaler is not the first optimization target because it improved historical CAGR and MDD while preserving right-tail growth days. Portfolio construction remains the stronger observable rigidity.

## BRRK-WINNER lineage — closed development evidence

`BRRK-WINNER-0001` remains a closed one-shot development PASS:

```text
canonical CAGR                         65.3057%
candidate CAGR                         69.6917%
CAGR delta                             +4.3860 pp
canonical max drawdown                 -33.5292%
candidate max drawdown                 -33.4499%
canonical Calmar                       1.9477
candidate Calmar                       2.0835
best-20 log-growth capture             103.5595%
turnover ratio                         1.1229x
result_status                          PASS_ROBUSTNESS_STAGE_ELIGIBLE
```

`BRRK-WINNER-ROBUSTNESS-0002` also remains closed. The unique robustness run was Actions `31374176442`, attempt 1. T1 and T3 temporal CAGR gates passed; T2 was negative evidence with candidate CAGR delta about `-1.7365 pp`. Full-horizon 10 bps and 20 bps stress gates passed. Final classification remains:

```text
PASS_FUTURE_ONLY_VALIDATION_STAGE_ELIGIBLE
```

This lineage remains researcher-exposed DEVELOPMENT evidence. It does not alter canonical BRRK or production authority.

## BRRK-EXHAUSTION-EVENT-STUDY-0043 — complete diagnostic

0043 remains closed read-only DEVELOPMENT evidence. The unique workflow run was `31381953131`, artifact `9060216534`.

Primary `-15%` panel:

```text
TRUE_EXHAUSTION / CONTINUATION / AMBIGUOUS     9 / 6 / 1
PRE14_7 total EXHAUSTION_SCORE AUC             0.7333
PRE14_7 F7 BRRK disagreement AUC               0.7556
PRE14_7 F4 volatility/downside AUC             0.7111
PRE14_7 F1 momentum decay AUC                  0.6889
PRE14_7 F2 price structure AUC                 0.6889
```

Severe `-20%` PRE14_7 total-score AUC remained `0.8571`. The simple frozen absolute threshold caught only `2/9` primary true events despite `0/6` continuation false triggers. The 48 oriented features had effective rank about `7.2046`; redundancy remains binding negative evidence. No 0043 threshold rescue or portfolio translation is allowed.

## BRRK-EXHAUSTION-STATE-0044 — PASS, closed

0044 remains immutable `PASS_TRIGGER_STAGE_ELIGIBLE`. The unique valid result run was `31388103016`, artifact `9062525981`.

```text
usable macro episodes                         7
TRUE / CONTINUATION episode coverage        5 / 4
15% PRE14_7 cross-episode AUC              0.750
15% PRE14_7 event AUC                      0.778
20% PRE14_7 cross-episode AUC              0.750
LOEO minimum / median AUC                  0.654 / 0.739
```

S2 trend disagreement remained the strongest exposed state axis. S5 volume confirmation remained negative evidence: adding it reduced CORE4 discrimination and S5 alone was approximately chance in primary PRE14_7. `RUN_ONCE.marker` is permanent. No 0044 rerun, reweighting, pruning, threshold search or gross mapping is allowed.

## BRRK-EXHAUSTION-TRIGGER-0045 — FAIL, closed

0045 remains immutable `FAIL_NO_DYNAMIC_GROSS_STAGE_ELIGIBILITY`. The unique valid result run was `31391109057`, artifact `9063704951`.

```text
primary TRUE PRE14_7 WATCH/RISK            3 / 9 = 33.3% FAIL
primary CONT PRE14_0 false WATCH/RISK       0 / 6 = 0.0%  PASS
primary TRUE episode hit                    2 / 5 = 40.0% FAIL
primary CONT episode false                  0 / 5 = 0.0%  PASS
severe TRUE PRE14_7 WATCH/RISK              3 / 7 = 42.9% FAIL
severe TRUE PRE7_POST3 RISK                 2 / 7 = 28.6% FAIL
qualifying TRUE PRE21_0 transition onsets             0    FAIL
WATCH+RISK occupancy                       ~34.38%
```

The candidate was specific but too insensitive and too sticky. Zero PRE21_0 onsets are binding negative evidence. 0045 cannot be rescued with another threshold, persistence rule, S2-only variant, CORE4 weighting or hysteresis under the same ID. Dynamic gross is not eligible.

## BRRK-EXHAUSTION-PULSE-0046 — preregistered and implemented pre-result

### Formal boundaries already merged

PR #162 merged the exact mathematical design at:

```text
b25faa350abf034af6abf961a9ec12e8834296fc
```

PR #163 then squash-merged the formal `PROGRAM_GOVERNED_V1` preregistration at:

```text
48a140a1d58cba859d537e7dee0ad399c541527a
```

The preregistered DEVELOPMENT slice ends `2026-08-02`. There is exactly one declared candidate and zero evaluated variants.

### Frozen detector

```text
S1 / S2 / S3 / S4 exactly from 0044
    -> 64-session causal pre-change OLS baseline
    -> one-sided positive slope working GLR per axis
    -> equal mixture over all 15 non-empty subsets
    -> maximum over change ages 3..32
    -> label-blind VAR(1) null
    -> intact 4D circular residual-vector bootstrap, block=7
    -> 5,000 paths / seed 460046 / burn-in 256 / path 1,460
    -> threshold for truncated ARL0 >=365
    -> 60-iteration deterministic bisection
    -> CALIBRATION_LOCK before taxonomy access
    -> Transition Pulse = threshold upcrossing only
```

`CORE4 + S2 + S3 + S4` remains rejected because CORE4 already contains all four axes. There is no extra Kalman/local-linear smoother. BOCPD, CUSUM, HMM, supervised classifier, S2-only rescue, cooldown, refractory period, persistence vote and hysteresis remain excluded.

### Frozen hard gates

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

A PASS can only create `PASS_FUTURE_ONLY_PULSE_VALIDATION_ELIGIBLE`. It does not create dynamic-gross eligibility.

### PR #164 implementation firewall

PR #164 currently implements the frozen design without executing it. Runtime is split:

```text
prepare-predictors
  raw causal inputs -> create-only PREDICTOR_PATH.json
  only timestamp + frozen S1/S2/S3/S4 leave this stage

calibrate
  reads PREDICTOR_PATH only
  calibration.py imports no raw market/NAV loader and no taxonomy/event/window code
  -> create-only CALIBRATION_LOCK.json

evaluate
  validate lock payload hash + code SHA + predictor binding + ARL0 first
  only then dynamically import evaluation/taxonomy code
  -> exactly-once PRIMARY_RESULT
```

The following implementation semantics are frozen **before any calibration output**:

1. null stopping time is 1-based from synthetic session 1; detector warm-up remains on the ARL clock;
2. earliest PRE21_0 pulse controls onset lead if more than one pulse occurs;
3. spell p90 uses empirical nearest rank `ceil(0.9*n)`;
4. zero alarm spells imply median/p90 `0`;
5. descriptive bootstrap intervals use 2.5% / 97.5% percentiles plus median and are never gating;
6. daily block-bootstrap spell statistics use the concatenated circular resampled path;
7. prefix-moment OLS and subset-product implementations must equal explicit reference calculations.

### Pre-result falsification on PR #164

The standing governance workflow originally did not discover tests under the formal 0046 path. Treating the initial green core as detector validation was therefore rejected. A test-only bridge was added at:

```text
research/governance/test_brrk_exhaustion_pulse_0046_implementation.py
```

It changes no governance policy or workflow. It makes the existing immutable discovery command execute the 0046 synthetic suites.

On PR #164 head `6c6c7ef54a661ceaf57a41b2d761c9479ac839da`, Actions run `31415282770` executed:

```text
python -m unittest discover -s research/governance -p 'test_*.py'
Ran 162 tests in 0.534s
OK
```

The 0046 bridge verified:

- rolling prefix-moment OLS equals explicit 64-session `numpy.linalg.lstsq` reference fits;
- fast equal-15-subset mixture equals explicit enumeration;
- linear/no-acceleration score, positive deterioration, negative/improving one-sided behavior and smallest-age tie semantics;
- first-valid-session cannot pulse and spell p90 nearest-rank semantics;
- calibration source contains no raw market/NAV or event-taxonomy/window import path;
- predictor materializer does not call event classification or macro-episode assignment;
- S1-S4 feature names equal immutable 0044 constants;
- `calibration.validate_lock` precedes dynamic evaluation-module import;
- frozen calibration constants, deterministic bootstrap toy behavior and stopping-time clock;
- zero-authority interface and absence of generated predictor/lock/result evidence.

The same run also passed future research enforcement, final no-drift and Phase-6 live-observation safety. These checks establish implementation integrity only. They do **not** create historical 0046 evidence.

Current 0046 lifecycle on PR #164 branch:

```text
exact design                         MERGED / IMMUTABLE / PR #162
formal preregistration               MERGED / PR #163 / 48a140a...
development exposure                 MERGED / RESEARCHER_EXPOSED / through 2026-08-02
declared candidates                  1
actual variants evaluated            0
runner                               IMPLEMENTED PRE-RESULT
RUN_INTERFACE                        IMPLEMENTED_PRE_RESULT_NOT_RUN
PREDICTOR_PATH.json                  NOT CREATED
historical VAR fit                   NOT RUN
CALIBRATION_LOCK                     NOT CREATED
calibration threshold                NONE
event taxonomy loaded by 0046        FALSE
PRIMARY_RESULT                       NONE
EXECUTION                            NONE
RUN_ONCE.marker                      NONE
portfolio economics                  FORBIDDEN
future-only pulse-validation eligible FALSE
dynamic-gross eligibility            FALSE
canonical BRRK change                NONE
Phase-6 change                       NONE
production authorization             NO_CHANGE / false
```

## Dashboard

Public read-only dashboard remains:

```text
https://laugh-to-2028.vercel.app/
```

## Canonical production / security authority

```text
directional core                  BRRK-0011
long universe                     BTC / ETH / SOL / BNB
XRP                               feature-only
primary venue                     Hyperliquid
decision boundary                 00:00 UTC
production gross cap              1.0
production_authorized_components = []
production_authorized             false
signature_authorized             false
order_submission_authorized      false
first real short authority        NONE
```

0046 design, preregistration and implementation do not change any of these fields.

## Current drift assessment

`DRIFT_0`.

PR #164 changes only:

- the governed `research/brrk_exhaustion_pulse_0046/**` implementation/interface/tests/README;
- one `research/governance/**` test bridge that executes the formal 0046 synthetic suites through the standing CI command;
- existing cross-chat status handoff files.

It does not change `.github/workflows/**`, `execution/**`, the central research/dataset registries, formal 0046 preregistration mathematics, canonical BRRK, Phase-6 collector/schedule/evidence, leverage/shorting, signing, order submission or production authority. It contains no generated predictor artifact, calibration lock or result.

## Exact next task

1. Re-run PR #164 after this final handoff and require `Research governance core`, future-policy, final no-drift, P3.2 parity, Phase-0 baseline, Phase-6 shadow safety and PR handoff governance to remain green.
2. Final-audit PR #164 for zero generated evidence: `PREDICTOR_PATH.json`, `CALIBRATION_LOCK*`, `PRIMARY_RESULT.json`, `EXECUTION.json`, `RUN_ONCE.marker` and `RESULT.md` must all remain absent.
3. Merge PR #164 as **implementation-only** and immediately verify live `main` moved to the merge SHA.
4. Treat the resulting merged fully green SHA as the 0046 pre-result code boundary. Do not change detector mathematics, null calibration, seeds, gates, pulse semantics or the implementation clarifications afterward.
5. Create a separate controlled execution branch from that exact SHA.
6. Materialize the create-only timestamp+S1-S4 predictor artifact and verify its payload/digest.
7. Run label-blind calibration exactly once. If VAR spectral radius is `>=1`, close 0046 `FAIL_NULL_MODEL_NONSTATIONARY` before any label access. Otherwise write and hash-bind `CALIBRATION_LOCK` with threshold, code SHA and predictor/null provenance.
8. Validate the lock before importing the evaluation module. Only then may the immutable 0043/0044 event taxonomy and macro episodes be loaded.
9. Execute the frozen historical evaluation exactly once; retain PASS, FAIL or INSUFFICIENT without same-ID rescue.
10. Do not map dynamic gross, evaluate portfolio economics, alter canonical BRRK, alter Phase 6, launch Phase 7, sign or submit orders, or confer production authority from 0046 DEVELOPMENT evidence.
