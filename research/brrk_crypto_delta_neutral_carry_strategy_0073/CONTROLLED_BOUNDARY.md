# BRRK-CRYPTO-DELTA-NEUTRAL-CARRY-STRATEGY-0073 — Stage 6 CONTROLLED BOUNDARY

Status: `BOUNDARY IN PROGRESS / ZERO CONTROLLED HISTORY READS / ATTEMPT 0/1`

Date: 2026-08-22

## Lifecycle anchors

- Program roadmap merge: `169d9adf6531dc099a43541df413fef079322adf`.
- 0072 immutable closeout remains `INCONCLUSIVE_INSUFFICIENT_SUPPORT / CLOSED TO SAME-ID RERUN`.
- 0073 OWNER-FIRST, DESIGN, PREREGISTRATION, IMPLEMENTATION and NONHISTORICAL QUALIFICATION are merged.
- Stage-5 merge commit: `8ccf14ecf0e1e2b0ccfa94ad3600105fb321380b`.
- Controlled attempt remains `0/1`.
- Controlled scientific/history reads remain `0`.
- Scientific engine calls remain `0`.
- Source-network fetches by the scientific attempt remain `0`.
- Production/signature/order authority remains `false/false/false`.

## Frozen scientific contract

This boundary cannot alter any Stage-3 preregistration or Stage-4 implementation semantics. Assets remain exactly BTC, ETH and SOL. Declared candidates remain exactly:

1. `C1_LONG_SPOT_SHORT_PERPETUAL`;
2. `C2_LONG_SPOT_SHORT_DATED_FUTURE`;
3. `C3_CROSS_VENUE_SAME_UNDERLYING_HEDGE`.

No candidate replacement, source substitution, cross-asset hedge substitution, threshold relaxation, stress deletion, history extension, result-informed rescue, retune or rerun is permitted.

The 730-UTC-day controlled window, minimum 365 eligible daily observations, same-underlying neutrality rules, gross exposure cap, 20% reserve, dated-future eligibility/roll rules, C1_REALISTIC/C2_STRESSED costs, eight mandatory stresses, synchronized moving-block bootstrap `L=20 / 4000 replicates / seed=730073`, DSR trial count exactly 3, conditional PBO, concentration/capacity gates and frozen terminal classifications remain unchanged.

## Marker-before-read and exactly-once boundary

Stage 8 receives exactly one controlled scientific attempt. Before any authorized historical object content is opened, a durable remote `RUN_ATTEMPT.marker` must exist and identify the exact Stage-6 merged boundary commit. Marker creation itself consumes no historical read.

After that marker exists:

- each authorized historical object may be opened at most once by the scientific attempt;
- the scientific engine may be called exactly once;
- source-network fetches during the scientific attempt are fixed at zero;
- results are persisted create-only;
- `RUN_ONCE.marker` seals the attempt;
- same-ID rerun, rescue, retune, recomputation, refetch, source replacement and candidate replacement are forbidden.

## Authorized-object manifest requirement

No historical object is authorized merely by host, filename pattern or asset family. Stage 6 is not complete until a committed create-only manifest enumerates every authorized object by all of the following fields before any object-content read:

- `candidate_id`;
- `asset`;
- `venue`;
- `instrument_type`;
- exact official archive/object path;
- exact UTC coverage;
- object checksum supplied by the official archive where available;
- persisted SHA256 identity used by the controlled attempt;
- maximum scientific content-read budget, fixed to `1` per authorized object.

Primary archive authorization may use only official Binance public archive objects from `data.binance.vision` that satisfy the frozen point-in-time identity contract. Present-day instrument metadata may not be projected backward. `premiumIndexKlines` cannot be relabeled as funding. Funding requires an official historical funding object with event timestamps. C3 requires a separately prospectively qualified second official venue; absent exact frozen identities, C3 remains `UNAVAILABLE_INSUFFICIENT_SUPPORT` and cannot be replaced.

This file deliberately does **not** fabricate archive paths, checksums or hashes. Until the exact manifest is committed, authorized-object count is `0` and controlled content reads remain prohibited.

## Stage-6 completion gate

Stage 6 may earn lifecycle credit only when the same branch contains the exact authorized-object manifest, the zero-result preflight contract needed for Stage 7, and the mandatory `docs/CURRENT_STATE.md` handoff, with every standing governance check successful.

Until that merge:

- formal completion is `5/10`;
- Stage 6 is `IN PROGRESS`;
- attempt remains `0/1`;
- controlled reads remain `0`;
- scientific engine calls remain `0`;
- Stage 7 and Stage 8 remain prohibited.
