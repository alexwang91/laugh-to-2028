# EXEC-AUDIT-0001-BOOK-DEPTH — 2026-08-04

Read-only Hyperliquid L2 diagnostic. No private account data, API wallet, order, or trading threshold was used.

The public `l2Book` endpoint was sampled for BTC, ETH, SOL, BNB and XRP. Marketable buy/sell VWAP was simulated for fixed USD notionals of $1k, $5k, $10k, $25k and $50k against the visible book returned by Hyperliquid (up to 20 levels per side).

## Snapshot findings

Selected $50k simulated slippage versus mid:

| Coin | Buy slippage | Sell slippage | Visible bid depth | Visible ask depth |
|---|---:|---:|---:|---:|
| BTC | 0.93 bps | 0.08 bps | ~$10.05m | ~$2.77m |
| ETH | 0.27 bps | 0.27 bps | ~$10.76m | ~$11.10m |
| SOL | 0.69 bps | 0.07 bps | ~$0.62m | ~$0.54m |
| BNB | 5.49 bps | 1.12 bps | ~$0.143m | ~$0.111m |
| XRP | 1.91 bps | 1.94 bps | ~$1.91m | ~$1.74m |

The snapshot demonstrates material cross-asset and directional asymmetry. A single fixed slippage assumption is therefore a poor execution-risk model even before considering stressed books.

## Decision

1. Do not set an execution veto threshold from one snapshot.
2. Preserve the diagnostic and begin collecting repeated snapshots so empirical Slippage-at-Risk / expected-tail-slippage statistics can be estimated prospectively.
3. The eventual executor should simulate its actual target delta notional against the current side of the L2 book before order submission.
4. A live execution adapter should also reconcile partial fills and re-check the book before any retry/slice.
5. Funding/carry remains a separate execution-cost state variable; liquidity risk must not be inferred from funding alone.

This diagnostic supports replacing the current conceptual fixed-slippage assumption with target-notional-specific real-time book simulation, but it does not yet authorize any automatic veto threshold.
