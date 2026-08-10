# BRRK Next Steps

Last updated: 2026-08-10

## Current instruction

**Phase-6 ARM is active on `main`. The first genuine future-only scheduled decision at `2026-08-10T00:00:00Z` has already produced durable evidence plus a separate hash-bound receipt and is indexed as scheduled decision #1. Continue automatic daily `00:00 UTC` observation without backfill. Verify each future schedule-origin evidence/receipt pair before indexing credit. Phase-6 live acceptance remains `MEASUREMENT_INCONCLUSIVE_TIME_DEPENDENT`; production and Phase-7 authority remain blocked.**

## Immediate live state

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
first genuine scheduled decision        2026-08-10T00:00:00Z / CREDITED EXISTING DURABLE EVIDENCE
genuine scheduled decisions             1 / >=10
emergency drills                        0 / >=1
critical reconciliation errors observed 0
unexplained target drift observed       0
schedule failures observed              0
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

## First genuine future-only scheduled observation

GitHub Actions run `31346545269`, attempt 1, is a genuine `schedule` event on `main`. The collector persisted a create-only evidence artifact and then a separate receipt artifact:

```text
decision timestamp          2026-08-10T00:00:00Z
observed_at                 2026-08-10T01:14:21Z
workflow SHA                405d2f75221ba97734973dd9bee2df04c9ecbcd2

evidence artifact id       9047515515
evidence artifact digest   sha256:35324a527eec2e10c44ad8ccd124c0074a3b23f64be4352651037b4209a811a3
receipt artifact id        9047516114
receipt artifact digest    sha256:f2299a0dca868c3fcedc4cafd561104930f8b8f52e8ba71d88e0f423d4461380

shadow status              SHADOW_COMPUTED_NO_AUTHORITY
shadow alerts              []
target reference parity    PASS / zero gross drift / zero max-weight drift
offline reference L1 drift 0.0
```

The receipt binds the run identity, workflow SHA, decision timestamp, evidence-object digest, input-provenance digest, shadow-record digest and evidence artifact. This is sufficient to index the already-existing durable evidence as scheduled decision #1 under the frozen future-only rules.

The repository-side ledger is intentionally non-authoritative: `research/governance/phase6_observation_ledger.json` and `docs/PHASE6_OBSERVATION_LEDGER.md` only index already-persisted evidence. Recording an entry cannot create credit, recreate a missed decision, convert manual dispatch into schedule credit, or confer production/security authority.

## Automatic future-only observation

GitHub Actions runs the collector daily at:

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

The ARM marker was created on 2026-08-09, so the rule-derived first eligible canonical timestamp was `2026-08-10T00:00:00Z`. That timestamp is now occupied by the verified genuine scheduled observation above. Future missed timestamps must remain missing; never recreate or backfill them.

## Frozen Phase-6 closeout requirements

```text
minimum elapsed calendar days       14
minimum genuine scheduled decisions 10
minimum emergency drills             1
critical reconciliation errors       0
unexplained target drift              0
schedule failures                     0
```

The elapsed-time condition is not satisfied merely by ARM, one scheduled observation, or the passage of wall-clock time. The closeout review must have durable evidence satisfying the frozen rules.

One future manual emergency drill is still required. A properly evidenced `workflow_dispatch` with the emergency-drill input may count only toward that drill requirement; it does not become a scheduled decision.

## Evidence persistence and accounting rule

Each creditable scheduled decision must produce:

1. a create-only GitHub Actions evidence artifact with 90-day retention containing raw public/read-only inputs, provenance manifest and shadow record; then
2. a separate hash-bound receipt artifact created only after the evidence upload succeeds.

Logs, PR diagnostics, ephemeral runner files, failed evidence uploads, missing receipts or expired evidence before acceptance review create no credit.

The repository accounting ledger may be updated only after those durable artifacts exist and are independently checked. The Actions artifacts remain the evidence authority. A ledger edit alone creates no credit.

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
- `BRRK-EXHAUSTION-STATE-0044` remains immutable `PASS_TRIGGER_STAGE_ELIGIBLE`.
- `BRRK-EXHAUSTION-TRIGGER-0045` remains immutable `FAIL_NO_DYNAMIC_GROSS_STAGE_ELIGIBILITY`; no same-ID rescue or dynamic-gross stage is authorized.
- Future gross-reducing Research IDs remain subject to the right-tail gate: canonical best-20 log-growth retention >=90% **and** net summed daily-return delta >0.

## Research continuation after 0045

Issue #160 is design/literature synthesis only for a fresh result-informed transition-pulse architecture. The next research step is to freeze an exact mathematical specification before any result-bearing preregistration or runner exists.

The preferred primary family under review is a causal robust local-linear latent-dynamics layer followed by a one-sided multiscale sparse GLR deterioration detector. BOCPD may serve only as a separately frozen secondary comparator. Historical exhaustion labels must not tune the detection threshold, scale, filter hyperparameters or pulse duration.

Until the exact statistical contract is frozen:

```text
BRRK-EXHAUSTION-PULSE-0046 result-bearing preregistration  NOT CREATED
0046 runner                                                 NOT CREATED
0046 economic result                                        NONE
dynamic-gross mapping                                       NOT ELIGIBLE
canonical BRRK change                                       NONE
Phase-6 change                                              NONE
```

## Human-control boundaries that remain

No further owner action is required for the **daily zero-authority Phase-6 scheduled collection**.

Separate explicit owner approval remains required for:

- Phase-7 launch;
- `MONITOR_ONLY -> ACTIVE`;
- `FLAT -> LONG`;
- `FLAT -> SHORT`;
- first short exposure of a new confirmed bear phase.

## Exact next steps

1. Keep the daily Phase-6 schedule unchanged and future-only.
2. For each genuine future schedule event, verify durable evidence + separate receipt before adding one unique timestamp to the accounting ledger.
3. Never backfill missed timestamps, count reruns twice, or convert manual dispatch into scheduled credit.
4. Perform one separately evidenced manual emergency drill before Phase-6 closeout; count it only as a drill.
5. Do not conduct Phase-6 acceptance review until all frozen elapsed/decision/drill/error requirements are actually satisfied.
6. Independently continue Issue #160 design work by freezing the exact 0046 filter, detector, multiscale aggregation, null calibration, pulse/reset semantics, inference and hard FAIL gates before result-bearing preregistration.
7. Do not create an 0046 runner, run historical outcomes, map dynamic gross, change canonical BRRK, change Phase 6, or confer any production/security authority during the design-freeze step.
