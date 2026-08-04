# Research History

本项目目标是建立一个低频、可审计的 crypto regime / rotation / risk-allocation system。基本纪律：completed data only、t→t+1 no lookahead、明确成本、先登记再评估，并把 model selection、asset selection 与 survivorship bias 作为一等问题。

## 1. BTC Dynamic Beta

BTC core 使用20/60/120/240日风险调整动量，权重0.15/0.25/0.30/0.30，并结合30日 realized volatility。负趋势时beta收缩至0.18–0.65；正趋势时从1.0向上扩张。0.05 rebalance band用于降低无效换手。

人工“最后一跌后跳升beta”规则回测失败并永久淘汰。

## 2. Fixed-universe V1 rotation

第一版多资产模型固定BTC/ETH/SOL/BNB：BTC决定regime；risk-off时alt为0；risk-on时alt必须同时满足绝对趋势和相对BTC趋势，再选择top1–2。

2021-05-01至2026-08-02，no-leverage fixed V1历史CAGR约36.4%。但SOL是主要历史alpha来源；去掉SOL后早期高杠杆版本CAGR大幅下降，且2024后优势显著减弱。

早期结论：alpha不只是杠杆造成，但固定今天已知赢家存在严重selection/survivorship bias，不能直接外推。

## 3. BRRK：从alpha engine收缩为risk authority

早期BRRK-0004/0005广泛缩放或替代V1，降低回撤但牺牲太多牛市收益。

BRRK-0006将HMM权限收窄：正常状态默认接近完整V1，只有Risk-Off概率上升时才允许meta allocator降风险。该结构首次在共同历史窗口同时改善增长与主要风险指标。

随后实验表明：

- risk scaling的有效性来自稀疏Risk-Off干预，而不是永久低仓位；
- execution lag会削弱结果；
- deterministic cycle/halving与CUSUM re-entry没有提供足够独立价值；
- HMM factor count存在显著model-specification uncertainty；
- persistent semantic anchoring与label-free替代方案均未超越基线。

## 4. BRRK-0011：冻结基线

0011只修正path CDaR数学定义，没有改alpha、HMM、state count、risk budget或成本。修正后headline结果几乎不变，说明BRRK优势不是旧drawdown bug造成。

| Model | CAGR | MDD | Sharpe | Calmar | CDaR95 | Up capture | Down capture |
|---|---:|---:|---:|---:|---:|---:|---:|
| V1 | 61.26% | -37.64% | 1.295 | 1.628 | 36.55% | 106.05% | 80.33% |
| **BRRK-0011** | **65.10%** | **-33.72%** | **1.353** | **1.931** | **31.78%** | 105.02% | **72.99%** |

**Canonical research baseline = BRRK-0011.**

## 5. Calibration audits

AUDIT-0010/0012对44个strictly prequential 20-day forecasts做coverage与PIT calibration。

- terminal-return distribution没有明显系统失准；
- maximum-drawdown distribution偏保守，经常预测比实际更严重的drawdown；
- 没有证据支持继续加厚尾部、增加conformal safety buffer或在同一窗口放松risk budget。

## 6. Fixed-panel dispersion experiments

### DISP-0013 — alt to BTC

当ETH/SOL/BNB/XRP的20日横截面return dispersion进入历史极端区间时，将部分alt权重转回BTC，不降低gross。

BRRK+0013 headline CAGR约67.5%，但post-band实际变化只有29/1332日，约97%的正episode贡献来自最大的三个episode，集中在2024年末。

Status: mechanistically plausible, event-concentrated, shadow only.

### DISP-0014 — total exposure to cash

0014采用外部文献式median-ratio scaling，不从0013 PNL重新优化参数。

| Strategy | CAGR | MDD | Vol | Sharpe | Calmar | Up | Down |
|---|---:|---:|---:|---:|---:|---:|---:|
| BRRK-0011 | 65.10% | -33.72% | 44.21% | 1.353 | 1.931 | 105.02% | 72.99% |
| + fixed DISP-0014 | 65.71% | -30.60% | 39.01% | 1.488 | 2.147 | 98.45% | 62.40% |

固定五币结果表现强，但后续PIT-DISP-0015证明其timing materially selection-sensitive。

## 7. Point-in-time universe engineering

Archive与lifecycle审计发现数百个历史Binance spot-USDT candidates，其中大量当前已BREAK或inactive。今天的survivor集合不是合法历史universe。

数据访问审计确认BREAK以及从current exchangeInfo消失的symbol仍可通过Binance public market-data API返回历史日线，因此可以构建dead-pool-inclusive panel。

## 8. PIT-DISP-0015 — risk-signal qualification

Frozen design:

- historical ordinary spot-USDT universe；
- later inactive assets在真实存在期间保留；
- 240连续completed rows；
- completed-day quote volume >=$25m；
- 20日横截面累计log-return dispersion；
- expanding-prior-median/current ratio，clip[0.10,1.00]；
- smoothing lambda0.80；
- total V1 exposure toward cash；
- 0.05 band，5bps，t→t+1。

Valid run:

- candidates652，symbols with rows646；
- zero fetch errors；
- 1,332 evaluation days；
- mean eligible universe30.62；
- 159 currently inactive/non-TRADING symbols historically eligible。

| Strategy | CAGR | MDD | Vol | Sharpe | Calmar | CDaR95 |
|---|---:|---:|---:|---:|---:|---:|
| BRRK-0011 | 65.10% | -33.72% | 44.21% | 1.353 | 1.931 | 31.78% |
| BRRK + fixed0014 | 65.71% | -30.60% | 39.01% | 1.488 | 2.147 | 28.85% |
| BRRK + dynamic0015 | 60.81% | -30.40% | 39.69% | 1.393 | 2.000 | 28.08% |

What survived:

- broad dispersion genuinely reduces MDD、CDaR、volatility与downside capture；
- risk mechanism survives dead-pool inclusion。

What failed:

- CAGR 65.10%→60.81%；
- upside capture明显下降；
- fixed与dynamic scale correlation只有0.064。

Decision:

- BRRK-0011 remains baseline；
- DISP-0014 downgraded to selection-sensitive diagnostic；
- PIT-DISP-0015 retained as broad-market risk diagnostic, not promoted；
- no post-result tuning。

## 9. PIT-ALPHA-0016 — alpha-mechanism qualification

### Frozen design

- 648 historical ordinary USDT candidates；
- 240连续completed rows；
- completed-day quote volume >=$25m；
- own trend >0 and relative-to-BTC trend >0；
- rank=`(0.5 own + 0.5 relative)/rv30`；
- Top-2 primary；
- gross<=1；
- 50%BTC core / 50%alt sleeve；
- universal alt cap35%；
- 0.05 band，5bps，t→t+1；
- 100 fixed-random-priority placebo seeds；
- Top1/Top2/Top3/equal-all完整报告；
- 5/10/20bps成本压力与missing-day haircut压力。

### Valid run integrity

- 648 candidates，646 with rows；
- zero fetch errors；
- panel 2019-01-01 to 2026-08-02；
- evaluation 2021-05-01 to 2026-08-02，1,920日；
- mean age/liquidity universe34.91；
- mean positive-trend eligible universe14.98；
- 152 currently inactive/non-TRADING symbols historically eligible。

### Portfolio family

| Strategy | CAGR | MDD | Sharpe | Calmar | Turnover |
|---|---:|---:|---:|---:|---:|
| Top-1 | 8.31% | -66.02% | 0.407 | 0.126 | 270.04 |
| **Top-2 primary** | **12.25%** | **-69.12%** | **0.480** | **0.177** | **349.62** |
| Top-3 | 0.71% | -76.39% | 0.268 | 0.009 | 333.03 |
| Equal all eligible | -24.91% | -82.93% | -0.266 | -0.300 | 352.62 |
| BTC dynamic | 11.07% | -54.31% | 0.461 | 0.204 | 40.44 |
| **Fixed V1 gross<=1** | **36.43%** | **-59.72%** | **0.889** | **0.610** | **131.81** |

### Ranking mechanism passed

The Top-2 rank:

- beat 98/100 placebo seeds on terminal NAV；
- beat 98/100 placebo seeds on Calmar；
- placebo median final value only$2,326 versus primary$18,354；
- largest positive contributor share13.14%；
- top-three share34.93%；
- positive contribution distributed acrossSOL、XRP、EGLD、AXS、DOGE、TRX以及later-inactive FTM/OM/RNDR等。

Conclusion: own-trend + relative-strength rank contains real cross-sectional information. It is not merely a current-survivor or single-SOL artifact.

### Portfolio conversion failed

- Top-2 CAGR12.25% versus fixed V136.43%；
- MDD-69.12% worse than fixed V1-59.72% and BTC dynamic-54.31%；
- turnover349.62；
- 2025+ CAGR negative；
- 10bps CAGR8.57%；
- 20bps CAGR1.57%，edge almost disappears。

The 0/-25/-50% first-missing-day stress did not bind because no symbol remained held on the first day its row disappeared. This does not prove delisting risk is zero.

### 0016 decision

- **Ranking mechanism validated.**
- **Portfolio specification rejected.**
- BRRK-0011 remains canonical baseline.
- PIT-ALPHA-0016 is not live/shadow portfolio eligible.
- No 0016 parameter may be tuned on this window.
- Next step is a no-trading-change attribution audit of churn、holding duration、tail losses、rank persistence、2024 success、2025 failure and fixed-V1 overlap.

## 10. Funding and execution

Historical funding backtest remains invalid because the first endpoint attempt receivedHTTP451. Funding is an unvalidated execution/routing variable, not established alpha.

Hyperliquid Plan B implements signal、portfolio conversion and testnet/shadow skeleton, but remains incomplete: dynamic precision、fill reconciliation、partial fills、slicing、idempotency、emergency protection and endpoint hardening are still open.

## 11. Current evidence hierarchy

| Component | Status |
|---|---|
| BTC Dynamic Beta | Frozen core concept |
| Fixed V1 | Strong historical alpha, selection-biased |
| **BRRK-0011** | **Canonical research baseline** |
| DISP-0013 | Event-concentrated diagnostic |
| DISP-0014 | Selection-sensitive fixed-panel diagnostic |
| PIT-DISP-0015 | Valid risk mechanism, portfolio not promoted |
| **PIT-ALPHA-0016 rank** | **Mechanism validated versus placebo** |
| **PIT-ALPHA-0016 portfolio** | **Rejected** |
| Funding-aware PNL | Unvalidated |
| Hyperliquid Plan B | Testnet/shadow implementation |

## 12. Current stopping rule

The next question is no longer whether broad trend ranking contains information. It does.

The current bottleneck is:

> Why does a rank that beats98% of placebos still translate into12.25%CAGR、-69%MDD and extreme turnover?

Until that attribution is completed, do not add HYPE by name, leverage, funding alpha, covariance optimizer, volatility gate or a large parameter grid.

Original experiment records and exact outputs are under `research/results/`.
