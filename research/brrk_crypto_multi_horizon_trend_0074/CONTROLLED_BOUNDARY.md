# BRRK-CRYPTO-MULTI-HORIZON-TREND-0074 — CONTROLLED BOUNDARY

Status: STAGE 6 / CONTROLLED BOUNDARY IN PROGRESS

This boundary inherits the merged Stage-3 preregistration and Stage-4/5 mechanics without scientific change. Stage-6 controlled scientific/history reads remain 0, scientific engine calls remain 0, scientific source-network fetches remain 0, and the controlled attempt remains 0/1.

## Immutable lineage

- Stage 1 OWNER-FIRST merge: `2af445a26e2a1d08b38a1cc9f6c853b29c828cde`.
- Stage 2 DESIGN merge: `08eafc22c3772bd021bc7e3c201c5dc63ac81e64`.
- Stage 3 PREREGISTRATION merge: `beae11d807886bfec65aa5cc8a26f79e92e5a0e9`.
- Stage 4 IMPLEMENTATION merge: `b74263cd6ab2bddd37544702fec0a187b7433151`.
- Stage 5 NONHISTORICAL QUALIFICATION merge: `c1bf177d98e14f54c26374cf52151c9ad90733e8`.

No Stage-6 action may change frozen source families, window, candidates, horizons, chronology, volatility target, exposure caps, costs, support minima, G0-G11 gates, inference constants, neighborhood stresses or terminal classifications.

## Authorized source universe

Official host: `https://data.binance.vision` only.

Symbols: exactly `BTCUSDT`, `ETHUSDT`, `SOLUSDT`.

Months: exactly every calendar month from `2021-01` through `2026-07` inclusive, 67 months.

Required archive families for every symbol-month:

1. `data/futures/um/monthly/klines/{SYMBOL}/1d/{SYMBOL}-1d-{YYYY}-{MM}.zip`
2. `data/futures/um/monthly/fundingRate/{SYMBOL}/{SYMBOL}-fundingRate-{YYYY}-{MM}.zip`

Expected required historical payload-object count is therefore exactly `3 assets × 2 families × 67 months = 402` ZIP objects, plus exactly 402 paired official `.CHECKSUM` identity objects.

No alternate venue, API endpoint, spot series, mark/index series, symbol substitution, source-family substitution or history extension is authorized.

## Identity manifest gate

Before Stage 6 may merge, a create-only authorized-object manifest must prospectively enumerate all 402 required payload objects. Every row must contain:

- asset;
- archive family;
- exact calendar month;
- exact official object path;
- paired official `.CHECKSUM` path;
- checksum text parsed as SHA-256 identity;
- expected UTC coverage identity;
- scientific content-read budget = 1;
- staging status and immutable staged-object identity fields.

Identity/checksum metadata may be obtained without opening ZIP/CSV scientific payload content. Missing, malformed, ambiguous or changing checksum identity fails closed for that required object. No payload may be opened merely to repair identity uncertainty.

## Payload staging gate

Stage 6 must not repeat the 0073 failure mode in which object identities existed but decision-critical payload bytes were not durably staged before the irreversible attempt.

Before Stage 7 can PASS, every one of the 402 required historical payloads must be:

1. durably staged before Stage 8;
2. bound to its prospectively frozen official SHA-256 identity;
3. independently hash-verifiable from the staged bytes;
4. offline-readable without any Stage-8 scientific source-network fetch;
5. mapped one-to-one to the authorized-object manifest;
6. unmodified after the final Stage-7 preflight PASS.

Stage 7 is forbidden to PASS if any required payload is identity-only, missing, unreadable offline, hash-mismatched, ambiguously mapped or dependent on a Stage-8 network fetch.

## Scientific-content prohibition before Stage 8

Stage 6 and Stage 7 may inspect only identity, checksum, file-presence, byte-size, hash and offline-readability mechanics. They may not expose scientific values from historical klines or funding payloads to the researcher and may not compute returns, signals, funding realization, NAV, candidate metrics, gates, bootstrap, DSR or PBO.

Any pre-Stage-8 scientific-value exposure is a governance violation and blocks the same-ID controlled attempt rather than being retroactively legalized.

## Exactly-once Stage-8 boundary

After a merged Stage-7 `PREFLIGHT_PASS_ZERO_RESULT` and contemporaneous explicit user authorization:

1. persist durable remote `RUN_ATTEMPT.marker`;
2. independently re-read and verify marker durability;
3. only then open authorized staged historical payloads;
4. read each authorized payload object at most once scientifically;
5. execute the frozen scientific engine exactly once;
6. perform zero scientific source-network fetches;
7. persist create-only `PRIMARY_RESULT.json`, `EVIDENCE.json`, `EXECUTION.json` and finally `RUN_ONCE.marker`.

After durable attempt-marker creation, no rerun, retune, rescue, source substitution, history extension, horizon alteration, candidate replacement, threshold relaxation or recomputation is legal.

## Stage-6 accounting

- controlled attempt: `0/1`;
- controlled scientific/history reads: `0`;
- scientific engine calls: `0`;
- scientific source-network fetches: `0`;
- production_authorized=false;
- signature_authorized=false;
- order_submission_authorized=false.

Stage 6 remains IN PROGRESS until the exact authorized-object manifest and durable-staging evidence satisfy this boundary and exact-head standing CI succeeds.