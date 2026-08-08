# BRRK Next Steps

Last updated: 2026-08-08

## Current instruction

**Phase 0–8 drift audit/remediation is complete. Before consuming more historical data in new strategy research or building further Phase 6 observation infrastructure, implement Program-Level Epistemic Governance v1. Production remains unauthorized.**

Pre-implementation handoff:

`docs/PROGRAM_LEVEL_EPISTEMIC_GOVERNANCE_V1_HANDOFF_2026-08-08.md`

## Immediate state

```text
Phase 0-3                              COMPLETE / MERGED
Phase 4 leverage research              FAIL_STOP / no eligible >1 candidate
production gross cap                   1.0
production_authorized_components = []
P5.1-P5.4                              COMPLETE / FROZEN
P5.5 joint validation                  COMPLETE / IMMUTABLE / NO_PROMOTION / FAIL_STOP
P5.5 result commit                     ae20890d87567c98e403e3558219d5de55daef67
P5.5 summary SHA256                    ccbdc067f9f7f1277e6eecaa2f74f31f84e3a1882ccef418e097b2ea66bf6e71
P5.6 integration                       BLOCKED / NO ELIGIBLE CANDIDATE
Phase 6 implementation/replay          PASS_SHADOW_ONLY_IMPLEMENTATION_REPLAY / MERGED #109
Phase 6 live elapsed evidence          MEASUREMENT_INCONCLUSIVE_TIME_DEPENDENT
Phase 7 readiness gate                 IMPLEMENTED / MERGED #110 / LAUNCH BLOCKED
Phase 7 mode                           MONITOR_ONLY
Phase 8 BEAR-SHORT-0001                PREREGISTERED_TRIGGER_ABSENT_NOT_RUN / MERGED #111
Phase 0-8 drift audit                  COMPLETE / PASS_FINAL_HEAD_VERIFIED / DRIFT_2 REMEDIATED
Program epistemic governance v1        PREPARED / IMPLEMENTATION NOT STARTED
production authorization               NONE
first real short authorization         NONE
```

## Program-Level Epistemic Governance v1 — next program

This is a governance upgrade, not a new alpha/strategy program.

The next session must first audit and reuse existing experiment-level governance, then add the minimum sufficient program-level controls for:

- research-family accounting;
- typed research-lineage DAG;
- structured validation/data exposure events;
- dataset-slice identity and contamination accounting;
- researcher degrees of freedom and trial/variant counts;
- prospective research data budgets;
- primary metrics and stopping rules;
- negative-result preservation and same-line-tuning controls;
- retrospective legacy mapping with `UNKNOWN` for unrecoverable history;
- research-governance debt;
- machine-auditable provenance and deterministic program audit;
- fail-closed CI rules for future research;
- lightweight edge-registry schema without inventing new alpha.

Do not overload `config/decision_registry.json` with every trial/exposure record. Keep decision/production authority separate from detailed research/exposure facts while linking them by stable IDs.

Do not treat `validation_peek_count` as the only source of truth. Prefer structured exposure events that record what information was released; derive simple peek counts from those events.

Do not allow an experiment to assert `independent_edge=true` by declaration. Independence/incrementality must be an evidence conclusion against existing information families.

Do not introduce a single 0–100 governance score or complexity score.

## Legacy / retrospective boundary

The new framework must be prospective. Existing immutable experiments retain their historical states and are not retroactively claimed to have satisfied the new framework.

At implementation start:

1. re-read canonical `main`;
2. verify no new strategy research has occurred after the prepared handoff;
3. freeze an explicit `legacy_boundary_commit` and `research_governance_version`;
4. map prior experiments conservatively as legacy/retrospective records;
5. write `UNKNOWN` where historical trial count, validation exposure or researcher decisions cannot be recovered.

Historical research branches are intentionally retained until retrospective provenance mapping is complete.

## Phase 6 sequencing

Phase 6 implementation/replay is complete. Its frozen elapsed requirement remains:

```text
minimum elapsed calendar days   14
minimum scheduled decisions     10
status before evidence exists   MEASUREMENT_INCONCLUSIVE_TIME_DEPENDENT
```

Do not manufacture historical substitutes for elapsed time.

Further Phase 6 observation-infrastructure work should resume **after** Program-Level Epistemic Governance v1 is merged so genuinely future observations can enter the new evidence/provenance model from inception.

## Phase 7 boundary

The Phase 7 readiness gate is implemented, not activated. Current mode is `MONITOR_ONLY`.

Do not transition to ACTIVE until the complete launch checklist is satisfied, including Phase 6 elapsed evidence and explicit owner approval. Human approval remains required for:

```text
MONITOR_ONLY -> ACTIVE
FLAT -> LONG
FLAT -> SHORT
first short exposure of a new bear phase
```

Credentials, `TRADING_MODE=trade`, a durable ledger or a historical mainnet confirmation string are not substitutes for production authorization.

## Phase 8 boundary

`BEAR-SHORT-0001` is preregistered but trigger-absent. Do not run trigger-dependent economics until a repository-valid `CONFIRMED_BEAR_TRANSITION_ARTIFACT` exists under the frozen contract.

Until then:

```text
status                       PREREGISTERED_TRIGGER_ABSENT_NOT_RUN
short_ready                  false
production_authorized        false
first_real_short_authorized  false
```

A subjective market view must not be used as the trigger.

## Exact execution order

```text
1. VERIFY CANONICAL MAIN AND READ THE PROGRAM-GOVERNANCE V1 HANDOFF
2. PG0: AUDIT EXISTING GOVERNANCE / OVERLAP / LEGACY EVIDENCE BEFORE DESIGN
3. PG1: FREEZE GOVERNANCE SEMANTICS, VERSION AND LEGACY BOUNDARY
4. PG2: ADD MINIMAL MACHINE-READABLE REGISTRIES / SCHEMAS
5. PG3: ADD VALIDATOR + DETERMINISTIC PROGRAM AUDIT
6. PG4: RETROSPECTIVELY MAP LEGACY RESEARCH CONSERVATIVELY; UNKNOWN MEANS UNKNOWN
7. PG5: ENFORCE FUTURE-RESEARCH CI FAIL-CLOSED RULES
8. PG6: UPDATE HANDOFF DOCS AND PROVE NO STRATEGY / PARAMETER / AUTHORITY DRIFT
9. ONLY AFTER GOVERNANCE V1 MERGES, RESUME REAL PHASE-6 ZERO-AUTHORITY ELAPSED OBSERVATION
10. REQUIRE EXPLICIT HUMAN APPROVAL BEFORE MONITOR_ONLY -> ACTIVE OR ZERO -> RISK
11. WAIT FOR THE FROZEN CONFIRMED-BEAR TRIGGER BEFORE BEAR-SHORT-0001 ECONOMICS
12. REQUIRE A SEPARATE HUMAN GATE BEFORE ANY FIRST REAL SHORT
```

## Explicit non-goals for the next session

Do **not** start:

```text
Supertrend research
funding/OI alpha research
new relative-strength research
new asset-allocation research
new leverage research
new short-model research
portfolio optimization
production deployment
```

Do not modify BRRK-0011, BNB membership, strategy parameters, transaction-cost assumptions, frozen research results or production authority as part of the governance upgrade.
