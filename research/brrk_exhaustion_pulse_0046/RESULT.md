# BRRK-EXHAUSTION-PULSE-0046 — Immutable Result

Status: **FAIL_NO_FUTURE_ONLY_PULSE_VALIDATION_ELIGIBILITY / CLOSED**

This is the first and only valid historical result for the exact preregistered 0046 Transition Pulse candidate. The evidence remains researcher-exposed DEVELOPMENT history and is not independent OOS evidence.

## Execution chain

Pre-result implementation boundary:

```text
f23d2aac6fa8699af12b784ca03489061e331865
```

Controlled run #1 (`31417259266`) completed the label-blind calibration and validated its lock, but the initial evaluator raised before creating `PRIMARY_RESULT` when the frozen `2023-02-03` event peak preceded the complete S1-S4 predictor path. It uploaded zero artifacts and is retained as a post-lock evaluation implementation/infrastructure failure, not a research PASS/FAIL.

PR #165 repaired only the already-frozen 0045-compatible session-window behavior and merged at:

```text
aef20ae0e452fa8d737a64846ba433aebcb55628
```

Controlled run #2 (`31419044159`, attempt 1, head `88f7c7e769352ea9d7b4cac881d2836678576b8e`) first proved the predictor and complete run-1 calibration reproduced exactly before any label access. Substituting the run-1 code SHA reproduced the original lock payload hash:

```text
cba7aa3406c58ec80e391c389ea076439912d6bc3abecdfb89911739be1f2445
```

Only after that proof did the frozen taxonomy load and the historical evaluation execute once.

## Frozen calibration

```text
predictor start                      2023-08-07
predictor end                        2026-08-02
predictor sessions                   1092
predictor digest                     f25d93a39838b28a5bd9527db3b541c53b87a7e71c111b399a2997ed1202b9e4
VAR(1) spectral radius               0.9655669199981354
threshold                            1125.89535644321
threshold full precision             1125.8953564432099
threshold hex                        0x1.19794d851c766p+10
truncated ARL0                       365.0472
max simulated G                      16420.651959614333
```

Calibration remained label-blind. `label_data_accessed=false` and `event_taxonomy_loaded=false` during calibration.

## Primary gates

```text
primary TRUE PRE14_7 event pulse hit       0 / 9 = 0.0000   FAIL
primary CONT PRE14_0 false pulse            0 / 6 = 0.0000   PASS
primary TRUE episode PRE14_7                0 / 5 = 0.0000   FAIL
primary CONT episode PRE14_0                0 / 5 = 0.0000   PASS
severe TRUE PRE14_7 event pulse hit         0 / 7 = 0.0000   FAIL
primary TRUE PRE21_0 qualifying onsets      0               FAIL
median qualifying onset lead                null            FAIL
raw alarm occupancy                         0.001958864      PASS
median raw-alarm spell                      1               PASS
p90 raw-alarm spell                         1               PASS
label-blind truncated ARL0                  365.0472        PASS
```

Episode diversity passed: eight usable macro episodes, with five TRUE and five CONTINUATION episode groups. The frozen taxonomy reproduced exactly.

## Interpretation

0046 resolved the operational stickiness exposed by 0045, but only by becoming far too sparse. Across 1,021 eligible detector sessions it produced two raw-alarm sessions and only one Transition Pulse, on:

```text
2025-11-22
```

That pulse did not land inside any preregistered TRUE_EXHAUSTION PRE14_7 or PRE21_0 window. The detector therefore failed all advance-sensitivity/timing gates while passing specificity and anti-stickiness gates.

This is binding negative evidence. The result may **not** be rescued under the same ID by lowering the threshold, relaxing ARL0, changing the 3..32 age scan, reweighting axes, privileging S2, adding BOCPD/CUSUM/Kalman/classifiers, changing pulse/reset rules, filtering early events, changing denominators, or adding a portfolio response.

## Evidence binding

```text
workflow run                         31419044159 / attempt 1
workflow head                        88f7c7e769352ea9d7b4cac881d2836678576b8e
artifact id                          9074623455
artifact digest                      sha256:2938e8c0a776255848b13990200cd77bec85ab15e143596a477fc08f3b63c2a0
predictor file SHA256                a82d41513995888cf4c9d39e66e4a09fa72649ffe84528377a5040b08bae693c
calibration-lock file SHA256         8ce129b1254e6cdb110486d3f1791851f6b4b9d18771b6dec2c39f7b5acade6f
full PRIMARY_RESULT SHA256           5c0e9aa4864b0044d5033573be78cdee3c0802db2d8b98d24fc0afcc21abbf8c
execution-summary SHA256             bc9a99481aa2b901987360606a4a5b589e5cbc92d763681579d8768ef3296e8b
full result internal payload hash    e70c712389569094bc671743236c2e3db0b481b66a817722331cdb152f7cf80d
```

## Authority

```text
future-only pulse-validation eligible false
dynamic-gross eligibility             false
portfolio economics executed          false
canonical strategy changed            false
Phase-6 observation changed            false
production_authorized                  false
signature_authorized                   false
order_submission_authorized            false
```

`RUN_ONCE.marker` is permanent. `BRRK-EXHAUSTION-PULSE-0046` is closed to same-ID rerun or rescue.
