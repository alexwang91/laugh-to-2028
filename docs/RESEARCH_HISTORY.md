# Research History

本项目的目标是建立一个低频、可审计的 crypto regime / rotation / risk-allocation 系统。研究原则是：只用完成日线、避免 lookahead、记录交易成本、先登记规则再评估，并把策略选择偏差与幸存者偏差作为一等问题。

## 1. BTC Dynamic Beta

最初核心使用 BTC 20/60/120/240 日风险调整动量，权重 0.15/0.25/0.30/0.30，并结合 30 日 realized volatility。负趋势时 beta 被压在 0.18–0.65；正趋势时从 1.0 向上扩张。0.05 rebalance band 明显降低不必要换手。

“最后一跌后人工跳升 beta”一类 recovery-jump 规则回测失败，已淘汰。

## 2. Fixed-universe rotation

第一版多资产模型固定使用 BTC/ETH/SOL/BNB：BTC 决定 regime；风险偏弱时 alt 为 0；风险偏强时 alt 必须同时满足绝对趋势和相对 BTC 趋势，再从合格资产里选 top 1–2。

2021-05-01 至 2026-08-02 的历史结果中，rotation cap 1.30 CAGR 约 44.7%，no-leverage 版本约 36.4%。但 SOL 是主要历史 alpha 来源：去掉 SOL 后 CAGR 降到约 20.3%。同时 2024 年之后 rotation 优势明显变弱，SOL 甚至成为拖累。

结论：历史 alpha 不是纯杠杆造成，但固定使用今天已知的成功资产存在严重 selection / survivorship bias，不能直接外推。

## 3. BRRK：从“预测市场”收缩为 risk-budget overlay

早期 BRRK-0004/0005 使用 HMM / scenario risk 直接缩放 V1，虽然降低回撤，但损失太多牛市收益。关键结论是：state model 有信息，但不应该替代 V1 alpha。

BRRK-0006 将 state model 的权限缩窄：正常状态默认接近完整 V1，只有 Risk-Off 概率上升时才给予 meta allocator 降风险权限。该结构首次在共同历史窗口同时改善增长和主要风险指标。

后续 robustness 说明：风险缩放是稀疏的，不是永久低仓位；execution lag 会快速削弱效果；deterministic halving/calendar-cycle 没提供足够独立信息；连续 blend 也弱于离散 authority 结构。

## 4. BRRK-0011：当前冻结研究基线

0011 只修正 path CDaR 的数学定义，没有改 alpha、HMM、state count、risk budget 或成本。修正后 headline 结果几乎不变，说明 BRRK 优势不是由旧 drawdown 计算错误造成。

| Model | CAGR | MDD | Sharpe | Calmar | Path CDaR95 | Upside capture | Downside capture |
|---|---:|---:|---:|---:|---:|---:|---:|
| V1 | 61.255% | -37.635% | 1.2950 | 1.6276 | 36.550% | 106.047% | 80.327% |
| **BRRK-0011** | **65.104%** | **-33.715%** | **1.3532** | **1.9310** | **31.781%** | 105.021% | **72.993%** |

**当前 frozen research baseline = BRRK-0011。**

## 5. Calibration audit

AUDIT-0012 对 44 个严格 prequential 20-day forecasts 做 PIT calibration。terminal-return distribution 没发现明显失准；maximum-drawdown distribution 反而偏保守，经常预测比实际更严重的 drawdown。

因此目前没有证据支持继续加厚尾部、增加额外 safety buffer，或在同一历史窗口内因为模型偏保守就放松 risk budget。

## 6. Dispersion experiments

### DISP-0013: alt -> BTC

当 ETH/SOL/BNB/XRP 的 20 日横截面 return dispersion 进入历史极端区间时，0013 将部分 alt 权重转回 BTC，不降低 gross。

BRRK-0011 + 0013 历史 CAGR 约 67.50%，Calmar 约 2.00。但 attribution audit 显示，真正改变 post-band 持仓的只有 29/1332 日，约 97% 的正贡献来自最大的三个 episode，集中于 2024-11 下旬至 12 月初。

结论：0013 是 high-NAV shadow candidate，但证据集中，不能升级为正式基线。

### DISP-0014: total exposure -> cash

0014 直接采用外部文献式 median-ratio dispersion scaling，不从 0013 PnL 里重新优化参数。

| Strategy | CAGR | MDD | Ann Vol | Sharpe | Calmar | Upside | Downside |
|---|---:|---:|---:|---:|---:|---:|---:|
| BRRK-0011 | 65.104% | -33.715% | 44.207% | 1.353 | 1.931 | 105.02% | 72.99% |
| + DISP-0014 | **65.709%** | **-30.603%** | **39.010%** | **1.488** | **2.147** | 98.45% | **62.40%** |

0014 更像 risk overlay 而不是 alpha enhancer。它牺牲一部分 upside capture，但显著降低波动、回撤和 downside capture。

**当前 strongest shadow risk-overlay candidate = DISP-0014。**

## 7. Point-in-time universe

PIT universe audit 找到 661 个历史普通 Binance spot-USDT candidates：当前约 471 个仍为 TRADING、189 个为 BREAK、另有 1 个已经不在 current exchangeInfo。至少 185 个历史候选在 2026-07 前已经结束。

历史候选池从 2020-08 的约 143 个扩张到 2026-07 的约 475 个。说明“今天仍活着的币”不是合法历史 universe。

数据访问审计进一步确认：BREAK / 已从当前 exchangeInfo 消失的 symbol 仍可通过 Binance public market-data API 获取历史日线，因此可以构建包含后来失败资产的 point-in-time panel。

## 8. PIT-DISP-0015：当前最关键实验

0015 已 preregister 并实现：历史普通 USDT universe；later inactive assets 在真实历史存在期间保留；最近 240 个 calendar days 必须连续有完整日线；completed-day quote volume >= $25m；20d return dispersion；使用 0014 原有 median-ratio + 0.8 smoothing；5 bps cost；无 lookahead。

**目前没有合法的 0015 PnL 结果。** 首次执行及多次 rerun 都在 hosted runner 启动前失败，表现为 0 steps / 0 logs / 0 artifacts，因此属于 CI/runner-start failure，不是模型失败。

## 9. Funding / execution

历史 funding backtest 曾尝试读取 Binance USD-M funding API，但 runner 收到 HTTP 451，因此不存在合法 historical funding-aware PnL 结果。Funding 目前只能作为待验证 execution/routing 模块，不能当作已证实 alpha。

Hyperliquid Plan B 已实现 BTC daily signal、portfolio beta conversion、testnet/shadow execution skeleton，但仍有 production engineering gaps，例如动态 size precision、fill reconciliation、partial-fill handling、order slicing、idempotency/audit log、emergency reduce-only protection 和 endpoint hardening。

## 10. 当前证据等级

| Component | Status |
|---|---|
| BTC Dynamic Beta | Frozen core concept |
| Fixed V1 Rotation | Historical alpha, selection-biased |
| **BRRK-0011** | **Frozen research baseline** |
| DISP-0013 | Shadow / lower evidence |
| **DISP-0014** | **Strongest shadow risk overlay** |
| **PIT-DISP-0015** | **Critical qualification test / pending** |
| Funding-aware historical PnL | Unvalidated |
| Hyperliquid Plan B | Testnet/shadow implementation |

## 11. Research stopping rule

在 PIT-DISP-0015 得到有效结果之前，不继续新增新的 volatility/breadth/dispersion threshold、halving heuristic 或 leverage rule。当前最大的未解决问题不是“还能不能加一个指标”，而是：

> 在历史上真实可获得、包含后来失败资产的 point-in-time universe 中，现有 edge 还能剩多少？

原始实验结果见 `research/results/`。
