# laugh-to-2028

一个以 **长期生存、可审计、可自动执行和减少回测自欺** 为目标的 crypto systematic-allocation research project。

当前原则：

1. 机制有效不等于组合可用；
2. 固定赢家币池结果不能直接外推；
3. 先登记、后运行，失败版本必须保留；
4. 归因只能授权一种结构变化，不能授权参数搜索；
5. 研究信号和交易执行必须分层；
6. 对同一历史窗口不再无限救策略。

## Current status

| Layer | Evidence | Decision |
|---|---|---|
| BTC dynamic beta | Frozen core exposure concept | 保留 |
| Fixed-universe V1 | Strong historical result, materially asset-selection-biased | 不直接外推 |
| **BRRK-0011** | **Best frozen canonical risk/alpha baseline** | **当前研究基线** |
| DISP-0014 | Strong fixed-panel risk result, selection-sensitive | Diagnostic only |
| PIT-DISP-0015 | Broad PIT dispersion compresses risk but sacrifices growth | Shadow diagnostic |
| PIT-ALPHA-0016 rank | Beats 98/100 same-universe random priorities | Ranking mechanism validated |
| PIT-ALPHA-0016 portfolio | Daily Top-2, extreme churn and -69.12% MDD | Rejected |
| AUDIT-0017 | 83.41% turnover from name switching; median hold 1 day | Dominant defect identified |
| **PIT-ALPHA-0018** | **Turnover/persistence repaired; 2025+ and drawdown still fail** | **Portfolio rejected; alpha line stopped** |
| Historical funding / Spot-Perp Router | Not yet validated | **Next research priority** |
| Hyperliquid execution | Testnet/shadow skeleton | Hardening required |

---

## Canonical BRRK / dispersion PNL

![Exact daily BRRK backtest PNL](docs/pnl.svg)

The chart uses 1,332 persisted daily equity observations from 2022-12-10 through 2026-08-02, completed UTC information, `t → t+1` execution, 0.05 L1 band and 5 bps per absolute weight change.

| Strategy | Final $10k | CAGR | MDD | Ann vol | Sharpe | Calmar | CDaR95 |
|---|---:|---:|---:|---:|---:|---:|---:|
| V1 baseline | $57,116 | 61.26% | -37.64% | 44.45% | 1.295 | 1.628 | 36.55% |
| **BRRK-0011** | **$62,247** | **65.10%** | **-33.72%** | 44.21% | **1.353** | **1.931** | 31.78% |
| BRRK + fixed DISP-0014 | $63,084 | 65.71% | -30.60% | 39.01% | 1.488 | 2.147 | 28.85% |
| BRRK + dynamic PIT-DISP-0015 | $56,543 | 60.81% | -30.40% | 39.69% | 1.393 | 2.000 | 28.08% |

### Current canonical decision

- `BRRK-0011` remains the canonical baseline.
- Fixed-panel `DISP-0014` and broad `PIT-DISP-0015` remain diagnostics.
- The fixed and broad dispersion scales correlate only about 0.064; the attractive fixed-panel result is materially panel-selection-sensitive.

Detailed result: [`research/results/PIT_DISP_0015_RESULT_2026-08-04.md`](research/results/PIT_DISP_0015_RESULT_2026-08-04.md)

---

## Dynamic alpha research

### PIT-ALPHA-0016 — ranking works, daily Top-2 portfolio fails

Rules were reconstructed on the historical point-in-time Binance USDT universe, including later inactive assets:

```text
240 consecutive completed daily rows
+ completed-day quote volume >= $25m
+ own trend > 0
+ relative-to-BTC trend > 0
+ rank = (0.5 own + 0.5 relative) / rv30
```

The rank beat **98/100** fixed-random-priority placebos, but daily Top-2 replacement produced:

- CAGR 12.25%;
- MDD -69.12%;
- turnover 349.62;
- median holding spell one day;
- negative 2025+ economics.

Decision: **ranking mechanism validated; portfolio rejected.**

Detailed result: [`research/results/PIT_ALPHA_0016_RESULT_2026-08-04.md`](research/results/PIT_ALPHA_0016_RESULT_2026-08-04.md)

### AUDIT-0017 — the exact conversion defect

The audit found:

- 83.41% of turnover was within-alt name switching;
- 653 holding spells across 113 alt symbols;
- median hold one day;
- only 19.35% of entries remained daily Top-2 after 30 days;
- but 52.07% remained broadly eligible;
- 30-day median forward return was -2.43%, while mean was +4.83%.

The rank has many small losers and a few large persistent winners. Daily Top-2 replacement exited winners before they compounded.

Detailed audit: [`research/results/AUDIT_0017_PIT_ALPHA_ATTRIBUTION_2026-08-04.md`](research/results/AUDIT_0017_PIT_ALPHA_ATTRIBUTION_2026-08-04.md)

### PIT-ALPHA-0018 — entry rank / eligibility exit

![Exact daily PIT-ALPHA-0018 PNL](research/results/pit_alpha_0018/pnl_daily.svg)

0018 changed only one authority:

```text
Top-2 rank fills vacancies
        ↓
incumbent stays while own trend, relative trend,
history and liquidity eligibility remain valid
        ↓
exit on eligibility loss or BTC risk-off
```

| Strategy | Final $10k | CAGR | MDD | Sharpe | Calmar | Turnover |
|---|---:|---:|---:|---:|---:|---:|
| **PIT-ALPHA-0018** | **$22,437** | **16.62%** | **-66.86%** | **0.555** | **0.249** | **141.86** |
| PIT-ALPHA-0016 daily Top-2 | $18,354 | 12.25% | -69.12% | 0.480 | 0.177 | 349.62 |
| BTC dynamic gross<=1 | $17,362 | 11.07% | -54.31% | 0.461 | 0.204 | 40.44 |
| Fixed V1 gross<=1 | $51,185 | 36.43% | -59.72% | 0.889 | 0.610 | 131.81 |

0018 confirms the audit mechanism:

- turnover falls about **59.4%**;
- holding spells fall from 653 to **188**;
- median hold rises from one to **three days**;
- maximum hold reaches 260 days;
- the rank still beats **98/100** same-state-machine placebos;
- 20 bps cost stress still retains 12.00% CAGR.

But the portfolio still fails:

- MDD remains **-66.86%**;
- 2025 return is **-10.03%**;
- 2026 through Aug 2 is **-11.06%**;
- 2025+ CAGR is **-13.11%**;
- contribution becomes more concentrated;
- fixed V1 remains materially superior historically.

**Decision:** the rank and persistence mechanisms are real, but the broad dynamic-alpha portfolio is rejected. No more threshold tuning is authorized on this window.

Detailed result: [`research/results/PIT_ALPHA_0018_RESULT_2026-08-04.md`](research/results/PIT_ALPHA_0018_RESULT_2026-08-04.md)

Exact outputs: [`research/results/pit_alpha_0018/`](research/results/pit_alpha_0018/)

---

## What the research now establishes

The evidence separates four claims:

| Claim | Result |
|---|---|
| Broad-market dispersion contains risk information | Supported |
| Own-trend + relative-strength ranking contains cross-sectional information | Supported |
| Daily broad-universe Top-2 is a viable portfolio | Rejected |
| Eligibility-exit persistence makes broad dynamic alpha deployable | Rejected |

The remaining problem is not random ranking or transaction cost alone. It is the combination of:

- highly right-skewed alt outcomes;
- deep cross-sectional tail risk;
- weak 2025+ persistence;
- broad-universe exposure during regimes where the ranking edge does not convert to acceptable compound wealth.

The project will **not** mine another exit threshold from the same history to rescue this line.

---

## Next research queue

### P0 — Historical funding + Spot/Perp Router

Keep target exposure unchanged and separately attribute:

- realized funding;
- spot/perp basis;
- fees;
- slippage;
- available spot inventory;
- cheapest instrument for each required exposure;
- perp use only when needed for leverage, shorting or advantageous negative funding.

This is implementation optimization, not a new directional alpha model.

### P1 — Hyperliquid execution hardening

Priorities:

1. metadata-derived size precision;
2. account/position/fill reconciliation;
3. partial, resting and rejected order handling;
4. order slicing / TWAP;
5. persistent idempotency and audit logs;
6. target-notional L2 VWAP / slippage-at-risk checks;
7. funding/carry routing;
8. reduce-only emergency protection;
9. endpoint authorization and mainnet double confirmation;
10. deterministic parity between research JSON and executor target.

### P2 — Forward shadow collection

Continue accumulating real Hyperliquid:

- funding;
- mark/oracle premium;
- L2 depth;
- expected VWAP/slippage by side and notional;
- signal outputs and subsequent realized PNL.

Promote a new variable only after forward evidence, not because it improves this historical window.

### P3 — Leverage last

Do not reconsider 1.30–1.50 beta before funding, costs, fills, execution and operational controls are validated.

---

## Repository structure

```text
research/
  core/                 frozen strategy foundations
  regime_kelly/         BRRK state/risk research
  dispersion_overlay/   dispersion experiments
  pit_universe/          survivorship-aware universe and alpha tests
  results/               exact reports, CSVs, SVGs and logs
execution/
  plan-b-bot/            Hyperliquid testnet/shadow executor skeleton
docs/
  NEXT_STEPS.md
  RESEARCH_HISTORY.md
  MIGRATION_MANIFEST.md
  pnl.svg
.github/workflows/       reproducible experiment and automation jobs
```

## Research discipline

- completed information only;
- `t → t+1` no-lookahead execution;
- stated transaction costs included;
- material tests preregistered;
- inactive/delisted assets retained historically;
- full registered family reported;
- rejected specifications remain rejected;
- attribution may authorize one structure, not a threshold search;
- research and execution remain separate;
- optimize future validity, not maximum historical CAGR.

Detailed stopping rules: [`docs/NEXT_STEPS.md`](docs/NEXT_STEPS.md)  
Research evolution: [`docs/RESEARCH_HISTORY.md`](docs/RESEARCH_HISTORY.md)

This repository is research software, not a representation that future returns will match backtests.
