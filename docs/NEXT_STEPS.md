# BRRK Next Steps

Last updated: 2026-08-10

## Current instruction

**Phase-6 ARM remains active on `main` and independent of 0046 research. The first genuine future-only scheduled decision at `2026-08-10T00:00:00Z` is indexed as scheduled decision #1 from already-persisted evidence plus a separate hash-bound receipt. Continue automatic daily `00:00 UTC` observation without backfill. Separately, the proposed 0046 Transition Pulse mathematics is now frozen in a design-only document; do not run it. The next research step is a new formal preregistration PR that copies the frozen design without alteration.**

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

0046 exact design                        FROZEN DESIGN-ONLY / NOT PREREGISTERED
0046 runner                              NOT CREATED
0046 calibration                         NOT RUN
0046 historical result                   NONE
0046 dynamic-gross eligibility           FALSE
```

The bound public account is recorded in the identity contract. No private key, seed phrase, API private key or signing credential is stored or required for Phase-6 observation.

## Phase-6 accounting is now merged

PR #161 merged at `c1308fa20e85de69cfa0acf3decb56619d74df58` after continuity and no-drift falsification checks.

The first draft was not merged merely because the economic evidence looked valid. CI first rejected missing handoff sections, then rejected an out-of-allowlist human-readable `docs/` ledger. The correction did **not** expand governance permissions: the extra `docs/` file was deleted, the audit narrative stayed under `research/governance/**`, and the machine-readable accounting index remained non-authoritative.

The merged accounting index is:

```text
research/governance/phase6_observation_ledger.json
```

The Actions evidence artifact plus separate receipt remain the evidence authority. A repository ledger edit alone creates no credit.

## First genuine future-only scheduled observation

GitHub Actions run `31346545269`, attempt 1, is a genuine `schedule` event on `main`.

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

The receipt binds run identity, workflow SHA, decision timestamp, evidence-object digest, input-provenance digest, shadow-record digest and evidence artifact. Manual dispatch, replay, reruns and duplicate timestamps remain non-crediting.

## Automatic future-only observation

GitHub Actions continues the collector daily at:

```text
00:00 UTC
```

A genuine scheduled run may become a credit candidate only when:

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

Future missed timestamps must remain missing. Never recreate or backfill them.

## Frozen Phase-6 closeout requirements

```text
minimum elapsed calendar days       14
minimum genuine scheduled decisions 10
minimum emergency drills             1
critical reconciliation errors       0
unexplained target drift              0
schedule failures                     0
```

The elapsed-time condition is not satisfied by ARM, one scheduled observation, or wall-clock passage alone. One future manual emergency drill is still required and may count only toward the drill requirement.

## Production/security boundary

Phase-6 ARM is observation-only. It does not authorize private-key input, signing, order submission, withdrawals/transfers, production activation, leverage expansion, strategy retuning or Phase-7 launch.

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

## 0046 exact design freeze

The design-only contract is:

```text
research/governance/BRRK_EXHAUSTION_PULSE_0046_DESIGN_FREEZE_2026-08-10.md
```

It replaces the remaining ambiguity in Issue #160 without creating a formal research ID.

Primary coordinates are exactly the symmetric frozen 0044 axes:

```text
S1_MOMENTUM_DECELERATION
S2_TREND_DISAGREEMENT
S3_PRICE_STRUCTURE
S4_VOL_DOWNSIDE
```

`CORE4 + S2 + S3 + S4` was rejected because CORE4 already contains all four axes and would duplicate exposed S2/S3/S4 information inside a coordinate-sparse detector. CORE4 is benchmark-only.

No extra Kalman/local-trend smoother is used. The primary candidate is exactly:

```text
S1/S2/S3/S4
 -> 64-session causal pre-change linear baseline
 -> one-sided positive slope GLR per axis
 -> equal mixture over all 15 non-empty axis subsets
 -> multiscale maximum over candidate change ages 3..32
 -> label-blind VAR(1) residual-block-bootstrap calibration
 -> 5,000 null paths / 7-vector blocks / seed 460046
 -> truncated model-implied ARL0 >=365
 -> CALIBRATION_LOCK before any event taxonomy can be loaded
 -> Transition Pulse = threshold upcrossing only
```

There is exactly one 0046 candidate. BOCPD is excluded from this ID and cannot rescue a failure. There is no WATCH/RISK state, entry persistence, cooldown, refractory parameter, recovery threshold or hysteresis machine.

Proposed hard gates are frozen before formal preregistration:

```text
primary TRUE PRE14_7 event pulse hit          >=0.50
primary CONT PRE14_0 false pulse              <=0.34
primary TRUE episode pulse hit                >=0.60
primary CONT episode false pulse              <=0.50
severe TRUE PRE14_7 pulse hit                 >=0.57
qualifying primary TRUE PRE21_0 onsets        >=4
median qualifying onset lead                  7..21 sessions
raw alarm occupancy                           <=0.175
median raw-alarm spell                        <=7 sessions
90th percentile raw-alarm spell               <=14 sessions
label-blind truncated ARL0                    >=365
```

The occupancy gate is explicitly result-informed: it requires approximately a 50% reduction from failed 0045 WATCH+RISK occupancy. No claim of independent evidence is made.

A future 0046 PASS may at most make a separately preregistered **future-only pulse-validation** stage eligible. It does not make dynamic gross eligible.

## Research lifecycle boundary

Until a separate preregistration PR is merged:

```text
BRRK-EXHAUSTION-PULSE-0046 formal registration  NOT CREATED
0046 dataset/exposure registration               NOT CREATED
0046 runner                                      NOT CREATED
0046 calibration                                 NOT RUN
0046 historical outcome result                   NONE
0046 portfolio economics                         FORBIDDEN
dynamic-gross mapping                            NOT ELIGIBLE
canonical BRRK change                            NONE
Phase-6 change                                   NONE
```

The later preregistration must copy the frozen mathematics, label firewall, null calibration, hard gates, seeds and failure semantics without changing them. If a material design change becomes necessary, do not silently edit the preregistration: reopen design work and record the change before any result.

## Human-control boundaries that remain

No further owner action is required for the daily zero-authority Phase-6 scheduled collection.

Separate explicit owner approval remains required for:

- Phase-7 launch;
- `MONITOR_ONLY -> ACTIVE`;
- `FLAT -> LONG`;
- `FLAT -> SHORT`;
- first short exposure of a new confirmed bear phase.

## Exact next steps

1. Validate and merge the current 0046 design-only PR only if continuity, research-governance and no-drift checks remain green.
2. Keep Phase-6 daily schedule unchanged and future-only; verify durable evidence + separate receipt before indexing each unique scheduled timestamp.
3. Never backfill Phase-6 missed timestamps, count reruns twice, or convert manual dispatch into scheduled credit.
4. Perform one separately evidenced manual emergency drill before Phase-6 closeout; count it only as a drill.
5. After the exact 0046 design freeze is merged, create a separate `PROGRAM_GOVERNED_V1` **preregistration-only PR** that copies the frozen design without running calibration or outcomes.
6. Require the preregistration PR to register lineage and the already-exposed DEVELOPMENT dataset, freeze one candidate, and preserve 0044/0045 negative evidence.
7. Do not create the 0046 runner, run historical outcomes, map dynamic gross, evaluate portfolio economics, change canonical BRRK, change Phase 6, or confer any production/security authority during the design-freeze or preregistration stages.
