# BRRK Implementation Roadmap — 2026-08-05

This roadmap is subordinate to `docs/MASTER_PLAN_2026-08-05.md`.

The rule is simple: **do the next dependency, close the evidence loop, then move on.** Do not jump ahead because a later item is more interesting.

---

## Phase 0 — Program baseline and registry

Goal: create a single source of truth for what is approved, what is experimental and what is live.

### P0.1 Canonical product config

Create a machine-readable config containing at least:

- long universe = BTC, ETH, SOL, BNB;
- primary venue = Hyperliquid;
- canonical timezone = UTC;
- daily boundary = 00:00 UTC;
- initial live capital = $2,000;
- weekly manual contribution = $100;
- catastrophic drawdown limit = 70%;
- normal operating risk budget = explicit but not yet frozen until leverage study;
- production state = ACTIVE / MONITOR_ONLY / SHORT_READY / STOPPED;
- human approval flags;
- strategy release identifier;
- model/data version identifiers.

Acceptance criteria:

- one canonical config consumed by research integration tests and execution code;
- no duplicated contradictory constants in multiple modules;
- config serializable and archived with each production release.

### P0.2 Decision registry

Create a registry of frozen decisions:

- accepted research lines;
- rejected/stopped lines;
- shadow-only lines;
- production-authorized components.

Acceptance criteria:

- every future task references an existing decision or creates a new decision record;
- stopped research is not silently reopened.

---

## Phase 1 — Account and execution truth

Goal: make the bot capable of proving what happened, not merely sending an order.

This phase is required before any increase in live risk.

### P1.1 Deterministic order identity

Implement deterministic client/order IDs derived from:

- release;
- decision timestamp;
- asset;
- side;
- intent / target revision.

Acceptance criteria:

- rerunning the same decision cannot create duplicate economic orders;
- IDs survive process restart;
- replay tests pass.

### P1.2 Persistent order ledger

Persist:

- intent;
- submitted order;
- exchange order ID;
- status history;
- fill events;
- fees;
- average fill price;
- remaining quantity;
- cancellation / rejection reason.

Acceptance criteria:

- process restart reconstructs unresolved orders;
- no fill is lost;
- no order is treated as complete merely because it was submitted.

### P1.3 Partial-fill correctness

Implement position transition from actual fills, not requested notional.

Acceptance criteria:

- 0%, partial and full fill cases all reconcile correctly;
- resting remainder is visible;
- target versus actual exposure is continuously calculable.

### P1.4 Reversal safety

No non-atomic long-to-short or short-to-long assumption.

Acceptance criteria:

- reduction and new-direction opening are distinct intents;
- reduce-only is used where applicable;
- failure during reversal cannot accidentally double directional risk.

### P1.5 Precision / metadata

Remove hardcoded size and price precision.

Acceptance criteria:

- asset metadata drives valid order formatting;
- all BRRK instruments pass formatting tests.

### P1.6 Post-submit reconciliation

After every trading cycle:

- fetch open orders;
- fetch fills;
- fetch positions;
- fetch account equity/margin;
- compare with local ledger and target.

Acceptance criteria:

- unexplained differences block further risk-increasing orders;
- reduce-risk actions remain available.

### P1.7 Restart recovery

Acceptance criteria:

- cold restart with open order;
- cold restart with partial fill;
- cold restart after network timeout with unknown submit result;
- cold restart with actual position differing from stale local state.

All cases must resolve safely and idempotently.

### P1.8 Kill and emergency paths

Implement:

- cancel-all;
- reduce-only close;
- emergency FLAT;
- disable-new-risk switch.

Acceptance criteria:

- testnet / controlled test proves each path;
- emergency path does not depend on the normal target engine being healthy.

---

## Phase 2 — Hyperliquid instrument router

Goal: separate economic exposure from implementation instrument.

### P2.1 Canonical instrument registry

For BTC, ETH, SOL, BNB record:

- spot token identity;
- perp identity;
- decimals / tick size;
- custody/redemption facts where relevant;
- liquidity metrics;
- availability state.

BTC spot identity already has prior evidence and should be imported rather than rediscovered.

### P2.2 UETH / USOL / BNB validation

Verify official identity and actual implementation constraints.

Acceptance criteria:

- no PnL study can substitute for token-identity evidence;
- unavailable / ambiguous spot assets are explicitly marked and routed to perp only if permitted.

### P2.3 Cost model

For each candidate route estimate:

- taker/maker fee;
- spread;
- live depth / VWAP;
- expected slippage;
- funding;
- basis / premium;
- expected holding duration.

### P2.4 Router decision

The target engine should request economic exposure. Router returns implementation plan and reason code.

Example reason codes:

```text
SPOT_VERIFIED_LOWER_COST
PERP_SPOT_UNVERIFIED
PERP_REQUIRED_FOR_SHORT
PERP_REQUIRED_FOR_LEVERAGE_OVERLAY
NO_TRADE_LIQUIDITY_FAIL
```

Acceptance criteria:

- all routing decisions logged;
- research backtest can reproduce router assumptions;
- production can compare expected versus realized cost.

---

## Phase 3 — Production-quality BRRK daily engine

Goal: make the frozen directional core reproducible in live operation before adding new top/exit intelligence.

### P3.1 Data contract

Define canonical sources and transformations for:

- daily close;
- missing data;
- corporate/token mapping changes where relevant;
- funding/basis inputs used by router.

Acceptance criteria:

- UTC 00:00 boundary is identical in research and live;
- same historical input produces same target.

### P3.2 Target calculation API

Input:

- canonical daily data;
- account equity;
- current positions;
- approved config.

Output:

- BRRK relative weights;
- cash share;
- base gross target;
- risk state;
- version and feature snapshot.

### P3.3 Rebalance band / turnover controls

Use explicit banding rules rather than ad-hoc minimum-size checks.

Acceptance criteria:

- no unnecessary churn from tiny target changes;
- all deviations from theoretical target measurable.

### P3.4 Weekly cash contribution handling

Manual deposit is detected as equity change and included at the next daily decision.

Acceptance criteria:

- deposit does not trigger unscheduled intraday risk increase;
- new cash allocation follows the same target engine.

---

## Phase 4 — Dynamic leverage extension

Goal: determine economically justified gross exposure above 1.0 without treating the 70% catastrophe tolerance as an operating target.

### P4.1 Preserve current 0–1 scaler

The current corrected CVaR/CDaR risk scaler remains the baseline defensive layer.

Do not overwrite historical BRRK results.

### P4.2 Preregister leverage study

Define before running:

- leverage search domain;
- operating drawdown candidate budgets;
- hard gross cap candidates;
- funding / fee / slippage treatment;
- stress windows;
- benchmark comparison;
- acceptance/failure conditions.

Candidate search may include gross exposure above 1.0, but deployment remains separately capped.

### P4.3 Objective

Primary objective:

```text
maximize expected long-run compounded wealth
```

subject to:

- operating drawdown budget;
- 70% catastrophic boundary;
- CVaR/CDaR constraints;
- liquidation-distance constraints;
- cost-aware economics;
- minimum implementation robustness.

### P4.4 Stress suite

At minimum include:

- 2021 spring crash;
- 2021 November / subsequent bear transition;
- 2022 severe drawdown environment;
- 2024 stress episodes already identified in prior work;
- 2025 multi-peak / deleveraging windows;
- synthetic gap / volatility shocks;
- funding spikes;
- degraded fill assumptions.

### P4.5 Selection rule

Do not choose leverage from the best in-sample CAGR.

Prefer the broad region where:

- terminal wealth is strong;
- Calmar remains robust;
- Sharpe does not collapse;
- drawdown sensitivity is not knife-edge;
- nearby parameters behave similarly.

### P4.6 Deployment gate

Research may support a higher gross target before production does.

Production leverage is capped until Phase 1 and Phase 2 evidence is complete.

---

## Phase 5 — Cycle-top / late-bull / exit model

Goal: capture the final rotation while reducing aggregate risk before a terminal trend break.

This phase is a new research program, not a retune of BRRK core.

### P5.1 Event taxonomy

Create labeled research windows without labeling every local top as a terminal top.

At minimum:

#### 2021

- spring first major top / May crash;
- summer recovery / second-wind transition;
- November terminal peak / bear transition.

#### 2025

- June new-high phase;
- August new-high phase;
- October new-high and deleveraging phase;
- subsequent late-2025 deterioration.

Also include non-top high-volatility controls so the model must distinguish a real terminal structure from ordinary pullbacks.

### P5.2 Feature families

#### BTC trend maturity

- 20d trend;
- 40d trend;
- slopes;
- KAMA state/slope;
- distance from high;
- consolidation duration.

#### Momentum exhaustion

- daily RSI family;
- 4h RSI family;
- price/momentum divergence;
- persistence and failure from extremes.

Do not preselect daily or 4h RSI from visual intuition; compare them under the same validation framework.

#### Leadership migration

- BTC dominance;
- ETH/BTC;
- SOL/BTC;
- BNB/BTC;
- cross-sectional relative-strength dispersion.

#### Breadth

- proportion outperforming BTC;
- high-beta participation;
- breadth acceleration;
- breadth contraction after expansion;
- headline strength versus internal deterioration.

#### Leverage/speculation

- funding;
- OI;
- basis;
- premium;
- volatility;
- liquidation proxies where data quality is sufficient.

### P5.3 State model

Target states:

```text
NORMAL_BULL
BTC_LEADERSHIP_MATURING
LATE_BULL_ROTATION
EXHAUSTION_WATCH
DE_RISK_1
DE_RISK_2
FLAT
```

### P5.4 Required behavior

- BTC high-level consolidation plus falling BTC dominance is not automatically bearish;
- LATE_BULL_ROTATION may raise relative alt weight;
- total gross risk should begin falling as cycle hazard rises;
- hard-risk combinations may force direct FLAT;
- the model should seek useful 7–14 day lead information but must not be forced to generate that lead if evidence does not support it.

### P5.5 Validation

Use leave-one-event-out or comparable event-level validation where feasible.

A rule that needs 2021-specific or 2025-specific hand tuning fails robustness.

Report:

- lead/lag distribution;
- false positive duration;
- missed upside before exit;
- drawdown avoided;
- terminal wealth impact;
- behavior on second-wind scenarios.

### P5.6 Integration rule

The exit model controls total risk state, not BRRK relative ranking directly.

Conceptually:

```text
BRRK = which assets
Cycle layer = how much total directional risk
Router = with which instruments
Execution = how to reach actual target safely
```

---

## Phase 6 — Integrated shadow system

Goal: run the complete candidate system against live conditions with zero trading authority.

The shadow candidate may read:

- real Hyperliquid account state;
- real market data;
- funding;
- live order books.

It may calculate hypothetical orders but must not sign them.

### P6.1 Shadow comparison

Log daily:

- target BRRK weights;
- cycle state;
- leverage target;
- router choice;
- hypothetical fill estimate;
- incumbent ACTIVE behavior if another version is live.

### P6.2 Drift checks

Alert on:

- feature mismatch versus offline reference;
- target mismatch;
- missing data;
- instrument identity changes;
- cost-model errors;
- unexplained state transitions.

### P6.3 Shadow acceptance

Require a defined period or sufficient decision count with:

- no critical reconciliation errors;
- no unexplained target drift;
- stable daily schedule;
- emergency logic tested;
- audit trail complete.

Do not predetermine a cosmetic calendar duration if the number of meaningful decisions is too small; define both minimum elapsed time and minimum decision/event coverage.

---

## Phase 7 — Limited-capital live long program

Goal: operate the approved long system with the initial $2,000 and weekly $100 contributions.

### P7.1 Launch checklist

Required before launch:

- explicit user approval;
- production release frozen;
- trading Agent credential only;
- no master wallet private key in bot;
- withdrawal/transfer automation absent;
- hard exposure caps configured;
- kill switch tested;
- startup reconciliation passes;
- monitoring active.

### P7.2 Normal autonomy

Within an approved long ACTIVE state the bot may automatically:

- rebalance weights;
- change normal leverage inside approved limits;
- route spot/perp;
- reduce risk;
- execute emergency FLAT.

### P7.3 Human approval boundaries

Require explicit approval for:

```text
FLAT -> LONG
FLAT -> SHORT
MONITOR_ONLY -> ACTIVE
first short exposure of a new bear phase
```

### P7.4 Scale-up evidence

Before increasing capital allocation, review:

- expected versus realized slippage;
- realized funding;
- order/fill reconciliation history;
- uptime and data quality;
- drawdown behavior;
- target fidelity;
- operational incidents.

Scale capital only when implementation evidence supports it.

---

## Phase 8 — Bear-short research

Goal: optional future program after a confirmed bear transition.

Do not prioritize this ahead of long/exit production readiness.

### P8.1 Candidate universe

Start with:

- BTC;
- ETH;
- SOL;
- BNB.

Research may then expand to a contemporaneous liquid Top 20 universe.

### P8.2 Universe safety filters

Before a candidate may be shorted, require:

- sufficient live liquidity;
- reliable perp market;
- acceptable spread/depth;
- non-pathological funding;
- no known market-structure issue that makes short execution unreliable.

### P8.3 Selection research

Test whether weakest/high-beta/crowded new Top 20 entrants provide better short economics than simply shorting BTC or the BRRK basket.

### P8.4 Human gate

A future bear model may emit `SHORT_READY`, but no first short is opened without explicit approval.

---

# Task ordering rules

1. Do not start P4 production integration before P1 execution truth is complete.
2. Do not make P5 cycle-exit logic responsible for fixing P1 execution deficiencies.
3. Do not widen the long universe while P3/P5 are unresolved.
4. Do not widen the short universe before P8.
5. Do not implement automated withdrawals.
6. Do not hot-patch the ACTIVE production strategy.
7. Do not rescue a failed historical line without a new registered hypothesis.

---

# Evidence status convention

Each task should end in one of:

```text
PASS_PRODUCTION_CANDIDATE
PASS_SHADOW_ONLY
FAIL_STOP
FAIL_FIX_IMPLEMENTATION
MEASUREMENT_INCONCLUSIVE
```

Every status should link to evidence.

---

# Immediate next task

The next work item after this plan is merged is:

```text
P0.1 Canonical product config + P0.2 decision registry
```

Then proceed directly into Phase 1 execution/account truth.

Do not start the cycle-top model first simply because it is analytically interesting; the project needs a reliable state and execution spine before the new model can become deployable.