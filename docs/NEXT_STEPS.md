# Next Steps

当前原则：**BRRK directional core 冻结；失败的历史 alpha/sleeve 不继续同窗救援；instrument identity、capital structure、execution 和 production authorization 分开验证。**

## Frozen completed decisions

### BRRK-0011

Canonical directional target. Price-only CAGR **65.10%**, MDD **-33.72%**, Sharpe **1.353**, Calmar **1.931**.

Do not retune BRRK on the current historical window.

### Dynamic PIT alpha

PIT-ALPHA-0016/0018 validated ranking/persistence information but produced unacceptable deep drawdowns and negative 2025+ economics.

Decision: **portfolio line stopped**. No exit-rank/min-hold/rebalance/liquidity/named-winner rescue.

### ASYM-BETA-0024

Daily latency cap is the best tested bull-extra implementation, but funding-aware MDD/Sharpe remain worse than strict BRRK and April 2024 remains unresolved.

Decision: parameters frozen; forward shadow only. No more historical April rescue.

### TSMOM-ALPHA-0029

Funding-aware first valid PIT long/short test: CAGR **-4.12%**, MDD **-88.30%**, Sharpe **0.251**. Corr vs BRRK was low but crisis-alpha gate failed.

Decision: **rejected; TSMOM line stopped on this sample**.

### Funding / router

- FUNDING-PNL-0003: all-perp Hyperliquid implementation cuts common-window CAGR to **44.08%**.
- ROUTER-DATA-0004: BTC spot is verified through official UI BTC->UBTC remap.
- ROUTER-PNL-0005: BTC-only spot accounting recovers common-window CAGR to **56.20%**.

Decision: all-perp default rejected; BTC spot-first remains implementation/shadow candidate.

### CARRY-PNL-0031 + CARRY-RF-0036R1

The original CARRY-PNL-0031 report is preserved unchanged. It passed a zero-return `net_economics` hurdle with:

- CAGR **2.740%**;
- MDD **-7.005%**;
- zero-hurdle Sharpe **1.428**;
- daily corr vs BRRK **-0.098**;
- mean return on BRRK worst-decile days positive.

F1 preregistered a benchmark-only restatement. No asset, weight, cost, funding-accounting or window change was allowed. The first valid `CARRY-RF-0036R1` result on 2020-09-15..2026-07-30 is:

- CARRY-PNL-0031 CAGR: **2.7404%**;
- FRED `DTB3` cash CAGR: **3.1653%**;
- excess CAGR over rf: **-0.4249 pp/yr**;
- excess Sharpe over rf: **-0.2216**;
- 2021 carry return: **+16.8037%**;
- full-window cumulative carry return: **+17.1983%**.

Corrected gate:

```text
net_economics = excess return over risk-free cash > 0
```

Decision: **FAIL_CORRECTED_NET_ECONOMICS_STOP_CARRY_LINE**.

Under discipline #7, the carry line is stopped. Do not drop BNB, filter funding sign, add basis thresholds, change the window, change costs, change weights or add leverage to rescue this sample.

Exact restatement plus daily evidence: `research/results/carry_rf_0036r1/`.

### CARRY-AUDIT-0032

Extreme SOL/XRP daily-close basis observations matched exact official Binance daily archives and did not artificially create 0031 economics.

Decision: source attribution passed. This does not override the F1 cash-hurdle failure.

### CARRY-STACK-0033

The frozen idle-capital rule had already failed:

```text
carry_scale_t = clip(1 - held_BRRK_gross_t, 0, 1)
```

- BRRK CAGR **56.66%** -> combined **56.04%**;
- Sharpe **1.235** -> **1.226**;
- Calmar **1.621** -> **1.597**;
- carry allocation turnover **20.87x**;
- scale-change cost about **1.043%**;
- net carry contribution **-1.236%**.

F1 further compared the combined stack with **BRRK + the same idle capital accruing DTB3 cash**. The corrected `net_economics_vs_idle_cash` also fails.

Decision: **remain rejected**. The previous interpretation that standalone carry still passed while only the idle-cash conversion failed is no longer supported after F1.

### CARRY-IMPL-0034

Public Hyperliquid Portfolio Margin audit passed BTC public feasibility:

- BTC UI -> HyperCore UBTC mapping verified;
- exact UBTC token index **197**;
- current UBTC reserve LTV **0.50**;
- live BTC spot and perp books.

Decision: `PASS_BTC_PUBLIC_FEASIBILITY` remains valid as an implementation observation, but it no longer authorizes live carry work because the upstream corrected economic gate failed.

Formal result: `research/results/CARRY_IMPL_0034_RESULT_2026-08-05.md`.

### CARRY-PM-0035 / CARRY-PM-0037

**CARRY-PM-0035 is no longer required. Do not spend live probe capital.**

F2 is retained as an implementation fix because the old 0035 comparator could confuse genuine margin release with a timing/price-drift-corrupted measurement. Since this changes a frozen gate, it was preregistered separately as `CARRY-PM-0037-MEASUREMENT-INTEGRITY`; `CARRY-PM-0035.json` remains untouched.

Frozen F2 integrity rules:

- spot -> matched snapshot gap <= **300 seconds**;
- UBTC spot midpoint drift <= **25 bps**;
- BTC perp midpoint drift <= **25 bps**;
- observed probe spot notional <= **$500 * 1.05 = $525**;
- bounded `/info` retries: **4 attempts**, backoff **0.5 / 1 / 2 seconds**, retrying transport failures plus HTTP 408/429/5xx only;
- research remains read-only: `/info` only, no signing, no orders, account address stored only as SHA-256 fingerprint.

Measurement state is now explicit:

```text
PM_RELEASES_MARGIN
PM_CONSUMES_MARGIN
MEASUREMENT_INCONCLUSIVE
```

`snapshot_gap_within_bound` and `mid_drift_within_bound` must pass before interpreting raw available-after-maintenance change. Failed timing/drift integrity is `MEASUREMENT_INCONCLUSIVE`, never a false zero-consumption pass.

Decision: **0037 implementation retained but live probe NOT REQUIRED because F1 stopped the carry line.**

Preregistration: `research/carry/CARRY-PM-0037.json`  
Runbook: `docs/CARRY_PM_0037_RUNBOOK.md`

---

# Current priority — non-carry forward implementation evidence

There is no authorized historical carry rescue, no live PM carry probe, and no PM-aware carry stack experiment.

Continue independent work already separated from carry:

1. BTC verified long spot capacity -> spot;
2. unverified/unavailable long exposure -> perp;
3. short exposure -> perp;
4. live L2 VWAP/slippage checks;
5. account/order/fill reconciliation;
6. partial/resting/rejected/cancelled handling;
7. slicing/TWAP;
8. idempotency and persistent audit logs;
9. reduce-only emergency paths / kill switch;
10. explicit mainnet confirmation and hard caps.

UETH/USOL identity/custody/redemption validation remains separate. No PNL may upgrade token identity.

This F1/F2 change set does **not** modify `execution/`.

---

# Forward evidence

Accumulate without retuning targets:

- BRRK target;
- routing instrument/reason;
- funding;
- spot/perp basis;
- mark/oracle premium;
- L2 depth and expected VWAP;
- actual fee/fill/slippage;
- post-trade reconciliation;
- operational failure events.

Portfolio Margin carry evidence is no longer a required forward track after the F1 failure.

---

# Leverage last

Do not reopen gross 1.30–1.50 until routing, execution reconciliation, slippage controls, kill paths and forward evidence are all established.
