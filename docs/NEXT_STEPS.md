# BRRK Next Steps

Last updated: 2026-08-08

## Current instruction

**Close PR #136 without retuning its observed Stablecoin mapping, then return to the unique Phase-6 pre-arm dependency: one exact public Hyperliquid observation account address. Production remains unauthorized.**

## Immediate state

```text
Phase 6 implementation/replay          PASS_SHADOW_ONLY_IMPLEMENTATION_REPLAY / MERGED #109
Phase 6 live elapsed evidence          MEASUREMENT_INCONCLUSIVE_TIME_DEPENDENT / CLOCK NOT ARMED
Phase 6 durable evidence backend       FROZEN / MERGED #133
Phase 6 valuation contract             PHASE6-LIVE-VALUATION-V1 / MERGED #134
Phase 6 account-identity rules         PHASE6-LIVE-ACCOUNT-IDENTITY-V1 / MERGED #135 / UNBOUND
Phase 6 pre-arm dependencies           3/4 FROZEN
remaining dependency                   EXACT PUBLIC OBSERVATION ACCOUNT IDENTITY
dual-layer sanity                      COMPLETE / NON-PROMOTABLE / NO INTEGRATION
Phase 7                                MONITOR_ONLY / LAUNCH BLOCKED
Phase 8                                TRIGGER ABSENT / NOT RUN
production gross cap                   1.0
production_authorized_components = []
```

## PR #136 result — do not retune

The one-variant architecture sanity check used already-exposed Stablecoin history only and therefore has no promotion authority. It preserved canonical BRRK relative weights and allowed the external layer only to reduce gross with pre-frozen caps `SUPPORTIVE=1.00`, `NEUTRAL=0.80`, `RESTRICTIVE=0.60`.

Matched 2022-12-10 through 2026-08-02, 5 bps, canonical P3.3 L1 band 0.05:

```text
baseline CAGR        65.3056777%
fused CAGR           57.2191846%
delta                -8.0864931 pp

baseline MaxDD      -33.5292296%
fused MaxDD         -32.5723083%
improvement           0.9569213 pp

baseline Sharpe       1.3561161
fused Sharpe          1.3556295

baseline Calmar       1.9477238
fused Calmar          1.7566819

baseline turnover    91.0866089
fused turnover       103.1500774
```

Interpretation:

- external fusion **does** mechanically change exposure and rebalance timing;
- this specific frozen Stablecoin state/cap mapping is economically inferior;
- do not tune 1.00/0.80/0.60 after seeing the result;
- do not rescue `STABLECOIN-LIQUIDITY-0001`;
- do not admit an edge or change canonical P3.2/P3.3;
- any future dual-layer validation must be a new prospective research ID with independent/unexposed evidence.

## #136 closeout sequence

```text
1. KEEP research/governance/dual_layer_fusion_sanity_result.json IMMUTABLE IN ECONOMIC CONTENT
2. VERIFY TEMPORARY DIAGNOSTIC WORKFLOW EDIT IS FULLY RESTORED TO MAIN BLOB
3. RUN FINAL GOVERNANCE / NO-DRIFT / HANDOFF CI ON THE FINAL HEAD
4. VERIFY NO P3.1 / P3.2 / P3.3 / ROUTER / EXECUTOR / PHASE-6 RUNTIME FILE CHANGED
5. MERGE ONLY WITH EXPECTED-HEAD PROTECTION IF ALL REQUIRED FINAL-HEAD CHECKS ARE GREEN
```

## Unique operational task after #136

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

After genuine Phase-6 collection becomes operational, resume the governance/infrastructure roadmap and only then open a new formally preregistered dual-layer evidence study if independent external evidence is available.
