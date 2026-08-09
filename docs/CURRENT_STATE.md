# BRRK Current State

Last updated: 2026-08-10  
Handoff PR: **#149**  
Handoff branch: `research/brrk-opportunity-audit-0042`  
Authoritative baseline main at branch creation: `7a8b0385963e96ecce9dc70c313c27507cd99b52`  
Latest merged dashboard PR at branch creation: **#148**

Status: **authoritative current-state handoff candidate**

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
Phase 6 ARM                       MERGED #143 / ACTIVE FUTURE-ONLY OBSERVATION
Phase 6 ARM marker                cbd58adb05187651ca72d67900a0ccbbd3e83b1e
Phase 6 daily schedule            00:00 UTC
Phase 6 live elapsed evidence     MEASUREMENT_INCONCLUSIVE_TIME_DEPENDENT
BRRK opportunity-cost audit       0042 DIAGNOSTIC CANDIDATE / NO PROMOTION AUTHORITY
Program timeline dashboard        READ-ONLY V5 / PROFESSIONAL FUND TERMINAL
Phase 7                           MONITOR_ONLY / LAUNCH BLOCKED
Phase 8                           TRIGGER ABSENT / NOT RUN
Production                        NO_CHANGE
```

## Phase 6 active observation state

The durable prospective ARM marker remains:

```text
cbd58adb05187651ca72d67900a0ccbbd3e83b1e
```

The authoritative live-observation gate remains:

```text
status                             ARMED_FUTURE_ONLY_OBSERVATION_ACTIVE
collector_armed                    true
schedule_configured                true
elapsed_evidence_credit_authorized true
daily schedule                     0 0 * * *  (UTC)
production_authorized              false
signature_authorized               false
order_submission_authorized        false
```

The evidence backend remains `ARMED_COLLECTING_FUTURE_ONLY`. Genuine scheduled credit still requires a real future `schedule` event plus its create-only evidence artifact and separate hash-bound receipt artifact. Historical replay, pull-request preflight, rerun, duplicate decision timestamps and manual dispatch do not create scheduled-decision credit.

First theoretical eligible canonical timestamp remains `2026-08-10T00:00:00Z`. Frozen acceptance remains:

```text
minimum elapsed calendar days       14
minimum genuine scheduled decisions 10
minimum emergency drills             1
critical reconciliation errors       0
unexplained target drift              0
schedule failures                     0
```

A separately evidenced manual emergency drill remains required and never counts as a scheduled decision.

## BRRK Opportunity-Cost Audit 0042 — candidate

This branch adds a deterministic read-only diagnostic audit under `research/governance/` using only already committed canonical historical artifacts:

```text
research/results/pit_disp_0015/daily_weights.csv
research/results/pit_disp_0015/daily_equity.csv
```

The audit is explicitly not a new strategy experiment and has no promotion authority. It freezes the following measurements before CI result review:

- validate whether normalized BRRK target mixes equal normalized V1 target mixes on overlap days;
- BRRK-vs-V1 CAGR and maximum-drawdown difference;
- observable defensive-scale distribution via BRRK gross / V1 gross where mechanically valid;
- BTC reserve share on alt-active days;
- ETH 50% / SOL 35% / BNB 25% structural cap signatures;
- target-vector change frequency and gap days;
- top-20 V1 daily log-growth capture and bottom-20 relative exposure.

The audit explicitly does **not** infer:

```text
historical daily P3.2 signal-speed causality
historical P3.3 5% account-gap execution attribution
winner-cap return counterfactuals
```

because those require missing historical state or a separately preregistered strategy experiment.

The diagnostic may identify which mechanism deserves the next prospective research ID. It may not modify BRRK-0011, Phase 6, Phase 7, signing, order submission, production authorization, or immutable historical results.

## Dashboard V5

PR #148 merged V5 at current baseline main:

```text
7a8b0385963e96ecce9dc70c313c27507cd99b52
```

The public dashboard remains:

```text
https://laugh-to-2028.vercel.app/
```

## Canonical production / security authority

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

This audit changes none of these fields and adds no signer, private key, order submission, withdrawal, transfer, or production capability.

## Other frozen decisions

- F27 R2 remains authoritative; R1 remains superseded-preserved.
- F7 remains `PARTIAL`; immutable studies are not rewritten.
- LEVERAGE-0040 remains `FAIL_STOP / NO_PROMOTION`.
- Idle Cash remains `NOT_FEASIBLE_ON_HYPERLIQUID_STANDARD / FUTURE_OPTION / NOT_AUTHORIZED`.
- Phase-6 future-only observation continues independently of this diagnostic.

## Current drift assessment

`DRIFT_0`.

This candidate adds only a read-only governance diagnostic, its contract test/spec, and this handoff. It does not modify `execution/**`, `config/**`, `research/results/**`, strategy mathematics, Phase-6 scheduling, immutable economic evidence, or execution authority.

## Exact next task

1. Require PR #149 governance/no-drift and all existing strategy/safety CI to stay green.
2. Read the machine-emitted audit JSON from CI only after the frozen measurement code is committed.
3. Based on that diagnostic, preregister exactly one or more separate candidate experiments before evaluating any modified strategy economics.
4. Continue Phase-6 future-only evidence accumulation independently.
