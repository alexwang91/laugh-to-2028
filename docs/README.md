# Documentation Index

This directory contains both **current authority** and **historical evidence**. They are intentionally not the same thing.

## Read this first

Use the following precedence when determining the current project state:

1. [`../README.md`](../README.md) — short project map and current-phase summary.
2. [`CURRENT_STATE.md`](CURRENT_STATE.md) — **authoritative current snapshot**.
3. [`NEXT_STEPS.md`](NEXT_STEPS.md) — **authoritative dependency order and pause/resume rule**.
4. [`MASTER_PLAN_2026-08-05.md`](MASTER_PLAN_2026-08-05.md) — frozen product and architecture intent.
5. [`IMPLEMENTATION_ROADMAP_2026-08-05.md`](IMPLEMENTATION_ROADMAP_2026-08-05.md) — phase definitions and acceptance criteria.
6. [`../config/decision_registry.json`](../config/decision_registry.json) — machine-readable accepted / rejected / shadow / production decisions.
7. The dated audit, research, runbook, and handoff documents below — evidence snapshots.

If a dated document describes an older phase as “current,” that statement is historical. It does **not** override `CURRENT_STATE.md`.

## Current / canonical governance

| Document | Role |
| --- | --- |
| [`CURRENT_STATE.md`](CURRENT_STATE.md) | Single authoritative current-state handoff. |
| [`NEXT_STEPS.md`](NEXT_STEPS.md) | Unique dependency order; currently freezes the owner-requested P4.4 pause. |
| [`MASTER_PLAN_2026-08-05.md`](MASTER_PLAN_2026-08-05.md) | Product intent, architecture, risk and security boundaries. |
| [`IMPLEMENTATION_ROADMAP_2026-08-05.md`](IMPLEMENTATION_ROADMAP_2026-08-05.md) | Phase 0–5 implementation roadmap and gates. |
| [`PROJECT_GOVERNANCE_2026-08-05.md`](PROJECT_GOVERNANCE_2026-08-05.md) | PR, evidence, status and production-authorization governance. |
| [`CONTEXT_CONTINUITY_PROTOCOL.md`](CONTEXT_CONTINUITY_PROTOCOL.md) | Cross-session handoff and continuity protocol. |
| [`REPOSITORY_HYGIENE_2026-08-07.md`](REPOSITORY_HYGIENE_2026-08-07.md) | Branch cleanup, documentation authority and repository-maintenance record. |

## Phase / implementation documentation

### Phase 1 — execution safety

Most Phase 1 implementation truth now lives directly in `execution/plan-b-bot/` tests and the decision registry. One older handoff remains:

- [`P1_4_CANDIDATE_HANDOFF.md`](P1_4_CANDIDATE_HANDOFF.md) — historical P1.4 candidate handoff; **not current state**.

### Phase 2 — instrument / routing / cost

- [`BNB_ROUTING_POLICY_2026-08-06.md`](BNB_ROUTING_POLICY_2026-08-06.md) — evidence-scoped BNB perp-only routing policy.
- [`RISK_FREE_METRIC_CONVENTIONS.md`](RISK_FREE_METRIC_CONVENTIONS.md) — return / risk-free metric conventions used by later evidence normalization.

Canonical implementation is in `config/` and `execution/plan-b-bot/`; route/depth snapshots are point-in-time execution evidence, not historical liquidity guarantees.

### Phase 3 — research-to-live target pipeline

- [`P3_1_DATA_CONTRACT.md`](P3_1_DATA_CONTRACT.md) — canonical daily data contract; BTC/ETH/SOL/BNB targets plus XRP feature-only input.
- [`P3_3_REBALANCE_CONTROL.md`](P3_3_REBALANCE_CONTROL.md) — economic 5% L1 rebalance / turnover semantics.
- [`P3_4_CONTRIBUTION_HANDLING.md`](P3_4_CONTRIBUTION_HANDLING.md) — contribution handling without changing target authority.

P3.2 canonical target-engine implementation and parity tests live primarily under `execution/plan-b-bot/` and `research/integration/` rather than in a standalone docs file.

### Phase 4 — leverage research

- [`P4_1_P4_2_LEVERAGE_BASELINE_PREREG.md`](P4_1_P4_2_LEVERAGE_BASELINE_PREREG.md) — corrected defensive baseline / leverage preregistration history.
- [`P4_LEVERAGE_ARCHITECTURE_CORRECTION_2026-08-07.md`](P4_LEVERAGE_ARCHITECTURE_CORRECTION_2026-08-07.md) — two-layer P4 architecture correction.
- [`P4_0040_PRE_RUN_CHECKLIST.md`](P4_0040_PRE_RUN_CHECKLIST.md) — LEVERAGE-0040 pre-run checklist.

**Current P4.4 status is PAUSED / DRAFT / NOT RUN.** See `CURRENT_STATE.md`, not the checklist alone, before taking any action.

## Audit / review / migration history

These files are valuable evidence but are dated snapshots:

- [`CODE_REVIEW_2026-08-04.md`](CODE_REVIEW_2026-08-04.md)
- [`CODE_REVIEW_FOLLOWUP_2026-08-05.md`](CODE_REVIEW_FOLLOWUP_2026-08-05.md)
- [`FULL_PROJECT_AUDIT_2026-08-06.md`](FULL_PROJECT_AUDIT_2026-08-06.md)
- [`REVIEW_FIX_BACKLOG.md`](REVIEW_FIX_BACKLOG.md)
- [`BACKLOG_ROADMAP_CROSSWALK_2026-08-06.md`](BACKLOG_ROADMAP_CROSSWALK_2026-08-06.md)
- [`SOURCE_INVENTORY.md`](SOURCE_INVENTORY.md)
- [`MIGRATION_MANIFEST.md`](MIGRATION_MANIFEST.md)

Do not treat a historical “next step” inside these documents as an active task without checking `CURRENT_STATE.md` and `NEXT_STEPS.md`.

## Research history / decisions

- [`RESEARCH_HISTORY.md`](RESEARCH_HISTORY.md) — historical experiment narrative.
- [`EXPOSURE_SMOOTH_0038_DECISION_2026-08-06.md`](EXPOSURE_SMOOTH_0038_DECISION_2026-08-06.md) — EXPOSURE-SMOOTH-0038 remains mechanism evidence / shadow only, not promoted.
- [`../config/decision_registry.json`](../config/decision_registry.json) — machine-readable status of canonical, shadow, stopped and implementation-verified decisions.

Detailed immutable / persisted outputs live under:

`../research/results/`

The presence of a result file means **evidence exists**. It does not imply that the experiment was promoted, merged into production logic, or production-authorized.

## Historical runbooks / artifacts

- [`CARRY_PM_0035_RUNBOOK.md`](CARRY_PM_0035_RUNBOOK.md) — historical carry live-probe runbook; upstream carry economics later stopped the line.
- [`CARRY_PM_0037_RUNBOOK.md`](CARRY_PM_0037_RUNBOOK.md) — historical measurement-integrity runbook.
- [`pnl.svg`](pnl.svg) — historical research visualization artifact.

These remain for traceability. They are not current execution instructions.

## Status vocabulary

Never collapse these states:

```text
IMPLEMENTED
TESTED
CI VERIFIED
MERGED
PRODUCTION AUTHORIZED
```

Likewise:

- `SHADOW_ONLY` is not promoted.
- `REJECTED_STOPPED` must not be rescued by retuning on the same evidence.
- `SUPERSEDED` remains historical record, not current authority.
- a merged PR without recorded final-head CI cannot be retroactively labeled CI VERIFIED.

## Current pause boundary

As of 2026-08-07:

```text
PR #90 / LEVERAGE-0040     PAUSED / DRAFT
RUN_ONCE marker            ABSENT
immutable P4.4 result      ABSENT
cap > 1 candidate result   NONE
production authorization   NONE
```

Repository maintenance does not automatically resume P4.4. Resume requires an explicit owner instruction followed by a fresh-main refresh and complete pre-result revalidation.
