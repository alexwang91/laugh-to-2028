# BRRK Current State

Last updated: 2026-08-09  
Handoff PR: **#144**  
Handoff branch: `dashboard/program-timeline-v1`  
Authoritative baseline main at branch creation: `139287a269cf32281c7753ef63b1df7429d7a289`  
Latest merged PR at branch creation: **#143**

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
Phase 6 ARM                       MERGED #143 / ACTIVE FUTURE-ONLY OBSERVATION
Phase 6 ARM marker                cbd58adb05187651ca72d67900a0ccbbd3e83b1e
Phase 6 daily schedule            00:00 UTC
Phase 6 live elapsed evidence     MEASUREMENT_INCONCLUSIVE_TIME_DEPENDENT
Program timeline dashboard        READ-ONLY V1 / PR #144
Phase 7                           MONITOR_ONLY / LAUNCH BLOCKED
Phase 8                           TRIGGER ABSENT / NOT RUN
Production                        NO_CHANGE
```

## Phase 6 active observation state

PR #143 was merged to `main` with normal merge commit:

```text
139287a269cf32281c7753ef63b1df7429d7a289
```

The durable prospective ARM marker remains a real ancestor of `main`:

```text
cbd58adb05187651ca72d67900a0ccbbd3e83b1e
```

The authoritative live-observation gate is:

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

The evidence backend is `ARMED_COLLECTING_FUTURE_ONLY`. A scheduled decision can become a credit candidate only after both its create-only evidence artifact and separate hash-bound receipt artifact persist successfully. Historical replay, CI replay, pull-request preflight, workflow rerun, duplicate decision timestamps and manual dispatch do not create scheduled-decision credit.

The first theoretical eligible canonical timestamp is `2026-08-10T00:00:00Z`. It becomes decision #1 only if a genuine `schedule` event succeeds with the required durable evidence pair. No missed timestamp may be backfilled.

Frozen Phase-6 acceptance remains:

```text
minimum elapsed calendar days       14
minimum genuine scheduled decisions 10
minimum emergency drills             1
critical reconciliation errors       0
unexplained target drift              0
schedule failures                     0
```

A separately evidenced manual emergency drill is still required before Phase-6 closeout.

## Program Timeline Dashboard V1 — PR #144

While Phase-6 future evidence accumulates, PR #144 adds a read-only observability dashboard under:

```text
research/governance/dashboard/
```

The dashboard is intentionally downstream of authoritative evidence and does not recompute, mutate or replace historical results.

Historical source-of-record inputs displayed by V1 include:

```text
research/results/pit_disp_0015/daily_equity.csv
research/results/pit_disp_0015/daily_weights.csv
research/results/funding_pnl_0003/full_window_daily_equity.csv
config/research_registry.json
config/decision_registry.json
```

The repository historical equity/holdings window used by the canonical chart begins `2022-12-10` and currently extends through `2026-07-31`, i.e. close to four years rather than an invented exact four-year window.

V1 provides:

- a dropdown containing all governed Research Registry records;
- a separate dropdown for records/scenarios that actually have daily equity artifacts and are therefore chartable;
- cumulative NAV / PnL;
- daily PnL percentage;
- drawdown;
- stacked historical BTC/ETH/SOL/BNB canonical target weights;
- research result/promotion/production-state metadata;
- a large past-to-future program timeline;
- a Phase-6 future schedule/evidence/receipt ledger based on public GitHub Actions metadata;
- visible Phase-7 and Phase-8 future gates.

The dashboard freezes this semantic separation:

```text
historical backtest NAV
!= Phase-6 hypothetical shadow PnL
!= future real-account PnL
```

It must never visually splice those three into one continuous economic return series.

For Phase 6, the UI may label a row only as a **scheduled credit candidate** when public workflow metadata shows:

```text
schedule event conclusion = success
AND phase6-evidence-* artifact exists
AND phase6-receipt-* artifact exists
```

That UI classification does not itself create evidence credit and is deliberately weaker than formal Phase-6 acceptance review.

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

Dashboard PR #144 changes none of these fields and introduces no signer, private key, order submission, withdrawal, transfer or production-state capability.

## Other frozen decisions

- F27 R2 remains authoritative; R1 remains superseded-preserved.
- F7 remains `PARTIAL`; immutable studies are not rewritten.
- LEVERAGE-0040 remains `FAIL_STOP / NO_PROMOTION`.
- Idle Cash remains `NOT_FEASIBLE_ON_HYPERLIQUID_STANDARD / FUTURE_OPTION / NOT_AUTHORIZED`.
- Future new Research IDs capable of lowering canonical BRRK gross remain subject to the frozen right-tail gate: best-20 log-growth retention >=90% **and** net summed daily-return delta >0.

## Human-control boundaries that remain

ARM authorization is complete only for zero-authority Phase-6 observation. Later explicit human gates remain:

- Phase-7 launch approval;
- `MONITOR_ONLY -> ACTIVE`;
- `FLAT -> LONG`;
- `FLAT -> SHORT`;
- first short exposure of a new confirmed bear phase.

## Current drift assessment

`DRIFT_0`.

PR #144 is an observability-only governance-layer change. It adds dashboard HTML/documentation/tests and this handoff update. It does not modify historical result blobs, `execution/**`, production `config/**`, strategy mathematics, Phase-6 workflow scheduling, immutable economic evidence or execution authority.

## Exact next task

1. Make PR #144 fully green under governance/no-drift and handoff CI.
2. Merge the read-only dashboard without changing Phase-6 or production authority.
3. Continue allowing the daily Phase-6 schedule to accumulate genuine future evidence independently of the dashboard.
4. After the first successful scheduled evidence+receipt pair exists, verify that the dashboard ledger reflects it without creating or modifying the underlying credit.
5. If detailed forward daily target weights, hypothetical shadow return, account equity and alerts are desired in the UI, design a separate read-only derived summary index; do not weaken or replace the canonical create-only evidence/receipt contract.
