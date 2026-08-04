# Research History

本项目的目标是建立一个低频、可审计的 crypto regime / rotation / risk-allocation system。原则是：completed data only、no lookahead、明确交易成本、先登记再评估，并把 strategy-selection bias 与 survivorship bias 作为一等问题。

## 1. BTC Dynamic Beta

最初核心使用 BTC 20/60/120/240 日风险调整动量，权重 0.15/0.25/0.30/0.30，并结合30日 realized volatility。负趋势时 beta 压在0.18–0.65；正趋势时从1.0向上扩张。0.05 rebalance band 降低了不必要换手。

“最后一跌后人工跳升 beta”类 recovery-jump 规则回测失败，已淘汰。

## 2. Fixed-universe rotation

第一版多资产模型固定使用 BTC/ETH/SOL/BNB：BTC 决定 regime；风险偏弱时 alt 为0；风险偏强时 alt 必须同时满足绝对趋势和相对 BTC 趋势，再选 top 1–2。

2021-05-01 至 2026-08-02，rotation cap1.30 历史 CAGR约44.7%，no-leverage约36.4%。但 SOL 是主要历史 alpha 来源，去掉SOL后CAGR降到约20.3%；2024年后优势明显减弱，SOL甚至成为拖累。

结论：alpha不是纯杠杆造成，但固定今天已知赢家存在严重 selection/survivorship bias，不能直接外推。

## 3. BRRK：从 market predictor 收缩为 risk authority

早期 BRRK-0004/0005 使用 HMM/scenario risk 广泛缩放 V1，降低回撤但损失太多牛市收益。核心教训是：state model有条件信息，但不应该替代V1 alpha。

BRRK-0006 将权限收窄：正常状态默认接近完整V1，只有Risk-Off概率上升时才给予meta allocator降风险权限。该结构首次在共同历史窗口同时改善增长和主要风险指标。

Robustness结果表明风险缩放是稀疏的，不是永久低仓位；execution lag会削弱效果；deterministic cycle/halving没有提供足够独立信息。

## 4. BRRK-0011：当前冻结研究基线

0011只修正path CDaR数学定义，没有改alpha、HMM、state count、risk budget或成本。修正后headline结果几乎不变，说明BRRK优势不是旧drawdown计算错误造成。

| Model | CAGR | MDD | Sharpe | Calmar | Path CDaR95 | Upside capture | Downside capture |
|---|---:|---:|---:|---:|---:|---:|---:|
| V1 | 61.255% | -37.635% | 1.2950 | 1.6276 | 36.550% | 106.047% | 80.327% |
| **BRRK-0011** | **65.104%** | **-33.715%** | **1.3532** | **1.9310** | **31.781%** | 105.021% | **72.993%** |

**Canonical frozen research baseline = BRRK-0011。**

## 5. Calibration audits

AUDIT-0010/0012 对44个严格 prequential 20-day forecasts 做 coverage/PIT calibration。Terminal-return distribution没有明显失准；maximum-drawdown distribution反而偏保守，经常预测比实际更严重的drawdown。

因此没有证据支持继续加厚尾部、增加额外 safety buffer，或因为模型偏保守就在同一窗口放松risk budget。

## 6. Dispersion experiments

### DISP-0013 — alt to BTC

当 ETH/SOL/BNB/XRP 的20日横截面return dispersion进入历史极端区间时，将部分alt权重转回BTC，不降低gross。

BRRK+0013历史CAGR约67.50%，Calmar约2.00。但attribution显示post-band真正变化只有29/1332日，约97%的正episode贡献来自最大的三个episode，集中在2024-11下旬至12月初。

结论：机制合理但证据集中，shadow only。

### DISP-0014 — fixed-panel total exposure to cash

0014直接采用外部文献式median-ratio scaling，不从0013 PnL重新优化参数。

| Strategy | CAGR | MDD | Ann Vol | Sharpe | Calmar | Upside | Downside |
|---|---:|---:|---:|---:|---:|---:|---:|
| BRRK-0011 | 65.104% | -33.715% | 44.207% | 1.353 | 1.931 | 105.02% | 72.99% |
| + fixed DISP-0014 | **65.709%** | **-30.603%** | **39.010%** | **1.488** | **2.147** | 98.45% | **62.40%** |

固定五币结果表现出强风险压缩，但该结果后来被PIT-DISP-0015证明 materially selection-sensitive。

## 7. Point-in-time universe engineering

历史archive审计发现数百个普通 Binance spot-USDT candidates，其中大量当前已为BREAK或不再活跃。今天的survivor集合不是合法历史universe。

数据访问审计确认：BREAK及从current exchangeInfo消失的symbol仍可通过Binance public market-data API返回历史日线，因此可以构建真正包含后来失败资产的point-in-time panel。

## 8. PIT-DISP-0015 — completed qualification test

### Frozen design

- historical ordinary Binance spot-USDT candidates；
- later inactive assets在真实存在期间保留；
- 240个连续completed daily rows；
- completed-day quote volume >= $25m；
- minimum valid cross-section 5；
- 20d cumulative-log-return dispersion；
- expanding prior median/current ratio，clip到[0.10,1.00]；
- recursive smoothing lambda 0.80；
- total V1 exposure scaled toward cash；
- 0.05 L1 band，5bps cost，t signal held over t+1。

### Valid run integrity

2026-08-04首次成功完成：

- historical candidates 652；
- 646有历史数据；
- 1,120 API calls，0 fetch errors；
- 1,332 evaluation days；
- mean eligible universe 30.62，median 27，max 143；
- **159个当前inactive/non-TRADING symbols曾历史合格**。

因此该运行确实是dead-pool-inclusive，而不是today-survivor reconstruction。

### Result

| Strategy | CAGR | MDD | Ann Vol | Sharpe | Calmar | CDaR95 | Upside | Downside |
|---|---:|---:|---:|---:|---:|---:|---:|---:|
| BRRK-0011 | 65.104% | -33.715% | 44.207% | 1.353 | 1.931 | 31.781% | 105.02% | 72.99% |
| BRRK + fixed DISP-0014 | 65.709% | -30.603% | 39.010% | 1.488 | 2.147 | 28.850% | 98.45% | 62.40% |
| **BRRK + dynamic PIT-0015** | **60.809%** | **-30.398%** | **39.691%** | **1.393** | **2.000** | **28.078%** | 95.92% | **65.71%** |

### What survived

Broad point-in-time dispersion retained real risk compression versus BRRK-0011:

- MDD improvement约3.32pp；
- path CDaR improvement约3.70pp；
- annualized vol下降约4.52pp；
- downside capture 72.99%→65.71%；
- Sharpe 1.353→1.393；
- Calmar 1.931→2.000；
- turnover下降。

### What failed

- CAGR 65.10%→60.81%；
- 每$10,000初始资金最终少约$5,704；
- upside capture下降约9.10pp；
- 对fixed-panel 0014的headline风险调整指标无法复现。

Fixed-panel与dynamic smoothed scales的相关性只有**0.064**，mean absolute difference 0.122，dynamic exposure约69.1%的日子低于fixed-panel。

结论：固定BTC/ETH/SOL/BNB/XRP dispersion不是broad historical market dispersion的可靠代理，0014的漂亮结果明显受panel selection影响。

### Final decision

- BRRK-0011继续作为canonical baseline；
- DISP-0014降级为selection-sensitive fixed-panel diagnostic；
- PIT-0015保留为broad-market risk diagnostic/shadow overlay，不promotion；
- 禁止在该窗口调整0015参数；
- 下一主线转为point-in-time dynamic alpha universe。

完整结果：`research/results/PIT_DISP_0015_RESULT_2026-08-04.md`。

日级产物：`research/results/pit_disp_0015/`。

## 9. Funding / execution

历史funding backtest尝试读取Binance USD-M funding API，但runner收到HTTP451，因此不存在合法historical funding-aware PnL。Funding只能作为待验证execution/routing模块，不能当作已证实alpha。

Hyperliquid Plan B已实现daily signal、portfolio conversion和testnet/shadow skeleton，但仍有production gaps：dynamic size precision、fill reconciliation、partial fills、slicing、idempotency/audit log、emergency reduce-only protection和endpoint hardening。

## 10. Current evidence hierarchy

| Component | Status |
|---|---|
| BTC Dynamic Beta | Frozen core concept |
| Fixed V1 Rotation | Historical alpha, selection-biased |
| **BRRK-0011** | **Frozen canonical research baseline** |
| DISP-0013 | Shadow diagnostic / episode-concentrated |
| DISP-0014 | Fixed-panel diagnostic / selection-sensitive |
| **PIT-DISP-0015** | **Valid partial risk-mechanism validation; not promoted** |
| Dynamic point-in-time alpha | **Next critical qualification test** |
| Funding-aware historical PnL | Unvalidated |
| Hyperliquid Plan B | Testnet/shadow implementation |

## 11. Current stopping rule

PIT-DISP-0015解决了风险signal的survivorship test，但alpha layer仍未通过。

当前最大问题变为：

> 当V1必须从当时真实存在、包括后来失败与退市的资产中选择时，own-trend + relative-strength alpha还剩多少？

在dynamic alpha结果出现前，不新增leverage、HYPE hard-code、额外volatility gate或大规模optimizer complexity。

Original experiment records are under `research/results/`.
