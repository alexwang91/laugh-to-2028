# P3.1 Canonical Data Contract

Status: **PASS / MERGED — canonical P3.1 data contract.** This document defines data semantics only; it does not authorize P3.2 target generation or production trading.

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
source = Binance public spot klines
interval = 1d
timeZone = 0
```

The machine-readable mapping is in `config/data_contract.json`. Source mappings are versioned by UTC effective range. For every requested asset/session exactly one source mapping must resolve; gaps, overlaps and ambiguous mappings fail closed.

### Router / execution market data

Hyperliquid remains canonical for instrument identity, funding, basis/perp observations and execution evidence. These observations do not substitute for the strategy signal close series.

---

## 2. Canonical decision boundary

The product boundary is:

```text
00:00:00 UTC
```

For a daily Binance kline to be usable at decision timestamp `D`, its close timestamp must satisfy:

```text
close_time_ms < D_ms
```

A candle closing exactly at or after the decision boundary is not completed information for that decision.

The canonical decision timestamp is distinct from scheduler wall-clock invocation time. The service may execute shortly after the boundary while still labeling the economic decision with the exact 00:00 UTC boundary.

---

## 3. Canonical daily-row contract

Every canonical row contains:

```text
asset
source_id
source_symbol
session_start_ms
session_end_ms
close
```

Required properties:

- canonical asset belongs to BTC / ETH / SOL / BNB;
- close is finite and positive;
- session is exactly one UTC calendar day;
- `session_end_ms = session_start_ms + 86,400,000 - 1`;
- the row is completed before the decision boundary;
- each asset has the same ordered session set;
- no duplicate session per asset;
- sessions are contiguous;
- no forward-fill, previous-close fill or cross-venue price substitution.

If the four-asset common history is not complete and contiguous, target generation must fail closed rather than modify the historical path.

---

## 4. Source mapping versioning

`config/data_contract.json` maps canonical economic assets to source symbols by effective UTC interval.

P3.1 intentionally does not assume that one symbol name remains valid forever. A future source migration must add a new versioned mapping rather than overwrite history.

Resolution rule:

```text
requested session start
-> exactly one mapping whose effective range covers that session
-> use that source_id + source_symbol
```

Zero matches or more than one match is a data-contract failure.

---

## 5. Research/live identity

Research and live code must call the same canonicalizer:

```text
execution/plan-b-bot/beta_bot/data_contract.py
```

Research adapter:

```text
research/integration/p3_1_data_contract_adapter.py
```

The adapter contains no independent candle-cleaning implementation. Given identical raw source batches and decision timestamp, research and live must emit byte-identical canonical JSON and SHA-256 digest.

This protects against a common failure mode where research and production appear to use the same market but differ in boundary handling, incomplete-candle inclusion, fill policy or symbol migration.

---

## 6. Router funding contract

Funding is a router/execution input, not strategy-price data.

Canonical source:

```text
Hyperliquid fundingHistory
```

Canonical unit:

```text
bps_per_hour
```

Hyperliquid's decimal funding rate converts as:

```text
bps_per_hour = funding_rate_decimal * 10,000
```

At decision timestamp `D`, P3.1 requires the exact 24 completed hourly slots immediately preceding `D`.

Requirements:

- each expected slot appears exactly once;
- timestamp belongs to the required completed-hour set;
- no missing slot;
- no duplicate slot;
- no boundary/future slot consumed early;
- values are finite.

Missing required funding history fails closed for a route comparison that requires the 24-hour funding observation.

---

## 7. Basis / premium observation contract

P3.1 defines verified spot/perp basis as:

```text
basis_bps = (perp_mark_price / verified_spot_price - 1) * 10,000
```

The observation retains:

```text
spot source
spot instrument
spot timestamp
spot price
perp source
perp instrument
perp timestamp
perp mark price
observation skew
basis bps
```

P3.1 does not hide asynchronous observations behind a single timestamp. Later router policy may define acceptable skew/freshness limits, but the data contract preserves the evidence needed to make that decision.

---

## 8. Missing-data policy

Canonical policy:

```text
FAIL_CLOSED_NO_TARGET
```

Forbidden fallbacks include:

- forward-fill;
- previous-close substitution;
- Hyperliquid perp candle substituted for missing Binance strategy close;
- another exchange substituted without an explicit versioned contract change;
- incomplete current-day candle;
- silently dropping one asset and continuing with a smaller product universe.

This is intentional. A skipped decision is preferable to silently changing the strategy input path.

---

## 9. P3.1 authorization boundary

P3.1 verifies only the data contract.

It does **not** authorize or implement:

- P3.2 full BRRK target calculation;
- P3.3 rebalance / turnover controls;
- P3.4 weekly contribution handling;
- P4 leverage above 1;
- P5 cycle-exit state intelligence;
- production trading.

Machine-readable decision:

```text
DATA-CONTRACT-P3.1 = IMPLEMENTATION_VERIFIED
```

Production authorization remains unchanged and empty.
