# PIT-UNIVERSE-0001-DISCOVERY — 2026-08-04

Read-only data-discovery audit. No trading or PnL calculation.

Binance's public unsigned S3 archive was enumerated directly at `data/spot/monthly/klines/`, and compared with the public no-auth `data-api.binance.vision/api/v3/exchangeInfo` response.

## Result

- archive symbol prefixes across all quote currencies: **3,695**;
- historical archive USDT symbols: **723**;
- current exchangeInfo rows with USDT quote: **722**;
- common archive/exchangeInfo USDT rows: **722**;
- archive-only USDT rows: **1** (`NBTUSDT`);
- current-only rows: 0.

Archive USDT symbol classification used only obvious mechanical exclusions:
- ordinary USDT candidates: 661;
- leveraged-token-like suffixes (`UP/DOWN/BULL/BEAR`): 50;
- stable/fiat-like bases: 12.

The small archive-only count does **not** imply that only one historical pair delisted, because Binance exchangeInfo retains many non-TRADING/inactive symbol records. Therefore future survivorship reconstruction must use dated archive availability / symbol status, not simple presence in current exchangeInfo.

## Dated-file verification

The S3 bucket exposes monthly 1d files by symbol and date. Examples:
- `NBTUSDT`: 12 monthly 1d files, 2022-03 through 2023-02;
- `BTCUSDT`: 108 files, 2017-08 through 2026-07;
- `ETHUSDT`: 108 files, 2017-08 through 2026-07;
- `SOLUSDT`: 72 files, 2020-08 through 2026-07;
- `BNBUSDT`: 105 files, 2017-11 through 2026-07.

All three preregistered discovery success criteria passed: archive prefix enumeration, historical inactive candidate detection, and dated 1d-file discovery.

## Decision

Proceed to a separate lifecycle audit that enumerates first/last archived month for every ordinary USDT candidate and records current trading status. This will create a point-in-time listing/delisting catalog before any dynamic-universe PnL test. Historical eligibility must later use only information available at each date (age and trailing quote volume); present-day survival or market capitalization cannot be used to delete historical losers.
