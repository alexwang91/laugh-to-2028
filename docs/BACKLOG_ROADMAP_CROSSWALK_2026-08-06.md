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
| F22 research/execution price + timing parity | P3.1 data contract plus operational schedule | PARTIAL | PR #74 merged the schema-v2 correction that restores XRPUSDT as feature-only strategy input while preserving BTC/ETH/SOL/BNB as the target/router universe. Implementation parity is now on main, but #74 and its merge SHA received zero Actions runs during the GitHub Actions incident. F22 remains PARTIAL only because post-merge validation evidence is missing. P3.3 separately owns rebalance-band/turnover semantics. |
| F23 funding filter scope | future registered research only; must not be slipped into P3.2 | DEFERRED_REGISTERED_BOUNDARY | current legacy filter thresholds are not canonical BRRK research. P3.2 must reproduce frozen BRRK-0011 without treating this filter as promoted logic. Any whole-range funding response requires a new registered experiment; do not retune existing thresholds. |
| F28 impact cost / capacity | P2.3 cost model | RESOLVED_FOR_CURRENT_SCOPE | canonical Hyperliquid L2 depth/VWAP, capacity fail-closed behavior and beyond-spread accounting were completed in P2.3 + correction. Revalidate capacity if deployment size materially changes. |

## P3.1 feature-input parity residual

The product/tradable long universe remains:

```text
BTC ETH SOL BNB
```

The exact frozen BRRK-0011 regime feature implementation additionally consumes:

```text
XRPUSDT — feature-only
```

PR #74 merged the schema-v2 contract that makes this role split explicit:

```text
target_assets  = BTC, ETH, SOL, BNB
feature_assets = XRP
strategy-signal daily payload = BTC, ETH, SOL, BNB, XRP
router-eligible assets         = BTC, ETH, SOL, BNB only
```

The merged implementation requires complete five-series strategy history, fails closed on XRP gaps, keeps research/live canonicalization shared, and rejects XRP from funding/basis routing. No BRRK weight, regime parameter, risk budget or research promotion changed.

Residual before F22 can return to resolved-for-P3.2 status:

- obtain a real post-merge Phase 0 run covering the complete execution pytest suite and research integration contract;
- obtain normal PR handoff governance on the validation PR;
- preserve `production_authorized_components = []`.

The absence of #74 CI is missing evidence caused by the Actions incident, not a recorded test failure.

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

The frozen V1 exposure function and BRRK-0011 remain authoritative. `EXPOSURE-SMOOTH-0038` must not be substituted into P3.2 and does not authorize leverage or production trading.

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
P3.1 schema-v2 post-merge validation
-> P3.2 Target calculation API
-> P3.3
-> P3.4
-> P4
-> P5
```

P3.2 remains target calculation only. It must not absorb F23 funding-response research, >1 leverage, cycle-exit logic, P3.3 turnover/rebalance behavior, P3.4 contribution handling, XRP target exposure, or production authorization.
