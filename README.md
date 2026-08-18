# laugh-to-2028

一个面向长期生存、可审计研究和受治理自动执行的加密资产系统项目。

**研究结论、回测结果、代码合并、受控实验和生产授权属于不同层级。任何研究 PASS 都不会自动产生交易、签名、下单或资金转移权限。本仓库不构成收益承诺或投资建议。**

## 当前状态 — 2026-08-18

```text
Canonical BRRK-0011                  NO CHANGE
Phase 6                              NO CHANGE / ZERO AUTHORITY
Phase 7                              MONITOR_ONLY / LAUNCH BLOCKED
Phase 8                              TRIGGER ABSENT / NOT RUN
0070                                 10/10 CLOSED / PASS_LOCKED_EPISODE_ROBUSTNESS_REPLICATION
0071                                 6/10 BLOCKED / PREFLIGHT CONTAMINATION / ATTEMPT 0/1
0083                                 10/10 CLOSED / FAIL_NO_ROBUST_LOCKED_P02_ECONOMIC_CONTROLLER_VALUE / ATTEMPT 1/1
0072                                 2/10 / STAGE 3 PREREGISTRATION IN PROGRESS / ATTEMPT 0/1
production gross cap                 1.0
production_authorized_components = []
production_authorized                false
signature_authorized                 false
order_submission_authorized          false
```

## 研究治理原则

从 0069/0070 起，前瞻研究采用严格的十阶段生命周期：

1. OWNER-FIRST
2. DESIGN
3. PREREGISTRATION
4. IMPLEMENTATION
5. NONHISTORICAL QUALIFICATION
6. CONTROLLED BOUNDARY
7. ZERO-RESULT PREFLIGHT
8. UNIQUE CONTROLLED ATTEMPT
9. RESULT
10. IMMUTABLE CLOSEOUT

每个研究 ID 独立计算阶段。不得补写阶段、事后改门槛、消费 attempt 后重跑、根据结果调参救援、把旧 ID 的阶段转移给 replacement，或在 exact-head CI 失败/过期时合并。

## 0069–0083 关键研究历史

### 0069：事件提前预警

`BRRK-BTC-SOL-PATH-EVENT-EARLY-WARNING-EXECUTION-ASSURED-0069` 已关闭，终局为 `PASS_EVENT_EARLY_WARNING_ONLY`。它在预测层找到 SOL 长横盘事件的有效提前预警，但 controller/economic 层没有形成可用结果。attempt 1/1 已永久消费，同 ID 禁止重跑、调参、救援和重计算。

### 0070：锁定信号的 episode robustness replication

0070 已完成 10/10，终局为 `PASS_LOCKED_EPISODE_ROBUSTNESS_REPLICATION`。它在不重新选模、不重新训练、不调整 warning lead 的条件下，对 0069 锁定的 `P02_RAW_ELASTIC_NET_LOGIT | SOL | T4_LONG_SIDEWAYS | lead=10` 做 episode-level robustness replication，并通过冻结门槛。它仍属于 researcher-exposed development history，不是独立 OOS，也不产生生产授权。

### 0071：controller integration 治理事故

0071 已完成 OWNER-FIRST、DESIGN、PREREGISTRATION、IMPLEMENTATION、NONHISTORICAL QUALIFICATION 和 CONTROLLED BOUNDARY，共 6/10。随后在 Stage 7 ZERO-RESULT PREFLIGHT 中，在 durable `RUN_ATTEMPT.marker` 创建之前读取了受控 0069 `PRIMARY_RESULT.json` 内容。由于 roadmap 明确要求 Stage 7 对受控 scientific/history payload 保持零读取，0071 永久冻结为：

`BLOCKED_PRE_ATTEMPT_CONTROLLED_CONTENT_CONTAMINATION`

attempt 保持 0/1，不能补 marker、不能继续 Stage 8、不能伪造 RESULT/CLOSEOUT。事故记录于 Issue #295。治理 resolution #296 允许使用新的完整生命周期 replacement ID 0083，但不允许转移 0071 已完成阶段。

### 0083：0071 的完整 replacement

`BRRK-SOL-LONG-SIDEWAYS-CONTROLLER-INTEGRATION-REPLACEMENT-0083` 从 0/10 独立走完全部十阶段。Stage 8 唯一 attempt 按严格顺序执行：identity-only preflight PASS → durable attempt marker → controlled reads/execution → immutable result → marker-only finalization。

终局：

`FAIL_NO_ROBUST_LOCKED_P02_ECONOMIC_CONTROLLER_VALUE`

执行有效，common support = 685；6 个 selectable controller 中 0/6 通过，representative candidate = null。这个 FAIL 被 immutable closeout 永久封存，attempt 1/1 已消费，不允许同 ID rescue、retune、rerun 或 reinterpretation。

## 0071–0082 多策略研究计划

正式 roadmap：`research/governance/CRYPTO_MULTI_STRATEGY_RESEARCH_PROGRAM_0071_0082.md`，merge anchor：`169d9adf6531dc099a43541df413fef079322adf`。

roadmap 将 0071–0082 组织为串行、前瞻、逐 ID 治理的研究计划。0071 因治理事故由 0083 完整 replacement；治理 resolution 将 0072 的硬前置改为 0083 immutable closeout，且不要求 0083 PASS。因此 0083 的科学 FAIL 不阻止独立 carry-atlas 研究。

## 当前主线：0072 Carry Atlas

Research ID：`BRRK-CRYPTO-CARRY-ATLAS-0072`。

目标是建立 BTC / ETH / SOL 的 point-in-time funding、basis、carry 与 crowding 结构图谱。0072 本身只回答结构机制是否稳定、可复现，**不声称交易盈利，不把 strategy PnL、Sharpe 或 hedge-ratio optimization 偷渡进结构研究。**

已完成：

- OWNER-FIRST merge：`e1d61eadb8a4564cae2689a718e2eaaa859aa05e`
- DESIGN merge：`90a7b68718c5cb59002fe4b451d39d8979602161`
- Stage 3 source-identity precondition merge：`318adfe656ba1dfe4028ac3df388a96796e5ce60`
- Stage 3 first metadata-only capture boundary merge：`d8c9f3a262dadf1721103499f00fe9dcff4561ca`

当前正式完成度仍为 **2/10**。Stage 3 PREREGISTRATION 尚未完成。下一步只允许机械实现已经冻结的 `BRRK-CRYPTO-CARRY-ATLAS-0072-CAPTURE-0001`。

冻结的 first-capture 边界包括：

- cutoff：`2026-08-18T19:45:00Z`
- universe：BTC / ETH / SOL
- source roster：仅已冻结的 Binance / Bybit 官方公共接口
- automatic retry：0
- partial durable capture：fail closed，禁止自动二次抓取
- raw bytes 必须先持久化，再解析 metadata
- 对研究者只允许暴露 hash、row/time coverage、schema/missingness 和 support metadata
- 禁止在该 capture 中输出 funding/basis/OI 数值、相关性、回归、p-value、signal、position、PnL、performance 或 scientific classification
- 不创建 Stage 8 `RUN_ATTEMPT.marker`
- 不消费 Stage 8 attempt

Liquidation intensity 与 external attention 仍未资格化，不允许用第 11 个 family 替换；dated-futures / term-structure 只有 metadata support 能证明合法 PIT coverage 后才可进入完整 preregistration。

## 当前下一步

1. 在独立 wiring 分支机械实现已冻结的 metadata-only capture wiring。
2. 通过 exact-head standing CI 后合并 wiring，不提前执行 capture。
3. 按已合并 request 执行一次 create-only、0-retry、fail-closed metadata capture，取得真实 raw identities 和 support metadata，同时不暴露科学数值。
4. 基于真实 immutable identities 冻结完整 numerical/scientific PREREGISTRATION。
5. 只有完整 Stage 3 合并后，0072 才从 2/10 变为 3/10，并进入 Stage 4 IMPLEMENTATION。

## Canonical product boundaries

- directional core：**BRRK-0011**
- long target/tradable assets：**BTC / ETH / SOL / BNB**
- XRP：**feature-only**
- primary venue：**Hyperliquid**
- canonical decision boundary：**00:00 UTC**
- P3.2 target engine：`P3.2-BRRK0011-V1`
- P3.3 control：`P3.3-L1-BAND-V1`，aggregate L1 band `0.05`
- BNB：`PERP_ONLY_DEFAULT`
- production gross cap：`1.0`
- no P5 cycle overlay or >1 production leverage was promoted
- production/signature/submission/withdrawal/external-transfer authority：全部 false
- first real short authority：NONE

## Phase 6–8

Phase 6 现有 shadow implementation、durable evidence backend、valuation contract 和 identity-binding rules 不因 0069–0083 研究推进而改变。Phase 7 仍为 `MONITOR_ONLY`；Phase 8 仍为 trigger absent / not run。研究 PASS/FAIL 都不能自动修改生产权限。

## 状态与历史入口

- 本 README 的 `0069–0083 关键研究历史` 章节提供中文历史概览。
- 精确治理状态与 immutable anchors：`docs/CURRENT_STATE.md`
- 正式 roadmap：`research/governance/CRYPTO_MULTI_STRATEGY_RESEARCH_PROGRAM_0071_0082.md`

## Source-of-truth 顺序

1. `README.md`
2. `docs/CURRENT_STATE.md`
3. `docs/NEXT_STEPS.md`
4. governance / decision / research / dataset / edge registries
5. Phase 6/7/8 machine contracts
6. immutable research contracts/results

详细、逐锚点的当前状态以 `docs/CURRENT_STATE.md` 为准；研究计划以 `research/governance/CRYPTO_MULTI_STRATEGY_RESEARCH_PROGRAM_0071_0082.md` 为准。