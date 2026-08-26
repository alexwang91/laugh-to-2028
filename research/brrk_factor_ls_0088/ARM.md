# BRRK Factor Long/Short 0088 — ARM

Research ID: `BRRK-FACTOR-LS-0088`
Gate: `ARM`
Controlled attempt: `0/1`
Controlled value reads: `0`
Scientific engine calls: `0/1`
Scientific values exposed: `false`
Production/signature/order/withdrawal/transfer authority: `false`

## Bound controlled source

ARM reuses only opaque byte identities already staged under the immutable 0075/0076 lineage. It transfers zero scientific result, attempt credit, lifecycle credit, factor-selection credit, or portfolio-result credit.

The exact outer artifact identity is GitHub Actions run `32646565505`, artifact `9495175701`, name `0075-stage6-authorized-payloads-v1`, size `174445627`, digest `sha256:8040282ff412b2d3fd360173e4745ebfd048796eb9e9c2ad49fa0901e5cedf56`.

The immutable 0075 parent manifest SHA-256 is `2f70384dd84a601b69528ef3d770e0fa9c714b3e0888bec009e93b5067ecebf8`. The immutable 0076 metadata-only submanifest SHA-256 is `c33b575cc436db795086458a25ca38fe1527f649809e549caba00e9754422e58`.

0088 selects exactly all `30,336` authorized objects in that immutable submanifest:

- `15,254` Binance USD-M monthly `1d` kline objects;
- `15,082` Binance USD-M monthly funding-rate objects;
- historical candidate months remain `2021-01` through `2026-07`;
- the source universe covers `467` eligible symbols represented in the immutable submanifest;
- `BTCUSDT` must be present because the frozen SPEC uses BTC MOM60 state and beta diagnostics.

The source selection is deterministic from the immutable submanifest and may not change after ARM. No current-symbol snapshot, survivorship-filtered universe, alternate venue, new download, source substitution, or history extension is permitted.

## Source-qualified interface

Any future RUN must use `ControlledResearchRunnerV1SourceQualified` and `FactorLS0088Engine`.

The metadata-only source-key validator must accept only the BUILD-qualified namespaces and exact families encoded in `research/brrk_factor_ls_0088/source_adapter.py`:

- `payloads/...monthly__klines__<SYMBOL>__1d__<SYMBOL>-1d-YYYY-MM.zip`;
- `stage/payloads/...monthly__klines__<SYMBOL>__1d__<SYMBOL>-1d-YYYY-MM.zip`;
- `payloads/...monthly__fundingRate__<SYMBOL>__<SYMBOL>-fundingRate-YYYY-MM.zip`;
- `stage/payloads/...monthly__fundingRate__<SYMBOL>__<SYMBOL>-fundingRate-YYYY-MM.zip`.

Unknown namespaces, unknown families, duplicate logical `(family, symbol, month)` objects, missing required kline or funding family, or missing `BTCUSDT` fail closed before controlled value execution.

The common runner owns durable marker-before-read, manifest/hash/size verification, at-most-once payload reads, exactly-one scientific-engine invocation, create-only result persistence, failure classification, and `RUN_ONCE` sealing.

## Zero-result preflight boundary

Before a durable RUN marker, code may inspect only Git identity, artifact identity/size/digest, declared manifest/submanifest hashes, central-directory filenames/metadata, source-key filenames, and declared object hashes/sizes.

Before a durable marker, code may not call `testzip()`, decompress payload entries, open inner ZIPs, open or parse CSV, traverse payload CRCs, read scientific rows, calculate factors, calculate funding PnL, build portfolios, calculate returns, or calculate scientific metrics.

ARM performs no controlled payload read and consumes no attempt.

## Frozen RUN order

1. fresh metadata/identity-only zero-result preflight passes;
2. a separate contemporaneous user authorization explicitly grants 0088 controlled attempt `1/1`;
3. create durable `RUN_ATTEMPT.marker`;
4. verify that marker remotely;
5. consume attempt `1/1`;
6. read each of the `30,336` selected controlled objects at most once through the common runner;
7. invoke `FactorLS0088Engine` exactly once;
8. persist `PRIMARY_RESULT.json` create-only;
9. create durable `RUN_ONCE.marker`;
10. SEAL performs zero scientific reread or recomputation.

Any common-runner-caused new `INVALID_EXECUTION` pauses all new controlled science pending runner repair and full requalification. It does not authorize a replacement retry chain.

## What did not change

- 0088 still uses exactly the three immutable 0086 passing factors with signs `MOM60_RAW=-1`, `RVOL20_RAW=-1`, `LIQ30_RAW=+1`.
- Equal one-third signed-rank composite, PIT top-30 universe, Monday UTC-close cadence, FWD5 horizon, top/bottom terciles, gross `2.0`, net `0`, turnover, source-native funding, C0/C1/C2 costs, beta, capacity, concentration, support rules, 8-week 10,000-replicate MBB, seed `880088`, G0-G9, and terminal classifications remain unchanged.
- The merged invalid-week transition clarification remains unchanged.
- Controlled attempt remains `0/1`; controlled reads remain `0`; scientific engine remains `0/1`; scientific values remain unexposed.
- 0086 remains immutable `PASS_VALIDATED_FACTOR_ATLAS`; its factor identities/signs cannot be reinterpreted.
- 0076 remains sealed at its Stage7 pre-marker read-boundary incident; 0085 remains immutable `INVALID_EXECUTION`; 0072/0073 remain paused; 0083 remains immutable FAIL; all other immutable historical states remain unchanged.
- `workflow run                         31381953131 / attempt 1` remains immutable; CAPTURE-0001 remains sealed/no-retry; CAPTURE-0002 remains permanently claimed/no-refetch.
- Phase6 PASS closeout, common-runner qualification, and prospective five-gate lifecycle remain unchanged.
- 0087 remains blocked before controlled science by its qualifying Deribit source-metadata requirement.
- No production, signing, order, withdrawal, or transfer authority is granted.
