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
| F22 research/execution price + timing parity | P3.1 data contract plus operational schedule | PARTIAL | Source/timestamp semantics and 00:00 UTC economic boundary are already fixed, but P3.2 recovery exposed a P3.1 input-parity residual: frozen BRRK-0011 regime features consume XRPUSDT as feature-only input while the v1 canonical payload exposed only BTC/ETH/SOL/BNB. `fix/p3-1-feature-input-parity` must merge before F22 returns to resolved-for-P3.2 status. P3.3 separately owns rebalance-band/turnover semantics. |
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

The v1 P3.1 contract omitted that feature-only series. Removing XRP from the model would change frozen BRRK-0011, so the correction instead versions the canonical strategy payload to include XRP while preserving a four-asset target/router boundary.

Required evidence before this residual closes:

- machine contract explicitly distinguishes target assets from feature-only assets;
- canonical daily payload fails closed if XRP is missing or gapped;
- research/live canonical payload remains byte/digest identical for identical observations;
- router funding/basis rejects XRP;
- no BRRK weight, regime parameter, risk budget or research promotion changes;
- normal tests/governance/CI and expected-head merge complete.

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

The F27 table retained inside `docs/REVIEW_FIX_BACKLOG.md` is **R1 superseded historical measurement evidence**. Its `pct_change().dropna()` return reconstruction dropped the first realized equity row and shortened the calendar span by one day. Any sentence in that historical F27 section calling R1 the “current source of truth” is superseded by the merged R2 correction and must not be used as current authority.

PR #72 preserves R1 and adds the authoritative corrected measurement:

```text
research/results/idle_cash_credit_0027r2.json
```

R2 reconstructs day one from the known `$10,000` base, first reproduces the frozen BRRK-0011 calendar-span CAGR anchor `0.6516609785...`, and then restates the full metric set. Corrected headline values are:

- V1 raw CAGR `61.3126529%`, credited CAGR `62.6632027%`;
- BRRK-0011 raw CAGR `65.1660979%`, credited CAGR `66.8067973%`;
- BRRK-vs-V1 rf=0 Sharpe gap `+0.0581629 -> +0.0617832`.

The F27 qualitative conclusion remains unchanged: idle-cash credit improves both variants and does not change the BRRK-0011 promotion decision.

Disposition: `RESOLVED` for measurement/authority normalization. R2 is authoritative corrected evidence; R1 remains preserved as superseded historical evidence.

## Forward sequencing

Current dependency ordering is:

```text
P3.1 feature-input parity correction
-> P3.2 Target calculation API
-> P3.3
-> P3.4
-> P4
-> P5
```

P3.2 remains target calculation only. It must not absorb F23 funding-response research, >1 leverage, cycle-exit logic, P3.3 turnover/rebalance behavior, P3.4 contribution handling, XRP target exposure, or production authorization.
