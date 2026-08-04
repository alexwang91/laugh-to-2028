# Crypto Regime/Rotation Research Roadmap — after AUDIT-0017

Date: 2026-08-04

This is a stopping-rule document, not a strategy. It limits degrees of freedom and prevents serial backtest optimization.

## Canonical baseline

**BRRK-0011** remains the canonical research portfolio.

Common BRRK window 2022-12-10 through 2026-08-02:

- CAGR 65.10%;
- MDD -33.72%;
- Sharpe 1.353;
- Calmar 1.931.

No PIT module is promoted over BRRK-0011.

## Evidence hierarchy

### Tier A — canonical portfolio

- BRRK-0011.
- Calibration audits show no observed terminal-tail undercoverage and conservative path-drawdown forecasts.

### Tier B — validated mechanisms, rejected implementations

**PIT-DISP-0015**:

- broad historical dispersion contains real risk information;
- reduces MDD, CDaR, volatility and downside capture;
- lowers CAGR and upside capture;
- not promoted.

**PIT-ALPHA-0016 rank**:

- beats 98/100 random-priority placebos;
- contribution is diversified;
- ranking information survives dead-pool inclusion.

**PIT-ALPHA-0016 portfolio**:

- CAGR 12.25%;
- MDD -69.12%;
- turnover 349.62;
- negative 2025+ economics;
- almost eliminated at 20 bps;
- rejected.

### Tier C — causal attribution

**AUDIT-0017**:

- daily eligible-set Jaccard 0.630;
- monthly first-to-last Jaccard 0.249;
- median holding period 1 day;
- 83.41% of turnover from within-alt name switching;
- at 30 days, only 19.35% remain Top-2 but 52.07% remain eligible;
- 30-day median forward return -2.43%, mean +4.83%;
- dominant failure identified: daily leaderboard replacement exits right-tail winners too early.

### Tier D — fixed-panel/event diagnostics

- DISP-0014: selection-sensitive fixed-panel diagnostic.
- DISP-0013: event-concentrated alt-to-BTC diagnostic.

## Gate 1 — PIT-DISP-0015: resolved

Broad risk information survives, portfolio promotion fails. No tuning allowed.

## Gate 2 — PIT-ALPHA-0016: resolved

Ranking mechanism survives placebo/dead-pool tests, daily Top-2 portfolio fails. No tuning allowed.

## Gate 3 — AUDIT-0017: resolved

The audit identifies three causal layers:

1. daily name replacement dominates turnover;
2. the rank payoff is strongly right-skewed and requires persistence;
3. tail loss/volatility sequence drag prevents additive signal from compounding.

Capacity at $1m NAV is not the primary bottleneck. Transaction cost matters but is not a sufficient explanation for the -69% drawdown.

The audit authorizes exactly one new structural experiment.

## Gate 4 — authorized next experiment

### Entry-rank / eligibility-exit state machine

```text
BTC risk-on and vacancy exists
        ↓
Top-2 validated rank chooses entry
        ↓
incumbent remains held while:
  own trend > 0
  relative-to-BTC trend > 0
  age/liquidity eligibility holds
        ↓
exit when:
  incumbent becomes ineligible
  BTC becomes risk-off
  or data availability ends
        ↓
fill vacancy with highest-ranked eligible non-incumbent
```

This is the only authorized alpha-portfolio change after AUDIT-0017.

### Frozen inputs

- historical dead-pool-inclusive Binance USDT universe;
- 240 consecutive completed daily observations;
- completed-day quote volume >= $25m;
- existing own/relative trend definitions;
- existing `(0.5 own + 0.5 relative)/rv30` entry rank;
- Top-2 capacity;
- gross <= 1;
- 50% BTC core / 50% alt sleeve in risk-on;
- universal 35% single-alt cap;
- 0.05 L1 band;
- 5 bps primary cost and registered 10/20 bps stress;
- t signal held over t+1.

### Sole structural change

Falling out of daily Top-2 is no longer an exit. Eligibility loss or risk-off is the exit.

### Prohibited additions

- no exit rank threshold;
- no minimum holding period;
- no monthly calendar frequency;
- no higher age threshold;
- no hard-coded current winners;
- no funding/dispersion/covariance/LPM/leverage overlay;
- no broad parameter grid.

### Required comparisons

- PIT-ALPHA-0016 daily replacement;
- BTC dynamic gross<=1;
- fixed V1 gross<=1;
- random-priority placebo using the same eligibility-exit state machine;
- 5/10/20 bps costs;
- 2024+, 2025+ and 2026 subperiods;
- turnover decomposition and holding duration;
- contribution concentration and inactive-asset attribution;
- tail losses and maximum drawdown.

### Promotion requirements

- materially lower name-switch turnover and longer holdings than 0016;
- preserve meaningful advantage over state-machine placebo;
- materially improve MDD/Calmar, not merely cost;
- retain positive 2025+ economics;
- remain economically positive at 10 bps and informative at 20 bps;
- no single asset >50% of positive contribution;
- no post-result parameter change.

Beating PIT-ALPHA-0016 alone is insufficient.

## Gate 5 — funding history and Spot/Perp Router

Use accessible archives to compare implementation of unchanged target exposure. Funding, basis, fees and slippage must be separated. This is not an alpha claim.

## Gate 6 — execution hardening

Hyperliquid testnet/shadow work:

- metadata precision;
- target-notional L2 VWAP and Slippage-at-Risk;
- partial fills and reconciliation;
- slicing;
- idempotency/audit logs;
- emergency reduce-only controls;
- endpoint authorization;
- deterministic parity with research targets.

## Gate 7 — risk allocation and leverage last

Do not add covariance, LPM, generic volatility gates or leverage to rescue a weak alpha implementation.

## Explicitly stopped lines

- manual bottom/recovery jumps;
- CUSUM threshold tuning;
- HMM factor/state selection by PNL;
- semantic-state anchoring;
- generic volatility-gate stacking;
- tuning PIT-DISP-0015;
- tuning PIT-ALPHA-0016;
- exit-rank/minimum-hold/monthly-frequency grids after AUDIT-0017;
- hard-coding HYPE or another current winner;
- deep RL before survivor-aware simple economics work;
- leverage expansion before validation.

## Promotion philosophy

Promotion requires:

**mechanism + preregistration + no-lookahead + realistic cost + subperiod persistence + universe/model uncertainty + implementation audit + controlled opportunity cost + acceptable turnover and tail risk.**

Mechanism validation alone is not portfolio validation. Lower turnover alone is not alpha validation.
