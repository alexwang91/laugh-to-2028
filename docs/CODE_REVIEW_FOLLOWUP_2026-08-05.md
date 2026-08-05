# 代码库复审 — 2026-08-05

只读复审。承接 [`CODE_REVIEW_2026-08-04.md`](CODE_REVIEW_2026-08-04.md)。未修改任何策略、参数或既有结果。

自上次审查以来 `main` 前进 16 个提交、+10,993 行、106 个文件，新增三条研究线（`asym_beta/`、`tsmom/`、`carry/`），README / NEXT_STEPS / RESEARCH_HISTORY 重写。

---

## 摘要

**最重要的一条：当前唯一 P0（CARRY-PM-0035）所依赖的 CARRY-PNL-0031，全窗口跑输现金。**

CARRY-PNL-0031 是 delta-neutral、gross=1.0、全额抵押的 long spot + short perp。它的合格门槛 `net_economics` 是**与零比较**。但对一个 delta-neutral 全额出资的账本，正确的门槛只能是现金——这个策略本身就是一个合成现金工具。

用同一窗口（2020-09-15 → 2026-07-30）的 3 个月美债：

| | CAGR | $10k → |
|---|---:|---:|
| CARRY-PNL-0031（5 bps 净） | **2.740%** | $11,720 |
| 3M T-bills，同窗口 | **3.165%** | **$12,007** |
| 超额 | **-0.425 pp/年** | |
| 报告 Sharpe | 1.428 | |
| **对现金的 Sharpe** | **-0.223** | |

而且全部收益来自一年：

| 年份 | carry | 现金 | 超额 |
|---|---:|---:|---:|
| 2020（09-15 起） | +0.83% | 0.03% | +0.80pp |
| **2021** | **+16.80%** | 0.05% | **+16.76pp** |
| 2022 | -6.52% | 2.04% | -8.55pp |
| 2023 | +1.27% | 5.19% | -3.92pp |
| 2024 | +4.57% | 5.11% | -0.54pp |
| 2025 | +0.69% | 4.15% | -3.46pp |
| 2026（至 07-30） | -0.17% | 2.12% | -2.29pp |

**2021 一年贡献了 +16.80%，全窗口累计只有 +17.20%。剔除 2021 后，4.9 年累计 +0.34%。**
**2021 之后的 4.58 年：carry -0.11%/年，现金 +4.06%/年，年化落后 4.17 个百分点。**

复算脚本：[`research/review_2026_08_04/verify_carry_vs_cash.py`](../research/review_2026_08_04/verify_carry_vs_cash.py)

其余两条：ASYM-BETA-0024 在 funding-aware 口径下被"直接给 BRRK 加杠杆"支配；README 现在把 3.65 年窗口明确标注成 "full historical result"，比上一版更不准确。

---

## 1. 上轮发现的处理状态

| # | 发现 | 状态 |
|---|---|---|
| §2.1 | `pit_alpha_0018` 缺报告与日志 | **未修**。`.gitignore` 的 `*_report.json` / `*.log` 原样保留；新实验改用 `summary.json` 命名绕开，根因仍在 |
| §2.2 | 加权协方差缺 `1/(1-Σw²)` 修正 | **未修**（逐行相同） |
| §2.3 | 未修正的 drawdown 起点版本并存 | **未修**。但新代码（0021/0022/0024）都 import `choose_scale_corrected`，走的是正确路径 |
| §2.4 | 前视泄漏死代码 + 未使用的 purge/embargo | **未修** |
| §2.5 | `api/cron.py` 授权可绕过 | **未修**（`execution/` 目录零改动） |
| §2.6 | 执行器无幂等 / 部分成交 / 反向非原子 | **未修**（同上）。README 仍把这些列在队列里 |
| §2.7 | CI `pull_request` + `contents: write` | **部分修**。13 个新 workflow 全部 `contents: read`；仍有 5 个旧的是 `write`：`funding-data-0001`、`funding-crossvenue-0002`、`funding-pnl-0003`、`pit-alpha-0018`、`pit-disp-0015` |
| §3.1 | 头条窗口未披露 | **变差**，见 N3 |
| §3.2/3.3 | 样本长度 / BRRK vs V1 不显著 | 未处理；新实验重复了同一模式，见 N2 |
| §3.5 | dispersion estimator 规模依赖 | 未处理（PIT-DISP-0015 已降级为 diagnostic，影响下降） |
| §3.6 | 研究/执行价格源与时点不一致 | 未处理。但 **AUDIT-0023 + ASYM-BETA-0024 独立发现了 latency 这一类缺陷**并做了修正，方向一致 |
| §3.8 | rf=0 与闲置现金不计息 | **未处理，且现在是决策性的**，见 N1 |
| §3.10 | 0018 丢失 delisting haircut | 未处理（PIT-ALPHA 线已停止） |

值得肯定：新 workflow 的权限收敛、AUDIT-0023 主动量化 latency 缺陷、TSMOM-ALPHA-0029 干脆拒绝（CAGR -4.12%、MDD -88.30%）、CARRY-STACK-0033 拒绝自己的 stacking 方式并写明"不授权任何历史 scale/threshold/固定权重/杠杆救援"——纪律 #7 在这两处执行得很好。

---

## 2. 新发现

### N1. CARRY 线的合格门槛用了错误的基准 —— 严重，影响当前 P0 **[已验证]**

见摘要。三点补充：

**这不是风格偏好。** 对方向性策略，rf=0 的 Sharpe 只是让数字好看一点（上轮 §3.8 量化为 ~0.08）。对 **delta-neutral 全额抵押**策略，现金就是它的直接替代品：gross 1.0 意味着 0.50 的 NAV 压在现货、其余压在空头保证金，**没有一分钱在赚利息**。拿它和零比，等于和"把钱烧掉"比。

**2021 是不可重复的机制。** 2021 是散户杠杆多头的顶峰，永续资金费率持续极端为正。这正是 RESULT.md 自己写的"funding-led"的来源——BTC +6.55%、ETH +7.30%、XRP +7.68% 的累计资金费贡献，绝大部分产生在那一年。纪律 #2（"固定赢家币池结果不能直接外推"）和纪律 #7 直接适用，但没有被应用。

**这解释了 CARRY-STACK-0033 为什么失败。** 0033 把失败归因于"allocation turnover 20.87x"和"额外 scale 变更成本约 1.043%"。但更根本的原因是：往 BRRK 的闲置现金里塞一个跑输现金的 sleeve，**在数学上必然降低组合收益**，跟换手率无关。0033 的结论"carry 机制没失败，是把它当日度闲置资金填充器失败了"——**在这个证据上站不住**。机制本身在 2021 之后就没有正超额。

**建议**：在 CARRY-PM-0035 消耗任何实盘资金之前，先补一个零成本的登记实验：把 0031 的 `net_economics` 门槛重定义为"净收益超过同期无风险利率"，重跑 0031 与 0033。如果 0031 在新门槛下不合格（按上表几乎必然），整条 carry 线应当按纪律 #7 停止，PM 探针也就没有必要了。

反过来说，如果 carry 要继续，唯一诚实的论证是"2021 型资金费率环境会再现"——那需要独立证据，而且必须先登记。

### N2. ASYM-BETA-0024 在 funding-aware 口径下被"给 BRRK 加杠杆"支配 —— 严重 **[代码/结果阅读]**

`research/results/asym_beta_0024/summary.json`：

| | price-only Sharpe | price-only Calmar | **funding-aware Sharpe** | **funding-aware Calmar** | funding-aware MDD |
|---|---:|---:|---:|---:|---:|
| BRRK0011_CORE | 1.3532 | 1.9328 | **1.2286** | **1.6082** | -34.95% |
| ASYM_BETA_0022_MONTHLY | 1.3465 | 1.9307 | 1.1824 | 1.5210 | -42.42% |
| **ASYM_BETA_0024_DAILY_CAP** | 1.3572 | 1.9620 | **1.1990** | **1.5644** | **-41.44%** |

**Sharpe 对杠杆是不变的**（忽略融资成本）。0024 的 funding-aware Sharpe 比 core 低 0.030，Calmar 低 0.044，MDD 深 6.5 个百分点。也就是说，**在项目自己认定为正确口径的 funding-aware 基础上，直接把 BRRK-0011 core 按任意倍数加杠杆，都严格优于 ASYM-BETA-0024**。extra-beta 这一层做的事情只是把一个更低的 Sharpe 换算成更高的 CAGR。

price-only 口径下 Sharpe +0.004（噪声），Calmar +0.029。纪律 #6 明确说"价格回测不是可部署 PNL"——那么判定就应该用 funding-aware 那一行。

0024 自己的月度归因也指向同一结论：

| 月份 | core strict | 0024 strict |
|---|---:|---:|
| 2024-04 | -19.87% | **-25.67%** |
| 2024-06 | -7.73% | **-10.04%** |

最差的两个月，extra-beta 各多亏 5.8 和 2.3 个百分点。AUDIT-0023 自己也写明"faster refresh 预期能处理 June 型 latency，但预期无法解决 April 2024"。

README 目前写的是"ASYM-BETA-0024 | Bull extra-beta 机制有效；strict funding-aware CAGR 64.82%, MDD -41.44%, Sharpe 1.199 | 参数冻结；forward shadow only"。引用了 Sharpe 1.199，但没有指出它低于 core 的 1.229——因为 core 的 funding-aware Sharpe 在**另一张表**里（"Strict BTC-spot router | 56.20% | -34.95% | 1.229"）。这个对比读者拿不到。

**建议**：把两张表合并成一张 funding-aware 对照表，让 core 与 0024 并排。然后按 0024 自己的 `promotion_evidence: false` 处理——现在的"参数冻结；forward shadow only"读起来像是通过了。

### N3. README 把 3.65 年窗口标注为 "full historical result" —— 比上一版更不准确 **[已验证]**

新 README：

> ## Canonical BRRK economics
> Price-only **full historical result**:
> | V1 baseline | $57,116 | 61.26% | -37.64% | 1.295 | 1.628 |
> | **BRRK-0011** | **$62,247** | **65.10%** | **-33.72%** | **1.353** | **1.931** |

这些数字来自 `pit_disp_0015/validated_summary.json`，其中明确写着 `"start": "2022-12-10", "end": "2026-08-02"` —— **3.65 年，不是完整历史**。上轮 §3.1 已验证：同一套构造从 2021-05-01 起算是 36.44% CAGR / -59.72% MDD / Calmar 0.61。

上一版 README 至少没有断言这是全历史；这一版加了 "full historical result"，把一个未披露的窗口升级成了一个**错误陈述**。Binance 的 BTC/ETH/BNB 现货数据可回溯到 2017，SOL 到 2020-08，面板起点是 2020-08-11——比 2022-12-10 早了两年四个月。

**建议**：改成 `Price-only result, 2022-12-10 .. 2026-08-02 (BRRK walk-forward OOS window)`，并另给一行 V1 的全面板数字。

### N4. gross 1.42 与"leverage remains last"政策直接矛盾 **[已验证]**

`run_asym_beta_0024.py:46` `GROSS_CAP = 1.50`，`summary.json` 记录 `max_final_held_gross = 1.4228`。

- `regime_kelly/config.py` 的 `research_gross_cap = 1.30`
- 上一版 README 的 P4：**"Do not reopen 1.30–1.50 beta until funding-aware routing, reconciliation, slippage controls and kill switches have forward evidence."**
- 新 README 队列仍写着 **"leverage remains last"**

而 reconciliation、slippage veto、kill switch 三项在 `execution/` 里一个都没实现（本次复审确认该目录零改动）。研究层已经跑在 1.42x 并"参数冻结"，政策层还在说杠杆排最后。**要么政策改，要么实验降级——不能两条同时挂在 README 上。**

### N5. 新实验只提交 `summary.json`，结论无法独立复算 **[已验证]**

新增的 14 个结果目录里，`asym_beta_0021/0022/0024`、`audit_0023/0025/0026`、`tsmom_data_0027`、`tsmom_pit_0028` **只有 `summary.json`**，没有日频权益、权重或收益序列。

对比 BRRK-0011：因为有 `pit_disp_0015/daily_equity.csv`，我在上一轮才能独立算出 PSR/DSR/MinTRL 和 BRRK vs V1 的配对 bootstrap（0.9948 相关、Sharpe 差不显著）。**ASYM-BETA-0024 的 "Sharpe 1.1990 vs 1.2286" 这个差，我这次无法做同样的显著性检验**——数据没提交。

而且 `*.log` 仍被 gitignore，新目录里一个日志都没有。

这与纪律 #3（"失败版本必须保留"）的精神相悖：保留了结论，没保留能重新检验结论的证据。

**建议**：每个产生 PNL 的实验至少提交 `daily_equity.csv`（一列一策略）。体积很小（BRRK 的 1332 行 6 列约 100KB），价值极高。

### N6. CARRY-PM-0035 的通过门槛无法区分"PM 释放保证金"与"测量失败" **[代码阅读]**

`run_carry_pm_0035.py`：

```python
raw_available_change = available_spot - available_matched
incremental_maintenance = max(0.0, raw_available_change)
incremental_fraction = incremental_maintenance / short_notional
```

`max(0, ·)` 与预登记 JSON 一致（`"incremental_maintenance_measurement": "max(0, ...)"`），所以代码没有违反冻结规范。但门槛本身有问题：

`incremental_fraction <= 0.25` 这个 gate，在下面三种情况下**都判 PASS**：

1. PM 正常工作、对冲被识别、保证金被释放（`raw_change < 0` → 钳到 0）；
2. PM 恰好消耗零增量保证金；
3. **两次快照之间价格漂移导致噪声把差值推成负数——即测量失败。**

第 3 种是真正的风险。而且这个被钳成 0 的 `capital_factor` 会直接喂给后续的 `CARRY-STACK-0036-PM` 资本规则——**一个测量失败会被当成"空头腿不占资本"的最优结论传下去。**

**快照之间没有任何时间或价格漂移约束。** 四个快照通过四次独立 CLI 调用采集，`available_after_maintenance` 依赖 mark price。现有的 `spot_quantity_preserved_to_matched`（UBTC 数量变动 ≤ 0.1%）只挡住"你又买了现货"，挡不住"BTC 在两次快照之间动了 2%"。$500 探针上 2% 的价格移动约 $10，与被测量的增量保证金同一量级——**测量误差可以和信号一样大**。

好消息是**所需数据已经全部采集**：`observed_at_utc`、`ubtc_spot_mid`、`btc_perp_mid` 都在快照里。补两个 check 即可，成本几乎为零：

```python
"snapshot_gap_within_bound":  (t_matched - t_spot) <= N minutes
"mid_drift_within_bound":     abs(mid_matched/mid_spot - 1) <= X
"measurement_sign_reported":  raw_available_change            # 单独作为一等公民结论
```

并且建议把 `raw_available_change < 0` 从"隐式 PASS"改成"显式的第三种状态"（`PM_RELEASES_MARGIN`），而不是和"消耗为零"混在一起。

其余小问题：`post_info` 六次连续 HTTP 调用无重试（研究代码里普遍有 6 次重试）；`MAX_PROBE_NOTIONAL_USD * 1.05` 的 5% 松弛在 README 里没有说明（runbook 里有）。

**注意**：脚本本身确实是只读的——只调 `/info`，不签名、不下单、地址只存 SHA-256 指纹、workflow 用 `if: github.event_name == 'workflow_dispatch'` 隔离 secret。这部分做得很好。

### N7. README 的 `capital_factor` 公式漏了 `max(0, ·)` **[已验证]**

README：

```text
incremental_maintenance_consumption_usdc
  = available_after_maintenance_USDC(spot-only) - available_after_maintenance_USDC(matched)
```

预登记 JSON 和代码都是 `max(0, ...)`。README 是唯一不一致的一处。小问题，但 README 是读者的第一入口，而这正是整个 P0 的主测量量。

### N8. BRRK0011_CORE 的 CAGR 在两处不一致 **[已验证]**

- `pit_disp_0015/validated_summary.json`：`"cagr": 0.6510389`（README 引用的 65.10%）
- `asym_beta_0024/summary.json`：`"cagr": 0.6516609785`（65.17%）

两处都标称 `BRRK0011_CORE` / `BRRK0011_BASELINE`，`final_10k` 完全相同（62247.3823），所以差异来自年数口径（`len(r)/365.25` vs 实际日历跨度）而非策略。0.07pp，不影响结论，但同一个"canonical"数字在仓库里有两个值，应当统一到一个 metrics 实现。

---

## 3. 建议优先级

### P0 — 在 CARRY-PM-0035 动用实盘资金之前

1. **用无风险利率重新评估 0031/0033**（N1）。零成本、纯记账，不需要新数据。如果 0031 在正确门槛下不合格，按纪律 #7 停止 carry 线，PM 探针自动取消。
2. 若仍决定跑 0035：补上快照时间/价格漂移约束，并把 `raw_available_change < 0` 单列为独立状态（N6）。

### P1 — 修正会误导读者的表述

3. README 去掉 "full historical result"，标注真实窗口（N3）
4. funding-aware 对照表把 core 与 0024 并排；按 `promotion_evidence: false` 重述 0024 的状态（N2）
5. 解决 gross 1.42 与 "leverage remains last" 的矛盾（N4）
6. README 的 `capital_factor` 公式补上 `max(0, ·)`（N7）
7. 统一 BRRK0011 CAGR 到单一 metrics 实现（N8）

### P2 — 证据基础设施（上轮 P0 未动，现在更要紧）

8. 修 `.gitignore` / 补回 `pit_alpha_0018` 报告与日志（上轮 §2.1）
9. 每个产生 PNL 的实验提交 `daily_equity.csv`（N5）
10. 加 `research/stats/inference.py`（PSR / DSR / MinTRL / 配对 bootstrap），接入所有 report（上轮 §4.1）。有了它，N2 那个 0.030 的 Sharpe 差会自动带出置信区间，不必等人工复审
11. 剩余 5 个 workflow 的 `contents: write` 收敛为 `read`（上轮 §2.7）

### P3 — 执行器（未动，且现在研究层已跑到 1.42x）

12–16. 幂等 / 部分成交 / 反向原子性与失败告警 / `szDecimals` / 杠杆上限告警（上轮 §2.6）
17. `api/cron.py` 授权（上轮 §2.5）

---

## 4. 值得肯定的部分

- **TSMOM-ALPHA-0029 被干脆拒绝**（CAGR -4.12%、MDD -88.30%），且写明"拒绝并停止救援"。
- **CARRY-STACK-0033 拒绝了自己的 stacking 方式**，并明确"不授权任何历史 scale/threshold/固定权重/杠杆救援"。纪律 #7 在这两处执行得很好——问题在于同样的标准没有用在 0031 的基准选择和 0024 的 funding-aware 结果上。
- **AUDIT-0023 主动量化 latency 缺陷**并驱动 0024，方向与上轮 §3.6 一致，且是他们自己独立发现的。
- **新 workflow 全部 `contents: read`**，`carry-pm-0035.yml` 用 `if: github.event_name == 'workflow_dispatch'` 把 secret 与 PR 运行隔离，地址只存 SHA-256 指纹。
- **CARRY-IMPL-0034 把公开可行性与账户行为严格分离**，`PASS_BTC_PUBLIC_FEASIBILITY` 只授权 0035 这一件事。
- **0024 的自校验**：`core_weight_max_abs_error 5e-11`、`reconstructed_0022_final_10k_error 0.0`、`gross cap violation` 直接抛异常——重构校验做得比大多数研究代码严格。
