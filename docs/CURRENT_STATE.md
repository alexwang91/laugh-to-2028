# BRRK Current State

Last updated: 2026-08-08  
Status: **authoritative current-state handoff**

## Executive state

```text
Phase 0-3                         COMPLETE / MERGED
Phase 4 leverage research         FAIL_STOP / no eligible >1 candidate
production gross cap              1.0
production_authorized_components = []
P5.1-P5.4                         COMPLETE / frozen
P5.5 validation                   COMPLETE / IMMUTABLE / NO_PROMOTION / FAIL_STOP
P5.6 cycle integration            BLOCKED / NO ELIGIBLE P5.5 CANDIDATE
Phase 6 implementation/replay     PASS_SHADOW_ONLY_IMPLEMENTATION_REPLAY / MERGED #109
Phase 6 live elapsed evidence     MEASUREMENT_INCONCLUSIVE_TIME_DEPENDENT
Phase 7 readiness gate            IMPLEMENTED / MERGED #110 / LAUNCH BLOCKED
Phase 7 program state             MONITOR_ONLY
Phase 8 bear-short research       PREREGISTERED_TRIGGER_ABSENT_NOT_RUN / MERGED #111
Phase 0-8 drift audit             COMPLETE / PASS_FINAL_HEAD_VERIFIED / DRIFT_2 REMEDIATED
Program epistemic governance v1   PG0-PG1 COMPLETE / PG2 NEXT
production authorization          NONE
first real short authorization    NONE
```

## Phase 4

`LEVERAGE-0040` and `LEVERAGE-0041` remain immutable `NO_PROMOTION`. No research cap, operating drawdown budget or prospective production leverage cap was selected. Current production gross remains `1.0` and P4.6 remains blocked.

`LEVERAGE-0040` summary SHA256 remains:

```text
3bb4dc46c61a5e9c7e049862575a89b2771830410ce4bc2bb25c83e469f52fc0
```

## Phase 5

P5.5 immutable result commit `ae20890d87567c98e403e3558219d5de55daef67`; summary SHA256 `ccbdc067f9f7f1277e6eecaa2f74f31f84e3a1882ccef418e097b2ea66bf6e71`.

No profile/map combination passes the frozen validation stack. P5.6 remains `BLOCKED / NO ELIGIBLE CANDIDATE`; no cycle-risk multiplier is carried into Phase 6/7.

## Phase 6

Merged PR #109 at `1763d3c6f2c2d68f77f9e68b3cf9e252e4b799d4`.

Machine contract: `config/phase6_shadow_contract.json`.

Canonical P3.2 parity/golden vectors and zero-authority shadow implementation/replay passed. The shadow path can read account/market/order-book state and compute hypothetical routing, but it cannot sign or submit orders.

Actual elapsed evidence remains time-dependent. The frozen contract requires at least 14 elapsed calendar days, at least 10 scheduled decisions and the required live-shadow quality criteria before the live-observation state can change from:

```text
MEASUREMENT_INCONCLUSIVE_TIME_DEPENDENT
```

No CI replay or historical replay may backfill that elapsed-time evidence.

The Phase 6 contract is unchanged. New observation-infrastructure work is sequenced after Program-Level Epistemic Governance v1 so future elapsed observations can enter the new provenance/evidence model from inception.

## Phase 7

Readiness gate merged in PR #110. Machine contract: `config/phase7_launch_readiness.json`.

Current state is `MONITOR_ONLY`; production authorization is false. Launch is blocked at minimum by missing Phase 6 elapsed evidence and missing explicit owner approval. The gate also requires production-release, credential, monitoring, reconciliation and kill-switch evidence.

Human approval remains mandatory for:

```text
MONITOR_ONLY -> ACTIVE
FLAT -> LONG
FLAT -> SHORT
first short exposure of a new bear phase
```

## Phase 8

`BEAR-SHORT-0001` research package merged in PR #111. Machine contract: `research/bear_short_0001/BEAR-SHORT-0001.json`.

No canonical `CONFIRMED_BEAR_TRANSITION_ARTIFACT` exists, therefore:

```text
status                       PREREGISTERED_TRIGGER_ABSENT_NOT_RUN
selection_status             NONE_TRIGGER_ABSENT
short_ready                  false
production_authorized        false
first_real_short_authorized  false
```

No subjective market judgment substitutes for the missing trigger and no trigger-dependent short economics has been run.

## Phase 0-8 drift audit

Machine contract: `config/phase0_8_drift_audit.json`. Evidence report: `docs/PHASE_0_8_DRIFT_AUDIT_2026-08-08.md`.

The audit is complete and remediated three drift classes without economic retuning:

1. **Legacy execution authority bypass** — normal risk increases are fail-closed behind explicit production authority.
2. **Legacy production-cap drift** — production-facing `NORMAL_BETA_CAP` default/ceiling is `1.0`.
3. **Authoritative handoff drift** — README/CURRENT_STATE/NEXT_STEPS reflect completed Phase 6/7/8 work.

Same-direction reductions and emergency flatten remain available. The audit status is `PASS_FINAL_HEAD_VERIFIED` and does not confer production authority.

## Program-Level Epistemic Governance v1

PG0 repository governance audit is complete:

`docs/PROGRAM_GOVERNANCE_PG0_REPOSITORY_AUDIT_2026-08-08.md`

PG1 canonical semantics are frozen in:

- `config/research_governance_v1.json`;
- `docs/PROGRAM_GOVERNANCE_V1_SPEC_2026-08-08.md`.

The prospective governance boundary is the verified pre-governance implementation main:

```text
legacy_boundary_commit = 896cbd123b7a0c38943815dd802f0f9dcd12e1c2
research_governance_version = 1
```

Legacy research remains `RETROSPECTIVE_LEGACY`; new formal result-bearing research after the boundary must use `PROGRAM_GOVERNED_V1`. Decision/authorization, research, dataset exposure, edge and phase authority remain separate planes. Typed lineage, data-budget, exposure-release, contamination, research-domain/objective, evidence-dimension and future fail-closed vocabularies are frozen before registry implementation.

PG1 does not create research/exposure/edge records and does not retroactively claim that old experiments satisfied v1.

Historical research branches remain retained until PG4 retrospective provenance mapping is complete.

## Frozen product boundaries

- BRRK relative ranking unchanged.
- Production gross cap remains 1.0.
- `production_authorized_components = []`.
- No >1 production leverage.
- No P5 cycle overlay.
- No automated withdrawal/transfer.
- No live launch authorization.
- No real short authorization.
- Legacy credentials / `TRADING_MODE=trade` do not create production authority.

## Exact next action

```text
PG2: ADD MINIMAL RESEARCH / DATASET-EXPOSURE / EDGE REGISTRIES AND SCHEMAS
DO NOT MAP LEGACY FACTS BEYOND EXPLICIT PLACEHOLDERS UNTIL PG4
KEEP EDGE REGISTRY EMPTY UNTIL AN EDGE PASSES ADMISSION EVIDENCE
DO NOT OVERLOAD DECISION_REGISTRY WITH TRIAL OR EXPOSURE FACTS
DO NOT START SUPERTrend / FUNDING-OI / RELATIVE-STRENGTH / NEW-ALLOCATION RESEARCH
DO NOT CHANGE BRRK / BNB / PARAMETERS / COSTS / PRODUCTION AUTHORITY
AFTER GOVERNANCE V1 MERGES, RESUME REAL PHASE-6 ZERO-AUTHORITY ELAPSED OBSERVATION
DO NOT REBUILD OR BACKFILL PHASE-6 ELAPSED EVIDENCE
DO NOT ACTIVATE PHASE 7 WITHOUT THE COMPLETE CHECKLIST AND EXPLICIT OWNER APPROVAL
DO NOT RUN BEAR-SHORT-0001 ECONOMICS WITHOUT THE FROZEN CONFIRMED-BEAR TRIGGER
```
