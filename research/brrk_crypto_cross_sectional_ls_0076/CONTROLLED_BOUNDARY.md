# 0076 Stage6 CONTROLLED-EXECUTION BOUNDARY

Research ID: `BRRK-CRYPTO-CROSS-SECTIONAL-LS-0076`

Lifecycle stage: `6/10 CONTROLLED-EXECUTION BOUNDARY`.

Parent Stage5 merge: `0e453df9a1148919333a85d695bacfc9b35dbd39`.

Formal lifecycle completion remains `5/10` until this Stage6 PR merges.

## Boundary purpose

This stage freezes the execution boundary after the already-frozen Stage3 science, complete Stage4 implementation, and Stage5 nonhistorical qualification. It does not authorize or perform any controlled scientific/history read.

Stage6 derives the exact 0076 authorized-object sub-manifest from the immutable 0075 Stage6 zero-result cache identities using object-path identity only. The selection is restricted to the source contract frozen in 0076 Stage3:

- official source family: `data.binance.vision` public archive;
- parent authorized-object manifest Git blob: `74b119149e55c6c7a4fc641840b07c24bb27644a`;
- parent manifest SHA-256: `2f70384dd84a601b69528ef3d770e0fa9c714b3e0888bec009e93b5067ecebf8`;
- parent symbol-universe Git blob: `45c07672c6404593279333ec1995c0ae0203eed3`;
- parent symbol-universe SHA-256: `85337b0681d4e61fc60eef62f4f05b2ea6e43f7da9e7648b4d94032794f95dbd`;
- staging workflow run: `32646565505` = terminal `SUCCESS`;
- staging artifact: `9495175701` / `0075-stage6-authorized-payloads-v1`;
- only USD-M monthly daily perpetual kline objects and USD-M monthly `fundingRate` objects for eligible `*USDT` symbols;
- source months exactly `2021-01` through `2026-07`, inclusive.

No parent scientific result or lifecycle credit transfers to 0076.

## Durable Stage6 sub-manifest evidence

The repository now durably persists `AUTHORIZED_OBJECT_SUBMANIFEST.json` and `STAGE6_SUBMANIFEST_VALIDATION.json` derived solely from the pinned parent metadata files and ZIP central-directory filenames.

Validation is `PASS`:

- authorized objects = `30336`;
- unique canonical object IDs = `30336`; duplicates = `0`;
- USD-M monthly 1d perpetual-kline objects = `15254`;
- USD-M monthly funding-rate objects = `15082`;
- eligible symbols = `467`;
- selected objects missing staged payload filenames = `0`;
- selected objects missing checksum filenames = `0`;
- parent manifest and symbol-universe SHA-256 identities verified = `true`;
- authorized sub-manifest SHA-256 = `c33b575cc436db795086458a25ca38fe1527f649809e549caba00e9754422e58`;
- scientific payload file contents opened = `false`;
- scientific rows parsed = `false`;
- frozen science changed = `false`.

The temporary metadata-only materialization workflow removed itself after creating this durable evidence and is not part of the final Stage6 tree.

## Exactly-once boundary

Before Stage8:

- controlled attempt = `0/1`;
- controlled scientific/history reads = `0`;
- scientific engine calls = `0/1`;
- Stage8 scientific source-network fetches = `0`;
- scientific values exposed = `false`;
- `RUN_ATTEMPT.marker` must be absent;
- result bundle must be absent;
- `RUN_ONCE.marker` must be absent.

Stage7 may verify only exact identities, artifact availability/readability, checksums, object counts, execution-interface identity, marker/result absence, and zero-budget state. Stage7 must not parse scientific payload rows or compute any factor, return, funding, cost, p-value, gate, ranking, or terminal classification.

Stage8, if later authorized after a lawful Stage7 PASS, must durably create and remotely verify `RUN_ATTEMPT.marker` before the first controlled content read. Marker durability consumes attempt `1/1`. Each authorized historical object may then be read at most once, the scientific engine must run exactly once, scientific source-network fetches must remain exactly zero, the result bundle must be create-only, and `RUN_ONCE.marker` must seal the attempt.

After marker durability, same-ID rerun, retune, rescue, source substitution, candidate replacement, history extension, or recomputation is forbidden.

## Fail-closed rules

Stage6 and later stages must fail closed if any pinned identity, checksum, staged artifact, authorized object, execution-interface identity, or budget invariant is missing or inconsistent. Same-ID network refetch or substitute-source rescue is forbidden.

No DEVELOPMENT-history evidence may be described as independent OOS evidence.

## Immutable governance anchors

The exact `docs/CURRENT_STATE.md` line `workflow run                         31381953131 / attempt 1` must remain permanently preserved. CAPTURE-0001 remains sealed failed HTTP 451 with no retry. CAPTURE-0002 remains permanently claimed with no refetch. Immutable 0070, 0071, 0083, 0072, 0073, 0074, 0075, and 0084 anchors remain authority.

Production authorization, signature authorization, and order-submission authorization remain false.

## Exact next step

Require fresh mandatory CI on this maintainer-authored exact head. If all checks are terminal green and ancestry/mergeability remain clean, expected-head merge this Stage6 PR. Only after that merge may an independent Stage7 ZERO-RESULT PREFLIGHT branch/PR begin.