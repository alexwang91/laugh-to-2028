# laugh-to-2028

一个以 **长期生存、可审计、可自动执行和减少回测自欺** 为目标的 crypto systematic-allocation research project。

核心纪律：

1. 机制有效不等于组合可用；
2. 固定赢家币池结果不能直接外推；
3. 先登记、后运行，失败版本必须保留；
4. 归因只能授权一种结构变化，不能授权参数搜索；
5. 研究信号和交易执行必须分层；
6. 价格回测不是可部署 PNL，funding、basis、fees、slippage 和 fills 必须单独验证；
7. 对同一历史窗口不无限救策略。

## Current status

| Layer | Evidence | Decision |
|---|---|---|
| BTC dynamic beta | Frozen core exposure concept | 保留 |
| Fixed-universe V1 | Strong historical result, materially asset-selection-biased | 不直接外推 |
| **BRRK-0011** | **Best frozen canonical alpha/risk target** | **当前研究基线** |
| DISP-0014 / PIT-DISP-0015 | Dispersion contains risk information; fixed-panel result is selection-sensitive | Diagnostic only |
| PIT-ALPHA-0016 / 0018 | Rank and persistence mechanisms work; broad portfolio has deep MDD and negative 2025+ | Portfolio rejected; alpha line stopped |
| FUNDING-DATA-0001 | Official Binance and Hyperliquid sources validated | Passed |
| FUNDING-CROSSVENUE-0002 | Binance is sign/regime proxy, not Hyperliquid level proxy | Passed with strict source-role limit |
| **FUNDING-PNL-0003** | Native Hyperliquid all-perp funding materially damages BRRK PNL | **All-perp gross≤1 default rejected** |
| **ROUTER-DATA-0004** | BTC spot verified via official BTC→UBTC UI remap; UETH/USOL candidate-only; no direct BNB/XRP spot | **Passed as implementation audit** |
| **ROUTER-PNL-0005** | BTC-only verified spot accounting lifts common-window CAGR 44.08% → **56.20%** | Exploratory accounting; **not production promotion evidence** |
| Hyperliquid executor | Testnet/shadow skeleton | Hardening required |

---

## Canonical price-only BRRK result

![Exact daily BRRK backtest PNL](docs/pnl.svg)

The canonical daily BRRK series uses completed UTC information, `t → t+1` execution, a 0.05 L1 rebalance band and 5 bps per absolute weight change.

| Strategy | Final $10k | CAGR | MDD | Sharpe | Calmar |
|---|---:|---:|---:|---:|---:|
| V1 baseline | $57,116 | 61.26% | -37.64% | 1.295 | 1.628 |
| **BRRK-0011** | **$62,247** | **65.10%** | **-33.72%** | **1.353** | **1.931** |
| BRRK + dynamic PIT-DISP-0015 | $56,543 | 60.81% | -30.40% | 1.393 | 2.000 |

`BRRK-0011` remains the canonical **directional target**. Implementation research must preserve that target unless a separately registered strategy experiment says otherwise.

---

## Funding and router economics

Common native-Hyperliquid funding window: **2023-06-18 through 2026-07-31**.

| Implementation accounting | Final $10k | CAGR | MDD | Sharpe | Calmar |
|---|---:|---:|---:|---:|---:|
| Price-only upper bound | $47,998 | 65.37% | -33.72% | 1.355 | 1.939 |
| Hyperliquid all-perp | $31,228 | 44.08% | -37.04% | 1.046 | 1.190 |
| **Strict verified spot: BTC only** | **$40,178** | **56.20%** | **-34.95%** | **1.229** | **1.608** |

Native Hyperliquid funding attribution over the common window is approximately:

- BTC: **-25.19%** additive contribution;
- SOL: **-13.40%**;
- ETH: **-3.05%**;
- BNB: **-1.33%**;
- XRP: approximately 0%.

`FUNDING-PNL-0003` therefore rejects a default all-perp architecture. `ROUTER-PNL-0005` shows that moving only the currently verified BTC exposure to spot recovers about **12.13 percentage points of CAGR** without changing the directional target.

Important limitation: **56.20% is not deployable net CAGR.** The 0005 accounting isolates funding recovery while preserving the original price-return path and backtest cost assumption. It does not invent historical spot fees, basis, spread, slippage or realized fills.

Detailed funding result: [`research/results/FUNDING_PNL_0003_FROZEN_HOLDINGS_2026-08-04.md`](research/results/FUNDING_PNL_0003_FROZEN_HOLDINGS_2026-08-04.md)  
Router availability result: [`research/results/ROUTER_DATA_0004_RESULT_2026-08-04.md`](research/results/ROUTER_DATA_0004_RESULT_2026-08-04.md)  
Strict router accounting: [`research/results/ROUTER_PNL_0005_RESULT_2026-08-04.md`](research/results/ROUTER_PNL_0005_RESULT_2026-08-04.md)

---

## Hyperliquid spot implementation audit

`ROUTER-DATA-0004` queried current HyperCore metadata and order books at fixed $1k / $10k / $50k / $100k notionals.

| Target | Current spot evidence | Router status |
|---|---|---|
| **BTC** | `UBTC/USDC`, official UI BTC→UBTC remap | **Verified for strict spot accounting/shadow** |
| ETH | `UETH/USDC` exists, noncanonical/contracted Unit representation | Candidate only |
| SOL | `USOL/USDC` exists, noncanonical/contracted Unit representation | Candidate only |
| BNB | No deterministic direct-USDC candidate | Perp-only / unavailable for strict spot router |
| XRP | No deterministic direct-USDC candidate | Perp-only / unavailable for strict spot router |

At the audited snapshot, BTC spot had about $523k returned ask depth and $606k bid depth; a $100k order was fully fillable within the returned book. This is a **snapshot**, not historical liquidity evidence.

### Mechanical counterfactual attribution

The following scenarios answer only how much historical funding drag would disappear **if** later evidence independently authorized those spot representations. They are not routing approvals.

| Spot-treated assets | CAGR | MDD | Status |
|---|---:|---:|---|
| BTC only | **56.20%** | -34.95% | Current strict verified case |
| BTC + ETH | 57.74% | -34.69% | Counterfactual only |
| BTC + SOL | **63.06%** | -34.23% | Counterfactual only |
| BTC + ETH + SOL | **64.66%** | -33.98% | Counterfactual only |
| All spot | 65.37% | -33.72% | Theoretical zero-funding ceiling |

This attribution makes **SOL identity / custody / redemption validation** the highest-value remaining spot question.

---

## Dynamic alpha research

The PIT dynamic-alpha line is stopped on the current historical window.

- PIT-ALPHA-0016 validated ranking information but produced 12.25% CAGR, -69.12% MDD and extreme churn.
- AUDIT-0017 identified daily name replacement as the dominant conversion defect.
- PIT-ALPHA-0018 reduced turnover and improved persistence, but still had -66.86% MDD and negative 2025+ economics.

No further threshold tuning is authorized on this sample. `BRRK-0011` remains the research baseline.

Detailed result: [`research/results/PIT_ALPHA_0018_RESULT_2026-08-04.md`](research/results/PIT_ALPHA_0018_RESULT_2026-08-04.md)

---

## Next research queue

### P0 — Unit identity / custody / redemption audit

Before UETH or USOL can be promoted from candidate-only to a verified spot substitute, establish with authoritative evidence:

1. exact economic identity and backing;
2. deposit / withdrawal / redemption path;
3. custody, bridge and contract risk;
4. fees, delays, limits and operational failure modes;
5. whether Hyperliquid officially maps the intended ETH/SOL UI exposure to those Unit assets;
6. deterministic fallback if redemption or spot execution is unavailable.

No PNL result may upgrade a token's identity classification.

### P1 — Strict Spot/Perp forward shadow router

First shadow rule:

```text
verified long spot capacity → spot
unverified / unavailable long exposure → perp
short or leverage overlay → perp
```

Start with BTC spot only. Record live funding, fees, basis, spread, L2 depth, expected VWAP, submitted orders, fills and fallback decisions. Do not manufacture historical liquidity or basis series from a single snapshot.

### P2 — Hyperliquid execution hardening

1. metadata-derived size precision;
2. pre/post account, order and fill reconciliation;
3. partial/resting/rejected/cancelled handling;
4. order slicing / TWAP;
5. persistent idempotency and audit logs;
6. live target-notional L2 slippage veto;
7. reduce-only emergency protection;
8. endpoint authorization and explicit mainnet confirmation;
9. deterministic parity between research target JSON and actual orders.

### P3 — Forward evidence

Accumulate BRRK signals, funding, mark/oracle premium, spot/perp basis, L2 depth, expected and realized slippage, routing decisions and realized fills without retuning targets.

### P4 — Leverage last

Do not reopen 1.30–1.50 beta until funding-aware routing, reconciliation, slippage controls and kill switches have forward evidence.

---

## Repository structure

```text
research/
  core/                 frozen strategy foundations
  regime_kelly/         BRRK state/risk research
  dispersion_overlay/   dispersion experiments
  pit_universe/          survivorship-aware universe and alpha tests
  funding_router/        funding, router audits and accounting
  results/               exact reports, CSVs, SVGs and logs
execution/
  plan-b-bot/            Hyperliquid testnet/shadow executor skeleton
docs/
  NEXT_STEPS.md
  RESEARCH_HISTORY.md
  MIGRATION_MANIFEST.md
.github/workflows/       reproducible experiments and validation jobs
```

Detailed stopping rules: [`docs/NEXT_STEPS.md`](docs/NEXT_STEPS.md)  
Research evolution: [`docs/RESEARCH_HISTORY.md`](docs/RESEARCH_HISTORY.md)

This repository is research software, not a representation that future returns will match backtests.