# Research History

本项目目标是建立一个低频、可审计、可自动执行的 crypto regime / allocation system。研究纪律始终保持：completed data only、t→t+1 no lookahead、明确成本、先登记后运行、失败结果保留、禁止在同一历史窗口无限救援。

## 1. BTC Dynamic Beta / Fixed V1

早期 BTC core 使用 20/60/120/240 日风险调整趋势和 realized volatility 动态调整 beta。Fixed V1 使用 BTC/ETH/SOL/BNB rotation，risk-off 时 alt=0，risk-on 时 alt 必须同时满足绝对趋势与相对 BTC 趋势。

Fixed V1 历史表现较强，但后续 attribution 证明 SOL 是重要历史收益来源，当前 survivor/winner panel 不能合法外推为历史可交易 universe。

## 2. BRRK-0004 → BRRK-0011

BRRK 研究逐步把 HMM 从“alpha engine”收缩为稀疏 risk authority。永久低仓位会牺牲太多牛市收益，真正有效的是少数 Risk-Off 状态下的风险收缩。

BRRK-0011 只修正 path CDaR 数学定义，没有改变 alpha、HMM、risk budget 或成本。

| Model | CAGR | MDD | Sharpe | Calmar | CDaR95 |
|---|---:|---:|---:|---:|---:|
| V1 | 61.26% | -37.64% | 1.295 | 1.628 | 36.55% |
| **BRRK-0011** | **65.10%** | **-33.72%** | **1.353** | **1.931** | **31.78%** |

Decision: **BRRK-0011 frozen as canonical directional target**.

## 3. Dispersion line

### DISP-0013 / DISP-0014

Fixed-panel dispersion showed attractive risk compression, but episode concentration and panel selection were material concerns.

### PIT-DISP-0015

A dead-pool-inclusive historical Binance spot-USDT universe was constructed with 240 contiguous completed days and $25m completed-day liquidity.

Dynamic PIT dispersion retained real risk information:

- MDD -33.72% -> -30.40%;
- CDaR95 31.78% -> 28.08%;
- Sharpe 1.353 -> 1.393;

but CAGR fell 65.10% -> 60.81% and fixed-vs-dynamic scale correlation was only ~0.064.

Decision: dispersion retained as diagnostic/shadow risk information, not promoted.

## 4. Dynamic cross-sectional alpha line

### PIT-ALPHA-0016

Own-trend + relative-to-BTC rank beat 98/100 fixed-random-priority placebos on terminal NAV and Calmar, proving the ranking mechanism contains information.

Portfolio conversion failed:

- CAGR 12.25%;
- MDD -69.12%;
- Sharpe 0.480;
- turnover 349.62x;
- 2025+ CAGR negative.

### AUDIT-0017

Attribution showed 83.41% of turnover came from within-alt name switching. Median holding spell was only one day despite medium-horizon signals. Rare persistent winners produced a right-tailed payoff shape.

### PIT-ALPHA-0018

Eligibility-based incumbent persistence reduced turnover to 141.86x and improved CAGR to 16.62%, but MDD remained -66.86% and 2025+ economics stayed negative.

Decision: **dynamic-alpha portfolio line stopped on this historical window**.

## 5. Historical funding validation

### FUNDING-DATA-0001

Official Binance USD-M funding archives and Hyperliquid native fundingHistory were validated. Hyperliquid historically changed funding frequency; accounting must use actual event timestamps.

### FUNDING-CROSSVENUE-0002

Binance vs Hyperliquid overlap showed BTC/ETH/SOL/XRP reasonable sign/regime agreement but material level differences; BNB was structurally inconsistent.

Decision: Binance may serve only as sign/regime/stress proxy, not Hyperliquid funding level estimator.

### FUNDING-PNL-0003

Frozen BRRK held weights were charged native Hyperliquid funding.

Common 2023-06-18 through 2026-07-31:

| Scenario | CAGR | MDD | Sharpe |
|---|---:|---:|---:|
| Price-only | 65.37% | -33.72% | 1.355 |
| Hyperliquid all-perp | **44.08%** | **-37.04%** | **1.046** |

Native funding drag was dominated by BTC and SOL.

Decision: **all-perp default implementation rejected**.

## 6. Spot/perp router

### ROUTER-DATA-0004

Current Hyperliquid metadata and books were audited.

- BTC: verified through official UI BTC -> UBTC HyperCore remap;
- ETH: UETH candidate only;
- SOL: USOL candidate only;
- BNB/XRP: no deterministic direct-USDC candidate.

### ROUTER-PNL-0005

Funding-only accounting moved verified BTC long exposure to spot while preserving all targets.

- all-perp CAGR 44.08%;
- strict BTC-spot CAGR **56.20%**;
- price-only upper bound 65.37%.

Decision: BTC spot-first is an implementation/shadow candidate. UETH/USOL identity cannot be promoted from PNL.

## 7. Bull extra-beta line

### ASYM-BETA-0021

Applying the old absolute CVaR/CDaR budget to approve gross >1 made the extra sleeve structurally inert. Rejected.

### ASYM-BETA-0022

Downside-semivol control allowed bull extra beta and raised price-only CAGR to 78.89%, but strict funding-aware MDD worsened to -42.42% and Sharpe fell to 1.182.

### AUDIT-0023 / ASYM-BETA-0024

Daily refresh confirmed a real stale-holding defect in June 2024. A daily cap improved 0022 without changing BRRK core:

- strict CAGR 64.82%;
- MDD -41.44%;
- Sharpe 1.199.

April 2024 remained the dominant unresolved tail.

### AUDIT-0025 / 0026

Short-horizon trend masking was real but did not justify a simple 20d veto. Frozen semantic RISK_OFF probability was effectively absent during April 2024.

Decision: **stop historical rescue of the bull-extra tail; 0024 remains forward-shadow evidence only**.

## 8. TSMOM independent sleeve

### TSMOM-DATA-0027 / PIT-0028

Historical Binance USD-M perpetual archives produced 828 ordinary candidates and a daily PIT eligibility set preserving later-ended contracts. 550 contracts were historically eligible; no survivor substitution was used.

### TSMOM-ALPHA-0029

First valid funding-aware broad long/short TSMOM:

- CAGR **-4.12%**;
- MDD **-88.30%**;
- Sharpe **0.251**;
- daily corr vs BRRK **0.060**;
- mean return on BRRK worst-decile days **-0.589%**.

Decision: diversification correlation passed, economics/crisis-alpha failed. **TSMOM line stopped on this sample**.

## 9. Carry independent sleeve

### CARRY-DATA-0030

Official Binance same-venue spot/perp/funding data qualified for BTC/ETH/SOL/BNB/XRP with >=99% daily spot-perp alignment on every target.

### CARRY-PNL-0031

Frozen five-asset delta-neutral baseline:

- each asset +0.10 spot / -0.10 USD-M perp;
- total gross 1.0;
- no funding threshold, Top-K, basis threshold, leverage search or dynamic weighting;
- event-by-event funding;
- fixed 5/10/20 bps cost family.

Canonical 5 bps result:

- CAGR **2.740%**;
- MDD **-7.005%**;
- vol **1.904%**;
- Sharpe **1.428**;
- funding-only no-cost CAGR **3.701%**;
- corr vs BRRK **-0.098**;
- BRRK worst-decile mean carry return positive.

Decision: **independent carry mechanism qualified**.

### CARRY-AUDIT-0032

SOL (~-16.9%) and XRP (~-6.7%) basis extrema were cross-checked against exact official daily archives. Zero mismatches. Outlier dates contributed positive rather than artificial negative spread PNL.

Decision: data/source attribution passed.

### CARRY-STACK-0033

Carry was inserted only into BRRK idle gross:

```text
carry_scale = clip(1 - held_BRRK_gross, 0, 1)
```

Result:

- BRRK CAGR 56.66% -> combined **56.04%**;
- MDD -34.95% -> **-35.08%**;
- Sharpe 1.235 -> **1.226**;
- Calmar 1.621 -> **1.597**;
- average carry scale 25.55%;
- active 62.3% of days;
- scale turnover **20.87x**;
- extra scale-change cost ~**1.043%**;
- net carry contribution **-1.236%**.

Decision: **carry-as-daily-idle-cash-filler rejected**. The carry mechanism itself remains qualified.

## 10. Portfolio Margin implementation path

### CARRY-IMPL-0034

After 0033 failed, a separate public Hyperliquid Portfolio Margin audit asked whether matched spot + short perp could have a more capital-efficient implementation path.

2026-08-05 public snapshot:

- UBTC token index **197**;
- current reserve LTV **0.50**;
- BTC perp present;
- BTC spot/perp books live;
- spot/perp midpoint basis **2.492 bps**;
- $100k UBTC spot simulated buy/sell slippage **1.177 / 0.287 bps** within returned book.

Decision: **PASS_BTC_PUBLIC_FEASIBILITY**.

This only proves infrastructure/collateral eligibility. It does not measure account-level capital release.

Formal result: `research/results/CARRY_IMPL_0034_RESULT_2026-08-05.md`.

## 11. CARRY-PM-0035 — superseded and no longer required

**Status: not required.** `CARRY-RF-0036R1` re-priced CARRY-PNL-0031 against cash rather than zero and the sleeve failed the corrected `net_economics` gate, so the carry line is stopped under discipline #7 and no probe capital is committed. `CARRY-PM-0037` supersedes the gate design below with time/drift bounds and a three-state outcome, and is retained as corrected infrastructure that is not run. See section 11a and `docs/RISK_FREE_METRIC_CONVENTIONS.md`.

The description below is retained as the frozen 0035 design that 0037 replaced.

Preregistered account-behavior probe uses a dedicated Portfolio Margin account/subaccount below $1,000 and a probe notional capped at $500.

Frozen four-stage sequence:

```text
cash
-> UBTC spot only
-> UBTC + matched BTC short perp
-> close both probe legs
```

Primary account-level measurement:

```text
incremental_maintenance_consumption_usdc
  = available_after_maintenance_USDC(spot)
    - available_after_maintenance_USDC(matched)

capital_factor
  = incremental_maintenance_consumption_usdc
    / matched_short_notional
```

Frozen PASS requirements include:

- Portfolio Margin mode and flag active;
- no other perp positions;
- matched notional mismatch <=2%;
- portfolio margin ratio <0.50;
- incremental maintenance fraction <=25%;
- flat BTC/UBTC probe state after closing.

Research code is read-only and does not hold private keys or submit orders.

A PASS authorizes only one preregistered PM-aware BRRK + frozen CARRY-0031 stack accounting experiment. A FAIL/inconclusive result stops that path without threshold rescue.

## 11a. CARRY-RF-0036R1/R2 — the cash hurdle that stopped the carry line

CARRY-PNL-0031's `net_economics` gate tested net return against **zero**. For a delta-neutral, gross-1.0, fully collateralized book that is the wrong hurdle: the sleeve is itself a synthetic cash instrument, and every dollar in it displaces a dollar that could sit in T-bills.

Re-priced against FRED `DTB3` over the identical 2020-09-15..2026-07-30 window:

| measure | CARRY-PNL-0031 | cash |
|---|---:|---:|
| CAGR | **2.7404%** | **3.1653%** |
| final $10k | $11,719.83 | **$12,007.20** |
| excess CAGR | **-0.4249 pp/yr** | — |

The result is also a single year: 2021 returned **+16.80%** against a full-window cumulative of **+17.20%**. Excluding 2021 the sleeve returned +0.34% over ~4.9 years, and post-2021 it trails cash by roughly 4 pp/yr. CARRY-STACK-0033 fails the same way against the correct alternative for unused capital, BRRK plus idle-cash accrual.

Decision: **stop the carry line under discipline #7.** No BNB removal, funding-sign filter, basis threshold, alternate window, or weight/leverage change is authorized.

Two reporting caveats are recorded in `docs/RISK_FREE_METRIC_CONVENTIONS.md`: `excess_sharpe_over_rf` carries different denominators in R1 (-0.221582) and R2 (-0.223151), and the 0033 comparison must be quoted as an information ratio (**-10.31**) rather than either published excess Sharpe, because the two series are 0.9999953 correlated and the geometric ratio divides by nearly nothing.

Evidence: `research/results/carry_rf_0036r1/` (including daily sequences and the raw FRED CSV) and `research/results/carry_rf_0036r2/`.

## 11b. EXPOSURE-SMOOTH-0038 — mechanism validated, not promoted

`EXPOSURE-SMOOTH-0038-CONTINUOUS-BETA` tested one structural change to the frozen V1 exposure function: replace the discontinuous BTC `btc_last_drop_beta` branches with one continuous function using only constants already present in the frozen formula.

Full-panel evidence from 2021-05-01:

| Metric | Frozen V1 | Smooth-beta 0038 |
|---|---:|---:|
| CAGR | 36.38% | 34.13% |
| MDD | -59.72% | -43.20% |
| Sharpe | 0.888 | 0.966 |
| Calmar | 0.609 | 0.790 |

The 2021-05 crash drawdown improved from -59.72% to -30.11%, and turnover fell. The cost is also retained: 2023-style one-way bull performance was materially lower, the 2021-2022 bear Sharpe worsened, and the paired-bootstrap Sharpe difference still included zero.

Canonical decision:

```text
MECHANISM_VALIDATED_NOT_PROMOTED_BASELINE_UNCHANGED
```

Meaning:

- the mechanism result remains valid historical/shadow evidence;
- the 0038 function is not the canonical V1 exposure function;
- BRRK-0011 remains the frozen canonical directional research target;
- P3.2 must not substitute 0038 for the frozen baseline;
- no same-window retuning, leverage authorization, production authorization, or silent promotion is created;
- promotion would require a separate registered decision plus a full downstream BRRK regime/ref-table rerun.

Authority: `docs/EXPOSURE_SMOOTH_0038_DECISION_2026-08-06.md`, `config/decision_registry.json`, and `research/results/exposure_smooth_0038/summary.json`.

## 11c. F27 idle-cash-credit measurement normalization

The original F27 R1 overlay dropped the first realized equity observation by using `pct_change().dropna()`. The committed `daily_equity.csv` starts after the first realized strategy day, so R1 both discarded day-one PnL and shortened the measured calendar span by one day.

R2 preserves R1 as superseded historical measurement evidence and reconstructs day one from the known $10,000 base. It first reproduces the frozen calendar-span BRRK-0011 raw CAGR anchor `0.6516609785` before emitting any restated metrics.

Corrected R2 headline evidence:

| | V1 baseline | BRRK-0011 core |
|---|---:|---:|
| mean idle cash | 20.52% | 24.57% |
| raw CAGR | 61.3127% | 65.1661% |
| credited CAGR | 62.6632% | 66.8068% |
| CAGR delta | +1.3505 pp | +1.6407 pp |
| raw Sharpe (rf=0) | 1.2950 | 1.3532 |
| credited Sharpe (rf=0) | 1.3138 | 1.3756 |
| raw excess Sharpe | 1.2724 | 1.3667 |
| credited excess Sharpe | 1.3029 | 1.4039 |
| raw MDD | -37.6349% | -33.7151% |
| credited MDD | -36.6003% | -33.5524% |

BRRK-vs-V1 rf=0 Sharpe gap changes from `+0.0581629` to `+0.0617832`, a `+0.0036204` shift. The qualitative F27 conclusion is unchanged: crediting idle cash improves both variants and does not change the BRRK-0011 promotion decision.

Evidence: `research/results/idle_cash_credit_0027r1.json` (superseded measurement) and `research/results/idle_cash_credit_0027r2.json` (corrected measurement).

## 12. Current evidence hierarchy

| Component | Status |
|---|---|
| **BRRK-0011** | **Canonical directional core** |
| EXPOSURE-SMOOTH-0038 | Mechanism validated, **not promoted**; frozen V1/BRRK baseline unchanged |
| PIT dispersion | Diagnostic/shadow risk information |
| Dynamic PIT alpha | Mechanisms interesting; portfolio line stopped |
| ASYM-BETA-0024 | Forward-shadow bull-extra candidate only |
| TSMOM-0029 | Rejected |
| Funding data/cross-venue | Validated with source-role limits |
| All-perp BRRK implementation | Rejected |
| BTC strict spot router | Implementation/shadow candidate |
| **CARRY-PNL-0031** | **Rejected: fails net economics against cash (CARRY-RF-0036R1)** |
| CARRY-STACK-0033 | Rejected against both the original gate and BRRK + idle cash |
| CARRY-IMPL-0034 | Public feasibility valid; no downstream carry authorization |
| CARRY-PM-0035 / 0037 | **Not required; carry line stopped, no live probe** |
| Hyperliquid executor | Testnet/shadow; hardening required |
| Leverage | Deferred to final stage |
