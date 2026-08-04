# PIT-UNIVERSE-0003-DATA-ACCESS — 2026-08-04

Read-only engineering audit. No strategy or PnL changes.

The public no-auth Binance market-data API was tested against active, currently `BREAK`, and missing-from-current-exchangeInfo symbols, with the S3 monthly 1d archive checked in parallel.

## Result

API success:
- active: 2 / 2;
- `BREAK`: **6 / 6**;
- missing from exchangeInfo: **1 / 1**.

S3 archive success was also 100% for all tested symbols.

Inactive examples successfully returned historical daily klines from `data-api.binance.vision`: NKNUSDT, BTTUSDT, HNTUSDT, LRCUSDT, OMUSDT and NANOUSDT. NBTUSDT, which was not present in current exchangeInfo, also returned historical rows.

This means current symbol status does not prevent historical market-data retrieval. A survivorship-aware daily panel can therefore be built with paginated public REST calls, using S3 as an independent fallback/check rather than downloading every archive file by default.

One useful discrepancy was observed: NBTUSDT returned API history through 2023-09 while the monthly 1d S3 listing found files only through 2023-02. Therefore archive object presence should not be treated as a perfect exact delisting timestamp without cross-checking actual daily data. The final point-in-time eligibility loader should use observed daily rows and completed-history counts as the authoritative trading-availability proxy.

## Decision

Proceed to PIT-DISP-0015: build a daily survivorship-aware dispersion universe from all mechanically eligible historical USDT pairs using completed daily rows, at least 240 completed observations, and an externally motivated $25m daily quote-volume liquidity floor. Apply the already frozen DISP-0014 median-ratio/smoothing formula without changing its parameters. This validates the dispersion risk signal separately from the still-fixed V1 alpha universe.
