# 代码库审查 — 2026-08-04

只读审查。未修改任何策略、参数或既有结果。

审查范围：`research/`（core、regime_kelly、hybrid_meta、dispersion_overlay、pit_universe、funding_router、risk_metric_fix）、`execution/plan-b-bot/`、`.github/workflows/`、`docs/`。

本文中标注 **[已验证]** 的结论都由独立复算得到，脚本逻辑记录在正文中；标注 **[代码阅读]** 的是静态检查结论。

---

## 摘要

先说结论中最重要的三条：

1. **README 头条表格的评估窗口是 2022-12-10 → 2026-08-02（3.65 年），而 README 没有写出这一点。** 同一套 V1 权重构造换成 2021-05-01 起算，CAGR 从 61.31% 掉到 36.44%，MDD 从 -37.63% 变成 -59.72%，Calmar 从 1.63 变成 0.61。窗口起点在 2022-11-21 周期底部之后三周。**[已验证]**

2. **BRRK-0011 与 V1 的日收益相关性是 0.9948，Sharpe 差 +0.058，配对 bootstrap 的 95% 置信区间为 [-0.046, +0.164]，包含 0。** 把 BRRK-0011 定为"当前研究基线"、把 V1 降级，在这个样本上没有统计依据。整套 HMM + PCA + 变分推断 + 5000 路径 Monte Carlo + CVaR/CDaR 二分 + Kelly 对数最优搜索，最终输出是一个标量 scale，而这个标量有 81% 的交易日恰好等于 1.0。**[已验证]**

3. **纪律 #7（"对同一历史窗口不无限救策略"）执行得不一致。** PIT-ALPHA 线因为"negative 2025+ economics"被否决，但 BRRK-0011 的年度收益是 2023 +229.7%、2024 +83.2%、2025 **+9.1%**、2026 **-5.6%**——同样的问题，却保留为 canonical。**[已验证]**

另外确认了 7 个代码级缺陷和 12 处与实盘实践的差距，详见下文。

有一条我原本怀疑、但实测**证伪**的：`apply_band` 的权重漂移记账问题。见 §2.0。

---

## 1. 可复现性验证

先确认代码本身是忠实的。用 `research/core/crypto_rotation_backtest.py` 的原始函数、原始 Binance 数据源独立重跑：

| 指标 | README / validated_summary | 独立复算 |
|---|---:|---:|
| V1 baseline final $10k | $57,116 | $57,111 |
| V1 baseline CAGR | 61.25% | 61.31% |
| V1 baseline MDD | -37.63% | -37.63% |
| V1 baseline Sharpe | 1.295 | 1.295 |

**代码是可复现的，数值是诚实的。** 下面所有批评都是关于*这些数字意味着什么*，不是关于它们算错了。

---

## 2. 确认的逻辑缺陷

### 2.0 先说一个我证伪了的怀疑：band 的漂移记账

`run_portfolio` 把 `held` 当作再平衡之间的常数权重向量，而换手率算的是 `held.diff().abs()`。但"维持一个常数权重向量"在价格变动时是需要每天交易的，这部分交易没有被计费。我怀疑这会系统性低估成本。

实测（2021-05-01 → 2026-08-03，1921 天）：

| | 仓库口径 | 漂移一致口径 |
|---|---:|---:|
| B_ROTATION_BAND05 换手 | 158.29 | 159.93 |
| CAGR | 44.70% | **45.30%** |

**差距只有 1%，且方向对仓库不利（漂移口径 CAGR 更高）。** 原因是 beta 是连续变量，目标权重几乎每天都变，band 几乎每天都触发，漂移根本来不及累积。按 5bps 计，未计费部分约 0.1%/年。

**结论：不是问题，不需要修。** 但研究层和执行层的 band *语义*确实不同（见 §3.6），那是一致性问题。

### 2.1 `research/results/pit_alpha_0018/` 缺失主报告与日志 — 严重 **[已验证]**

`.gitignore` 含 `*_report.json` 和 `*.log`。`pit-alpha-0018.yml` 的持久化步骤用 `git add "$DEST"`，于是 `pit_alpha_0018_report.json` 和 `pit_alpha_0018.log` 被**静默丢弃**。

对比其他实验目录：

| 目录 | report.json | log |
|---|---|---|
| `pit_alpha_0016/` | ✅ `dynamic_alpha_report.json` | ✅ |
| `audit_0017_pit_alpha_attribution/` | ✅ | ✅ |
| `funding_pnl_0003/` | ✅ | ✅ |
| **`pit_alpha_0018/`** | ❌ **缺失** | ❌ **缺失** |

README 里"PIT-ALPHA-0018 … -66.86% MDD 且 2025+ 为负 → 组合被否决"这个结论，**在仓库里没有对应的原始报告可查**。这直接违反纪律 #3（"先登记、后运行，失败版本必须保留"）。

修法：把 `.gitignore` 的两条规则改成只作用于工作目录，例如

```gitignore
research/**/[a-z]*_outputs/**/*_report.json
*.log
!research/results/**/*.log
```

或者在 CI 里改用 `git add -f "$DEST"`。前者更好，因为它让规则本身正确。

### 2.2 `daily_distribution.py` 的加权协方差缺无偏修正 — 中等 **[代码阅读]**

`research/regime_kelly/daily_distribution.py:37`

```python
w = w / w.sum()
mu = np.sum(x * w[:, None], axis=0)
xc = x - mu
cov = (xc * w[:, None]).T @ xc          # 有偏
```

频率权重下的无偏加权协方差需要除以 `1 - Σwᵢ²`。这里没有，所以**协方差被系统性低估**，低估幅度约 `1/n_eff`。而 `n_eff` 正是同一函数算出来的（`1/Σw²`），拿来做修正是免费的。

后果：state-conditional 协方差偏小 → Monte Carlo 路径偏窄 → CVaR/CDaR 偏小 → `safe_max_scale` 偏大 → 仓位偏高。方向上是**朝着更激进的一侧错**。

### 2.3 两套 drawdown 计算并存，旧的那套有起点 bug — 中等 **[代码阅读]**

`risk_metric_fix/corrected_risk.py` 修正了"路径峰值不包含 t=0 的 wealth=1"这个 bug（第 15 行 `nav0 = concatenate([ones, nav])`），并且**已经**被 `dispersion_overlay/run_dispersion_overlay.py` 使用——BRRK-0011 用的是修正版，这点没问题。

但未修正的版本仍然存在且仍在被调用：

- `hybrid_meta/walkforward_v1_meta.py:194` `path_tail_risk`
- `regime_kelly/daily_distribution.py:174` `portfolio_path_cdar95`（定义了但全仓库无调用者）

`walkforward_v1_meta.py` 是可执行入口，跑它会产出用错误 CDaR 算出的仓位。保留失败版本是对的，但**可执行的错误版本和正确版本同名并存**，迟早有人跑错。建议把 `walkforward_v1_meta.py` 里的 `path_tail_risk` 直接改成 `from corrected_risk import path_tail_risk_corrected`，并在文件头注明"BRRK-MVP-0005 的历史结果由未修正版产生，见 BRRK_0011_CDAR_CORRECTION"。

### 2.4 死代码里藏着一个前视泄漏 — 低（但应清理）**[已验证无调用]**

`regime_kelly/regime_model.py:123` `fit_regime_model` 用 `train_forward_returns`（20 日前瞻收益）给 HMM 状态贴语义标签：

```python
"btc_fwd": wmean(fwd["BTC"]) ...
risk_score = st["btc_trend"] + 0.5*st["alt_breadth"] + 0.5*st["btc_fwd"]
```

如果传入的 forward returns 覆盖到训练窗口末尾，最后 20 行会用到窗口外的价格 —— 这正是 `config.py` 里 `purge_days=20` / `embargo_days=5` 想防的。

**这两个配置项在全仓库从未被引用。** 好消息是 `fit_regime_model`、`fit_daily_conditional_distribution`、`forward_log_returns`、`portfolio_path_cdar95` 也全都**没有调用者**——当前活跃路径走的是 `regime_model_vb_nd.semantic_mapping_no_dominance`，只用同期特征，没有泄漏。

所以这是**潜伏的**而非活跃的问题。建议要么删掉这些函数，要么在 `fit_regime_model` 开头加一句断言，强制调用者传入已经 purge 过的 forward returns。同时把 `purge_days`/`embargo_days` 从 config 里删掉——留着未被使用的安全配置项，会让读者误以为防护已经生效。

### 2.5 `api/cron.py` 授权可绕过 — 中等（安全）**[代码阅读]**

```python
def _authorized(headers, settings):
    auth = headers.get("Authorization")
    if settings.cron_secret:
        return auth == f"Bearer {settings.cron_secret}"     # 非常量时间比较
    if settings.can_trade:
        return False
    return headers.get("User-Agent") == "vercel-cron/1.0" or os.getenv("VERCEL") is None
```

两个问题：

1. `auth == f"Bearer {secret}"` 是非常量时间比较，对公网端点存在计时侧信道。应改用 `hmac.compare_digest`。
2. 未设 `CRON_SECRET` 时，shadow 模式下的授权条件是 `User-Agent == "vercel-cron/1.0"`——**User-Agent 完全由调用方控制**。任何人 `curl -H 'User-Agent: vercel-cron/1.0' https://<app>/api/cron` 就能拿到完整的 `payload`，其中包含 `nav_usd`、`hyperliquid_equity_usd`、`current_perp_qty`、`external_spot_btc_qty`——完整的持仓和净值。同时会触发一条 Telegram 推送。

即使 shadow 模式不下单，这也是账户信息泄漏 + 通知轰炸通道。建议：`CRON_SECRET` 无条件必填，`_authorized` 只保留 `hmac.compare_digest` 一条路径。

### 2.6 执行器：无幂等、部分成交当全成交、反向操作非原子 — 严重（上线前必须修）**[代码阅读]**

`execution/plan-b-bot/beta_bot/executor.py`：

- **无 `cloid`、无持久化状态、无去重。** `/api/cron` 的 Vercel `maxDuration` 是 60 秒。如果订单已被交易所接受但 HTTP 响应超时，下一次 cron 会读到（可能已陈旧的）`current_qty` 并**重复下单**。这是当前代码里风险最高的一处。
- **`_extract_status` 只看 `statuses[0]`，且把 `filled` 当作完全成交。** Hyperliquid 的 market IOC 订单会返回 `totalSz`，可能小于请求量。代码不比对 `totalSz` 与请求 size，也不在下单后重读 `clearinghouseState` 核对。**部分成交被静默当成完成。**
- **反向调仓非原子。** 先 `market_close` 再 `market_open`；第二步失败时异常向上抛出，`run_strategy` 末尾的 `send_telegram(...)` **永远不会执行**——账户被留在空仓状态，而且**没有任何告警**。至少要用 try/finally 保证通知发出。
- **`_round_size(size, decimals=5)` 硬编码 5 位小数**，而不是从 `meta` 的 `szDecimals` 取。BTC 当前恰好是 5，所以能跑，但这正是 README P2 第 1 条列的缺口。另外 Python 的 `round()` 是银行家舍入，可能向上取整，在最大仓位边缘会超出可用保证金；reduce 方向应该向零截断。
- **`update_leverage` 每次运行都调用一次**，是一个多余的状态变更调用；持仓存在时它可能失败，从而阻断整个流程。
- **杠杆上限触发时无告警。** `build_portfolio_plan` 把 `target_perp_notional` 夹到 `max_platform_leverage * equity`，此后 `delta_notional ≈ 0` → `reason="below_min_trade"`。系统报告"无需交易"，实际是"目标不可达"。这两种状态必须区分。

### 2.7 CI 工作流：`pull_request` + `contents: write` — 中等（供应链）**[代码阅读]**

`.github/workflows/pit-alpha-0018.yml`（其余实验工作流同构）：

```yaml
permissions:
  contents: write
on:
  pull_request:
...
      - uses: actions/checkout@v4
        with:
          ref: ${{ github.event.pull_request.head.sha || github.sha }}
      - run: python run_entry_rank_eligibility_exit.py
```

推送步骤有 `head.repo.full_name == github.repository` 的保护，但**写权限的 token 在更早的、执行 PR 代码的步骤里就已经可用**。同仓库分支上的一个恶意 PR 可以在 `run` 步骤中读取并外泄 token。

建议拆成两个 job：跑研究代码的 job 用 `permissions: contents: read`，持久化用单独的 `workflow_run` 或 `push` 触发的 job。

---

## 3. 与实盘实践的差距

### 3.1 头条指标的窗口未披露 —— 最重要的一条 **[已验证]**

`validated_summary.json` 写明 `"start": "2022-12-10", "end": "2026-08-02"`，但 README 的表格没有。同一套 gross≤1 的 V1 权重构造，只改起算日：

| 起算日 | 年数 | final $10k | CAGR | MDD | Sharpe | Calmar |
|---|---:|---:|---:|---:|---:|---:|
| 2021-05-01 | 5.25 | 51,160 | **36.44%** | **-59.72%** | 0.889 | **0.610** |
| 2021-11-10 | 4.73 | 31,566 | 27.54% | -44.99% | 0.791 | 0.612 |
| 2022-01-01 | 4.58 | 41,716 | 36.57% | -37.63% | 0.964 | 0.972 |
| 2022-06-01 | 4.17 | 47,580 | 45.37% | -37.63% | 1.098 | 1.205 |
| **2022-12-10** | **3.64** | **57,111** | **61.31%** | **-37.63%** | **1.295** | **1.629** ← README |
| 2023-06-18 | 3.12 | 44,232 | 60.96% | -37.63% | 1.290 | 1.620 |
| 2024-01-01 | 2.58 | 17,401 | 23.90% | -37.63% | 0.720 | 0.635 |

这个窗口**不是人为挑的**——它由 BRRK walk-forward 的 `min_train_days=600` 决定，是合法的 OOS 起点约束。问题在于三件事：

1. README 把它当成无条件的"canonical result"呈现，没有写窗口；
2. V1 baseline 作为对照**不需要**那个约束，完全可以在全样本上展示，却也被截到同一窗口；
3. 真正重要的后果是：**所有头条风险指标描述的都是同一个牛市周期**。2022-12-10 距 BTC 周期底部（2022-11-21，约 $15,476）只有三周。

相同长度（3.65 年）的滚动窗口共 20 个，CAGR 中位数 59.9%、最差 44.6%；MDD 中位数 -36.3%、最差 -59.7%。README 的数字落在第 65 百分位——在同长度窗口里不算极端。**但这 20 个窗口高度重叠、且全部落在同一个加密周期内，有效独立样本量约等于 1。**

建议：README 表格加上窗口列；V1 baseline 额外给出 2020-08 起的全样本数字；把"包含至少一个完整熊市"作为任何 promotion 的硬性前提。

### 3.2 样本长度不足以支撑 Sharpe 水平的声明 **[已验证]**

用仓库自己提交的 `pit_disp_0015/daily_equity.csv` 日收益，按 Bailey & López de Prado (2014) 计算：

| | BRRK-0011 | V1 |
|---|---:|---:|
| N | 1332 天（3.65 年） | 同 |
| 年化 Sharpe | 1.353 | 1.295 |
| 偏度 / 峰度 | +0.567 / 7.07 | +0.561 / 6.93 |
| PSR(SR\*=0) | 99.57% | 99.40% |
| PSR(SR\*=1.0) | 75.35% | 71.65% |
| **MinTRL，95% 置信断言年化 Sharpe > 1.0** | **20.97 年** | **30.10 年** |

Deflated Sharpe 在 K=100 次试验假设下仍有 98.9%——**"Sharpe 显著大于 0"这个结论是稳的**，不要误读成策略无效。

真正的约束是 MinTRL：**要在 95% 置信度下断言年化 Sharpe 超过 1.0，需要约 21 年日频数据；现有 3.65 年。** 峰度 7.07 让这个门槛进一步抬高。所以 "Sharpe 1.353 vs 1.295"、"Calmar 1.931 vs 1.628" 这类比较，在这个样本上不具备分辨力。

### 3.3 BRRK-0011 相对 V1 没有统计显著的改进 **[已验证]**

- 日收益相关性 **0.9948**
- Sharpe 差 +0.058，配对 bootstrap（4000 次）95% CI **[-0.046, +0.164]**，P(BRRK > V1) = 86.0%
- Calmar 差 95% CI **[-0.164, +0.599]**，P(BRRK > V1) = 83.8%

再看 BRRK-0011 的 scale 序列（`dispersion_scale.csv`）：**均值 0.855，中位数 1.000，81.1% 的交易日恰好等于 1.0。** 也就是说，HMM + PCA + 变分推断 + 5000 路径 Monte Carlo + CVaR/CDaR 二分 + Kelly 搜索这一整套机器，五分之四的时间在输出"不动"，全部贡献来自约 19% 的日子，净效果是 +0.058 Sharpe 且不显著。

这与仓库自己的文献综述第 6 条（Goyal 2026，walk-forward 再优化会损害 OOS）和第 2 条（Subanthran 2026，显式 regime 模型改善 MDD 但 Sharpe 跑输动量-波动基线）完全一致。**文献已经预测了这个结果，但结论没有被应用到 BRRK-0011 的定位上。**

### 3.4 纪律 #7 的执行不一致 **[已验证]**

年度收益：

| | 2022 | 2023 | 2024 | 2025 | 2026 |
|---|---:|---:|---:|---:|---:|
| V1 baseline | -1.4% | +232.7% | +83.2% | +7.9% | -11.9% |
| **BRRK-0011** | -0.0% | **+229.7%** | **+83.2%** | **+9.1%** | **-5.6%** |
| BRRK + dynamic DISP-0015 | -0.0% | +212.4% | +77.2% | +8.3% | -5.7% |

README 因为 "negative 2025+ economics" 否决了 PIT-ALPHA 线。BRRK-0011 是 2025 年 +9.1%、2026 年 -5.6%——**同一个判据，不同的处理**。

我不认为应该因此否决 BRRK-0011（它的 MDD 好得多，机制也更简单）。但判据必须写死并一致适用，否则纪律 #7 就变成了事后合理化。建议把停止规则写成可执行的检查，而不是散文。

### 3.5 dispersion 信号测的是 universe 组成，不是风险 **[已验证]**

`validated_summary.json` 里最刺眼的一个数字：**`fixed_dynamic_scale_correlation: 0.0641`**。同一个"dispersion"概念的两个实现，相关性 0.064——几乎正交。

原因在数据里：

- 合格 universe 规模：min 4，中位数 27，max 143
- 逐年中位数：2022→8，2023→20，2024→39，2025→30，2026→15（**逐年 5 倍变动**）
- `dynamic_dispersion` 均值 0.245 vs `fixed_panel_dispersion` 均值 0.087（**2.8 倍水平差**）

`run_dynamic_dispersion.dynamic_dispersion` 算的是横截面 20 日对数收益的样本标准差。当合格集从 8 个名字扩张到 39 个（新进来的多是更小、更波动的币），这个标准差**机械性地**上升，与市场风险无关。然后 `scale_from_dispersion` 拿它去除一个几乎恒定的扩展中位数（0.2332–0.2413），于是 scale 主要在追踪 universe 组成的变化。

这解释了为什么 dynamic 版本反而更差（60.81% vs 65.10% CAGR）。**这不是"dispersion 无效"，而是这个 estimator 没有跨期可比性。**

修法（任选其一，都需要新的实验 ID）：
- 固定横截面规模（例如始终取按成交额排名的前 N 名），或
- 用规模无关的统计量（横截面 MAD/中位数比、或对 n 做偏差修正），或
- 先把每个名字的收益按自身波动率标准化再取横截面离散度。

### 3.6 研究层与执行层的四处不一致 **[代码阅读]**

| 维度 | 研究层 | 执行层 |
|---|---|---|
| 价格源 | Binance **现货**日收盘 | Hyperliquid **永续** `candleSnapshot` |
| 成交时点 | 假设 UTC 00:00 边界 | Vercel cron `10 1 * * *` = **01:10 UTC** |
| band 语义 | target vs 上一次采纳的 target，L1 ≥ 0.05 | target_beta vs **实际** beta，差 ≥ 0.05 |
| 1.30–1.50 beta | 回测中**不存在**这个分支 | `ALLOW_STRONG_BETA` 可开启 |

第一条最要紧：**产生 65% CAGR 的那个信号，和实盘要算的信号，用的不是同一条价格序列。** 永续 mark 价与现货存在基差，Hyperliquid 的 BTC 历史更短更薄。冻结的 trend score 对输入序列不是不敏感的。

第二条：01:10 UTC 意味着每天迟 70 分钟建仓。按 4% 日波动折算，70 分钟的价格不确定性约 0.9%——无偏但纯噪声，且会与 band 产生交互（推迟触发/误触发）。

第四条：`compute_raw_beta` 里的 `strong_trend = trend_score >= 0.70 and realized_vol_30 <= 0.45` 分支在 `crypto_rotation_backtest.py` 中**完全没有对应物**。README P4 说"不要重开 1.30–1.50 beta"，默认值也确实是关的，但这条无回测支撑的路径通过环境变量就能打开。建议直接删掉，等有了正式实验再加回。

### 3.7 funding filter 的作用域和实证证据不匹配 **[代码阅读]**

`model.apply_funding_filter` 第一行：

```python
if raw_beta <= 1.0 or funding_apr <= 0.10:
    return raw_beta, "none"
```

**只在 beta > 1.0 时生效。** 但 FUNDING-PNL-0003 的结论是：native Hyperliquid funding 在共同窗口里让 BTC 贡献 **-25.19%**、SOL **-13.40%**——而策略绝大部分时间的 gross 在 0.18–1.0 之间。**实证上的 funding 损耗几乎全部发生在这个 filter 够不到的区间。**

同时 0.10 / 0.15 / 0.25 APR 这三个阈值没有任何回测或登记实验支撑。

### 3.8 无风险利率两边都没做 **[已验证]**

- Sharpe 全部按 rf = 0 计算（`crypto_rotation_backtest.metrics`、`run_dynamic_alpha.metrics`、`walkforward_v1_meta.metrics`、`run_frozen_holdings_funding_pnl.metrics` 都是）
- 闲置现金不计息。实测 2022-12-10 窗口内**平均闲置现金 20.5%**

两个方向相反、量级相近的偏差：

| rf | CAGR | Sharpe(raw) | Sharpe(excess) |
|---:|---:|---:|---:|
| 0.0% | 61.31% | 1.295 | 1.295 |
| 3.0% | 62.31% | 1.309 | 1.241 |
| 4.5% | 62.81% | 1.316 | **1.215** |

2023–2026 美元利率在 4–5% 区间。正确做法是两个都建模：现金按 T-bill 计息（CAGR +1.5pp），Sharpe 减去 rf（Sharpe -0.08）。目前的做法把两者都省略，看起来"相互抵消"，但对 CAGR 和 Sharpe 的影响方向不同，抵消不掉。

考虑到 §3.2 已经说明 Sharpe 1.353 vs 1.295 不可分辨，0.08 的系统性偏差量级上是可比的。

### 3.9 交易成本模型没有冲击项 **[代码阅读]**

全仓库统一 `COST_BPS = 5.0`，线性乘以 L1 换手。`run_dynamic_alpha` 有 5/10/20 bps 的成本压力测试，是好的实践。但线性模型对规模不敏感——ROUTER-DATA-0004 的快照显示 BTC 现货簿只有约 $523k ask / $606k bid 深度，$100k 单可以吃掉，但这是**单点快照**，README 自己也这么说。

PIT-ALPHA 线的换手更是问题：AUDIT-0017 已经识别出"每日换名"是主要转化缺陷。在几十上百个小市值 alt 上做高频轮动，线性成本模型必然低估。

### 3.10 delisting 压力测试在 0018 中被丢掉了 **[代码阅读]**

`run_dynamic_alpha.evaluate_array` 有 `missing_haircut` 参数，并跑了 0 / -25% / -50% 三档压力测试——这是很好的实践。

但 `run_entry_rank_eligibility_exit.evaluate_stateful`（0018）**没有这个参数**，也没有对应的压力测试。0018 的 `returns = np.nan_to_num(returns, nan=0.0)` 意味着退市资产先以 0% 收益持有，然后按最后价格平价退出——**退市在 0018 里是免费的**。

这是相对 0016 的严格性倒退。文献上，Univ. St. Gallen 的加密退市偏差研究报告等权组合的年化偏差可达 **62%** 量级——对 0018 这种在长尾 alt 上轮动的结构，这不是小数。

### 3.11 PIT universe 的错误容忍会造成选择性缺失 **[代码阅读]**

`run_dynamic_alpha.main`：

```python
if len(errors) > max(10, int(0.05 * len(symbols))):
    raise RuntimeError(...)
```

允许最多 5%（约 32 个）symbol 静默取数失败。**取数最容易失败的，恰恰是退市最久、最可能归零的那些币。** 这是选择性缺失，方向对策略有利。

`run_entry_rank_eligibility_exit.main` 用的是 `if errors: raise`，更严格，是对的。建议 0016 也改成零容忍，或者至少把失败的 symbol 列表持久化到结果里（目前 0016 的 report 里有 `fetch_errors`，0018 只有计数）。

顺带肯定一下：PIT-UNIVERSE-0003 专门验证了公开 REST API 能返回已退市 symbol 的历史（`BREAK` 状态 6/6、不在 exchangeInfo 的 1/1 都成功），并且注意到 NBTUSDT 的 API 历史比 S3 归档更长。**这是全仓库做得最扎实的一段工作**，survivorship 的处理明显强于行业常见做法。

### 3.12 spot/perp 反事实忽略了资金占用差异 **[代码阅读]**

`run_strict_router_accounting.scenario_equity` 把"转现货"实现为**把该资产的 funding 置零**，同时保留原始价格收益路径。加减号是对称的（负 funding 时的收入也一并去掉），这点是对的。

但现货和永续的差别不止 funding：现货占用全额资金，永续只占保证金。策略 gross 最高到 1.30，现货实现需要真实借贷；risk-off 时 beta 降到 0.18 需要真实卖出。报告里 `historical_spot_fee_basis_slippage: "NOT_INCLUDED"` 已经声明了，但**资金占用/借贷这一项没有列出来**，建议补进免责清单。

---

## 4. 结合最新文献的改进建议

仓库已有的 `research/literature/LITERATURE_2026-08-04.md` 覆盖了 regime 模型、下行风险、conformal 校准、change-point、再优化过拟合。以下是针对本次发现的**缺口**补充的文献。

### 4.1 多重检验与最小回测长度 —— 最该补的一块

仓库的文献综述完全没有覆盖 backtest overfitting 的统计工具，而这恰恰是当前最紧的约束。

- Bailey & López de Prado (2014), *The Deflated Sharpe Ratio: Correcting for Selection Bias, Backtest Overfitting and Non-Normality* — DSR / PSR，本报告 §3.2 已用它算出 MinTRL = 21 年。
- Bailey, Borwein, López de Prado & Zhu, *The Probability of Backtest Overfitting* — CSCV 计算 PBO，以及 Minimum Backtest Length。

**建议（P0，工程量小、价值高）**：在 `research/` 下加一个 `stats/inference.py`，实现 PSR / DSR / MinTRL / 配对 bootstrap，然后让**每一个** experiment report 的 JSON 里都带上这几个字段。这样"BRRK-0011 优于 V1"这类声明会自动附带置信区间，纪律 #7 就从散文变成可执行检查。本报告的复算脚本可以直接作为起点。

### 4.2 回测实现风险

- Yin, Miki, Lesnichenko & Gural (2026), *Implementation Risk in Portfolio Backtesting: A Previously Unquantified Source of Error* (arXiv:2603.20319)

正好对应 §3.6 的四处研究/执行不一致。**建议（P1）**：在 shadow 阶段每天同时记录"用 Binance 现货收盘算的目标 beta"和"用 Hyperliquid 永续收盘算的目标 beta"，把两者之差作为一个一等公民指标持续监控。如果这个差的分布不可忽略，冻结信号就必须重新定义在实际执行所用的价格源上。

### 4.3 crypto 退市与生存偏差

- *Survivorship and Delisting Bias in Cryptocurrency Markets* (Univ. St. Gallen) — 报告等权组合年化偏差量级可达 62%，并讨论退市收益应如何假设。

**建议（P1）**：把 0016 的 `missing_haircut` 压力测试恢复到 0018，并把 haircut 档位扩展到 -100%（完全归零）。当前 0018 的隐含假设是"退市 = 平价退出"，这是最乐观的一端。

### 4.4 永续资金费率的定价与可预测性

- Ackerer et al. (2026), *Perpetual Futures Pricing*, Mathematical Finance — 多种合约设定下的无套利估值。
- Inan, *Predictability of Funding Rates* (SSRN 5576424) — 用 DAR 模型对 Binance/Bybit BTC 永续资金费率做样本外预测，优于 no-change 基准，但**可预测性随时间变化**。
- Zhang (2026), *Funding Rate Mechanism in Perpetual Futures* (SSRN 6185958) — 把资金费率当作反馈控制规则而非被动转移，给出稳定性条件，并分析费率上限、clamp 型分段线性规则与清算驱动的崩溃。

**建议（P1）**：把 `apply_funding_filter` 重新定义在**全 beta 区间**上（见 §3.7），并且用预期 funding 而不是过去 24 小时均值。Zhang (2026) 的 clamp 机制分析对 Hyperliquid 尤其相关——它的资金费率有上下限，极端行情下会饱和，这会改变 filter 的响应形状。这需要一个新的登记实验，因为它改变交易目标。

### 4.5 crypto 市场冲击

- Talos (2025), *An Empirical Model of Market Impact in Cryptocurrency Trading* — 基于 60 个现货/永续标的、5 万个母单/5000 万个子单，把执行成本分解为价差、临时冲击与时间风险。
- 平方根冲击律在加密市场同样成立，且在子单层面就已出现。

**建议（P2）**：把 `COST_BPS` 从常数换成 `spread/2 + k·σ·sqrt(Q/V)` 形式，并对 PIT-ALPHA 线在 $100k / $1M / $10M 三档规模上重跑容量分析。目前 `capacity_proxy.csv` 已经存在，接上冲击模型就能给出真实容量上限。

### 4.6 已有文献综述中被低估的两条

仓库自己引用的两篇，结论其实比综述里写的更强：

- Subanthran (2026)：显式 regime 检测改善 MDD 但 Sharpe **显著跑输**动量-波动基线。
- Goyal (2026)：walk-forward 再优化会损害 OOS。

§3.3 的实测（相关性 0.995、Sharpe 差不显著、81% 的日子 scale = 1.0）**正是这两篇论文预测的结果**。综述把它们读成"保留 V1 alpha、用 HMM 控风险"的支持证据，但更严格的读法是：**HMM 层需要证明自己值得存在，而目前的证据不足以支撑它取代 V1 成为 canonical baseline。**

---

## 5. 建议的优先级

### P0 — 不改任何策略，先修可信度基础设施

1. 修 `.gitignore` / CI，补回 `pit_alpha_0018_report.json` 与日志（§2.1）
2. 加 `research/stats/inference.py`（PSR / DSR / MinTRL / 配对 bootstrap），并接入所有 experiment report（§4.1）
3. README 头条表格补上评估窗口，并对 V1 baseline 补一份全样本（2020-08 起）数字（§3.1）
4. 把纪律 #7 写成可执行的停止规则，一致适用于 BRRK 与 PIT-ALPHA（§3.4）

### P1 — 修正会影响结论的记账与安全问题

5. 加权协方差的无偏修正（§2.2）
6. 统一到 `corrected_risk`，或明确标注旧路径（§2.3）
7. 删除带前视泄漏的死代码与未使用的 purge/embargo 配置（§2.4）
8. `api/cron.py`：`CRON_SECRET` 无条件必填 + `hmac.compare_digest`（§2.5）
9. CI 工作流拆分权限（§2.7）
10. rf 与闲置现金同时建模（§3.8）
11. 恢复并加强 0018 的 delisting haircut 压力测试（§3.10 / §4.3）

### P2 — 上线前必须完成的执行硬化

12. 幂等：`cloid` + 持久化订单状态 + 重放保护（§2.6）—— **这是当前最高的单点风险**
13. 部分成交处理 + 下单后 `clearinghouseState` 核对（§2.6）
14. 反向调仓的原子性与失败告警（try/finally 保证通知）（§2.6）
15. `szDecimals` 从 meta 读取 + reduce 方向向零截断（§2.6）
16. 杠杆上限触发与"无需交易"两种状态分离告警（§2.6）
17. 删除无回测支撑的 `ALLOW_STRONG_BETA` 分支（§3.6）
18. shadow 阶段并行记录两条价格源的信号差（§4.2）
19. cron 时点对齐到 UTC 00:0x，或在回测中显式建模延迟（§3.6）

### P3 — 需要新登记实验的方法论改动

20. dispersion estimator 改为规模无关形式（§3.5）
21. funding filter 覆盖全 beta 区间并使用预期 funding（§3.7 / §4.4）
22. 平方根冲击成本模型 + 分规模容量分析（§4.5）
23. 在有了统计推断工具之后，重新评估 HMM 层是否值得保留（§3.3 / §4.6）

---

## 6. 值得肯定的部分

审查中看到的好实践，明确记录下来避免在整改中被误伤：

- **PIT-UNIVERSE-0003 的数据可达性审计**（用 S3 归档发现历史 symbol，再验证 REST API 能取回已退市 symbol 的历史，并交叉核对归档与 API 的时间跨度差异）——生存偏差处理明显强于行业常见水平。
- **placebo 检验**（`deterministic_priority` 用 SHA256 生成确定性随机优先级，100 个种子，报告百分位）——这是真正的证伪设计，不是装饰。
- **成本压力测试与 delisting haircut**（0016）。
- **`ROUTER-PNL-0005` 的自我标注**：`"promotion_evidence": false`、`"reason_not_preregistered"` 明确写出"该诊断是在观察到 0004 结果之后计算的，不得表述为预登记的 promotion 证据"——这种自律很少见。
- **`verified_spot_targets` 的一致性断言**：声明值与推导值不符时直接抛异常，而不是静默采用其一。
- **`all_perp_reconstruction_max_abs_error` 的重构校验**：用独立路径重算并与持久化结果比对，超过 1e-3 就失败。
- **funding 记账的完整性校验**：`validate_complete_blocks` 强制要求 8 小时区块无缺口、无缺资产。

这些机制的存在，正是本次审查能把问题定位到方法论层面（而不是停在"数字对不对"）的原因。
