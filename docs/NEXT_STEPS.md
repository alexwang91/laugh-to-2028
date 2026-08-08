# BRRK Next Steps

Last updated: 2026-08-08

## Current instruction

**Freeze the account-identity binding rules without fabricating an address; after that, the unique remaining Phase-6 pre-arm dependency is the real public observation account address. Production remains unauthorized.**

## Immediate state

```text
Phase 6 implementation/replay          PASS_SHADOW_ONLY_IMPLEMENTATION_REPLAY / MERGED #109
Phase 6 live elapsed evidence          MEASUREMENT_INCONCLUSIVE_TIME_DEPENDENT / CLOCK NOT ARMED
Phase 6 durable evidence backend       FROZEN / MERGED #133
Phase 6 valuation contract             PHASE6-LIVE-VALUATION-V1 / MERGED #134
Phase 6 account-identity rules         PHASE6-LIVE-ACCOUNT-IDENTITY-V1 / CANDIDATE / UNBOUND
Phase 6 pre-arm dependencies           3/4 FROZEN
remaining dependency                   EXACT PUBLIC OBSERVATION ACCOUNT IDENTITY
Phase 7                                MONITOR_ONLY / LAUNCH BLOCKED
Phase 8                                TRIGGER ABSENT / NOT RUN
production gross cap                   1.0
production_authorized_components = []
```

## Current candidate — identity binding rules only

The candidate freezes the future binding contract under `research/governance/**` while intentionally keeping:

```text
account_address                     null
identity_frozen                     false
binding_evidence                    null
collector_armed                     false
schedule_configured                 false
elapsed_evidence_credit_authorized  false
```

Frozen rules:

```text
address format           0x + 40 hexadecimal characters
accepted userRole        user / subAccount
rejected userRole        agent / vault / missing
required userAbstraction disabled
subaccount master        evidence required; no silent substitution
private-key discovery    forbidden
production authority     false
```

The preactivation gate must derive its account-identity dependency from the validated identity contract. A hand-edited gate flag cannot turn an unbound contract into a frozen identity.

## Candidate closeout sequence

```text
1. KEEP account_address=null AND identity_frozen=false
2. RUN FINAL GOVERNANCE / NO-DRIFT / P3.2 PARITY / PHASE-6 SAFETY CI
3. MERGE ONLY WITH EXPECTED-HEAD PROTECTION IF ALL REQUIRED CHECKS ARE GREEN
4. VERIFY NEW MAIN AND CANONICAL AUTHORITY INVARIANTS
```

## Unique next task after this candidate

Obtain one exact **public read-only Hyperliquid master/subaccount address** and bind it prospectively.

Required verification:

```text
address is explicit and exact
address is the actual observed master/subaccount
userRole is user OR subAccount
userRole is NOT agent / vault / missing
userAbstraction == disabled
account fits PHASE6-LIVE-VALUATION-V1
unsupported nonzero assets/surfaces are not silently ignored
non-secret address provenance is persisted
raw userRole + userAbstraction response SHA256 digests are persisted
no private key is required, supplied or derived
```

For a subaccount, preserve the returned master address as evidence but continue observing the exact subaccount address; do not silently replace it with the master.

If the real address is an agent wallet, vault, missing account, Unified Account, Portfolio Margin, `default`, DEX abstraction or otherwise outside V1, the correct outcome is **BLOCKED / INCOMPATIBLE**. Do not broaden the contract after observing the account merely to make it fit.

## Arm boundary after 4/4

A valid account binding completes the dependency set but still does not start elapsed credit. A separate prospective arm change is required.

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