# Next Steps

当前原则：**先验证偏差，再增加复杂度。**

## Completed gate — PIT-DISP-0015

PIT-DISP-0015 已在 2026-08-04 完成第一份合法、可复现、包含 later inactive/delisted assets 的 point-in-time 运行。

已持久化：

- exact `daily_equity.csv`；
- exact `daily_weights.csv`；
- daily dynamic-universe count；
- fixed/dynamic dispersion and exposure scales；
- inactive-symbol historical eligibility audit；
- exact daily `docs/pnl.svg`；
- full JSON report and formal result record。

研究结论：

- broad dynamic dispersion 的风险压缩机制成立；
- 但它降低 CAGR 和 upside capture，不满足 production promotion；
- fixed-panel DISP-0014 与 dynamic signal 的 scale correlation 只有约 0.064，证明0014 materially selection-sensitive；
- BRRK-0011 继续作为 canonical baseline；
- 0014 与0015都不允许在当前窗口上调参。

Formal result: `research/results/PIT_DISP_0015_RESULT_2026-08-04.md`。

---

## P0 — Point-in-time dynamic ALPHA universe

这是当前最高优先级。0015只解决 dispersion risk signal 的 universe bias，V1 alpha 仍使用固定的今天赢家集合。

### Primary question

> 当 own-trend + relative-strength 模型必须从当时真实存在的完整候选池中选择，并且不能事后删除后来失败/退市资产时，historical alpha 还剩多少？

### Frozen design requirements before first PnL

- 每个日期只使用当时真实存在且有 completed data 的资产；
- later delistings 在历史真实存在期间保留；
- stablecoins、fiat-like bases、wrapped duplicates 和 leveraged tokens 机械排除；
- 不使用今天的 market cap、rank 或 survivor status；
- 至少240个连续 completed daily rows；
- liquidity 使用 completed-day、point-in-time quote volume；
- ranking 之前必须满足 own absolute trend > 0；
- relative-to-BTC trend 作为第二层 eligibility / ranking；
- BTC regime 继续决定 risk-on / risk-off；
- gross <= 1 作为首轮主测试，不使用 leverage；
- 交易成本、rebalance band 和 t→t+1 no-lookahead 规则保持清晰。

### Top-N and concentration control

不能从 PnL 中挑最佳 N。首轮应 preregister 一个小 family 并全部报告，例如：

- Top-1；
- Top-2；
- Top-3；
- breadth-weighted sleeve。

同时报告：

- random-ranking placebo；
- equal-weight eligible-universe benchmark；
- BTC-only dynamic baseline；
- fixed V1 comparator；
- each asset contribution；
- top contributor share；
- later inactive/delisted asset contribution；
- turnover and realistic capacity diagnostics。

### Promotion gate

Dynamic alpha 只有在以下条件下才有资格继续：

1. 明显优于 random/placebo，而不仅仅是优于 cash；
2. 不依赖一个 SOL-like ex-post winner；
3. 2024+、2025+ 子区间不完全失效；
4. later inactive assets 的加入不使 edge 消失；
5. 对5–20bps成本压力不过度脆弱；
6. 不需要看到结果后移动 liquidity / age / Top-N 参数。

失败时保留 BRRK-0011，不继续复杂化 alpha。

---

## P0 Audit — fixed vs dynamic dispersion identity

这是 no-trading-change audit，可与 dynamic alpha implementation 并行。

目标：解释 fixed-panel DISP-0014 与 PIT-DISP-0015 的 scale correlation 为什么只有约0.064。

只做 attribution，不优化策略：

- dynamic universe size；
- top-5 / top-10 return contribution concentration；
- volume-weighted vs equal-weight dispersion；
- meme / L1 / DeFi / legacy-coin group contribution；
- inclusion/exclusion of BTC；
- inactive/dead-pool contribution；
- high-dispersion episode overlap；
- fixed-panel false-positive / false-negative de-risk episodes。

这一步的用途是理解 signal identity，不是寻找一个能恢复0014漂亮 PnL 的新公式。

---

## P1 — Funding history + Spot/Perp Router

当前没有有效 historical funding-aware PnL。

下一步：

1. 使用可访问的 historical funding archive，而不是被 HTTP 451 阻断的 endpoint；
2. 把 funding 作为 portfolio carry / execution routing input；
3. gross <= 1 的 directional long 比较 spot 与 perp 的真实净成本；
4. gross > 1 的额外 beta 单独核算 perp funding；
5. hedge/short 与 negative-funding long 单独归因；
6. funding、fees、slippage、basis 分开记录。

Spot/Perp Router 只优化同一 target exposure 的实现方式，不创造新的方向预测。

---

## P2 — Risk allocation after dynamic-alpha validation

只有 dynamic alpha 通过后再测试：

- covariance / marginal risk contribution；
- downside/LPM risk measure；
- correlation concentration；
- volatility shock；
- breadth / dispersion interaction。

禁止一次引入多个 gate。每个新模块单独 preregister、回测和 attribution。

PIT-0015 已经表明：一个经济上合理的风险信号也可能因为长期削减上涨 exposure 而降低最终 NAV。因此新风险模块必须同时报告 upside opportunity cost。

---

## P3 — Hyperliquid execution hardening

`execution/plan-b-bot` 当前只用于 testnet / shadow validation。

Engineering backlog：

1. 从 exchange metadata 动态读取 size decimals；
2. reversal close 后重新读取真实 position/fill；
3. 明确处理 partial fill / resting / rejected；
4. 大订单分片；
5. notification failure 不得让成功订单返回 HTTP 500；
6. persistent idempotency key 与 run audit log；
7. native reduce-only emergency orders；
8. status/account endpoint 权限保护；
9. mainnet double-confirm / allocation cap；
10. testnet end-to-end reconciliation；
11. daily signal 与 research implementation deterministic parity test；
12. target-notional L2 slippage simulation before submission。

---

## P4 — Leverage only after validation

现阶段 live candidate 优先 gross <= 1。

只有 dynamic universe、funding 和 execution 三层都验证后，才重新评估：

- normal beta cap around 1.30；
- strong-trend hard max 1.50；
- platform effective leverage 不接近 exchange maximum。

历史 CAGR 不能作为直接提高杠杆的理由。

---

## Stopping Rules

以下情况应停止优化并保留 BRRK-0011：

- dynamic-alpha edge 主要由极少数今天仍存活的赢家贡献；
- dead-pool inclusion 后 alpha 消失；
- edge 在合理成本/funding 压力下消失；
- 新模块只改善同一历史窗口，不能跨子区间；
- 需要不断移动 threshold 才能保持漂亮结果；
- 风险 overlay 的 drawdown improvement 由更大的 bull opportunity cost 换来；
- 参数数量增长快于独立有效市场 regime 数量。

研究目标不是最高 historical CAGR，而是得到**对未来仍有可解释性的 exposure-control system**。
