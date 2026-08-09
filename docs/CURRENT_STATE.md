# BRRK Current State

Last updated: 2026-08-09  
Handoff PR: **V2 candidate**  
Handoff branch: `dashboard/program-timeline-v2`  
Authoritative baseline main at branch creation: `eab80f7e3599eada22c695e3f013f18ae774a2c5`  
Latest merged dashboard PR at branch creation: **#144**

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
Program timeline dashboard        READ-ONLY V2 CANDIDATE
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

## Program Timeline Dashboard V2 — candidate

V1 was merged in PR #144. The V2 candidate remains under:

```text
research/governance/dashboard/
```

The dashboard is intentionally downstream of authoritative evidence and does not recompute, mutate or replace immutable historical result artifacts.

Historical source-of-record inputs displayed by V2 include:

```text
research/results/pit_disp_0015/daily_equity.csv
research/results/pit_disp_0015/daily_weights.csv
research/results/funding_pnl_0003/full_window_daily_equity.csv
research/governance/brrk_signal_attribution_result.json
config/research_registry.json
config/decision_registry.json
```

The repository historical equity/holdings window used by the canonical chart begins `2022-12-10` and currently extends through `2026-07-31`, i.e. close to four years rather than an invented exact four-year window.

V2 preserves V1 and adds:

- a historical day scrubber, exact date input and chart-click date selection;
- selected-day NAV, daily PnL, cumulative PnL and running drawdown;
- selected-day BTC/ETH/SOL/BNB target holdings and target gross;
- adjacent-day target-weight deltas and L1 delta;
- deterministic target action labels `ENTER / EXIT / INCREASE / DECREASE / HOLD` with display tolerance `REBALANCE_EPS=1e-9`;
- explicit source/column provenance for the selected day;
- frozen BRRK aggregate attribution context including hit rate, payoff and right-tail concentration;
- the existing Phase-6 public schedule/evidence/receipt ledger and future gates.

### Daily explainability boundary

V2 deliberately labels the daily mechanical explanation:

```text
目标权重变化（由 canonical weights 派生）
```

This is authoritative only as a description of adjacent values already present in canonical `daily_weights.csv`. V2 does **not** assert that an adjacent target change proves P3.3 actual turnover or proves a unique day-level `signal -> trade` cause.

The frozen BRRK attribution audit establishes aggregate portfolio mechanics — including modest hit rate, positive payoff asymmetry and strong right-tail dependence — but does not expose a unique per-day causal signal ledger. Therefore the dashboard does not invent one.

Frozen V2 display semantics:

```text
dashboard_record_authoritative=false
scheduled_decision_credit_created=false
production_authorized=false
target_change_mechanics_authoritative_from_canonical_weights=true
execution_causality_asserted=false
```

The dashboard continues to freeze this separation:

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

V2 also refuses to fabricate artifact-internal forward details that the public GitHub artifact metadata does not expose. Target weights, account equity, shadow return, cumulative shadow PnL, alerts and provenance digests remain unavailable in the browser until a separately governed derived read-only index exists.

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

Dashboard V2 changes none of these fields and introduces no signer, private key, order submission, withdrawal, transfer or production-state capability.

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

The V2 candidate changes only dashboard HTML/documentation/tests and this handoff update. It does not modify historical result blobs, `execution/**`, production `config/**`, strategy mathematics, Phase-6 workflow scheduling, immutable economic evidence or execution authority.

## Exact next task

1. Open the V2 dashboard PR with the required handoff sections, `DRIFT_0`, and `NO_CHANGE` production authorization.
2. Run full PR governance/no-drift and dashboard contract CI.
3. Merge only if the final head is green and the diff remains limited to dashboard/docs/tests.
4. Continue allowing the daily Phase-6 schedule to accumulate genuine future evidence independently of the dashboard.
5. After the first successful scheduled evidence+receipt pair exists, verify that the dashboard ledger reflects it without creating or modifying the underlying credit.
6. If artifact-internal forward daily details are later required in-browser, design a separate read-only derived index bound to canonical evidence/receipt identities; do not weaken or replace the canonical create-only evidence contract.
