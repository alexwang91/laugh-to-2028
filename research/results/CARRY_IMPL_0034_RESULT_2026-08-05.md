# CARRY-IMPL-0034 — Hyperliquid Portfolio Margin public feasibility

Date: 2026-08-05
Actions run: 30989699527
Artifact: `carry-impl-0034-results` (artifact id 8923562757)

## Decision

**PASS_BTC_PUBLIC_FEASIBILITY**

The public mainnet audit establishes that the already-verified Hyperliquid BTC UI exposure (`BTC/USDC` -> HyperCore `UBTC/USDC`) currently has a Portfolio Margin collateral path suitable for a separately preregistered account-level mechanism probe.

This result does **not** authorize production trading, leverage optimization, a BRRK+carry stack, or any change to CARRY-PNL-0031 / CARRY-STACK-0033.

## Frozen gate

BTC passes only if all are true:

1. BTC spot identity is already verified under the official UI remap;
2. the exact selected spot base-token index has numeric LTV > 0 in `allBorrowLendReserveStates`;
3. BTC perp exists;
4. both spot and perp books are live and non-empty.

All four conditions passed.

## Exact current collateral evidence

Observed at UTC: `2026-08-05T08:36:31.510309+00:00`

- selected spot: `UBTC/USDC`
- spot pair index: `142`
- spot API coin: `@142`
- UBTC token index: `197`
- UBTC token id: `0x8f254b963e8468305d409b33aa137c67`
- reserve LTV: **0.50**
- reserve oracle price: **64194.0**
- reserve supplied: **1398.4341005844 UBTC**
- reserve borrowed: **0.0 UBTC**
- reserve utilization: **0.0**

At the same snapshot, the only positive-LTV reserve tokens returned were HYPE and UBTC, both with LTV 0.5. UETH and USOL did not have a matching positive-LTV reserve on their exact selected token indices and therefore remain unpromoted.

## BTC spot / perp execution snapshot

Spot book (`@142`):

- best bid / ask: **64193 / 64194**
- midpoint: **64193.5**
- spread: **0.155779 bps**
- returned bid / ask notional: about **$442,346 / $433,026**

BTC perp book:

- best bid / ask: **64209 / 64210**
- midpoint: **64209.5**
- spread: **0.155740 bps**
- returned bid / ask notional: about **$8.13m / $6.01m**

Spot-perp midpoint basis: **2.492464 bps**.

Selected BTC spot VWAP diagnostics:

| Side | Notional | Fill fraction | Slippage vs midpoint |
|---|---:|---:|---:|
| Buy | $1k | 100% | 0.0779 bps |
| Buy | $10k | 100% | 0.4813 bps |
| Buy | $50k | 100% | 0.9063 bps |
| Buy | $100k | 100% | 1.1769 bps |
| Sell | $1k | 100% | 0.0779 bps |
| Sell | $10k | 100% | 0.0779 bps |
| Sell | $50k | 100% | 0.1644 bps |
| Sell | $100k | 100% | 0.2872 bps |

These are one-time public order-book diagnostics, not historical liquidity evidence.

## Official Portfolio Margin context

Hyperliquid documentation explicitly describes Portfolio Margin as unifying spot and perp balances and gives the carry trade as an intended use case: a spot balance can offset a short perp position while the spot balance serves as collateral.

Rollout status must be treated as time-sensitive. Hyperliquid's official June 2026 announcement states that Portfolio Margin has advanced to **beta**, with BTC and HYPE accepted as collateral and increased limits. Older pre-alpha documentation/announcements are retained only as rollout history and must not be used to describe current eligibility or caps.

The account-abstraction documentation also states that Portfolio Margin / Unified Account balances and holds should be read from the spot clearinghouse state; individual perp-DEX user states are not authoritative for unified balances. Perp position fields remain useful as position diagnostics, while the primary capital-efficiency measurement for 0035 is taken from Portfolio Margin fields in the spot clearinghouse state.

Relevant official docs:

- `https://hyperliquid.gitbook.io/hyperliquid-docs/trading/portfolio-margin`
- `https://hyperliquid.gitbook.io/hyperliquid-docs/trading/account-abstraction-modes`
- `https://hyperliquid.gitbook.io/hyperliquid-docs/for-developers/api/info-endpoint`
- official Hyperliquid announcements channel for current rollout/cap changes

## Next authorized gate

Create `CARRY-PM-0035` as an **account-behavior / capital-efficiency probe**.

For experimental isolation, the project independently caps the dedicated probe account/subaccount at **<$1,000** and the UBTC probe leg at **$500**. These are project safety limits, not claims about current Hyperliquid eligibility requirements.

0035 may measure:

- abstraction mode;
- spot clearinghouse state;
- borrow/lend user state;
- account diagnostics where exposed by the API;
- UBTC balance and collateral state;
- BTC short-perp position state;
- portfolio margin ratio / liquidation-health diagnostics;
- pre/post state around one preregistered matched spot + short-perp configuration.

It must not search leverage, optimize size, change BRRK or CARRY-0031, or promote a stack based on this public feasibility result alone.
