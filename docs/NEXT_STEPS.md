# Next Steps

当前原则：**先验证偏差，再增加复杂度。**

## P0 — 让 PIT-DISP-0015 产生第一份合法结果

这是当前最高优先级。

必须保持 preregistered 参数不变：

- historical ordinary Binance spot-USDT universe；
- later BREAK / inactive symbols 在其真实历史存在期间保留；
- 240 个连续 completed daily rows；
- completed-day quote volume >= $25m；
- minimum cross-section = 5；
- 20d cumulative-log-return dispersion；
- `clip(expanding_prior_median/current, 0.10, 1.00)`；
- recursive smoothing lambda = 0.80；
- 0.05 rebalance band；
- 5 bps cost；
- t 日信息作用于 t+1。

### 0015 输出必须新增

下一次成功运行除了现有 JSON report，还应持久化：

- `daily_equity.csv`
- `daily_weights.csv`
- `daily_dynamic_universe_count.csv`
- `dispersion_scale.csv`
- exact daily `docs/pnl.svg`
- inactive/delisted symbols ever eligible audit

这样 README 的 PNL 图可以从当前“年度收益复利轨迹”升级为真实日级 equity curve。

### 0015 promotion gate

只有同时满足以下条件，DISP-0014 才能从 shadow candidate 升级：

1. dynamic-universe 方向与 fixed-panel 0014 一致；
2. MDD / downside capture / Calmar 的改善不是单一 episode 驱动；
3. 2024+ / 2025+ 子区间仍有合理风险改善；
4. transaction-cost sensitivity 不脆弱；
5. inactive/delisted assets 确实在历史 eligible universe 中出现；
6. 不需要看到结果后修改 $25m、240d、20d、0.10 或 0.80 参数。

如果失败，保留 BRRK-0011，0014 不 promotion。

---

## P1 — Point-in-time dynamic ALPHA universe

0015 只验证 dispersion risk signal，V1 alpha 仍使用固定的今天赢家集合。下一步必须解决 alpha universe 本身的 selection bias。

设计要求：

- 每个日期只使用当时真实存在、满足年龄与流动性条件的资产；
- later delistings 不能从历史删除；
- stablecoins / wrapped duplicates / leveraged tokens 机械排除；
- 不根据今天的市值/排名决定历史候选；
- ranking 之前先要求 own absolute trend > 0，再使用 relative-strength 排序；
- universe / Top-N family 必须 preregister 并整组报告，不能从 PnL 中挑 N；
- 独立报告 SOL、ETH、BNB 等历史赢家的 contribution，防止新版本仍被单一 winner 主导。

这是检验 V1 historical alpha 是否可泛化的真正 test。

---

## P2 — Funding history + Spot/Perp Router

当前没有有效 historical funding-aware PnL。

下一步：

1. 使用可访问的 historical funding archive，而不是被 HTTP 451 阻断的 endpoint；
2. 把 funding 作为 portfolio carry / execution routing 的输入；
3. 对 gross <= 1 的 directional long，比较 spot 与 perp 的真实净成本；
4. 对 gross > 1 的额外 beta 单独计算 perp funding；
5. hedge/short 与 negative-funding long 单独核算；
6. 将 funding、fees、slippage、basis 分开归因。

候选模块：Spot/Perp Router。它应优化同一个 target exposure 的实现方式，而不是创造新的方向性预测。

---

## P3 — Risk allocation after universe validation

只有 P0/P1 通过后再测试：

- covariance / marginal risk contribution；
- downside/LPM risk measure；
- correlation concentration；
- volatility shock；
- breadth / dispersion interaction。

禁止一次引入多个 gate。每个新模块必须单独登记、单独做 attribution。

---

## P4 — Hyperliquid execution hardening

`execution/plan-b-bot` 目前只应该用于 testnet / shadow validation。

工程 backlog：

1. 从 exchange metadata 动态读取 size decimals；
2. reversal close 后重新读取真实 position/fill；
3. 明确处理 partial fill / resting / rejected 状态；
4. 大订单分片；
5. 通知失败不得让成功订单返回 HTTP 500；
6. persistent idempotency key 与 run audit log；
7. native reduce-only emergency orders；
8. status/account endpoint 权限保护；
9. mainnet double-confirm / allocation cap；
10. testnet 完整 end-to-end reconciliation；
11. daily signal 输出与 research implementation 做 deterministic parity test。

---

## P5 — Leverage only after validation

现阶段 live candidate 应优先 gross <= 1。

只有 universe、funding、execution 三层都验证后，才重新评估：

- normal beta cap ~1.30；
- strong-trend hard max 1.50；
- platform effective leverage 不应接近 exchange max leverage。

不要用历史 CAGR 为理由直接提高杠杆。

---

## Stopping Rules

以下情况应停止优化并保留 BRRK-0011：

- 0015 survivor-aware 结果不能复现 0014 风险改善；
- dynamic-alpha edge 主要由极少数今天仍存活的赢家贡献；
- edge 对成本/funding 的合理压力测试消失；
- 新增模块只改善同一历史窗口、无法跨子区间；
- 需要不断移动 threshold 才保持漂亮结果。

研究目标不是得到最高历史 CAGR，而是得到**对未来仍有可解释性的 exposure-control system**。
