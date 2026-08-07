# P5.3 State Model — Preregistration

Status: **FROZEN BEFORE STATE-PATH EVALUATION**  
Contract: `P5.3-STATE-MODEL-STRUCTURE-V1`  
Base main: `4b5f41b449b2e9ac3d8ec9125644bc0a10e36963`

## Objective

Build a causal multi-state cycle-risk classifier that can distinguish normal bull continuation, BTC leadership maturation, late-bull rotation, exhaustion and progressively stronger de-risk states without turning any single indicator into a cycle-top switch.

P5.3 is not a BRRK retune. BRRK remains responsible for relative asset ranking. The cycle state model describes **how much total directional risk should eventually be permitted**, with exact gross multipliers deferred to P5.4.

## Frozen dependencies

P5.3 consumes, but may not rewrite:

- `P5.1-EVENT-TAXONOMY-V1`;
- immutable `P5.2-FEATURE-FAMILIES-V1` result;
- P5.2 summary SHA256 `3f6dc3c512d22ac8f71d43ed155f2602cd40d5caf3d617c0e130e170727e0627`;
- P5.2 descriptive closeout constraints.

Only one P5.1 event is explicitly terminal. Any terminal-specific behavior is therefore hypothesis-generating until later validation; P5.3 may not hand-tune a rule to 2021 November and call it cross-cycle evidence.

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

`MONITOR_ONLY` remains a downstream control/runtime state after FLAT rather than a P5.3 market-state classification.

## Why a state machine instead of a top score

P5.2 showed that:

- volatility context separates many event windows from high-vol controls, but is not terminal-specific;
- ETH/BTC leadership is strong in terminal and second-wind/nonterminal structures;
- price-versus-RSI divergence is unusually strong in the sole 2021 terminal lead window, but has only one terminal positive example;
- breadth acceleration is a transition feature, not a terminal switch;
- raw RSI is not uniquely terminal;
- some discrete breadth variables cannot be ranked fairly using robust-z when control MAD is zero.

Therefore P5.3 uses complementary evidence channels and explicit state semantics rather than a weighted scalar chosen after seeing one historical top.

## Runtime evidence groups

### REGIME_TEXTURE

- BTC RV20;
- BTC RV20/RV60;
- distance from trailing 90d high;
- KAMA gap.

This channel identifies mature/high-level/low-vol texture. It may enter `BTC_LEADERSHIP_MATURING`; it cannot de-risk on its own.

### LEADERSHIP_ROTATION

- ETH/BTC 20d and 40d relative strength;
- BNB/BTC 40d secondary context;
- breadth acceleration;
- canonical-five outperformance breadth.

This channel identifies `LATE_BULL_ROTATION`. ETH/BTC or breadth strength alone is not bearish.

### EXHAUSTION_TRANSITION

- 20d price-vs-RSI rank divergence;
- RSI14 failure from recent maximum;
- daily RSI14;
- completed-4h RSI14/28;
- breadth acceleration/contraction.

Raw RSI alone cannot activate the full exhaustion rule. At least two independent subchannels are required.

### TREND_DAMAGE

- KAMA gap;
- distance from trailing high;
- BTC 20d return;
- BTC 40d return.

At least two damage inputs must agree before ordinary de-risk states are eligible.

## Causal normalization

Continuous inputs use a trailing empirical percentile over the latest 365 completed daily observations with at least 252 observations required.

At date `t`:

- only observations available by `t` are used;
- the current completed observation may be included;
- future observations are forbidden;
- average rank handles ties;
- missing required evidence cannot de-escalate or automatically re-add risk.

The P5.2 robust-z-versus-controls statistic is a research diagnostic only and is **not** a runtime feature.

## Frozen sensitivity profiles

Three profiles are preregistered before any P5.3 state path is computed:

| Profile | Moderate high/low | Strong high/low | Escalation persistence | De-escalation clear |
| --- | --- | --- | ---: | ---: |
| EARLY | 0.65 / 0.35 | 0.80 / 0.20 | 2d | 5d |
| BALANCED | 0.70 / 0.30 | 0.85 / 0.15 | 3d | 5d |
| CONSERVATIVE | 0.75 / 0.25 | 0.90 / 0.10 | 3d | 7d |

These are sensitivity profiles, not three opportunities to post-result tune a winner. P5.3 reports all three. Later selection may not be based solely on the 2021 terminal event.

## Evidence atoms

The exact machine rules are frozen in `research/cycle_exit/p5_3_state_model_contract.json`.

Conceptually:

```text
MATURE_TEXTURE
  = multiple mature/high-level regime-texture signals

ROTATION
  = ETH/BTC leadership + at least one confirming persistence/breadth signal

EXHAUSTION
  = at least two independent divergence/momentum-failure/breadth-transition subchannels

DAMAGE
  = at least two trend-damage inputs

STRONG_* atoms
  = stricter percentile variants under the same feature definitions
```

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

Rotation is deliberately evaluated below exhaustion/de-risk priority but above generic maturity. This allows the system to participate in late-bull leadership migration without confusing it with terminal damage.

## Transition / hysteresis rules

- official state decision boundary: 00:00 UTC daily;
- ordinary escalation requires profile-specific persistence;
- hard `STRONG_DAMAGE + STRONG_EXHAUSTION` may enter FLAT immediately;
- de-escalation requires a profile-specific clear period;
- de-escalation moves at most one state per completed daily decision;
- FLAT is absorbing inside P5.3;
- `FLAT -> risk-on` requires external explicit human approval;
- missing evidence may not de-escalate/re-risk;
- no intraday P5.3 risk addition.

## Required P5.3 research outputs

For EARLY, BALANCED and CONSERVATIVE report:

- complete daily state path;
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

This preregistration is complete when its contract and governance tests are green and merged. The next P5.3 step is deterministic implementation of the three frozen profiles against the immutable P5.2 feature panel.
