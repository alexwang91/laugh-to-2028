# BRRK Next Steps

Last updated: 2026-08-09

## Current instruction

**Phase 6 remains 3/4 and identity-unbound. A prior prospective read-only probe in closed, unmerged PR #138 reached a valid `user` role but failed V1 Standard-mode compatibility because `userAbstraction` returned `default`. No address was bound. The next compatible binding still requires an explicit public master/subaccount identity satisfying `userRole=user/subAccount` and `userAbstraction=disabled`. Production remains unauthorized.**

## Immediate state

```text
Phase 6 implementation/replay          PASS_SHADOW_ONLY_IMPLEMENTATION_REPLAY / MERGED #109
Phase 6 live elapsed evidence          MEASUREMENT_INCONCLUSIVE_TIME_DEPENDENT / CLOCK NOT ARMED
Phase 6 durable evidence backend       FROZEN / MERGED #133
Phase 6 valuation contract             PHASE6-LIVE-VALUATION-V1 / MERGED #134
Phase 6 account-identity rules         PHASE6-LIVE-ACCOUNT-IDENTITY-V1 / MERGED #135 / UNBOUND
Phase 6 pre-arm dependencies           3/4 FROZEN
identity blocker                       COMPATIBLE EXPLICIT PUBLIC MASTER/SUBACCOUNT IDENTITY
collector_armed                        false
schedule_configured                    false
elapsed evidence credit                false
Phase 7                                MONITOR_ONLY / LAUNCH BLOCKED
Phase 8                                TRIGGER ABSENT / NOT RUN
production gross cap                   1.0
production_authorized_components = []
production_authorized                  false
signature_authorized                   false
order_submission_authorized            false
```

The PR #138 address must not be copied, inferred, reused or rebound from historical discussion in this docs-only work.

## Future identity action

Use `docs/PHASE6_ADDRESS_BINDING_REQUEST.md`.

A compatible future public identity must:

```text
be the exact observed master/subaccount
match 0x + 40 hex characters
not be an agent/API wallet
not be a vault
userRole = user OR subAccount
userAbstraction = disabled
fit PHASE6-LIVE-VALUATION-V1 Standard semantics
```

An incompatible role or abstraction yields `BLOCKED_INCOMPATIBLE`. Do not relax the contract to make an observed identity fit.

## What happens after identity binding

```text
compatible identity verified
-> non-secret provenance + raw-response digests persisted
-> identity frozen
-> dependencies 4/4
-> STOP
-> separate prospective ARM change
-> collector armed + schedule configured
-> first eligible 00:00 UTC decision strictly after ARM commit
-> future-only shadow evidence
```

`4/4 != CLOCK STARTED`, `IDENTITY BOUND != ARM`, and `ARM != HISTORICAL CREDIT`.

Frozen Phase-6 acceptance:

```text
minimum elapsed calendar days       14
minimum scheduled decisions         10
minimum emergency drills             1
critical reconciliation errors       0
unexplained target drift              0
schedule failures                     0
```

No historical backfill/replay, CI replay, rerun, duplicate timestamp or manual dispatch receives scheduled-decision credit.

## Prospective research admission rule

Any future new Research ID that can reduce canonical BRRK target gross must satisfy `docs/RIGHT_TAIL_PRESERVATION_GATE.md`:

```text
canonical best-20 log-growth retention >= 90%
net summed daily-return delta > 0
```

Both gates must pass. Best-10 and best-50 retention are mandatory reports but have no V1 hard threshold. Historical immutable evidence is excluded from retrospective rescoring.

## Current authorized docs-only sequence

After the Phase-6/right-tail governance PR merges, the exact next task in this work package is:

1. restate F27 documentation from authoritative R2 evidence while leaving R1 immutable;
2. add the verified LEVERAGE-0040 metric-convention footnote without recomputation;
3. correct F7 adoption status from live repository evidence;
4. evaluate Idle Cash execution feasibility against current official Hyperliquid mechanics;
5. update `CURRENT_STATE.md`, run applicable checks, and merge only at `DRIFT_0`.

## Human-control boundaries

Explicit human approval remains required for:

- the future compatible identity owner action;
- the separate Phase-6 ARM transition;
- Phase-7 launch;
- `MONITOR_ONLY -> ACTIVE`;
- `FLAT -> LONG`;
- `FLAT -> SHORT`;
- the first short exposure of a new confirmed bear phase.

Do not substitute Stablecoin rescue, leverage rescue, post-result cap tuning, short research, production deployment, identity probing, collector arming or clock backfill for the current authorized work.
