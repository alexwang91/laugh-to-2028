# BRRK Current State

Last updated: 2026-08-09  
Handoff PR: **#139**  
Authoritative baseline main at branch creation: `e6c5b7459bae4dc89c73f1669be0eca10c2e2372`  
Latest merged PR at branch creation: **#137**

Status: **authoritative current-state handoff**

## Executive state

```text
Phase 0-3                         COMPLETE / MERGED
Phase 4 leverage research         FAIL_STOP / NO_PROMOTION
P5.5                              COMPLETE / IMMUTABLE / NO_PROMOTION / FAIL_STOP
P5.6                              BLOCKED / NO ELIGIBLE CANDIDATE
Phase 6 implementation/replay     PASS_SHADOW_ONLY_IMPLEMENTATION_REPLAY / MERGED #109
Phase 6 live elapsed evidence     MEASUREMENT_INCONCLUSIVE_TIME_DEPENDENT / CLOCK NOT ARMED
Phase 6 evidence backend          FROZEN / MERGED #133
Phase 6 valuation contract        PHASE6-LIVE-VALUATION-V1 / MERGED #134
Phase 6 identity contract         PHASE6-LIVE-ACCOUNT-IDENTITY-V1 / MERGED #135 / UNBOUND
Phase 6 pre-arm dependencies      3/4 / IDENTITY UNRESOLVED
Right-tail admission gate         PROSPECTIVE_FROZEN_RESEARCH_ADMISSION_GATE / V1
Dual-layer sanity                 COMPLETE / IMMUTABLE / NON-PROMOTABLE / MERGED #136
BRRK signal attribution           COMPLETE / IMMUTABLE / NON-PROMOTABLE / MERGED #137
Phase 7                           MONITOR_ONLY / LAUNCH BLOCKED
Phase 8                           TRIGGER ABSENT / NOT RUN
Stablecoin Stage-1               TERMINAL FAIL / NO_PROMOTION
```

## Current Phase 6 blocker and readiness

`PHASE6-LIVE-ACCOUNT-IDENTITY-V1` is merged but no observation identity is bound.

```text
status                            AWAITING_COMPATIBLE_EXPLICIT_PUBLIC_IDENTITY
account_address                   null
identity_frozen                   false
accepted userRole                 user / subAccount
required userAbstraction          disabled
dependencies satisfied            3/4
collector_armed                   false
schedule_configured               false
elapsed_evidence_credit_authorized false
```

Closed, unmerged PR #138 performed a prospective public read-only probe. The observed account returned `userRole=user` but `userAbstraction=default`, so it was incompatible with V1. No address was bound, no dependency was credited, and no elapsed clock started. The address is intentionally not reproduced here.

A future binding requires an explicit public master/subaccount identity satisfying `userRole=user/subAccount` and `userAbstraction=disabled`. `docs/PHASE6_ADDRESS_BINDING_REQUEST.md` freezes the non-secret request and verification path.

After a valid binding reaches 4/4, work still stops before a **separate prospective ARM change**. The first eligible scheduled decision is the first canonical 00:00 UTC decision strictly after the ARM commit.

Frozen shadow acceptance:

```text
minimum elapsed calendar days      14
minimum genuine scheduled decisions 10
minimum emergency drills            1
critical reconciliation errors      0
unexplained target drift             0
schedule failures                    0
```

Historical backfill/replay, CI replay, workflow reruns, duplicate decision timestamps and manual dispatch create no scheduled-decision credit.

## Prospective right-tail research gate

`docs/RIGHT_TAIL_PRESERVATION_GATE.md` freezes a V1 admission requirement for future **new** Research IDs that can lower canonical BRRK target gross:

```text
candidate retained canonical best-20 log growth >= 90%
net summed daily-return delta > 0
logic: PASS Gate 1 AND PASS Gate 2
failure: FAIL_RIGHT_TAIL_GATE
```

Canonical best-10/best-20/best-50 sets must be defined by the canonical baseline. Best-10 and best-50 retention are reporting-only in V1.

This gate is prospective only. It does not reopen P5.x, LEVERAGE-0040/0041, STABLECOIN-LIQUIDITY-0001, dual-layer sanity, BRRK attribution, or any other immutable evidence.

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
collector_armed                   false
schedule_configured               false
elapsed_evidence_credit_authorized false
first real short authority        NONE
```

A public observation address never authorizes signing, orders, transfers, withdrawals, production activation or live trading.

## Explicit human gates

Still binding:

- explicit compatible identity owner action;
- separate prospective Phase-6 ARM transition;
- Phase-7 launch approval;
- `MONITOR_ONLY -> ACTIVE`;
- `FLAT -> LONG`;
- `FLAT -> SHORT`;
- first short exposure of a new confirmed bear phase.

## Stopped / forbidden work

Do not reopen, rerun, rescue, retune or reinterpret immutable/terminal P5.x, LEVERAGE-0040/0041, STABLECOIN-LIQUIDITY-0001, dual-layer sanity, BRRK attribution, or idle-cash R1 evidence for promotion.

Do not use the right-tail gate to justify post-result threshold search. Do not bind or re-probe the PR #138 address from historical discussion. Do not arm Phase 6 or backfill elapsed credit in this docs-only work.

## Current drift assessment

`DRIFT_0`.

This handoff and the two new governance/readiness documents change no strategy mathematics, economics, execution, config, frozen research result, production component, gross cap, credential authority or live state. The right-tail gate is a prospective future-research admission rule frozen before any new overlay candidate exists.

## Exact next task

For the current authorized docs-only work package, after this PR merges:

1. re-read the new main;
2. start a fresh PR for the F27 R2 documentation restatement, LEVERAGE-0040 metric-convention footnote, F7 status correction and Idle Cash execution-feasibility evaluation;
3. keep all research evidence immutable and all production/security authority unchanged.

Operationally, Phase 6 remains blocked at 3/4 until a future explicit compatible public master/subaccount identity is supplied and bound under the frozen contract.
