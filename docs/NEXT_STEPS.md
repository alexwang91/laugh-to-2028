# BRRK Next Steps

Last updated: 2026-08-08

## Current instruction

**PR #136 is merged and the BRRK attribution audit is descriptive only. Do not retune Stablecoin or BRRK from the audit. Return to the unique Phase-6 pre-arm dependency: one exact public Hyperliquid observation account address. Production remains unauthorized.**

## Immediate state

```text
Phase 6 implementation/replay          PASS_SHADOW_ONLY_IMPLEMENTATION_REPLAY / MERGED #109
Phase 6 live elapsed evidence          MEASUREMENT_INCONCLUSIVE_TIME_DEPENDENT / CLOCK NOT ARMED
Phase 6 durable evidence backend       FROZEN / MERGED #133
Phase 6 valuation contract             PHASE6-LIVE-VALUATION-V1 / MERGED #134
Phase 6 account-identity rules         PHASE6-LIVE-ACCOUNT-IDENTITY-V1 / MERGED #135 / UNBOUND
Phase 6 pre-arm dependencies           3/4 FROZEN
remaining dependency                   EXACT PUBLIC OBSERVATION ACCOUNT IDENTITY
dual-layer sanity                      COMPLETE / NON-PROMOTABLE / MERGED #136
BRRK signal attribution                COMPLETE / NON-PROMOTABLE DIAGNOSTIC / PR #137
Phase 7                                MONITOR_ONLY / LAUNCH BLOCKED
Phase 8                                TRIGGER ABSENT / NOT RUN
production gross cap                   1.0
production_authorized_components = []
```

## BRRK attribution finding — do not optimize from this audit

Matched canonical path: 2022-12-10 through 2026-08-02, 5 bps, P3.3 L1 band 0.05.

```text
canonical CAGR                       65.3056777%
active-session win rate              51.0752688%
holding-cycle win rate               54.4061303%
daily payoff ratio                    1.1988079
holding-cycle payoff ratio            1.3391727
best 10 sessions / log growth        51.5460%
best 20 sessions / log growth        91.6115%
CAGR if best 20 sessions zeroed       4.3064%
```

The canonical BRRK is therefore **not a high-hit-rate strategy**. Its economics depend on modest positive payoff asymmetry plus preservation of a small number of large right-tail sessions.

The already-frozen Stablecoin gross-cap diagnostic did provide real downside protection, but it removed more upside than it saved:

```text
fused-minus-baseline delta on BRRK-negative sessions   +1.1305444
fused-minus-baseline delta on BRRK-positive sessions   -1.3929561
net summed daily return delta                          -0.2624117
```

`RESTRICTIVE` was not a negative-expectancy BRRK regime: its baseline win rate was only 45.9144%, but mean BRRK return remained positive at about +0.14169% per session and compounded return over those sessions was +39.3675%. Canonical BRRK was already at or below the frozen 0.60 gross cap on about 44.49% of those decision rows, showing material redundancy with BRRK's existing defensiveness.

### Research implication

Do **not** use standalone external-signal hit rate as the admission criterion. Any future External Layer study must be newly prospectively registered and must test, before any portfolio mapping:

```text
1. incremental information conditional on canonical BRRK state/target
2. payoff-weighted left-tail protection, not just directional accuracy
3. explicit preservation of BRRK right-tail participation
4. overlap/redundancy with existing BRRK defensive scale
5. no post-result threshold/cap search
```

The audit does not authorize Stablecoin rescue, cap tuning, edge admission, BRRK modification, or production integration.

## Unique operational task

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

Do not start Stablecoin rescue, post-result cap tuning, leverage/allocation rescue, new short research or production deployment as a substitute for the Phase-6 account-identity blocker.

Keep BRRK-0011, BTC/ETH/SOL/BNB, XRP feature-only, BNB perp-only, P3.2/P3.3, immutable research results and production authority unchanged.

After genuine Phase-6 collection becomes operational, resume the governance/infrastructure roadmap. A future dual-layer study, if opened, must use a new prospective research ID and independent/unexposed evidence and must explicitly protect BRRK's right-tail economics.
