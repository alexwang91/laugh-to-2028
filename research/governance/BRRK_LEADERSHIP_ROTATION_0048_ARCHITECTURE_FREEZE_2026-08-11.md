# BRRK-LEADERSHIP-ROTATION-0048 — Architecture Freeze

Date: 2026-08-11  
Status: **ARCHITECTURE FROZEN / NUMERICAL PREREG NOT YET FROZEN / NOT RUN**  
Required governance for any later result-bearing stage: `PROGRAM_GOVERNED_V1`  
Proposed research family: `BRRK_DYNAMIC_LEADERSHIP_ROUTER`  
Proposed domain: `RELATIVE_VALUE + RISK_CONTROL`  
Base main SHA: `54e70551555fd0c0b99660c8ddca0ca82e175332`

This document replaces the previously envisioned direct `0047 -> duration-aware BTC-to-Beta handoff model` continuation. It does **not** modify, reopen, rerun, rescue or reinterpret `BRRK-BETA-HANDOFF-EVENT-STUDY-0047`, which remains immutable `FAIL_NO_RECURRENT_DURABLE_HANDOFF_STRUCTURE / CLOSED`.

0048 is design-only. It creates no dataset registration, runner, historical measurement, candidate evaluation, portfolio result, canonical strategy change, Phase-6 change, signing authority or order-submission authority.

---

## 1. Core economic architecture

The revised strategy hypothesis is not a one-way `BTC -> Beta` clock. It is a two-dimensional router:

1. **Leadership** answers: _which crypto asset should receive the risk budget?_  
2. **Exhaustion / market risk** answers: _how much Beta should the portfolio still be willing to carry?_

The intended economic state progression is:

```text
confirmed crypto uptrend
    -> BTC leadership when BTC is the strongest/cleanest leader
    -> high-confidence winner concentration when ETH or SOL clearly becomes leader
    -> re-anchor to BTC when winner leadership reverses OR exhaustion rises materially
    -> reduce BTC gross toward cash only when broader market risk deteriorates further
```

The state machine is not required to move monotonically. Valid paths include:

```text
BTC -> SOL -> BTC -> ETH
BTC -> ETH -> BTC
BTC -> cash
SOL -> BTC without any cash move
```

The economic principle is frozen as:

> **Concentrate during verified upside leadership; re-anchor to BTC when leadership quality or market risk deteriorates; use cash only for broader gross-risk reduction.**

---

## 2. Binding evidence motivating the redesign

### 2.1 Winner lineage

`BRRK-WINNER-0001` and `BRRK-WINNER-ROBUSTNESS-0002` are result-informed DEVELOPMENT evidence that the existing single-alt branch can be too BTC-heavy after a genuine winner is already identified. The frozen `40/60` BTC/winner construction improved exposed-history CAGR materially while preserving drawdown and passed 10/20 bps robustness.

This motivates testing **more concentrated winner allocations in a later portfolio stage**, but does not prove that `80% / 90% / 100%` winner concentration is optimal.

### 2.2 Exhaustion lineage

`BRRK-EXHAUSTION-STATE-0044` remains immutable `PASS_TRIGGER_STAGE_ELIGIBLE`. Its CORE4 state showed useful continuous ranking/separation information on exposed history. `0045` and `0046` failed as discrete trigger translations.

Therefore the positive information from 0044 may later be used as a **risk-compression overlay**, but 0048 must not reinterpret failed 0045/0046 triggers as valid execution rules.

### 2.3 0047 negative result

0047 remains immutable `FAIL_NO_RECURRENT_DURABLE_HANDOFF_STRUCTURE / CLOSED`.

Binding negative evidence:

```text
target-eligible BTC-positive episodes = 27
frozen durable handoffs               = 12
prevalence                             = 44.44% < 50% gate
ETH causes                             = 3
SOL causes                             = 9
handoffs at state_age=1               = 8 / 12
BTC/ETH pooled XCF peak lag            = 0
BTC/SOL pooled XCF peak lag            = 0
one-switch oracle positive uplift      = 17 / 27
oracle-positive without frozen label   = 7 episodes
```

0047 therefore rejects the idea that `BTC_TREND_FAST >= 0` is itself a clean **leadership clock** from which a later Beta handoff can always be timed. It also rejects a simple fixed BTC-leading delay as the central model.

The 0048 redesign is explicitly result-informed by this failure and must not be described as independent evidence.

---

## 3. Revised scientific question

0048 asks:

> **Within an already-confirmed crypto uptrend, does leadership rotate among BTC, ETH and SOL in persistent, causally identifiable states, such that there are economically distinct BTC-lead, ETH-lead and SOL-lead periods rather than a static “Beta always wins” ordering?**

The primary adversarial null is intentionally strong:

> **A0 — Static-Beta null:** if ETH/SOL are almost always superior once crypto is in an uptrend, then dynamic leadership rotation adds no information and the rational comparison becomes a static high-Beta allocation, not a BTC/winner router.

0048 must therefore demonstrate **alternation**, not merely that some Beta asset has higher average return than BTC.

---

## 4. Market state and asset leadership are separate layers

### Layer A — Market / diffusion state

This layer answers whether the environment supports broadening risk appetite.

Candidate information families:

- canonical BTC absolute fast/slow trend as an existing risk-on anchor;
- cross-asset breadth / diffusion;
- ETH/BTC and SOL/BTC breadth jointly;
- participation/liquidity expansion;
- **BTC Dominance level, slope and turning behavior** if and only if a reproducible historical source is independently selected and frozen before preregistration.

Important boundary:

> BTC Dominance is a market-diffusion variable, not the winner selector.

A falling BTC Dominance may show capital broadening away from BTC, but it cannot by itself decide whether ETH or SOL deserves the risk budget.

No price-only proxy may be mislabeled as BTC market-cap dominance.

### Layer B — Cross-sectional asset leadership

Leadership is evaluated separately for each `x in {BTC, ETH, SOL}`.

The architecture must use a **symmetric pairwise relative-strength representation**, rather than treating BTC as the permanent reference asset.

For each asset `x`, evaluate its relative state against each competing asset `y != x` using the already-established fast/slow trend family.

Conceptually:

```text
LEAD_x = information from x/y versus every other asset
```

Required families:

- absolute fast/slow trend of x;
- pairwise fast relative trend x/y;
- pairwise slow relative trend x/y;
- fast-minus-slow relative acceleration;
- cross-sectional leadership margin versus runner-up;
- participation/liquidity confirmation;
- market diffusion context from Layer A.

ETH and SOL must have independent clocks. 0048 may not assume:

```text
BTC -> ETH -> SOL
```

or

```text
BTC -> all Beta simultaneously
```

Both 2021-style sequential diffusion and 2023-style split leadership must be representable.

---

## 5. Frozen qualitative leadership states

The architecture contains four economic leadership states:

```text
BTC_LEAD
ETH_LEAD
SOL_LEAD
NO_CLEAR_LEADER / TRANSITION
```

`NO_CLEAR_LEADER` is mandatory. The system may not force a winner every day.

The later preregistration must define a causal confidence/margin rule such that a tiny rank difference cannot justify extreme concentration.

Examples of intended semantics:

```text
SOL barely outranks BTC -> no extreme concentration
SOL decisively outranks BTC and ETH -> high-confidence SOL leadership
leadership margin collapses -> de-concentrate / re-anchor
```

The architecture does not yet freeze a numeric confidence threshold.

---

## 6. Two distinct routes back to BTC

A later strategy must preserve two different mechanisms for leaving a high-Beta winner.

### Route 1 — Leadership reversal

This is an upside-allocation decision, not a top call.

Example:

```text
SOL leadership weakens
BTC relative leadership recovers
market exhaustion remains low
-> SOL -> BTC
```

This route exists to maximize expected return and prevent stale winner concentration.

### Route 2 — Exhaustion compression

This is a risk-quality decision.

Example:

```text
SOL remains nominal leader
but CORE4-style exhaustion risk rises materially
-> SOL -> BTC
```

BTC is the first defensive anchor **inside crypto**, not cash.

These routes must be independently attributable in later evaluation. A portfolio backtest may not combine them into an opaque single trigger and then infer which mechanism worked after seeing CAGR.

---

## 7. BTC -> cash is a separate gross-risk stage

BTC is not risk-free.

The architecture therefore requires a second risk-control layer:

```text
winner concentration
    -> BTC re-anchor
    -> only then, if broader market risk deteriorates further, reduce total crypto gross toward cash
```

The gross-reduction layer must use its own preregistered mapping and investment-basis cash credit. It is not part of 0048.

The historical 0038 lesson remains binding: improving drawdown while sacrificing too much bull-market upside is not sufficient. Future gross-reduction success must preserve right-tail opportunity and improve portfolio economics, not merely reduce volatility.

---

## 8. Intended later concentration research

The owner-approved economic hypothesis is explicitly aggressive:

> **When an uptrend is confirmed and winner confidence is genuinely high, the economically relevant candidate region is approximately 80%–100% of crypto risk budget in the winner, not merely the already-tested 60% winner allocation.**

This is a hypothesis, **not yet a parameter freeze**.

A later portfolio preregistration may consider a small predeclared family such as `80% / 90% / 100% winner`, with the existing `60% winner` lineage as benchmark, but the exact candidate budget and selection rule must be frozen before any result-bearing run.

No 0048 historical run may test these allocations.

---

## 9. What 0048 must prove before portfolio concentration is eligible

0048 is an information/mechanism stage. It must establish all of the following at the design level before any later portfolio stage is considered:

1. **Leadership alternation:** BTC, ETH and SOL must occupy economically meaningful winning states; the result cannot reduce to “always own the same Beta asset”.
2. **Persistence:** winner states must have enough duration to be potentially tradable after realistic execution delay/cost.
3. **Causal identifiability:** today’s information must contain predictive separation about subsequent relative leadership; hindsight rank alone is insufficient.
4. **State-margin relevance:** larger causal leadership margins should correspond to stronger subsequent relative advantage more often than small margins.
5. **No fixed-delay dependency:** the method must not require a universal `BTC leads by N days` assumption.
6. **Episode dependence control:** repeated days inside one bull phase may not be treated as independent observations.
7. **Static-Beta adversarial comparison:** descriptive opportunity analysis must compare dynamic leadership potential against always-BTC and best-static-asset alternatives, so rotation is not credited for what static asset selection already explains.

A later preregistration must convert these principles into exact numerical gates before any measurement.

---

## 10. Numerical items explicitly NOT frozen yet

The following are blocked from arbitrary selection and require a dedicated preregistration-design pass before any historical run:

### 10.1 Forward leadership target

0047's exact `same winner at +20 and +60 while BTC positive at both` label is **not reused automatically**.

The new target must measure economic leadership without forcing a dual-horizon durable label that can miss profitable one-switch opportunities.

Candidate architectures to be evaluated **methodologically, not empirically**, before preregistration include:

- single primary forward horizon plus persistence secondary;
- forward path-integrated relative wealth / regret;
- continuous winner-margin target rather than a hard binary durable label.

No historical sweep is allowed to choose among them.

### 10.2 BTC Dominance data source

The repository currently has no frozen BTC Dominance source. Before preregistration:

- select a reproducible source;
- freeze timestamp semantics and revision policy;
- verify historical availability and missing-data policy;
- register contamination/exposure status.

If this cannot be done cleanly, BTC Dominance must remain out of the primary 0048 result rather than be substituted with an improvised proxy.

### 10.3 Winner confidence -> allocation mapping

No `80 / 90 / 100` threshold or confidence cutoff is frozen here.

This mapping belongs to the later portfolio-economics stage after leadership information passes its own preregistered gates.

### 10.4 Exhaustion -> BTC and BTC -> cash mappings

0044 CORE4 may motivate later risk compression, but no percentile threshold, smoothing rule, persistence rule, BTC re-anchor percentage or cash-gross schedule is frozen in 0048.

---

## 11. Required validation structure

Any later 0048 result must be dependence-aware.

Minimum design requirements:

- preserve complete bull/market episodes as validation blocks;
- no random daily-row train/test split;
- report leave-one-episode-out or equivalent episode-held-out performance;
- retain negative episodes where BTC remains superior;
- separately report 2021-style sequential rotation and 2023-style split/asynchronous leadership if the frozen mechanical episode taxonomy produces such regimes;
- no manual relabeling of historical years to force a narrative.

The study must be able to fail because:

- leadership is too synchronous;
- states are too short/noisy;
- static SOL/ETH explains the apparent edge;
- causal leadership scores do not predict the subsequent winner;
- BTC Dominance adds no stable information;
- no-clear-leader periods dominate.

---

## 12. Program sequence after this architecture freeze

The revised program is:

```text
0048  Leadership Rotation Information Stage
      prove BTC / ETH / SOL leadership alternates and is causally identifiable
      NO portfolio allocation test

0049  Winner Concentration Portfolio Economics
      only if 0048 passes
      compare current 60% winner benchmark with a small preregistered aggressive family in the 80%–100% region
      primary objective = net CAGR after costs, with MDD / Calmar / right-tail / turnover constraints

0050  Winner -> BTC Risk Re-anchor
      add two explicit exit routes:
      (A) leadership reversal
      (B) exhaustion compression using separately frozen 0044-derived information

0051  BTC -> Cash Gross Brake
      only for broader risk deterioration
      investment-basis cash credit
      prevent 0038-style premature bull-market de-risking

0052  Integrated Router
      BTC / ETH / SOL leadership + risk re-anchor + gross brake
      future-only validation required before any canonical or production use
```

The numbering is a roadmap, not automatic eligibility. Each result-bearing stage requires its own preregistration and predecessor gate.

---

## 13. Explicit prohibitions

Under this architecture-freeze stage:

- no historical 0048 measurement;
- no model fit;
- no hazard/semi-Markov fit;
- no HMM / classifier / boosting / neural network;
- no fixed-delay search;
- no BOCPD rescue;
- no BTC Dominance proxy invention;
- no `80/90/100` allocation backtest;
- no CAGR / Sharpe / Sortino / Calmar / MDD portfolio test;
- no CORE4 threshold search;
- no winner->BTC threshold search;
- no BTC->cash mapping;
- no same-ID 0047 rescue;
- no canonical BRRK change;
- no Phase-6 change;
- no leverage increase or shorting;
- no signing, order submission or production authority.

---

## 14. Exact next step

The only permitted next research action is a **numerical-method design pass for 0048 preregistration**, with no historical result release.

That pass must freeze, before any run:

1. the exact forward leadership target and primary metric;
2. the exact causal leadership feature construction and any weighting/normalization;
3. the static-Beta / always-BTC adversarial controls;
4. the episode/block validation rule;
5. the numerical PASS/FAIL gates;
6. whether BTC Dominance has a sufficiently reproducible source to enter primary analysis;
7. the candidate/model budget, preferably one primary low-dimensional interpretable representation.

Only after that separate preregistration is merged may implementation begin.
