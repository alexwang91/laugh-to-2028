# BRRK / laugh-to-2028 Master Plan — 2026-08-05

Status: **planning baseline for all forward work**

This document converts the repository from a collection of research lines into one explicit product program. Future research, execution work and deployment changes should be evaluated against this plan. Historical research results remain preserved; this document does not reopen failed rescue lines unless a future preregistered study has a new hypothesis and new evidence.

---

## 1. Product objective

The project is not tied to a literal 2028 calendar exit date. The working expectation is that the next major cycle-top / cycle-exit regime may occur in the **2028–2029** area, but the system must act on market state, not on a hardcoded date.

Primary objective:

```text
maximize long-term compounded terminal wealth
subject to explicit operating-risk constraints
```

The system should:

1. run a BRRK directional long program during constructive regimes;
2. dynamically choose concentration versus diversification across the long universe;
3. dynamically scale total exposure, including leverage when justified by risk-adjusted economics;
4. reduce risk progressively as a cycle-top structure develops;
5. allow a hard-risk path that immediately moves to zero directional exposure;
6. remain flat after a cycle exit until an explicit human approval re-enables directional risk;
7. optionally support a separately approved bear-market short program after bearish confirmation.

The system is not designed to maximize headline CAGR at any cost. It is designed to maximize compounded wealth while preserving enough capital to survive regime changes and continue operating.

---

## 2. Canonical asset universe

### 2.1 Long universe

The production long universe is fixed as:

```text
BTC
ETH
SOL
BNB
```

No additional long asset may enter production automatically. A new long asset requires its own research, evidence and approval.

### 2.2 Concentration versus diversification

The portfolio may be either concentrated or diversified. There is no permanent equal-weight or one-asset-only rule.

The model should produce a target vector such as:

```text
BTC_weight
ETH_weight
SOL_weight
BNB_weight
cash_weight
```

with the weights and gross exposure jointly determined by the BRRK directional model plus the risk-scaling layer.

### 2.3 Short universe

The initial short benchmark universe is the BRRK four assets, but the short universe is **not permanently fixed**.

When a future bear phase is being researched, the candidate short universe may expand to sufficiently liquid assets in the then-current Top 20 market-cap universe. Inclusion must be based on contemporaneous evidence such as:

- liquidity and order-book depth;
- perpetual/funding structure;
- borrow / instrument availability;
- downside beta and relative weakness;
- crowding / leverage characteristics;
- execution and liquidation risk.

This short-universe expansion is research authorization only, not standing production authorization.

---

## 3. Capital scope

Initial live-validation capital:

```text
$2,000
```

Initial state:

```text
cash / stablecoin
no legacy crypto positions to migrate
```

Recurring contribution:

```text
$100 per week
```

The user manually deposits the recurring contribution. The bot does not transfer or withdraw funds.

New cash is not immediately chased into the market. It is incorporated into the next official daily decision and allocated according to the current system state.

Capital-adoption model:

```text
small dedicated live account
-> forward evidence
-> larger allocation only after gates pass
-> possible later migration of a larger share of crypto capital
```

---

## 4. Risk philosophy

### 4.1 Catastrophic tolerance

User-stated absolute maximum tolerable drawdown:

```text
70%
```

This is a **catastrophic boundary**, not a target and not a normal operating budget.

No leverage optimizer may interpret 70% as permission to design for routine 70% drawdowns.

### 4.2 Operating risk budget

The production operating drawdown budget must be materially below 70% and determined from evidence.

It should be chosen using:

- CAGR;
- maximum drawdown;
- Calmar;
- Sharpe;
- CVaR / CDaR;
- path-dependent stress tests;
- liquidation distance;
- funding and execution cost;
- forward-shadow evidence.

### 4.3 Objective hierarchy

The hierarchy is:

```text
1. survive / preserve continuity
2. maximize long-run compounded wealth
3. prefer better Calmar and robust risk-adjusted returns
4. use Sharpe as a quality diagnostic, not as a fixed leverage selector
```

### 4.4 Benchmark suite

Every material production candidate must be compared with both:

1. BTC buy-and-hold;
2. BTC / ETH / SOL / BNB equal-weight buy-and-hold.

A candidate should not be accepted because of CAGR alone. The target is stronger long-term terminal wealth with controlled drawdown and acceptable cost-adjusted quality.

All production comparisons must include fees, slippage, funding and other instrument-specific costs.

---

## 5. Dynamic leverage policy

Leverage is allowed, but there is no user-selected fixed leverage multiple.

```text
LEVERAGE_POLICY = model determined
```

The current repository's corrected risk scaler is a useful foundation, but its existing safe-scale search is bounded at 1.0. A production leverage layer therefore requires a separately validated extension above 1.0 rather than relabeling the current 0–1 risk scaler as leverage.

### 5.1 Intended architecture

```text
BRRK directional weights
x regime / risk scaler
x optional leverage multiplier
= final target economic exposure
```

### 5.2 Leverage acceptance rule

A leverage level is acceptable only if, after all relevant costs:

- expected compounded wealth improves;
- modeled and stress drawdowns remain within the operating budget;
- CVaR / CDaR remain acceptable;
- liquidation probability is effectively negligible under defined stress scenarios;
- Calmar is not materially degraded without compensation;
- the result survives walk-forward / out-of-sample checks;
- execution readiness is sufficient for the proposed gross exposure.

### 5.3 Late-cycle asymmetry

During late-cycle rotation, the portfolio may become **more aggressive in asset selection while becoming more conservative in total risk**.

Example:

```text
SOL relative weight rises
while total portfolio gross exposure falls
```

The system must not automatically combine late-cycle alt strength with higher total leverage.

---

## 6. Instrument policy — Hyperliquid first

Primary venue:

```text
Hyperliquid
```

The design should prefer a single-venue closed loop for the initial live program.

Instrument choice is economic and asset-aware, not ideologically fixed.

Working policy:

- BTC long: spot-first where identity and implementation are validated;
- ETH long: spot candidate versus perp based on verified identity, liquidity and net cost;
- SOL long: spot candidate versus perp, with special attention to funding drag;
- BNB long: choose spot/perp based on actual Hyperliquid instrument availability and cost;
- shorts: perp / derivative instrument as required;
- leverage above spot exposure: derivative overlay only after validation.

All-perp is not the default simply because it is easier to code.

The router must explicitly compare:

- funding;
- basis;
- fees;
- spread;
- L2 depth / VWAP;
- custody / token identity;
- execution risk.

---

## 7. Canonical time and decision frequency

Official time standard:

```text
UTC
```

Official daily boundary:

```text
00:00 UTC close
```

Normal strategy decisions are daily.

### 7.1 Daily strategy channel

The official daily run may:

- update BRRK weights;
- update risk scaling;
- update leverage;
- update spot/perp routing;
- rebalance the account.

### 7.2 Intraday risk channel

Intraday automation is **risk-reduction only**.

Allowed intraday actions:

- reduce exposure;
- remove leverage;
- cancel orders;
- emergency close;
- move to FLAT.

Not allowed intraday merely because price moved:

- increase leverage;
- add discretionary risk;
- change BRRK direction based on lower-timeframe noise;
- restart from FLAT.

---

## 8. Cycle-top / exit architecture

The exit layer must be separate from ordinary BRRK rotation.

A literal 20/40-day trend zero crossing is too late to be the only exit signal. The research goal is to detect the developing cycle-top structure approximately **7–14 days before** a major trend break when the evidence supports that lead time.

### 8.1 State machine

```text
NORMAL_BULL
-> BTC_LEADERSHIP_MATURING
-> LATE_BULL_ROTATION
-> EXHAUSTION_WATCH
-> DE_RISK_1
-> DE_RISK_2
-> FLAT
-> MONITOR_ONLY
```

A hard-risk combination may skip intermediate de-risk states and move directly to FLAT.

### 8.2 BTC is primary, not exclusive

The cycle-top layer uses BTC as the dominant reference asset but must not treat BTC weakness in isolation as sufficient.

The system should explicitly model:

1. BTC trend maturity;
2. BTC momentum exhaustion;
3. BTC dominance decline / leadership migration;
4. ETH/SOL/BNB relative-strength expansion;
5. broader alt / market breadth expansion and later contraction;
6. leverage and speculative exhaustion;
7. final trend damage.

### 8.3 Late bull rotation is not an exit by itself

A typical late-cycle structure may be:

```text
BTC strong trend
-> BTC high-level consolidation / momentum plateau
-> BTC dominance falls
-> ETH / SOL / BNB / broader alt beta accelerates
-> breadth expands
-> breadth and momentum exhaust
-> trend structure breaks
```

The system should attempt to participate in the late rotation while progressively reducing total risk.

### 8.4 Candidate features to research

BTC structure:

- 20-day / 40-day trend and slope;
- KAMA-derived state / slope;
- distance from high;
- duration of high-level consolidation;
- volatility contraction / expansion.

Momentum exhaustion:

- RSI across daily and 4h windows;
- divergence between price and momentum;
- persistence at extreme momentum followed by failure;
- multi-timeframe momentum agreement / disagreement.

Leadership migration:

- BTC dominance;
- ETH/BTC;
- SOL/BTC;
- BNB/BTC;
- BRRK relative-strength dispersion.

Breadth:

- proportion of relevant assets outperforming BTC;
- breadth acceleration and reversal;
- high-beta participation;
- internal deterioration while headline index remains elevated.

Leverage / positioning:

- funding;
- open interest;
- basis;
- mark/oracle premium;
- volatility;
- liquidation / leverage proxies where reliable.

No individual feature becomes production logic until it survives proper validation.

---

## 9. Historical cycle-top research windows

Cycle-exit research must not be fit only to one event.

### 9.1 2021 two-wave structure

Treat 2021 as at least two distinct events:

- spring 2021 first major top / May drawdown;
- autumn 2021 second advance and November final cycle peak / bear transition.

The spring event is useful for studying early warning and false-terminal-top risk. The November event is useful for studying true terminal-cycle exit.

### 9.2 2025 multi-window structure

2025 must be studied as a multi-peak sequence rather than one timestamp. Candidate windows include:

- the June new-high phase;
- the August new-high phase;
- the October new-high / subsequent deleveraging phase;
- the following deterioration into late 2025.

The purpose is to distinguish:

```text
temporary top
vs
re-accumulation / second wind
vs
terminal cycle break
```

### 9.3 Anti-overfit requirement

Research should explicitly penalize any rule that perfectly calls one historical event but fails on the other major top windows.

The target is a robust state classifier / hazard model, not a hand-built collection of dates.

---

## 10. Exit and human-control rules

### 10.1 Normal long operation

Within an approved ACTIVE regime, the bot may automatically:

- rebalance BRRK weights;
- change normal leverage within approved limits;
- change routing;
- reduce or increase exposure according to the approved model.

### 10.2 FLAT

At FLAT the target crypto directional exposure is:

```text
long = 0
short = 0
net directional exposure = 0
```

The bot should:

1. close directional positions;
2. cancel open orders;
3. reconcile fills, positions, balances and residual exposure;
4. record exit reason and state;
5. enter MONITOR_ONLY.

The user may then manually manage funds using the wallet.

### 10.3 Restart from FLAT

The bot may continue monitoring and generating signals while flat, but it may not automatically restart directional risk.

Transitions such as:

```text
FLAT -> LONG
FLAT -> SHORT
MONITOR_ONLY -> ACTIVE
```

require explicit human approval.

### 10.4 Bear short approval

Bear confirmation may create:

```text
SHORT_READY
```

but the first short exposure of a new bear phase requires explicit user approval.

After approval, the short program may automatically manage positions within its approved rules until the phase ends or a stop condition is triggered.

---

## 11. Security boundary

The trading system should use a Hyperliquid trading Agent / API credential.

The bot may:

- read account state;
- place / modify / cancel orders;
- read fills, positions and margin;
- execute de-risk and FLAT actions.

The bot must not:

- store the master wallet private key;
- withdraw funds;
- transfer funds out;
- modify wallet security settings.

The master key remains manual-only.

---

## 12. Production upgrade model — blue/green

Production strategy logic is not hot-patched.

Use two logical systems:

```text
ACTIVE = current approved production version
CANDIDATE = next version under development / validation
```

The CANDIDATE may read live market and account data in shadow mode and may generate hypothetical decisions, but must not trade unless it becomes ACTIVE.

Upgrade procedure:

1. complete candidate research and implementation;
2. pass all required tests and forward-shadow gates;
3. freeze a release artifact / configuration;
4. stop the old ACTIVE service;
5. reconcile account state and outstanding orders;
6. start the new release;
7. require successful startup reconciliation before new orders;
8. retain the old release for rollback.

Do not mutate the production strategy underneath a running service.

---

## 13. Research and production separation

Research may explore hypotheses, but production authorization requires an explicit gate.

Every material strategy change should have:

- hypothesis;
- preregistered test where appropriate;
- canonical input data and time boundaries;
- out-of-sample / walk-forward evaluation;
- cost-aware results;
- failure criteria;
- decision note: accept / reject / shadow-only.

Failed research should be preserved rather than repeatedly rescued on the same sample.

---

## 14. Core workstreams

Forward work is organized into seven workstreams.

### WS1 — Product registry and canonical state

Create one machine-readable registry for:

- canonical assets;
- strategy release;
- model version;
- risk limits;
- instrument mapping;
- approved venue;
- account state;
- human-approval state.

### WS2 — Execution/account truth

Build deterministic reconciliation for:

- order lifecycle;
- fills and partial fills;
- target versus actual positions;
- account equity and margin;
- restart recovery;
- idempotency;
- persistent audit logs.

### WS3 — Instrument router

Validate and implement spot/perp choice for BRRK assets on Hyperliquid.

### WS4 — Dynamic leverage

Extend the existing risk-scaling research into a cost-aware leverage layer above 1.0 with explicit hard caps and stress tests.

### WS5 — Cycle exit / late-bull model

Build and validate the leadership-migration and exhaustion model using 2021 and 2025 top structures plus all available non-top controls.

### WS6 — Bear program

Design only after long/exit core is robust. The bear research may use BRRK plus a dynamic liquid Top 20 candidate universe.

### WS7 — Shadow and staged live deployment

Run candidate logic in shadow, then limited capital, then scale only after evidence.

---

## 15. Acceptance gates

A production release must not be authorized solely because its backtest is attractive.

Minimum gates:

### Research gate

- no obvious lookahead;
- walk-forward / OOS support;
- cost-aware results;
- benchmark comparison;
- stress-window analysis;
- sensitivity analysis;
- no single-event dependency.

### Model gate

- deterministic target generation;
- explicit state transitions;
- bounded leverage;
- bounded turnover;
- explicit missing-data behavior;
- explicit hard-risk behavior.

### Execution gate

- deterministic client/order identifiers;
- partial-fill correctness;
- rejected/cancelled/resting order handling;
- post-submit reconciliation;
- restart recovery;
- reduce-only emergency path;
- kill switch;
- L2/slippage controls;
- production credential isolation.

### Shadow gate

- live data ingestion stable;
- target decisions reproducible;
- hypothetical fills and actual market conditions logged;
- no unexplained drift between research and live feature calculation;
- no unreconciled account-state errors.

### Live-capital gate

- explicit user approval;
- hard exposure cap;
- limited initial capital;
- production monitoring active;
- rollback path tested.

---

## 16. Correction loop

Future work should follow this loop:

```text
PLAN
-> preregister / define acceptance criteria
-> IMPLEMENT
-> TEST
-> REVIEW evidence
-> ACCEPT / REJECT / FIX
-> update plan status
-> next dependency
```

A failed gate does not automatically justify parameter tuning. The first question is whether the failure invalidates the hypothesis, the implementation, the data or the measurement.

Every correction should be classified as one of:

```text
BUG_FIX
MEASUREMENT_FIX
IMPLEMENTATION_HARDENING
NEW_HYPOTHESIS
PARAMETER_CHANGE
```

A parameter change intended to rescue a failed historical result requires a new preregistered experiment and should not overwrite the failed result.

---

## 17. Priority order

The intended build order is:

```text
P0  canonical product/state registry
P1  account/order/fill reconciliation and execution hardening
P2  Hyperliquid BRRK instrument router
P3  production-quality daily BRRK target engine
P4  dynamic leverage extension and risk-cap selection
P5  2021/2025 cycle-top / late-bull / exit model
P6  integrated shadow system
P7  limited-capital live long program
P8  future bear-short research and approval flow
```

The long program, exit logic and execution truth are higher priority than expanding the short universe.

---

## 18. Non-goals for the immediate phase

Do not spend immediate effort on:

- rescuing stopped carry research;
- adding random new long altcoins;
- optimizing a short universe before the long/exit system is operational;
- multi-venue architecture unless Hyperliquid has a demonstrated blocking limitation;
- hot-reload of production strategy logic;
- complex wallet automation or automated withdrawals;
- fixed-date 2028/2029 exit rules;
- fixed leverage chosen by preference rather than evidence.

---

## 19. Source of truth

This document is the high-level product source of truth.

Detailed task order and completion gates live in:

- `docs/IMPLEMENTATION_ROADMAP_2026-08-05.md`
- `docs/PROJECT_GOVERNANCE_2026-08-05.md`

Historical findings remain in the existing research results, README and review documents.

If a future proposed task conflicts with this master plan, the conflict should be made explicit before implementation.