# BRRK Current State

Last updated: 2026-08-09  
Handoff branch: `phase-6/live-observation-plumbing`  
Authoritative baseline main at branch creation: `443edc3adc0decf660daff608849b07764115cb0`  
Latest merged PR at branch creation: **#141**

Status: **authoritative current-state handoff**

## Executive state

```text
Phase 0-3                         COMPLETE / MERGED
Phase 4 leverage research         FAIL_STOP / NO_PROMOTION
P5.5                              COMPLETE / IMMUTABLE / NO_PROMOTION / FAIL_STOP
P5.6                              BLOCKED / NO ELIGIBLE CANDIDATE
F27 idle-cash measurement         R2 AUTHORITATIVE / R1 SUPERSEDED-PRESERVED
F7 metrics convergence            PARTIAL
Idle Cash execution feasibility   NOT_FEASIBLE_ON_HYPERLIQUID_STANDARD / FUTURE_OPTION_ONLY
Phase 6 implementation/replay     PASS_SHADOW_ONLY_IMPLEMENTATION_REPLAY
Phase 6 identity                  VERIFIED / FROZEN / STANDARD-DISABLED
Phase 6 pre-arm dependencies      4/4
Phase 6 ARM owner authorization   GRANTED 2026-08-09
Phase 6 ARM plumbing              PR #142 / UNARMED PREFLIGHT FIRST
Phase 6 live elapsed evidence     MEASUREMENT_INCONCLUSIVE_TIME_DEPENDENT / CLOCK NOT STARTED
Phase 7                           MONITOR_ONLY / LAUNCH BLOCKED
Phase 8                           TRIGGER ABSENT / NOT RUN
Production                        NO_CHANGE
```

## Phase 6 bound identity

`research/governance/phase6_live_account_identity_contract.json` is authoritative.

```text
status                             FROZEN_VERIFIED_READ_ONLY_IDENTITY
account role                       user
userAbstraction                    disabled
identity_frozen                    true
pre-arm dependencies               4/4
```

The exact public address and read-only evidence are stored only in the identity contract. No private key, seed phrase, API private key or signing credential is stored.

## Current ARM transition

The owner has explicitly authorized Phase-6 ARM and future-only shadow evidence collection. That authorization permits the necessary zero-authority collector/schedule governance changes, but **does not** authorize production, signing, order submission, withdrawal, transfer or Phase-7 launch.

PR #142 intentionally splits implementation from activation:

```text
step 1  merge zero-authority collector + workflow_dispatch plumbing
step 2  run one NON-CREDITING live preflight on merged main
step 3  only if preflight passes, commit the actual ARM activation
step 4  enable daily schedule + elapsed-evidence credit
step 5  first creditable decision = first genuine scheduled 00:00 UTC decision after ARM marker
```

The plumbing collector reuses the frozen chain:

```text
P3.1 canonical Binance UTC daily data
-> P3.2 BRRK-0011 target
-> independent frozen research reference parity
-> P3.3 rebalance control
-> Hyperliquid public/read-only Standard account valuation
-> frozen P2.4 read-only route projection
-> Phase-6 hypothetical shadow record
-> create-only GitHub Actions evidence artifact
-> separate hash-bound receipt artifact
```

Raw public/read-only response bytes are preserved before parsing. The collector imports no executor, signer or order-submission path.

### Current preflight state

Until the activation change merges, the authoritative gate remains:

```text
status                             PREACTIVATION_READY_AWAITING_SEPARATE_ARM
collector_armed                    false
schedule_configured                false
elapsed_evidence_credit_authorized false
armed_commit                       null
clock                              NOT STARTED
```

The manual preflight is explicitly non-crediting. It exists to catch external blockers such as unusable account valuation or live data before the first scheduled decision.

## Frozen Phase 6 acceptance

```text
minimum elapsed calendar days       14
minimum genuine scheduled decisions 10
minimum emergency drills             1
critical reconciliation errors       0
unexplained target drift              0
schedule failures                     0
```

Historical backfill/replay, CI replay, workflow reruns, duplicate decision timestamps and manual dispatch create no scheduled-decision credit. A manual emergency drill may count only toward the drill requirement after ARM when its durable evidence satisfies the frozen contract.

## Evidence backend

`PHASE6-LIVE-EVIDENCE-BACKEND-V1` remains the authority:

- GitHub Actions artifact v4;
- 90-day retention;
- overwrite disabled;
- raw market/account/route bytes preserved;
- input provenance manifest SHA256 required;
- shadow record SHA256 required;
- evidence bundle uploaded before receipt;
- separate receipt artifact required before any credit;
- artifact/log/ephemeral-runner data alone creates no credit.

PR #142 does not flip this backend into credit-active mode; that occurs only in the subsequent activation change after preflight success.

## Other frozen research/governance state

### F27

`research/results/idle_cash_credit_0027r2.json` is authoritative; R1 is superseded but preserved. BRRK R2 headline remains:

```text
mean idle cash                24.5700%
raw CAGR                      65.1661%
credited CAGR                 66.8068%
CAGR delta                    +1.6407 pp
```

### F7 / LEVERAGE-0040

F7 remains `PARTIAL`. Shared calendar-span metrics exist, while immutable historical studies retain their frozen local conventions. LEVERAGE-0040 remains `FAIL_STOP / NO_PROMOTION`; its study-local observation-count CAGR is not rewritten.

### Idle Cash

```text
NOT_FEASIBLE_ON_HYPERLIQUID_STANDARD
FUTURE_OPTION / NOT_AUTHORIZED
REQUIRES SEPARATE DESIGN + CONTRACT + APPROVAL
```

### Right-tail research admission

Future new Research IDs capable of lowering canonical BRRK gross must satisfy both:

```text
canonical best-20 log-growth retention >= 90%
net summed daily-return delta > 0
```

Historical immutable evidence is not retrospectively rescored.

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

Phase-6 shadow observation is read-only and hypothetical. It must never import private-key material, sign orders, submit orders, withdraw, transfer or activate production.

## Human-control boundaries that remain

ARM owner authorization has been granted for this transition, but these later gates remain explicit:

- Phase-7 launch approval;
- `MONITOR_ONLY -> ACTIVE`;
- `FLAT -> LONG`;
- `FLAT -> SHORT`;
- first short exposure of a new confirmed bear phase.

## Current drift assessment

`DRIFT_0`.

PR #142 adds only zero-authority governance orchestration and the canonical workflow dispatch needed for a live preflight. It does not change strategy mathematics, immutable economic results, product config, production authority, gross cap or execution submission capability.

## Exact next task

1. Make PR #142 green and merge it.
2. Dispatch `Research governance core` once on main with `emergency_drill=false` as a **non-crediting preflight**.
3. Inspect the live preflight result. If it fails, stop on the external fact and fix only that prerequisite.
4. If it passes, proceed under the already-granted ARM authorization to the activation change: freeze the ARM marker, set collector/schedule/elapsed-credit active, add the daily schedule, and keep every production/signing/order flag false.
