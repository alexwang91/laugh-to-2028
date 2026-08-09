# BRRK Current State

Last updated: 2026-08-09  
Handoff branch: `governance/phase6-bind-public-identity`  
Authoritative baseline main at branch creation: `f1cfced6ceb9d07cab78825297e46cdf8c60231b`  
Latest merged PR at branch creation: **#140**

Status: **authoritative current-state handoff**

## Executive state

```text
Phase 0-3                         COMPLETE / MERGED
Phase 4 leverage research         FAIL_STOP / NO_PROMOTION
LEVERAGE-0040 metric convention   DOCUMENTED / IMMUTABLE RESULT UNCHANGED
P5.5                              COMPLETE / IMMUTABLE / NO_PROMOTION / FAIL_STOP
P5.6                              BLOCKED / NO ELIGIBLE CANDIDATE
F27 idle-cash measurement         R2 AUTHORITATIVE / R1 SUPERSEDED-PRESERVED
F7 metrics convergence            PARTIAL / SHARED CALENDAR-SPAN HELPER EXISTS / LEGACY LOCAL CONVENTIONS REMAIN
Idle Cash execution feasibility   NOT_FEASIBLE_ON_HYPERLIQUID_STANDARD / FUTURE_OPTION_ONLY
Phase 6 implementation/replay     PASS_SHADOW_ONLY_IMPLEMENTATION_REPLAY / MERGED #109
Phase 6 live elapsed evidence     MEASUREMENT_INCONCLUSIVE_TIME_DEPENDENT / CLOCK NOT ARMED
Phase 6 evidence backend          FROZEN / MERGED #133
Phase 6 valuation contract        PHASE6-LIVE-VALUATION-V1 / MERGED #134
Phase 6 identity contract         PHASE6-LIVE-ACCOUNT-IDENTITY-V1 / VERIFIED + FROZEN
Phase 6 pre-arm dependencies      4/4 / READY / AWAITING SEPARATE ARM
Right-tail admission gate         PROSPECTIVE_FROZEN_RESEARCH_ADMISSION_GATE / V1
Dual-layer sanity                 COMPLETE / IMMUTABLE / NON-PROMOTABLE / MERGED #136
BRRK signal attribution           COMPLETE / IMMUTABLE / NON-PROMOTABLE / MERGED #137
Phase 7                           MONITOR_ONLY / LAUNCH BLOCKED
Phase 8                           TRIGGER ABSENT / NOT RUN
Stablecoin Stage-1               TERMINAL FAIL / NO_PROMOTION
```

## F27 corrected measurement authority

`research/results/idle_cash_credit_0027r2.json` is the authoritative F27 measurement.

R2 preserves day-one realized PnL from the known `$10,000` base; R1 had dropped the first realized equity observation during return construction. R1 remains preserved as superseded historical evidence and must not be edited.

Corrected R2 headline values:

```text
V1 mean idle cash                20.5183%
V1 CAGR raw -> credited          61.3127% -> 62.6632%   (+1.3505 pp)
BRRK mean idle cash              24.5700%
BRRK CAGR raw -> credited        65.1661% -> 66.8068%   (+1.6407 pp)
BRRK rf=0 Sharpe raw -> credited 1.3532 -> 1.3756
BRRK excess Sharpe raw -> credit 1.3667 -> 1.4039
```

F27 is economic counterfactual evidence only. `docs/IDLE_CASH_EXECUTION_FEASIBILITY.md` concludes that this credit is **not currently realizable inside the frozen Hyperliquid Standard V1 contract without changing account/margin/callability semantics**.

## F7 metrics-convergence status

F7 is **PARTIAL**, not fully closed.

`research/common/metrics.py` establishes the shared calendar-span convention for current/restated work, but immutable historical studies retain their frozen study-local metrics. In particular, LEVERAGE-0040 uses observation-count annualization. Those immutable results are not rewritten merely to force numerical identity.

No exact repository-wide count of remaining local implementations is asserted here because a complete caller census was not independently established in this docs-only pass.

## LEVERAGE-0040 convention note

`docs/LEVERAGE_0040_P4_5_DECISION_2026-08-07.md` documents that its 65.31% cap-1.00 CAGR uses the study-local observation-count year (`len(returns)/365.25`). It is not the same metric quantity as F27 R2's calendar-span BRRK raw CAGR `65.1661%`.

All LEVERAGE-0040 candidates used the same frozen convention, so this clarification changes no P4.5 result, selection or authority.

## Idle Cash execution feasibility

Primary conclusion:

```text
NOT_FEASIBLE_ON_HYPERLIQUID_STANDARD
FUTURE_OPTION
NOT_AUTHORIZED
REQUIRES_SEPARATE DESIGN + CONTRACT + APPROVAL
```

Current official Hyperliquid mechanics distinguish Standard from Portfolio Margin. The documented automatic yield on unused eligible borrowable assets belongs to Portfolio Margin, which changes account abstraction, unified collateral/borrowing and liquidation semantics. HLP adds strategy exposure plus a 4-day lock-up; HYPE staking adds asset exposure plus a 7-day staking-to-spot queue; off-venue lending/bridge mechanisms add transfer, venue and callability risk.

For V1, immediate margin availability, margin buffer, liquidation distance and frozen Standard valuation semantics take precedence over the historical ~1.64 pp F27 credit.

Simple materiality arithmetic from the BRRK R2 delta:

```text
$2,000 static capital                         ~= $32.81/year
$2,000 initial + $100/week, avg capital $4,600 ~= $75.47/year
```

These are arithmetic illustrations only, not executable quotes or strategy returns.

## Phase 6 identity binding and pre-arm readiness

`PHASE6-LIVE-ACCOUNT-IDENTITY-V1` now freezes the explicit owner-supplied public Hyperliquid master identity after read-only compatibility checks.

Authoritative identity evidence is stored in `research/governance/phase6_live_account_identity_contract.json`:

```text
status                             FROZEN_VERIFIED_READ_ONLY_IDENTITY
account role                       user
required/observed userAbstraction  disabled
identity_frozen                    true
dependencies satisfied             4/4
collector_armed                    false
schedule_configured                false
elapsed_evidence_credit_authorized false
armed_commit                       null
```

The binding evidence persists non-secret provenance, the parsed `userRole` / `userAbstraction` responses and SHA256 digests of the exact raw response strings. No private key, seed phrase, API secret or signing credential is stored.

The preactivation gate is now:

```text
PREACTIVATION_READY_AWAITING_SEPARATE_ARM
```

This is a readiness state only. **4/4 does not start the clock.** A separate prospective ARM change is still required before the collector may be armed, a schedule configured, or elapsed-evidence credit authorized.

After a future explicit ARM change, the first eligible scheduled decision remains the first canonical 00:00 UTC decision strictly after the ARM commit timestamp.

Frozen shadow acceptance:

```text
minimum elapsed calendar days       14
minimum genuine scheduled decisions 10
minimum emergency drills             1
critical reconciliation errors       0
unexplained target drift              0
schedule failures                     0
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

A bound public observation address never authorizes signing, orders, transfers, withdrawals, production activation or live trading.

## Explicit human gates

Still binding:

- separate prospective Phase-6 ARM transition;
- Phase-7 launch approval;
- `MONITOR_ONLY -> ACTIVE`;
- `FLAT -> LONG`;
- `FLAT -> SHORT`;
- first short exposure of a new confirmed bear phase.

The identity-owner action has been completed by this binding; it is no longer the Phase-6 blocker.

## Stopped / forbidden work

Do not reopen, rerun, rescue, retune or reinterpret immutable/terminal P5.x, LEVERAGE-0040/0041, STABLECOIN-LIQUIDITY-0001, dual-layer sanity, BRRK attribution, or idle-cash R1 evidence for promotion.

Do not implement Idle Cash yield in Standard V1 by silently switching account abstraction, moving collateral off venue, depositing into HLP, staking HYPE or counting non-immediately-callable supplied capital as available margin.

Do not arm Phase 6, configure its schedule, backfill elapsed credit or infer Phase-7 launch authority from identity binding.

## Current drift assessment

`DRIFT_0`.

This identity-binding change updates only the Phase-6 governance identity/gate state, its regression tests and handoff documentation. It changes no strategy mathematics, immutable economic result, execution path, config, workflow, production component, gross cap, signer/order authority or elapsed-credit state.

## Exact next task

After this identity-binding PR is green and merged, **STOP**.

The next operational action is a **separate prospective Phase-6 ARM change** and requires explicit owner authorization. Until that separate action occurs, the collector remains unarmed, the schedule remains unconfigured and the 14-day / 10-decision elapsed-evidence clock remains unstarted.
