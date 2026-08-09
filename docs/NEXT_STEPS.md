# BRRK Next Steps

Last updated: 2026-08-09

## Current instruction

**Phase-6 ARM has been explicitly owner-authorized and the activation package is in PR #143. A real public/read-only preflight passed. After PR #143 merges to `main` with the ARM marker preserved, the next scheduled work is automatic future-only shadow observation at `00:00 UTC` daily. Do not backfill missed timestamps and do not infer any production or Phase-7 authority from ARM.**

## Immediate state after PR #143 activation merges

```text
Phase 6 implementation/replay          PASS_SHADOW_ONLY_IMPLEMENTATION_REPLAY
Phase 6 account identity               VERIFIED + FROZEN / user / disabled
Phase 6 pre-arm dependencies           4/4
ARM owner authorization                GRANTED
ARM marker                              cbd58adb05187651ca72d67900a0ccbbd3e83b1e
live preflight                          PASS / workflow 31316348226 / ZERO CREDIT
observation gate                        ARMED_FUTURE_ONLY_OBSERVATION_ACTIVE
collector_armed                         true
schedule_configured                     true
daily schedule                          0 0 * * * UTC
elapsed evidence credit authorized      true
evidence backend                        ARMED_COLLECTING_FUTURE_ONLY
Phase 6 elapsed result                  MEASUREMENT_INCONCLUSIVE_TIME_DEPENDENT
Phase 7                                 MONITOR_ONLY / LAUNCH BLOCKED
production gross cap                    1.0
production_authorized_components = []
production_authorized                   false
signature_authorized                    false
order_submission_authorized             false
```

The bound public account is recorded in the identity contract. No private key, seed phrase, API private key or signing credential is stored or required for Phase-6 observation.

## What the real preflight established

The corrected non-crediting preflight on PR #143 passed the actual observation chain:

```text
workflow run                    31316348226
observed_at                     2026-08-09T13:40:30Z
account_equity_usd              53.788314
shadow_status                   SHADOW_COMPUTED_NO_AUTHORITY
shadow_alerts                   []
P3.2 independent parity         PASS
scheduled-decision credit       false
```

The first preflight had exposed only a source-adapter issue: Hyperliquid hourly funding timestamps arrive with small millisecond transport jitter. Raw bytes remain preserved, and a strict <=1 second source-boundary normalization maps the observation to the nominal hourly slot before the unchanged P3.1 canonicalizer. Larger jitter fails closed.

## Automatic future-only observation

After the activation is on the default branch, GitHub Actions runs the collector daily at:

```text
00:00 UTC
```

For a genuine scheduled run to become a credit candidate it must satisfy all of the following:

```text
event = schedule
collector_armed = true
schedule_configured = true
elapsed_evidence_credit_authorized = true
decision timestamp strictly after ARM marker
no duplicate credited decision timestamp
collector/shadow checks pass
evidence artifact upload succeeds
separate receipt artifact upload succeeds
```

PR runs, historical replay, CI replay, workflow rerun and manual dispatch never become scheduled-decision credit.

The ARM marker was created on 2026-08-09, so the rule-derived first eligible canonical timestamp is `2026-08-10T00:00:00Z`. It counts only if PR #143 has already merged to `main` for that genuine schedule and both artifacts persist. Otherwise wait for the next actual scheduled run; do not recreate or backfill the missed timestamp.

## Frozen Phase-6 closeout requirements

```text
minimum elapsed calendar days       14
minimum genuine scheduled decisions 10
minimum emergency drills             1
critical reconciliation errors       0
unexplained target drift              0
schedule failures                     0
```

The elapsed-time condition is not satisfied merely by ARM or by the passage of wall-clock time. The closeout review must have durable evidence satisfying the frozen rules.

One future manual emergency drill is still required. A properly evidenced `workflow_dispatch` with the emergency-drill input may count only toward that drill requirement; it does not become a scheduled decision.

## Evidence persistence rule

Each creditable scheduled decision must produce:

1. a create-only GitHub Actions evidence artifact with 90-day retention containing raw public/read-only inputs, provenance manifest and shadow record; then
2. a separate hash-bound receipt artifact created only after the evidence upload succeeds.

Logs, PR diagnostics, ephemeral runner files, failed evidence uploads, missing receipts or expired evidence before acceptance review create no credit.

## Production/security boundary

Phase-6 ARM is **observation-only**.

It does not authorize:

- private-key or seed input;
- signing;
- order submission;
- withdrawals or transfers;
- production activation;
- leverage expansion;
- strategy retuning;
- Phase-7 live launch.

Production remains:

```text
production gross cap               1.0
production_authorized_components  []
production_authorized              false
signature_authorized               false
order_submission_authorized        false
```

## Other frozen work

- F27 R2 remains authoritative; R1 is superseded-preserved.
- F7 remains `PARTIAL`.
- LEVERAGE-0040 remains `FAIL_STOP / NO_PROMOTION`.
- Idle Cash remains `NOT_FEASIBLE_ON_HYPERLIQUID_STANDARD / FUTURE_OPTION / NOT_AUTHORIZED`.
- Future gross-reducing Research IDs remain subject to the right-tail gate: canonical best-20 log-growth retention >=90% **and** net summed daily-return delta >0.

## Human-control boundaries that remain

No further owner action is required for the **daily zero-authority Phase-6 scheduled collection** once PR #143 is merged.

Separate explicit owner approval remains required for:

- Phase-7 launch;
- `MONITOR_ONLY -> ACTIVE`;
- `FLAT -> LONG`;
- `FLAT -> SHORT`;
- first short exposure of a new confirmed bear phase.

## Exact next step

After PR #143 is green and merged with the marker commit preserved, wait for the first genuine scheduled run. Verify evidence + receipt persistence before calling it scheduled decision #1. Continue future-only collection until the 14-day / 10-decision threshold is met, perform one evidenced emergency drill, then conduct the Phase-6 acceptance review. Do not activate Phase 7 without a later explicit owner approval.
