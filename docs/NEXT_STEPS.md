# Next Steps

当前原则：**机制验证与组合 promotion 必须分开。先解释失败，再设计下一版。**

## Completed gate — PIT-DISP-0015

Broad point-in-time dispersion 的风险压缩机制成立，但降低 CAGR 和 upside capture；fixed-panel DISP-0014 被证明 materially selection-sensitive。

Decision:

- BRRK-0011 remains canonical baseline;
- DISP-0014 and PIT-DISP-0015 remain diagnostics;
- no post-result tuning of PIT-DISP-0015.

Formal result: `research/results/PIT_DISP_0015_RESULT_2026-08-04.md`.

## Completed gate — PIT-ALPHA-0016

The dead-pool-inclusive dynamic-alpha run used 648 historical candidates, 646 symbols with rows, zero fetch errors and 152 currently inactive/non-TRADING symbols that were historically eligible.

### Mechanism result

The frozen Top-2 rank:

- beat 98/100 random-priority placebo seeds on terminal NAV;
- beat 98/100 placebo seeds on Calmar;
- had largest positive contributor share only 13.14%;
- had top-three positive contributor share 34.93%;
- included later-inactive assets without a single-winner dependency.

Therefore own-trend + relative-strength ranking contains real cross-sectional information.

### Portfolio result

Top-2 primary:

- CAGR 12.25%;
- MDD -69.12%;
- Sharpe 0.480;
- Calmar 0.177;
- turnover 349.62.

Fixed V1 gross<=1:

- CAGR 36.43%;
- MDD -59.72%;
- Sharpe 0.889;
- Calmar 0.610;
- turnover 131.81.

At 10 bps Top-2 CAGR falls to 8.57%; at 20 bps it falls to 1.57%. The 2025+ subperiod is negative.

Decision:

- ranking mechanism validated;
- portfolio specification rejected;
- BRRK-0011 remains canonical baseline;
- no 0016 parameter may be tuned on this window.

Formal result: `research/results/PIT_ALPHA_0016_RESULT_2026-08-04.md`.

---

## P0 — PIT-ALPHA attribution audit, no trading changes

This is now the highest priority.

Primary question:

> Why does a rank that beats 98% of placebos still produce only 12.25% CAGR, -69% MDD and extreme turnover?

Required outputs:

1. eligible-universe churn by day/month;
2. rank turnover versus actual held-position turnover;
3. holding-period distribution and re-entry frequency;
4. contribution by trade, asset, listing cohort and liquidity cohort;
5. worst tail-loss trades and drawdown episodes;
6. rank persistence and score decay after entry;
7. Top-2 overlap with fixed V1 holdings;
8. decomposition of 2024 success and 2025 failure;
9. cost split between gross-beta changes and name switching;
10. effect of banding on forced/optional turnover;
11. inactive-symbol entry/exit timing;
12. capacity/slippage proxy by target notional and historical quote volume.

This audit may not change target weights, selection rules or thresholds.

---

## P1 — new low-turnover experiment only after attribution

A new monthly/persistence-controlled strategy may be considered only under a new experiment ID.

Potential structural hypotheses to evaluate later, not tune now:

- monthly rather than daily cross-sectional reselection;
- minimum rank-persistence before entry;
- hold-until-rank-exit rather than daily Top-N replacement;
- separate universe refresh cadence from exposure cadence;
- turnover budget or hysteresis applied uniformly;
- limit new-name entries while preserving BTC beta changes.

The attribution audit must determine which one has a causal justification. Do not run a broad parameter grid.

---

## P2 — fixed versus dynamic dispersion identity audit

No trading changes. Explain the 0.064 fixed/dynamic scale correlation through:

- universe breadth and size;
- constituent concentration;
- volume selection;
- sector/group contribution;
- inactive/dead-pool inclusion;
- false-positive/false-negative de-risk episodes.

This remains secondary to the alpha attribution audit.

---

## P3 — historical funding + Spot/Perp Router

Use accessible historical archives and attribute separately:

- funding;
- fees;
- basis;
- slippage;
- spot versus perp implementation;
- gross>1 leverage overlay;
- hedge/short carry.

This module optimizes implementation of an unchanged target exposure; it is not a new direction signal.

---

## P4 — Hyperliquid execution hardening

`execution/plan-b-bot` remains testnet/shadow only.

Engineering backlog:

1. metadata-derived size precision;
2. reversal and fill reconciliation;
3. partial/resting/rejected state handling;
4. order slicing;
5. persistent idempotency and audit logs;
6. notification isolation;
7. reduce-only emergency protection;
8. endpoint authorization;
9. mainnet double confirmation and allocation cap;
10. testnet end-to-end parity;
11. target-notional L2 slippage simulation.

---

## P5 — risk allocation and leverage last

Do not add covariance, LPM, volatility gates or leverage to rescue PIT-ALPHA-0016.

Only after alpha economics, funding and execution are controlled may the project reconsider:

- covariance / marginal risk contribution;
- downside/LPM estimators;
- normal beta cap around1.30;
- strong-trend hard maximum1.50.

## Stopping rules

Stop and retain BRRK-0011 if:

- attribution cannot identify a stable reason for rank-to-portfolio degradation;
- a new design requires moving multiple thresholds after seeing 0016;
- lower turnover is achieved only by selecting the historical winner;
- 2025+ failure persists;
- reasonable costs remove the edge;
- model complexity grows faster than independent market regimes.

The objective is a robust exposure-control system, not recovery of the fixed-universe historical CAGR.
