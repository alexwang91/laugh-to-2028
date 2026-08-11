# BRRK Current State

Last updated: **2026-08-11**  
Authoritative repository: `alexwang91/laugh-to-2028`  
Implementation base `main`: **`d907bd167f4cc51142f3cf9ff3b7eb4eeab7fab8`**  
Current research branch: **`research/brrk-leadership-rotation-0048-implementation`**  
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
BRRK leadership rotation 0048         PREREGISTERED_NOT_RUN / IMPLEMENTATION-ONLY ZERO-RESULT CANDIDATE

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

The numerical preregistration and exposed DEVELOPMENT dataset provenance were then atomically frozen at merge:

`d907bd167f4cc51142f3cf9ff3b7eb4eeab7fab8`

The binding hierarchy is:

```text
Cash
  |
BTC defensive anchor inside crypto
  |
Beta risk
  |- ETH
  `- SOL
```

0048 asks only:

> Within a causally identified crypto-uptrend environment, can current ETH/SOL relative state predict which Beta asset will produce the stronger subsequent relative wealth path?

BTC does **not** receive a 0048 winner label. Beta->BTC continuation value belongs to later 0050 research. BTC->cash belongs to later 0051 research.

---

## 3. 0048 preregistration and implementation state

```text
0048 research ID                      BRRK-LEADERSHIP-ROTATION-0048
0048 governance mode                  PROGRAM_GOVERNED_V1
0048 architecture                     REVISED / MERGED / FROZEN
0048 numerical prereg                 FROZEN / PREREGISTERED_NOT_RUN
0048 prereg merge                     d907bd167f4cc51142f3cf9ff3b7eb4eeab7fab8
0048 declared variants                1
0048 actual variants evaluated        0
0048 implementation                   CREATED ON SEPARATE ZERO-RESULT BRANCH
0048 registered-history model fit      NONE
0048 registered-history calibration    NONE
0048 historical result                 NONE
0048 portfolio result                  NONE / FORBIDDEN
0048 RUN_INTERFACE                     ABSENT / FORBIDDEN AT IMPLEMENTATION STAGE
0048 RUN_ONCE.marker                   ABSENT / FORBIDDEN AT IMPLEMENTATION STAGE
0048 PRIMARY_RESULT                    ABSENT / FORBIDDEN AT IMPLEMENTATION STAGE
```

The preregistration object remains registered exactly in `config/research_registry.json`; its governed path is `research/brrk_leadership_rotation_0048/`. Implementation does not alter the preregistration object, research registry, dataset declaration or dataset-exposure registry.

Synthetic unit-test fits are permitted only to verify frozen numerical invariants. They do not consume the registered historical candidate variant and do not change `actual_variants_evaluated = 0`.

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

No observation after `2026-08-02` may enter the frozen 0048 DEVELOPMENT result. The implementation contains no new 0048 network-fetch path; historical data must enter through the frozen 0047 evidence identity and fail closed on a payload-hash mismatch.

---

## 5. Frozen 0048 target and state

Formal prediction origins must satisfy:

`BTC_TREND_FAST >= 0`

using the canonical 20/60/120/240 trend family and FAST weights `0.15 / 0.25 / 0.30 / 0.30`. This is an eligibility filter only, not a BTC-leading handoff clock. The implementation reuses the existing 0047 canonical `trend_score` code rather than introducing a second formula.

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

No FAST/SLOW recompression, feature pruning, feature addition, CORE4, BTC Dominance, dispersion, funding/OI, macro, sentiment, HMM, tree, boosting or neural-network candidate may be introduced under 0048.

---

## 6. Frozen model, walk-forward and calibration

At each refit:

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

ETH/SOL exchange must map `X -> -X`, `pi -> 1-pi` and invert predicted leadership probability. The implementation contract tests this with deterministic synthetic data.

Calibration is shadow-prequential. A raw forecast joins the calibration pool only after the full 56-day target matures. Formal calibrated evaluation begins only after at least 365 matured eligible shadow forecast/outcome pairs.

```text
p_cal = sigmoid(logit(pi) + gamma * eta)
eta   = beta'X
gamma >= 0
```

No finite stable calibration solution => `MEASUREMENT_INCONCLUSIVE_CALIBRATION_UNIDENTIFIABLE`. Beta calibration and isotonic remain diagnostics only; they are not primary replacement paths.

---

## 7. Frozen baselines and inference

```text
B0  uniform p=0.5
B1  expanding Laplace SOL-lead prevalence
B2  lagged equal-weight 14/28/56 past path leader
B3  simple 60-day SOL/ETH relative momentum
```

Primary metric is NLL. The simultaneous gate remains:

```text
d_b,t       = loss_candidate - loss_baseline_b
T*          = max_b(mean(d_b*) - mean(d_b))
q95         = 95th percentile of T*
UCL_b       = mean(d_b) + q95
G2 pass     = max_b(UCL_b) < 0
```

```text
moving-block bootstrap                10,000 replicates
block length                          56 ordered eligible evaluation observations
seed                                  4292549012
same sampled blocks                   candidate + all baselines
```

Support requires >=12 complete 56-observation formal-evaluation blocks and each realized direction in >=3 distinct full blocks. Four contiguous temporal blocks require >=3/4 candidate wins. Causal episode robustness uses maximal eligible RREL60-sign runs with duration >=14.

Subsampling remains nonselection only: `b=max(56,ceil(N^(2/3)))`; it has no rescue authority.

---

## 8. Confidence / breakpoint implementation

```text
confidence c = 2 * abs(p_cal - 0.5)
Z            = sign(p_cal - 0.5) * M
G(c)         = E[Z | c]
```

Shape diagnostic remains a natural cubic regression spline with boundaries 0/1 and internal knots `0.25 / 0.50 / 0.75`. `G'` and `G''` are diagnostics only; `argmax G''` has no threshold-selection authority.

The sole HIGH mechanism is:

```text
G(c) = alpha + beta*c + delta*(c-kappa)_+
kappa in [0.20,0.80]
```

The implementation finds the deterministic global SSE minimum over the frozen one-breakpoint family, checks all frozen side-support conditions, and uses the smaller kappa on an exact numerical tie. Each bootstrap replicate re-estimates its own spline and breakpoint; no original-sample threshold is held fixed inside bootstrap.

G0-G6 establish robust leadership information. G7-G11 are separately required before 0049 concentration research becomes eligible.

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

No result classification exists yet.

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

## 12. Current implementation boundary

Permitted on the current implementation branch:

```text
frozen protocol source code            YES
synthetic mathematical unit tests      YES
synthetic model/calibration fits        YES / TESTS ONLY
historical evidence identity checks     YES / HASH ONLY
```

Still forbidden:

```text
registered-history 0048 model fit       FORBIDDEN
registered-history calibration fit      FORBIDDEN
0048 historical evaluation              FORBIDDEN
0048 result release                     FORBIDDEN
RUN_INTERFACE / run_once                FORBIDDEN
PRIMARY_RESULT / EXECUTION / marker      FORBIDDEN
0048 portfolio allocation test          FORBIDDEN
80/90/100 winner backtest               FORBIDDEN
Beta -> BTC rule                        FORBIDDEN
BTC -> cash rule                        FORBIDDEN
same-ID retuning/rescue after result    FORBIDDEN
canonical BRRK change                   FORBIDDEN
Phase-6 change                          FORBIDDEN
production/signing/order authority      FORBIDDEN
```

---

## 13. Exact next step

For the current implementation branch:

1. keep the frozen `PREREGISTRATION.json`, research registry and dataset registry unchanged;
2. require implementation code to be deterministic and fail closed;
3. run only synthetic/equivalence/governance CI — no historical 0048 evaluation;
4. require exact target-formula, exchange-symmetry, label-maturity, prequential-calibration, bootstrap-alignment and no-result-artifact tests;
5. require all standing governance/no-drift/baseline/parity/Phase-6 checks to pass;
6. merge only with expected-head protection and only while `actual_variants_evaluated = 0` and all result/run artifacts remain absent.

After that zero-result implementation merge, stop and create a **separate controlled-execution boundary**. That later stage may add a hash-bound run interface/run-once mechanism and may perform exactly **one** registered-history 0048 DEVELOPMENT execution. Any valid scientific output closes 0048 to same-ID rerun, retuning and rescue.

---

## 14. Key authority files

```text
research/governance/BRRK_LEADERSHIP_ROTATION_0048_ARCHITECTURE_FREEZE_2026-08-11.md
research/governance/BRRK_LEADERSHIP_ROTATION_0048_ARCHITECTURE_AMENDMENT_2026-08-11.md
research/brrk_leadership_rotation_0048/PREREGISTRATION.json
research/brrk_leadership_rotation_0048/DATASET_DECLARATION.json
research/brrk_leadership_rotation_0048/IMPLEMENTATION_BOUNDARY.json
research/brrk_leadership_rotation_0048/engine.py
research/brrk_leadership_rotation_0048/test_engine_contract.py
research/brrk_leadership_rotation_0048/README.md
config/research_registry.json
config/dataset_exposure_registry.json
research/brrk_beta_handoff_0047/CLOSEOUT.json
research/brrk_beta_handoff_0047/EVIDENCE_RECOVERY.json
research/governance/phase6_observation_ledger.json
```
