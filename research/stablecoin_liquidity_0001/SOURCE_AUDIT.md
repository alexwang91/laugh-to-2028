# STABLECOIN-LIQUIDITY-0001 Source Audit

Status: **pre-result source/data audit**  
Research ID: `STABLECOIN-LIQUIDITY-0001`  
Production authority: **none**

## Frozen source identity

Primary source for Stage 1 is DefiLlama's public stablecoins API as exposed by the official `DefiLlama/api-sdk` repository.

Frozen SDK reference:

- repository: `DefiLlama/api-sdk`
- commit: `f0d43119c746dda0c1ad8460c37ac9e00e8e5161`
- repository package version at that commit: `0.1.4`
- SDK method: `stablecoins.getAllCharts()`
- module path: `src/modules/stablecoins.ts`
- client path: `src/client.ts`
- type path: `src/types/stablecoins.ts`

The official SDK maps the stablecoins base URL to:

```text
https://stablecoins.llama.fi
```

and `getAllCharts()` to:

```text
GET /stablecoincharts/all
```

Therefore the frozen direct source endpoint is:

```text
https://stablecoins.llama.fi/stablecoincharts/all
```

No API key is required by the official SDK for this endpoint.

## Frozen source fields

The official SDK type `StablecoinChartDataPoint` documents:

```text
date                  Unix timestamp encoded as string
totalCirculating      aggregate circulating supply by peg type
totalCirculatingUSD   aggregate circulating supply in USD by peg type
```

`PeggedAsset` exposes `peggedUSD` as the USD-pegged component. Stage 1 binds only:

```text
metric timestamp = date
primary raw value = totalCirculatingUSD.peggedUSD
```

Other fields remain preserved in the raw payload but are not Stage-1 feature alternatives.

## PIT limitation

The reviewed official SDK/API type exposes the observation timestamp (`date`) but does not expose a historical `published_at`, `available_at`, historical vintage identifier, or original first-seen timestamp for each historical observation.

Therefore current historical API history is **not** treated as pristine point-in-time data. It is classified conservatively as:

```text
RECONSTRUCTED_HISTORY / RESEARCHER_EXPOSED_HISTORY
```

For `STABLECOIN-LIQUIDITY-0001`, when a historical row has no independently verifiable publication timestamp:

```text
available_at = metric_timestamp + 2 calendar days
```

This `LAG_2D` rule was preregistered before source binding. `LAG_1D` and `LAG_3D` cannot replace it after observing Stage-1 results.

## Coverage rule

This PR deliberately does not retrieve the full history merely to inspect performance or choose a favorable sample. The coverage rule is frozen before retrieval:

```text
historical cutoff = 2026-08-08T00:00:00Z
start = earliest schema-valid metric timestamp returned by the endpoint
end   = latest schema-valid metric timestamp <= cutoff
use all valid rows in between
```

There is no result-driven start-date selection. Missing dates are not interpolated or forward-filled for the primary feature.

Concrete `start`, `end`, raw SHA256 and dataset version are written to `config/dataset_exposure_registry.json` only after the first immutable full-history raw capture establishes them truthfully.

## Raw-vintage policy

Every real capture must preserve the exact HTTP response bytes before parsing and compute SHA256 over those bytes. The raw payload and its manifest are create-only and may never be overwritten by later vendor revisions.

The manifest records at minimum:

- retrieval timestamp;
- exact endpoint and HTTP method;
- response status;
- selected provenance headers (`content-type`, `date`, `etag`, `last-modified` when present);
- exact byte length;
- SHA256;
- source SDK reference commit;
- parser version.

Recurring raw payloads must not be committed to Git. Genuine forward collection requires durable external object storage with create-if-absent/versioning semantics. The repository filesystem backend is only a local/CI reference implementation.

## Revision semantics

If DefiLlama later revises a historical value, the prior raw vintage remains immutable. For a decision timestamp `T`, only a revision first retrieved at or before `T` may be used. A later vendor revision cannot retroactively alter the researcher's earlier as-of view.

For genuinely future snapshots collected after this contract is merged, first-seen retrieval time becomes the earliest eligible `available_at` unless the source later exposes a verifiable publication timestamp under a separately frozen contract change.

## Feature boundary

The Stage-1 feature family remains exactly:

```text
growth_20d(t) = ln(S_t) - ln(S_t-20d)
acceleration_20d(t) = growth_20d(t) - growth_20d(t-20d)
```

with exact UTC date matching. A missing lag or non-positive value makes the feature unavailable; it does not trigger interpolation, nearest-date substitution, alternative lookback selection, or a new representation under the same Research ID.

USDT-only, USDC-only, chain-specific, dominance and price fields are not Stage-1 substitutes.

## Explicit non-actions in this PR

This source audit and contract do **not**:

- download the complete stablecoin history;
- calculate the Stablecoin feature on real history;
- fit Ridge or any other model;
- construct Stage-1 labels or predictions;
- run a backtest;
- inspect CAGR, Sharpe, Calmar, equity curves or crash-period results;
- update the Edge Registry;
- modify BRRK, BNB, costs, leverage, shorts, Phase 6/7/8 or production authority.

`ONCHAIN-HOLDER-COST-0001` remains backlog and is not part of this source contract.
