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
- P4.3 two-layer composition + cap=1 historical parity: **PASS / TESTED / CI VERIFIED / MERGED by PR #86**

## Current main and candidate

Normalized main after PR #87:

`6ba3f765fd52839e9841b299aab4a51c9a1cd523`

Current fresh prerequisite branch:

`p4-3/leverage-0040-pre-run-prereqs-v1`

```text
P4.3 liquidation-distance model             IMPLEMENTED CANDIDATE / CI PENDING
P4.3 >1 multiplier policy freeze            IMPLEMENTED CANDIDATE / CI PENDING
LEVERAGE-0040 >1 search                     NOT RUN
P4.4 stress execution                       BLOCKED
P4.5 selection/failure decision             BLOCKED
P4.6 deployment/production gate             BLOCKED
P5 exit intelligence                        BLOCKED
```

**SEARCH RUN: NO. RESULT SELECTED: NO. OPERATING BUDGET FROZEN: NO. PRODUCTION >1 AUTHORIZATION: NO.**

## Corrected two-layer architecture

```text
BRRK directional weights
× frozen defensive_scale in [0,1]
× separate leverage_multiplier
= final target economic exposure
```

The frozen defensive selector remains unchanged. P4 never extends it above 1.0.

## Cap=1 gate already merged

PR #86 final head:

`8f2f0bd0a77d1267e21a28f49b3abe359b8012cb`

Final evidence:

- Phase 0 `31176241468` (#144): SUCCESS, 243 passed + 5/5 integration
- Research evidence `31176241499` (#50): SUCCESS
- P3.2 parity/golden `31176241450` (#37): SUCCESS
- P4 cap=1 parity `31176241424` (#3): SUCCESS
- latest governance `31176460514` (#201): SUCCESS
- merge `ad560ada135cf556be24fa3ce62eb5a7a74cfeb5`

The P4 parity gate used only `research_cap=1.0` and `leverage_multiplier=1.0`, reproduced six committed full-BRRK decisions, and reported `leverage_search_run=false` / `production_authorized=false`.

## Frozen Hyperliquid margin evidence

`research/leverage_0039/hyperliquid_margin_snapshot.json`

```text
captured_at_utc      2026-08-07T09:11:25Z
relevant SHA-256     38060892f1976315084de4dc4ed1c9f3885d909ffccc47bce7ad589315d8b9dd
raw meta SHA-256     ef4b108e65806d05dab615f533dd113fd86210d2e55a82a005fcad89a7f9aff8
BTC                  table 56: 40x -> 20x @150M
ETH                  table 55: 25x -> 15x @100M
SOL                  table 54: 20x -> 10x @70M
BNB                  table 51: 10x -> 5x @3M
```

## Candidate liquidation model — pre-result

Machine contract:

`research/leverage_0040/P4_3_LIQUIDATION_MODEL_V1.json`

Implementation:

`research/leverage_0040/liquidation_model.py`

Scope is deliberately **standard Hyperliquid cross margin only** for this study version. Portfolio Margin and isolated margin are not assumed.

Frozen equations follow Hyperliquid official semantics:

```text
MMR(tier) = 1 / (2 × tier max leverage)
maintenance_margin = stressed_notional × MMR - maintenance_deduction
cross liquidation when stressed account equity <= total maintenance margin
```

Tier deduction is recursively calculated to keep maintenance margin continuous across lower bounds. The model reads tiers only from the frozen pre-result snapshot.

Required explicit inputs:

- current cross-account equity in USDC terms;
- actual cross-margin perp notionals from the implementation plan;
- frozen margin snapshot.

It does **not** assume ordinary spot balances are cross collateral or that Portfolio Margin is enabled. Missing route/collateral accounting fails closed.

Validation contract includes:

- frozen tier/MMR checks for BTC/ETH/SOL/BNB;
- maintenance continuity at every tier boundary;
- single-position first-tier distance matching Hyperliquid's published liquidation-price formula;
- cross-asset maintenance/PnL aggregation;
- deterministic stress-ray bisection;
- malformed/unsupported inputs fail closed.

No liquidation result for a >1 historical candidate has been generated yet.

## Candidate multiplier policy freeze — pre-result

Addendum:

`research/leverage_0040/LEVERAGE-0040-PRE-RUN-ADDENDUM-V1.json`

Implementation:

`research/leverage_0040/multiplier_policy.py`

Frozen policy ID:

`P4.3-DEFENSIVE-MONOTONE-MULTIPLIER-V1`

Formula:

```text
leverage_multiplier = 1 + (candidate_cap - 1) × frozen_defensive_scale
final_scale = defensive_scale + (candidate_cap - 1) × defensive_scale²
```

Allowed inputs are **only**:

```text
frozen_defensive_scale
candidate_research_cap ∈ {1.00, 1.10, 1.20, 1.30}
```

Properties frozen before first >1 observation:

- cap=1 is exact identity;
- defensive scale 0 keeps final scale 0;
- extra leverage fades continuously as defensive risk reduction increases;
- no thresholds or second alpha model;
- candidate cap is reached only at defensive scale 1;
- final gross cannot exceed candidate cap because P3.2 base gross <=1;
- no funding signal, raw HMM-state tuning, P5 logic, 0038, short/XRP target or historical-result-selected threshold.

No 1.10/1.20/1.30 historical result existed before this policy freeze.

## Dedicated candidate CI

`.github/workflows/p4-3-pre-run-prereqs.yml`

It runs only the liquidation-model and multiplier-policy contract tests. It does not run the LEVERAGE-0040 historical >1 search.

Full Phase 0, P3.2 parity/golden, P4 cap=1 parity and governance must also remain green before merge.

## LEVERAGE-0040 study constraints unchanged

```text
research caps                1.00 / 1.10 / 1.20 / 1.30
operating MDD candidates     35% / 40% / 45% / 50%
frozen defensive tail gate  20% CVaR/CDaR
transaction-cost grid        5 / 10 / 20 / 50 bps
catastrophic boundary        70%
```

Mandatory benchmarks remain BTC buy-and-hold, four-asset equal-weight buy-and-hold, frozen BRRK <=1 and P4 candidates. Mandatory stresses remain historical windows, synthetic gaps/volatility, native funding debit spikes, degraded fill/depth/capacity and liquidation distance.

## Explicit boundaries

Still forbidden:

- run/reuse `LEVERAGE-0039`;
- run any 1.10/1.20/1.30 historical candidate on this prerequisite branch;
- change multiplier formula after observing >1 results;
- assume spot collateral or Portfolio Margin without a separately frozen implementation model;
- production gross >1 / leverage authorization;
- search >1.30 under 0040;
- weaken frozen 20% defensive tail gate;
- promote EXPOSURE-SMOOTH-0038;
- absorb F23 funding-response logic;
- shorts / XRP targets;
- P5 exit intelligence.

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
open prerequisite PR
-> dedicated prerequisite CI + Phase 0 + P3.2 parity + P4 cap=1 + governance
-> fix same PR if needed
-> final-head validation
-> merge + post-merge normalization
-> only then create fresh LEVERAGE-0040 search branch
-> execute preregistered 0040 suite exactly once
```
