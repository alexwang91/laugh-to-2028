# ROUTER-DATA-0004 Result — Hyperliquid Spot/Perp Availability

Observed at `2026-08-04T19:56:13.283607+00:00` from the official Hyperliquid `/info` endpoint.

This result records the preregistered **no-PNL** implementation audit. It does not change BRRK targets and does not promote a router.

## Validation

- Workflow run: `30945504271`
- Artifact: `router-data-0004-results` (`8906907321`)
- Deterministic metadata/VWAP tests: passed
- Live metadata/book audit: passed
- Spot tokens: 482
- Spot pairs: 322
- Perp assets: 232

## Target classification

| Target | Spot result | Primary candidate | Decision |
|---|---|---|---|
| BTC | `verified_official_ui_remap` | UBTC/USDC (`@142`) | Verified for a later strict spot-router test under the preregistered official UI remap exception |
| ETH | `candidate_wrapped_or_bridged` | UETH/USDC (`@151`) | Candidate only; no automatic economic-equivalence approval |
| SOL | `candidate_wrapped_or_bridged` | USOL/USDC (`@156`) | Candidate only; no automatic economic-equivalence approval |
| BNB | `no_direct_spot_candidate` | none | Perp-only/unavailable for the first strict router |
| XRP | `no_direct_spot_candidate` | none | Perp-only/unavailable for the first strict router |

## Current book diagnostics

### BTC / UBTC spot

- spread: **0.156 bps**
- returned ask depth: **$523,422**
- returned bid depth: **$605,861**
- current perp-mid vs spot-mid basis: **3.113 bps**
- $100k buy: 100% fill, **0.969 bps** midpoint slippage
- $100k sell: 100% fill, **0.305 bps** midpoint slippage

### ETH / UETH candidate

- classification remains **candidate only**
- spread: **0.533 bps**
- returned ask/bid depth: **$422,718 / $491,353**
- $100k buy/sell are fully fillable in the returned book
- $100k midpoint slippage: **2.264 / 1.827 bps**

### SOL / USOL candidate

- classification remains **candidate only**
- spread: **1.484 bps**
- returned ask/bid depth: **$50,265 / $103,758**
- $50k buy is fully fillable; $100k buy fills only about **50.3%** within the returned 20 levels
- $100k sell is fully fillable; midpoint slippage **4.204 bps**

## Fee diagnostic

Public base-tier assumptions captured by the preregistration:

| Market | Taker | Maker |
|---|---:|---:|
| Spot | 7.0 bps | 4.0 bps |
| Perp | 4.5 bps | 1.5 bps |

These are current execution-cost diagnostics, not historical fee assumptions.

## Decision

1. **BTC is the only target verified for an immediate strict spot-first test.**
2. ETH and SOL remain unverified economic substitutes despite live UETH/USOL books.
3. BNB and XRP have no deterministic direct-USDC spot candidate in this snapshot.
4. One snapshot does not authorize historical liquidity/basis inference.
5. No strategy PNL or router promotion is made under `ROUTER-DATA-0004`.

The next accounting/shadow experiment must keep ETH/SOL/BNB/XRP perp-only unless a separate identity/availability audit upgrades them.
