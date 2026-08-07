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
LEVERAGE-0039                  STOPPED PRE-RUN / NO RESULT
LEVERAGE-0040                  COMPLETE / IMMUTABLE / NO_PROMOTION
LEVERAGE-0041                  COMPLETE / IMMUTABLE / NO_PROMOTION
Phase 4 leverage research      FAIL_STOP / no eligible >1 candidate
P4.6 production leverage gate  NOT ENTERED / BLOCKED by no candidate
P5.1 event taxonomy            COMPLETE / MERGED / FROZEN
P5.2 feature families          IMPLEMENTED / FROZEN / RESULT NOT RUN
P5.3-P5.6                      NOT STARTED
Phase 6 integrated shadow      NOT STARTED
Phase 7 limited live long      NOT STARTED / explicit approval required
Phase 8 bear-short research    NOT STARTED
production authorization       NONE
```

`production_authorized_components = []`

Current production gross cap remains `1.0`.

## Phase 4 immutable truth

`LEVERAGE-0040` and `LEVERAGE-0041` are complete immutable `NO_PROMOTION` studies. No research cap, operating drawdown budget or prospective P4.6 cap was selected. Do not rerun, rescue, retune, reinterpret or reuse either experiment ID.

LEVERAGE-0041 result commit:

`8ea784830cfffbf892a258cb329d437725d41982`

LEVERAGE-0041 immutable summary SHA256:

`e41a5895263e7aa9206df9fa99fcbb71e5f937abc4746a567fbeb462cca88d17`

## P5.1 immutable taxonomy truth

P5.1 merged in PR #97 on main `86497cdd663a89ca4d54c898b7acbac1cc07d836`.

Contract:

`P5.1-EVENT-TAXONOMY-V1`

Taxonomy blob SHA:

`73d010666fbfd957ec15214a00883a90a8adba5a`

Required 2021/2025 events and four high-volatility non-top controls are frozen before feature selection. Only 2021 November is explicitly terminal in V1. Search windows and anchor rules may not be moved after P5.2 results.

## P5.2 frozen pre-result truth

Contract:

`P5.2-FEATURE-FAMILIES-V1`

Status:

`FROZEN_BEFORE_FIRST_FEATURE_EVIDENCE_RUN`

Files:

```text
research/cycle_exit/p5_2_feature_contract.json
research/cycle_exit/p5_2_features.py
research/cycle_exit/run_p5_2_feature_evidence.py
research/cycle_exit/validate_p5_2_feature_result.py
docs/P5_2_FEATURE_FAMILIES.md
```

P5.2 is descriptive feature evidence only. It cannot select a final feature set, fit P5.3 state thresholds, alter BRRK-0011 or authorize production.

### Frozen available V1 evidence

29 causal features across:

- BTC trend maturity;
- daily / completed-4h momentum exhaustion;
- ETH/BTC, SOL/BTC, BNB/BTC leadership migration and BRRK return dispersion;
- canonical-five / BRRK breadth and high-beta participation.

Canonical price window:

`2020-10-01 -> 2026-02-28`

The end date was extended from 2025-12-31 **before any feature evidence was run** so the frozen P5.1 `+29..+90` medium-after bucket is fully covered for late-2025 events. No feature definition, event window, anchor or evaluation metric changed.

### Explicit data-source gaps

These remain `DATA_SOURCE_PENDING`, not silently proxied:

- BTC dominance;
- broad-market breadth;
- comparable 2021/2025 historical funding;
- historical open interest;
- fixed historical basis/premium panel;
- continuous liquidation proxy.

### One-time evidence boundary

Standing research authorization covers the P5.2 research RUN_ONCE after exact-head implementation/preflight CI is green.

The marker is a technical one-shot / no-retuning control, not a new owner-prompt boundary. Production authorization remains separate.

Before the marker is committed:

```text
P5.2 contract tests             MUST PASS
P5.1 taxonomy hash             MUST MATCH
Binance blinded data preflight MUST PASS
P5.2 result directory          MUST NOT EXIST
```

After the run, immutable validation must prove:

```text
feature evidence exists
available-feature coverage passes
pending source gaps remain explicit
feature_set_selected = false
state_thresholds_selected = false
production_authorized = false
```

## Roadmap audit status

All historical deviations identified by the 2026-08-07 program-wide audit have recorded CLOSED dispositions. Current canonical product/strategy/production drift: **DRIFT_0**.

## Frozen product boundaries

- directional core: BRRK-0011;
- target/tradable assets: BTC / ETH / SOL / BNB;
- XRP feature-only;
- primary venue: Hyperliquid;
- daily decision boundary: 00:00 UTC;
- FLAT = zero directional exposure;
- FLAT -> LONG / SHORT and MONITOR_ONLY -> ACTIVE require explicit human approval;
- first short of a new bear phase requires explicit human approval;
- intraday automation may reduce but not autonomously add directional exposure;
- master key, automated withdrawals and external transfers remain outside scope;
- P4.1 defensive scale stays `[0,1]`;
- production gross remains `1.0`.

## Exact next action

```text
RUN FRESH P5.2 CONTRACT + BLINDED DATA PREFLIGHT
IF ALL PRE-RUN GATES ARE GREEN, COMMIT THE FROZEN P5.2 RUN_ONCE MARKER
RUN THE ONE-TIME FEATURE-EVIDENCE SUITE
VALIDATE AND COMMIT IMMUTABLE RESULTS
DO NOT MOVE P5.1 EVENTS OR RETUNE P5.2 FEATURES AFTER RESULTS
DO NOT START P5.3 STATE-MODEL SELECTION UNTIL P5.2 EVIDENCE IS REVIEWABLE
DO NOT PRODUCTION-AUTHORIZE ANYTHING
```