# BRRK Next Steps

Last updated: 2026-08-08

## Current instruction

**Program-Level Epistemic Governance v1 is complete across PG0-PG6. Stablecoin Stage-1 is terminal FAIL. The highest-priority dependency is to make genuine future Phase 6 zero-authority elapsed observation operational without weakening no-drift or fabricating account/evidence semantics. Production remains unauthorized.**

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
P5.6 integration                       BLOCKED / NO ELIGIBLE CANDIDATE
Phase 6 implementation/replay          PASS_SHADOW_ONLY_IMPLEMENTATION_REPLAY / MERGED #109
Phase 6 live elapsed evidence          MEASUREMENT_INCONCLUSIVE_TIME_DEPENDENT / CLOCK NOT ARMED
Phase 6 observation preactivation      PREACTIVATION_BLOCKED_FAIL_CLOSED
Phase 6 durable evidence backend       FROZEN / ACTIONS_ARTIFACT_V4 / 90D / NO CREDIT
Phase 7 readiness gate                 IMPLEMENTED / MERGED #110 / LAUNCH BLOCKED
Phase 7 mode                           MONITOR_ONLY
Phase 8 BEAR-SHORT-0001                PREREGISTERED_TRIGGER_ABSENT_NOT_RUN / MERGED #111
Program epistemic governance v1        PG0-PG6 COMPLETE / CI-ENFORCED / NO-DRIFT CLOSEOUT
Stablecoin liquidity Stage-1           FAIL_NO_INCREMENTAL_INFORMATION / NO_PROMOTION / TERMINAL STOP
production authorization               NONE
first real short authorization         NONE
```

## Corrected governance/data state

The Dataset Exposure Registry is **not globally empty**. It contains the prospectively recorded Stablecoin reconstructed-history validation slice and RAW_DATA exposure created during `STABLECOIN-LIQUIDITY-0001`. Legacy retrospective exposure remains intentionally unbackfilled where historical facts cannot be reconstructed truthfully.

The Edge Registry remains empty. Stablecoin failed its preregistered incremental-information test and created no edge; governance v1 also does not infer edges retroactively from legacy naming or historical PASS labels.

Stablecoin is closed at its frozen stopping point. Do not rerun it, test rescue lags/alphas/horizons/representations under the same ID, start Stage-2, or create a Stablecoin multiplier/portfolio integration.

## Phase 6 — actual blocker found by live-state audit

The frozen Phase 6 contract still requires:

```text
minimum elapsed calendar days   14
minimum scheduled decisions     10
minimum emergency drills        1
critical reconciliation errors  0
unexplained target drift         0
schedule failures                0
signature_authorized             false
order_submission_authorized      false
production_authorized            false
```

The existing `.github/workflows/phase6-integrated-shadow.yml` is implementation/replay safety CI only. It has PR/push/manual triggers, no scheduled future collector and no durable elapsed-evidence persistence. Therefore no automatic Phase-6 elapsed evidence has been accumulating.

Governance v1 no-drift also forbids casually adding a new execution path under `beta_bot/` or mutating the frozen strategy/execution blobs. The correct place for elapsed-observation provenance control is the already-authorized `research/governance/**` plane.

`research/governance/phase6_live_observation_gate.json` and `phase6_live_observation_gate.py` freeze a fail-closed **preactivation** state. The gate does not start the elapsed clock.

`research/governance/phase6_live_evidence_contract.json` and `phase6_live_evidence.py` now freeze the durable storage/provenance mechanism to GitHub Actions Artifact v4 with 90-day retention, `overwrite=false`, hard failure on empty upload, immutable artifact ID/URL/digest, exact raw-input/provenance/shadow-record evidence categories and a separately uploaded hash-bound receipt. This closes the storage semantic only; it creates zero elapsed credit.

## Required before the collector may be armed

Four pre-arm dependencies are tracked. Two are now frozen and two remain unresolved:

1. **Observation account identity — UNRESOLVED.** Select and freeze one explicit read-only account identity. Never invent account state.
2. **Current-position/equity valuation contract — UNRESOLVED.** Freeze how the Phase-6 observation portfolio converts the permitted account surfaces into the P3.3 `current_positions_notional_usd` and `account_equity_usd`, including spot/perp treatment. This is operational measurement semantics, not a new alpha rule.
3. **Durable create-only evidence backend — FROZEN.** `GITHUB_ACTIONS_ARTIFACT_V4`, retention 90 days, overwrite false, evidence bundle + receipt required before credit. Runner files/logs/step summaries alone are not evidence.
4. **Schedule/duplicate rule — FROZEN.** Manual dispatch does not count as a scheduled decision; reruns and duplicate decision timestamps do not create new credit; a manual emergency drill may count only toward the drill requirement.

When a later prospective change arms the collector, its first eligible decision is the first canonical `00:00 UTC` decision **strictly after the arm commit timestamp**. Nothing before that point can be backfilled or credited.

## Execution order

```text
1. KEEP PROGRAM-LEVEL EPISTEMIC GOVERNANCE V1 + NO-DRIFT AUTHORITATIVE
2. KEEP THE MERGED PHASE-6 PREACTIVATION GATE FAIL-CLOSED
3. KEEP PHASE6-LIVE-EVIDENCE-BACKEND-V1 FROZEN; DO NOT CALL ITS EXISTENCE ELAPSED EVIDENCE
4. FREEZE ONE READ-ONLY OBSERVATION ACCOUNT IDENTITY
5. FREEZE CURRENT-POSITION / ACCOUNT-EQUITY VALUATION SEMANTICS WITHOUT CHANGING P3.2/P3.3 ECONOMICS
6. PROSPECTIVELY ARM THE FUTURE-ONLY COLLECTOR IN A SEPARATE CHANGE
7. CREDIT ONLY GENUINELY FUTURE SCHEDULED DECISIONS AFTER THE ARM COMMIT AND ONLY AFTER EVIDENCE BUNDLE + RECEIPT ARCHIVE SUCCEED
8. NEVER BACKFILL / REPLAY-CREDIT / RERUN-CREDIT / DUPLICATE-CREDIT
9. ACCUMULATE >=14 ELAPSED DAYS, >=10 SCHEDULED DECISIONS, >=1 EMERGENCY DRILL, WITH ALL FROZEN QUALITY COUNTS AT ZERO
10. KEEP PHASE 7 MONITOR_ONLY UNTIL PHASE-6 EVIDENCE + COMPLETE CHECKLIST + EXPLICIT OWNER APPROVAL
11. AFTER THE PHASE-6 COLLECTION PATH IS OPERATIONAL, IMPLEMENT THE FORMAL RESEARCH LIFECYCLE/STATE MACHINE
12. THEN IMPLEMENT RESEARCH QUEUE + TRIAL/OVERLAP ACCOUNTING
13. ONLY AFTER THOSE INFRASTRUCTURE LAYERS, CONSIDER A NEW RESULT-BEARING RESEARCH FAMILY THROUGH A NEW PROSPECTIVE ID
14. WAIT FOR THE FROZEN CONFIRMED-BEAR TRIGGER BEFORE BEAR-SHORT-0001 ECONOMICS
15. REQUIRE A SEPARATE HUMAN GATE BEFORE ANY FIRST REAL SHORT
```

## Future research rule

Any material post-boundary result-bearing research must be registered prospectively as exactly one `PROGRAM_GOVERNED_V1` record before formal results are consumed. Different experiment IDs or cosmetic parameter changes do not reset result-informed history into independence; failed ancestors remain part of the evidence lineage.

`ONCHAIN-HOLDER-COST-0001` remains only a backlog idea. It is not started by the Stablecoin closeout or by Phase-6 observation work.

## Phase 7 / 8 boundaries

Phase 7 remains `MONITOR_ONLY` and `production_authorized=false`. Do not transition to ACTIVE until the complete launch checklist is satisfied, including Phase 6 elapsed evidence and explicit owner approval. Credentials, `TRADING_MODE=trade`, a durable ledger or a historical mainnet confirmation string are not substitutes for production authorization.

`BEAR-SHORT-0001` remains `PREREGISTERED_TRIGGER_ABSENT_NOT_RUN`. A subjective market view cannot substitute for `CONFIRMED_BEAR_TRANSITION_ARTIFACT`, and no first real short may occur without the separate human gate.

## Explicit non-goals

Do **not** start as part of Phase 6 observation:

```text
Stablecoin rescue research
Holder Cost research
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
