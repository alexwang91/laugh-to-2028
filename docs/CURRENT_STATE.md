# BRRK Current State

Last updated: 2026-08-10
Last merged governance PR: **#161**
Current working branch: `research/brrk-exhaustion-pulse-0046-design-freeze`
Authoritative baseline main at branch creation: `c1308fa20e85de69cfa0acf3decb56619d74df58`
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
BRRK exhaustion pulse 0046       EXACT DESIGN FROZEN / NOT PREREGISTERED / NOT RUN
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

## BRRK-EXHAUSTION-PULSE-0046 — exact design frozen, not preregistered

Issue #160 remains design/literature history only. The exact proposed architecture is now frozen separately in `research/governance/BRRK_EXHAUSTION_PULSE_0046_DESIGN_FREEZE_2026-08-10.md`. No result-bearing 0046 registration, runner, calibration or result exists yet.

The design review rejected two freedoms from the first Issue #160 draft:

1. `CORE4 + S2 + S3 + S4` is not the primary coordinate basis because CORE4 already contains S1–S4 and would implicitly duplicate S2/S3/S4 in a coordinate-sparse detector. Primary coordinates are exactly symmetric `S1/S2/S3/S4`; CORE4 remains benchmark-only.
2. No extra Kalman/local-linear latent-state smoother is used. The 0044 axes are already causal trailing-z bounded composites; a second smoother would add parameters and latency. Instead the detector estimates a 64-session causal pre-change linear baseline directly for each axis and detects positive slope departure.

Frozen proposed primary candidate:

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

There is no WATCH/RISK state, persistence vote, cooldown, refractory period, recovery threshold or hysteresis machine under the primary 0046 design. BOCPD is excluded from 0046 rather than retained as a second candidate; any BOCPD study requires a later new research ID.

Frozen proposed hard gates preserve the comparable 0045 event/episode hit and false-pulse requirements while adding anti-stickiness gates:

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

The occupancy ceiling is explicitly result-informed and demands roughly a 50% reduction from failed 0045 WATCH+RISK occupancy. It is not presented as independent validation.

A future 0046 PASS may at most produce `PASS_FUTURE_ONLY_PULSE_VALIDATION_ELIGIBLE`. It **does not** make dynamic gross eligible. Failure remains immutable and cannot be rescued under the same ID.

Current lifecycle:

```text
0046 exact design                 FROZEN IN DESIGN-ONLY DOC
0046 formal PROGRAM_GOVERNED_V1  NOT REGISTERED
0046 dataset/exposure row         NOT CREATED
0046 runner                       NOT CREATED
0046 calibration                  NOT RUN
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

The BRRK-WINNER development and robustness PASS results, Phase-6 observation credit, and 0046 design freeze do not change any of these fields.

## Current drift assessment

`DRIFT_0`.

The current working branch adds only the design-only 0046 mathematical freeze and updates cross-chat status. It does not create a formal research ID, runner, calibration, outcome result or portfolio counterfactual. It does not change `execution/**`, canonical BRRK mathematics, the Phase-6 collector/schedule/evidence, leverage/shorting, signing, order submission or production authority.

## Exact next task

1. Validate and merge this 0046 design-only freeze only if existing governance/no-drift/continuity checks remain green.
2. Preserve Phase-6 automatic future-only observation independently at 00:00 UTC; the design PR must not alter Phase-6 evidence or credit.
3. Preserve 0044 PASS and 0045 FAIL as immutable; never rerun, retune or rescue either ID.
4. After the design freeze is merged, create a **separate formal preregistration PR** for `BRRK-EXHAUSTION-PULSE-0046` that copies the frozen detector, calibration firewall, hard gates and governance boundaries without alteration.
5. The preregistration PR may register lineage and exposed DEVELOPMENT data but must not execute calibration or outcomes.
6. Only after a fully green preregistration baseline may a separate implementation/run-once PR be considered.
7. Do not run 0046, map dynamic gross, evaluate portfolio economics, change canonical BRRK, alter Phase 6, or confer any production/security authority during the design-freeze or preregistration stages.
