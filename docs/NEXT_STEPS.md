# Next Steps

当前原则：**机制验证、组合验证和部署授权必须分开。归因只能授权一种新结构，不能调参救回测。**

## Completed — PIT-DISP-0015

Broad point-in-time dispersion contains real risk information, but its upside opportunity cost prevents promotion. Fixed-panel DISP-0014 is materially selection-sensitive.

Decision: BRRK-0011 remains canonical baseline; no PIT-DISP-0015 tuning.

## Completed — PIT-ALPHA-0016

The dead-pool-inclusive Top-2 rank beat 98/100 random-priority placebos and was not dominated by one winner. The portfolio itself failed:

- CAGR 12.25%;
- MDD -69.12%;
- turnover 349.62;
- negative 2025+ CAGR;
- almost all growth disappears at 20 bps.

Decision: ranking mechanism validated; portfolio rejected; no 0016 tuning.

## Completed — AUDIT-0017

The no-trading-change audit identified the dominant rank-to-portfolio failure.

### Core diagnosis

- eligible set changes by roughly 3 additions and 3 removals per day;
- monthly first-to-last eligible-set Jaccard is only 0.249;
- 653 holding spells across 113 symbols;
- median holding duration is 1 day;
- only 41.96% of spells have positive arithmetic contribution;
- 83.41% of turnover comes from within-alt name switching;
- BTC-weight turnover is only 7.18%;
- alt-sleeve-size turnover is only 9.41%.

### Payoff shape

At 30 days after entry:

- 52.07% of assets remain broadly eligible;
- only 19.35% remain daily Top-2;
- median forward return is -2.43%;
- mean forward return is +4.83%.

The rank is right-skewed: many small losers and a few large persistent winners. Strict daily Top-2 replacement exits incumbents before the rare winners can compound.

### Additional findings

- PIT alt exposure overlaps active fixed-V1 alts on only 28.70% of days;
- overlap days have materially higher mean return than non-overlap days;
- tail losses and volatility sequence drag are at least as important as fees;
- capacity at $1m NAV is not the primary bottleneck;
- younger listings have worse median outcomes, but the audit does not authorize an age-threshold change.

Formal result: `research/results/AUDIT_0017_PIT_ALPHA_ATTRIBUTION_2026-08-04.md`.

Exact evidence: `research/results/audit_0017_pit_alpha_attribution/`.

---

## P0 — New experiment: entry-rank / eligibility-exit

AUDIT-0017 authorizes exactly one next structural hypothesis.

### State machine

```text
vacancy exists in risk-on state
        ↓
use validated Top-2 rank to select entry
        ↓
keep incumbent while:
  own trend > 0
  relative-to-BTC trend > 0
  liquidity/continuous-history eligibility holds
        ↓
replace only when:
  incumbent becomes ineligible
  BTC enters risk-off
  or a vacancy remains
```

### What must remain frozen

- full point-in-time historical universe;
- later inactive/delisted assets retained historically;
- 240 consecutive completed daily rows;
- completed-day quote volume >= $25m;
- existing own/relative trend definitions and rank score;
- gross <= 1;
- BTC regime/core logic;
- 50% BTC / 50% alt sleeve in risk-on;
- universal 35% single-alt cap;
- 0.05 L1 band;
- stated transaction costs;
- t signal held over t+1.

### What changes

Only the exit authority:

- falling out of daily Top-2 is no longer an exit;
- losing own/relative eligibility, liquidity/history eligibility or risk-on state is an exit.

### Prohibited additions

- no exit-rank threshold;
- no minimum holding period;
- no monthly calendar parameter;
- no age-threshold increase;
- no hard-coded ETH/SOL/BNB/HYPE universe;
- no funding, dispersion, covariance, LPM or leverage overlay;
- no parameter family selected from PNL.

### Required evidence

- exact PNL and drawdown;
- turnover decomposition;
- holding-spell distribution;
- right-tail winner capture;
- 5/10/20 bps stress;
- 2024+, 2025+ and 2026 behavior;
- contribution concentration;
- inactive-asset attribution;
- comparison against PIT-ALPHA-0016, BTC dynamic, fixed V1 and random-priority placebo under the same state machine.

Promotion requires materially better turnover and drawdown without losing the validated rank advantage. Beating 0016 alone is insufficient.

---

## P1 — Historical funding + Spot/Perp Router

Use accessible archives and separately attribute funding, fees, basis and slippage for an unchanged target exposure. This is implementation optimization, not alpha.

## P2 — Hyperliquid execution hardening

Priorities:

1. metadata-derived size precision;
2. reversal/fill reconciliation;
3. partial/resting/rejected handling;
4. order slicing;
5. persistent idempotency and audit logs;
6. target-notional L2 simulation;
7. reduce-only emergency protection;
8. endpoint authorization and mainnet double confirmation;
9. deterministic parity with research targets.

## P3 — Risk allocation and leverage last

Do not use covariance, LPM, generic volatility gates or leverage to rescue a weak alpha implementation.

## Stopping rules

Stop and retain BRRK-0011 if the authorized state machine:

- still produces negative 2025+ economics;
- reduces turnover but retains unacceptable tail drawdown;
- loses the placebo-validated ranking edge;
- depends on one ex-post winner;
- is fragile at 10–20 bps;
- requires any additional threshold after seeing results.

The objective is not to recover the fixed-universe historical CAGR. It is to determine whether validated ranking information can be converted into a survivor-aware, low-turnover exposure system.
