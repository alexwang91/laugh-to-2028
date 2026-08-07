# Documentation Index

This directory contains both **current authority** and **historical evidence**. They are intentionally not the same thing.

## Read this first

Use this precedence for current project state:

1. [`../README.md`](../README.md) — short project map and current-phase summary.
2. [`CURRENT_STATE.md`](CURRENT_STATE.md) — **authoritative current snapshot**.
3. [`NEXT_STEPS.md`](NEXT_STEPS.md) — **authoritative forward dependency order**.
4. [`ROADMAP_AUDIT_2026-08-07.md`](ROADMAP_AUDIT_2026-08-07.md) — program-wide completion/deviation audit through LEVERAGE-0041.
5. [`MASTER_PLAN_2026-08-05.md`](MASTER_PLAN_2026-08-05.md) — frozen product and architecture intent.
6. [`IMPLEMENTATION_ROADMAP_2026-08-05.md`](IMPLEMENTATION_ROADMAP_2026-08-05.md) — phase definitions and acceptance criteria.
7. [`../config/decision_registry.json`](../config/decision_registry.json) — machine-readable accepted/rejected/shadow/implementation/production decisions.
8. Dated audit, research, runbook and historical handoff documents below — evidence snapshots.

If a dated document describes an older phase as “current,” that statement is historical and does **not** override `CURRENT_STATE.md`.

## Current program state

```text
Phase 0–3                     COMPLETE / MERGED
LEVERAGE-0039                 STOPPED PRE-RUN / NO RESULT
LEVERAGE-0040                 COMPLETE / IMMUTABLE / NO_PROMOTION
LEVERAGE-0041                 COMPLETE / IMMUTABLE / NO_PROMOTION
Phase 4 leverage line         FAIL_STOP / no eligible >1 candidate
P4.6 production leverage      NOT ENTERED
Phase 5                       NEXT
production gross cap          1.0
production authorization      NONE
```

`production_authorized_components = []`

## Current / canonical governance

| Document | Role |
| --- | --- |
| [`CURRENT_STATE.md`](CURRENT_STATE.md) | Single authoritative current-state handoff. |
| [`NEXT_STEPS.md`](NEXT_STEPS.md) | Unique forward dependency order; Phase 5 / P5.1 is next. |
| [`ROADMAP_AUDIT_2026-08-07.md`](ROADMAP_AUDIT_2026-08-07.md) | Full completed-task, historical-deviation and future-roadmap audit. |
| [`MASTER_PLAN_2026-08-05.md`](MASTER_PLAN_2026-08-05.md) | Product intent, architecture, risk and security boundaries. |
| [`IMPLEMENTATION_ROADMAP_2026-08-05.md`](IMPLEMENTATION_ROADMAP_2026-08-05.md) | Phase 0–8 implementation roadmap and gates. |
| [`PROJECT_GOVERNANCE_2026-08-05.md`](PROJECT_GOVERNANCE_2026-08-05.md) | PR, evidence, status and production-authorization governance. |
| [`CONTEXT_CONTINUITY_PROTOCOL.md`](CONTEXT_CONTINUITY_PROTOCOL.md) | Cross-session handoff and continuity protocol. |
| [`REPOSITORY_HYGIENE_2026-08-07.md`](REPOSITORY_HYGIENE_2026-08-07.md) | Branch cleanup and documentation-authority record. |

## Phase / implementation documentation

### Phase 1 — execution safety

Canonical implementation truth is primarily in `execution/plan-b-bot/` tests and `config/decision_registry.json`.

Historical candidate handoff:

- [`P1_4_CANDIDATE_HANDOFF.md`](P1_4_CANDIDATE_HANDOFF.md) — evidence snapshot only; not current state.

### Phase 2 — instrument / routing / cost

- [`BNB_ROUTING_POLICY_2026-08-06.md`](BNB_ROUTING_POLICY_2026-08-06.md) — BNB perp-only routing policy.
- [`RISK_FREE_METRIC_CONVENTIONS.md`](RISK_FREE_METRIC_CONVENTIONS.md) — return/risk-free metric conventions.

Canonical implementation lives in `config/` and `execution/plan-b-bot/`. Point-in-time route/depth snapshots are evidence, not permanent liquidity guarantees.

### Phase 3 — research-to-live daily pipeline

- [`P3_1_DATA_CONTRACT.md`](P3_1_DATA_CONTRACT.md) — canonical daily data contract; BTC/ETH/SOL/BNB targets plus XRP feature-only input.
- [`P3_3_REBALANCE_CONTROL.md`](P3_3_REBALANCE_CONTROL.md) — explicit aggregate L1 rebalance/turnover semantics.
- [`P3_4_CONTRIBUTION_HANDLING.md`](P3_4_CONTRIBUTION_HANDLING.md) — next-daily contribution handling without changing target authority.

P3.2 canonical target-engine code and parity evidence live primarily under `execution/plan-b-bot/` and `research/integration/`.

### Phase 4 — leverage research

Historical/preregistration and correction records:

- [`P4_1_P4_2_LEVERAGE_BASELINE_PREREG.md`](P4_1_P4_2_LEVERAGE_BASELINE_PREREG.md)
- [`P4_LEVERAGE_ARCHITECTURE_CORRECTION_2026-08-07.md`](P4_LEVERAGE_ARCHITECTURE_CORRECTION_2026-08-07.md)
- [`P4_0040_PRE_RUN_CHECKLIST.md`](P4_0040_PRE_RUN_CHECKLIST.md)
- [`LEVERAGE_0040_P4_5_DECISION_2026-08-07.md`](LEVERAGE_0040_P4_5_DECISION_2026-08-07.md)
- [`LEVERAGE_0041_PREREGISTRATION_2026-08-07.md`](LEVERAGE_0041_PREREGISTRATION_2026-08-07.md)

Current truth is **not** the old pre-run checklist. Both LEVERAGE-0040 and LEVERAGE-0041 have completed immutable `NO_PROMOTION` results. Exact persisted outputs live under:

- `../research/results/leverage_0040/`
- `../research/results/leverage_0041/`

No >1 research candidate is eligible for P4.6. Production gross remains 1.0.

### Phase 5 — current forward program

Phase 5 is the next research phase: cycle-top / late-bull / exit intelligence.

Read `NEXT_STEPS.md` and the Phase 5 sections of the Implementation Roadmap before creating P5 work. P5 must be treated as a new research program, not as a way to retune BRRK or rescue failed leverage studies.

## Audit / review / migration history

These remain useful evidence but are dated snapshots:

- [`CODE_REVIEW_2026-08-04.md`](CODE_REVIEW_2026-08-04.md)
- [`CODE_REVIEW_FOLLOWUP_2026-08-05.md`](CODE_REVIEW_FOLLOWUP_2026-08-05.md)
- [`FULL_PROJECT_AUDIT_2026-08-06.md`](FULL_PROJECT_AUDIT_2026-08-06.md)
- [`REVIEW_FIX_BACKLOG.md`](REVIEW_FIX_BACKLOG.md)
- [`BACKLOG_ROADMAP_CROSSWALK_2026-08-06.md`](BACKLOG_ROADMAP_CROSSWALK_2026-08-06.md)
- [`SOURCE_INVENTORY.md`](SOURCE_INVENTORY.md)
- [`MIGRATION_MANIFEST.md`](MIGRATION_MANIFEST.md)

Do not treat a historical “next step” in these documents as active without checking the current authority chain above.

## Research history / decisions

- [`RESEARCH_HISTORY.md`](RESEARCH_HISTORY.md) — historical experiment narrative.
- [`EXPOSURE_SMOOTH_0038_DECISION_2026-08-06.md`](EXPOSURE_SMOOTH_0038_DECISION_2026-08-06.md) — mechanism evidence / `SHADOW_ONLY`, not promoted.
- [`../config/decision_registry.json`](../config/decision_registry.json) — machine-readable current decision status.

The presence of a result under `../research/results/` means **evidence exists**. It does not imply promotion or production authorization.

## Historical runbooks / artifacts

- [`CARRY_PM_0035_RUNBOOK.md`](CARRY_PM_0035_RUNBOOK.md) — historical carry live-probe runbook; upstream economics later stopped the line.
- [`CARRY_PM_0037_RUNBOOK.md`](CARRY_PM_0037_RUNBOOK.md) — historical measurement-integrity runbook.
- [`pnl.svg`](pnl.svg) — historical visualization artifact.

These are not current execution instructions.

## Status vocabulary

Never collapse:

```text
IMPLEMENTED
TESTED
CI VERIFIED
MERGED
PRODUCTION AUTHORIZED
```

Likewise:

- `SHADOW_ONLY` is not promoted;
- `REJECTED_STOPPED` must not be rescued by same-evidence retuning;
- `SUPERSEDED` remains history, not current authority;
- a merged PR without recorded final-head CI cannot be retroactively labeled CI VERIFIED;
- a research PASS or result commit is not a production cutover.
