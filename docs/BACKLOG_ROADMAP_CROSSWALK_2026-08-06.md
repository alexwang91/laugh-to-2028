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
| F23 funding filter scope | future registered research only; must not be slipped into P3.2/P3.3/P3.4 | DEFERRED_REGISTERED_BOUNDARY | current legacy filter thresholds are not canonical BRRK research. Any whole-range funding response requires a new registered experiment; do not retune existing thresholds or absorb it into P3.4. |
| F28 impact cost / capacity | P2.3 cost model | RESOLVED_FOR_CURRENT_SCOPE | canonical Hyperliquid L2 depth/VWAP, capacity fail-closed behavior and beyond-spread accounting were completed in P2.3 + correction. Revalidate capacity if deployment size materially changes. |

## P3.1 / P3.2 / P3.3 execution-parity closure

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
2. PR #75 validated the merged schema-v2 state after the GitHub Actions outage:
   - Phase 0 run `31152649985` (#101): SUCCESS;
   - Research evidence run `31152649957` (#13): SUCCESS;
   - final governance run `31152716966` (#133): SUCCESS.
3. PR #76 implemented and merged the canonical P3.2 target engine:
   - final head `351df262d9dfda6e7900f6acc74bdb0a67c5ae1c`;
   - Phase 0 run `31154665875` (#108): SUCCESS;
   - Research evidence run `31154665880` (#19): SUCCESS;
   - P3.2 independent parity + committed-golden run `31154665888` (#6): SUCCESS;
   - final body-edit governance run `31154835417` (#140): SUCCESS;
   - expected-head squash merge `70e279bcb1e7f78cfed1d62376a7aa2fef17ac45`.
4. PR #78 implemented and merged P3.3 target-to-position control:
   - final head `53885b993b662991cd28370d4542e48a31f648b5`;
   - Phase 0 run `31156709738` (#113): SUCCESS, 204 tests + 5/5 research integration;
   - Research evidence run `31156709594` (#24): SUCCESS;
   - P3.2 parity/golden preservation run `31156709586` (#11): SUCCESS;
   - final body-edit governance run `31156872098` (#147): SUCCESS;
   - expected-head squash merge `a503e64da4641e434620aa6a04bf9f6448d00135`.

P3.2 parity covers two early V1-only decisions and six full BRRK decisions spanning 2022-12 through 2026-08, all four semantic regimes, near-flat through near-full defensive scales, exact canonical data digests and committed target vectors.

P3.3 adds the explicit downstream control boundary:

```text
L1 target gap = Σ |target_weight - current_weight|
L1 < 0.05  -> suppress routine churn but preserve theoretical deviation
L1 >= 0.05 -> desired state = full P3.2 target
```

The P3.3 V1 policy hard-freezes its 0.05 continuity value and safety override semantics. Legacy `$100` minimum trade notional remains downstream order feasibility only, not a portfolio rebalance gate.

Disposition for F22: `RESOLVED` across the required P3.1 data, P3.2 target, and P3.3 target-to-position control boundaries.

## Research / evidence backlog relationship

The remaining legacy research items are not silently promoted by this crosswalk. Their status remains governed by `config/decision_registry.json`, `docs/RESEARCH_HISTORY.md`, experiment preregistrations/results and stopped-line discipline.

### EXPOSURE-SMOOTH-0038 authority normalization

PR #72 is merged on main and records the experiment as:

```text
MECHANISM VALIDATED
NOT PROMOTED
BASELINE UNCHANGED
```

Disposition: `RESOLVED` for authority/handoff normalization.

The frozen V1 exposure function and BRRK-0011 remain authoritative. `EXPOSURE-SMOOTH-0038` must not be substituted into the target engine and does not authorize leverage or production trading.

### F27 idle-cash-credit measurement normalization

The F27 table retained inside `docs/REVIEW_FIX_BACKLOG.md` is **R1 superseded historical measurement evidence**. PR #72 preserves R1 and adds the authoritative corrected measurement:

```text
research/results/idle_cash_credit_0027r2.json
```

R2 reconstructs day one from the known `$10,000` base and reproduces the frozen BRRK-0011 calendar-span CAGR anchor before restating the full metric set.

Disposition: `RESOLVED` for measurement/authority normalization. R2 is authoritative corrected evidence; R1 remains preserved as superseded historical evidence.

## Forward sequencing

Current dependency ordering is:

```text
P3.1 schema-v2 data contract      PASS / MERGED
-> P3.2 Target calculation API    PASS / MERGED
-> P3.3 rebalance / turnover      PASS / MERGED
-> P3.4 contributions             UNIQUE NEXT
-> P4
-> P5
```

P3.4 must consume the merged P3.2 target and P3.3 control contracts. It must not absorb F23 funding-response research, >1 leverage, cycle-exit logic, XRP target exposure, or production authorization.
