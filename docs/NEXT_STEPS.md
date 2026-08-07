# Next Steps

> Read canonical sources in repository-defined order. GitHub actual state wins over stale prose.

## Current dependency

```text
P4.3 pre-run architecture correction in draft PR #84
```

Current authoritative main after PR #83:

`86045e6aefef81053fa8a9b624cbc4d9cb7a8c80`

## What changed in pre-run review

The Master Plan defines dynamic leverage as two layers:

```text
BRRK directional weights
× frozen 0-1 regime/risk defensive scaler
× separate leverage multiplier
= final target economic exposure
```

The merged `LEVERAGE-0039` preregistration had instead proposed extending the corrected defensive selector itself above 1.0. Review found that this is not equivalent under the frozen BRRK defensive formula: keeping the final clip removes >1 leverage, while removing the clip can make higher RISK_OFF probability increase exposure.

No leverage search or result had been produced.

Therefore:

```text
LEVERAGE-0039   STOPPED_PRE_RUN / NO_RESULT_EVER_PRODUCED
LEVERAGE-0040   PREREGISTERED CANDIDATE / NOT RUN
```

Do not rescue or reuse 0039. The corrected architecture receives the new experiment ID 0040.

## LEVERAGE-0040 frozen pre-run architecture

Machine preregistration:

`research/leverage_0040/LEVERAGE-0040.json`

```text
defensive_scale              frozen 0 .. 1
leverage multiplier          1 .. selected research cap
final scale                  defensive_scale × leverage_multiplier
research caps                1.00 / 1.10 / 1.20 / 1.30
operating MDD candidates     35% / 40% / 45% / 50%
scenario tail budget         frozen 20%
transaction-cost grid        5 / 10 / 20 / 50 bps
catastrophe boundary         70%
```

`cap=1.00` means the leverage multiplier is exactly `1.0`; the complete historical path must therefore reproduce frozen BRRK before any >1 candidate may be evaluated.

## Mandatory comparison set

Every material 0040 result must report:

```text
BTC buy-and-hold
BTC/ETH/SOL/BNB equal-weight buy-and-hold
frozen corrected BRRK-0011 <=1 baseline
P4 leverage candidates
```

Matched windows and clearly labeled cost/metric conventions are mandatory.

## Mandatory P4 stress coverage

0040 preregisters:

- 2021 spring crash;
- 2021 November/bear transition;
- 2022 severe drawdown;
- 2024 identified stress;
- 2025 full multi-peak/deleveraging year;
- recent 2026 window;
- synthetic -10/-20/-30/-40/-50% one-day gaps;
- cross-asset crash scenarios;
- 1.5x/2x/3x volatility shocks;
- Hyperliquid native funding debit stress at 2x/3x/5x;
- degraded depth/slippage scenarios;
- partial-fill/capacity stress using P2 fail-closed semantics;
- liquidation-distance checks against the captured official Hyperliquid margin snapshot.

Funding remains cost-only. No funding alpha/filter/threshold is allowed; F23 remains separate.

## Hyperliquid margin snapshot already captured

Candidate artifact in PR #84:

`research/leverage_0039/hyperliquid_margin_snapshot.json`

```text
relevant SHA-256  38060892f1976315084de4dc4ed1c9f3885d909ffccc47bce7ad589315d8b9dd
raw meta SHA-256  ef4b108e65806d05dab615f533dd113fd86210d2e55a82a005fcad89a7f9aff8
```

This snapshot is reusable evidence for 0040 because it was captured before any leverage result and its content is independent of the stopped selector architecture.

## Still blocked

```text
LEVERAGE-0040 SEARCH RUN:     NO
RESULT SELECTED:              NO
OPERATING BUDGET FROZEN:      NO
>1 RUNTIME IMPLEMENTED:       NO
CAP=1 PARITY:                 NOT RUN
PRODUCTION AUTHORIZED:        NO_CHANGE
```

Also blocked/separate:

- search >1.30 without a new experiment ID;
- EXPOSURE-SMOOTH-0038 promotion;
- F23 funding-response redesign;
- shorts / XRP target exposure;
- P5 exit intelligence;
- production leverage authorization.

`production_authorized_components = []` remains unchanged.

## Project drift audit

```text
PRE-RUN REVIEW DISCOVERY: DRIFT_2
TARGET AFTER PR #84:      DRIFT_0
```

The drift is limited to P4 architecture/benchmark/stress preregistration. Phase ordering and production/security/human-control boundaries were not crossed.

## Exact next action

```text
finish PR #84 contract + governance validation
-> merge the 0039 stop / 0040 prereg correction
-> fresh P4.3 runner branch
-> implement separate leverage multiplier after frozen defensive scaler
-> prove cap=1 exact historical parity
-> execute LEVERAGE-0040 once only after parity passes
-> run preregistered P4.4 stress suite
-> P4.5 selection / fail decision
-> P4.6 separate deployment cap and production authorization gate
```
