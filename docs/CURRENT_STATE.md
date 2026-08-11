# BRRK Current State

Last updated: **2026-08-11**  
Authoritative repository: `alexwang91/laugh-to-2028`  
Current `main` controlled-execution merge: **`12f70c927df39b9e2ba799c8d4c597a7ae9b1726`**  
Current research branch: **`research/brrk-leadership-rotation-0048-execute-once`**  
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
BRRK leadership rotation 0048         MEASUREMENT_INCONCLUSIVE_INSUFFICIENT_SUPPORT / CLOSED

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

## 2. 0048 immutable scientific result

0048 asked only:

> Within a causally identified crypto-uptrend environment, can current ETH/SOL relative state predict which Beta asset will produce the stronger subsequent relative wealth path?

The binding hierarchy remains:

```text
Cash
  |
BTC defensive anchor inside crypto
  |
Beta risk
  |- ETH
  `- SOL
```

BTC was an eligibility/defensive-anchor asset, not a competing 0048 winner. Beta->BTC belongs to a separate later mechanism; BTC->cash belongs to another separate later mechanism.

The unique frozen DEVELOPMENT execution completed successfully but stopped at preregistered support gate G1:

```text
result status                         MEASUREMENT_INCONCLUSIVE_INSUFFICIENT_SUPPORT
G0                                    PASS
G1                                    FAIL
required complete 56-row blocks       12
observed complete 56-row blocks        4
formal evaluation rows                245
minimum rows implied by G1            672
formal-row shortfall                  427
ETH-leader full blocks                  4
SOL-leader full blocks                  4
bootstrap                             NOT RUN / NOT ELIGIBLE AFTER G1
formal window                         2025-01-14 through 2026-05-10
```

The direction-diversity subcondition was satisfied. The binding failure was total dependence-aware support after the complete causal pipeline: feature validity, `BTC_TREND_FAST >= 0`, 365 matured training origins, shadow-prequential calibration burn-in and 56-day target maturity.

Therefore 0048 is **INCONCLUSIVE, not PASS and not formal FAIL**. G2 and all later hard gates were not eligible to run.

---

## 3. 0048 unique execution identity

```text
architecture amendment merge          09a676e0e704a360730b1df0a57e6010b5a15f00
numerical prereg merge                 d907bd167f4cc51142f3cf9ff3b7eb4eeab7fab8
implementation merge                   a60696d5fe23e5dd95c40f868ccca199f36a3c20
controlled-run merge                   12f70c927df39b9e2ba799c8d4c597a7ae9b1726
execution HEAD                         12f70c927df39b9e2ba799c8d4c597a7ae9b1726
GitHub Actions run                     31505757608 / attempt 1
job                                    93826791780
actual variants evaluated              1
preflight                              PREFLIGHT_PASS_ZERO_RESULT
final marker                           VALID_EXECUTION_COMPLETE_CLOSED_TO_SAME_ID_RERUN
```

`RUN_ATTEMPT.marker` was durably persisted before registered-history model computation. `RUN_ONCE.marker` was persisted last. No second 0048 historical computation occurred and none is allowed.

Official artifact:

```text
name                                   brrk-0048-execution-bundle
artifact ID                            9106961253
digest                                 sha256:3ae658faee064add594b5494bd660dec3d3cee735a5a7cf517e3a01f408bfb32
```

Hash-locked runtime identities:

```text
attempt marker SHA256                  86138d7c700709475ce65083d58e0dda248a5300505e48829436d0efd4a594f4
primary result SHA256                  c67d35848bce203a66f355e927c61abd8e5c846a075f38e089307223c283b419
result summary SHA256                  08dcd468ead7e5f8530e018c8eb2d0bd12a62f280a95c33d8f08a48078a3d466
execution SHA256                       76f54002ce8af411c700c33933a4e65dd347a901fef86c5d4269efcf788f539c
```

---

## 4. Frozen 0048 provenance and method

The result uses the already researcher-exposed 0047 Binance BTC/ETH/SOL UTC daily market evidence:

```text
dataset slice ID                       BRRK-LEADERSHIP-ROTATION-0048-EXPOSED-HIST-V1
common history                         2020-08-11 through 2026-08-02
market payload SHA256                  d1cd28bc76f2cd8ee0486287fc50b49e5451355a3e75132a2de5b30c15af3193
data budget                            DEVELOPMENT
contamination                          RESEARCHER_EXPOSED_HISTORY
independent OOS                        false
```

Frozen candidate remained exactly seven antisymmetric ETH/SOL relative features:

```text
K1 / K2 / K3 / K4
Persistence60
Position120
Participation
```

Model/calibration remained:

```text
pi = (N_SOL + 1) / (N_SOL + N_ETH + 2)
p_raw = sigmoid(logit(pi) + beta'X)
ridge lambda = 1
expanding training
28-calendar-day refit
56-calendar-day label maturity
shadow-prequential prior-preserving calibration
p_cal = sigmoid(logit(pi) + gamma*eta), gamma >= 0
```

No feature, target, calibration, baseline, gate or historical-window rescue occurred after the result became visible.

---

## 5. Descriptive non-gating diagnostics

The unique execution also produced the following point diagnostics. They are preserved as adverse evidence but cannot be promoted to a formal FAIL because G1 stopped the inferential hierarchy first:

```text
candidate NLL                         0.7185986815
B0 uniform NLL                        0.6931471806
B1 prevalence NLL                     0.7185986815
B2 lagged-leader NLL                  0.7185986815
B3 relative-momentum NLL              0.7185986815

candidate Brier                       0.2627024107
B0 Brier                              0.2500000000
B1/B2/B3 Brier                        0.2627024107

AUC                                   0.3789464939
balanced accuracy                     0.5508059156
ETH recall                            0.1751412429
ETH precision                         0.8611111111
SOL recall                            0.9264705882
SOL precision                         0.3014354067
confidence-vs-realized-margin rho    -0.4111806894
```

At the first formal refit on 2025-01-14, `gamma_candidate = gamma_B2 = gamma_B3 = 0.0`, so the prior-preserving calibration suppressed fitted relative logits at that refit. Aggregate candidate/B1/B2/B3 NLL and Brier are exactly equal on the observed formal segment. This is descriptive only.

---

## 6. 0048 authority and closure

```text
leadership information established     false
0049 concentration eligible from 0048 false
portfolio allocation tested            false
portfolio economics executed           false
Beta -> BTC tested                      false
BTC -> cash tested                      false
canonical BRRK changed                  false
Phase 6 changed                         false
production authorized                   false
signature authorized                    false
order submission authorized             false
same-ID rerun allowed                   false
same-ID retuning allowed                false
same-ID rescue allowed                  false
```

0048 is permanently closed. Reducing the 12-block requirement, changing burn-ins, eligibility, calibration, features, target, inference, or extending/altering the historical sample for the same mechanism requires a **new research ID and new preregistration**.

---

## 7. Binding prior evidence

### Winner 0001 / robustness 0002

The exposed-development 40% BTC / 60% winner construction materially improved historical CAGR and passed cost robustness. It motivates concentration as a general research question, but it is not independent evidence for 0048 and 0048 does not authorize 0049.

### BRRK-EXHAUSTION-EVENT-STUDY-0043 — complete diagnostic

```text
workflow run                         31381953131 / attempt 1
```

The frozen 0043 interpretation remains: a **7–14 day exhaustion-ranking signal appears feasible**, but the first equal-weight absolute trigger was not operationally ready. **ID 0043 is closed against result-informed pruning, reweighting, threshold rescue**, dynamic-gross mapping or portfolio-economic counterfactual under the same ID.

### 0044 / 0045 / 0046

0044 CORE4 retains useful continuous exhaustion/risk ranking evidence. 0045 and 0046 failed as discrete trigger translations. Their failures remain binding negative evidence. CORE4 remains excluded from 0048 and may only motivate separately preregistered future research.

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

## 8. Program roadmap after 0048

The old conceptual roadmap was:

```text
0048  ETH/SOL Beta Leadership Information
0049  Beta Winner Concentration Portfolio Economics
0050  Beta -> BTC Continuation-Value Handoff
0051  BTC -> Cash Gross Exit
0052  Integrated Hierarchical Router
```

The 0048 lineage **does not unlock 0049** because leadership information was not established. Any future continuation must begin with a new, separately preregistered research ID whose design explicitly accounts for the observed support constraint and the already-exposed adverse diagnostics. It may not be presented as a same-ID rescue.

---

## 9. No-drift operating state

Nothing in the 0048 execution or closeout changes the live/canonical program:

```text
Canonical BRRK-0011                    NO CHANGE
Phase 6                                NO CHANGE
production gross cap = 1.0
production_authorized_components = []
production_authorized = false
signature_authorized = false
order_submission_authorized = false
```

No 60/80/90/100 concentration backtest, CAGR/MDD portfolio test, Beta->BTC rule, BTC->cash rule, integrated router, leverage expansion, shorting, signing or order submission was executed under 0048.

---

## 10. Exact next step

1. preserve the unique runtime bundle, `RESULT.md` and `CLOSEOUT.json` unchanged;
2. run closeout-only contract/governance/no-drift/parity/Phase-6 CI;
3. merge the 0048 closeout with expected-head protection;
4. do **not** rerun or retune 0048;
5. before opening any successor study, design a new research ID around the now-known support constraint and treat the adverse 0048 point diagnostics as exposed evidence.

---

## 11. Key authority files

```text
research/governance/BRRK_LEADERSHIP_ROTATION_0048_ARCHITECTURE_FREEZE_2026-08-11.md
research/governance/BRRK_LEADERSHIP_ROTATION_0048_ARCHITECTURE_AMENDMENT_2026-08-11.md
research/brrk_leadership_rotation_0048/PREREGISTRATION.json
research/brrk_leadership_rotation_0048/DATASET_DECLARATION.json
research/brrk_leadership_rotation_0048/IMPLEMENTATION_BOUNDARY.json
research/brrk_leadership_rotation_0048/CONTROLLED_EXECUTION_BOUNDARY.json
research/brrk_leadership_rotation_0048/RUN_INTERFACE.json
research/brrk_leadership_rotation_0048/RESULT_SCHEMA.json
research/brrk_leadership_rotation_0048/engine.py
research/brrk_leadership_rotation_0048/run_once.py
research/brrk_leadership_rotation_0048/RUN_ATTEMPT.marker
research/brrk_leadership_rotation_0048/PRIMARY_RESULT.json
research/brrk_leadership_rotation_0048/RESULT_SUMMARY.json
research/brrk_leadership_rotation_0048/EXECUTION.json
research/brrk_leadership_rotation_0048/RUN_ONCE.marker
research/brrk_leadership_rotation_0048/RESULT.md
research/brrk_leadership_rotation_0048/CLOSEOUT.json
research/brrk_leadership_rotation_0048/test_closeout_contract.py
config/research_registry.json
config/dataset_exposure_registry.json
research/brrk_beta_handoff_0047/CLOSEOUT.json
research/brrk_beta_handoff_0047/EVIDENCE_RECOVERY.json
research/governance/phase6_observation_ledger.json
```
