# PIT-UNIVERSE-0002-LIFECYCLE — 2026-08-04

Read-only lifecycle audit; no strategy or PnL calculation. Every ordinary historical Binance spot-USDT archive symbol was enumerated and its first/last monthly 1d file was recorded. Current `exchangeInfo` status was attached only as present-day metadata, not as a historical eligibility filter.

## Result

- ordinary historical USDT candidates: **661**;
- symbols with archived monthly 1d files: **660**;
- listing errors: 0;
- latest complete archive month observed: 2026-07;
- current status: **471 TRADING, 189 BREAK, 1 missing from exchangeInfo**;
- archive ends before 2026-07: **185 symbols**;
  - 184 are currently `BREAK`;
  - 1 is missing from exchangeInfo.

This establishes that simple membership in current exchangeInfo is not a valid survivorship filter: Binance retains many delisted/inactive symbol records.

Historical archive coverage expanded from 143 ordinary USDT pairs in 2020-08, to 222 in 2021-05, ~320 in early 2023, ~361 in early 2024, ~388 in early 2025, and 475 with files in 2026-07. The candidate universe therefore changes substantially through time.

Examples of ended symbols include BTTUSDT, NANOUSDT, HNTUSDT, LRCUSDT, NKNUSDT, OMUSDT, DENTUSDT, TRUUSDT, TONUSDT and many others. They remain part of historical candidate construction until their actual archive availability ends; they cannot be removed because they later became inactive.

## Decision

Proceed to a historical-data access audit. First test whether Binance's no-auth market-data API still serves daily klines for `BREAK` symbols; if so it can materially reduce data-download complexity. If not, use S3 monthly 1d archives as the authoritative fallback. A subsequent construction audit will require 240 completed daily observations and trailing point-in-time quote-volume liquidity, without any present-day survival filter.
