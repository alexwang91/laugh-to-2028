# BRRK-LEADERSHIP-INTRADAY-SUPPORT-0053 — Design Freeze

**Date:** 2026-08-11  
**Research ID:** `BRRK-LEADERSHIP-INTRADAY-SUPPORT-0053`  
**Research family:** `BRRK_DYNAMIC_LEADERSHIP_ROUTER`  
**Stage:** SUPPORT FEASIBILITY ONLY  
**Status:** DESIGN FROZEN CANDIDATE / NO DATA RETRIEVAL / NO MODEL FIT / NO PREDICTIVE RESULT

## 1. Motivation

`BRRK-LEADERSHIP-ROTATION-0048` closed as:

`MEASUREMENT_INCONCLUSIVE_INSUFFICIENT_SUPPORT / CLOSED`

The binding failure was G1: only 4 complete 56-observation formal blocks were available versus 12 preregistered, with 245 formal rows versus a minimum 672 implied by that gate. 0048 cannot be rerun, retuned or rescued.

0053 is a new result-informed research ID. It does **not** ask whether the 0048 model predicts ETH/SOL leadership. It asks a narrower question:

> If BTC/ETH/SOL are represented at 4-hour resolution over the same approximately six-year historical span, does the complete causal support pipeline leave materially more dependence-aware formal support, or does 4h merely multiply highly correlated rows without increasing effective time support?

## 2. Scientific object

0053 is strictly **label-blind support accounting**.

It may measure:
- common 4h market coverage;
- feature-valid bars;
- causal BTC-uptrend eligibility;
- target-availability/maturity dates;
- training burn-in completion dates;
- shadow-calibration burn-in completion dates;
- formal-evaluation row counts;
- dependence-block counts;
- calendar spans and attrition at each funnel stage.

It may **not** compute or release:
- ETH/SOL winner labels;
- realized leadership margin;
- NLL, Brier, AUC, balanced accuracy;
- fitted logistic coefficients;
- fitted calibration gamma;
- confidence curves or breakpoints;
- bootstrap predictive superiority;
- portfolio weights, CAGR, MDD or concentration economics.

No predictive model is fit under 0053.

## 3. Data universe

Primary symbols:
- `BTCUSDT`
- `ETHUSDT`
- `SOLUSDT`

Venue: Binance Spot.  
Bar interval: `4h`.  
Timestamp standard: UTC.  
Required fields: open time, close time, OHLC, volume, quote volume, trades where available.

Target historical span is the same economic window used by 0048 where common 4h coverage permits:

`2020-08-11 00:00 UTC` through `2026-08-02 20:00 UTC` inclusive.

If exact common coverage starts later because a symbol lacks 4h bars at the requested start, the mechanically observed common start is reported; no synthetic backfill or cross-venue substitution is allowed.

The eventual data-retrieval stage must freeze the exact payload and SHA-256 before feasibility measurement.

## 4. Four-hour translation of 0048 calendar semantics

Six 4h bars equal one calendar day.

The following calendar-equivalent translations are fixed for feasibility accounting:

### Feature lookbacks
- 20d -> 120 bars
- 60d -> 360 bars
- 120d -> 720 bars
- 240d -> 1440 bars

The four non-overlapping 0048 age buckets therefore become:
- K1 equivalent: most recent 120 bars
- K2 equivalent: preceding 240 bars
- K3 equivalent: preceding 360 bars
- K4 equivalent: preceding 720 bars

Maximum feature history remains 240 calendar days = 1440 bars.

### Forward target availability only
0053 does not compute target values, but it must know when a hypothetical 0048-equivalent target would be fully mature:
- 14d -> 84 bars
- 28d -> 168 bars
- 56d -> 336 bars

Maximum target maturity = 336 bars.

### Refit clock
28 calendar days -> 168 bars.

### BTC trend eligibility
The canonical 20/60/120/240-day BTC trend family is translated to 4h calendar-equivalent horizons:
- 120 / 360 / 720 / 1440 bars
with the same FAST weights:
- 0.15 / 0.25 / 0.30 / 0.30.

The eligibility condition is the 4h calendar-equivalent analogue:

`BTC_TREND_FAST_4H >= 0`

This is used only for support counting.

## 5. Why 0053 uses three predeclared support clocks

The purpose is to separate genuine support improvement from artificial row multiplication. No clock may be selected as a predictive winner under 0053.

### Track A — STRICT CALENDAR-EQUIVALENT

This is the primary feasibility track and the only track allowed to answer whether 4h solves the **same support problem** as 0048.

- initial matured training support: `365 * 6 = 2190` eligible 4h origins;
- shadow-calibration support: `365 * 6 = 2190` matured eligible shadow origins;
- maximum label maturity: `336` bars;
- dependence block length: `56 * 6 = 336` ordered eligible formal rows;
- required complete dependence blocks: `12`.

No predictive fitting is performed; the 2190/2190 counts are support-clock counters only.

### Track B — RAW-ROW MULTIPLICATION DIAGNOSTIC

This diagnostic intentionally shows what happens if one naively carries the numeric counts from daily data into 4h data without preserving calendar time:

- training support: `365` eligible 4h origins;
- shadow support: `365` matured eligible 4h origins;
- dependence block length: `56` ordered eligible 4h rows;
- required complete blocks: `12`.

Track B has **zero authority** to claim adequate dependence-aware support. It exists to quantify how much apparent sample improvement comes only from cutting the same calendar time into smaller bars.

### Track C — HYBRID EARLIER-BURN-IN DIAGNOSTIC

This track tests whether the dominant bottleneck is the two 365-day-equivalent burn-ins rather than the final dependence scale:

- training support: `365` eligible 4h origins;
- shadow support: `365` matured eligible 4h origins;
- dependence block length: `336` ordered eligible 4h rows;
- required complete blocks: `12`.

Track C preserves the 56-calendar-day-equivalent dependence scale but uses 4h-native raw support counts for model/calibration warm-up. It is **diagnostic only** and cannot become a predictive specification under 0053.

Any later decision to use Track C-like burn-ins requires a new research ID and explicit statistical justification before any predictive result.

## 6. Funnel measurements

For each track, report mechanically:

1. raw common 4h bars;
2. bars lost to common-start alignment;
3. feature-valid bars after 1440-bar history requirement;
4. BTC-uptrend-eligible feature-valid bars;
5. first date at which training-support counter is satisfied;
6. first date at which a hypothetical shadow forecast may begin;
7. first date at which sufficient matured shadow forecasts exist;
8. first formal-evaluation origin;
9. last formal origin with a full 336-bar future maturity window;
10. formal evaluation rows;
11. complete dependence blocks;
12. trailing partial-block rows;
13. formal calendar span in days;
14. eligibility rate before and during formal evaluation;
15. attrition contribution attributable to each funnel stage.

0053 must additionally report the exact difference versus 0048:
- formal-row count ratio;
- complete-block count difference;
- formal-window start-date shift;
- formal-window calendar-span difference.

## 7. Primary feasibility classification

Primary authority belongs only to Track A.

### PASS_4H_CALENDAR_EQUIVALENT_SUPPORT_FEASIBLE

Requires Track A:

`complete_336_row_blocks >= 12`

with at least one full 336-bar maturity window remaining before the frozen dataset end.

Meaning:

> Four-hour data provide sufficient dependence-aware support under calendar-equivalent 0048 semantics to justify a separately preregistered 4h leadership-model study.

This does **not** establish predictive information.

### FAIL_4H_DOES_NOT_SOLVE_0048_SUPPORT_CONSTRAINT

If Track A has fewer than 12 complete 336-row blocks.

Meaning:

> Four-hour granularity does not solve the 0048 G1 support problem when calendar-equivalent burn-in and dependence scales are preserved.

Track B or C may still show more rows, but cannot overturn this classification.

### DATA_INTEGRITY_INCONCLUSIVE

If common 4h history is materially incomplete, non-contiguous, source identity cannot be frozen, or required fields cannot be reproduced reliably.

## 8. Interpretation rules

The study must explicitly distinguish:

`more rows != more independent time support`.

If Track B passes while Track A fails, the required interpretation is:

> The apparent support gain is predominantly a row-frequency artifact and not evidence that 4h resolves the original dependence-aware support deficit.

If Track C passes while Track A fails, the required interpretation is:

> Earlier burn-in could create a longer formal window, but that would be a new methodology choice informed by 0053; it requires a new preregistered study and cannot rescue 0048 or be silently promoted from 0053.

If Track A passes, a later 4h predictive study must still be separately preregistered and may not reuse 0048's observed adverse diagnostics for tuning.

## 9. Prohibitions

Under 0053:
- no ETH/SOL outcome labels;
- no model fitting;
- no calibration fitting;
- no feature selection;
- no alternate bar intervals such as 1h/2h/6h/8h/12h;
- no alternate venue or futures data;
- no lowering of the 12-block primary Track-A requirement after seeing counts;
- no portfolio testing;
- no 0049 concentration study;
- no Beta->BTC or BTC->cash rule;
- no canonical BRRK or Phase-6 change;
- no production/signing/order-submission authority.

## 10. Lineage

0053 is explicitly `RESULT_INFORMED` by 0048's immutable closeout:

`BRRK-LEADERSHIP-ROTATION-0048 -> BRRK-LEADERSHIP-INTRADAY-SUPPORT-0053`

The exposed 0048 point diagnostics (AUC ~0.379, candidate NLL ~0.7186, confidence-margin rho ~-0.411) are known background evidence and may not be used inside 0053 because 0053 does not evaluate predictions.

## 11. Governance sequence

Required order:

1. merge this 0053 design freeze;
2. preregister exact Binance 4h retrieval/data-integrity contract;
3. retrieve and hash-freeze BTC/ETH/SOL 4h payload once;
4. implement deterministic support-funnel counter only;
5. execute exactly one feasibility measurement;
6. immutable closeout;
7. only then decide whether a separate 4h predictive-leadership research ID is warranted.

At this design stage:

`actual_variants_evaluated = 0`

`model_fits = 0`

`predictive_results = 0`

`portfolio_runs = 0`

`production_authorized = false`
