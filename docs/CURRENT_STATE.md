# BRRK Current State

Last updated: 2026-08-09  
Handoff PR: **#143**  
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
Phase 6 real live preflight       PASS / RUN 31316348226 / NON-CREDITING
Phase 6 ARM marker                cbd58adb05187651ca72d67900a0ccbbd3e83b1e
Phase 6 activation package        ARMED_FUTURE_ONLY_OBSERVATION_ACTIVE / PR #143
Phase 6 live elapsed evidence     MEASUREMENT_INCONCLUSIVE_TIME_DEPENDENT / NO CREDIT YET
Phase 7                           MONITOR_ONLY / LAUNCH BLOCKED
Phase 8                           TRIGGER ABSENT / NOT RUN
Production                        NO_CHANGE
```

## Bound identity and ARM authority

`PHASE6-LIVE-ACCOUNT-IDENTITY-V1` remains frozen to the explicit owner-supplied Hyperliquid master account:

```text
userRole        user
userAbstraction disabled
identity_frozen true
pre-arm deps    4/4
```

The owner explicitly authorized Phase-6 ARM and future-only zero-authority shadow evidence collection. That authorization does **not** authorize production, signing, order submission, withdrawal, transfer, strategy retuning, or Phase-7 launch.

## Real external preflight

PR #143 ran the actual public/read-only observation chain before activation.

The first preflight exposed a Hyperliquid funding timestamp transport detail: returned hourly funding rows were tens of milliseconds after nominal hour boundaries. Raw bytes were preserved. The fix was confined to a fail-closed Hyperliquid source-boundary adapter with a maximum one-second jitter tolerance; the frozen P3.1 canonicalizer was not relaxed or modified.

The corrected real preflight then passed in workflow run `31316348226`:

```text
observed_at                      2026-08-09T13:40:30Z
account_equity_usd               53.788314
shadow_status                    SHADOW_COMPUTED_NO_AUTHORITY
shadow_alerts                    []
P3.2 independent parity          PASS
scheduled decision credit        false
production_authorized            false
signature_authorized             false
order_submission_authorized      false
input_provenance_digest          bb1e3cfb1946e43b3da917a8513f9cce8b2ae1bdab9735e5d2eac49e66472939
shadow_record_digest             59a689e42662f3fc871f6c0d67859a83ee136b959acd0299b3cd7ab46ae7cd03
```

The PR preflight is diagnostic only and creates no elapsed-time, scheduled-decision or emergency-drill credit.

## Prospective ARM marker and activation

The durable prospective marker is the dedicated commit:

```text
cbd58adb05187651ca72d67900a0ccbbd3e83b1e
```

The final activation package in PR #143 sets:

```text
status                             ARMED_FUTURE_ONLY_OBSERVATION_ACTIVE
collector_armed                    true
schedule_configured                true
elapsed_evidence_credit_authorized true
armed_commit                       cbd58adb05187651ca72d67900a0ccbbd3e83b1e
daily schedule                     0 0 * * *  (UTC)
production_authorized              false
signature_authorized               false
order_submission_authorized        false
```

The evidence backend is `ARMED_COLLECTING_FUTURE_ONLY` and references the same ARM marker. Credit still requires successful persistence of both the create-only 90-day evidence artifact and the separate hash-bound receipt artifact.

**Important:** scheduled workflows run from the default branch. Therefore PR #143 itself does not start a credited decision. The activation becomes operational only after merge to `main` while preserving the ARM-marker commit in history.

The marker was created on 2026-08-09, so the rule-derived first eligible canonical timestamp is `2026-08-10T00:00:00Z`. It becomes decision #1 only if the activation is already on `main` for that genuine schedule event and both required artifacts persist successfully. Otherwise the first actual post-merge scheduled event becomes the first credit candidate. No missed timestamp may be backfilled.

## Zero-authority observation chain

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

Historical backfill/replay, CI replay, pull-request preflight, workflow rerun, duplicate decision timestamps and manual dispatch create no scheduled-decision credit. A manual emergency drill may count only toward the drill requirement after ARM and never becomes a scheduled decision.

## Evidence backend

`PHASE6-LIVE-EVIDENCE-BACKEND-V1` remains the authority:

- GitHub Actions artifact v4;
- 90-day retention for creditable evidence;
- overwrite disabled;
- raw market/account/route bytes preserved;
- input-provenance and shadow-record SHA256 required;
- evidence artifact uploads before receipt creation;
- separate receipt artifact uploads before credit;
- failed uploads, logs, ephemeral files and PR diagnostics create no credit.

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

ARM authorization is complete for zero-authority Phase-6 observation. Later explicit human gates remain:

- Phase-7 launch approval;
- `MONITOR_ONLY -> ACTIVE`;
- `FLAT -> LONG`;
- `FLAT -> SHORT`;
- first short exposure of a new confirmed bear phase.

## Current drift assessment

`DRIFT_0`.

The ARM work changes only Phase-6 observation governance, source-boundary read normalization, evidence state and workflow scheduling. Strategy mathematics, frozen P3.1 canonical semantics, immutable economic results, production config, gross cap and execution submission capability remain unchanged.

## Exact next task

1. Make the final PR #143 head fully green, including its real non-crediting live preflight.
2. Merge PR #143 with a **normal merge, not squash/rebase**, so ARM marker commit `cbd58adb05187651ca72d67900a0ccbbd3e83b1e` remains a real ancestor of `main`.
3. Wait for the first genuine post-merge `00:00 UTC` schedule run.
4. Credit decision #1 only after both evidence and receipt artifacts succeed; never backfill a missed schedule.
5. Complete one separately evidenced manual emergency drill before Phase-6 closeout. Phase-7 remains blocked until the full 14-day / 10-decision / 1-drill review passes and the owner later gives separate launch approval.
