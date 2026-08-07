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
- historical stale-main PR #70: INVALID / CLOSED / DO NOT REVIVE

## Current P4 position

Fresh P4.1/P4.2 base:

`fee2ebd34e71f62fb8aaa9e11787aa7413f122cd`

Active PR / branch:

- PR `#82`
- branch `p4-1/leverage-baseline-prereg-v1`
- latest fully validated implementation checkpoint before this handoff update: `fd3e086893df1d57ce92fb7969e8d4ecc11509a1`

```text
P4.1 preserve corrected 0-1 scaler  IMPLEMENTED / TESTED / CI-VERIFIED CANDIDATE
P4.2 preregister leverage study     IMPLEMENTED / TESTED / CI-VERIFIED CANDIDATE
P4.3 leverage objective/runner      BLOCKED UNTIL P4.1/P4.2 MERGE + NORMALIZE
P4.4 stress suite execution         BLOCKED
P4.5 promotion decision             BLOCKED
P4.6 deployment cap                 BLOCKED
P5 exit intelligence                BLOCKED
```

**LEVERAGE SEARCH RUN: NO. >1 RUNTIME IMPLEMENTED: NO. PRODUCTION AUTHORIZED: NO_CHANGE.**

## Frozen Phase 3 chain

```text
P3.1 canonical daily data
-> P3.2-BRRK0011-V1 target
-> P3.3-L1-BAND-V1 rebalance control
-> P3.4-EQUITY-CHANGE-DAILY-V1 contribution timing
```

Frozen boundaries remain BTC/ETH/SOL/BNB targets, XRP feature-only, approved gross <=1, no shorts, P3.3 L1 band 0.05, P3.4 intraday contribution handling record-only/no-risk-increase, and `production_authorized_components = []`.

## P4.1 corrected 0–1 baseline freeze

Machine freeze:

`research/leverage_0039/P4_1_BASELINE_FREEZE.json`

Freeze ID:

`P4.1-BRRK0011-CORRECTED-0-1-V1`

Pinned base authority:

- source main `fee2ebd34e71f62fb8aaa9e11787aa7413f122cd`;
- `research/risk_metric_fix/corrected_risk.py` blob `bdf7cd6cb32961765716e4cb07288739e869703e`;
- `execution/plan-b-bot/beta_bot/target_math.py` blob `4a0b26943438045f2baacbe06d92650a486a8967`;
- `research/regime_kelly/config.py` blob `eecd092ac45c5fa86992a8de2f31d470405e6b5a`;
- `research/results/BRRK_0011_CDAR_CORRECTION_2026-08-04.md` blob `40cd0e90a357a2c2e5be0b9de69feaf0f1e75eaf`;
- `research/results/idle_cash_credit_0027r2.json` blob `46b509bf1b59a9d87a9092f9708eb41e5f8e50af`.

Frozen risk parameters:

```text
scale domain                 0.0 .. 1.0
scenario CVaR/CDaR budget    20%
tail alpha                   95%
forecast horizon             20d
scenario count               5000
Student-t df                 5
production gross cap         1.0
operating risk budget        UNFROZEN
catastrophic DD boundary     70% termination boundary, not operating target
```

Corrected BRRK-0011 reference, 2022-12-10 through 2026-08-02:

```text
CAGR                 65.104%
MaxDD               -33.715%
Sharpe                1.3532
Calmar                1.9310
realized path CDaR95 31.781%
average gross         0.75430
```

F27 R2 separately records raw calendar-span CAGR `65.16609785339962%`; the measurement conventions remain separately labeled and are not silently reconciled.

## P4.2 LEVERAGE-0039 preregistration

Machine prereg:

`research/leverage_0039/LEVERAGE-0039.json`

Status:

`PREREGISTERED_BEFORE_FIRST_RUN`

Only allowed structural change for the first study is extending the upper bound of the **same corrected CVaR/CDaR selector**. Candidate caps are fixed to:

```text
1.00 / 1.10 / 1.20 / 1.30
```

Cap 1.00 exact baseline parity is mandatory. Search above 1.30 requires a new experiment ID. The existing `research_gross_cap=1.30` is an unused research-only historical hint, not evidence or authorization.

Operating MDD candidate constraints:

```text
35% / 40% / 45% / 50%
```

Scenario CVaR/CDaR budget remains 20%; 70% remains catastrophe boundary only.

Matched cost grid is `5 / 10 / 20 / 50 bps`. Funding is exogenous cost only: Hyperliquid native common-window panel mandatory, Binance proxy stress-only, no funding signal/threshold, no zero-fill of missing native funding, and F23 remains separate.

Historical stress windows include 2021 spring crash, 2021 November/bear transition, 2022 severe drawdown, exact 2024-03-01 through 2024-05-15 April masking window, full calendar 2025 and 2026 through frozen 2026-08-02. Where full BRRK is ineligible under the frozen training gate, early periods are explicitly conservative pre-BRRK stress proxies rather than full-BRRK OOS claims.

Synthetic stress includes one-day uniform gaps -10/-20/-30/-40/-50%, registered BTC-led/alt-crash cross-asset gaps, and 1.5x/2x/3x volatility amplification. No favorable same-day rebalance is assumed inside a gap.

Liquidation-distance evidence is mandatory and must use a snapshotted/hash-pinned Hyperliquid margin/leverage-tier model before the first P4.3 run. Missing liquidation evidence fails closed.

## Promotion boundary

A >1 candidate can advance only if all machine-preregistered gates pass, including cap=1 parity, better matched-cost compounded wealth at 5 and 10 bps, non-domination at 20 bps, selected operating MDD constraint, <70% catastrophe, corrected scenario CVaR/CDaR <=20%, historical/synthetic stress, liquidation-distance evidence, start-date/block-bootstrap robustness, native Hyperliquid funding economics, and no P3/F23/0038/P5/short/XRP scope smuggling.

Failure preserves the <=1 baseline. Even research PASS does not authorize production leverage; P4.6 remains separately versioned and separately authorized.

## Same-PR correction and validated checkpoint

Initial PR head `ad8f2c633b753eb68dfbb6c566fba2eb6436364d` passed all four CI gates, with Phase 0 reporting **223 passed + 5/5 integration**.

A subsequent provenance self-review found the P4.1 freeze had the correct correction-result file path but an incorrect blob SHA (`40cd823...`). Live frozen base evidence is `40cd0e90a357a2c2e5be0b9de69feaf0f1e75eaf`. The wrong pin was corrected in the same PR and a dedicated exact-authority-blob regression test was added. No leverage logic, search domain or result was changed.

Validated corrected checkpoint:

`fd3e086893df1d57ce92fb7969e8d4ecc11509a1`

Evidence:

- `Phase 0 baseline contract` run `31163423607` (#125): **SUCCESS**
  - execution pytest: **224 passed in 7.87s**
  - research integration: **5 tests / OK**
- `Research evidence normalization` run `31163423497` (#36): **SUCCESS**
- `P3.2 target research-live parity` run `31163423629` (#23): **SUCCESS**
  - independent multi-date BRRK target parity: SUCCESS
  - committed historical golden enforcement: SUCCESS
- `PR handoff governance` run `31163423622` (#164): **SUCCESS**

## Candidate files and self-review scope

Changed-file scope remains exactly:

- `research/leverage_0039/P4_1_BASELINE_FREEZE.json`
- `research/leverage_0039/LEVERAGE-0039.json`
- `execution/plan-b-bot/tests/test_p4_leverage_prereg_contract.py`
- `docs/P4_1_P4_2_LEVERAGE_BASELINE_PREREG.md`
- `docs/CURRENT_STATE.md`
- `docs/NEXT_STEPS.md`

No leverage runner/result, runtime >1, product config, decision registry, workflow, production authorization, P3 behavior, F23, 0038 promotion, short/XRP target or P5 logic is introduced.

```text
DRIFT_0
```

## Candidate status

```text
P4.1 BASELINE FROZEN:          IMPLEMENTED / TESTED / CI VERIFIED CANDIDATE
P4.2 PREREGISTERED:            IMPLEMENTED / TESTED / CI VERIFIED CANDIDATE
LEVERAGE SEARCH RUN:           NO
RESULT SELECTED:               NO
OPERATING BUDGET FROZEN:       NO
>1 RUNTIME IMPLEMENTED:        NO
MERGED:                        NO
PRODUCTION AUTHORIZED:         NO_CHANGE
```

This CURRENT_STATE update itself moves the PR head. That final handoff head must re-run the normal PR workflows. No further branch-file mutation is planned unless final-head CI exposes a real failure.

## Exact next action

```text
final-head Phase 0 + research evidence + P3.2 parity/golden + governance
-> all GREEN
-> final compare/self-review
-> update PR #82 body with exact final-head evidence
-> newest body-edit governance GREEN
-> re-fetch PR/head
-> expected-head squash merge
-> docs-only post-merge normalization
-> fresh P4.3 branch
-> snapshot/hash Hyperliquid liquidation inputs
-> implement generalized selector and cap=1 parity
-> only then execute LEVERAGE-0039 exactly once
```
