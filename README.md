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

## Current frontier

项目已经从“继续寻找新历史 alpha”转入 **capital structure / routing / execution / forward evidence** 阶段。

当前唯一 P0：**CARRY-PM-0035 — Hyperliquid Portfolio Margin account-behavior probe**。

它要回答的不是“carry 历史收益还能不能更高”，而是：

> 在已验证的 `UBTC spot + BTC short perp` 结构下，Portfolio Margin 对 short leg 的真实增量 maintenance consumption 到底是多少，能否解决 CARRY-STACK-0033 的资本占用/频繁缩放缺陷。

---

## Canonical strategy / implementation status

| Layer | Evidence | Decision |
|---|---|---|
| **BRRK-0011** | Price-only CAGR **65.10%**, MDD **-33.72%**, Sharpe **1.353**, Calmar **1.931** | **冻结为 directional core** |
| PIT-DISP-0015 | MDD/Sharpe 改善但牺牲 CAGR；固定 panel selection-sensitive | Diagnostic only |
| PIT-ALPHA-0016 / 0018 | Rank/persistence 有信息，但组合 MDD -66%~-69%，2025+ 为负 | **停止** |
| ASYM-BETA-0024 | Bull extra-beta 机制有效；strict funding-aware CAGR **64.82%**, MDD **-41.44%**, Sharpe **1.199** | 参数冻结；forward shadow only |
| TSMOM-ALPHA-0029 | Corr vs BRRK 低，但 CAGR **-4.12%**, MDD **-88.30%** | **拒绝并停止救援** |
| FUNDING-PNL-0003 | Hyperliquid all-perp CAGR **44.08%** vs price-only ~65% | **全 perp 默认实现拒绝** |
| ROUTER-DATA-0004 / PNL-0005 | BTC->UBTC spot verified；BTC-only spot accounting CAGR **56.20%** | BTC spot-first shadow candidate |
| **CARRY-PNL-0031** | CAGR **2.74%**, MDD **-7.01%**, Sharpe **1.428**, corr(BRRK) **-0.098** | **独立 carry 机制通过** |
| CARRY-AUDIT-0032 | SOL/XRP basis extrema 与官方 exact daily archive 一致 | 0031 数据归因通过 |
| **CARRY-STACK-0033** | BRRK+idle-capital carry CAGR/Sharpe/Calmar 均下降；allocation turnover **20.87x** | **该 stacking 方式拒绝** |
| **CARRY-IMPL-0034** | UBTC token index 197 当前 LTV **0.50**；BTC spot/perp books live | **BTC PM public feasibility PASS** |
| **CARRY-PM-0035** | 四阶段账户机制探针 | **当前 P0，尚未产生账户结果** |
| Hyperliquid executor | testnet/shadow skeleton | reconciliation / slippage / failure-path hardening required |

---

## Canonical BRRK economics

Price-only full historical result:

| Strategy | Final $10k | CAGR | MDD | Sharpe | Calmar |
|---|---:|---:|---:|---:|---:|
| V1 baseline | $57,116 | 61.26% | -37.64% | 1.295 | 1.628 |
| **BRRK-0011** | **$62,247** | **65.10%** | **-33.72%** | **1.353** | **1.931** |

Native-Hyperliquid common window (2023-06-18 through 2026-07-31):

| Implementation accounting | CAGR | MDD | Sharpe |
|---|---:|---:|---:|
| Price-only upper bound | 65.37% | -33.72% | 1.355 |
| Hyperliquid all-perp | **44.08%** | -37.04% | 1.046 |
| **Strict BTC-spot router** | **56.20%** | -34.95% | 1.229 |

The dominant implementation lesson is that instrument/funding choice can destroy more return than another round of signal tuning can plausibly recover.

---

## Carry research

### CARRY-PNL-0031

Frozen same-venue Binance `long spot + short perp` baseline across BTC/ETH/SOL/BNB/XRP:

- 5 bps CAGR: **2.740%**;
- MDD: **-7.005%**;
- annualized vol: **1.904%**;
- Sharpe: **1.428**;
- funding-only no-cost CAGR: **3.701%**;
- daily corr vs BRRK: **-0.098**;
- mean carry return on BRRK worst-decile days: positive.

This establishes an economically independent low-vol carry mechanism.

### CARRY-STACK-0033

The conservative rule `carry_scale = max(0, 1 - held_BRRK_gross)` failed:

- BRRK CAGR **56.66%** -> combined **56.04%**;
- Sharpe **1.235** -> **1.226**;
- Calmar **1.621** -> **1.597**;
- carry allocation turnover: **20.87x**;
- extra scale-change cost: about **1.043%**;
- net carry contribution: **-1.236%**.

Interpretation: **carry mechanism did not fail; using it as a daily BRRK idle-cash filler failed.** No historical scale/threshold/fixed-weight/leverage rescue is authorized.

### CARRY-IMPL-0034

Public Hyperliquid audit on 2026-08-05:

- selected BTC spot representation: `UBTC/USDC` (`@142`);
- UBTC token index: **197**;
- reserve LTV: **0.50**;
- BTC perp present;
- spot/perp books live;
- spot/perp midpoint basis at snapshot: **2.492 bps**;
- $100k UBTC simulated spot buy/sell slippage: **1.177 / 0.287 bps** within returned 20 levels.

Decision: **PASS_BTC_PUBLIC_FEASIBILITY**. This only authorizes the separate account-behavior probe in CARRY-PM-0035.

Formal result: [`research/results/CARRY_IMPL_0034_RESULT_2026-08-05.md`](research/results/CARRY_IMPL_0034_RESULT_2026-08-05.md)

---

## P0 — CARRY-PM-0035

Use a dedicated new account/subaccount with value below $1,000. Research code is read-only and never handles private keys or submits orders.

Frozen four-stage sequence:

```text
cash
  -> UBTC spot only
  -> same UBTC + matched BTC short perp
  -> close both legs
```

Primary measurement:

```text
incremental_maintenance_consumption_usdc
  = available_after_maintenance_USDC(spot-only)
    - available_after_maintenance_USDC(matched)

capital_factor
  = incremental_maintenance_consumption_usdc
    / matched_short_notional
```

Frozen structural gate:

- account abstraction = Portfolio Margin;
- PM enabled;
- dedicated account, no other perp positions;
- matched notional mismatch <= **2%**;
- matched portfolio margin ratio < **0.50**;
- measured incremental maintenance fraction <= **25%**;
- closed stage returns flat in BTC short and UBTC probe legs.

PASS authorizes only one separately preregistered PM-aware BRRK + frozen CARRY-0031 stack accounting experiment. No leverage/weight/funding-threshold search.

Preregistration: [`research/carry/CARRY-PM-0035.json`](research/carry/CARRY-PM-0035.json)  
Runbook: [`docs/CARRY_PM_0035_RUNBOOK.md`](docs/CARRY_PM_0035_RUNBOOK.md)

---

## Queue after 0035

### If 0035 passes

1. preregister exactly one `CARRY-STACK-0036-PM` capital rule using the observed PM capital factor;
2. preserve BRRK-0011 and CARRY-0031 unchanged;
3. test CAGR / Sharpe / MDD / Calmar / capital utilization / carry turnover;
4. if 0036 fails, stop historical carry stacking research.

### In parallel / afterwards

- strict BTC spot/perp forward shadow router;
- UETH/USOL identity/custody/redemption validation remains separate from PNL;
- executor reconciliation, partial/rejected/cancelled handling, TWAP/slicing, L2 slippage veto, idempotency, reduce-only kill paths;
- forward collection of funding, basis, depth, expected/realized slippage and fills;
- leverage remains last.

---

## Repository structure

```text
research/
  core/                 frozen strategy foundations
  regime_kelly/         BRRK state/risk research
  dispersion_overlay/   dispersion experiments
  pit_universe/          survivorship-aware universe and alpha tests
  tsmom/                 independent trend sleeve research
  carry/                 carry and Portfolio Margin experiments
  funding_router/        funding/router audits and accounting
  results/               durable reports and compact evidence
execution/
  plan-b-bot/            Hyperliquid testnet/shadow executor skeleton
docs/
  NEXT_STEPS.md
  RESEARCH_HISTORY.md
  CARRY_PM_0035_RUNBOOK.md
.github/workflows/       reproducible experiment and validation jobs
```

This repository is research software, not a representation that future returns will match backtests.
