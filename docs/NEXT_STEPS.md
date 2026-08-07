# Next Steps

> Read canonical sources in repository-defined order. GitHub actual state wins over stale prose.

## Current dependency

```text
P4.3 remaining pre-run prerequisites:
1. liquidation-distance implementation/validation
2. freeze >1 multiplier-selection algorithm before first >1 result
```

PR #86 merged the two-layer composition and mandatory cap=1 historical identity gate as:

`ad560ada135cf556be24fa3ce62eb5a7a74cfeb5`

## Frozen authority

```text
P4.1 defensive scaler       frozen 0 .. 1; unchanged
LEVERAGE-0039              STOPPED_PRE_RUN / NO RESULT / DO NOT REUSE
LEVERAGE-0040              PREREGISTERED / MERGED / NOT RUN
two-layer cap=1 wiring     PASS / MERGED
production gross cap       1.0 unchanged
production authorization   none
```

`production_authorized_components = []` remains unchanged.

## LEVERAGE-0040 architecture

```text
BRRK directional weights
× frozen defensive_scale in [0,1]
× separate leverage_multiplier in [1, candidate cap]
= final target economic exposure
```

The frozen defensive selector may not be extended or reinterpreted above 1.0.

## Cap=1 gate closed

PR #86 final head `8f2f0bd0a77d1267e21a28f49b3abe359b8012cb`:

- Phase 0 #144 / `31176241468`: SUCCESS, 243 passed + 5/5 integration
- Research evidence #50 / `31176241499`: SUCCESS
- P3.2 parity/golden #37 / `31176241450`: SUCCESS
- P4.3 cap=1 parity #3 / `31176241424`: SUCCESS
- latest governance #201 / `31176460514`: SUCCESS
- merge `ad560ada135cf556be24fa3ce62eb5a7a74cfeb5`

The dedicated P4 gate executed only `research_cap=1.0` and `leverage_multiplier=1.0`, reproduced six committed full-BRRK historical decisions, and explicitly reported `leverage_search_run=false` and `production_authorized=false`.

This closes wiring parity only. It provides no >1 economic result.

## Remaining prerequisite 1 — liquidation distance

Frozen Hyperliquid snapshot:

`research/leverage_0039/hyperliquid_margin_snapshot.json`

```text
captured_at_utc      2026-08-07T09:11:25Z
relevant SHA-256     38060892f1976315084de4dc4ed1c9f3885d909ffccc47bce7ad589315d8b9dd
raw meta SHA-256     ef4b108e65806d05dab615f533dd113fd86210d2e55a82a005fcad89a7f9aff8
```

Next implementation must convert the frozen margin tables into deterministic liquidation-distance calculations for BTC/ETH/SOL/BNB and fail closed on unsupported/malformed tier semantics. It must be research-only and must not change production leverage.

## Remaining prerequisite 2 — freeze multiplier-selection algorithm

Before observing any 1.10/1.20/1.30 result, define in machine-readable form how the separate leverage multiplier is selected under a candidate cap.

The algorithm must:

- act after the frozen defensive target;
- preserve risk-off monotonicity;
- use no new alpha/funding signal/P5 logic;
- stay within the preregistered candidate cap;
- remain deterministic and preregistered;
- not be selected by inspecting which historical >1 result looks best.

No >1 search may run merely because cap=1 parity passed.

## LEVERAGE-0040 frozen study gates

```text
research caps                1.00 / 1.10 / 1.20 / 1.30
operating MDD candidates     35% / 40% / 45% / 50%
frozen defensive tail gate  20% CVaR/CDaR
cost grid                    5 / 10 / 20 / 50 bps
catastrophe boundary         70%
```

Mandatory benchmarks:

- BTC buy-and-hold;
- BTC/ETH/SOL/BNB equal-weight buy-and-hold;
- frozen corrected BRRK-0011 <=1;
- P4 leverage candidates.

Mandatory stresses:

- preregistered historical windows;
- synthetic gap/volatility shocks;
- Hyperliquid native funding debit 2x/3x/5x stress;
- degraded depth/slippage and partial-fill/capacity stress;
- liquidation distance from frozen Hyperliquid metadata.

Funding remains implementation cost/stress only. F23 is separate.

## Still blocked

```text
LEVERAGE-0040 SEARCH RUN:       NO
RESULT SELECTED:                NO
OPERATING BUDGET FROZEN:        NO
LIQUIDATION MODEL VALIDATED:    NO
>1 SELECTION ALGORITHM FROZEN:  NO
>1 PRODUCTION RUNTIME:          NO
PRODUCTION AUTHORIZED:          NO_CHANGE
```

Also blocked/separate:

- search >1.30 without a new experiment ID;
- EXPOSURE-SMOOTH-0038 promotion;
- F23 funding-response redesign;
- shorts / XRP target exposure;
- P5 exit intelligence;
- production leverage authorization.

## Project drift audit

```text
DRIFT_0
```

## Exact next action

```text
merge post-#86 normalization
-> fresh P4.3 prerequisite branch from normalized main
-> implement/validate liquidation-distance model
-> freeze >1 multiplier-selection algorithm before observing any >1 result
-> full CI/governance
-> only then execute LEVERAGE-0040 exactly once
```
