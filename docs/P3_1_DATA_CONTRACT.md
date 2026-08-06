# P3.1 Canonical Data Contract

Status: candidate implementation for roadmap P3.1 only.

Machine-readable authority: `config/data_contract.json`.
Implementation: `execution/plan-b-bot/beta_bot/data_contract.py`.

## 1. Separation of data roles

P3.1 deliberately separates **strategy signal data** from **router/execution market data**.

### Strategy signal price

The frozen BRRK directional research core used Binance spot UTC daily closes for:

```text
BTCUSDT
ETHUSDT
SOLUSDT
BNBUSDT
```

P3.1 preserves that economic-price source rather than silently replacing it with Hyperliquid perpetual candles merely because Hyperliquid is the execution venue.

Canonical request semantics:

```text
source      = Binance Spot klines
interval    = 1d
timeZone    = 0 (UTC, explicit)
candle key  = open_time_ms
decision    = 00:00:00 UTC
```

At decision timestamp `D 00:00 UTC`, only candles with:

```text
close_time_ms < D 00:00 UTC
```

are eligible. The latest required session therefore opens at `D-1 00:00 UTC` and closes at `D-1 23:59:59.999 UTC`.

Official Binance Spot API documentation states that klines are uniquely identified by open time and that the default kline timezone is UTC; the P3.1 request makes `timeZone=0` explicit rather than relying on a default.

Reference:

- https://github.com/binance/binance-spot-api-docs/blob/master/rest-api.md#klinecandlestick-data

### Router market inputs

Instrument-routing observations remain Hyperliquid execution-venue data. They do not replace the frozen BRRK strategy close series.

P3.1 normalizes:

- Hyperliquid `fundingHistory` into `bps_per_hour`;
- perp-versus-verified-spot basis into bps;
- observation timestamps needed to reproduce the router assumption set.

Hyperliquid Info API references:

- https://hyperliquid.gitbook.io/hyperliquid-docs/for-developers/api/info-endpoint
- https://hyperliquid.gitbook.io/hyperliquid-docs/for-developers/api/info-endpoint/perpetuals

## 2. Missing-data policy

Price gaps are not repaired economically.

```text
NO forward fill
NO previous-close substitution
NO cross-venue price substitution
NO incomplete-candle substitution
```

For a decision to publish a canonical four-asset daily dataset:

1. each canonical asset must contain the latest completed UTC session;
2. common history starts on the latest first-available canonical day among BTC/ETH/SOL/BNB;
3. from that common start through the latest required day, every UTC daily session must be present for every asset;
4. an internal or latest-session gap fails closed and no target input is published.

This is stricter than silently reproducing a `dropna()` result after a data outage and makes missing-data behavior observable.

## 3. Asset / token mapping changes

Economic asset identity remains:

```text
BTC
ETH
SOL
BNB
```

Strategy-source symbols are versioned in `source_mappings` in `config/data_contract.json`.

Mapping periods use:

```text
valid_from_utc <= session < valid_to_utc
```

with `null` representing an open boundary. A consumed session must resolve to exactly one mapping. Overlap, ambiguity or an uncovered consumed date fails closed. Historical mappings must be appended/versioned rather than silently rewriting old observations.

The current source mappings are the unchanged Binance spot symbols used by the frozen BRRK research core.

## 4. Funding contract

For router as-of time `T`, canonical funding uses the exact trailing 24 completed hourly Hyperliquid funding slots strictly before `T`.

```text
API unit       = decimal rate per hour
canonical unit = bps per hour
conversion     = api_rate * 10,000
aggregation    = arithmetic mean of exact 24 completed hourly slots
```

Input order does not matter. Duplicate slots, non-hour-aligned slots, malformed rates or any missing required hour fail closed as `cost input unavailable`; a future/boundary funding record is not used early.

This is a routing-cost input contract, not a funding forecast model.

## 5. Basis contract

Canonical basis is:

```text
(perp_mark_price / verified_spot_price - 1) * 10,000
```

where the spot reference is the verified spot instrument for the same economic asset. Both source observation timestamps are retained, neither may be after router `as_of`, and their observation skew is preserved for replay/audit.

P3.1 does not invent an arbitrary freshness threshold. P2.4 records the observed assumptions; later live orchestration may add an evidence-backed operational freshness gate without changing the basis unit or formula.

## 6. Research/live determinism

Research does not get a separate candle-cleaning implementation. `research/integration/p3_1_data_contract_adapter.py` calls the exact same `beta_bot.data_contract` canonicalizer used by the production package.

For the same raw observations and the same decision/as-of timestamps:

```text
research canonical JSON == live canonical JSON
research SHA-256 digest  == live SHA-256 digest
```

The controlled tests also feed the byte-identical close sequence into the already-existing frozen signal component and require identical output. P3.1 does **not** create the P3.2 target calculation API.

## 7. Deliberately not implemented in P3.1

- no new BRRK weighting formula;
- no target-calculation API;
- no rebalance band;
- no weekly cash-contribution logic;
- no leverage research;
- no cycle-exit research;
- no production trading authorization.

Production authorization remains controlled separately by `config/decision_registry.json` and remains empty unless explicitly changed by a later approved gate.
