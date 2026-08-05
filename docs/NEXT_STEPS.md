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

### CARRY-PNL-0031

Frozen five-asset same-venue delta-neutral baseline passed its independent sleeve gate:

- CAGR **2.740%**;
- MDD **-7.005%**;
- Sharpe **1.428**;
- daily corr vs BRRK **-0.098**;
- mean return on BRRK worst-decile days positive.

Decision: **carry mechanism qualified**.

### CARRY-AUDIT-0032

Extreme SOL/XRP daily-close basis observations matched exact official Binance daily archives and did not artificially create 0031 economics.

Decision: source attribution passed.

### CARRY-STACK-0033

The frozen idle-capital rule failed:

```text
carry_scale_t = clip(1 - held_BRRK_gross_t, 0, 1)
```

- BRRK CAGR **56.66%** -> combined **56.04%**;
- Sharpe **1.235** -> **1.226**;
- Calmar **1.621** -> **1.597**;
- carry allocation turnover **20.87x**;
- scale-change cost about **1.043%**;
- net carry contribution **-1.236%**.

Decision: carry-as-daily-idle-cash-filler rejected. No historical scale/threshold/fixed-weight/leverage rescue.

### CARRY-IMPL-0034

Public Hyperliquid Portfolio Margin audit passed BTC feasibility:

- BTC UI -> HyperCore UBTC mapping already verified;
- exact UBTC token index **197**;
- current UBTC reserve LTV **0.50**;
- live BTC spot and perp books;
- current PM infrastructure therefore supports a separately tested BTC collateral path.

Decision: **PASS_BTC_PUBLIC_FEASIBILITY**. This result does not establish actual account-level capital release.

Formal result: `research/results/CARRY_IMPL_0034_RESULT_2026-08-05.md`.

---

# P0 — CARRY-PM-0035 account-behavior probe

This is the only current primary historical/implementation gate.

## Question

For a small dedicated Portfolio Margin account/subaccount, how much incremental maintenance capacity is actually consumed when a BTC short perp is added against an already-held UBTC spot balance?

## Frozen account limits

- dedicated new account/subaccount;
- total account value < **$1,000**;
- probe UBTC spot notional <= **$500** plus fixed 5% execution tolerance;
- BTC only;
- no other perp positions;
- research code is read-only;
- no private key or order signing in research code.

## Frozen four-stage sequence

```text
1. cash
2. UBTC spot only
3. same UBTC + matched BTC short perp
4. both probe legs closed
```

The BTC short must match the UBTC economic notional within **2%**.

## Required API evidence

Read and persist sanitized summaries from:

- `userAbstraction`;
- `spotClearinghouseState`;
- `borrowLendUserState`;
- `clearinghouseState`;
- UBTC spot L2 (`@142`);
- BTC perp L2 (`BTC`).

The primary PM fields are:

- `portfolioMarginEnabled`;
- `portfolioMarginRatio`;
- `tokenToPortfolioBorrowRatio`;
- `tokenToAvailableAfterMaintenance`;
- USDC / UBTC balances;
- BTC perp size/notional;
- borrow/lend health.

## Frozen capital measurement

```text
incremental_maintenance_consumption_usdc
  = max(0,
      available_after_maintenance_USDC(spot-only)
      - available_after_maintenance_USDC(matched))

incremental_maintenance_fraction
  = incremental_maintenance_consumption_usdc
    / matched_BTC_short_notional
```

## PASS gate

All required:

1. account abstraction = `portfolioMargin`;
2. Portfolio Margin enabled;
3. no other perp positions in any stage;
4. spot stage has UBTC and no BTC short;
5. spot notional is within fixed probe cap;
6. matched stage contains UBTC + BTC short;
7. spot/short economic notional mismatch <= **2%**;
8. matched `portfolioMarginRatio` < **0.50**;
9. USDC available-after-maintenance measurement exists;
10. incremental maintenance fraction <= **25%** of short notional;
11. closed stage returns BTC short to zero and probe UBTC to near zero.

The 25% gate is a coarse structural discriminator chosen before account evidence. It is not a leverage target and may not be tuned after the result.

Preregistration: `research/carry/CARRY-PM-0035.json`  
Runbook: `docs/CARRY_PM_0035_RUNBOOK.md`

## Failure rule

If the first valid four-stage probe fails or is inconclusive:

- preserve the result;
- diagnose only API/state/account-isolation defects;
- do not change the $500 cap, 2% match tolerance, 0.50 PM-ratio gate, or 25% maintenance gate based on outcome;
- do not reopen carry stacking.

---

# P1 — CARRY-STACK-0036-PM, only if 0035 passes

Preregister exactly one PM-aware accounting rule using the **observed 0035 capital factor**.

Preserve:

- BRRK-0011 target weights;
- CARRY-PNL-0031 mechanism;
- no fixed 80/20 or other post-result weight search;
- no leverage grid;
- no asset removal;
- no funding/basis threshold optimization.

Required stack gates:

- CAGR improves vs strict-router BRRK;
- Sharpe improves;
- MDD non-worse;
- Calmar improves;
- carry turnover materially below 0033's 20.87x pathology;
- modeled combined capital use respects the observed PM factor and a separately frozen safety buffer.

If the first valid 0036 fails, **stop historical carry stacking research**.

---

# P2 — strict forward router / execution hardening

Independently of 0035/0036, continue implementation work:

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

---

# P3 — forward evidence

Accumulate without retuning targets:

- BRRK target;
- routing instrument/reason;
- funding;
- spot/perp basis;
- mark/oracle premium;
- L2 depth and expected VWAP;
- actual fee/fill/slippage;
- post-trade reconciliation;
- Portfolio Margin ratio/capital fields when applicable;
- operational failure events.

---

# P4 — leverage last

Do not reopen gross 1.30–1.50 until routing, Portfolio Margin behavior, execution reconciliation, slippage controls, kill paths and forward evidence are all established.
