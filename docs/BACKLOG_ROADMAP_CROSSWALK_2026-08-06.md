# Legacy Review Backlog ↔ Canonical Roadmap Crosswalk — 2026-08-06

Status: governance bridge for the pre-Master-Plan `docs/REVIEW_FIX_BACKLOG.md`.

The Master Plan and Implementation Roadmap are authoritative for forward sequencing. This file prevents older review findings from disappearing merely because the roadmap was later reorganized around product dependencies.

## Rule

Before closing a roadmap item, review every legacy backlog item mapped to that phase and classify each acceptance sub-item as:

- `RESOLVED` — evidence exists on main;
- `PARTIAL` — some acceptance requirements remain;
- `DEFERRED_REGISTERED_BOUNDARY` — intentionally not implemented because a later registered research/product gate owns it;
- `STOPPED_WITH_LINE` — no action because the upstream research line is stopped;
- `OPEN` — still requires work.

A roadmap task touching a legacy defect must not be called complete solely because the same file was edited. The backlog acceptance behavior must be checked explicitly.

## Execution / deployment crosswalk

| Legacy item | Canonical roadmap mapping | Current disposition | Evidence / residual |
| --- | --- | --- | --- |
| F15 order duplication | P1.1 deterministic identity + P1.2 persistent ledger | RESOLVED | deterministic CLOID, durable attempt truth, replay suppression and idempotency tests |
| F16 partial fills | P1.3 partial-fill correctness | RESOLVED | fill-transition accounting uses actual fills and exposes residual target gap |
| F17 reversal non-atomic / silent failure | P1.4 reversal safety + P1.8 emergency paths | RESOLVED | PR #71 preserved best-effort operator notification on unexpected strategy-cycle failure and re-raises the original error; the earlier reversal double-risk defect was already closed by P1.4. |
| F18 size precision | P1.5 precision / metadata | RESOLVED | Hyperliquid metadata drives formatting; truncation and multi-asset formatting tests exist |
| F19 unreachable leverage target reported as no-op | execution-plan semantics, discovered before P3.2 | RESOLVED | PR #71 records requested vs reachable target, explicit leverage-clamp state/reasons, and makes clamp reduction take precedence when the current position exceeds the reachable cap. |
| F20 `/api/cron` authorization | security hardening before any live phase | RESOLVED | PR #71 requires configured bearer `CRON_SECRET` in shadow/trade, uses constant-time comparison, removes User-Agent authorization, and redacts external exception text. |
| F21 unbacktested `ALLOW_STRONG_BETA` / 1.50 branch | P4 leverage-governance boundary | RESOLVED | PR #71 removed the env-toggleable 1.50 branch and `HARD_BETA_CAP` / `ALLOW_STRONG_BETA`; >1 research remains P4-only. |
| F22 research/execution price + timing + target/control parity | P3.1 data contract + P3.2 target parity + P3.3 target-to-position control | RESOLVED | PR #74 implemented schema-v2 five-series signal / four-asset target roles; PR #75 restored validation evidence; PR #76 independently reproduced BRRK-0011 and committed immutable target goldens; PR #78 added explicit four-asset L1 rebalance/turnover control with complete theoretical-gap measurement and preserved upstream P3.2 parity/goldens. |
| F23 funding filter scope | future registered research only; must not be slipped into completed Phase 3 or silently absorbed into P4 | DEFERRED_REGISTERED_BOUNDARY | current legacy filter thresholds are not canonical BRRK research. Any whole-range funding response requires a new registered experiment and explicit roadmap ownership. P4 LEVERAGE-0040 uses funding as exogenous cost/stress only; no signal/filter threshold is authorized. |
| F28 impact cost / capacity | P2.3 cost model + P4 degraded-fill stress reuse | RESOLVED_FOR_CURRENT_SCOPE | canonical Hyperliquid L2 depth/VWAP, capacity fail-closed behavior and beyond-spread accounting were completed in P2.3 + correction. P4 LEVERAGE-0040 preregisters stressed depth/slippage/partial-fill scenarios that reuse these semantics. Revalidate capacity if deployment size materially changes. |

## Phase 3 execution-parity closure

The product/tradable long universe remains:

```text
BTC ETH SOL BNB
```

The exact frozen BRRK-0011 regime feature implementation additionally consumes:

```text
XRPUSDT — feature-only
```

The merged role split remains:

```text
target_assets  = BTC, ETH, SOL, BNB
feature_assets = XRP
strategy-signal daily payload = BTC, ETH, SOL, BNB, XRP
router-eligible assets         = BTC, ETH, SOL, BNB only
```

Closure evidence:

1. PR #74 merged the schema-v2 contract and fail-closed five-series strategy history while keeping XRP out of targets/router inputs.
2. PR #75 validated the merged schema-v2 state after the GitHub Actions outage.
3. PR #76 implemented and merged the canonical P3.2 target engine with independent research/live parity and committed historical goldens.
4. PR #78 implemented and merged P3.3 explicit target-to-position L1 control.
5. PR #80 implemented and merged P3.4 contribution timing/equity handling.

P3.2 parity spans early V1-only and full BRRK decisions, all four semantic regimes, near-flat through near-full defensive scales, exact canonical data digests and committed target vectors.

P3.3 provides the explicit downstream control boundary:

```text
L1 target gap = Σ |target_weight - current_weight|
L1 < 0.05  -> suppress routine churn but preserve theoretical deviation
L1 >= 0.05 -> desired state = full P3.2 target
```

P3.4 adds the contribution timing boundary without creating a second allocation model:

```text
intraday equity-change observation -> record only / no risk increase
next eligible 00:00 UTC decision -> fresh full equity through P3.2 target -> P3.3 control
```

The approximately `$100/week` assumption is not a threshold or scheduler trigger. Positive equity changes remain contribution candidates without transfer-source attribution.

Disposition for F22 remains `RESOLVED` across the required P3.1 data, P3.2 target and P3.3 target-to-position control boundaries. P3.4 completes the separate roadmap requirement for contribution timing without changing that disposition.

## Phase 4 pre-run architecture correction

The Master Plan defines leverage as a separate layer after the frozen regime/risk scaler:

```text
BRRK directional weights
× frozen defensive scaler in [0,1]
× optional leverage multiplier
= final target economic exposure
```

The original `LEVERAGE-0039` preregistration proposed extending the corrected defensive selector itself above 1.0. Pre-run review found that this conflicts with the frozen defensive formula: retaining the final clip removes leverage, while removing the clip can make greater RISK_OFF probability increase exposure.

No leverage search, candidate matrix, selection or economic result had been produced. Therefore:

```text
LEVERAGE-0039 = STOPPED_PRE_RUN / NO_RESULT_EVER_PRODUCED
LEVERAGE-0040 = new preregistered two-layer hypothesis / NOT RUN
```

`LEVERAGE-0040` restores Master Plan coverage by preregistering:

- separate post-defensive leverage multiplier;
- mandatory BTC buy-and-hold benchmark;
- mandatory BTC/ETH/SOL/BNB equal-weight buy-and-hold benchmark;
- frozen BRRK <=1 benchmark;
- explicit Hyperliquid native funding-spike stress;
- explicit degraded-fill/depth/capacity stress;
- liquidation-distance evidence from the official pre-result Hyperliquid margin snapshot.

This correction changes no Phase-3 target/control behavior and authorizes no >1 production exposure.

## Research / evidence backlog relationship

The remaining legacy research items are not silently promoted by this crosswalk. Their status remains governed by `config/decision_registry.json`, `docs/RESEARCH_HISTORY.md`, experiment preregistrations/results and stopped-line discipline.

### F7 metrics-convention convergence

Disposition: `PARTIAL`.

The calendar-span metric convention now has a shared implementation in `research/common/metrics.py`, and corrected/restated work can use that helper. However, this does **not** mean every historical study-local implementation has been migrated. Frozen/immutable studies such as LEVERAGE-0040 retain their original observation-count annualization and must not be rewritten after results merely to force numerical identity.

`docs/LEVERAGE_0040_P4_5_DECISION_2026-08-07.md` documents this explicitly: its cap-1.00 CAGR near `65.31%` is a study-local observation-count metric, while corrected F27 R2 reports calendar-span BRRK raw CAGR `65.1661%`. Within-table LEVERAGE-0040 comparisons remain internally consistent.

No exact count of remaining independent metric implementations is asserted by this correction because a complete repository-wide caller census was not independently established. F7 can become `RESOLVED` only after remaining active/non-immutable callers are inventoried and either migrated or explicitly frozen as historical exceptions.

### EXPOSURE-SMOOTH-0038 authority normalization

PR #72 records the experiment as:

```text
MECHANISM VALIDATED
NOT PROMOTED
BASELINE UNCHANGED
```

Disposition: `RESOLVED` for authority/handoff normalization.

The frozen V1 exposure function and BRRK-0011 remain authoritative. `EXPOSURE-SMOOTH-0038` must not be substituted into the target engine and does not authorize leverage or production trading.

### F27 idle-cash-credit measurement normalization

The F27 table retained inside `docs/REVIEW_FIX_BACKLOG.md` is **R1 superseded historical measurement evidence**. Its old wording that called that R1 table the "current source of truth" is superseded by this canonical crosswalk and the authoritative corrected artifact `research/results/idle_cash_credit_0027r2.json`.

Disposition: `RESOLVED` for measurement/authority normalization. R2 is authoritative corrected evidence; R1 remains preserved as superseded historical evidence and is not edited away.

R2 fixes the measurement construction that dropped the first realized equity observation and instead preserves day-one PnL from the known `$10,000` starting base. Corrected headline evidence is:

| | V1 baseline | BRRK-0011 core |
| --- | ---: | ---: |
| mean idle-cash fraction | 20.5183% | 24.5700% |
| CAGR, raw -> credited | 61.3127% -> 62.6632% | 65.1661% -> 66.8068% |
| CAGR delta | **+1.3505 pp** | **+1.6407 pp** |
| Sharpe (rf=0), raw -> credited | 1.2950 -> 1.3138 | 1.3532 -> 1.3756 |
| Sharpe (excess over rf), raw -> credited | 1.2724 -> 1.3029 | 1.3667 -> 1.4039 |
| Max drawdown, raw -> credited | -37.6349% -> -36.6003% | -33.7151% -> -33.5524% |

The BRRK-vs-V1 rf=0 Sharpe gap moves from `+0.0581629` raw to `+0.0617832` credited, a `+0.0036204` shift. The qualitative F27 measurement conclusion is unchanged.

Execution feasibility is a separate question. `docs/IDLE_CASH_EXECUTION_FEASIBILITY.md` concludes `NOT_FEASIBLE_ON_HYPERLIQUID_STANDARD` for frozen Phase-7 V1: the R2 counterfactual credit does not establish an automatic yield source on immediately callable Standard-mode margin. Any future yield implementation requires separate design, contract and approval.

## Forward sequencing

Current dependency ordering is:

```text
P3.1 schema-v2 data contract      PASS / MERGED
-> P3.2 Target calculation API    PASS / MERGED
-> P3.3 rebalance / turnover      PASS / MERGED
-> P3.4 contributions             PASS / MERGED
=> PHASE 3                        COMPLETE
-> P4.1 frozen <=1 baseline       PASS / MERGED
-> LEVERAGE-0039                  STOPPED_PRE_RUN / NO RESULT
-> LEVERAGE-0040                  FAIL_STOP / NO_PROMOTION / IMMUTABLE
-> P5.x                           CLOSED / NO PROMOTION
-> Phase 6 pre-arm dependencies   3/4 / IDENTITY UNRESOLVED
```

The historical pre-run wording below is retained only as lineage: before LEVERAGE-0040 execution, the correction preregistration had to merge and cap=1 parity had to pass. That study has since completed and failed promotion; it must not be rerun or retuned.

Current forward work must not silently absorb F23 funding-response research, P5 exit logic, short/XRP target exposure, EXPOSURE-SMOOTH-0038 promotion, Idle Cash implementation, or production authorization.
