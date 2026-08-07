# Next Steps

> Read canonical sources in repository-defined order. GitHub actual state wins over stale prose.

## Current dependency

```text
P4.1 preserve corrected 0-1 scaler
+
P4.2 preregister first leverage study
```

Phase 3 is COMPLETE and post-P3.4 normalization PR #81 is merged. Fresh P4 base:

`fee2ebd34e71f62fb8aaa9e11787aa7413f122cd`

Active branch:

`p4-1/leverage-baseline-prereg-v1`

## Current P4 status

```text
P4.1 baseline freeze             IMPLEMENTED CANDIDATE
P4.2 LEVERAGE-0039 prereg        IMPLEMENTED CANDIDATE
P4.3 leverage runner/objective   BLOCKED
P4.4 stress execution            BLOCKED
P4.5 promotion                   BLOCKED
P4.6 deployment cap              BLOCKED
```

**No leverage search has been run. No >1 runtime target exists.**

## P4.1 baseline

Machine freeze:

`research/leverage_0039/P4_1_BASELINE_FREEZE.json`

Freeze ID:

`P4.1-BRRK0011-CORRECTED-0-1-V1`

It preserves the current corrected BRRK-0011 defensive layer:

```text
scale domain              0 .. 1
scenario CVaR/CDaR budget 20%
production gross cap      1.0
operating risk budget     UNFROZEN
catastrophic DD boundary  70% termination limit only
```

Do not overwrite historical BRRK artifacts or silently reconcile different metric conventions. The corrected BRRK result CAGR (65.104%) and F27 R2 raw calendar-span CAGR (65.16609785339962%) remain separately labeled evidence.

## P4.2 LEVERAGE-0039

Machine preregistration:

`research/leverage_0039/LEVERAGE-0039.json`

Status:

`PREREGISTERED_BEFORE_FIRST_RUN`

Only structural change allowed in the first study:

> extend the upper bound of the same corrected CVaR/CDaR scale selector.

Candidate research caps:

```text
1.00 / 1.10 / 1.20 / 1.30
```

`1.00` is a mandatory exact baseline-parity gate. The 1.30 ceiling is taken only as the repository's historical research-only cap hint; it is not promoted or production-authorized. Any search above 1.30 requires a new experiment ID.

Operating maximum-drawdown candidate budgets:

```text
35% / 40% / 45% / 50%
```

They are constraints, not targets. All remain below the 70% catastrophe boundary. Scenario CVaR/CDaR budget remains frozen at 20%.

## Cost / funding gate

Matched cost grid:

```text
5 / 10 / 20 / 50 bps per absolute weight change
```

Funding is exogenous cost only:

- Hyperliquid native common-window panel mandatory;
- Binance full-history panel proxy/stress only;
- no funding threshold, alpha or position filter;
- no zero-filling missing native funding;
- strict verified-spot accounting may be diagnostic but is not deployable net PnL without historical spot fee/basis/slippage evidence;
- F23 remains separate.

## Stress gate

Preregistered historical eras:

- 2021 spring crash;
- 2021 November/bear transition;
- 2022 severe drawdown;
- 2024-03-01 through 2024-05-15 April masking episode;
- calendar 2025 multi-peak/deleveraging;
- 2026 through frozen 2026-08-02 end.

2021/early-2022 uses an explicitly labeled conservative pre-BRRK proxy wherever the frozen 600-day training gate makes full BRRK ineligible.

Synthetic suite includes one-day uniform gaps -10/-20/-30/-40/-50%, cross-asset BTC-led/alt-crash gaps and 1.5x/2x/3x volatility amplification on worst 20-day blocks.

A canonical Hyperliquid liquidation-distance model must be snapshotted and hash-pinned before the first leverage run. Missing liquidation evidence fails closed.

## Promotion gate

A >1 candidate cannot advance unless all machine-preregistered conditions pass, including:

- cap=1 baseline parity;
- higher matched-cost compounded wealth at 5 and 10 bps;
- not dominated by <=1 baseline at 20 bps;
- selected operating MDD constraint;
- <70% catastrophic drawdown;
- corrected scenario CVaR/CDaR <=20%;
- all historical/synthetic stresses;
- liquidation-distance gate;
- start-date and stationary-block bootstrap robustness;
- Hyperliquid native funding panel;
- no P3/F23/0038/P5/short/XRP scope smuggling.

Failure preserves <=1 baseline.

## Deployment remains separate

Even a research PASS does not authorize live leverage.

Under `LEVERAGE-0039`, any future deployment cap must be the next lower preregistered cap grid point and never above 1.20, with a separate versioned decision and production authorization.

`production_authorized_components = []` remains unchanged.

## Explicit exclusions for this PR

Do not add:

- leverage runner or results;
- search above 1.30;
- runtime gross >1;
- P3.1/P3.2/P3.3/P3.4 modifications;
- EXPOSURE-SMOOTH-0038 promotion;
- F23 funding response;
- shorts / XRP targets;
- P5 exit logic;
- production authorization.

## Project drift audit

```text
DRIFT_0
```

## Exact next action

```text
self-review current P4.1/P4.2 diff
-> open PR
-> Phase 0 / applicable P3.2 parity / research evidence / governance
-> fix every real failure in same PR
-> final-head CI
-> write exact evidence into PR body
-> newest body-edit governance GREEN
-> expected-head squash merge
-> post-merge normalization
-> fresh P4.3 runner branch
-> snapshot/hash liquidation inputs
-> cap=1 exact parity first
-> execute LEVERAGE-0039 once only after all prereg inputs are frozen
```
