# BRRK Next Steps

Last updated: 2026-08-08

## Current instruction

**Close the final Phase-6 pre-arm dependency without weakening Governance v1 or fabricating account state. Production remains unauthorized.**

Program-Level Epistemic Governance v1 is complete across PG0-PG6. Stablecoin Stage-1 is terminal FAIL. Phase-6 implementation/replay passed shadow-only, but genuine elapsed evidence has not started because the collector is still unarmed.

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
Phase 6 durable evidence backend       FROZEN / ACTIONS_ARTIFACT_V4 / 90D / NO CREDIT / MERGED #133
Phase 6 valuation contract             PHASE6-LIVE-VALUATION-V1 / PR #134 CANDIDATE
Phase 6 pre-arm dependencies           3/4 FROZEN IN #134 CANDIDATE / ACCOUNT IDENTITY REMAINS
Phase 7 readiness gate                 IMPLEMENTED / MERGED #110 / LAUNCH BLOCKED
Phase 7 mode                           MONITOR_ONLY
Phase 8 BEAR-SHORT-0001                PREREGISTERED_TRIGGER_ABSENT_NOT_RUN / MERGED #111
Program epistemic governance v1        PG0-PG6 COMPLETE / CI-ENFORCED / NO-DRIFT
Stablecoin liquidity Stage-1           FAIL_NO_INCREMENTAL_INFORMATION / NO_PROMOTION / TERMINAL STOP
production authorization               NONE
first real short authorization         NONE
```

## Phase 6 pre-arm dependency table

Four dependencies govern whether a future scheduled collector may ever be armed:

1. **Observation account identity — UNRESOLVED.** One exact public read-only Hyperliquid master/subaccount address must be frozen and verified. It must be the actual observed account, not an agent-wallet identity. Do not invent it and do not derive it from a private key merely to satisfy the gate.
2. **Current-position/equity valuation contract — PR #134 CANDIDATE.** `PHASE6-LIVE-VALUATION-V1` supports only explicit Hyperliquid Standard mode (`userAbstraction=disabled`), maps verified canonical spot + signed perp exposure into existing P3.3 inputs, and fails closed on unsupported modes/assets. It becomes authoritative only after final green CI and merge.
3. **Durable create-only evidence backend — FROZEN / MERGED #133.** GitHub Actions Artifact v4, 90-day retention, overwrite false, evidence bundle + hash-bound receipt before credit.
4. **Schedule/duplicate-credit rule — FROZEN.** Manual dispatch is not a scheduled decision; reruns and duplicate decision timestamps create no new credit; a manual emergency drill may count only toward the drill requirement.

The current gate remains:

```text
collector_armed                    false
schedule_configured                false
elapsed_evidence_credit_authorized false
dependencies_ready                 false
production_authorized              false
signature_authorized               false
order_submission_authorized        false
```

## PR #134 closeout sequence

```text
1. KEEP THE VALUATION CONTRACT LIMITED TO STANDARD MODE; DO NOT BROADEN IT TO FIT AN UNKNOWN FUTURE ACCOUNT
2. KEEP BNB SPOT FORBIDDEN / PERP_ONLY_DEFAULT
3. KEEP P3.2 TARGET AND P3.3 CONTROL ECONOMICS UNCHANGED
4. RUN FINAL-HEAD GOVERNANCE / NO-DRIFT / P3.2 PARITY / PHASE-6 SAFETY CI
5. MERGE #134 ONLY WITH EXPECTED-HEAD PROTECTION WHEN ALL REQUIRED CHECKS ARE GREEN
6. VERIFY NEW MAIN AND RECHECK PRODUCT / RESEARCH / PRODUCTION AUTHORITY INVARIANTS
```

No failed or intermediate workflow is relabeled as PASS.

## Unique next task after #134

Freeze one exact **public read-only Hyperliquid observation account identity**.

Required validation before it can be marked frozen:

```text
address is explicit and exact
address is the actual master/subaccount being observed
address is not an agent-wallet identity
userAbstraction == disabled
account fits PHASE6-LIVE-VALUATION-V1 supported surfaces
no unsupported nonzero assets/surfaces are silently ignored
no private key is required or consumed
```

If the account is Unified Account, Portfolio Margin, `default`, DEX abstraction, or otherwise outside V1, the correct result is **BLOCKED / INCOMPATIBLE**, not a post-observation expansion of the valuation contract.

## Arm boundary after 4/4 dependencies

Even after the account identity is frozen, that fact alone does not start elapsed credit.

A separate prospective arm change must explicitly set the future-only collector state. The first eligible scheduled decision is:

```text
FIRST 00:00 UTC DECISION STRICTLY AFTER THE ARM COMMIT TIMESTAMP
```

Forbidden credit:

```text
historical backfill
historical replay
CI replay
workflow rerun as a new decision
duplicate decision timestamp
manual dispatch as a scheduled decision
```

Phase-6 acceptance remains:

```text
minimum elapsed calendar days   14
minimum scheduled decisions     10
minimum emergency drills        1
critical reconciliation errors  0
unexplained target drift         0
schedule failures                0
```

## Research / product boundaries while Phase 6 is unresolved

Do not start any substitute result-bearing work merely because the observation account is pending:

```text
Stablecoin rescue research
Stablecoin Stage-2
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

`STABLECOIN-LIQUIDITY-0001` remains terminal and cannot be rerun/rescued under the same ID. `ONCHAIN-HOLDER-COST-0001` remains only a backlog idea.

Do not modify BRRK-0011, BTC/ETH/SOL/BNB membership, XRP feature-only role, BNB perp-only policy, transaction-cost assumptions, P3.2/P3.3 economics, immutable research results or production authority.

## Phase 7 / 8 boundaries

Phase 7 remains `MONITOR_ONLY` and `production_authorized=false`. Do not transition to ACTIVE until the complete readiness checklist is satisfied, including genuine Phase-6 elapsed evidence and explicit owner approval.

`BEAR-SHORT-0001` remains `PREREGISTERED_TRIGGER_ABSENT_NOT_RUN`. A subjective market view cannot substitute for `CONFIRMED_BEAR_TRANSITION_ARTIFACT`, and no first real short may occur without the separate human gate.

## After Phase-6 collection becomes operational

Resume the infrastructure roadmap in order:

```text
1. formal research lifecycle/state-machine enforcement
2. Research Queue + trial/overlap accounting
3. only then consider a new prospectively registered result-bearing research family
```

Do not reorder those steps merely to generate new research results sooner.