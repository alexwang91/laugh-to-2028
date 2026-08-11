# BRRK Current State

Last updated: **2026-08-11**  
Authoritative repository: `alexwang91/laugh-to-2028`  
Baseline `main` before current preregistration PR: **`09a676e0e704a360730b1df0a57e6010b5a15f00`**  
Current research PR: **#177 — 0048 numerical preregistration**  
Status of this document: **AUTHORITATIVE OPERATING SNAPSHOT**

> GitHub `main`, immutable research artifacts and machine registries remain the sources of truth. This file is the compact human handoff, not a substitute for preregistration, execution, evidence, recovery or closeout artifacts.

---

## 1. Executive state

```text
Phase 0-3                              COMPLETE / MERGED
Phase 4 leverage research             FAIL_STOP / NO_PROMOTION
P5.5                                   COMPLETE / IMMUTABLE / NO_PROMOTION / FAIL_STOP
F27 idle-cash measurement             R2 AUTHORITATIVE / R1 SUPERSEDED-PRESERVED
F7 metrics convergence                PARTIAL

Phase 6 ARM                            ACTIVE FUTURE-ONLY OBSERVATION
Phase 6 ARM marker                     cbd58adb05187651ca72d67900a0ccbbd3e83b1e
Phase 6 daily schedule                 00:00 UTC
Phase 6 genuine scheduled credit       1 / >=10
Phase 6 emergency drills               0 / >=1
Phase 6 elapsed requirement            NOT MET
Phase 6 live acceptance                MEASUREMENT_INCONCLUSIVE_TIME_DEPENDENT

BRRK opportunity-cost audit 0042       COMPLETE DIAGNOSTIC / NO PROMOTION AUTHORITY
BRRK-WINNER-0001                       PASS_ROBUSTNESS_STAGE_ELIGIBLE / DEVELOPMENT / CLOSED
BRRK-WINNER-ROBUSTNESS-0002            PASS_FUTURE_ONLY_VALIDATION_STAGE_ELIGIBLE / DEVELOPMENT / CLOSED
BRRK exhaustion event study 0043      COMPLETE DIAGNOSTIC / CLOSED
BRRK exhaustion state 0044            PASS_TRIGGER_STAGE_ELIGIBLE / CLOSED
BRRK exhaustion trigger 0045          FAIL_NO_DYNAMIC_GROSS_STAGE_ELIGIBILITY / CLOSED
BRRK exhaustion pulse 0046            FAIL_NO_FUTURE_ONLY_PULSE_VALIDATION_ELIGIBILITY / CLOSED
BRRK Beta handoff event study 0047    FAIL_NO_RECURRENT_DURABLE_HANDOFF_STRUCTURE / CLOSED
BRRK leadership rotation 0048         REVISED ARCHITECTURE FROZEN / PREREGISTERED_NOT_RUN PR #177

Canonical BRRK-0011                    NO CHANGE
Phase 7                                MONITOR_ONLY / LAUNCH BLOCKED
Phase 8                                TRIGGER ABSENT / NOT RUN
Production                             NO CHANGE
production gross cap = 1.0
production_authorized_components = []
production_authorized = false
signature_authorized = false
order_submission_authorized = false
```

Phase-6 counts above are copied from the committed accounting index. That ledger is non-evidence and cannot create or backfill credit; durable Actions evidence and its separate receipt remain the evidence authority.

---

## 2. Active research frontier — 0048

The original 0048 qualitative architecture was amended before any numerical preregistration or historical 0048 result. The amendment merged at:

`09a676e0e704a360730b1df0a57e6010b5a15f00`

The binding hierarchy is now:

```text
Cash
  |
BTC defensive anchor inside crypto
  |
Beta risk
  |- ETH
  `- SOL
```

Therefore 0048 asks only:

> Within a causally identified crypto-uptrend environment, can current ETH/SOL relative state predict which Beta asset will produce the stronger subsequent relative wealth path?

BTC does **not** receive a 0048 winner label. Beta->BTC continuation value belongs to later 0050 research. BTC->cash belongs to later 0051 research.

---

## 3. 0048 preregistration state

PR #177 freezes the exact numerical method before implementation or result release.

```text
0048 research ID                      BRRK-LEADERSHIP-ROTATION-0048
0048 governance mode                  PROGRAM_GOVERNED_V1
0048 architecture                     REVISED / MERGED / FROZEN
0048 numerical prereg                 PREREGISTERED_NOT_RUN / PR #177 CANDIDATE
0048 declared variants                1
0048 actual variants evaluated        0
0048 implementation                   NOT CREATED
0048 model fit                         NONE
0048 calibration fit                   NONE
0048 historical result                 NONE
0048 portfolio result                  NONE / FORBIDDEN AT THIS STAGE
```

The preregistration object is registered exactly in `config/research_registry.json`; its governed path is `research/brrk_leadership_rotation_0048/`.

---

## 4. 0048 frozen dataset provenance

0048 reuses the already researcher-exposed 0047 Binance BTC/ETH/SOL UTC daily market evidence rather than pretending that the same history is new OOS evidence.

```text
dataset slice ID
BRRK-LEADERSHIP-ROTATION-0048-EXPOSED-HIST-V1

underlying assets                     BTC / ETH / SOL
source                                 Binance Spot UTC daily klines
common history                         2020-08-11 through 2026-08-02
source market payload SHA256           d1cd28bc76f2cd8ee0486287fc50b49e5451355a3e75132a2de5b30c15af3193
data budget                            DEVELOPMENT
contamination                          RESEARCHER_EXPOSED_HISTORY
independent OOS                        false
```

No observation after `2026-08-02` may enter the frozen 0048 DEVELOPMENT result.

---

## 5. Frozen 0048 target and state

Formal prediction origins must first satisfy the pre-existing causal eligibility rule:

`BTC_TREND_FAST >= 0`

using the canonical 20/60/120/240 trend family and FAST weights `0.15 / 0.25 / 0.30 / 0.30`. This is an eligibility filter only, not a BTC-leading handoff clock.

For `i in {ETH,SOL}` and `h in {14,28,56}`:

```text
A_i,h(t) = 2/[h(h+1)] * sum_{u=1..h} log(P_i[t+u] / P_i[t])
L_i(t)   = mean(A_i,14, A_i,28, A_i,56)
M_t      = L_SOL(t) - L_ETH(t)
Y_t      = 1 if M_t > 0; 0 if M_t < 0
```

Exact `M_t=0` is `TARGET_TIE`, excluded from supervised scoring but counted. Rank direction is the predictive target; continuous realized margin is retained separately for confidence/economic-strength validation.

The sole candidate has exactly seven antisymmetric ETH/SOL relative features:

```text
K1   relative momentum age block 1-20
K2   relative momentum age block 21-60
K3   relative momentum age block 61-120
K4   relative momentum age block 121-240
Persistence60
Position120        symmetric relative range position
Participation      relative quote-volume activity, median20 vs median120
```

The four momentum blocks do not overlap. Each is volatility-normalized and tanh-compressed. All seven features are naturally bounded in `[-1,1]`; no training z-score standardization is used.

No FAST/SLOW recompression, feature pruning, feature addition, CORE4, BTC Dominance, dispersion, funding/OI, macro, sentiment, HMM, tree, boosting or neural-network candidate may be introduced under 0048.

---

## 6. Frozen 0048 model, training and calibration

At each refit, matured historical winner prevalence is Laplace-smoothed:

```text
pi = (N_SOL + 1) / (N_SOL + N_ETH + 2)
p_raw = sigmoid(logit(pi) + beta'X)
```

with:

```text
fitted intercept                      none
ridge lambda                          1 fixed
training window                       expanding
maximum label maturity                56 calendar days
first shadow-model support            >=365 matured eligible origins
refit cadence                         28 calendar days
```

ETH/SOL exchange must map `X -> -X`, `pi -> 1-pi` and invert the predicted leadership probability. No rolling-window, lambda or refit-frequency search is allowed.

Calibration is shadow-prequential. A raw forecast must be stored before its future outcome exists and may join the calibration pool only after the full 56-day target matures. Formal calibrated evaluation begins only after at least 365 matured eligible shadow forecast/outcome pairs.

Primary calibration preserves the expanding prevalence prior:

```text
p_cal = sigmoid(logit(pi) + gamma * eta)
eta   = beta'X
gamma >= 0
```

If no finite stable calibration solution exists, the study fails closed to `MEASUREMENT_INCONCLUSIVE_CALIBRATION_UNIDENTIFIABLE`. Beta calibration and isotonic regression are diagnostics only and have no rescue authority.

---

## 7. Frozen baselines and inference

Probabilistic controls:

```text
B0  uniform p=0.5
B1  expanding Laplace SOL-lead prevalence
B2  lagged equal-weight 14/28/56 past path leader
B3  simple 60-day SOL/ETH relative momentum
```

B2/B3 use the same causal expanding/refit/prequential-calibration structure as the candidate. Always-historical-favorite is classification diagnostic only.

Primary metric is NLL. 0048 must beat **all** frozen causal probabilistic baselines using simultaneous dependence-aware inference:

```text
moving-block bootstrap                10,000 replicates
block length                          56 ordered eligible evaluation observations
seed                                  4292549012
same sampled blocks                   candidate + all baselines
```

Support requires at least 12 complete 56-observation formal-evaluation blocks, with each realized winner direction represented in at least 3 distinct full blocks.

Temporal robustness uses four mechanical contiguous equal-count blocks and requires candidate NLL superiority in at least 3/4. Causal episode robustness uses maximal eligible runs of 60-day SOL/ETH relative-return sign; only episodes lasting at least 14 observations enter the equal-episode gate.

The contiguous-subsampling diagnostic `b=max(56,ceil(N^(2/3)))` has no rescue authority.

---

## 8. Confidence and concentration-handoff gate

After calibration:

```text
confidence c = 2 * abs(p_cal - 0.5)
Z            = sign(p_cal - 0.5) * M
G(c)         = E[Z | c]
```

Shape diagnostic is a fixed natural cubic spline with boundaries 0/1 and internal knots `0.25 / 0.50 / 0.75`. `G'` and `G''` are diagnostics only; `argmax G''` may not select a threshold.

The sole threshold mechanism is exactly one segmented-regression breakpoint:

```text
G(c) = alpha + beta*c + delta*(c-kappa)_+
kappa in [0.20,0.80]
```

A reliable breakpoint requires the exact side-support, bootstrap-validity, CI-width and positive post-break-slope conditions frozen in `PREREGISTRATION.json`.

G0-G6 establish robust leadership information. G7-G11 are separately required before 0049 confidence-driven concentration research becomes eligible. Failure of HIGH does not erase a valid leadership-information PASS.

---

## 9. 0048 result hierarchy

```text
INVALID_EXECUTION
MEASUREMENT_INCONCLUSIVE_INSUFFICIENT_SUPPORT
MEASUREMENT_INCONCLUSIVE_CALIBRATION_UNIDENTIFIABLE
FAIL_NO_INCREMENTAL_DYNAMIC_LEADERSHIP
FAIL_NO_ROBUST_DYNAMIC_LEADERSHIP
PASS_LEADERSHIP_INFORMATION_NO_CONCENTRATION_HANDOFF
PASS_ONE_SIDED_LEADERSHIP_NO_FULL_ROUTER
PASS_LEADERSHIP_INFORMATION_CONCENTRATION_HANDOFF_ELIGIBLE
```

A full 0048 PASS still does not prove that 80%, 90% or 100% winner concentration is economically optimal.

---

## 10. Binding prior evidence

### Winner 0001 / robustness 0002

The exposed-development 40% BTC / 60% winner construction materially improved historical CAGR and passed cost robustness. It motivates later concentration research but does not identify an 80%-100% optimum and is not independent evidence for 0048.

### BRRK-EXHAUSTION-EVENT-STUDY-0043 — complete diagnostic

```text
workflow run                         31381953131 / attempt 1
```

The frozen 0043 interpretation remains: a **7–14 day exhaustion-ranking signal appears feasible**, but the first equal-weight absolute trigger was not operationally ready. **ID 0043 is closed against result-informed pruning, reweighting, threshold rescue**, dynamic-gross mapping or portfolio-economic counterfactual under the same ID.

### 0044 / 0045 / 0046

0044 CORE4 retains useful continuous exhaustion/risk ranking evidence. 0045 and 0046 failed as discrete trigger translations. Their failures remain binding negative evidence. CORE4 is excluded from primary 0048 and may only motivate separately preregistered later Beta->BTC continuation-value work.

### 0047

0047 remains immutable:

```text
target-eligible BTC-positive episodes       27
primary durable handoffs                    12
prevalence                                  44.44% < 50% gate
ETH causes                                  3
SOL causes                                  9
result                                      FAIL_NO_RECURRENT_DURABLE_HANDOFF_STRUCTURE / CLOSED
```

This rejects the exact frozen recurrent BTC-positive handoff-clock structure. It does not establish that continuous ETH/SOL relative information is absent.

---

## 11. Program roadmap

```text
0048  ETH/SOL Beta Leadership Information
0049  Beta Winner Concentration Portfolio Economics
0050  Beta -> BTC Continuation-Value Handoff
0051  BTC -> Cash Gross Exit
0052  Integrated Hierarchical Router
```

Each later stage requires its own preregistration and predecessor gate. The long-run portfolio objective for later economic stages is terminal compound wealth / net CAGR over a fixed causal evaluation interval after costs. Intermediate MDD is diagnostic rather than the primary objective; no leverage expansion is authorized by 0048.

---

## 12. Current prohibitions

Until PR #177 is merged and a separate zero-result implementation boundary is created:

```text
0048 model fit                         FORBIDDEN
0048 calibration fit                   FORBIDDEN
0048 historical evaluation             FORBIDDEN
0048 result release                    FORBIDDEN
0048 portfolio allocation test         FORBIDDEN
80/90/100 winner backtest              FORBIDDEN
Beta -> BTC rule                       FORBIDDEN
BTC -> cash rule                       FORBIDDEN
same-ID retuning/rescue after result   FORBIDDEN
canonical BRRK change                  FORBIDDEN
Phase-6 change                         FORBIDDEN
production/signing/order authority     FORBIDDEN
```

---

## 13. Exact next step

For PR #177:

1. require the final diff to contain the two central registry updates, the four 0048 preregistration files and this CURRENT_STATE refresh only;
2. require standing governance, handoff, no-drift, baseline and parity CI to pass on the final owner-authored head;
3. merge only with expected-head protection.

After the preregistration merge:

1. create a separate implementation-only branch from that exact merge boundary;
2. mechanically implement the frozen target/features/model/walk-forward/calibration/baselines/inference;
3. add exchange-symmetry, numerical-equivalence, label-maturity, prequential-calibration and fail-closed tests;
4. keep `PRIMARY_RESULT.json`, `EXECUTION.json`, `RUN_ONCE.marker` and all portfolio outputs absent;
5. merge only a zero-result implementation.

Only after that implementation boundary is merged and green may exactly **one** controlled historical 0048 DEVELOPMENT execution occur.

---

## 14. Key authority files

```text
research/governance/BRRK_LEADERSHIP_ROTATION_0048_ARCHITECTURE_FREEZE_2026-08-11.md
research/governance/BRRK_LEADERSHIP_ROTATION_0048_ARCHITECTURE_AMENDMENT_2026-08-11.md
research/brrk_leadership_rotation_0048/PREREGISTRATION.json
research/brrk_leadership_rotation_0048/DATASET_DECLARATION.json
research/brrk_leadership_rotation_0048/README.md
config/research_registry.json
config/dataset_exposure_registry.json
research/brrk_beta_handoff_0047/CLOSEOUT.json
research/brrk_beta_handoff_0047/EVIDENCE_RECOVERY.json
research/governance/phase6_observation_ledger.json
```
