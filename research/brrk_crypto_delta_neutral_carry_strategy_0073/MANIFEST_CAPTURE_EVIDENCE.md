# 0073 Stage-6 authorized-object capture evidence

Status: `METADATA-ONLY / ZERO CONTROLLED PAYLOAD READS / ATTEMPT 0/1`

Date: 2026-08-22

## Purpose

This note narrows the Stage-6 authorized-object manifest without opening any historical ZIP/CSV payload. It records only official archive-family and integrity metadata that may be used to prospectively freeze exact objects.

## Frozen study interval

- capture cutoff: `2026-07-31T23:59:59.999999Z`
- controlled study interval: `2024-08-01T00:00:00Z` through `2026-07-31T23:59:59.999999Z`
- assets: exactly `BTC`, `ETH`, `SOL`
- declared candidates remain exactly C1/C2/C3; unavailable candidates remain in multiplicity accounting and may not be replaced.

## Official Binance archive families qualified at the family level

The official `binance/binance-public-data` documentation states that archive ZIPs are published as daily/monthly objects and each ZIP has a sibling `.CHECKSUM` file verified with SHA-256. Its helper documentation separately documents USD-M futures downloads and checksum retrieval.

For C1, the only archive families eligible for exact-object enumeration are:

1. spot monthly daily-close klines under `data/spot/monthly/klines/<ASSET>USDT/1d/`;
2. USD-M perpetual monthly daily-close klines under `data/futures/um/monthly/klines/<ASSET>USDT/1d/`;
3. USD-M historical funding-event archives under `data/futures/um/monthly/fundingRate/<ASSET>USDT/`.

`premiumIndexKlines` is explicitly excluded from funding evidence. No family substitution is permitted.

## Integrity rule added before exact-object authorization

Official archive documentation states archived files may later be updated and provides an update log. Public issue history also documents cases where monthly archive checksum/content integrity required correction or investigation. Therefore Stage 6 must pin the checksum companion observed during this boundary stage for every exact object. A filename or host path alone is insufficient identity evidence.

For each object, final authorization requires all of:

- exact object path;
- exact native UTC coverage;
- exact sibling `.CHECKSUM` path;
- checksum text captured before any payload read;
- persisted SHA256 identity equal to the checksum value;
- scientific content-read budget exactly `1`.

If any checksum companion is absent, malformed, ambiguous, or changes before Stage-6 merge, that object is not authorized. Stage 6 must fail closed rather than download the payload to resolve uncertainty.

## Candidate-specific status

### C1_LONG_SPOT_SHORT_PERPETUAL

`PENDING_EXACT_OBJECT_ENUMERATION`.

Family-level qualification exists for spot klines, USD-M perpetual klines, and historical funding-event archives. C1 does not become authorized until every required monthly object for all three assets across the frozen interval has an exact checksum-pinned manifest row.

### C2_LONG_SPOT_SHORT_DATED_FUTURE

`PENDING_POINT_IN_TIME_IDENTITY / FAIL_CLOSED_IF_NOT_ENUMERABLE`.

Stage 3 forbids projecting present-day instrument metadata backward. Dated-future contract identities and listing eligibility therefore require exact historical archive identities that prove which contract objects existed for each roll decision. No perpetual object, continuous-contract series, or present-day exchange metadata may substitute for that evidence.

### C3_CROSS_VENUE_SAME_UNDERLYING_HEDGE

`UNAVAILABLE_INSUFFICIENT_SUPPORT` unless a separately prospectively qualified second official venue and exact historical object identities are frozen before any controlled history read. No second venue has been frozen by this evidence note, so no replacement venue is introduced.

## Budget preservation

- controlled attempt: `0/1`
- controlled scientific/history payload reads: `0`
- scientific engine calls: `0`
- Stage-8 source-network fetches: `0`
- production/signature/order authority: `false/false/false`

This metadata-only capture does not create `RUN_ATTEMPT.marker`, does not open any historical payload, does not inspect realized strategy results, and does not consume a scientific read budget.

## Exact next capture step

Enumerate the C1 monthly objects for BTC/ETH/SOL over `2024-08` through `2026-07`, capture each sibling `.CHECKSUM`, and create the final create-only authorized-object manifest. In parallel, enumerate C2 dated-future archive identities only if they can be established prospectively from official historical archive metadata without opening scientific payloads. Otherwise persist C2 as unavailable under the frozen preregistration.
