# BRRK-LEADERSHIP-INTRADAY-SUPPORT-0053 — Capture Source Amendment 1

**Date:** 2026-08-11  
**Research ID:** `BRRK-LEADERSHIP-INTRADAY-SUPPORT-0053`  
**Amendment:** `BRRK-LEADERSHIP-INTRADAY-SUPPORT-0053-CAPTURE-SOURCE-AMENDMENT-1`  
**Status:** PRE-EXPOSURE DATA-CONTRACT AMENDMENT / NO DATASET CAPTURED / NO SUPPORT RESULT

## 1. Trigger

The frozen first capture attempted the original public endpoint:

`https://api.binance.com/api/v3/klines`

GitHub Actions run `31511625959`, job `93846583481`, on a U.S. hosted runner failed on the first BTCUSDT request with HTTP 451.

The failure occurred before any market row was returned and before any of the following existed:

- `MARKET_4H_PAYLOAD.json`
- market payload SHA-256
- `MARKET_4H_EVIDENCE.json`
- `DATASET_DECLARATION.json`
- dataset exposure event
- Track A/B/C support count
- predictive label, model, calibration or metric

Therefore no 0053 scientific dataset was exposed and the one-successful-capture budget remains unused.

## 2. Amendment

Before first data exposure, change only the Binance REST base used for public market data:

```text
OLD  https://api.binance.com/api/v3/klines
NEW  https://data-api.binance.vision/api/v3/klines
```

Binance's official Spot REST documentation identifies `data-api.binance.vision` as the base endpoint for public market-data-only APIs. The kline path remains exactly `/api/v3/klines`.

Official references:

- `https://developers.binance.com/en/docs/products/spot/rest-api`
- `https://github.com/binance/binance-spot-api-docs/blob/master/rest-api.md`

## 3. Everything else remains frozen

Unchanged:

- venue: Binance Spot;
- assets: BTCUSDT / ETHUSDT / SOLUSDT;
- interval: 4h;
- UTC semantics;
- requested window: 2020-08-11 00:00 UTC through 2026-08-02 20:00 UTC;
- `/api/v3/klines` resource;
- limit 1000;
- deterministic `startTime` pagination;
- raw 12-field kline rows;
- canonical JSON serialization;
- payload SHA-256 rule;
- strict four-hour continuity checks;
- no synthetic fill;
- no alternate venue;
- no Track A/B/C measurement during capture;
- no predictive labels/models/metrics;
- Track A/B/C numerical support definitions;
- success/failure classification.

## 4. Governance interpretation

This is not a result-informed scientific modification. It repairs an execution-environment incompatibility before any 0053 data were observed. The source remains Binance's official Spot market-data API and the same `/api/v3/klines` resource.

After this amendment merges, the next capture may retry until the **first complete internally valid payload** is durably persisted. Once that payload and SHA-256 are exposed, the source/base/window cannot be changed under 0053.

## 5. Authority

This amendment creates no:

- support-feasibility result;
- model result;
- 0048 rescue;
- 0049 eligibility;
- portfolio authority;
- canonical BRRK change;
- Phase-6 change;
- production/signing/order-submission authority.
