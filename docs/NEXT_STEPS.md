# BRRK Next Steps

Last updated: 2026-08-08

## Current instruction

**Phase 0–8 drift audit/remediation is complete. Do not start another strategy implementation phase. The next real dependency is Phase 6 zero-authority elapsed-shadow evidence. Production remains unauthorized.**

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
production authorization               NONE
first real short authorization         NONE
```

## Audit closeout

Machine contract: `config/phase0_8_drift_audit.json`. Evidence report: `docs/PHASE_0_8_DRIFT_AUDIT_2026-08-08.md`.

Completed remediation:

- legacy BTC-only normal service cannot add directional risk merely because `TRADING_MODE=trade`;
- same-direction risk reduction and emergency-flat capability remain available;
- legacy production-facing `NORMAL_BETA_CAP` is capped at `1.0`;
- authoritative handoff documentation reflects completed Phase 6/7/8 work;
- cross-phase regression tests pin production policy, LEVERAGE-0040 digest and Phase 6/7/8 boundaries.

The audit closeout does not authorize production trading.

## Phase 6 evidence accumulation — current dependency

Phase 6 implementation/replay is complete. Do **not** rebuild the shadow harness or manufacture historical substitutes for elapsed time.

The remaining dependency is the frozen live observation requirement in `config/phase6_shadow_contract.json`:

```text
minimum elapsed calendar days   14
minimum scheduled decisions     10
status before evidence exists   MEASUREMENT_INCONCLUSIVE_TIME_DEPENDENT
```

Continue the zero-authority observation mechanism and record real evidence only. Phase 6 shadow may read real account/market/order-book state and calculate hypothetical actions, but cannot sign or submit orders.

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
1. VERIFY MAIN CONTAINS THE PHASE 0-8 AUDIT CLOSEOUT AND POLICY INVARIANTS
2. CONTINUE REAL PHASE-6 ZERO-AUTHORITY ELAPSED OBSERVATION
3. WHEN PHASE-6 EVIDENCE ACTUALLY PASSES, REVIEW PHASE-7 CHECKLIST
4. REQUIRE EXPLICIT HUMAN APPROVAL BEFORE MONITOR_ONLY -> ACTIVE OR ZERO -> RISK
5. WAIT FOR THE FROZEN CONFIRMED-BEAR TRIGGER BEFORE BEAR-SHORT-0001 ECONOMICS
6. REQUIRE A SEPARATE HUMAN GATE BEFORE ANY FIRST REAL SHORT
```
