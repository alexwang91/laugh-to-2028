# BRRK Next Steps

Last updated: 2026-08-07

## Current instruction

**P5.3 state-model structure is preregistered before state-path evaluation. Validate and merge the frozen structure, then implement all three preregistered profiles exactly as written against the immutable P5.2 feature panel. Do not alter P5.1/P5.2, add post-result features, or choose P5.4 gross multipliers.**

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
P5.3 prereg correction                 P5.3-PREREG-COMPLETENESS-R1 / BEFORE ANY STATE PATH
P5.3 structure                         PREREGISTERED / FROZEN BEFORE STATE-PATH EVALUATION
P5.3 state paths                       NOT RUN
P5.4-P5.6                              NOT STARTED
```

## Frozen P5.3 state vocabulary

```text
NORMAL_BULL
BTC_LEADERSHIP_MATURING
LATE_BULL_ROTATION
EXHAUSTION_WATCH
DE_RISK_1
DE_RISK_2
FLAT
```

Before initialization, `DATA_INSUFFICIENT` is emitted as a research diagnostic, not a market state. `MONITOR_ONLY` remains a runtime/human-control state after FLAT.

## Frozen evidence architecture

### REGIME_TEXTURE

- BTC RV20;
- BTC RV20/RV60;
- distance from trailing 90d high;
- KAMA gap.

Purpose: maturity/high-level/volatility context only. It cannot trigger de-risk alone.

### LEADERSHIP_ROTATION

- ETH/BTC 20d / 40d;
- BNB/BTC 40d secondary context;
- breadth acceleration;
- canonical-five outperformance breadth.

Purpose: identify late-bull rotation. ETH/BTC/alt strength is **not automatically bearish**.

### EXHAUSTION_TRANSITION

- price-vs-RSI rank divergence;
- RSI14 failure from recent maximum;
- daily RSI14;
- completed-4h RSI14 / RSI28;
- breadth acceleration / contraction.

Purpose: require multiple independent exhaustion/failure channels. Raw RSI alone is insufficient.

### TREND_DAMAGE

- KAMA gap;
- distance from trailing high;
- BTC 20d return;
- BTC 40d return.

Purpose: confirm structural deterioration before ordinary de-risk escalation.

## Frozen causal normalization

For every continuous runtime feature at date `t`:

```text
window          last up to 365 completed daily dates ending at t
missing         drop missing rows for that feature
minimum N       20 nonmissing feature observations
percentile      (average_rank(current) - 1) / (N - 1)
range           [0,1]
ties            average rank
future data     forbidden
20 <= N < 365   use causal available history and report N
N < 20          feature unavailable
```

The initial `252`-observation text was corrected **before any P5.3 state path was run** because it would exclude required early-2021 taxonomy windows. The exact percentile formula was also frozen at the same pre-evaluation correction.

The path remains `DATA_INSUFFICIENT` until every continuous runtime input used by the state atoms has at least 20 observations. CI must prove initialization is possible by `2021-01-31`, the earliest frozen control `early_warning` date. Calibration depth is a required output.

After initialization, missing evidence cannot de-escalate or automatically re-add risk.

P5.2 robust-z is a research diagnostic only. It is not a P5.3 runtime feature.

## Frozen sensitivity profiles

| Profile | Moderate high/low | Strong high/low | Escalation | De-escalation clear |
| --- | --- | --- | ---: | ---: |
| EARLY | 0.65 / 0.35 | 0.80 / 0.20 | 2d | 5d |
| BALANCED | 0.70 / 0.30 | 0.85 / 0.15 | 3d | 5d |
| CONSERVATIVE | 0.75 / 0.25 | 0.90 / 0.10 | 3d | 7d |

All three must be evaluated. They are sensitivity cases, not free knobs after results.

## Frozen evidence atoms / candidate-state priority

Exact rules live in `research/cycle_exit/p5_3_state_model_contract.json`.

Conceptual priority:

```text
STRONG_DAMAGE + STRONG_EXHAUSTION      -> FLAT
strong damage/exhaustion combinations -> DE_RISK_2
DAMAGE + EXHAUSTION                    -> DE_RISK_1
EXHAUSTION                             -> EXHAUSTION_WATCH
ROTATION and not DAMAGE                -> LATE_BULL_ROTATION
MATURE_TEXTURE and not DAMAGE          -> BTC_LEADERSHIP_MATURING
otherwise                              -> NORMAL_BULL
```

Ordinary escalation requires persistence. De-escalation requires a clear period and may move at most one state/day. Hard strong-damage + strong-exhaustion may jump directly to FLAT. FLAT is absorbing inside P5.3 and re-entry requires explicit human approval outside this research layer.

## P5.3 implementation outputs — NEXT

Implement deterministic EARLY/BALANCED/CONSERVATIVE state paths from the immutable P5.2 feature panel and report:

- complete daily state path;
- per-feature normalization observation counts;
- minimum calibration depth by date;
- `DATA_INSUFFICIENT` range and initialization date;
- event-window state occupancy;
- first entry dates per state;
- lead/lag versus frozen P5.1 anchors;
- transition and churn counts;
- second-wind false-terminal / FLAT behavior;
- conservative-state occupancy in non-top controls;
- missing-data diagnostics;
- profile sensitivity.

P5.3 does **not** need to force 7–14 day warning. It reports whether the frozen structure naturally produces useful lead.

## P5.3 selection boundary

P5.3 may identify a research profile/candidate worth carrying to P5.4/P5.5, but:

- it may not select a production state model;
- it may not select solely on 2021 November;
- it may not add/delete/reparameterize features after state paths are observed;
- it may not select P5.4 gross-risk multipliers;
- P5.5 owns robustness selection after P5.4 behavior/economic mapping exists.

## P5.4 — later

Map accepted state semantics to total directional risk while keeping BRRK relative ranking unchanged.

```text
BRRK        = which assets / relative weights
Cycle layer = how much total directional risk
Router      = which instruments
Execution   = safe realization
```

## P5.5 — later validation

Must report:

- lead/lag distribution;
- false-positive duration;
- missed upside;
- drawdown avoided;
- terminal wealth impact;
- second-wind behavior;
- state churn/persistence;
- behavior with the sole terminal event held out.

Any rule requiring 2021-specific or 2025-specific hand tuning fails robustness.

## Frozen pending data

Do not proxy these names until a separate data authority is validated:

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
IF GREEN, MERGE THE PREREGISTRATION
VERIFY NEW MAIN
CREATE P5.3 IMPLEMENTATION BRANCH FROM THAT MAIN
IMPLEMENT THE THREE FROZEN PROFILES EXACTLY
RUN DETERMINISTIC STATE-PATH EVIDENCE
DO NOT RETUNE AFTER OBSERVING STATE PATHS
DO NOT START P5.4 GROSS MAPPING UNTIL P5.3 EVIDENCE IS REVIEWABLE
```
