# BRRK-LEADERSHIP-INTRADAY-SUPPORT-0053

Status: **`FAIL_4H_DOES_NOT_SOLVE_0048_SUPPORT_CONSTRAINT / CLOSED`**.

0053 was a label-blind 4h support-feasibility study created after the immutable 0048 insufficient-support closeout. It tested whether six years of Binance Spot BTC/ETH/SOL 4h data create genuinely more dependence-aware formal support under calendar-equivalent 0048 semantics, or merely more correlated rows.

## Immutable result

Unique support measurement:

- GitHub Actions run `31515648029`, job `93859999438`, attempt 1
- controlled execution HEAD `4de5b8b97075d5614b2dad121b6eb0d93b4def24`
- payload SHA256 `471b54991ae648b79433285f073ea7bc813663319b6e2389c1682dad1a319135`
- final marker `VALID_SUPPORT_MEASUREMENT_COMPLETE_CLOSED_TO_SAME_ID_RERUN`

### Track A — primary strict calendar-equivalent

```text
training support                   2190
shadow support                     2190
block length                       336 4h rows = 56 days equivalent
required blocks                    12
formal rows                        1468
complete blocks                    4
trailing rows                      124
first formal                       2025-01-14T16:00:00Z
last formal                        2025-11-05T16:00:00Z
classification                    FAIL
```

Track A is the only primary authority. Four-hour data therefore **did not solve** the 0048 dependence-aware support constraint.

### The important diagnostic

0048 daily formal rows were 245. Track A produced 1468 four-hour rows:

`1468 / 245 = 5.9918x`

But the dependence block also changed from 56 daily rows to 336 4h rows. Therefore complete blocks stayed:

```text
0048       4 blocks
0053 A     4 blocks
```

The extra rows were primarily finer sampling of the same calendar time, not more independent time support.

Track B (365/365/56) produced 98 blocks, but a 56-bar 4h block is only ~9.3 days and therefore deliberately demonstrates row-frequency inflation.

Track C (365/365/336) preserved the honest 56-day-equivalent dependence block and produced:

```text
formal rows                        5493
complete blocks                    16
first formal                       2022-02-15T20:00:00Z
```

Track C strongly indicates that the **two long 2190-origin burn-ins** are the dominant support bottleneck. However Track C was preregistered as diagnostic only and cannot rescue 0053 or 0048.

## What 0053 did not test

0053 computed no:

- ETH/SOL winner label or realized margin;
- predictive model or calibration fit;
- NLL, Brier, AUC or balanced accuracy;
- confidence curve or breakpoint;
- predictive bootstrap inference;
- portfolio allocation, CAGR or MDD.

Therefore 0053 provides a support-design result only, not evidence for or against a 4h ETH/SOL leadership signal.

## Governance closure

```text
same-ID rerun allowed              false
same-ID retuning allowed           false
same-ID rescue allowed             false
0048 rescue executed               false
0049 concentration unlocked        false
canonical BRRK changed             false
Phase 6 changed                    false
production_authorized              false
signature_authorized               false
order_submission_authorized        false
```

Any continuation requires a new research ID. The scientifically justified next problem is to preregister a **4h-native effective-sample / burn-in methodology** before fitting any new predictive leadership model. The observed Track C=16-block result is now exposed evidence and may not simply be adopted as a new 365/365 rule without independent justification.
