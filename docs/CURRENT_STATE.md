# BRRK Current State

Last updated: 2026-08-07
Status: authoritative cross-chat handoff snapshot

## Authoritative baseline

- P0.1 / P0.2: PASS / MERGED
- P1.1 through P1.8: PASS / MERGED; Phase 1 COMPLETE
- P2.1 through P2.4: PASS / MERGED; Phase 2 COMPLETE
- P3.1 through P3.4: PASS / TESTED / CI VERIFIED / MERGED
- **Phase 3 COMPLETE**
- post-P3.4 normalization PR #81: PASS / MERGED
- PR #73 remains historically MERGED without a recorded green required PR-governance run before merge; do not retroactively relabel it CI VERIFIED
- PR #74 remains historically MERGED during the GitHub Actions incident without its own pre-merge workflow evidence; PR #75 subsequently validated the merged schema-v2 state
- historical stale-main PR #70: INVALID / CLOSED / DO NOT REVIVE

## Current main and P4 position

Fresh P4.1/P4.2 base:

`fee2ebd34e71f62fb8aaa9e11787aa7413f122cd`

Active branch:

`p4-1/leverage-baseline-prereg-v1`

```text
P3.1 -> P3.4                         PASS / MERGED / PHASE 3 COMPLETE
P4.1 preserve corrected 0-1 scaler  IMPLEMENTED CANDIDATE
P4.2 preregister leverage study     IMPLEMENTED CANDIDATE
P4.3 leverage objective/runner      BLOCKED UNTIL P4.1/P4.2 MERGE
P4.4 stress suite execution         BLOCKED
P4.5 promotion decision             BLOCKED
P4.6 deployment cap                 BLOCKED
P5 exit intelligence                BLOCKED
```

**No leverage search has been run on this branch. No >1 runtime target exists.**

## Frozen Phase 3 chain

```text
P3.1 canonical daily data
-> P3.2-BRRK0011-V1 target
-> P3.3-L1-BAND-V1 rebalance control
-> P3.4-EQUITY-CHANGE-DAILY-V1 contribution timing
```

Frozen boundaries remain:

```text
target assets = BTC, ETH, SOL, BNB
feature-only  = XRP
approved gross <= 1
short targets forbidden
P3.3 routine L1 band = 0.05
P3.4 intraday contribution handling = record only / no risk increase
production_authorized_components = []
```

## P4.1 corrected 0–1 baseline freeze

Machine-readable freeze:

`research/leverage_0039/P4_1_BASELINE_FREEZE.json`

Freeze ID:

`P4.1-BRRK0011-CORRECTED-0-1-V1`

The baseline pins:

- source main SHA `fee2ebd34e71f62fb8aaa9e11787aa7413f122cd`;
- corrected research risk implementation `research/risk_metric_fix/corrected_risk.py`;
- product-owned P3.2 reproduction `execution/plan-b-bot/beta_bot/target_math.py`;
- frozen regime configuration `research/regime_kelly/config.py`;
- corrected BRRK-0011 result `research/results/BRRK_0011_CDAR_CORRECTION_2026-08-04.md`;
- separate F27 R2 measurement convention without overwriting/reconciling it into the correction-result metric table.

Frozen risk parameters include:

```text
scale domain                 0.0 .. 1.0
scenario CVaR/CDaR budget    20%
tail alpha                   95%
forecast horizon             20d
scenario count               5000
Student-t df                 5
production gross cap         1.0
operating risk budget        UNFROZEN
catastrophic DD boundary     70% (termination boundary, not operating target)
```

Authoritative corrected BRRK-0011 result, 2022-12-10 through 2026-08-02:

```text
CAGR                 65.104%
MaxDD               -33.715%
Sharpe                1.3532
Calmar                1.9310
realized path CDaR95 31.781%
average gross         0.75430
```

F27 R2 separately records calendar-span raw CAGR `65.16609785339962%`; provenance labels remain separate.

Historical artifacts are not overwritten.

## P4.2 LEVERAGE-0039 preregistration

Machine-readable preregistration:

`research/leverage_0039/LEVERAGE-0039.json`

Status:

`PREREGISTERED_BEFORE_FIRST_RUN`

Only allowed structural change for the first study:

> generalize the upper bound of the **same corrected CVaR/CDaR selector** from 1.0 to a preregistered research cap.

Candidate caps:

```text
1.00 / 1.10 / 1.20 / 1.30
```

Why stop at 1.30:

- `RegimeKellyConfig` already contains an unused `research_gross_cap = 1.30` research-only hint;
- repository code search found no consumer of that field;
- it is not evidence or authorization;
- any search above 1.30 requires a new experiment ID/preregistration.

Mandatory cap=1.0 gate:

- generalized runner must reproduce the frozen <=1 baseline before any >1 result is valid.

Operating maximum-drawdown candidate budgets:

```text
35% / 40% / 45% / 50%
```

These are constraint candidates, not targets. All remain below the 70% catastrophic boundary.

The scenario CVaR/CDaR budget remains frozen at 20%.

## Cost and funding preregistration

Matched turnover/fee/slippage stress grid:

```text
5 / 10 / 20 / 50 bps per absolute weight change
```

This reuses the already-audited robustness grid. Candidate and <=1 baseline always receive identical cost assumptions.

Funding is exogenous cost only:

- Hyperliquid native all-perp common window is mandatory;
- Binance full-history funding is a sign/regime proxy only, never a Hyperliquid level estimate;
- `ROUTER-PNL-0005` strict verified-spot accounting may be reported diagnostically but is not deployable net PnL because historical spot fee/basis/slippage evidence is incomplete;
- missing native funding cannot be filled with zero;
- no funding signal/threshold/position filter is allowed;
- F23 remains separate.

## Preregistered stress / robustness gates

Historical windows include:

- 2021 spring crash;
- 2021 November / bear transition;
- 2022 severe drawdown;
- exact prior 2024-03-01 to 2024-05-15 April masking window;
- full calendar 2025 with mechanically reported largest three non-overlapping drawdowns;
- 2026 through frozen 2026-08-02 end.

Where full BRRK is not legally eligible under the frozen minimum-training rule, 2021/early-2022 is explicitly a conservative pre-BRRK stress proxy and cannot be labeled full-BRRK OOS performance.

Synthetic suite includes:

- uniform one-day target-asset gaps -10/-20/-30/-40/-50%;
- preregistered BTC-led and alt-crash cross-asset gaps;
- 1.5x / 2x / 3x volatility amplification of worst realized 20-day blocks;
- no favorable same-day rebalance inside a gap.

Liquidation-distance evidence is mandatory. The future runner must snapshot/hash canonical Hyperliquid margin/leverage tiers before its first run. Missing liquidation modeling fails closed; every mandatory stress must avoid modeled liquidation.

Robustness is preregistered across start dates 2022-12-10 / 2023-03-01 / 2023-06-01 / 2024-01-01 and stationary block bootstrap mean lengths 7/21/63 days, 10,000 resamples.

## Promotion boundary

A >1 candidate can advance only if every preregistered gate passes, including:

- cap=1 baseline parity;
- better matched-cost compounded wealth at both 5 and 10 bps;
- not dominated by <=1 at 20 bps;
- selected operating DD budget respected;
- 70% catastrophe boundary respected;
- corrected scenario CVaR95/CDaR95 <=20% at every leverage decision;
- historical + synthetic stress passes;
- liquidation-distance evidence passes;
- start-date + block-bootstrap robustness passes;
- Hyperliquid native funding economics reported;
- no new alpha/F23/0038/short/XRP/P5 logic.

Failure preserves the <=1 baseline.

Even a successful research result does not authorize production leverage. P4.6 requires a lower, separately versioned deployment cap and separate production authorization.

## Candidate files

- `research/leverage_0039/P4_1_BASELINE_FREEZE.json`
- `research/leverage_0039/LEVERAGE-0039.json`
- `execution/plan-b-bot/tests/test_p4_leverage_prereg_contract.py`
- `docs/P4_1_P4_2_LEVERAGE_BASELINE_PREREG.md`
- `docs/CURRENT_STATE.md`
- `docs/NEXT_STEPS.md`

## Current status

```text
P4.1 BASELINE FROZEN:          CANDIDATE / NOT MERGED
P4.2 PREREGISTERED:            CANDIDATE / NOT MERGED
LEVERAGE SEARCH RUN:           NO
RESULT SELECTED:               NO
OPERATING BUDGET FROZEN:       NO
>1 RUNTIME IMPLEMENTED:        NO
PRODUCTION AUTHORIZED:         NO_CHANGE
```

## Explicit exclusions

Do not add in this P4.1/P4.2 PR:

- leverage runner or result artifact;
- search above 1.30;
- runtime gross >1;
- P3.1/P3.2/P3.3/P3.4 changes;
- EXPOSURE-SMOOTH-0038 promotion;
- F23 funding-response logic;
- shorts;
- XRP targets;
- P5 exit intelligence;
- historical BRRK artifact overwrite;
- production authorization.

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
self-review P4.1/P4.2 candidate
-> open PR
-> Phase 0 + applicable upstream parity/research/governance
-> same-PR correction of any real failure
-> final-head CI
-> expected-head merge
-> docs-only post-merge normalization
-> fresh P4.3 branch
-> snapshot/hash liquidation inputs
-> implement generalized selector runner with mandatory cap=1 parity
-> only then execute LEVERAGE-0039 exactly once
```
