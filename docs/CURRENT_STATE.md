# BRRK Current State

Last updated: 2026-08-09  
Handoff branch: `phase-6/arm-activation`  
Authoritative baseline main at branch creation: `7520c2e620af2fcd9f407a3bfac9205b84120092`  
Latest merged PR at branch creation: **#142**

Status: **authoritative current-state handoff**

## Executive state

```text
Phase 0-3                         COMPLETE / MERGED
Phase 4 leverage research         FAIL_STOP / NO_PROMOTION
P5.5                              COMPLETE / IMMUTABLE / NO_PROMOTION / FAIL_STOP
F27 idle-cash measurement         R2 AUTHORITATIVE / R1 SUPERSEDED-PRESERVED
F7 metrics convergence            PARTIAL
Idle Cash execution feasibility   NOT_FEASIBLE_ON_HYPERLIQUID_STANDARD / FUTURE_OPTION_ONLY
Phase 6 implementation/replay     PASS_SHADOW_ONLY_IMPLEMENTATION_REPLAY
Phase 6 identity                  VERIFIED / FROZEN / STANDARD-DISABLED
Phase 6 pre-arm dependencies      4/4
Phase 6 ARM owner authorization   GRANTED 2026-08-09
Phase 6 live preflight            PENDING ON ARM ACTIVATION PR / NON-CREDITING
Phase 6 live elapsed evidence     MEASUREMENT_INCONCLUSIVE_TIME_DEPENDENT / CLOCK NOT STARTED
Phase 7                           MONITOR_ONLY / LAUNCH BLOCKED
Phase 8                           TRIGGER ABSENT / NOT RUN
Production                        NO_CHANGE
```

## Bound identity and ARM scope

`PHASE6-LIVE-ACCOUNT-IDENTITY-V1` is frozen to the explicit owner-supplied Hyperliquid master account with:

```text
userRole        user
userAbstraction disabled
identity_frozen true
pre-arm deps    4/4
```

The owner has now explicitly authorized the Phase-6 ARM transition and future-only shadow evidence collection. That authorization permits the zero-authority collector and daily observation schedule required by Phase 6. It does **not** authorize production, signing, order submission, withdrawal, transfer, strategy retuning, or Phase-7 launch.

## ARM activation sequence

PR #142 merged the zero-authority collector plumbing at `7520c2e620af2fcd9f407a3bfac9205b84120092` while keeping the gate unarmed.

The activation branch now uses the pull-request workflow as a real external preflight. A PR event is explicitly diagnostic only and can never receive scheduled-decision or emergency-drill credit.

```text
ARM activation PR opens
-> real public/read-only Hyperliquid + Binance preflight runs
-> PR preflight artifact only / zero credit
-> if preflight FAILS: stop before ARM
-> if preflight PASSES: create durable ARM marker commit
-> set collector_armed=true
-> set schedule_configured=true
-> set elapsed_evidence_credit_authorized=true
-> add daily 00:00 UTC schedule
-> merge while preserving ARM marker commit
-> first eligible scheduled decision strictly after ARM marker
```

Until the preflight passes and the activation fields are committed, the authoritative main state remains:

```text
status                             PREACTIVATION_READY_AWAITING_SEPARATE_ARM
collector_armed                    false
schedule_configured                false
elapsed_evidence_credit_authorized false
armed_commit                       null
clock                              NOT STARTED
```

## Zero-authority live collector

The collector reuses the frozen chain rather than introducing new strategy logic:

```text
P3.1 canonical Binance UTC daily data
-> P3.2 BRRK-0011 target
-> independent research-reference parity
-> P3.3 rebalance control
-> Hyperliquid Standard read-only account valuation
-> P2.4 read-only route projection
-> Phase-6 hypothetical shadow record
-> create-only evidence artifact
-> separate hash-bound receipt artifact
```

Raw public/read-only response bytes are preserved before parsing. The collector imports no executor, signer, private-key or order-submission path.

## Frozen Phase 6 acceptance

```text
minimum elapsed calendar days       14
minimum genuine scheduled decisions 10
minimum emergency drills             1
critical reconciliation errors       0
unexplained target drift              0
schedule failures                     0
```

Historical backfill/replay, CI replay, workflow reruns, duplicate decision timestamps, pull-request preflights and manual dispatch create no scheduled-decision credit. A manual emergency drill may count only toward the drill requirement after ARM and only with the frozen durable evidence rules.

## Evidence backend

`PHASE6-LIVE-EVIDENCE-BACKEND-V1` remains authoritative:

- GitHub Actions artifact v4;
- 90-day retention for creditable evidence;
- overwrite disabled;
- raw market/account/route bytes preserved;
- input-provenance and shadow-record SHA256 required;
- evidence artifact must upload before receipt creation;
- separate receipt artifact must upload before credit;
- logs, ephemeral files, PR diagnostics and failed uploads create no credit.

## Production / security authority

```text
directional core                  BRRK-0011
long universe                     BTC / ETH / SOL / BNB
XRP                               feature-only
primary venue                     Hyperliquid
decision boundary                 00:00 UTC
BNB route policy                  PERP_ONLY_DEFAULT
production gross cap              1.0
production_authorized_components = []
production_authorized             false
signature_authorized              false
order_submission_authorized       false
first real short authority        NONE
```

## Other frozen decisions

- F27 R2 remains authoritative; R1 remains superseded-preserved.
- F7 remains `PARTIAL`; immutable studies are not rewritten.
- LEVERAGE-0040 remains `FAIL_STOP / NO_PROMOTION`.
- Idle Cash remains `NOT_FEASIBLE_ON_HYPERLIQUID_STANDARD / FUTURE_OPTION / NOT_AUTHORIZED`.
- Future new Research IDs capable of lowering canonical BRRK gross remain subject to the frozen right-tail gate: best-20 log-growth retention >=90% **and** net summed daily-return delta >0.

## Human-control boundaries that remain

ARM authorization is granted for this transition. Later explicit human gates remain:

- Phase-7 launch approval;
- `MONITOR_ONLY -> ACTIVE`;
- `FLAT -> LONG`;
- `FLAT -> SHORT`;
- first short exposure of a new confirmed bear phase.

## Current drift assessment

`DRIFT_0`.

The activation work changes only Phase-6 zero-authority observation governance/workflow state. Strategy mathematics, immutable economic results, production config, gross cap and execution submission capability remain unchanged.

## Exact next task

1. Open the ARM activation PR and require the real non-crediting PR preflight to run.
2. If the external preflight fails, stop before ARM and resolve only the evidenced prerequisite.
3. If it passes, create the prospective ARM marker and activation fields, add the daily `00:00 UTC` schedule, rerun all CI/preflight, and merge preserving the marker commit.
4. Do not claim elapsed credit until a genuine post-ARM scheduled run successfully uploads both evidence and receipt artifacts.
