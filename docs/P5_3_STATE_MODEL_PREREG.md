# P5.3 State Model — Preregistration

Status: **FROZEN BEFORE STATE-PATH EVALUATION**  
Contract: `P5.3-STATE-MODEL-STRUCTURE-V1`  
Base main: `4b5f41b449b2e9ac3d8ec9125644bc0a10e36963`

## Objective

Build a causal multi-state cycle-risk classifier that distinguishes normal bull continuation, BTC leadership maturation, late-bull rotation, exhaustion and progressively stronger de-risk states without turning any single indicator into a cycle-top switch.

P5.3 is not a BRRK retune. BRRK remains responsible for relative asset ranking. The cycle state model classifies total directional-risk state; exact gross multipliers belong to P5.4.

## Frozen dependencies

P5.3 consumes but may not rewrite:

- `P5.1-EVENT-TAXONOMY-V1`;
- immutable `P5.2-FEATURE-FAMILIES-V1` result;
- P5.2 summary SHA256 `3f6dc3c512d22ac8f71d43ed155f2602cd40d5caf3d617c0e130e170727e0627`;
- P5.2 descriptive closeout constraints.

Only one P5.1 event is explicitly terminal. Terminal-specific behavior is therefore hypothesis-generating until later validation; P5.3 may not hand-tune a rule to 2021 November and call it cross-cycle evidence.

## Pre-evaluation completeness corrections

Both corrections below were made **before any P5.3 state path was evaluated**.

### R1 — percentile and early-history calibration

`P5.3-PREREG-COMPLETENESS-R1` froze:

1. the exact empirical-percentile mapping;
2. a 365 completed-date maximum causal window;
3. a minimum of 20 nonmissing observations per normalized feature;
4. `DATA_INSUFFICIENT` pre-initialization semantics;
5. mandatory calibration-depth reporting.

The original 252-feature-observation idea would exclude required early-2021 windows because immutable P5.2 starts 2020-10-01 and several features have their own warm-up periods. CI must prove all continuous runtime inputs are calibrated by `2021-01-31`.

### R2 — deterministic hysteresis and dead-input removal

`P5.3-PREREG-COMPLETENESS-R2` froze the exact state-transition algorithm so independent implementations cannot choose different escalation/de-escalation behavior. It also removed two dead runtime inputs that no frozen evidence atom actually referenced:

- `bnb_btc_log_return_40d`;
- `btc_daily_rsi14`.

R2 changes no profile percentile, evidence-atom threshold, P5.1/P5.2 artifact or production boundary.

## State vocabulary

```text
NORMAL_BULL
BTC_LEADERSHIP_MATURING
LATE_BULL_ROTATION
EXHAUSTION_WATCH
DE_RISK_1
DE_RISK_2
FLAT
```

The same list is the exact `severity_order`, from least to most conservative.

Before enough causal feature history exists, the research path emits `DATA_INSUFFICIENT`. This is a pre-initialization diagnostic, not a market-risk state.

`MONITOR_ONLY` remains a downstream runtime/human-control state after FLAT rather than a P5.3 market-state classification.

## Why a state machine instead of a top score

P5.2 showed that:

- volatility context separates many event windows from high-vol controls but is not terminal-specific;
- ETH/BTC leadership is strong in terminal and second-wind/nonterminal structures;
- price-versus-RSI divergence is unusually strong in the sole 2021 terminal lead window but has only one terminal positive example;
- breadth acceleration is transition evidence, not a terminal switch;
- raw RSI is not uniquely terminal;
- some discrete breadth variables cannot be ranked fairly with robust-z when control MAD is zero.

Therefore P5.3 uses complementary evidence channels and explicit state semantics rather than a weighted scalar chosen after seeing one historical top.

## Runtime evidence groups

### REGIME_TEXTURE

- BTC RV20;
- BTC RV20/RV60;
- distance from trailing 90d high;
- KAMA gap.

This channel identifies mature/high-level/low-vol texture. It may enter `BTC_LEADERSHIP_MATURING`; it cannot de-risk on its own.

### LEADERSHIP_ROTATION

- ETH/BTC 20d relative strength;
- ETH/BTC 40d relative strength;
- breadth acceleration;
- canonical-five outperformance breadth.

Canonical-five breadth is used as its raw `[0,1]` fraction for the frozen 0.75 confirmation rule. It is not percentile-normalized for that threshold.

This channel identifies `LATE_BULL_ROTATION`. ETH/BTC or breadth strength alone is not bearish.

### EXHAUSTION_TRANSITION

- 20d price-vs-RSI rank divergence;
- RSI14 failure from recent maximum;
- completed-4h RSI14;
- completed-4h RSI28;
- breadth acceleration;
- breadth contraction.

Raw RSI alone cannot activate the full exhaustion rule. At least two independent divergence / momentum-failure / breadth-transition subchannels are required.

### TREND_DAMAGE

- KAMA gap;
- distance from trailing high;
- BTC 20d return;
- BTC 40d return.

At least two damage inputs must agree before ordinary de-risk states are eligible.

## Causal normalization

For each continuous feature independently at completed date `t`:

1. take the last up to 365 completed daily dates ending at `t`;
2. drop missing values for that feature only;
3. require at least 20 nonmissing observations;
4. rank the current value among those `N` values using average rank for ties;
5. compute:

```text
percentile = (average_rank - 1) / (N - 1)
```

The observed sample minimum maps to 0 and maximum to 1.

Additional rules:

- current `t` may be used only after the completed 00:00 UTC observation exists;
- future observations are forbidden;
- when `20 <= N < 365`, use the available causal history and report `N`;
- when `N < 20`, that normalized input is unavailable;
- the state path remains `DATA_INSUFFICIENT` until every continuous runtime input used by any evidence atom meets the minimum;
- per-feature observation count and minimum calibration depth by date are mandatory outputs.

The P5.2 robust-z-versus-controls statistic is a research diagnostic only and is **not** a runtime feature.

## Frozen sensitivity profiles

| Profile | Moderate high/low | Strong high/low | Escalation persistence | De-escalation clear |
| --- | --- | --- | ---: | ---: |
| EARLY | 0.65 / 0.35 | 0.80 / 0.20 | 2d | 5d |
| BALANCED | 0.70 / 0.30 | 0.85 / 0.15 | 3d | 5d |
| CONSERVATIVE | 0.75 / 0.25 | 0.90 / 0.10 | 3d | 7d |

All three profiles must be reported. They are sensitivity cases, not post-result tuning knobs.

## Evidence atoms

Exact machine rules are frozen in `research/cycle_exit/p5_3_state_model_contract.json`.

Conceptually:

```text
MATURE_TEXTURE
  = multiple mature/high-level regime-texture signals

ROTATION
  = ETH/BTC20 strength + at least one ETH/BTC40 / breadth confirmation

EXHAUSTION
  = at least two independent divergence / momentum-failure / breadth-transition subchannels

STRONG_EXHAUSTION
  = stronger divergence plus another exhaustion subchannel, or all three subchannels

DAMAGE
  = at least two trend-damage inputs

STRONG_DAMAGE
  = at least two strong-low trend-damage inputs including KAMA gap or distance-from-high
```

There is no unused `STRONG_ROTATION` state atom in V1.

## Raw candidate-state priority

```text
STRONG_DAMAGE + STRONG_EXHAUSTION      -> FLAT
strong damage/exhaustion combinations -> DE_RISK_2
DAMAGE + EXHAUSTION                    -> DE_RISK_1
EXHAUSTION                             -> EXHAUSTION_WATCH
ROTATION and not DAMAGE                -> LATE_BULL_ROTATION
MATURE_TEXTURE and not DAMAGE          -> BTC_LEADERSHIP_MATURING
otherwise                              -> NORMAL_BULL
```

Rotation is deliberately below exhaustion/de-risk priority but above generic maturity. This allows late-bull participation without confusing leadership migration with terminal damage.

## Exact transition / hysteresis algorithm

State comparisons use zero-based indices in `severity_order`.

### Initialization

On the first date when all required continuous inputs are calibrated:

- if fully evaluated raw candidate is `FLAT`, initialize directly to `FLAT`;
- otherwise initialize to `NORMAL_BULL`;
- reset escalation and de-escalation counters to zero.

### Ordinary escalation

When `raw_index > current_index`:

- accumulate an escalation streak only while every consecutive initialized date remains above the current state;
- reset the streak if `raw_index <= current_index` or the current state changes;
- after the profile persistence length is met, transition to the **minimum-severity raw candidate observed over the persistence window**;
- therefore a multi-state jump is allowed only to the strongest state continuously supported by every date in the window;
- reset both counters after transition.

### Hard FLAT

If the fully evaluated raw candidate is `FLAT`, enter `FLAT` immediately without ordinary persistence.

### Ordinary de-escalation

When `raw_index < current_index` and current state is not FLAT:

- accumulate a de-escalation streak only while every consecutive date remains below the current state;
- reset if `raw_index >= current_index` or current state changes;
- after the profile clear period, move **exactly one** severity step lower;
- reset both counters;
- every further de-escalation step requires a fresh clear period.

When `raw_index == current_index`, hold state and reset both ordinary counters.

### Missing data

Before initialization emit `DATA_INSUFFICIENT`.

After initialization, if any input required for ordinary raw-candidate evaluation is missing:

- hold current state;
- reset ordinary transition counters;
- do not de-escalate or re-risk because of missing data.

A missing-data day may still enter hard `FLAT` only if every normalized/raw input required to prove both `STRONG_DAMAGE` and `STRONG_EXHAUSTION` is present and both atoms are true. Otherwise missing data cannot change state.

### FLAT

`FLAT` is absorbing inside P5.3. `FLAT -> risk-on` requires explicit human approval outside this research classifier.

No P5.3 intraday risk addition is allowed.

## Required P5.3 research outputs

For EARLY, BALANCED and CONSERVATIVE report:

- complete daily state path;
- raw candidate state and evidence-atom booleans by date/profile;
- per-feature normalization observation count and minimum calibration depth by date;
- `DATA_INSUFFICIENT` date range and initialization date;
- event-window state occupancy;
- first entry into each later-cycle state;
- lead/lag versus frozen P5.1 anchors;
- transition/churn counts;
- second-wind false-terminal / FLAT behavior;
- conservative-state occupancy in non-top controls;
- missing-data behavior;
- profile sensitivity.

P5.3 may identify a research candidate for downstream work, but **P5.5 owns robustness selection after P5.4 behavior/economic mapping exists**.

## Explicitly excluded pending data

Until a separately validated data authority exists, P5.3 does not use or proxy:

- BTC dominance;
- broad-market breadth;
- historical funding;
- historical OI;
- historical basis/premium;
- liquidation proxy.

## Forbidden

- moving P5.1 events or anchors;
- mutating P5.2 evidence;
- adding a feature after seeing P5.3 state paths;
- using future observations in percentile normalization;
- using P5.2 robust-z as a live input;
- ETH/BTC leadership alone -> bearish;
- raw RSI alone -> top;
- low volatility alone -> top;
- automatic exit from FLAT;
- rewriting BRRK relative ranking;
- choosing P5.4 gross multipliers here;
- production authorization.

## Completion boundary

This preregistration is complete when its contract, tests and governance are green and merged. The next P5.3 step is deterministic implementation of the three frozen profiles against the immutable P5.2 feature panel.
