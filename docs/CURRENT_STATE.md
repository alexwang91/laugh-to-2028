# BRRK Current State

Last updated: 2026-08-10
Last merged governance PR: **#161**
Current working branch: `research/brrk-exhaustion-pulse-0046-prereg`
Authoritative baseline main at branch creation: `b25faa350abf034af6abf961a9ec12e8834296fc`
Latest merged research execution PR: **#159**

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
BRRK exhaustion pulse 0046       PREREGISTERED_NOT_RUN / PR #163 CANDIDATE / NO RESULT
Program timeline dashboard        READ-ONLY V5 / PROFESSIONAL FUND TERMINAL
Phase 7                           MONITOR_ONLY / LAUNCH BLOCKED
Phase 8                           TRIGGER ABSENT / NOT RUN
Production                        NO_CHANGE
```

## Phase 6 remains frozen and independent

The canonical BRRK-0011 strategy remains unchanged while future-only Phase-6 observation continues. Genuine scheduled credit still requires a real `schedule` event plus create-only evidence and a separate hash-bound receipt. Pull-request runs, reruns, replay and manual dispatch do not create scheduled-decision credit.

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

### First genuine future-only scheduled decision — credited existing durable evidence

The first rule-eligible canonical decision after the ARM marker was `2026-08-10T00:00:00Z`. GitHub Actions run `31346545269`, attempt 1, was a real `event=schedule` run on `main` and completed successfully. The persisted collector metadata records `scheduled_decision_credit_candidate=true`.

Evidence binding independently checked from the existing Actions artifacts:

```text
decision timestamp                 2026-08-10T00:00:00Z
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

The integrated shadow code fails closed and emits alerts for feature-reference mismatch, target-reference mismatch, incomplete data, instrument-identity mismatch, cost-model failure, unexplained state transition, and daily-schedule drift. The persisted observation contains no alerts and exact independent target parity. For this decision the accounting record therefore records zero observed critical reconciliation errors, zero unexplained target drift and zero schedule failures.

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

PR #161 merged the fail-closed accounting index and anti-backfill/anti-manual/anti-duplicate/receipt-binding validation at merge SHA `c1308fa20e85de69cfa0acf3decb56619d74df58`. The repository-side `research/governance/phase6_observation_ledger.json` remains an accounting index only. It cannot create credit. The durable Actions evidence artifact plus separate receipt remain the evidence authority. Manual dispatch, reruns, replay and duplicate timestamps remain non-crediting.

## BRRK Opportunity-Cost Audit 0042 — merged

PR #149 merged deterministic diagnostic audit at `405d2f75221ba97734973dd9bee2df04c9ecbcd2`.

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

Interpretation remains frozen: the defensive scaler is not the first optimization target because it improved both historical CAGR and MDD while preserving V1 top-growth days. The strongest observable rigidity is portfolio construction: BTC remains at least half of gross on about 70% of alt-active days.

## BRRK-WINNER-0001 — closed development PASS

PR #151 merged the exactly-once 40/60 single-alt development candidate. It remains researcher-exposed DEVELOPMENT evidence and must not run again.

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
all frozen hard gates                  PASS
result_status                          PASS_ROBUSTNESS_STAGE_ELIGIBLE
```

No canonical BRRK, Phase 6 or production authority changed.

## BRRK-WINNER-ROBUSTNESS-0002 — closed robustness PASS

PR #152 merged the preregistration. PR #153 executed the frozen robustness panel exactly once after the pre-result green baseline `561ecee69d30253aa398caf51d589cb03b5cfe47`. The unique economic run was GitHub Actions `31374176442`, attempt 1, from trigger SHA `346e26e3906df2416a21a40223e8791c3dfef86a`.

Evidence binding:

```text
artifact id                        9057294415
artifact digest                    sha256:8eb08d0080fae185953ae50a15b05bc9994d6c06da33761bd2125dc89037313c
PRIMARY_RESULT SHA256              cf149308df5aea1a0cc1315432a7effd0e163cda21e6df0b8f39cf0b6ce6fdf0
baseline reproduced before release true
actual variants evaluated          1
retuning performed                 false
```

Frozen 5 bps primary reproduction remained unchanged:

```text
canonical CAGR                     65.3057%
candidate CAGR                     69.6917%
canonical MDD                      -33.5292%
candidate MDD                      -33.4499%
canonical Calmar                   1.9477
candidate Calmar                   2.0835
right-tail capture                 103.5595%
turnover ratio                     1.1229x
```

Temporal robustness at 5 bps:

```text
T1  candidate CAGR delta  +22.5832 pp   PASS
    MDD deterioration       1.7459 pp   PASS
T2  candidate CAGR delta   -1.7365 pp   NEGATIVE EVIDENCE / CAGR GATE FAIL
    MDD deterioration       0.0000 pp   PASS
T3  candidate CAGR delta   +2.3255 pp   PASS
    MDD deterioration      ~0.0000 pp   PASS
aggregate CAGR gate         2 / 3       PASS
```

T2 is retained as negative evidence. It may not be removed, relabeled or used to justify same-ID rescue tuning.

Transaction-cost robustness on the full 1,332-session path:

```text
10 bps  canonical CAGR 63.2574%   candidate 67.3311%   +4.0737 pp
        canonical Calmar 1.8583   candidate 1.9805     PASS
20 bps  canonical CAGR 59.2440%   candidate 62.7142%   +3.4702 pp
        canonical Calmar 1.6910   candidate 1.7888     PASS
        MDD deterioration 0.0244 pp                         PASS
```

All preregistered temporal aggregate, drawdown, 10/20 bps CAGR/Calmar, right-tail, turnover, long-only and gross-cap gates passed. Final classification:

```text
PASS_FUTURE_ONLY_VALIDATION_STAGE_ELIGIBLE
```

This result is still result-informed, researcher-exposed DEVELOPMENT robustness evidence. It is not independent OOS evidence and does not create temporal novelty.

`RUN_ONCE.marker` is permanent. `BRRK-WINNER-ROBUSTNESS-0002` is closed and may not run again. No 45/55, 35/65, 30/70 or other rescue split, alternative temporal partition, transaction-cost grid or hard-gate change is permitted under this ID.

## BRRK-EXHAUSTION-EVENT-STUDY-0043 — complete diagnostic

PR #155 is a read-only DEVELOPMENT diagnostic created after merged PR #153. It mechanically separates genuine local exhaustion tops from ordinary pullbacks / continuation false tops and measures causal 7–14 day deterioration signals. User-provided dates are sanity checks only and do not define labels, thresholds, or score weights.

Unique execution and evidence binding:

```text
workflow run                         31381953131 / attempt 1
artifact id                          9060216534
artifact digest                      sha256:6df40bbe0112082f045cd4da7b461753382c6980a348609a35bed9967f1520c4
full result SHA256                   1ca030e544d6e3391143c9ec47e202f9585ce8a846e0e46be583c31258958b43
source summary SHA256                82579688952e990809a01044378b40cd44ceba84142307686cfa8ae05158c278
historical sessions                  1332
mechanically detected peak candidates 16
portfolio economics executed         false
```

Primary `-15%` competing-barrier panel:

```text
TRUE_EXHAUSTION / CONTINUATION / AMBIGUOUS     9 / 6 / 1
PRE14_7 total EXHAUSTION_SCORE AUC             0.7333
PRE14_7 F7 BRRK disagreement AUC               0.7556
PRE14_7 F4 volatility/downside AUC             0.7111
PRE14_7 F1 momentum decay AUC                  0.6889
PRE14_7 F2 price structure AUC                 0.6889
PRE7_0 F4 volatility/downside AUC              0.8444
PRE7_0 F7 BRRK disagreement AUC                0.8222
```

Severe `-20%` panel strengthens the one-to-two-week signal:

```text
TRUE_EXHAUSTION / CONTINUATION / AMBIGUOUS     7 / 6 / 3
PRE14_7 total EXHAUSTION_SCORE AUC             0.8571
PRE14_7 F7 BRRK disagreement AUC               0.8000
PRE14_7 F2 price structure AUC                 0.7714
PRE14_7 F4 volatility/downside AUC             0.7714
```

Important negative evidence remains binding: the frozen equal-weight absolute threshold is too insensitive. The 80th-percentile / 3-day rule catches only `2/9` primary true events, although it produces `0/6` continuation false triggers; those two hits lead by 10 and 21 days. No threshold is selected or rescued under ID 0043.

The 48 oriented raw features collapse to about `7.2046` effective dimensions; 14 pairs have `|corr| >= 0.85`, including one exact duplicate between F1 and F7. Future work must deduplicate rather than count technical indicators as independent votes.

Anchor sanity checks remain result-neutral: 2023-12-25 and 2024-03-31 are mechanically TRUE_EXHAUSTION; the January-2025 region maps to 2025-01-18 TRUE_EXHAUSTION; the October-2025 region maps to the nearby higher 2025-10-08 TRUE_EXHAUSTION. The 2024-11-24 region maps to 2024-11-22 and is AMBIGUOUS under the primary `-15% / 60-session` rule (`-11.77%` minimum), but TRUE_EXHAUSTION in the frozen `-10%` panel. The taxonomy is not altered to force the anchor to pass.

Interpretation: a 7–14 day exhaustion-ranking signal appears feasible, especially for severe drawdowns, but the first equal-weight absolute trigger is not operationally ready. ID 0043 is closed against result-informed pruning, reweighting, threshold rescue, dynamic-gross mapping, or portfolio-economic counterfactual. Any continuation requires a new research ID with deduplicated state dimensions and episode/block-aware validation.

Canonical BRRK-0011, Phase 6 and all production/security authority remain unchanged.

## BRRK-EXHAUSTION-STATE-0044 — PASS, closed

PR #156 froze 0044 before result release. PR #157 implemented the frozen runner and released exactly one valid result after a fully green pre-result baseline. The historical evidence remains researcher-exposed DEVELOPMENT evidence, not independent OOS.

Execution binding:

```text
pre-result green SHA                 f6fd1fc3425fefdc6bd024fa032a065accab7c6e
pre-result failed workflow run       31387906469 / NO DIAGNOSTIC / NO RESULT
unique valid result workflow run     31388103016 / run number 2 / attempt 1
trigger head SHA                     9affc7572dd0feefb14fe41e2aea7904c3a132ba
artifact id                          9062525981
artifact digest                      sha256:b109b610710b00904c924680a63305579f3f3c4c799d539906e0853629ddd378
full result SHA256                   687ff49d8db8baf54a1cfafcf8863c848011800b6c74689ab0534796ac86ff29
source taxonomy reproduction         MATCHED 0043 EXACTLY
```

Frozen CORE4 gate result:

```text
usable macro episodes                         7   PASS
TRUE / CONTINUATION episode coverage        5 / 4 PASS
15% PRE14_7 cross-episode AUC              0.750 PASS
15% PRE14_7 event AUC                      0.778 PASS
20% PRE14_7 cross-episode AUC              0.750 PASS
LOEO minimum / median AUC                  0.654 / 0.739 PASS
result_status                              PASS_TRIGGER_STAGE_ELIGIBLE
```

Result-informed component evidence is preserved without same-ID reweighting. S2 trend disagreement was strongest (`0.744` cross-episode AUC at PRE14_7, `0.893` at PRE7_0, `0.833` for severe PRE14_7). Secondary S5 volume confirmation was negative evidence: adding it reduced CORE4 cross-episode AUC from `0.750` to `0.676` at PRE14_7 and from `0.736` to `0.606` at PRE7_0; S5 alone was `0.500` at primary PRE14_7.

0044 therefore establishes that a frozen low-dimensional exhaustion state retains useful advance discrimination after macro-episode dependence control. It **does not** define a trading trigger or gross-risk response. `RUN_ONCE.marker` is permanent and 0044 may not be rerun, reweighted, pruned, rescued or used for same-ID threshold/gross search.

The only authorized research continuation is a new, separately preregistered trigger-stage ID. Canonical BRRK-0011, the 40/60 winner lineage, Phase 6 and all production/security authority remain unchanged.

## BRRK-EXHAUSTION-TRIGGER-0045 — FAIL, closed

PR #158 froze one trigger candidate before any result. PR #159 implemented it and released exactly one valid result after a fully green pre-result baseline. The historical evidence remains researcher-exposed DEVELOPMENT evidence, not independent OOS.

Execution binding:

```text
pre-result green SHA                 669942a4bef3f32894f616b9b28e5001d81e82b9
pre-result failed workflow run       31390711467 / NO DIAGNOSTIC / NO RESULT
unique valid result workflow run     31391109057 / run number 2 / attempt 1
trigger head SHA                     f9d4fba80bd07b8a5c67c5c3928f9081332809c7
artifact id                          9063704951
artifact digest                      sha256:0f8cd31ca3905d798194387622456fc8e59cb786376e57a6c135bdb2867c9c04
full result SHA256                   06714848cbb8c812a655700c29362487fc9e77ef2638f57547c7340ee10a2682
source taxonomy reproduction         MATCHED 0043 EXACTLY
parent 0044                          PASS_TRIGGER_STAGE_ELIGIBLE
```

Frozen trigger result:

```text
primary TRUE PRE14_7 WATCH/RISK            3 / 9 = 33.3% FAIL
primary CONT PRE14_0 false WATCH/RISK       0 / 6 = 0.0%  PASS
primary TRUE episode hit                    2 / 5 = 40.0% FAIL
primary CONT episode false                  0 / 5 = 0.0%  PASS
severe TRUE PRE14_7 WATCH/RISK              3 / 7 = 42.9% FAIL
severe TRUE PRE7_POST3 RISK                 2 / 7 = 28.6% FAIL
primary CONT PRE14_POST3 RISK               0 / 6 = 0.0%  PASS
qualifying TRUE PRE21_0 transition onsets             0    FAIL
premature-clear gate                         no denominator FAIL
result_status                       FAIL_NO_DYNAMIC_GROSS_STAGE_ELIGIBILITY
```

The candidate is specific but too insensitive and too persistent for the requested one-to-two-week action trigger. WATCH plus RISK occupies about `34.38%` of the 1,332-session history, while non-HEALTHY states occupy about `52.70%`. The three primary TRUE PRE14_7 hits were `2024-06-05`, `2024-07-21`, and `2025-10-08`; important genuine exhaustion events `2023-12-25`, `2024-03-31`, and `2025-01-18` were missed. `2025-10-08` was WATCH/RISK in PRE14_7 but did not confirm RISK in PRE7_POST3.

The zero PRE21_0 onset count is binding negative evidence: captured events were already in WATCH/RISK before the frozen lead window, so this machine acts more like a sticky risk regime than a precise 7–14 day transition trigger. No same-ID threshold, persistence, onset-window, S2-only, CORE4-weight or hysteresis rescue is allowed.

0045 is permanently closed and **does not authorize a dynamic-gross stage**. 0044's underlying state-discrimination PASS remains valid; what failed is this particular state-to-trigger translation. Any alternative trigger architecture requires a fresh result-informed research ID before evaluation.

Canonical BRRK-0011, the winner lineage, Phase 6, signing, order submission and production authority remain unchanged.

## BRRK-EXHAUSTION-PULSE-0046 — formal preregistration candidate, not run

PR #163 is the preregistration-only continuation of the exact design frozen by PR #162. On this branch, `BRRK-EXHAUSTION-PULSE-0046` is registered as one `PROGRAM_GOVERNED_V1` candidate with the already exposed DEVELOPMENT slice through `2026-08-02`. No runner, calibration threshold, pulse date or historical outcome result exists.

The preregistration keeps the two design corrections that were made before formal registration:

1. `CORE4 + S2 + S3 + S4` is rejected as the primary coordinate basis because CORE4 already contains S1–S4 and would implicitly duplicate S2/S3/S4. Primary coordinates remain exactly symmetric `S1/S2/S3/S4`; CORE4 is benchmark-only.
2. No extra Kalman/local-linear latent-state smoother is used. The detector estimates a 64-session causal pre-change linear baseline directly for each axis and detects positive slope departure.

Frozen primary candidate:

```text
S1 / S2 / S3 / S4 exactly from 0044
    -> 64-session causal pre-change OLS baseline for each candidate changepoint
    -> one-sided positive slope GLR per axis
    -> equal mixture over all 15 non-empty subsets of the four axes
    -> multiscale maximum over change ages 3..32 sessions
    -> label-blind VAR(1) + 7-vector residual-block bootstrap null calibration
    -> 5,000 null paths / seed 460046 / 256 burn-in / 1,460 evaluation sessions
    -> threshold chosen prospectively for truncated model-implied ARL0 >=365
    -> CALIBRATION_LOCK before any 0043/0044 event taxonomy may be loaded
    -> Transition Pulse = threshold upcrossing only
```

There is no WATCH/RISK state, persistence vote, cooldown, refractory period, recovery threshold or hysteresis machine. BOCPD remains excluded from 0046; any BOCPD study requires a later new research ID.

Frozen hard gates:

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
90th percentile raw-alarm spell               <=14 sessions
label-blind truncated ARL0                    >=365
```

The occupancy ceiling is explicitly result-informed and demands roughly a 50% reduction from failed 0045 WATCH+RISK occupancy. It is not independent validation.

A later 0046 PASS may at most produce `PASS_FUTURE_ONLY_PULSE_VALIDATION_ELIGIBLE`. It **does not** make dynamic gross eligible. Failure remains immutable and cannot be rescued under the same ID.

Current lifecycle on PR #163 branch:

```text
0046 exact design                 FROZEN BY PR #162
0046 formal PROGRAM_GOVERNED_V1  PREREGISTERED_NOT_RUN / MERGE PENDING
0046 dataset/exposure row         REGISTERED ON PR BRANCH / DEVELOPMENT EXPOSED
0046 declared variants            1
0046 actual variants evaluated    0
0046 runner                       NOT CREATED
0046 RUN_INTERFACE                NOT CREATED
0046 CALIBRATION_LOCK             NOT CREATED
0046 calibration                  NOT RUN
0046 threshold                    NONE
0046 historical outcome result    NONE
0046 portfolio economics          FORBIDDEN
dynamic-gross eligibility         FALSE
canonical BRRK change             NONE
Phase-6 change                    NONE
```

## Dashboard V5

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

The BRRK-WINNER development and robustness PASS results, Phase-6 observation credit, and 0046 preregistration do not change any of these fields.

## Current drift assessment

`DRIFT_0`.

The current working branch adds only the formal 0046 preregistration, its already exposed DEVELOPMENT dataset registration, fail-closed preregistration tests and this cross-chat handoff. It does not create a runner, calibration lock, threshold, pulse dates, outcome result or portfolio counterfactual. It does not change `execution/**`, canonical BRRK mathematics, the Phase-6 collector/schedule/evidence, leverage/shorting, signing, order submission or production authority.

## Exact next task

1. Require PR #163 final governance/no-drift/continuity/P3.2/Phase-6 checks to be green and retain all negative evidence.
2. Squash-merge PR #163 only if the final diff remains preregistration-only, zero-result and zero-authority.
3. Preserve Phase-6 automatic future-only observation independently at 00:00 UTC; 0046 must not alter Phase-6 evidence or credit.
4. Preserve 0044 PASS and 0045 FAIL as immutable; never rerun, retune or rescue either ID.
5. After PR #163 is merged, create a separate 0046 implementation branch from the new `main` and implement the frozen detector plus `RUN_INTERFACE` exactly.
6. Establish a fully green pre-result implementation SHA before any calibration.
7. Calibration must write and hash-bind `CALIBRATION_LOCK` before any event taxonomy or macro-episode labels may be loaded.
8. Do not run outcome evaluation, map dynamic gross, evaluate portfolio economics, change canonical BRRK, alter Phase 6, or confer any production/security authority before the frozen lifecycle permits it.

## PR #164 implementation handoff — supersedes the preregistration-stage handoff above

The preceding PR #163 wording is retained as immutable cross-chat history. The live authoritative continuation is now: PR #163 actually squash-merged at `48a140a1d58cba859d537e7dee0ad399c541527a`; PR #164 implements the already-frozen 0046 candidate on branch `research/brrk-exhaustion-pulse-0046-runonce` and remains **pre-result**.

```text
0046 exact design                    MERGED / IMMUTABLE / PR #162
0046 formal preregistration          MERGED / PR #163 / 48a140a1d58cba859d537e7dee0ad399c541527a
0046 implementation                 IMPLEMENTED_PRE_RESULT_NOT_RUN / PR #164
declared variants                   1
actual variants evaluated           0
PREDICTOR_PATH.json                 NOT CREATED
historical VAR fit                  NOT RUN
CALIBRATION_LOCK                    NOT CREATED
threshold                           NONE
event taxonomy loaded by 0046       FALSE
PRIMARY_RESULT                      NONE
EXECUTION                           NONE
RUN_ONCE.marker                     NONE
portfolio economics                 FORBIDDEN
future-only pulse-validation eligible FALSE
dynamic-gross eligibility           FALSE
canonical BRRK change               NONE
Phase-6 change                      NONE
production gross cap                1.0
production_authorized_components = []
production_authorized               false
signature_authorized                false
order_submission_authorized         false
```

The implementation enforces a three-stage information firewall:

```text
prepare-predictors
  raw causal inputs -> create-only timestamp + S1/S2/S3/S4 predictor artifact
calibrate
  reads predictor artifact only; no market/NAV or taxonomy/event/window imports
  -> create-only hash/code-bound CALIBRATION_LOCK
evaluate
  validate lock payload hash + code SHA + predictor binding + ARL0 first
  only then dynamically import evaluation/taxonomy code
```

Standing CI was explicitly extended through a test-only bridge under `research/governance/`; no workflow or policy was weakened. The immutable discovery command executed 162 tests including 0046 reference-equivalence, one-sided detector, pulse, firewall, frozen-constant and zero-authority suites. The implementation branch contains no generated predictor, lock or result evidence.

The exact next task is to require the final PR #164 head to remain green across Research governance core, Phase 0-8 drift audit, PR handoff governance, P3.2 parity and Phase-6 integrated shadow safety; final-audit the diff for zero generated evidence; merge #164 as implementation-only; verify live `main` moved; then treat that merged SHA as the immutable pre-result code boundary. Only a separate controlled execution branch may materialize the predictor artifact and run label-blind calibration. If VAR spectral radius is `>=1`, close 0046 before labels. Otherwise write/hash-bind `CALIBRATION_LOCK`, validate it, and only then execute the frozen historical evaluation exactly once. Same-ID rescue, dynamic-gross mapping, portfolio economics, canonical BRRK changes, Phase-6 changes and production/security authority remain forbidden.

## 0046 controlled run #1 + repair-only handoff — supersedes the implementation-stage next task above

PR #164 actually squash-merged at `f23d2aac6fa8699af12b784ca03489061e331865`, which is the immutable pre-result implementation boundary. A separate controlled execution branch added only a temporary one-shot workflow and ran GitHub Actions `31417259266` / job `93549100062` from head `d365c6d80bf198354fbaacd0e63bad6e0f4fe0c2`.

Execution-before-result proofs passed: the only diff from `f23d2aac...` was the temporary workflow; frozen 0046 implementation/governance/no-drift checks passed; the create-only predictor artifact contained only timestamp + S1/S2/S3/S4; and calibration read no labels/taxonomy.

The first label-blind calibration completed and is now immutable evidence:

```text
predictor start                      2023-08-07
predictor end                        2026-08-02
predictor sessions                   1092
predictor digest                     f25d93a39838b28a5bd9527db3b541c53b87a7e71c111b399a2997ed1202b9e4
VAR(1) spectral radius               0.9655669199981354
threshold float                      1125.89535644321
threshold full precision decimal     1125.8953564432099
threshold hex                        0x1.19794d851c766p+10
truncated ARL0                       365.0472
max simulated G                      16420.651959614333
run-1 lock payload hash              cba7aa3406c58ec80e391c389ea076439912d6bc3abecdfb89911739be1f2445
calibration label_data_accessed       false
calibration event_taxonomy_loaded    false
```

The lock validated successfully before evaluation. Historical evaluation then failed before `PRIMARY_RESULT` creation on frozen peak `2023-02-03`, because that peak precedes the complete four-axis predictor index and the first implementation raised on an absent peak. Run #1 uploaded zero Actions artifacts and emitted no `BRRK_0046_RESULT=` line. This is therefore retained as a **post-lock evaluation implementation/infrastructure failure with no research result**, not a PASS/FAIL signal result.

The repair question was checked against the frozen parent semantics before code change. 0046 preregistration explicitly reuses exact 0045 PRE14_7/PRE14_0/PRE21_0 session-window definitions. Immutable 0045 returns an empty window when a peak is absent and clips boundary windows; empty windows produce no hit/onset while the event remains in the original denominator. The 0046 raise was therefore an implementation deviation, not a new research rule.

PR #165 is repair-only. It adds `window_compat.py`, binds evaluation to the exact 0045 window helpers **after CALIBRATION_LOCK validation and before `run_locked`**, and adds standing-CI tests that directly compare absent/normal/left-clipped/right-clipped 0046 windows with immutable 0045. It does not modify detector, calibration, predictor, threshold, null, seeds, gates, pulse semantics, event filtering, denominators, taxonomy, registry, portfolio logic or authority.

Because run #1 calibration has been observed, every detector/null/threshold/gate/pulse parameter is permanently frozen. Before any corrected evaluation may read labels, a fresh deterministic calibration must reproduce run #1 in every non-code-SHA field. The fail-closed proof must replace the regenerated lock's code SHA with run #1 head `d365c6d80bf198354fbaacd0e63bad6e0f4fe0c2` and require the canonical payload hash to equal exactly `cba7aa3406c58ec80e391c389ea076439912d6bc3abecdfb89911739be1f2445`.

Current state:

```text
0046 pre-result boundary               f23d2aac6fa8699af12b784ca03489061e331865
0046 run #1 calibration                COMPLETE / IMMUTABLE
0046 run #1 historical result          NONE / evaluation infrastructure failure
0046 run #1 durable result artifact    NONE
0046 repair                            PR #165 CANDIDATE / EXACT 0045 WINDOW COMPATIBILITY ONLY
0046 detector/calibration retuning     FORBIDDEN
0046 threshold                         FROZEN AT 1125.89535644321
0046 dynamic-gross eligibility         FALSE
production gross cap                   1.0
production_authorized_components = []
production_authorized                  false
signature_authorized                   false
order_submission_authorized            false
```

Exact next task: require PR #165 final governance/no-drift/P3.2/Phase-6/handoff checks green; final-audit that only the window compatibility repair, repair tests and this append-only handoff changed; merge repair-only PR; create a fresh controlled execution branch from the repaired merge SHA; reproduce the first calibration lock as specified before label access; then execute the frozen historical evaluation exactly once if and only if reproduction succeeds. Preserve the resulting PASS/FAIL/INSUFFICIENT without same-ID rescue. Dynamic gross, portfolio economics, canonical BRRK changes, Phase-6 changes and production/security authority remain forbidden.


## 0046 immutable artifact evidence correction — 2026-08-10

PR #166 preserved the correct 0046 FAIL disposition but its hand-built compact closeout summary contained artifact-derived transcription errors. The immutable GitHub Actions artifact `9074623455` from run `31419044159` is authoritative. Correct facts: artifact digest `sha256:2938e8c0a14d30a750503d7fc0710cfe72db2066a4a2ba058518b11019b3c2a0`; `1,026` eligible sessions; `19` raw-alarm sessions; occupancy `1.8518519%`; one 19-session alarm spell; Transition Pulse `2026-06-03`; median-spell and p90-spell anti-stickiness gates both FAIL. Primary TRUE PRE14_7 remains `0/9`, TRUE episode `0/5`, severe TRUE `0/7`, PRE21_0 onset count `0`; therefore `FAIL_NO_FUTURE_ONLY_PULSE_VALIDATION_ELIGIBILITY` is unchanged. No 0046 rerun, retuning, rescue, threshold change, denominator change or portfolio economics occurred.

```text
production gross cap = 1.0
production_authorized_components = []
production_authorized = false
signature_authorized = false
order_submission_authorized = false
```

## BRRK-BETA-HANDOFF-EVENT-STUDY-0047 — exact design freeze candidate

PR #169 is the design-only candidate for the new BTC-to-Beta handoff anatomy study. The design file is `research/governance/BRRK_BETA_HANDOFF_EVENT_STUDY_0047_DESIGN_FREEZE_2026-08-11.md`.

This stage is intentionally restricted to a `STAGE_1_INFORMATION_TEST / MECHANISM_TEST` question: after the canonical BTC fast trend enters a positive episode, does exposed history contain recurrent, duration-aware ETH/SOL durable leadership handoffs? It does not test portfolio weights or portfolio economics.

Frozen scientific scope on the PR branch:

```text
primary universe                     BTC / ETH / SOL
historical role                      DEVELOPMENT / RESEARCHER_EXPOSED_HISTORY
history end                          2026-08-02
BTC-positive episode                 maximal contiguous BTC_TREND_FAST >= 0
causal trend horizons                20 / 60 / 120 / 240
causal anatomy                       fast+slow absolute and relative trend
relative acceleration                REL_FAST - REL_SLOW
Beta breadth                         0 / 0.5 / 1 from ETH/SOL participation
participation                        60-session trade-count surprise
state age                            raw sessions since BTC-positive episode start
realized durable target              same ETH/SOL uniquely beats BTC + other Beta at 20d and 60d while BTC > 0 at both horizons
cross-correlation                    episode-preserving lags -14..+14
VAR                                  pooled episode-preserving VAR(7)
Granger/Wald                         all six directed pairs / descriptive only
IRF                                  generalized BTC shock / horizons 0..14
episode bootstrap                    10,000 / seed 470047
oracle                               one-switch BTC->ETH/SOL hindsight bound only
```

Frozen stage gates for any later valid 0047 execution require at least 5 target-eligible BTC-positive episodes, at least 3 episodes with a primary durable handoff, episode-level prevalence >=0.50, and at least one ETH-cause plus one SOL-cause episode. These are modeling-sufficiency gates only; even a PASS would at most make a separately preregistered duration-aware handoff-model study eligible.

Explicitly forbidden under 0047:

```text
40/60 / 20/80 / 0/100 or any portfolio allocation test
CAGR / Sharpe / Calmar / MDD optimization
hazard-model fitting under this ID
HMM / classifier / boosting / neural-net candidate
fixed N-day switch delay chosen from result
BOCPD rescue
adding BNB after result
changing 20/60 target horizons after result
Edge Registry admission from descriptive DEVELOPMENT evidence
canonical BRRK / Phase-6 / production / signing / order changes
```

Current 0047 lifecycle:

```text
0047 exact design                    PR #169 / FROZEN DESIGN-ONLY CANDIDATE
0047 formal PROGRAM_GOVERNED_V1     NOT REGISTERED
0047 dataset/exposure row            NOT CREATED
0047 runner                          NOT CREATED
0047 historical result               NONE
0047 actual variants evaluated       0
0047 portfolio economics             FORBIDDEN
canonical BRRK change                NONE
Phase-6 change                       NONE
production_authorized                false
signature_authorized                 false
order_submission_authorized          false
```

Method-compliance checkpoint at this handoff: leader→follower→new-leader framing, canonical BTC-positive episode, fast/slow relative structure, breadth, trade-count participation, state age, episode-preserving cross-correlation/VAR(7)/Granger/generalized IRF, complete-episode bootstrap and oracle isolation are all present in the frozen design. No portfolio translation has been introduced.

Exact next step: require PR #169 final governance/no-drift/continuity checks to be green and verify the final diff contains only the design freeze plus this CURRENT_STATE handoff. If so, squash-merge #169. Only after the merged design boundary exists may a separate preregistration-only branch register 0047 and the exposed DEVELOPMENT dataset. No runner or result is allowed in that preregistration PR.

## BRRK-BETA-HANDOFF-EVENT-STUDY-0047 — formal preregistration candidate

The exact 0047 design is already merged and immutable at `398b7ec3f78f602461787b1b45e8d5041729e126`. The current preregistration branch mechanically registers that design under Program Governance v1 and registers the already exposed BTC/ETH/SOL DEVELOPMENT history through `2026-08-02`. No runner, model fit, market result or portfolio result exists on this branch.

```text
0047 exact design                    MERGED / IMMUTABLE / 398b7ec3f78f602461787b1b45e8d5041729e126
0047 formal PROGRAM_GOVERNED_V1     PREREGISTERED_NOT_RUN / PR CANDIDATE
0047 dataset slice                   BRRK-BETA-HANDOFF-0047-EXPOSED-HIST-V1
0047 contamination                   RESEARCHER_EXPOSED_HISTORY / DEVELOPMENT
0047 declared variants               1
0047 actual variants evaluated       0
0047 runner                          NOT CREATED
0047 historical result               NONE
0047 duration-aware model            FORBIDDEN UNDER 0047
0047 60/80/100 winner allocation     FORBIDDEN UNDER 0047
0047 portfolio economics             FORBIDDEN UNDER 0047
canonical BRRK change                NONE
Phase-6 change                       NONE
production_authorized                false
signature_authorized                 false
order_submission_authorized          false
```

Frozen method checkpoint remains unchanged from the design merge: canonical BTC-positive episodes; exact V1 20/60/120/240 fast/slow trend math; ETH/BTC and SOL/BTC fast/slow relative structure; `REL_FAST-REL_SLOW` acceleration; two-asset Beta breadth; trailing-60 trade-count participation surprise; raw state age; separate unique same-cause +20/+60 durable realized target with positive BTC on both horizons; right censoring rather than false negatives; episode-preserving cross-correlation `-14..+14`; pooled episode-preserving VAR(7); all six directed Granger/Wald diagnostics; generalized BTC-shock IRF `0..14`; complete-episode bootstrap `10,000 / seed 470047`; and a one-switch hindsight oracle isolated as a non-gating opportunity bound.

The preregistration treats those components as **one frozen diagnostic protocol**, not a candidate tournament. `actual_variants_evaluated=0`. A future valid 0047 execution may only determine whether recurrent durable handoff structure is sufficient to justify a new, separately preregistered duration-aware model stage. It cannot establish predictability, CAGR improvement, portfolio concentration or production authority.

Exact next task after this preregistration PR is fully green and merged: create a separate implementation-only branch from the merged preregistration boundary; encode the frozen anatomy with equivalence/fail-closed tests; keep result files absent; re-audit the full method checklist; merge only a zero-result implementation. Only after that boundary may one controlled historical 0047 execution occur. No 0047 allocation test, hazard-model fit, BOCPD rescue, exhaustion gross mapping, Phase-6 change or production/security change is permitted.

## BRRK-BETA-HANDOFF-EVENT-STUDY-0047 — implementation candidate

The exact 0047 design and formal preregistration are already merged at `398b7ec3f78f602461787b1b45e8d5041729e126` and `80c0d3cb7339012cac74e20563e07c7139ba3031`. The current branch implements that frozen Stage-1 anatomy only. It has not fetched 0047 historical market evidence and has released no 0047 scientific or economic result.

```text
0047 exact design                    MERGED / IMMUTABLE / 398b7ec3f78f602461787b1b45e8d5041729e126
0047 formal preregistration          MERGED / IMMUTABLE / 80c0d3cb7339012cac74e20563e07c7139ba3031
0047 implementation                 IMPLEMENTED_PRE_RESULT_NOT_RUN / PR CANDIDATE
0047 declared variants               1
0047 actual variants evaluated       0
0047 MARKET_EVIDENCE                  NOT CREATED
0047 historical result               NONE
0047 duration-aware model            FORBIDDEN UNDER 0047
0047 winner allocation/economics     FORBIDDEN UNDER 0047
canonical BRRK change                NONE
Phase-6 change                       NONE
production_authorized                false
signature_authorized                 false
order_submission_authorized          false
```

Implementation checkpoint: canonical V1 20/60/120/240 fast/slow trend equivalence is test-bound; BTC-positive episodes remain maximal contiguous `BTC_TREND_FAST >= 0`; ETH/BTC and SOL/BTC fast/slow relative trend, fast-minus-slow acceleration, two-asset breadth, trailing-60 trade-count participation and state age are implemented; the same-cause +20/+60 durable target requires positive BTC at both horizons and right-censors unavailable +60; cross-episode return/VAR pairs are forbidden; XCF is -14..+14 with positive lag meaning BTC leads; pooled episode-fixed-effect VAR(7), all six cluster-aware Granger/Wald diagnostics with seven-lag coefficient sets and complete-episode coefficient uncertainty, generalized BTC IRF 0..14, complete-episode 10,000/470047 bootstrap and the non-gating one-switch oracle are implemented. Stage classification reads only the frozen recurrence/cause-diversity gates.

Pre-result engineering clarifications are frozen in `RUN_INTERFACE.json`: raw requests begin 2020-08-01 but the common index begins at the latest first available BTC/ETH/SOL date; all days from common start through 2026-08-02 must be present or fail closed; within-episode demeaning is the fixed-intercept VAR implementation; singular Granger cluster covariance returns a null descriptive p-value rather than a rescue estimator; market evidence is create-only and SHA256-bound before result metrics.

Exact next task: require the implementation PR to pass standing governance/no-drift/P3.2/Phase-6/handoff CI, verify no temporary workflow or generated evidence remains, and merge only as a zero-result implementation boundary. Only after that merge may a separate controlled execution branch call `prepare-data` and then execute the frozen anatomy exactly once. No hazard model, BOCPD rescue, 60/80/100 allocation, portfolio economics, exhaustion gross mapping, Phase-6 change or production/security change is permitted under 0047.


## BRRK-LEADERSHIP-ROTATION-0048 — architecture-freeze candidate

0047 is immutable `FAIL_NO_RECURRENT_DURABLE_HANDOFF_STRUCTURE / CLOSED` and is not being rescued. The new 0048 design replaces the blocked one-way `BTC -> Beta` handoff continuation with a two-dimensional dynamic router.

```text
0048 architecture                      PR #174 / FROZEN ARCHITECTURE CANDIDATE
0048 numerical prereg                  NOT FROZEN
0048 dataset registration              NOT CREATED
0048 runner/model                      NOT CREATED
0048 historical measurement            NONE
0048 actual variants evaluated         0
0048 portfolio economics               NOT RUN
canonical BRRK change                  NONE
Phase-6 change                         NONE
production_authorized                  false
signature_authorized                   false
order_submission_authorized            false
```

Frozen architecture checkpoint:

- `Leadership` selects the asset; `Exhaustion / market risk` controls tolerated Beta/gross.
- Leadership states are `BTC_LEAD / ETH_LEAD / SOL_LEAD / NO_CLEAR_LEADER`.
- BTC, ETH and SOL use symmetric pairwise relative leadership; ETH and SOL have independent clocks.
- BTC Dominance is market-diffusion context only and cannot directly select the winner; no price proxy may be mislabeled as dominance.
- High-confidence winner concentration in the `80%-100%` risk-budget region is a later portfolio hypothesis, not an 0048 backtest.
- Two separate routes return a winner to BTC: leadership reversal and exhaustion compression.
- BTC-to-cash gross reduction is a later, separate stage and must not be conflated with winner-to-BTC re-anchoring.
- 0048 must defeat a static-Beta adversarial null; if one Beta asset is almost always superior, dynamic rotation has no incremental information value.

The only permitted next research action after this architecture freeze is a no-result numerical-method design pass that freezes the forward leadership target, causal score/normalization, episode-block validation, static-Beta/always-BTC controls, numerical gates, model budget, and a reproducible BTC Dominance source or explicit exclusion. No historical sweep, allocation test, CORE4 threshold search, portfolio economics, canonical change or production/security authority is permitted.
