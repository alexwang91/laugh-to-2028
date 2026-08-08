# BRRK Next Steps

Last updated: 2026-08-08

## Current instruction

**Close the final Phase-6 pre-arm dependency without weakening Governance v1 or fabricating account state. Production remains unauthorized.**

## Immediate state

```text
Phase 0-3                              COMPLETE / MERGED
Phase 4 leverage research              FAIL_STOP / no eligible >1 candidate
production gross cap                   1.0
production_authorized_components = []
P5.1-P5.4                              COMPLETE / FROZEN
P5.5 joint validation                  COMPLETE / IMMUTABLE / NO_PROMOTION / FAIL_STOP
P5.6 integration                       BLOCKED / NO ELIGIBLE CANDIDATE
Phase 6 implementation/replay          PASS_SHADOW_ONLY_IMPLEMENTATION_REPLAY / MERGED #109
Phase 6 live elapsed evidence          MEASUREMENT_INCONCLUSIVE_TIME_DEPENDENT / CLOCK NOT ARMED
Phase 6 observation preactivation      PREACTIVATION_BLOCKED_FAIL_CLOSED
Phase 6 durable evidence backend       FROZEN / ACTIONS_ARTIFACT_V4 / 90D / NO CREDIT / MERGED #133
Phase 6 valuation contract             PHASE6-LIVE-VALUATION-V1 / PR #134 CANDIDATE
Phase 6 pre-arm dependencies           3/4 FROZEN IN #134 CANDIDATE / ACCOUNT IDENTITY REMAINS
Phase 7 mode                           MONITOR_ONLY / LAUNCH BLOCKED
Phase 8 BEAR-SHORT-0001                PREREGISTERED_TRIGGER_ABSENT_NOT_RUN
Stablecoin liquidity Stage-1           FAIL_NO_INCREMENTAL_INFORMATION / TERMINAL STOP
production authorization               NONE
first real short authorization         NONE
```

## Four Phase-6 pre-arm dependencies

1. **Observation account identity — UNRESOLVED.** Freeze one exact public read-only Hyperliquid master/subaccount address. It must be the actual observed account, not an agent-wallet identity. Do not invent it or derive it from a private key.
2. **Current-position/equity valuation — PR #134 CANDIDATE.** `PHASE6-LIVE-VALUATION-V1` supports only explicit Standard mode (`userAbstraction=disabled`) and fails closed on unsupported account modes/assets. It becomes authoritative only after final green CI and merge.
3. **Durable create-only evidence backend — FROZEN / MERGED #133.** GitHub Actions Artifact v4, 90-day retention, overwrite false, evidence bundle + hash-bound receipt before credit.
4. **Schedule/duplicate-credit rule — FROZEN.** Manual dispatch is not a scheduled decision; reruns and duplicate decision timestamps create no new credit.

## PR #134 closeout sequence

```text
1. KEEP PHASE6-LIVE-VALUATION-V1 LIMITED TO STANDARD MODE
2. KEEP BNB SPOT FORBIDDEN / PERP_ONLY_DEFAULT
3. KEEP P3.2 TARGET AND P3.3 CONTROL ECONOMICS UNCHANGED
4. RUN FINAL-HEAD GOVERNANCE / NO-DRIFT / P3.2 PARITY / PHASE-6 SAFETY CI
5. MERGE #134 ONLY WITH EXPECTED-HEAD PROTECTION WHEN ALL REQUIRED CHECKS ARE GREEN
6. VERIFY NEW MAIN AND RECHECK PRODUCT / RESEARCH / PRODUCTION AUTHORITY INVARIANTS
```

## Unique next task after #134

Freeze one exact public read-only Hyperliquid observation account identity and verify:

```text
address exact and explicit
actual master/subaccount being observed
not an agent-wallet identity
userAbstraction == disabled
fits PHASE6-LIVE-VALUATION-V1 supported surfaces
no unsupported nonzero assets/surfaces silently ignored
no private key required or consumed
```

If the account is Unified Account, Portfolio Margin, `default`, DEX abstraction, or otherwise outside V1, the correct state is **BLOCKED / INCOMPATIBLE**. Do not broaden V1 after seeing live state merely to make the account fit.

## Arm boundary after 4/4 dependencies

Account identity freeze does not itself start elapsed credit. A separate prospective arm change is required.

```text
first eligible scheduled decision = FIRST 00:00 UTC STRICTLY AFTER ARM COMMIT
minimum elapsed calendar days     = 14
minimum scheduled decisions       = 10
minimum emergency drills          = 1
critical reconciliation errors    = 0
unexplained target drift           = 0
schedule failures                  = 0
```

Never credit historical backfill, historical/CI replay, reruns, duplicate timestamps or manual dispatch as scheduled decisions.

## Boundaries while Phase 6 is unresolved

Do not start Stablecoin rescue/Stage-2, Holder Cost, new leverage, new allocation, funding/OI alpha, new short research, portfolio optimization or production deployment as substitutes for closing the observation dependency.

Do not modify BRRK-0011, BTC/ETH/SOL/BNB membership, XRP feature-only role, BNB perp-only policy, transaction costs, P3.2/P3.3 economics, immutable research evidence or production authority.

Phase 7 remains `MONITOR_ONLY`; Phase 8 remains trigger-absent/not-run. No first real short is authorized.

## After Phase-6 collection becomes operational

Resume the infrastructure roadmap in order:

```text
1. formal research lifecycle/state-machine enforcement
2. Research Queue + trial/overlap accounting
3. only then consider a new prospectively registered result-bearing research family
```