# BRRK Next Steps

Last updated: 2026-08-08

## Current instruction

**Finish PR #134, then freeze the one remaining Phase-6 pre-arm dependency: the exact public read-only Hyperliquid observation account identity. Production remains unauthorized.**

## Immediate state

```text
Phase 6 implementation/replay          PASS_SHADOW_ONLY_IMPLEMENTATION_REPLAY / MERGED #109
Phase 6 live elapsed evidence          MEASUREMENT_INCONCLUSIVE_TIME_DEPENDENT / CLOCK NOT ARMED
Phase 6 durable evidence backend       FROZEN / MERGED #133
Phase 6 valuation contract             PHASE6-LIVE-VALUATION-V1 / PR #134 CANDIDATE
Phase 6 pre-arm dependencies           3/4 FROZEN IN #134 CANDIDATE
remaining dependency                   OBSERVATION ACCOUNT IDENTITY
Phase 7                                MONITOR_ONLY / LAUNCH BLOCKED
Phase 8                                TRIGGER ABSENT / NOT RUN
production gross cap                   1.0
production_authorized_components = []
```

## PR #134 closeout

```text
1. KEEP PHASE6-LIVE-VALUATION-V1 STANDARD-MODE ONLY
2. KEEP BNB PERP_ONLY_DEFAULT
3. KEEP P3.2/P3.3 ECONOMICS UNCHANGED
4. RUN FINAL-HEAD GOVERNANCE / NO-DRIFT / PARITY / PHASE-6 SAFETY CI
5. MERGE ONLY WITH EXPECTED-HEAD PROTECTION IF REQUIRED CHECKS ARE GREEN
6. VERIFY NEW MAIN AND CANONICAL AUTHORITY INVARIANTS
```

## Unique next task after #134

Freeze one exact **public read-only Hyperliquid master/subaccount address** and verify:

```text
address is explicit and exact
address is the actual observed master/subaccount
address is not an agent-wallet identity
userAbstraction == disabled
account fits PHASE6-LIVE-VALUATION-V1
unsupported nonzero assets/surfaces are not silently ignored
no private key is required or consumed
```

If the account is Unified Account, Portfolio Margin, `default`, DEX abstraction, or otherwise outside V1, mark it `BLOCKED / INCOMPATIBLE`; do not broaden V1 post-observation simply to make the account fit.

## Arm boundary after 4/4

Freezing the account does not start elapsed credit. A separate prospective arm change is required.

```text
first eligible decision          FIRST 00:00 UTC STRICTLY AFTER ARM COMMIT
minimum elapsed days             14
minimum scheduled decisions      10
minimum emergency drills         1
critical reconciliation errors   0
unexplained target drift          0
schedule failures                 0
```

Historical backfill, replay, CI replay, reruns, duplicate timestamps and manual dispatch do not count as scheduled-decision credit.

## Do not substitute other work

Until the Phase-6 observation dependency is closed, do not start Stablecoin rescue/Stage-2, Holder Cost, new leverage/allocation/funding alpha, new short research, portfolio optimization or production deployment as a substitute.

Keep BRRK-0011, BTC/ETH/SOL/BNB, XRP feature-only, BNB perp-only, P3.2/P3.3, transaction costs, immutable research results and production authority unchanged.

## After genuine Phase-6 collection is operational

```text
1. formal research lifecycle/state-machine enforcement
2. Research Queue + trial/overlap accounting
3. only then consider a new prospectively registered result-bearing research family
```