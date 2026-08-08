# BRRK Next Steps

Last updated: 2026-08-08

## Current instruction

**Program-Level Epistemic Governance v1 is complete across PG0-PG6. The next dependency is genuine future Phase 6 zero-authority elapsed observation under the new provenance/evidence model. Production remains unauthorized.**

Canonical governance closeout:

- `docs/PROGRAM_LEVEL_EPISTEMIC_GOVERNANCE_V1_FINAL_REPORT_2026-08-08.md`
- `docs/PROGRAM_GOVERNANCE_V1_SPEC_2026-08-08.md`
- `config/research_governance_v1.json`
- `config/research_registry.json`
- `config/dataset_exposure_registry.json`
- `config/edge_registry.json`

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
Program epistemic governance v1        PG0-PG6 COMPLETE / CI-ENFORCED / NO-DRIFT CLOSEOUT
production authorization               NONE
first real short authorization         NONE
```

## Governance v1 closeout

Governance v1 is an institutional research-control layer, not a new alpha program. It extends existing experiment contracts and keeps research, decision and production authority separate.

The frozen prospective boundary is:

```text
legacy_boundary_commit = 896cbd123b7a0c38943815dd802f0f9dcd12e1c2
research_governance_version = 1
```

Implemented controls include:

- research-family accounting and typed lineage DAG;
- explicit variant/trial budgets and researcher degrees of freedom;
- structured dataset/exposure semantics;
- prospective data budgets including SEALED and TEMPORALLY_UNSEEN evidence;
- preservation of negative results and same-line tuning ancestry;
- 17 conservative `RETROSPECTIVE_LEGACY` records;
- six explicit legacy governance-debt classes;
- deterministic registry validation and program audit;
- exact-PR-diff fail-closed future-research registration enforcement;
- final legacy-boundary-to-HEAD no-drift regression;
- evidence-gated Edge Registry admission with no retroactive legacy edge claims.

The Dataset Exposure Registry remains empty for retrospective history because historical release/consumption facts cannot be reconstructed truthfully. The Edge Registry remains empty because v1 does not infer independent/incremental information from legacy naming or isolated historical PASS results.

A governance audit `WARNING` caused by explicit legacy debt is expected. Do not erase that debt by guessing missing historical facts.

## Phase 6 — exact next dependency

Phase 6 implementation/replay is complete. The frozen live-observation requirement remains:

```text
minimum elapsed calendar days   14
minimum scheduled decisions     10
status before evidence exists   MEASUREMENT_INCONCLUSIVE_TIME_DEPENDENT
signature_authorized            false
order_submission_authorized     false
production_authorized           false
```

Resume only **real, forward Phase 6 zero-authority observation**. Genuinely future observations should be recorded under Governance v1 provenance from inception.

Do not manufacture, replay, interpolate or backfill elapsed time. Historical/CI replay cannot satisfy the elapsed-calendar requirement.

The observation program must remain economically passive: it may read state and compute hypothetical decisions/orders, but it must not sign or submit production orders.

## Future research rule

Any material post-boundary result-bearing research must be registered prospectively as exactly one `PROGRAM_GOVERNED_V1` record before formal results are consumed.

The record must freeze the required governance fields, including primary metric, data budget, variant budget, stopping/pass/fail rules, lineage/data references, researcher decision surface, governed path ownership and `production_authorized=false`.

Different experiment IDs or cosmetic parameter changes do not reset result-informed history into independence. Failed ancestors remain part of the evidence lineage.

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
trigger_present              false
short_ready                  false
production_authorized        false
first_real_short_authorized  false
```

A subjective market view must not be used as the trigger.

## Exact execution order

```text
1. KEEP PROGRAM-LEVEL EPISTEMIC GOVERNANCE V1 CI/REGISTRIES AUTHORITATIVE FOR FUTURE RESEARCH
2. RESUME REAL PHASE-6 ZERO-AUTHORITY ELAPSED OBSERVATION
3. RECORD ONLY GENUINELY FORWARD OBSERVATIONS; DO NOT BACKFILL THE 14-DAY / 10-DECISION REQUIREMENT
4. KEEP SIGNING / ORDER SUBMISSION / PRODUCTION AUTHORITY FALSE THROUGH PHASE 6
5. IF NEW FORMAL RESEARCH IS NEEDED, REGISTER PROGRAM_GOVERNED_V1 BEFORE RESULT-BEARING WORK
6. AFTER PHASE-6 ELAPSED + QUALITY EVIDENCE EXISTS, RE-EVALUATE THE EXISTING PHASE-7 READINESS CHECKLIST
7. REQUIRE EXPLICIT HUMAN APPROVAL BEFORE MONITOR_ONLY -> ACTIVE OR ZERO -> RISK
8. WAIT FOR THE FROZEN CONFIRMED-BEAR TRIGGER BEFORE BEAR-SHORT-0001 ECONOMICS
9. REQUIRE A SEPARATE HUMAN GATE BEFORE ANY FIRST REAL SHORT
```

## Explicit non-goals

Do **not** start as part of Phase 6 observation:

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

Do not modify BRRK-0011, BNB membership, strategy parameters, transaction-cost assumptions, frozen research results or production authority. Governance v1 itself confers no production authorization.
