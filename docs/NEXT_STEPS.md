# BRRK Next Steps

Last updated: 2026-08-07

## Current instruction

**P5.3 state-model structure is preregistered before state-path evaluation. Validate/merge the final R1+R2 contract, then implement EARLY/BALANCED/CONSERVATIVE exactly as frozen against immutable P5.2 evidence. Do not alter P5.1/P5.2, add post-result features, or choose P5.4 gross multipliers.**

## Immediate state

```text
Phase 0-3                              COMPLETE / MERGED
LEVERAGE-0040 / 0041                   COMPLETE / IMMUTABLE / NO_PROMOTION
Phase 4 leverage research              FAIL_STOP
production gross cap                   1.0
production_authorized_components       []
P5.1 event taxonomy                    COMPLETE / MERGED / FROZEN
P5.2 feature evidence                  COMPLETE / IMMUTABLE / DESCRIPTIVE CLOSEOUT
P5.2 summary SHA256                    3f6dc3c512d22ac8f71d43ed155f2602cd40d5caf3d617c0e130e170727e0627
P5.3 structure contract                P5.3-STATE-MODEL-STRUCTURE-V1
P5.3 prereg corrections                R1 + R2 / BOTH BEFORE ANY STATE PATH
P5.3 structure                         PREREGISTERED / FROZEN BEFORE STATE-PATH EVALUATION
P5.3 state paths                       NOT RUN
P5.4-P5.6                              NOT STARTED
```

## Frozen state vocabulary / severity order

```text
NORMAL_BULL
BTC_LEADERSHIP_MATURING
LATE_BULL_ROTATION
EXHAUSTION_WATCH
DE_RISK_1
DE_RISK_2
FLAT
```

Before initialization, `DATA_INSUFFICIENT` is a diagnostic rather than a market state. `MONITOR_ONLY` remains a downstream human/runtime control state.

## Frozen runtime evidence

### REGIME_TEXTURE
- BTC RV20;
- BTC RV20/RV60;
- distance from trailing high;
- KAMA gap.

### LEADERSHIP_ROTATION
- ETH/BTC 20d;
- ETH/BTC 40d;
- breadth acceleration;
- canonical-five breadth raw fraction.

### EXHAUSTION_TRANSITION
- price-vs-RSI rank divergence;
- RSI14 failure from recent max;
- completed-4h RSI14 / RSI28;
- breadth acceleration / contraction.

### TREND_DAMAGE
- KAMA gap;
- distance from trailing high;
- BTC 20d / 40d return.

R2 removed `bnb_btc_log_return_40d` and `btc_daily_rsi14` from runtime inputs because no frozen evidence atom referenced them. No evidence threshold was changed.

Core semantics remain:

```text
volatility alone            != top
ETH/BTC leadership alone    != bearish
raw RSI alone               != top
rotation without damage     -> LATE_BULL_ROTATION candidate
exhaustion without damage   -> EXHAUSTION_WATCH candidate
exhaustion + damage         -> de-risk candidate
strong exhaustion + damage  -> hard-risk / FLAT candidate
```

## Frozen causal normalization

```text
window          last up to 365 completed daily dates ending at t
missing         drop missing feature-by-feature
minimum N       20 nonmissing feature observations
percentile      (average_rank(current) - 1) / (N - 1)
ties            average rank
future data     forbidden
20 <= N < 365   use causal available history and report N
N < 20          feature unavailable
```

Path remains `DATA_INSUFFICIENT` until every continuous runtime input is calibrated. CI must prove that is possible by `2021-01-31`. After initialization, missing data cannot cause de-escalation or automatic re-risk.

P5.2 robust-z is research diagnostics only, not a runtime feature.

## Frozen profiles

| Profile | Moderate high/low | Strong high/low | Escalation | Clear |
| --- | --- | --- | ---: | ---: |
| EARLY | 0.65 / 0.35 | 0.80 / 0.20 | 2d | 5d |
| BALANCED | 0.70 / 0.30 | 0.85 / 0.15 | 3d | 5d |
| CONSERVATIVE | 0.75 / 0.25 | 0.90 / 0.10 | 3d | 7d |

## Frozen raw-candidate priority

```text
STRONG_DAMAGE + STRONG_EXHAUSTION      -> FLAT
strong damage/exhaustion combinations -> DE_RISK_2
DAMAGE + EXHAUSTION                    -> DE_RISK_1
EXHAUSTION                             -> EXHAUSTION_WATCH
ROTATION and not DAMAGE                -> LATE_BULL_ROTATION
MATURE_TEXTURE and not DAMAGE          -> BTC_LEADERSHIP_MATURING
otherwise                              -> NORMAL_BULL
```

## Exact R2 hysteresis mechanics

- first fully calibrated date: raw FLAT initializes FLAT; otherwise initialize NORMAL_BULL;
- ordinary escalation counts only consecutive `raw > current` days;
- after persistence, jump only to the **minimum raw severity continuously supported throughout that window**;
- fully evaluated raw FLAT enters immediately;
- ordinary de-escalation counts only consecutive `raw < current` days;
- after clear period, move exactly one severity step lower;
- each further de-escalation step needs a fresh clear period;
- `raw == current` resets both counters;
- ordinary missing-data day holds state and resets counters;
- missing-data hard FLAT is allowed only if every input needed to prove both strong atoms is present and both are true;
- FLAT is absorbing; re-risk requires explicit human approval outside P5.3.

## P5.3 implementation outputs — NEXT

Implement all three profiles and report:

- complete daily state path;
- raw candidate + atom booleans;
- per-feature normalization counts / minimum calibration depth;
- initialization date / `DATA_INSUFFICIENT` range;
- event-window occupancy;
- first entries and lead/lag versus P5.1 anchors;
- transition/churn counts;
- second-wind false-terminal / FLAT behavior;
- non-top-control conservative-state occupancy;
- missing-data diagnostics;
- profile sensitivity.

P5.3 does not need to force 7–14 day warning; it reports whether useful lead emerges naturally.

## Selection boundary

P5.3 may identify a research profile worth carrying to P5.4/P5.5, but may not:

- select a production state model;
- select solely on 2021 November;
- add/delete/reparameterize features after state paths;
- choose P5.4 gross multipliers;
- authorize production.

P5.5 owns robustness selection after P5.4 behavior/economic mapping exists.

## Frozen pending data

Do not proxy until separately validated:

- BTC dominance;
- broad-market breadth;
- historical funding;
- historical OI;
- historical basis/premium;
- liquidation proxy.

## Frozen product boundaries

- BRRK-0011 relative ranking unchanged;
- BTC/ETH/SOL/BNB long universe unchanged;
- XRP feature-only;
- Hyperliquid primary venue;
- P4.1 defensive scaler `[0,1]` unchanged;
- production gross `1.0`;
- no withdrawal/external-transfer automation;
- no production authorization.

## Exact next step

```text
RUN FRESH P5.3 PREREG CI / GOVERNANCE
IF GREEN, MERGE #99 WITH EXACT HEAD
VERIFY NEW MAIN
CREATE FRESH P5.3 IMPLEMENTATION BRANCH
IMPLEMENT R1+R2 CONTRACT EXACTLY
RUN CONTROLLED DETERMINISTIC STATE-PATH EVIDENCE
DO NOT RETUNE AFTER OBSERVING STATE PATHS
DO NOT START P5.4 GROSS MAPPING UNTIL P5.3 EVIDENCE IS REVIEWABLE
```
