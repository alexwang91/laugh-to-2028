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

## 11. CARRY-PM-0035 — current frontier

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

## 12. Current evidence hierarchy

| Component | Status |
|---|---|
| **BRRK-0011** | **Canonical directional core** |
| PIT dispersion | Diagnostic/shadow risk information |
| Dynamic PIT alpha | Mechanisms interesting; portfolio line stopped |
| ASYM-BETA-0024 | Forward-shadow bull-extra candidate only |
| TSMOM-0029 | Rejected |
| Funding data/cross-venue | Validated with source-role limits |
| All-perp BRRK implementation | Rejected |
| BTC strict spot router | Implementation/shadow candidate |
| **CARRY-PNL-0031** | **Qualified independent low-vol sleeve** |
| CARRY-STACK-0033 | Idle-capital stacking rule rejected |
| **CARRY-IMPL-0034** | **BTC PM public feasibility passed** |
| **CARRY-PM-0035** | **Current P0; account result pending** |
| Hyperliquid executor | Testnet/shadow; hardening required |
| Leverage | Deferred to final stage |
