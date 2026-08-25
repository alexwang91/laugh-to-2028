# BRRK Cross-Sectional Factor Atlas 0086 — ARM

Research ID: `BRRK-CROSS-SECTIONAL-FACTOR-ATLAS-0086`
Gate: `ARM`
Controlled attempt: `0/1`
Controlled value reads: `0`
Scientific engine calls: `0/1`
Scientific values exposed: `false`
Production/signature/order/withdrawal/transfer authority: `false`

## Bound controlled source

ARM reuses only opaque byte identities already staged under the immutable 0075/0076 lineage. It transfers zero scientific result, factor-selection credit, attempt credit, or lifecycle credit.

The exact outer artifact identity is GitHub Actions run `32646565505`, artifact `9495175701`, name `0075-stage6-authorized-payloads-v1`, size `174445627`, digest `sha256:8040282ff412b2d3fd360173e4745ebfd048796eb9e9c2ad49fa0901e5cedf56`.

The immutable 0075 parent manifest SHA-256 is `2f70384dd84a601b69528ef3d770e0fa9c714b3e0888bec009e93b5067ecebf8`. The immutable 0076 metadata-only submanifest SHA-256 is `c33b575cc436db795086458a25ca38fe1527f649809e549caba00e9754422e58`. That submanifest contains 30,336 authorized objects: 15,254 USD-M monthly 1d kline objects and 15,082 funding objects across 467 eligible symbols. 0086 selects exactly the 15,254 kline objects and excludes every funding object.

The selection is deterministic from the immutable submanifest and may not change after ARM. Candidate months remain 2021-01 through 2026-07. `BTCUSDT` must be present because the frozen SPEC uses BTC MOM60 state diagnostics.

## Source-qualified interface

Any future RUN must use `ControlledResearchRunnerV1SourceQualified` and `CrossSectionalFactorAtlas0086Engine`. Metadata-only source-key qualification may accept the already-qualified `payloads/...` and `stage/payloads/...` namespaces. Duplicate logical `(symbol, month)` objects, unknown namespaces, non-kline objects, or missing BTCUSDT fail closed before controlled value execution.

The common runner owns durable marker-before-read, verified at-most-once payload reads, exactly-one engine invocation, create-only result persistence, failure classification, and `RUN_ONCE` sealing.

## Zero-result preflight boundary

Before a durable RUN marker, code may inspect only Git identity, artifact identity/size/digest, declared manifest/submanifest hashes, central-directory filenames/metadata, and source-key filenames.

Before a durable marker, code may not call `testzip()`, decompress payload entries, open inner ZIPs, open or parse CSV, traverse payload CRCs, read scientific rows, calculate factors/returns, or calculate scientific metrics.

ARM itself performs no controlled payload read and consumes no attempt.

## Frozen RUN order

1. fresh metadata/identity-only zero-result preflight passes;
2. a separate contemporaneous user authorization explicitly grants 0086 controlled attempt 1/1;
3. create durable `RUN_ATTEMPT.marker`;
4. verify that marker remotely;
5. consume attempt 1/1;
6. read each of the 15,254 selected kline objects at most once through the common runner;
7. invoke the 0086 engine exactly once;
8. persist `PRIMARY_RESULT.json` create-only;
9. create durable `RUN_ONCE.marker`;
10. SEAL performs zero scientific reread/recomputation.

Any common-runner-caused new `INVALID_EXECUTION` pauses new scientific attempts pending runner repair/requalification. It does not authorize a replacement retry chain.

## What did not change

- SPEC_FREEZE science remains exactly three candidates: `MOM60_RAW`, `RVOL20_RAW`, `LIQ30_RAW`; no size or carry family is added.
- PIT top-30 universe, Monday UTC-close timing, FWD5 target, rank transforms, three-test Holm FWER 0.05, support minima, 10/20 bps cost panels, bootstrap/inference rules, G0-G9 gates, trial budget and terminal classifications remain unchanged.
- Controlled attempt remains `0/1`; controlled reads remain `0`; scientific engine remains `0/1`; scientific values remain unexposed.
- 0085 remains immutable `INVALID_EXECUTION`, attempt 1/1 consumed, with no admissible Trend result and no same-ID rerun/rescue/recompute.
- 0076 remains sealed at its pre-marker boundary incident; 0075/0084 remain immutable; 0072/0073 remain paused; 0083 remains immutable FAIL.
- `workflow run                         31381953131 / attempt 1` remains unchanged; CAPTURE-0001 remains sealed/no-retry; CAPTURE-0002 remains permanently claimed/no-refetch.
- Phase6 PASS closeout remains unchanged.
- No production, signing, order, withdrawal, or transfer authority is granted.
