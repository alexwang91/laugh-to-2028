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
- P4.3 two-layer composition + cap=1 historical parity: **PASS / TESTED / CI VERIFIED / MERGED BY PR #86**
- historical stale-main PR #70: INVALID / CLOSED / DO NOT REVIVE

## Current main and roadmap position

PR #86 expected-head squash merge:

`ad560ada135cf556be24fa3ce62eb5a7a74cfeb5`

```text
P4.1 corrected 0-1 defensive baseline       PASS / MERGED
LEVERAGE-0039                               STOPPED_PRE_RUN / NO RESULT
LEVERAGE-0040 preregistration               PASS / MERGED / NOT RUN
P4 margin/liquidation metadata snapshot     PASS / MERGED
P4.3 two-layer composition                  PASS / MERGED
P4.3 cap=1 historical parity                PASS / MERGED
P4.3 liquidation-distance implementation    UNIQUE NEXT PREREQUISITE
P4.3 >1 multiplier-selection algorithm      BLOCKED UNTIL PRE-RUN FREEZE
P4.4 LEVERAGE-0040 search/stress execution  BLOCKED
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

Merged research-only composition:

`research/leverage_0040/two_layer_runner.py`

It does not choose the multiplier. It composes an already-frozen P3.2 target with an explicitly supplied research multiplier and enforces long-only/four-asset/base-gross/defensive-scale/cap boundaries. No product runtime imports this research module.

## Cap=1 historical parity — merged

Dedicated workflow:

`P4.3 LEVERAGE-0040 cap1 parity`

PR #86 final head:

`8f2f0bd0a77d1267e21a28f49b3abe359b8012cb`

Final evidence:

- Phase 0 baseline contract `31176241468` (#144): **SUCCESS**, **243 passed in 7.60s**, 5/5 research integration OK
- Research evidence normalization `31176241499` (#50): **SUCCESS**
- P3.2 target research-live parity `31176241450` (#37): **SUCCESS**, independent parity + committed golden
- P4.3 cap=1 parity `31176241424` (#3): **SUCCESS**
- latest metadata/ready governance `31176460514` (#201): **SUCCESS**
- expected-head squash merge: `ad560ada135cf556be24fa3ce62eb5a7a74cfeb5`

The P4 cap=1 gate executed only:

```text
research_cap        = 1.0
leverage_multiplier = 1.0
```

and reported:

```text
status                P4_3_CAP1_EXACT_HISTORICAL_PARITY_PASS
decision_count        6
leverage_search_run   false
production_authorized false
```

It reproduced six committed full-BRRK historical decisions spanning RISK_OFF, BTC_LEAD, MAJOR_ROTATION and ALT_EXPANSION and preserved target weights, gross/cash, defensive scale, sessions, risk state, canonical data digest and committed golden vectors.

This proves the new P4 wiring is an identity at cap=1. It is **not** evidence that any >1 multiplier is economically valid.

## LEVERAGE-0040 frozen preregistration

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

## Frozen Hyperliquid liquidation inputs

`research/leverage_0039/hyperliquid_margin_snapshot.json`

```text
captured_at_utc      2026-08-07T09:11:25Z
relevant SHA-256     38060892f1976315084de4dc4ed1c9f3885d909ffccc47bce7ad589315d8b9dd
raw meta SHA-256     ef4b108e65806d05dab615f533dd113fd86210d2e55a82a005fcad89a7f9aff8
```

Captured tiers:

```text
BTC  table 56   40x -> 20x at 150M
ETH  table 55   25x -> 15x at 100M
SOL  table 54   20x -> 10x at 70M
BNB  table 51   10x -> 5x at 3M
```

The next prerequisite is to turn this frozen metadata into a tested liquidation-distance model. Missing or ambiguous margin semantics must fail closed.

## Remaining pre-run prerequisites

Before the first `LEVERAGE-0040` >1 search:

1. implement and validate liquidation-distance calculation against the frozen Hyperliquid snapshot;
2. freeze the >1 multiplier-selection algorithm in machine-readable form **before any >1 result is observed**;
3. rerun governance/tests showing these are pre-result inputs;
4. only then execute the preregistered 0040 candidate/stress suite once with no post-result retuning.

## Explicit boundaries

Still forbidden:

- running/reusing `LEVERAGE-0039`;
- running any >1 `LEVERAGE-0040` candidate before the remaining prerequisites are merged;
- choosing or changing the multiplier algorithm after observing >1 results;
- production gross >1 / production leverage authorization;
- search >1.30 under `LEVERAGE-0040`;
- weakening the frozen defensive 20% scenario tail gate;
- EXPOSURE-SMOOTH-0038 promotion;
- F23 funding-response logic;
- shorts / XRP target exposure;
- P5 exit intelligence;
- historical BRRK overwrite.

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
merge this docs-only post-#86 normalization
-> verify new main
-> fresh P4.3 prerequisite branch
-> implement/validate liquidation-distance model from frozen Hyperliquid snapshot
-> freeze >1 multiplier-selection algorithm before first >1 observation
-> CI/governance
-> only then execute LEVERAGE-0040 exactly once
```
