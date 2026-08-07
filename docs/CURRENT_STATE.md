# BRRK Current State

Last updated: 2026-08-07
Status: authoritative cross-chat handoff snapshot

## Authoritative baseline

- P0 / P1 / P2: PASS / MERGED; Phases 0–2 complete
- P3.1 through P3.4: PASS / TESTED / CI VERIFIED / MERGED; **Phase 3 COMPLETE**
- P4.1 corrected 0–1 baseline freeze: PASS / TESTED / CI VERIFIED / MERGED by PR #82
- P4.2 original `LEVERAGE-0039` preregistration: MERGED historically, now **STOPPED_PRE_RUN / NO_RESULT** after pre-run architecture review
- P4.2 replacement `LEVERAGE-0040`: **PREREGISTERED BEFORE FIRST RUN / CANDIDATE IN PR #84**
- historical stale-main PR #70: INVALID / CLOSED / DO NOT REVIVE

## Current main and candidate position

Current authoritative main after post-P4.1/P4.2 normalization:

`86045e6aefef81053fa8a9b624cbc4d9cb7a8c80`

Current draft candidate:

`PR #84 — p4-3/leverage-runner-v1`

```text
P4.1 preserve corrected 0-1 scaler             PASS / MERGED
P4.2 LEVERAGE-0039 prereg                       STOPPED_PRE_RUN / NO RESULT
P4.2 LEVERAGE-0040 replacement prereg           CANDIDATE / NOT RUN
P4.3 official Hyperliquid margin snapshot       CAPTURED / HASHED / CANDIDATE
P4.3 two-layer leverage runner                  NOT IMPLEMENTED
P4.3 cap=1 historical parity                    NOT RUN
P4.4 stress execution                           BLOCKED
P4.5 promotion decision                         BLOCKED
P4.6 deployment cap                             BLOCKED
P5 exit intelligence                            BLOCKED
```

**LEVERAGE SEARCH RUN: NO. RESULT SELECTED: NO. OPERATING BUDGET FROZEN: NO. >1 RUNTIME IMPLEMENTED: NO.**

## P4 architecture review correction

The Master Plan requires:

```text
BRRK directional weights
× frozen regime/risk defensive scaler
× optional leverage multiplier
= final target economic exposure
```

The original `LEVERAGE-0039` preregistration instead proposed extending the upper bound of the same corrected defensive selector from 1.0 to 1.10/1.20/1.30.

Pre-run review found this is not a safe equivalent under the frozen BRRK formula:

```text
meta_scale = corrected_selector(...)
defensive_scale = 1 - P(RISK_OFF) * (1 - meta_scale)
defensive_scale = clip(defensive_scale, 0, 1)
```

If `meta_scale > 1` remains clipped, leverage disappears. If the clip is removed, increasing `P(RISK_OFF)` can increase exposure. No leverage search had been run when this contradiction was found.

Therefore:

```text
LEVERAGE-0039 = STOPPED_PRE_RUN
result          = NO_RESULT_EVER_PRODUCED
reuse/rescue    = FORBIDDEN
```

This stop is a governance/architecture correction, not an adverse economic result.

## LEVERAGE-0040 preregistered replacement

Machine preregistration:

`research/leverage_0040/LEVERAGE-0040.json`

Frozen architecture:

```text
frozen defensive_scale ∈ [0,1]
leverage_multiplier     ∈ [1, candidate cap]
final_scale             = defensive_scale × leverage_multiplier
research caps           = 1.00 / 1.10 / 1.20 / 1.30
```

At cap 1.00 the multiplier is identically 1.0, so exact frozen BRRK parity is structurally mandatory before any >1 candidate is valid.

Unchanged risk/search constraints:

```text
operating MDD candidates   35% / 40% / 45% / 50%
frozen scenario tail gate  20% CVaR/CDaR
transaction costs           5 / 10 / 20 / 50 bps
catastrophic boundary       70%
search above 1.30           forbidden without new experiment ID
```

Mandatory benchmarks now explicitly include:

1. BTC buy-and-hold;
2. BTC/ETH/SOL/BNB equal-weight buy-and-hold;
3. frozen corrected BRRK-0011 <=1 baseline.

Mandatory stress coverage now explicitly includes:

- historical 2021/2022/2024/2025/2026 windows;
- synthetic gap and volatility shocks;
- Hyperliquid native funding stress with 2x/3x/5x debit multipliers;
- degraded depth/slippage and partial-fill/capacity scenarios;
- liquidation-distance evidence using the frozen official Hyperliquid margin snapshot.

Funding remains exogenous implementation cost only. It is not alpha, a filter or an allocation threshold. F23 remains separate.

## Hyperliquid liquidation-input snapshot

PR #84 captured official mainnet `/info {"type":"meta"}` evidence before any leverage search.

Committed candidate artifact:

`research/leverage_0039/hyperliquid_margin_snapshot.json`

Frozen relevant hash:

`38060892f1976315084de4dc4ed1c9f3885d909ffccc47bce7ad589315d8b9dd`

Frozen raw-meta hash:

`ef4b108e65806d05dab615f533dd113fd86210d2e55a82a005fcad89a7f9aff8`

Relevant current captured tiers:

```text
BTC  table 56   40x -> 20x at 150M
ETH  table 55   25x -> 15x at 100M
SOL  table 54   20x -> 10x at 70M
BNB  table 51   10x -> 5x at 3M
```

This is research liquidation-distance input evidence only and does not authorize leverage.

## Production authorization

```text
NO_CHANGE
production_authorized_components = []
```

## Project drift audit

Architecture review discovered a temporary P4 design mismatch and missing benchmark/stress prereg coverage:

```text
DISCOVERY: DRIFT_2
```

The candidate correction in PR #84 is intended to restore:

```text
POST-CORRECTION TARGET: DRIFT_0
```

No phase ordering, asset universe, production authorization, human-control boundary, wallet/security boundary, F23 boundary, P5 boundary or historical BRRK authority was violated.

## Exact next action

```text
validate PR #84 preregistration correction
-> merge only after contract/governance CI passes
-> fresh P4.3 runner branch from new main
-> implement separate post-defensive leverage multiplier
-> cap=1 exact historical parity
-> only then execute LEVERAGE-0040 exactly once
-> P4.4 stress suite / P4.5 decision / P4.6 deployment gate
```
