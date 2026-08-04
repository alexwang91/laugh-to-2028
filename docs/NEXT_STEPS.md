# Next Steps

当前原则：**机制验证、组合验证和部署授权必须分开。已经失败的 alpha 组合不能通过同一窗口上的新阈值继续被救。**

## Completed — PIT-DISP-0015

Broad point-in-time dispersion contains real risk information, but its upside opportunity cost prevents promotion. Fixed-panel DISP-0014 is materially selection-sensitive.

Decision: `BRRK-0011` remains canonical baseline; no PIT-DISP-0015 tuning.

## Completed — PIT-ALPHA-0016

The dead-pool-inclusive Top-2 rank beat 98/100 random-priority placebos and was not dominated by one winner. The portfolio failed:

- CAGR 12.25%;
- MDD -69.12%;
- turnover 349.62;
- negative 2025+ economics;
- almost all growth disappears at 20 bps.

Decision: ranking mechanism validated; daily Top-2 portfolio rejected; no 0016 tuning.

## Completed — AUDIT-0017

The no-trading-change audit identified the dominant conversion defect:

- 83.41% of turnover came from switching one alt name for another;
- 653 holding spells across 113 symbols;
- median hold one day;
- only 19.35% remained daily Top-2 after 30 days;
- 52.07% remained broadly eligible;
- 30-day median forward return -2.43%, mean +4.83%.

The rank is right-skewed: many small losers and a few persistent winners. This authorized exactly one new structure—entry rank with eligibility exit.

## Completed — PIT-ALPHA-0018

The authorized state machine was executed without adding a threshold:

```text
Top-2 rank fills vacancies
        ↓
hold incumbent while own trend, relative trend,
history and liquidity eligibility remain valid
        ↓
exit on eligibility loss or BTC risk-off
```

### What improved

- CAGR 12.25% → **16.62%**;
- MDD -69.12% → **-66.86%**;
- turnover 349.62 → **141.86**;
- median hold 1 day → **3 days**;
- spells 653 → **188**;
- longest spell **260 days**;
- 20 bps CAGR remains **12.00%**;
- final NAV and Calmar still beat **98/100** same-state-machine placebos.

### What failed

- MDD remains unacceptable at **-66.86%**;
- 2025 return **-10.03%**;
- 2026 through Aug 2 **-11.06%**;
- 2025+ CAGR **-13.11%**;
- fixed V1 remains far stronger historically;
- contribution concentration rises as long winners are allowed to compound.

Decision:

1. ranking mechanism remains validated;
2. persistence mechanism is validated as a turnover/right-tail improvement;
3. broad dynamic-alpha portfolio remains rejected;
4. `BRRK-0011` remains canonical baseline;
5. no 0018 threshold or portfolio parameter may be tuned on this window;
6. no live or shadow allocation change is authorized.

Formal result: `research/results/PIT_ALPHA_0018_RESULT_2026-08-04.md`.

---

## Research stopping rule for dynamic alpha

The current alpha line stops here.

Do **not** add any of the following to rescue 0018 on the same historical window:

- exit-rank threshold;
- minimum holding period;
- weekly/monthly rebalance schedule;
- higher listing-age threshold;
- higher liquidity threshold;
- named ETH/SOL/BNB/HYPE universe;
- dispersion, funding, LPM, covariance or generic volatility gate;
- leverage;
- PNL-selected parameter family.

A future alpha experiment requires new evidence outside this selection loop—for example a genuinely new forward sample or a separately justified external mechanism. Another historical threshold search is not authorized.

---

## P0 — Historical funding + Spot/Perp Router

This is now the primary research task.

### Goal

Improve implementation economics without changing the frozen target exposure.

### Required components

1. Obtain accessible historical funding archives for BTC, ETH, SOL, BNB and XRP, with exact timestamps and signs.
2. Align funding to the held instrument and actual holding interval.
3. Separate:
   - price PNL;
   - funding PNL;
   - spot/perp basis;
   - exchange fees;
   - market impact/slippage.
4. Implement a deterministic router:
   - use spot for gross<=1 long exposure when positive perp funding is expensive and spot is available;
   - use perp for leverage overlay, shorts, operational necessity or advantageous negative funding;
   - never change the directional target because of historical funding optimization in the first test.
5. Report BTC/ETH/SOL/BNB/XRP attribution and the exact difference versus price-only BRRK-0011.
6. Stress costs and funding-source disagreement.

### Prohibited

- no funding threshold selected from PNL;
- no changing coin weights because one funding series looks attractive;
- no assumption that Binance funding equals Hyperliquid funding without labeling it as proxy evidence;
- no leverage increase.

Promotion requires a reproducible improvement after all fees, basis and slippage, not merely a lower quoted APR.

---

## P1 — Hyperliquid execution hardening

Priorities:

1. derive size precision from live metadata;
2. read account/position state before and after every trade;
3. reconcile reversal close and reopen fills;
4. handle partial, resting, rejected and cancelled orders;
5. slice large deltas or use controlled TWAP;
6. persist idempotency keys, decisions, orders and fills;
7. simulate target-notional L2 VWAP and slippage before submission;
8. route by side, notional, funding and spot/perp availability;
9. add reduce-only emergency protection;
10. secure status/cron endpoints;
11. require explicit mainnet confirmation and hard leverage caps;
12. prove deterministic parity between research target JSON and executor orders.

No production promotion until testnet reconciliation and failure-path tests pass.

---

## P2 — Forward shadow evidence

Continue accumulating, without changing trading targets:

- daily BRRK-0011 signal;
- PCA3/4/5 specification disagreement;
- label-free bad-state probability;
- cycle diagnostic;
- Hyperliquid hourly funding;
- mark/oracle premium;
- L2 book depth;
- expected VWAP/slippage by side and notional;
- realized execution outcome.

Only forward evidence can authorize basis/funding/liquidity variables as active controls.

---

## P3 — Risk allocation and leverage last

Do not use covariance, LPM, generic volatility scaling or leverage to rescue a rejected alpha portfolio.

Reconsider gross 1.30–1.50 only after:

- funding-aware net PNL is validated;
- spot/perp routing is deterministic;
- execution reconciliation is reliable;
- L2 slippage controls are implemented;
- BRRK-0011 shadow signals have accumulated forward evidence;
- operational kill switches are tested.

## Canonical position

Until those gates are passed:

- `BRRK-0011` remains the research baseline;
- PIT dispersion remains diagnostic;
- dynamic alpha ranks remain research evidence, not target weights;
- Plan B remains testnet/shadow;
- no increase in leverage is authorized.
