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
LEVERAGE-0039                  STOPPED PRE-RUN / NO RESULT
LEVERAGE-0040                  COMPLETE / IMMUTABLE / NO_PROMOTION
LEVERAGE-0041                  COMPLETE / IMMUTABLE / NO_PROMOTION
Phase 4 leverage research      FAIL_STOP / no eligible >1 candidate
P4.6 production leverage gate  NOT ENTERED / BLOCKED by no candidate
P5 cycle-top / exit research   NEXT
Phase 6 integrated shadow      NOT STARTED
Phase 7 limited live long      NOT STARTED / explicit approval required
Phase 8 bear-short research    NOT STARTED
production authorization       NONE
```

`production_authorized_components = []`

Current production gross cap remains `1.0`.

## LEVERAGE-0040 immutable truth

- result commit: `bd256e77a9800556e97769858fbb3ba5054c4389`;
- summary SHA256: `3bb4dc46c61a5e9c7e049862575a89b2771830410ce4bc2bb25c83e469f52fc0`;
- result status: `ONE_TIME_PREREGISTERED_STUDY_COMPLETE`;
- selection: `NO_PROMOTION`;
- selected research cap: none;
- selected operating DD budget: none;
- production authorization: none.

Do not rerun, rescue, retune, reinterpret, or reuse `LEVERAGE-0040`.

## LEVERAGE-0041 immutable truth

Implementation/prereg base main:

`baaa5776892411990734ef2121cf54a5dbbab047`

One-time result commit:

`8ea784830cfffbf892a258cb329d437725d41982`

Immutable summary SHA256:

`e41a5895263e7aa9206df9fa99fcbb71e5f937abc4746a567fbeb462cca88d17`

Final selection:

```text
status                                  ONE_TIME_PREREGISTERED_STUDY_COMPLETE
selection.status                        NO_PROMOTION
selected_research_cap                   NONE
selected_operating_max_drawdown_budget  NONE
prospective_live_cap_if_authorized      NONE
production_authorized                   false
```

Frozen search grid:

`1.00 / 1.05 / 1.10 / 1.15 / 1.20 / 1.25 / 1.30`

5 bps result summary:

```text
cap 1.00  CAGR 61.28%  MDD -33.83%  Sharpe 1.3005  comparator
cap 1.05  CAGR 62.56%  MDD -35.30%  Sharpe 1.2935  FAIL
cap 1.10  CAGR 62.84%  MDD -36.59%  Sharpe 1.2746  FAIL
cap 1.15  CAGR 62.96%  MDD -37.90%  Sharpe 1.2544  FAIL
cap 1.20  CAGR 64.90%  MDD -39.16%  Sharpe 1.2574  FAIL
cap 1.25  CAGR 64.89%  MDD -40.19%  Sharpe 1.2387  FAIL
cap 1.30  CAGR 66.28%  MDD -40.93%  Sharpe 1.2360  FAIL
```

All caps above 1.0 failed `pass_pre_broad_region`; therefore no contiguous all-pass neighborhood exists and no cap reaches the frozen selection stage.

The liquidation-distance gate remained binding under the corrected spot/perp/collateral accounting. Frozen acceptance was strictly `>55%`; measured minimum uniform adverse-move distance was:

```text
cap 1.00  45.98%  FAIL
cap 1.05  42.52%  FAIL
cap 1.10  38.54%  FAIL
cap 1.15  35.19%  FAIL
cap 1.20  32.33%  FAIL
cap 1.25  29.86%  FAIL
cap 1.30  27.71%  FAIL
```

`starting_liquidatable_state_seen=false` in the corrected 0041 implementation; unlike the old 0040 architecture, this is not the former zero-distance accounting pathology. It is a genuine failure of the preregistered >55% reserve/liquidation safety threshold under the tested architecture.

Do not rerun, rescue, retune, reinterpret, or reuse `LEVERAGE-0041` under the same experiment ID.

## Roadmap audit status

Full review: `docs/ROADMAP_AUDIT_2026-08-07.md`.

Current unresolved product/strategy/production drift: **none identified**.

Historical deviations were handled as corrections rather than silently carried forward:

- legacy execution/security backlog gaps were corrected before P3.2;
- F27 measurement / EXPOSURE-SMOOTH authority drift was normalized;
- P3.1 missing feature-only XRP input was corrected through an explicit schema version and revalidation;
- `LEVERAGE-0039` architecture drift was detected before first economic run, stopped, and replaced with new experiment IDs rather than rescued;
- `LEVERAGE-0040` and `LEVERAGE-0041` preserve immutable failed results and no post-result retuning;
- repository branch/document authority hygiene was normalized;
- P3.2/P3.3/P3.4 machine-readable registry omissions are being normalized in the current closeout without changing implementation semantics.

Current product-state classification: **DRIFT_0**. The closeout PR itself is a documentation/registry normalization change and may be labeled `DRIFT_1` operationally without implying product/strategy drift.

## Frozen product boundaries

- directional core: BRRK-0011;
- target/tradable assets: BTC / ETH / SOL / BNB;
- XRP feature-only;
- primary venue: Hyperliquid;
- daily decision boundary: 00:00 UTC;
- FLAT = zero directional exposure;
- FLAT -> LONG / SHORT requires human approval;
- MONITOR_ONLY -> ACTIVE requires human approval;
- first short of a new bear phase requires human approval;
- intraday automation may reduce but not autonomously add directional exposure;
- trading Agent/API credentials only;
- master key, withdrawals and external transfers remain outside scope;
- P4.1 defensive scaler stays `[0,1]`;
- production gross remains `1.0`.

## Exact next action

After the Phase-4 closeout branch is fully CI/governance verified and merged into `main`:

```text
CREATE A FRESH PHASE-5 BRANCH FROM NEW MAIN
START P5.1 EVENT TAXONOMY ONLY
PRESERVE BRRK-0011 / FOUR-ASSET LONG UNIVERSE / HYPERLIQUID / 00:00 UTC
DO NOT RETUNE LEVERAGE-0040 OR LEVERAGE-0041
DO NOT PRODUCTION-AUTHORIZE LEVERAGE
DO NOT START P6/P7/P8 BEFORE P5 CLOSES ITS OWN GATES
```
