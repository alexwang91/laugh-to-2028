# AUDIT-0023 Result — Extra-Beta Intra-Refit Latency Is Real but Not the Whole Tail Problem

`AUDIT-0023-LATENCY` is a **no-trading-change attribution audit** authorized by the `ASYM-BETA-0022` drawdown result. It does not change weights or calculate a promoted strategy.

## Status

**LATENCY DEFECT VALIDATED, PARTIAL EXPLANATION ONLY.**

GitHub Actions run `30958047983` completed successfully. The audit keeps each monthly HMM and raw-state risk distribution frozen; only the causal filtered posterior, existing BTC trend score and existing 30-day downside semivol are updated each completed day.

The diagnostic daily implied extra uses the already-frozen 0022 arithmetic. No alternative threshold, refit cadence, window or volatility anchor is tested.

## Aggregate result

Across the **21 monthly intervals** in which 0022 had positive extra beta, covering 630 active daily rows:

- daily implied extra is below the monthly-held extra on **53.81%** of active days;
- 13 / 21 active intervals cross below **75%** of their monthly-held extra;
- 8 / 21 cross below **50%**;
- 5 / 21 cross below **25%**;
- median time after refit to those descriptive crossings is **7 / 12.5 / 17 days** respectively;
- total positive held-minus-implied gap is **27.13 extra-exposure-days**;
- **16.35 extra-exposure-days** of that gap occur on negative BTC days.

These levels are descriptive latency diagnostics only; they are not authorized trading thresholds.

## June 2024 — strong latency evidence

The monthly refit on 2024-06-01 approved **+0.3461x** extra beta.

Without retraining the HMM, daily causal updates of the already-defined diagnostics imply:

- <=75% of monthly extra by **2024-06-09** (8 days after refit);
- <=50% by **2024-06-18**;
- <=25% by **2024-06-24**;
- minimum implied ratio **3.35%** on **2024-06-28**.

During June:

- monthly-held extra: 0.3461x;
- mean daily implied extra: **0.1941x**;
- mean implied/held ratio: **56.08%**;
- excess exposure-days: **4.57**;
- excess exposure-days on negative BTC days: **2.78**;
- daily trend falls as low as **0.031**;
- daily `p_bad` rises as high as **0.256**.

This validates the hypothesis that the 30-day overlay holding cadence was materially stale during the June loss window.

## April 2024 — latency does not solve the dominant early drawdown

April is different.

Across 2024-04-01 through 2024-04-30:

- mean monthly-held extra: **0.2927x**;
- mean daily implied extra: **0.3161x**;
- mean implied/held ratio: **108.03%**;
- minimum implied/held ratio: **61.21%**, reached only on **2024-04-30**;
- `p_bad` never rises above approximately **0.0010**;
- trend remains positive, minimum approximately **0.356**;
- downside semivol rises to about **54.63%**, but the frozen 45% scaler only partially reduces extra.

Therefore the existing daily diagnostics would generally have maintained, and often requested more, extra exposure during most of April. Faster refresh alone cannot explain or fix the approximately 6 percentage points of incremental April loss identified by 0022.

## Other latency evidence

The largest latency-gap interval begins 2023-07-07:

- monthly extra 0.3144x;
- daily implied extra crosses 75% after 7 days, 50% after 14 days and 25% after 17 days;
- minimum implied ratio 18.20%;
- `p_bad` rises as high as 0.621.

A similar pattern appears in several other active intervals, supporting a general cadence defect rather than a one-episode accident.

## Interpretation

The audit establishes two separate facts:

1. **Overlay latency is real.** The 30-day BRRK refit cadence is too slow for the extra-beta risk sleeve in many intervals. Existing information frequently weakens well before the next refit.
2. **Latency is not sufficient.** April 2024 remains a distinct failure where the existing `trend + p_bad + downside semivol` information itself did not flag the reversal early enough.

This distinction matters. It would be invalid to respond by tuning the semivol anchor or inventing a new April-specific threshold under the same experiment family.

## Authorized next step

Exactly one structural change is authorized next:

> Keep BRRK core and the monthly 0022 approved extra unchanged, but allow the **already-defined daily implied extra** to act as a daily cap on the incremental sleeve between monthly refits.

The next test must not allow daily information to increase exposure above the monthly approved extra. It may only reduce/release that cap. No HMM daily refit, no new risk variable, no SOL tilt and no new threshold are authorized.

That experiment will quantify the value of fixing latency alone. If April remains the dominant tail problem afterward, a separate no-trading-change audit must identify what new mechanism is needed before adding another risk variable.
