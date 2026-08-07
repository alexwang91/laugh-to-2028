# BRRK Current State

Last updated: 2026-08-07
Status: authoritative cross-chat handoff snapshot

## Authoritative baseline

- P0 / P1 / P2: PASS / MERGED; Phases 0–2 complete
- P3.1 through P3.4: PASS / TESTED / CI VERIFIED / MERGED; **Phase 3 COMPLETE**
- P4.1 corrected 0–1 baseline freeze: PASS / TESTED / CI VERIFIED / MERGED
- `LEVERAGE-0039`: **STOPPED_PRE_RUN / NO_RESULT_EVER_PRODUCED / DO NOT REUSE**
- `LEVERAGE-0040`: **PREREGISTERED BEFORE FIRST RUN / TESTED / CI VERIFIED / MERGED / NOT RUN**
- Hyperliquid P4 margin snapshot: **CAPTURED / HASHED / TESTED / CI VERIFIED / MERGED**
- historical stale-main PR #70: INVALID / CLOSED / DO NOT REVIVE

## Current main and roadmap position

Post-correction normalization main:

`8d95810cd30fbce61fa7ed0234ac7e308aeb3a17`

Current draft PR:

`#86 — P4.3 two-layer runner wiring and cap=1 historical parity`

Validated initial checkpoint head:

`3aaacd8e2347e05238d8a8ad072876e959f73e77`

```text
P4.1 corrected 0-1 defensive baseline       PASS / MERGED
LEVERAGE-0039                               STOPPED_PRE_RUN / NO RESULT
LEVERAGE-0040 preregistration               PASS / MERGED / NOT RUN
P4 margin/liquidation metadata snapshot     PASS / MERGED
P4.3 two-layer composition module           IMPLEMENTED / TESTED / CI VERIFIED CANDIDATE
P4.3 cap=1 historical leverage parity       PASS / TESTED / CI VERIFIED CANDIDATE
P4.3 liquidation-distance implementation    NOT IMPLEMENTED
P4.3 >1 multiplier selection rule           NOT IMPLEMENTED
P4.4 preregistered stress execution         BLOCKED
P4.5 promotion/failure decision             BLOCKED
P4.6 deployment cap / production gate       BLOCKED
P5 exit intelligence                        BLOCKED
```

**LEVERAGE-0040 SEARCH RUN: NO. RESULT SELECTED: NO. OPERATING BUDGET FROZEN: NO. >1 PRODUCTION RUNTIME IMPLEMENTED: NO.**

## Corrected P4 architecture

Authoritative architecture:

```text
BRRK directional weights
× frozen defensive_scale in [0,1]
× separate leverage_multiplier in [1, research cap]
= final target economic exposure
```

The frozen defensive selector remains unchanged and strictly bounded to `[0,1]`.

Research-only candidate composition module:

`research/leverage_0040/two_layer_runner.py`

It deliberately does **not** choose a leverage multiplier. It only composes an already-frozen P3.2 target with an explicitly supplied research multiplier after validating:

- exact BTC/ETH/SOL/BNB target set;
- long-only base target;
- frozen base gross <=1;
- frozen defensive scale remains in `[0,1]`;
- multiplier remains in `[1,research_cap]`;
- `LEVERAGE-0040` cap remains <=1.30;
- no production authorization.

This prevents multiplier-selection economics from being smuggled into the cap=1 wiring gate.

## Cap=1 historical parity result

Dedicated workflow:

`P4.3 LEVERAGE-0040 cap1 parity`

Initial checkpoint run:

`31175967899` (#1): **SUCCESS**

The workflow executed only:

```text
research_cap        = 1.0
leverage_multiplier = 1.0
```

and explicitly reported:

```text
status                P4_3_CAP1_EXACT_HISTORICAL_PARITY_PASS
decision_count        6
leverage_search_run   false
production_authorized false
```

Historical decisions reproduced exactly:

- 2022-12-15 — RISK_OFF, defensive scale `1.3453862979240228e-07`;
- 2023-10-25 — MAJOR_ROTATION, `0.9999718626245347`;
- 2024-08-06 — BTC_LEAD, `0.9999984868728992`;
- 2025-04-10 — MAJOR_ROTATION, `0.9999999939549142`;
- 2025-11-15 — ALT_EXPANSION, `0.9881751992198149`;
- 2026-08-03 — RISK_OFF, `0.009600519865636481`.

For each decision, the new P4 boundary preserved:

- literal P3.2 target weights at multiplier 1;
- gross and cash/financing share;
- defensive scale;
- target/refit session;
- risk state;
- canonical data digest;
- committed historical golden vectors.

This is a baseline wiring/parity result only. It is **not** a leverage-search result and conveys no information about whether 1.10/1.20/1.30 is economically desirable.

## PR #86 initial checkpoint evidence

Head:

`3aaacd8e2347e05238d8a8ad072876e959f73e77`

- Phase 0 baseline contract `31175967400` (#142): **SUCCESS**, **243 passed in 7.54s**, 5/5 research integration OK
- Research evidence normalization `31175967978` (#48): **SUCCESS**
- P3.2 target research-live parity `31175967755` (#35): **SUCCESS**, independent parity + committed golden
- P4.3 cap=1 historical parity `31175967899` (#1): **SUCCESS**, six full-BRRK decisions, no >1 search
- PR handoff governance `31175967977` (#197): **SUCCESS**

The current handoff/checklist update must now receive final-head revalidation; previous runs are checkpoint evidence, not final-head merge evidence.

## LEVERAGE-0040 preregistered study

Frozen pre-run constraints remain:

```text
research caps                1.00 / 1.10 / 1.20 / 1.30
operating MDD candidates     35% / 40% / 45% / 50%
frozen defensive tail gate  20% CVaR/CDaR
transaction-cost grid        5 / 10 / 20 / 50 bps
catastrophic boundary        70%
```

Mandatory benchmarks:

1. BTC buy-and-hold;
2. BTC/ETH/SOL/BNB equal-weight buy-and-hold;
3. frozen corrected BRRK-0011 <=1 baseline;
4. P4 leverage candidates.

Mandatory stresses include historical windows, synthetic gap/volatility shocks, native funding debit spikes, degraded fill/depth/capacity and liquidation distance.

Funding remains exogenous implementation cost/stress only. F23 remains separate.

## Frozen Hyperliquid liquidation-input snapshot

`research/leverage_0039/hyperliquid_margin_snapshot.json`

```text
captured_at_utc      2026-08-07T09:11:25Z
relevant SHA-256     38060892f1976315084de4dc4ed1c9f3885d909ffccc47bce7ad589315d8b9dd
raw meta SHA-256     ef4b108e65806d05dab615f533dd113fd86210d2e55a82a005fcad89a7f9aff8
```

This is research liquidation-distance evidence only and authorizes no leverage.

## Explicit boundaries

Still forbidden:

- running/reusing `LEVERAGE-0039`;
- executing any `LEVERAGE-0040` >1 candidate before #86 merges and the remaining pre-run prerequisites are frozen;
- inventing a multiplier-selection rule after observing >1 results;
- production gross >1 / production leverage authorization;
- search >1.30 under `LEVERAGE-0040`;
- weakening/replacing the frozen defensive 20% scenario tail gate;
- EXPOSURE-SMOOTH-0038 promotion;
- F23 funding-response logic;
- shorts / XRP target exposure;
- P5 exit intelligence;
- historical BRRK overwrite.

Remaining pre-run prerequisites after cap=1 parity:

1. merge/freeze the cap=1 wiring implementation;
2. validate liquidation-distance implementation against the frozen Hyperliquid snapshot;
3. freeze the >1 multiplier-selection algorithm before any >1 observation;
4. only then execute the preregistered `LEVERAGE-0040` suite once.

## Production authorization

```text
NO_CHANGE
production_authorized_components = []
```

## Project drift audit

```text
DRIFT_0
```

## Exact next action

```text
revalidate final #86 branch head
-> update final PR evidence / mark ready
-> latest governance
-> expected-head squash merge #86
-> post-merge normalization
-> fresh P4.3 prerequisite branch
-> implement/validate liquidation-distance model against frozen Hyperliquid snapshot
-> freeze >1 multiplier-selection algorithm before first >1 result
-> only then execute LEVERAGE-0040 exactly once
```
