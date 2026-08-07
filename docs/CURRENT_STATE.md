# BRRK Current State

Last updated: 2026-08-07
Status: authoritative cross-chat handoff snapshot

## Authoritative baseline

- P0 / P1 / P2: PASS / MERGED; Phases 0–2 complete
- P3.1 through P3.4: PASS / TESTED / CI VERIFIED / MERGED; **Phase 3 COMPLETE**
- P4.1 corrected 0–1 baseline freeze: PASS / TESTED / CI VERIFIED / MERGED
- `LEVERAGE-0039`: **STOPPED_PRE_RUN / NO_RESULT_EVER_PRODUCED / DO NOT REUSE**
- `LEVERAGE-0040`: **PREREGISTERED BEFORE FIRST RUN / TESTED / CI VERIFIED / MERGED BY PR #84 / NOT RUN**
- Hyperliquid P4 margin snapshot: **CAPTURED / HASHED / TESTED / CI VERIFIED / MERGED BY PR #84**
- historical stale-main PR #70: INVALID / CLOSED / DO NOT REVIVE

## Current main and roadmap position

PR #84 expected-head squash merge:

`5cfc7996ef59cc6552d1ec5bdfbc74affdaf53b4`

```text
P4.1 corrected 0-1 defensive baseline       PASS / MERGED
LEVERAGE-0039                               STOPPED_PRE_RUN / NO RESULT
LEVERAGE-0040 preregistration               PASS / MERGED / NOT RUN
P4 margin/liquidation metadata snapshot     PASS / MERGED
P4.3 two-layer leverage runner              UNIQUE NEXT IMPLEMENTATION
P4.3 cap=1 historical leverage parity       BLOCKED UNTIL RUNNER
P4.4 preregistered stress execution         BLOCKED UNTIL CAP=1 PARITY
P4.5 promotion/failure decision             BLOCKED
P4.6 deployment cap / production gate       BLOCKED
P5 exit intelligence                        BLOCKED
```

**LEVERAGE-0040 SEARCH RUN: NO. RESULT SELECTED: NO. OPERATING BUDGET FROZEN: NO. >1 RUNTIME IMPLEMENTED: NO.**

## Corrected P4 architecture

The Master Plan architecture is restored and authoritative:

```text
BRRK directional weights
× frozen defensive_scale in [0,1]
× separate leverage_multiplier in [1, research cap]
= final target economic exposure
```

The frozen defensive selector remains unchanged and strictly bounded to `[0,1]`. It must not be generalized above 1.0.

`LEVERAGE-0040` preregisters:

```text
research caps                1.00 / 1.10 / 1.20 / 1.30
operating MDD candidates     35% / 40% / 45% / 50%
frozen defensive tail gate  20% CVaR/CDaR
transaction-cost grid        5 / 10 / 20 / 50 bps
catastrophic boundary        70%
```

At cap 1.00 the leverage multiplier is identically 1.0; complete historical frozen-BRRK parity is mandatory before any >1 candidate may be evaluated.

Mandatory result comparisons include:

1. BTC buy-and-hold;
2. BTC/ETH/SOL/BNB equal-weight buy-and-hold;
3. frozen corrected BRRK-0011 <=1 baseline;
4. preregistered P4 leverage candidates.

Mandatory stress coverage includes historical windows, synthetic gap/volatility shocks, Hyperliquid native funding debit spikes, degraded fill/depth/capacity scenarios and liquidation-distance checks.

Funding remains exogenous cost/stress only. F23 remains separate.

## Hyperliquid liquidation-input snapshot

Frozen artifact:

`research/leverage_0039/hyperliquid_margin_snapshot.json`

```text
captured_at_utc      2026-08-07T09:11:25Z
relevant SHA-256     38060892f1976315084de4dc4ed1c9f3885d909ffccc47bce7ad589315d8b9dd
raw meta SHA-256     ef4b108e65806d05dab615f533dd113fd86210d2e55a82a005fcad89a7f9aff8
```

Captured relevant tiers:

```text
BTC  table 56   40x -> 20x at 150M
ETH  table 55   25x -> 15x at 100M
SOL  table 54   20x -> 10x at 70M
BNB  table 51   10x -> 5x at 3M
```

This evidence is for research liquidation-distance modeling only and authorizes no leverage.

## PR #84 final evidence

Final head:

`19711b85d3ab4bf1abae28dfd25926a7e682d6d2`

- Phase 0 run `31174963182` (#140): **SUCCESS**; final-head execution/research-integration contract green; prior same-content checkpoint measured 235 passed + 5/5 integration
- Research evidence run `31174960649` (#46): **SUCCESS**
- P3.2 parity/golden run `31174960611` (#33): **SUCCESS**, independent parity + committed historical goldens
- P4.3 margin snapshot run `31174960599` (#15): **SUCCESS**
- latest metadata/ready governance run `31175158261` (#194): **SUCCESS**
- expected-head squash merge: `5cfc7996ef59cc6552d1ec5bdfbc74affdaf53b4`

The pre-run audit discovery was `DRIFT_2`; validated correction returned the repository architecture to `DRIFT_0` before any leverage result was produced.

## Explicit boundaries

Still forbidden:

- running or reusing `LEVERAGE-0039`;
- running `LEVERAGE-0040` before cap=1 exact historical parity;
- production gross >1 or production leverage authorization;
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
merge this docs-only normalization
-> verify new main
-> fresh P4.3 LEVERAGE-0040 runner branch
-> implement separate post-defensive leverage multiplier
-> prove cap=1 exact historical parity
-> validate liquidation-distance implementation against frozen Hyperliquid snapshot
-> only then execute LEVERAGE-0040 exactly once
-> P4.4 stress suite
-> P4.5 select/fail
-> P4.6 separate deployment/production authorization gate
```
