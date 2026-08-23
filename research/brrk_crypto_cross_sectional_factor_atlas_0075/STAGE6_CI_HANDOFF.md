# 0075 Stage 6 CI Handoff — CONTROLLED-EXECUTION BOUNDARY

Research ID: `BRRK-CRYPTO-CROSS-SECTIONAL-FACTOR-ATLAS-0075`

Lifecycle stage: `6/10 CONTROLLED-EXECUTION BOUNDARY` **IN PROGRESS; NO LIFECYCLE CREDIT YET**.

Stage5 merge / Stage6 parent: `c03dba8a89de81869a8dcb8024f95538f2f9af3f`.

Controlled attempt: `0/1`; controlled scientific-history reads: `0`; scientific engine calls: `0`; scientific source-network fetches: `0`.

## Purpose

This handoff opens Stage6 from the exact merged Stage5 parent. It does not authorize Stage8 execution and does not itself claim that the controlled boundary is complete.

Stage6 must enumerate and hash-bind every exact authorized Binance public archive object required by the frozen Stage3 source families and candidate months, prove durable offline readability without exposing scientific payload values, freeze per-object at-most-once controlled read budgets, and persist an exact create-only marker/result contract before Stage7 can begin.

## Frozen source families

No source family changes are permitted from Stage3. The only admissible families remain:

- SPOT monthly daily klines for eligible `*USDT` symbols;
- USD-M monthly daily perpetual klines for matching perpetual symbols where derivatives features are defined;
- USD-M monthly `fundingRate` archives for matching perpetual symbols.

Candidate months remain exactly `2021-01` through `2026-07`, inclusive, subject only to exact Stage6 object availability. No network/economic-state family, open-interest family, substitute venue, alternate endpoint, history extension, candidate replacement, or result-informed pruning may be introduced.

## Stage6 completion obligations

Before this stage may earn 6/10 credit, the branch must persist and CI must validate all of the following without any controlled scientific-history read:

1. an exact authorized-object manifest with source path, paired `.CHECKSUM` identity, payload SHA256 and frozen object role for every staged object;
2. durable offline staging/readability evidence for every authorized object, using identity/metadata validation only;
3. explicit fail-closed behavior for missing, extra, duplicate or hash-mismatched objects;
4. exact at-most-once per-object controlled content-read budget for Stage8;
5. Stage8 scientific source-network fetch budget exactly `0`;
6. Stage8 scientific engine budget exactly `1/1`;
7. durable `RUN_ATTEMPT.marker` creation and remote verification before any controlled payload content read;
8. create-only result persistence followed by marker-only finalization and durable `RUN_ONCE.marker`;
9. no source substitution, rerun, retune, rescue, recomputation or history extension after attempt-marker durability;
10. exact standing-CI SUCCESS on the final Stage6 head and synchronized `docs/CURRENT_STATE.md` before merge.

## What did not change

- Stage3 frozen science is unchanged.
- No 0075 historical/scientific payload content was opened.
- No factor return, IC, spread, p-value, support, sign, ranking, winner, universe membership, price, volume, funding or basis value was inspected.
- Controlled attempt remains `0/1` and unconsumed.
- Controlled scientific-history reads remain `0`.
- Scientific engine calls remain `0`.
- Scientific source-network fetches remain `0`.
- Stage5 remains the latest formally completed 0075 lifecycle stage until this Stage6 boundary is fully evidenced, CI-green and merged.
- 0072, 0073 and 0074 immutable outcomes remain unchanged; 0071 remains permanently blocked at 6/10; 0083 remains immutable FAIL 10/10 attempt 1/1.
- The historical CURRENT_STATE line `workflow run                         31381953131 / attempt 1` must remain byte-for-byte present.
- CAPTURE-0001 remains sealed after failed HTTP 451 with no retry; CAPTURE-0002 remains permanently claimed with no refetch.

## Exact next step

Enumerate the frozen Stage3 source identities into the Stage6 authorized-object manifest and stage/hash-verify them without reading scientific payload values. Then persist boundary/staging evidence, synchronize CURRENT_STATE, run exact-head standing CI, and merge only after every mandatory check is terminal SUCCESS.
