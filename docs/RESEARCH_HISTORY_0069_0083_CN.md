# BRRK 研究历史记录：0069–0083

更新日期：2026-08-18

本文用于给人阅读，汇总 0069、0070、0071、0083 和当前 0072 的治理与科学演进。机器可验证的 immutable artifacts、registry、workflow evidence 与 `docs/CURRENT_STATE.md` 仍具有更细粒度的证据地位。本文不改变任何研究状态、attempt 状态或生产授权。

## 一、为什么从 0069 开始形成严格研究链

0069 以前的研究已经暴露出一个核心问题：科学假设、执行完整性、数据边界和生产权限必须分离。一个模型可能有预测信号，但执行不完整；一个实验可能执行有效，但经济价值为零；一个研究即使 PASS，也不能自动获得生产权限。

因此 0069/0070 之后的研究逐步固化为十阶段 lifecycle，并在 0071–0082 roadmap 中明确序列化。

## 二、0069：找到提前预警，但没有得到经济 controller

Research ID：`BRRK-BTC-SOL-PATH-EVENT-EARLY-WARNING-EXECUTION-ASSURED-0069`

终局：`PASS_EVENT_EARLY_WARNING_ONLY / CLOSED TO SAME-ID RERUN`

0069 对 BTC/SOL path events 做系统预测研究。预测层出现明确赢家，集中在 SOL 的 `T4_LONG_SIDEWAYS`，包括 P02、P03、P08。经济/controller 层没有形成可用赢家。

关键治理结论：预测信号成立不等于 controller 有经济价值。0069 attempt 1/1 已消费，禁止同 ID 结果导向修复。

## 三、0070：先验证锁定信号是不是 episode-robust

Research ID：`BRRK-SOL-LONG-SIDEWAYS-EARLY-WARNING-EPISODE-ROBUSTNESS-0070`

终局：`PASS_LOCKED_EPISODE_ROBUSTNESS_REPLICATION / CLOSED TO SAME-ID RERUN`

0070 不重新选模型，不重新训练，不重新搜索 warning lead。它锁定 0069 的 P02/SOL/T4_LONG_SIDEWAYS/10-session warning，并对七个最终 unique onset 做 episode-level replication。

结果通过冻结 robustness gate，因此可以说锁定信号在 researcher-exposed development history 中具有 episode robustness。不能把这个结论扩大成独立 OOS，更不能直接变成交易权限。

## 四、0071：科学尚未运行，治理先失败

Research ID：`BRRK-SOL-LONG-SIDEWAYS-CONTROLLER-INTEGRATION-0071`

0071 已合法完成前六阶段：OWNER-FIRST、DESIGN、PREREGISTRATION、IMPLEMENTATION、NONHISTORICAL QUALIFICATION、CONTROLLED BOUNDARY，formal completion = 6/10。

在 Stage 7 ZERO-RESULT PREFLIGHT 中，durable `RUN_ATTEMPT.marker` 创建之前，GitHub connector 打开了受控 0069 `PRIMARY_RESULT.json` 内容。roadmap 明确规定 Stage 7 可以检查 Git identity，但不能读取 controlled scientific/history payload；Stage 8 又要求 durable marker 必须先于第一次 permitted controlled content read。

因此 0071 不能宣称 preflight PASS，也不能事后补 marker。治理事故永久记录在 Issue #295。

最终状态：`BLOCKED_PRE_ATTEMPT_CONTROLLED_CONTENT_CONTAMINATION`。

attempt = 0/1。没有 runtime/result artifacts。不能继续、不能 rescue、不能伪造 RESULT/CLOSEOUT。

## 五、治理 resolution：不修 0071，另开完整 replacement 0083

PR #296 的治理 resolution 没有给 0071 创造恢复规则，而是永久保持 0071 6/10 blocked，并授权新的完整 replacement：`BRRK-SOL-LONG-SIDEWAYS-CONTROLLER-INTEGRATION-REPLACEMENT-0083`。

关键原则：0083 不继承 0071 的任何正式阶段，必须从 OWNER-FIRST 重新走完整十阶段。

同时，0072 的 post-resolution prerequisite 被改为 0083 immutable closeout，而不是要求 0083 科学 PASS。

## 六、0083：执行完全合法，但科学结果 FAIL

0083 从 0/10 走完 10/10。

Stage 7 identity-only ZERO-RESULT PREFLIGHT PASS。Stage 8 严格按以下顺序执行：preflight → durable `RUN_ATTEMPT.marker` → remote durability verification → 唯一 controlled execution → immutable result bundle → marker-only finalization。

attempt 1/1 永久消费。

终局：`FAIL_NO_ROBUST_LOCKED_P02_ECONOMIC_CONTROLLER_VALUE`。

`execution_valid=true`，common support = 685。6 个 selectable controller 全部未通过冻结经济/robustness gates，0/6 PASS，representative candidate = null。

这次 FAIL 区分了两件事：0070 的锁定 P02 warning 可以具有预测/episode robustness，但在 0083 的冻结 controller contract 下，它没有证明 robust economic controller value。

治理上不能因为 FAIL 再调 controller、改成本、改 gate 或重跑 0083。immutable closeout 已永久封存结果。

## 七、0072：转向独立 Carry Atlas

Research ID：`BRRK-CRYPTO-CARRY-ATLAS-0072`

0072 不再试图救援 0083。它是 roadmap 中独立的 carry-structure 研究，目标是对 BTC/ETH/SOL 建立 point-in-time funding / basis / carry / crowding atlas。

当前已完成：OWNER-FIRST = 1/10，DESIGN = 2/10。

Stage 3 PREREGISTRATION 正在进行。因为完整 preregistration 必须绑定真实、不可变的数据 identity，而这些 raw identities 在第一次合法 capture 前并不存在，所以 Stage 3 被拆成不计 lifecycle credit 的治理 preconditions：source-identity contract、one-shot first-capture gate、frozen capture request、metadata-only capture wiring、一次 capture 后取得 immutable raw identities/support metadata、最后冻结完整 numerical/scientific preregistration。

截至 2026-08-18：

- source-identity precondition merge：`318adfe656ba1dfe4028ac3df388a96796e5ce60`
- first-capture boundary merge：`d8c9f3a262dadf1721103499f00fe9dcff4561ca`

0072 仍为 2/10，attempt 0/1，controlled scientific/history reads 0。

## 八、0072 first capture 的特殊边界

这次 first capture 不是 Stage 8 controlled scientific experiment。它只为 Stage 3 建立可验证的数据 identity。

冻结规则包括：request `BRRK-CRYPTO-CARRY-ATLAS-0072-CAPTURE-0001`；cutoff `2026-08-18T19:45:00Z`；BTC/ETH/SOL；仅冻结的 Binance / Bybit 官方公共 source roster；automatic retry = 0；partial durable artifact 后 fail closed；raw bytes 先持久化；研究者可见输出仅限 hash、row/time coverage、schema/missingness、support metadata；禁止暴露 funding/basis/OI values；禁止相关性、回归、p-value、signal、position、PnL、performance 和 scientific classification；不创建 Stage 8 marker；不消费 Stage 8 attempt。

## 九、生产权限始终独立

0069 PASS、0070 PASS、0083 FAIL、0072 的任何后续结果都不会自动改变生产系统。

```text
production_authorized_components = []
production_authorized = false
signature_authorized = false
order_submission_authorized = false
```

Phase 6、Phase 7、Phase 8 的 authority plane 继续按各自治理合同运行，不因研究结果自动升级。

## 十、当前精确下一步

在独立 wiring 分支机械实现已冻结 capture request。wiring 必须先经过 exact-head CI 并合并。之后才能执行一次 metadata-only capture。取得真实 raw identities 后，再完成 0072 Stage 3 完整 preregistration。

在 Stage 3 正式合并以前，0072 始终保持 2/10。