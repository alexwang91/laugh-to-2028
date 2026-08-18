# BRRK 当前状态（中文镜像）

更新日期：2026-08-18

权威仓库：`alexwang91/laugh-to-2028`

> 本文件是给人阅读的中文状态镜像。精确治理锚点、immutable identities、workflow evidence 与机器检查仍以 `docs/CURRENT_STATE.md`、registry 和对应 immutable artifacts 为准。本文件不改变任何 lifecycle、attempt 或 authority 状态。

## 一、生产与权限总状态

```text
Canonical BRRK-0011                  NO CHANGE
Phase 6                              NO CHANGE
Phase 7                              MONITOR_ONLY / LAUNCH BLOCKED
Phase 8                              TRIGGER ABSENT / NOT RUN
production gross cap                 1.0
production_authorized_components     []
production_authorized                false
signature_authorized                 false
order_submission_authorized          false
```

研究 PASS/FAIL 都不会自动产生生产权限。

## 二、当前研究主线总览

| ID | 状态 | 正式完成度 | attempt | 说明 |
|---|---|---:|---:|---|
| 0069 | CLOSED | 10/10 | 1/1 consumed | `PASS_EVENT_EARLY_WARNING_ONLY` |
| 0070 | CLOSED | 10/10 | 1/1 consumed | `PASS_LOCKED_EPISODE_ROBUSTNESS_REPLICATION` |
| 0071 | PERMANENTLY BLOCKED | 6/10 | 0/1 | pre-attempt controlled-content contamination |
| 0083 | CLOSED | 10/10 | 1/1 consumed | `FAIL_NO_ROBUST_LOCKED_P02_ECONOMIC_CONTROLLER_VALUE` |
| 0072 | ACTIVE | 2/10 | 0/1 | Stage 3 PREREGISTRATION in progress |

## 三、0069

Research ID：`BRRK-BTC-SOL-PATH-EVENT-EARLY-WARNING-EXECUTION-ASSURED-0069`

终局：`PASS_EVENT_EARLY_WARNING_ONLY / CLOSED TO SAME-ID RERUN`

预测层找到 SOL `T4_LONG_SIDEWAYS` 的提前预警，主要赢家为 P02、P03、P08。controller/economic 层没有可用赢家。attempt 1/1 已消费，同 ID 禁止 rerun、retune、rescue 和 recomputation。

## 四、0070

Research ID：`BRRK-SOL-LONG-SIDEWAYS-EARLY-WARNING-EPISODE-ROBUSTNESS-0070`

终局：`PASS_LOCKED_EPISODE_ROBUSTNESS_REPLICATION / CLOSED TO SAME-ID RERUN`

锁定 0069 的 `P02_RAW_ELASTIC_NET_LOGIT | SOL | T4_LONG_SIDEWAYS | lead=10`，不重新选模、不重新训练、不调整 lead，对七个最终 onset 做 episode robustness replication 并通过冻结门槛。

该结论仍属于 researcher-exposed development history，不是独立 OOS，也不产生生产授权。

## 五、0071

Research ID：`BRRK-SOL-LONG-SIDEWAYS-CONTROLLER-INTEGRATION-0071`

已完成：OWNER-FIRST、DESIGN、PREREGISTRATION、IMPLEMENTATION、NONHISTORICAL QUALIFICATION、CONTROLLED BOUNDARY，共 6/10。

在 Stage 7 ZERO-RESULT PREFLIGHT 中，在 durable `RUN_ATTEMPT.marker` 之前打开了受控 0069 `PRIMARY_RESULT.json` 内容，因此不能宣称 preflight PASS。

终局状态：

`BLOCKED_PRE_ATTEMPT_CONTROLLED_CONTENT_CONTAMINATION`

attempt 仍为 0/1。没有 0071 runtime/result artifacts。禁止补 marker、禁止继续 Stage 8、禁止伪造 RESULT/CLOSEOUT。事故永久记录于 Issue #295。

治理 resolution PR #296 允许新的 full-lifecycle replacement 0083，但不允许转移 0071 的任何正式阶段。

## 六、0083

Research ID：`BRRK-SOL-LONG-SIDEWAYS-CONTROLLER-INTEGRATION-REPLACEMENT-0083`

0083 从 0/10 独立完成十阶段。Stage 7 identity-only preflight PASS，Stage 8 唯一 attempt 在 durable marker 后执行。

终局：`FAIL_NO_ROBUST_LOCKED_P02_ECONOMIC_CONTROLLER_VALUE / CLOSED TO SAME-ID RERUN`

关键结果：

- `execution_valid=true`
- common support = 685
- selectable controllers = 6
- passing controllers = 0/6
- representative candidate = null
- attempt = 1/1 consumed

这个 FAIL 说明：0070 的预测/episode robustness 不能自动推导为 robust economic controller value。

## 七、0071–0082 governed roadmap

正式文件：`research/governance/CRYPTO_MULTI_STRATEGY_RESEARCH_PROGRAM_0071_0082.md`

merge anchor：`169d9adf6531dc099a43541df413fef079322adf`

roadmap 要求每个 eligible ID 独立走同一十阶段 lifecycle，并冻结 point-in-time、anti-lookahead、成本、trial counting、DSR/PBO/bootstrap、concentration/capacity/stress、stop/gating 与 zero production authority。

0071 治理事故后，resolution #296 将 0072 的硬前置改为 0083 immutable closeout，而不要求 0083 PASS。因此 0083 的科学 FAIL 不阻止 0072。

## 八、当前主线 0072 Carry Atlas

Research ID：`BRRK-CRYPTO-CARRY-ATLAS-0072`

目标：建立 BTC / ETH / SOL 的 point-in-time funding、basis、carry 与 crowding 结构图谱。0072 本身不声称交易盈利，不做 strategy PnL / Sharpe / hedge-ratio optimization。

### 已完成 lifecycle

- Stage 1 OWNER-FIRST merge：`e1d61eadb8a4564cae2689a718e2eaaa859aa05e`
- Stage 2 DESIGN merge：`90a7b68718c5cb59002fe4b451d39d8979602161`

formal completion = **2/10**。

### Stage 3 已合并的前置治理边界

- source-identity precondition merge：`318adfe656ba1dfe4028ac3df388a96796e5ce60`
- first metadata-only capture boundary merge：`d8c9f3a262dadf1721103499f00fe9dcff4561ca`

这些前置工作不计 lifecycle credit，因此 0072 仍是 2/10。

### first capture 冻结合同

request：`BRRK-CRYPTO-CARRY-ATLAS-0072-CAPTURE-0001`

cutoff：`2026-08-18T19:45:00Z`

universe：BTC / ETH / SOL

source roster：仅冻结的 Binance / Bybit 官方公共接口。

执行约束：

- automatic retry = 0
- partial durable artifact 后 fail closed
- raw bytes 必须先持久化
- 对研究者只允许暴露 hash、row/time coverage、schema/missingness、support metadata
- 禁止输出 funding/basis/OI values
- 禁止相关性、回归、p-value、signal、position、PnL、performance、scientific classification
- 不创建 Stage 8 `RUN_ATTEMPT.marker`
- 不消费 Stage 8 attempt

Liquidation intensity 与 external attention 仍未资格化，不允许用第 11 个 family 替换。dated-futures / term-structure 只有 metadata-only support 能证明合法 PIT coverage 后才可进入完整 preregistration。

### 当前状态

```text
0072 active stage                    Stage 3 PREREGISTRATION
formal completion                    2/10
controlled attempt                   0/1
controlled scientific/history reads  0
production_authorized                false
signature_authorized                 false
order_submission_authorized          false
```

## 九、当前精确下一步

1. 在独立 wiring 分支机械实现已经合并并冻结的 capture request。
2. exact-head standing CI 全绿后合并 wiring。
3. 之后执行一次 create-only、0-retry、fail-closed metadata capture。
4. 获取真实 immutable raw identities 和 support metadata。
5. 用这些真实 identities 冻结完整 numerical/scientific PREREGISTRATION。
6. 只有 Stage 3 正式合并后，0072 才变为 3/10，并进入 Stage 4 IMPLEMENTATION。

## 十、不可越过的边界

- 不允许 result-informed gate relaxation。
- 不允许 consumed attempt rerun/retune/rescue。
- 不允许 stale/failed exact head merge。
- 不允许把 0071 的阶段转移给 0083。
- 不允许把 Stage 3 metadata capture 当成 Stage 8 attempt。
- 不允许研究结果自动改变 production/signature/order authority。

## 十一、相关文件

- 精确状态：`docs/CURRENT_STATE.md`
- 中文状态：`docs/CURRENT_STATE_CN.md`
- 中文研究历史：`docs/RESEARCH_HISTORY_0069_0083_CN.md`
- 正式 roadmap：`research/governance/CRYPTO_MULTI_STRATEGY_RESEARCH_PROGRAM_0071_0082.md`
- 0071 incident：Issue #295
