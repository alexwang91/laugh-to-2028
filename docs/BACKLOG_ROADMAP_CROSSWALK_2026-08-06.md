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
| F17 reversal non-atomic / silent failure | P1.4 reversal safety + P1.8 emergency paths | PARTIAL -> audit correction | directional double-risk defect was resolved by fresh-flat reversal gating; the separate requirement that unexpected strategy-cycle failures still notify the operator remained open because `send_telegram` sat after the execution path. Audit correction adds best-effort failure notification and re-raises the original error. |
| F18 size precision | P1.5 precision / metadata | RESOLVED | Hyperliquid metadata drives formatting; truncation and multi-asset formatting tests exist |
| F19 unreachable leverage target reported as no-op | execution-plan semantics, discovered before P3.2 | OPEN -> audit correction | add requested-vs-reachable target, `target_clamped_by_leverage`, explicit unreachable/rebalance reason, and warning payload |
| F20 `/api/cron` authorization | security hardening before any live phase | OPEN -> audit correction | require bearer `CRON_SECRET` for HTTP cron in both shadow/trade, constant-time compare, remove spoofable User-Agent authorization, redact external exception messages. CLI/emergency paths intentionally do not depend on cron auth. |
| F21 unbacktested `ALLOW_STRONG_BETA` / 1.50 branch | P4 leverage-governance boundary | OPEN -> audit correction | remove the env-toggleable 1.50 branch and `HARD_BETA_CAP` / `ALLOW_STRONG_BETA` settings. This does not implement P4 or promote a new leverage model. |
| F22 research/execution price + timing parity | P3.1 data contract plus operational schedule | PARTIAL -> audit correction | P3.1 resolved source/timestamp semantics and 00:00 UTC decision boundary; old Vercel schedule remained 01:10 UTC. Audit correction moves cron to 00:05 UTC while retaining the canonical decision timestamp at 00:00. |
| F23 funding filter scope | future registered research only; must not be slipped into P3.2 | DEFERRED_REGISTERED_BOUNDARY | current legacy filter thresholds are not canonical BRRK research. P3.2 must reproduce frozen BRRK-0011 without treating this filter as promoted logic. Any whole-range funding response requires a new registered experiment; do not retune existing thresholds. |
| F28 impact cost / capacity | P2.3 cost model | RESOLVED_FOR_CURRENT_SCOPE | canonical Hyperliquid L2 depth/VWAP, capacity fail-closed behavior and beyond-spread accounting were completed in P2.3 + correction. Revalidate capacity if deployment size materially changes. |

## Research / evidence backlog relationship

The remaining legacy research items are not silently promoted by this crosswalk. Their status remains governed by `config/decision_registry.json`, `docs/RESEARCH_HISTORY.md`, experiment preregistrations/results and stopped-line discipline.

Two evidence-governance corrections identified during the 2026-08-06 audit remain separate from the execution correction above:

1. `EXPOSURE-SMOOTH-0038` must be recorded as mechanism-validated but **not promoted** so a fresh session cannot accidentally rerun or promote it as canonical V1/BRRK logic.
2. F27 idle-cash-credit absolute CAGR values must be restated from a return series that preserves the first equity observation relative to the known $10,000 initial capital. This is a `MEASUREMENT_FIX`; it does not change the F27 qualitative decision.

## Forward sequencing

After the audit corrections are closed with CI and handoff evidence:

```text
P3.2 Target calculation API
-> P3.3
-> P3.4
-> P4
-> P5
```

P3.2 remains target calculation only. It must not absorb F23 funding-response research, >1 leverage, cycle-exit logic or production authorization.
