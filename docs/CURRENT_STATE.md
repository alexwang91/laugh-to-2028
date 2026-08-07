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

Current candidate branch:

`p4-3/leverage-0040-runner-v1`

```text
P4.1 corrected 0-1 defensive baseline       PASS / MERGED
LEVERAGE-0039                               STOPPED_PRE_RUN / NO RESULT
LEVERAGE-0040 preregistration               PASS / MERGED / NOT RUN
P4 margin/liquidation metadata snapshot     PASS / MERGED
P4.3 two-layer composition module           IMPLEMENTED CANDIDATE
P4.3 cap=1 historical leverage parity       IMPLEMENTED / CI PENDING
P4.3 >1 multiplier selection rule           NOT IMPLEMENTED
P4.4 preregistered stress execution         BLOCKED UNTIL CAP=1 PARITY
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

## Cap=1 historical parity gate

Candidate gate:

`research/leverage_0040/p4_3_cap1_parity.py`

CI workflow:

`.github/workflows/p4-3-cap1-parity.yml`

The gate is executable only with:

```text
research_cap        = 1.0
leverage_multiplier = 1.0
```

It regenerates the six committed full-BRRK historical decisions through the canonical P3.1/P3.2 path, passes each frozen target through the new two-layer composition boundary, and requires:

- literal cap=1 target-weight identity versus P3.2 output;
- gross/cash/defensive identity;
- unchanged target/refit sessions, risk state and data digest;
- match to immutable `research/results/p3_2_target_parity/golden_v1.json`.

Until this workflow is green, every >1 candidate remains invalid and blocked.

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
- evaluating any `LEVERAGE-0040` >1 candidate before cap=1 exact historical parity passes;
- inventing a multiplier-selection rule from observed >1 results;
- production gross >1 / production leverage authorization;
- search >1.30 under `LEVERAGE-0040`;
- weakening/replacing the frozen defensive 20% scenario tail gate;
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
open P4.3 runner/cap1 candidate PR
-> Phase 0 + P3.2 parity/golden + dedicated P4 cap1 parity + governance
-> fix any implementation/parity issue in same PR
-> only after cap=1 exact historical parity is merged may the >1 multiplier-selection algorithm be frozen
-> no LEVERAGE-0040 search before that gate
```
