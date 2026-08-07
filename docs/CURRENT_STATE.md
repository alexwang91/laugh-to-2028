# BRRK Current State

Last updated: 2026-08-07
Status: **authoritative current-state handoff**

## Executive state

```text
Phase 0                         COMPLETE / MERGED
Phase 1                         COMPLETE / MERGED
Phase 2                         COMPLETE / MERGED
Phase 3                         COMPLETE / MERGED
P4.1 defensive scaler          COMPLETE / MERGED / frozen [0,1]
P4 architecture + cap1         COMPLETE / MERGED
P4 margin/liquidation prereqs  COMPLETE / MERGED
LEVERAGE-0040                  COMPLETE / IMMUTABLE / NO_PROMOTION
P4.5 closeout                  COMPLETE / MERGED
LEVERAGE-0041 preregistration  COMPLETE / MERGED
LEVERAGE-0041 implementation   IN PROGRESS / PRE-RESULT
P4.6 production leverage gate  BLOCKED / SEPARATE AUTHORIZATION
P5 exit intelligence           NOT STARTED
production authorization       NONE
```

`production_authorized_components = []`

Current production gross cap = `1.0`.

Canonical merged base for LEVERAGE-0041 implementation:

`baaa5776892411990734ef2121cf54a5dbbab047`

## LEVERAGE-0040 immutable truth

- result commit: `bd256e77a9800556e97769858fbb3ba5054c4389`
- summary SHA256: `3bb4dc46c61a5e9c7e049862575a89b2771830410ce4bc2bb25c83e469f52fc0`
- selection: `NO_PROMOTION`
- selected cap: none
- operating DD budget: none
- production authorization: none

Do not rerun, rescue, retune, reinterpret, or reuse `LEVERAGE-0040`.

## LEVERAGE-0041 frozen research target

Candidate grid:

`1.00 / 1.05 / 1.10 / 1.15 / 1.20 / 1.25 / 1.30`

`1.20` is a focal design point only.

Architecture: `SPOT_FIRST_BASE_PLUS_PERP_OVERLAY_V1`

- requested target = frozen raw BRRK-0011 target × cap;
- 25% NAV explicit cross-margin cash reserve;
- <=75% NAV spot financing;
- BTC/ETH/SOL base longs spot-first when pinned P2 evidence permits;
- BNB perp-only;
- residual base and incremental exposure perp;
- funding reducer uses seven complete prior sessions / 168h and may only reduce incremental overlay;
- liquidation uses only actual routed perp notionals against the explicit 25% reserve;
- liquidation distance must be >55%;
- 20% defensive tail budget and 70% catastrophe limit remain unchanged;
- bootstrap seed = `20260807`;
- sweet spot must be inside a contiguous three-cap all-PASS neighborhood.

## Authorization state

The owner has explicitly authorized, as one continuous research workflow:

1. merge the LEVERAGE-0041 preregistration;
2. implement the frozen study contract;
3. run pre-result CI/preflight;
4. if those gates are green, commit the frozen RUN_ONCE marker and execute the one-time research study.

Therefore the RUN_ONCE boundary is a **technical/audit one-shot boundary, not a new permission prompt**.

This standing research authorization does **not** authorize P4.6 or production gross >1.

## Frozen product boundaries

- directional core: BRRK-0011;
- target/tradable assets: BTC / ETH / SOL / BNB;
- XRP feature-only;
- Hyperliquid primary venue;
- daily 00:00 UTC;
- FLAT = zero directional exposure;
- FLAT -> LONG / SHORT requires human approval;
- intraday automation may reduce but not autonomously add directional exposure;
- trading Agent/API credentials only;
- master key, withdrawals and external transfers remain out of scope;
- P4.1 defensive scaler stays `[0,1]`.

## Exact next action

```text
IMPLEMENT LEVERAGE-0041 FROZEN STUDY CONTRACT
RUN FRESH CI + BLINDED PREFLIGHT
IF GREEN, COMMIT THE ALREADY-AUTHORIZED RUN_ONCE MARKER
EXECUTE THE ONE-TIME STUDY
VALIDATE + COMMIT IMMUTABLE RESULT
DO NOT RETUNE AFTER RESULT OBSERVATION
DO NOT PRODUCTION-AUTHORIZE; P4.6 REMAINS SEPARATE
```
