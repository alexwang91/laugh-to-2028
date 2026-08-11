# BRRK-LEADERSHIP-INTRADAY-SUPPORT-0053 — Result

**Final classification:** `FAIL_4H_DOES_NOT_SOLVE_0048_SUPPORT_CONSTRAINT / CLOSED`

## Primary answer

Using six years of Binance Spot BTC/ETH/SOL 4h bars does **not** solve the 0048 dependence-aware support deficit when the 0048 economic-time semantics are preserved.

The frozen Track A pipeline produced:

```text
raw common 4h bars                    13,097
feature-valid bars                    11,657
BTC-uptrend eligible feature bars      6,605
eligibility rate                       56.66%

training support required               2,190 eligible matured 4h origins
shadow support required                 2,190 matured shadow origins
56-day-equivalent dependence block        336 4h rows
required complete blocks                    12

Track A formal rows                     1,468
Track A complete blocks                     4
Track A trailing rows                     124
```

Track A therefore failed the frozen 12-block requirement.

## Why 4h rows increased but effective support did not

0048 daily formal rows were 245. Track A 4h formal rows were 1,468:

`1468 / 245 = 5.9918x`

That is almost exactly the six 4h bars per day expected from changing resolution.

But the frozen dependence scale also changed from:

`56 daily rows -> 336 four-hour rows`

Therefore:

```text
0048 complete dependence blocks        4
0053 Track A complete blocks            4
net effective-block gain                0
```

This is the key result: **the row count increased, but the amount of independent calendar-time support did not.**

Track A's first formal origin was `2025-01-14T16:00:00Z`, essentially the same calendar date as 0048's `2025-01-14` formal start. That directly shows that preserving the two long calendar-equivalent support burn-ins consumes nearly the same calendar history even at 4h resolution.

## Where the bottleneck actually is

The diagnostic tracks isolate the source of attrition.

### Track B — raw-row multiplication diagnostic

```text
training support       365 4h eligible origins
shadow support         365 4h shadow origins
block length            56 4h rows
formal rows          5,493
complete blocks          98
```

This is **not** genuine evidence of 98 independent 56-day blocks. A 56-bar block at 4h resolution is only about 9.3 days. Track B deliberately demonstrates how changing bar frequency can create apparent sample size without preserving the original dependence horizon.

### Track C — earlier-burn-in diagnostic with honest dependence scale

```text
training support       365 4h eligible origins
shadow support         365 4h shadow origins
block length           336 4h rows = 56 days equivalent
formal rows          5,493
complete blocks          16
```

Track C is the important diagnostic. It preserves the 56-day-equivalent dependence block but starts formal support on `2022-02-15T20:00:00Z`, about three years earlier than Track A, and retains 16 complete blocks.

Therefore the evidence points to the **two 2,190-origin calendar-equivalent burn-ins** as the dominant bottleneck, rather than the 4h data frequency itself.

However Track C was frozen as diagnostic only. Its apparent adequacy cannot be promoted into a new predictive model under 0053 and cannot rescue 0048.

## What this result does not say

0053 did not compute:

- ETH/SOL winner labels;
- realized leadership margins;
- logistic coefficients;
- calibration gamma;
- NLL, Brier, AUC or balanced accuracy;
- confidence curves or HIGH breakpoints;
- predictive bootstrap inference;
- portfolio weights, CAGR or MDD.

Therefore this result says only that strict calendar-equivalent 4h support is insufficient. It does **not** say whether a properly designed 4h ETH/SOL leadership signal is predictive.

## Recommended scientific continuation

Do not reduce Track A from 2,190 to 365 and rerun 0053. That would be result-informed rescue.

The justified next question is a **new research ID**:

> What minimum 4h-native training and calibration support is statistically defensible for this low-dimensional relative-leadership model, given serial dependence and regime nonstationarity?

The new ID must treat the observed Track C result (16 blocks at 365/365/336) as exposed evidence and therefore must not simply choose 365 because it looked convenient after this result.

0048 remains closed. 0053 is closed. 0049 winner-concentration research remains blocked until a separately preregistered predictive leadership stage actually passes.

## Authority

```text
same-ID rerun                  false
same-ID retuning               false
same-ID rescue                 false
predictive model executed      false
portfolio economics executed   false
canonical BRRK changed         false
Phase 6 changed                false
production_authorized          false
signature_authorized           false
order_submission_authorized    false
```
