# BRRK Current State

Last updated: 2026-08-07
Status: authoritative cross-chat handoff snapshot

## Authoritative baseline

- P0/P1/P2: PASS / MERGED; Phases 0–2 complete
- P3.1–P3.4: PASS / TESTED / CI VERIFIED / MERGED; **Phase 3 COMPLETE**
- P4.1 corrected defensive scaler: PASS / MERGED; frozen strictly to `[0,1]`
- `LEVERAGE-0039`: **STOPPED_PRE_RUN / NO_RESULT_EVER_PRODUCED / DO NOT REUSE**
- `LEVERAGE-0040`: **PREREGISTERED / MERGED / NOT RUN**
- official Hyperliquid margin snapshot: **CAPTURED / HASHED / MERGED**
- P4.3 two-layer composition + cap=1 historical parity: **PASS / TESTED / CI VERIFIED / MERGED**
- P4.3 liquidation-distance model: **PASS / TESTED / CI VERIFIED / MERGED by PR #88**
- P4.3 defensive-monotone multiplier policy: **FROZEN PRE-RESULT / TESTED / CI VERIFIED / MERGED by PR #88**

## Current main and roadmap position

PR #88 expected-head squash merge:

`8d512479c5b2a0522409afbf0b63b817de6c6fe0`

```text
P4.1 corrected <=1 baseline                 PASS / MERGED
LEVERAGE-0039                               STOPPED_PRE_RUN / NO RESULT
LEVERAGE-0040 preregistration               PASS / MERGED / NOT RUN
P4 margin snapshot                          PASS / MERGED
P4.3 two-layer composition                  PASS / MERGED
P4.3 cap=1 historical parity                PASS / MERGED
P4.3 liquidation-distance model             PASS / MERGED
P4.3 >1 multiplier policy freeze            PASS / MERGED / NO RESULT OBSERVED
P4.4 LEVERAGE-0040 one-time search/stress   UNIQUE NEXT
P4.5 promotion/failure decision             BLOCKED UNTIL RESULTS
P4.6 deployment/production gate             BLOCKED
P5 exit intelligence                        BLOCKED
```

**LEVERAGE-0040 SEARCH RUN: NO. RESULT SELECTED: NO. OPERATING BUDGET FROZEN: NO. PRODUCTION >1 AUTHORIZATION: NO.**

## Frozen P4 architecture

```text
BRRK directional weights
× frozen defensive_scale in [0,1]
× leverage_multiplier
= final target economic exposure
```

Multiplier policy frozen before any >1 result:

```text
leverage_multiplier = 1 + (candidate_cap - 1) × frozen_defensive_scale
final_scale = defensive_scale + (candidate_cap - 1) × defensive_scale²
candidate caps = 1.00 / 1.10 / 1.20 / 1.30
```

The policy uses only frozen defensive scale and candidate cap. It has no result-selected threshold, funding signal, raw HMM retune, P5 input, 0038 input, short/XRP target input, or production authorization.

## Frozen liquidation model

Contract:

`research/leverage_0040/P4_3_LIQUIDATION_MODEL_V1.json`

Implementation:

`research/leverage_0040/liquidation_model.py`

Scope: standard Hyperliquid cross margin only, using frozen snapshot `research/leverage_0039/hyperliquid_margin_snapshot.json`.

```text
MMR = 1 / (2 × tier max leverage)
maintenance = stressed notional × MMR - tier deduction
liquidation when cross-account equity <= total maintenance margin
```

Explicit cross-account equity and actual perp notionals are required. Ordinary spot collateral and Portfolio Margin are not assumed; missing accounting fails closed.

## PR #88 final evidence

Final head:

`9ed8c627afd9800f8c4a8cf79246a07bc89e6108`

- dedicated prerequisite `31178219708` (#4): **SUCCESS**, 14 passed
- Phase 0 `31178220870` (#149): **SUCCESS**, 257 passed in 8.12s + 5/5 research integration
- Research evidence `31178223443` (#55): **SUCCESS**
- P3.2 parity/golden `31178219593` (#42): **SUCCESS**
- P4 cap=1 parity `31178220456` (#8): **SUCCESS**
- latest metadata/ready governance `31178603896` (#209): **SUCCESS**
- expected-head squash merge `8d512479c5b2a0522409afbf0b63b817de6c6fe0`

No 1.10/1.20/1.30 historical candidate was produced before these semantics were frozen.

## LEVERAGE-0040 frozen study gates

```text
research caps                1.00 / 1.10 / 1.20 / 1.30
operating MDD candidates     35% / 40% / 45% / 50%
frozen defensive tail gate  20% CVaR/CDaR
transaction-cost grid        5 / 10 / 20 / 50 bps
catastrophic boundary        70%
```

Mandatory benchmarks: BTC buy-and-hold, BTC/ETH/SOL/BNB equal-weight buy-and-hold, frozen BRRK <=1, and P4 candidates.

Mandatory stresses: preregistered historical windows, synthetic gaps/volatility, native funding debit spikes, degraded fills/depth/capacity, and liquidation distance.

## Explicit boundaries

Still forbidden:

- running/reusing `LEVERAGE-0039`;
- altering preregistered 0040 caps/budgets/stress windows/policy after seeing results;
- changing the frozen defensive selector or 20% tail gate;
- search above 1.30 under 0040;
- EXPOSURE-SMOOTH-0038 promotion;
- F23 funding-response logic;
- shorts / XRP target exposure;
- P5 exit intelligence;
- production gross >1 / production leverage authorization.

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
merge this docs-only post-#88 normalization
-> verify new main
-> fresh LEVERAGE-0040 search branch
-> implement the preregistered result runner without changing frozen inputs/policies
-> execute the complete LEVERAGE-0040 suite exactly once
-> preserve full candidate/stress/benchmark result matrix
-> P4.5 select/fail decision with no post-result retuning
-> P4.6 separate deployment/production authorization gate
```
