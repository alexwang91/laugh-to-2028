# Next Steps

> Read canonical sources in repository-defined order. GitHub actual state wins over stale prose.

## Current authorized task

```text
P2.3 Spot vs perp cost model
```

P0.1, P0.2, P1.1-P1.8, P2.1 and P2.2 are PASS / MERGED. P2.3 is the only authorized next implementation dependency.

Do not start P2.4, P3, P4, P5, P6, P7 or P8 early.

## P2.3 acceptance boundary

For BTC / ETH / SOL compare spot and perp economics using the same economic exposure and explicit holding horizons.

Model at minimum:
- spot and perp execution fees;
- spread/slippage assumptions or live observations;
- perp funding drag/benefit;
- liquidity/capacity constraints;
- custody/redemption or bridge friction where economically relevant;
- sensitivity to holding horizon and funding regime.

BNB is excluded from spot-vs-perp comparison because `ROUTER-BNB-PERP-ONLY-2026-08-06` fixes it to `PERP_ONLY_DEFAULT` unless separately reopened and approved.

P2.3 does not include P2.4 route-selection implementation or production authorization.

## P2.2 closure baseline

P2.2 is PASS / MERGED through PR #60.

Final implementation head:

```text
882f404d5bda11839c52ed92167fb96cb3097353
```

Final evidence:
- Phase 0 baseline contract #70 / `31099064883`: SUCCESS;
- execution tests: SUCCESS;
- research integration: SUCCESS;
- PR handoff governance #88 / `31099065127`: SUCCESS.

Squash/main commit:

```text
d8a2554ea520f73e77eee9816108261fdaaf762f
```

`ROUTER-SPOT-IDENTITY-P2.2 = IMPLEMENTATION_VERIFIED`.
`ROUTER-BNB-PERP-ONLY-2026-08-06 = ACCEPTED_RESEARCH_TARGET`.

## Ordered forward program

```text
P1.1-P1.8 COMPLETE
P2.1 COMPLETE
P2.2 COMPLETE
P2.3 CURRENT / NEXT
P2.4 BLOCKED ON P2.3
P3   BLOCKED
P4   BLOCKED
P5   BLOCKED
P6   BLOCKED
P7   BLOCKED
P8   BLOCKED
```

## Production authorization

```text
NO_CHANGE
production_authorized_components = []
```

## Project drift audit

```text
DRIFT_0
```

## Exact next action

After this normalization PR is green and merged, start **P2.3 Spot vs perp cost model** from then-current main on a fresh candidate branch. Do not implement P2.4 before P2.3 closes.
