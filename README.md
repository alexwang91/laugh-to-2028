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

**Carry 历史研究线已停止。** `CARRY-RF-0036R1` 将 CARRY-PNL-0031 从“相对零收益为正”重新定价为“相对现金为正”；随后 `CARRY-RF-0036R2` 仅校正 PR #30 指定的命名指标口径。最终可复算结果为：5 bps carry CAGR **2.740%**，同期 FRED `DTB3` 现金 CAGR **3.165%**，`excess_cagr_over_rf = -0.425 pp/yr`，`excess_sharpe_over_rf = -0.223`。因此 corrected `net_economics` **FAIL**，按纪律 #7 不再救援。

由此：**CARRY-PM-0035 不再需要执行；CARRY-PM-0037 作为 F2 的 measurement-integrity 修复保留，但同样不再需要投入 live probe capital。**

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
| **CARRY-PNL-0031** | 原报告 CAGR **2.74%**, Sharpe **1.428**；F1 复算同期 DTB3 CAGR **3.165%**, excess Sharpe **-0.223** | **corrected net_economics FAIL；carry 线停止** |
| CARRY-AUDIT-0032 | SOL/XRP basis extrema 与官方 exact daily archive 一致 | 数据归因通过，但不改变 F1 停止结论 |
| **CARRY-STACK-0033** | 原规则已拒绝；F1 再与 BRRK+idle cash 对照后仍为负超额 | **保持拒绝；不再解释为“standalone carry 仍通过”** |
| **CARRY-IMPL-0034** | UBTC token index 197 当前 LTV **0.50**；BTC spot/perp books live | public feasibility 有效，但无后续 carry 授权 |
| **CARRY-PM-0035** | 旧四阶段账户机制探针 | **NOT REQUIRED — upstream carry economics failed** |
| **CARRY-PM-0037** | F2 measurement-integrity gate：time/drift bounds + 3-state outcome + bounded retry | **实现保留；NOT REQUIRED，不运行 live probe** |
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

### CARRY-PNL-0031 — original report preserved, qualification restated by CARRY-RF-0036R1/R2

Frozen same-venue Binance `long spot + short perp` baseline across BTC/ETH/SOL/BNB/XRP originally reported:

- 5 bps CAGR: **2.740%**;
- MDD: **-7.005%**;
- annualized vol: **1.904%**;
- zero-hurdle Sharpe: **1.428**;
- funding-only no-cost CAGR: **3.701%**;
- daily corr vs BRRK: **-0.098**;
- mean carry return on BRRK worst-decile days: positive.

F1 did **not** change assets, weights, costs, funding accounting or window. `CARRY-RF-0036R1` changed only the economic hurdle to FRED 3-month T-bill `DTB3` cash on the identical 2020-09-15..2026-07-30 window. `CARRY-RF-0036R2` then corrected only the named `excess_sharpe_over_rf` reporting convention to match PR #30 exactly, using strategy annualized volatility as the denominator:

| Measure | Carry 0031 | DTB3 cash / excess |
|---|---:|---:|
| CAGR | **2.7404%** | cash **3.1653%** |
| Final $10k | **$11,719.83** | cash **$12,007.20** |
| excess CAGR | — | **-0.4249 pp/yr** |
| excess Sharpe over rf | — | **-0.22315** |

R1 的旧命名值 **-0.221582** 原样保留在 R1 报告中，作为使用 excess-return volatility 分母的旧诊断值；R2 不覆盖 R1，也不改变任何 gate 或策略结果。

2021 carry return was **+16.8037%** while full-window cumulative carry return was **+17.1983%**. The corrected `net_economics = excess return over rf > 0` gate therefore **FAILS**.

Decision: **stop the carry line under discipline #7.** No BNB removal, funding-sign filter, basis threshold, alternate window, weight/leverage change or other same-window rescue is authorized.

Exact restatement and daily evidence: [`research/results/carry_rf_0036r1/`](research/results/carry_rf_0036r1/)  
Reporting-parity correction: [`research/results/carry_rf_0036r2/`](research/results/carry_rf_0036r2/)

### CARRY-STACK-0033

The conservative rule `carry_scale = max(0, 1 - held_BRRK_gross)` had already failed its preregistered stack gate:

- BRRK CAGR **56.66%** -> combined **56.04%**;
- Sharpe **1.235** -> **1.226**;
- Calmar **1.621** -> **1.597**;
- carry allocation turnover: **20.87x**;
- extra scale-change cost: about **1.043%**;
- net carry contribution: **-1.236%**.

F1 additionally compares the combined stack against the correct alternative for unused BRRK capital: **BRRK + matched idle cash accrual**. The combined stack again has negative excess economics; corrected `net_economics_vs_idle_cash` **FAILS**. Under the R2 review convention, the stack's `excess_sharpe_over_rf` is **-0.04953**.

The earlier interpretation “carry mechanism did not fail; only the idle-cash conversion failed” is no longer supported after the cash-hurdle correction. Both the standalone economic gate and the 0033 conversion gate fail. No historical rescue is authorized.

### CARRY-IMPL-0034

Public Hyperliquid audit on 2026-08-05:

- selected BTC spot representation: `UBTC/USDC` (`@142`);
- UBTC token index: **197**;
- reserve LTV: **0.50**;
- BTC perp present;
- spot/perp books live;
- spot/perp midpoint basis at snapshot: **2.492 bps**;
- $100k UBTC simulated spot buy/sell slippage: **1.177 / 0.287 bps** within returned 20 levels.

`PASS_BTC_PUBLIC_FEASIBILITY` remains a valid implementation observation, but F1 removed the upstream economic authorization for a carry PM probe.

Formal result: [`research/results/CARRY_IMPL_0034_RESULT_2026-08-05.md`](research/results/CARRY_IMPL_0034_RESULT_2026-08-05.md)

---

## F2 — CARRY-PM-0037 measurement integrity

`CARRY-PM-0035.json` is preserved unchanged. Because F2 changes a frozen gate, the replacement was preregistered first as `CARRY-PM-0037-MEASUREMENT-INTEGRITY`.

The script remains strictly read-only: Hyperliquid `/info` only, no signing, no orders, public address stored only as a SHA-256 fingerprint.

Frozen F2 integrity bounds:

- spot -> matched snapshot gap <= **300 seconds**;
- UBTC spot midpoint drift <= **25 bps**;
- BTC perp midpoint drift <= **25 bps**;
- probe spot cap remains **$500**, with the already-existing fixed **5% execution tolerance** (`$525` observed-notional ceiling);
- `/info` calls use bounded retries: **4 attempts**, backoff **0.5 / 1 / 2 seconds**, only transport errors plus HTTP 408/429/5xx are retryable.

The old clamped single-number interpretation is replaced by explicit measurement states:

```text
PM_RELEASES_MARGIN
PM_CONSUMES_MARGIN
MEASUREMENT_INCONCLUSIVE
```

`snapshot_gap_within_bound` and `mid_drift_within_bound` must both pass before a release/consume interpretation is allowed. Failed drift/timing integrity produces `MEASUREMENT_INCONCLUSIVE`, not a false zero-consumption PASS.

Because F1 failed the upstream cash hurdle, **0035/0037 are not required and no live PM probe should be run**. F2 is retained as corrected measurement infrastructure, not as authorization to spend capital.

Preregistration: [`research/carry/CARRY-PM-0037.json`](research/carry/CARRY-PM-0037.json)  
Runbook: [`docs/CARRY_PM_0037_RUNBOOK.md`](docs/CARRY_PM_0037_RUNBOOK.md)

---

## Queue after F1/F2

There is no authorized historical carry rescue and no authorized PM carry stack experiment.

Continue only independent non-carry work already separated by the project disciplines:

- strict BTC spot/perp forward shadow router;
- UETH/USOL identity/custody/redemption validation remains separate from PNL;
- executor reconciliation, partial/rejected/cancelled handling, TWAP/slicing, L2 slippage veto, idempotency, reduce-only kill paths;
- forward collection of funding, basis, depth, expected/realized slippage and fills;
- leverage remains last.

This PR does not implement any `execution/` work.

---

## Repository structure

```text
research/
  common/               reusable research infrastructure, including risk-free series
  core/                 frozen strategy foundations
  regime_kelly/         BRRK state/risk research
  dispersion_overlay/   dispersion experiments
  pit_universe/          survivorship-aware universe and alpha tests
  tsmom/                 independent trend sleeve research
  carry/                 carry and Portfolio Margin experiments
  funding_router/        funding/router audits and accounting
  results/               durable reports and daily evidence
execution/
  plan-b-bot/            Hyperliquid testnet/shadow executor skeleton
docs/
  NEXT_STEPS.md
  RESEARCH_HISTORY.md
  CARRY_PM_0035_RUNBOOK.md
  CARRY_PM_0037_RUNBOOK.md
.github/workflows/       reproducible experiment and validation jobs
```

This repository is research software, not a representation that future returns will match backtests.
