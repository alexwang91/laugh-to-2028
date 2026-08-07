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
P5.1 event taxonomy            COMPLETE / FROZEN BEFORE FEATURE SELECTION
P5.2 feature families          NEXT
P5.3-P5.6                      NOT STARTED
Phase 6 integrated shadow      NOT STARTED
Phase 7 limited live long      NOT STARTED / explicit approval required
Phase 8 bear-short research    NOT STARTED
production authorization       NONE
```

`production_authorized_components = []`

Current production gross cap remains `1.0`.

## Phase 4 immutable truth

### LEVERAGE-0040

- result commit: `bd256e77a9800556e97769858fbb3ba5054c4389`;
- summary SHA256: `3bb4dc46c61a5e9c7e049862575a89b2771830410ce4bc2bb25c83e469f52fc0`;
- result status: `ONE_TIME_PREREGISTERED_STUDY_COMPLETE`;
- selection: `NO_PROMOTION`;
- selected research cap: none;
- selected operating DD budget: none;
- production authorization: none.

Do not rerun, rescue, retune, reinterpret, or reuse `LEVERAGE-0040`.

### LEVERAGE-0041

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

All caps above 1.0 failed `pass_pre_broad_region`; no candidate reaches P4.6. The corrected architecture removed the old 0040 zero-distance accounting pathology, but still failed the frozen `>55%` liquidation-distance safety threshold.

Do not rerun, rescue, retune, reinterpret, or reuse `LEVERAGE-0041` under the same experiment ID.

## P5.1 frozen event-taxonomy truth

Contract:

`P5.1-EVENT-TAXONOMY-V1`

Files:

```text
research/cycle_exit/p5_1_event_taxonomy.json
research/cycle_exit/p5_1_event_taxonomy.py
docs/P5_1_EVENT_TAXONOMY.md
```

The taxonomy was frozen before P5.2 feature/model selection. It references the existing product decision `PRODUCT-CYCLE-EXIT-2026-08-05` and changes no production authority.

Required roadmap cases are present:

```text
2021 spring major top / May crash        LOCAL_MAJOR_TOP_NONTERMINAL
2021 summer recovery                     SECOND_WIND_TRANSITION
2021 November final peak                 TERMINAL_TOP_BEAR_TRANSITION
2025 June new-high phase                 TEMPORARY_NEW_HIGH_PHASE
2025 August new-high phase               SECOND_WIND_NEW_HIGH_PHASE
2025 October new-high / deleveraging     NEW_HIGH_DELEVERAGING_PHASE
late-2025 deterioration                  POST_DELEVERAGING_DETERIORATION
```

Only the 2021 November case is explicitly terminal in V1. The 2025 sequence is not silently treated as a terminal cycle top.

V1 also includes four `HIGH_VOLATILITY_NON_TOP_CONTROL` windows spanning 2021, 2024 and 2025.

### Anchor discipline

P5.1 does not hand-pick the prettiest indicator date. It freezes calendar search windows and resolves anchors mechanically from canonical P3.1 BTCUSDT UTC daily closes using one of:

```text
BTC_CLOSE_MAX_IN_SEARCH_WINDOW
BTC_CLOSE_MIN_IN_SEARCH_WINDOW
MAX_10D_DRAWDOWN_END
PARENT_EVENT_ANCHOR
```

Missing canonical daily data fails closed. Forward fill is forbidden.

### Evaluation buckets

```text
early_warning    -28 .. -15 calendar days
target_lead      -14 ..  -7 calendar days
near_event        -6 ..   0 calendar days
immediate_after   +1 .. +28 calendar days
medium_after     +29 .. +90 calendar days
```

The 7–14 day target is an evaluation bucket, not a requirement to force a model to emit a warning there.

### Leakage boundary

Historical outcome labels may use realized future outcome to define what happened. P5.2+ feature values evaluated at day `t` may use only information observable by `t`.

Event windows/anchors may not be moved after feature performance is observed.

## Roadmap audit status

Full review: `docs/ROADMAP_AUDIT_2026-08-07.md`.

All historical deviations identified by the 2026-08-07 program-wide audit have recorded **CLOSED** dispositions. Current unresolved product/strategy/production drift: **none identified**.

Current product-state classification: **DRIFT_0**.

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

After this P5.1 taxonomy PR is CI/governance verified and merged:

```text
CREATE A FRESH P5.2 BRANCH FROM NEW MAIN
EVALUATE FEATURE FAMILIES UNDER P5.1-EVENT-TAXONOMY-V1
DO NOT MOVE EVENT WINDOWS OR ANCHORS BASED ON FEATURE PERFORMANCE
PRESERVE BRRK-0011 RELATIVE RANKING
DO NOT START P5.3 STATE-MODEL SELECTION BEFORE P5.2 FEATURE EVIDENCE IS REVIEWABLE
DO NOT START P6/P7/P8 BEFORE P5 CLOSES ITS OWN GATES
```
