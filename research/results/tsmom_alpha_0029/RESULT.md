# TSMOM-ALPHA-0029 — first valid result

Decision: **rejected for portfolio stacking** under the preregistered gate. No same-window rescue tuning is authorized.

## Canonical funding-aware result

- Window: 2020-08-29 to 2026-07-30
- 5 bps transaction-cost assumption plus official Binance USD-M recorded funding events
- Final value from $10,000: **$7,797.02**
- CAGR: **-4.12%**
- Max drawdown: **-88.30%**
- Annualized volatility: **62.46%**
- Sharpe: **0.251**
- Calmar: **-0.047**

Price-only at 5 bps was positive (CAGR **7.41%**) but economically weak, with MDD **-85.61%** and Sharpe **0.434**. Funding changed the canonical economics from positive to negative.

## Diversification and crisis behavior

The sleeve was genuinely low-correlation versus BRRK: daily correlation **0.060** versus canonical BRRK and **0.041** versus the strict-router BRRK overlap. However, it did **not** provide crisis alpha. On BRRK's worst 10% daily returns, mean TSMOM return was **-0.589%**; on the worst 20 BRRK days it averaged **-1.843%**.

Therefore the preregistered qualification gate passed only the low-correlation criterion. Funding-aware economics and crisis-alpha criteria both failed.

## Data quality notes

- 828/828 historical ordinary USDT perpetual candidates loaded without top-level/month archive errors.
- 549 symbols were actually held; 19 later-ended contracts participated historically, preserving survivorship discipline.
- Monthly-kline audit detected 323 internal gaps; 318 were repaired only from official Binance daily 1d archives. Five ICPUSDT dates remained unresolved, but no held next-day return remained missing in the valid run.
- Funding accounting used 553,743 official recorded events. Event coverage was **155,927 / 156,229 active symbol-days = 99.8067%**. The 302 active symbol-days without a recorded settlement event were retained explicitly and assigned no manufactured cashflow; archive download failure remained a hard failure.

## Research decision

Do not change horizons, horizon weights, volatility window, Top-K selection, stop rules, liquidity thresholds, gross, or funding thresholds to rescue this sample. Preserve 0029 as negative evidence and move the independent diversifier search to a carry/funding sleeve.
