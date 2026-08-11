# BRRK-LEADERSHIP-ROTATION-0048 — Immutable Result

Status: **MEASUREMENT_INCONCLUSIVE_INSUFFICIENT_SUPPORT / CLOSED**

## Bottom line

The exactly-once frozen DEVELOPMENT execution completed successfully, but the study stopped at preregistered support gate **G1**. Only **4 complete 56-observation formal-evaluation blocks** were available, versus the frozen minimum of **12**. Therefore 0048 is **INCONCLUSIVE**, not PASS and not FAIL.

No bootstrap superiority gate, temporal robustness gate, confidence-HIGH eligibility gate, concentration portfolio study, Beta-to-BTC rule, BTC-to-cash rule or production action is authorized by this result.

## Execution identity

- controlled execution HEAD: `12f70c927df39b9e2ba799c8d4c597a7ae9b1726`
- GitHub Actions run: `31505757608`, attempt 1
- job: `93826791780`
- market payload SHA256: `d1cd28bc76f2cd8ee0486287fc50b49e5451355a3e75132a2de5b30c15af3193`
- artifact: `brrk-0048-execution-bundle`, ID `9106961253`
- artifact digest: `sha256:3ae658faee064add594b5494bd660dec3d3cee735a5a7cf517e3a01f408bfb32`

`preflight` returned `PREFLIGHT_PASS_ZERO_RESULT` before any historical computation began. `RUN_ATTEMPT.marker` was then durably created before model evaluation, and `RUN_ONCE.marker` was written last with status `VALID_EXECUTION_COMPLETE_CLOSED_TO_SAME_ID_RERUN`.

## Hash-locked bundle

```text
attempt_marker_sha256
86138d7c700709475ce65083d58e0dda248a5300505e48829436d0efd4a594f4

primary_result_sha256
c67d35848bce203a66f355e927c61abd8e5c846a075f38e089307223c283b419

result_summary_sha256
08dcd468ead7e5f8530e018c8eb2d0bd12a62f280a95c33d8f08a48078a3d466

execution_sha256
76f54002ce8af411c700c33933a4e65dd347a901fef86c5d4269efcf788f539c
```

## G1 support result

```text
formal evaluation window              2025-01-14 through 2026-05-10
eligible feature-valid origins        1102
formal predictions                    245
formal evaluation rows                245
target ties                           0

required complete 56-row blocks       12
observed complete 56-row blocks        4
minimum rows implied by G1            672
observed rows                         245
shortfall                             427

ETH-leader full blocks                  4
SOL-leader full blocks                  4
G1                                    FAIL
```

The direction-diversity subcondition was satisfied; the binding failure was total dependence-aware support. The strict causal pipeline — feature validity, `BTC_TREND_FAST >= 0` eligibility, 365 matured training origins, shadow-prequential calibration burn-in, and 56-day target maturity — left materially fewer formal observations than the preregistration required.

Because G1 failed, the frozen runner correctly set `bootstrap = null`; G2 and all later hard gates were not eligible to run.

## Descriptive diagnostics — non-gating

These numbers are preserved because they were produced by the unique frozen execution, but they do **not** convert the G1 outcome into a formal model failure.

```text
candidate NLL                         0.7185986815
B0 uniform NLL                        0.6931471806
B1 prevalence NLL                     0.7185986815
B2 lagged-leader NLL                  0.7185986815
B3 relative-momentum NLL              0.7185986815

candidate Brier                       0.2627024107
B0 uniform Brier                      0.2500000000
B1/B2/B3 Brier                        0.2627024107

AUC                                   0.3789464939
balanced accuracy                     0.5508059156
ETH recall                            0.1751412429
ETH precision                         0.8611111111
SOL recall                            0.9264705882
SOL precision                         0.3014354067
confidence-vs-realized-margin rho     -0.4111806894
```

At the first formal refit (`2025-01-14`), `gamma_candidate = gamma_B2 = gamma_B3 = 0.0`, so the prior-preserving calibration suppressed the fitted relative logits and emitted the expanding prevalence prior. Aggregate candidate/B1/B2/B3 NLL and Brier are exactly equal over the observed formal segment. This is adverse descriptive evidence, but the preregistered inference hierarchy does not permit using it as a formal G2 failure after G1 stopped the study.

## Scientific interpretation

0048 does **not** establish that the seven-feature ETH/SOL leadership model contains incremental information. It also does **not** formally reject that hypothesis. The registered historical sample simply did not contain enough post-burn-in, BTC-supportive, fully matured formal observations for the frozen dependence-aware inference plan.

The most important design lesson is therefore about **support accounting**: the preregistered expectation for available formal evaluation support was too optimistic after the entire causal pipeline was applied.

The adverse point diagnostics are still relevant when designing any future study. They must be treated as already exposed evidence, not ignored and not used to tune 0048.

## Authority and closure

```text
0048 leadership information established     false
0049 concentration eligible from 0048       false
portfolio economics executed                 false
Beta -> BTC tested                           false
BTC -> cash tested                           false
canonical BRRK changed                       false
Phase 6 changed                              false
production authorized                        false
signature authorized                         false
order submission authorized                  false
```

0048 is permanently closed to same-ID rerun, retuning and rescue. Any change to support thresholds, burn-ins, eligibility, calibration, features, target, historical window or model requires a **new research ID and a new preregistration**.
