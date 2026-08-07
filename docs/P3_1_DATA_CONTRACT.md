# P3.1 Canonical Data Contract

Status: **P3.1 schema v2 parity correction MERGED; post-merge CI validation pending.** This document defines data semantics only; it does not authorize P3.2 target generation or production trading.

Machine-readable authority: `config/data_contract.json`.
Implementation: `execution/plan-b-bot/beta_bot/data_contract.py`.

PR #74 merged the schema-v2 feature-input correction to main as `277eb777b4b28d32bb24c201bba1155b08686c71`. Because GitHub Actions/webhook processing was in a major outage, neither the PR head nor the resulting main SHA received a recorded workflow run. Therefore the implementation is merged, but TESTED/CI VERIFIED must remain unclaimed until a post-merge validation PR passes Phase 0 and governance.

## 1. Separation of asset roles

P3.1 separates three different roles that must not be conflated.

### Target / tradable universe

The BRRK product long universe remains exactly:

```text
BTC
ETH
SOL
BNB
```

Only these four assets may appear in P3.2 target weights or in the Hyperliquid router. Schema v2 does **not** add XRP to the product universe.

### Strategy feature-only input

Recovery of the exact frozen BRRK-0011 implementation found that the frozen regime feature model also consumes:

```text
XRPUSDT
```

as a **feature-only** Binance spot daily series. `RegimeKellyConfig` includes XRP in the major/alt feature panels, and `features_no_dominance.py` uses that panel for breadth, relative-strength dispersion and BTC-correlation features. XRP never receives a BRRK target weight.

Therefore the canonical strategy-signal dataset is:

```text
BTCUSDT  target asset
ETHUSDT  target asset
SOLUSDT  target asset
BNBUSDT  target asset
XRPUSDT  feature-only asset
```

The original P3.1 v1 contract omitted XRP and incorrectly described the frozen model as requiring only the four target assets. Schema v2 fixes that input-parity defect without changing the frozen model.

### Router market inputs

Instrument-routing observations remain Hyperliquid execution-venue data for BTC/ETH/SOL/BNB only. XRP is rejected by funding/basis router canonicalizers and cannot become tradable through the feature-input path.

## 2. Strategy price semantics

All five strategy-signal price series use the frozen research source:

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

Strategy-source mappings are versioned in `source_mappings` in `config/data_contract.json`; the current mappings are BTCUSDT/ETHUSDT/SOLUSDT/BNBUSDT/XRPUSDT.

## 3. Missing-data policy

Price gaps are not repaired economically.

```text
NO forward fill
NO previous-close substitution
NO cross-venue price substitution
NO incomplete-candle substitution
```

For a decision to publish the canonical strategy-signal dataset:

1. BTC, ETH, SOL, BNB and feature-only XRP must each contain the latest completed UTC session;
2. common history starts on the latest first-available day across all five required series;
3. every UTC session from common start through the latest required day must exist for every required series;
4. any internal or latest-session gap fails closed and no target input is published.

## 4. Asset / token mapping changes

Target economic identity remains:

```text
BTC
ETH
SOL
BNB
```

XRP has only `strategy_feature_assets` identity under this contract. It is not a target asset, route candidate, leverage overlay instrument or production authorization.

Mapping periods use:

```text
valid_from_utc <= session < valid_to_utc
```

with `null` representing an open boundary. A consumed session must resolve to exactly one mapping. Overlap, ambiguity or an uncovered consumed date fails closed. Historical mappings must be appended/versioned rather than silently rewriting old observations.

## 5. Funding contract

For router as-of time `T`, canonical funding uses the exact trailing 24 completed hourly Hyperliquid funding slots strictly before `T` for target/tradable assets only.

```text
API unit       = decimal rate per hour
canonical unit = bps per hour
conversion     = api_rate * 10,000
aggregation    = arithmetic mean of exact 24 completed hourly slots
```

Input order does not matter. Duplicate slots, non-hour-aligned slots, malformed rates or any missing required hour fail closed. Feature-only XRP is explicitly router-ineligible.

## 6. Basis contract

Canonical basis for target/tradable assets is:

```text
(perp_mark_price / verified_spot_price - 1) * 10,000
```

Both source observation timestamps are retained, neither may be after router `as_of`, and their observation skew is preserved for replay/audit. Feature-only XRP is rejected by the basis canonicalizer.

## 7. Research/live determinism

Research does not get a separate candle-cleaning implementation. `research/integration/p3_1_data_contract_adapter.py` calls the exact same `beta_bot.data_contract` canonicalizer used by the live package.

For the same raw observations and decision timestamp:

```text
research canonical JSON == live canonical JSON
research SHA-256 digest  == live SHA-256 digest
```

Schema v2 serializes the role boundary explicitly:

```text
target_assets   = BTC, ETH, SOL, BNB
feature_assets  = XRP
closes_by_asset = BTC, ETH, SOL, BNB, XRP
```

## 8. Evidence status

```text
IMPLEMENTED:           YES
MERGED:                YES
TESTED:                NOT YET VERIFIED AFTER MERGE
CI VERIFIED:           NO
PRODUCTION AUTHORIZED: NO_CHANGE
```

A fresh post-merge validation PR must trigger the full Phase 0 pytest/research-integration workflow and normal PR handoff governance before P3.2 begins.

## 9. Deliberately not implemented here

- no new BRRK weighting formula;
- no target-calculation API;
- no rebalance band;
- no weekly cash-contribution logic;
- no leverage research;
- no cycle-exit research;
- no XRP target or routing support;
- no production trading authorization.

Production authorization remains controlled separately by `config/decision_registry.json` and remains empty unless explicitly changed by a later approved gate.
