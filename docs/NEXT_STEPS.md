# Next Steps

> Read canonical sources in repository-defined order. GitHub actual state wins over stale prose.

## Current authorized task

```text
P2.4 Router decision
```

P0.1, P0.2, P1.1-P1.8, P2.1, P2.2 and P2.3 are PASS / MERGED. P2.4 is the only authorized next implementation dependency.

Do not start P3, P4, P5, P6, P7 or P8 early.

## P2.4 acceptance boundary

The target engine requests **economic exposure**. The router returns an **implementation plan and deterministic reason code**.

Roadmap example reason codes:

```text
SPOT_VERIFIED_LOWER_COST
PERP_SPOT_UNVERIFIED
PERP_REQUIRED_FOR_SHORT
PERP_REQUIRED_FOR_LEVERAGE_OVERLAY
NO_TRADE_LIQUIDITY_FAIL
```

Acceptance criteria:

- all routing decisions are logged;
- research/backtest can reproduce router assumptions;
- production can compare expected versus realized cost;
- P2.4 consumes the canonical instrument identity and cost evidence from P2.1-P2.3 rather than inventing new identities or silently changing cost units;
- BNB remains `PERP_ONLY_DEFAULT` under `ROUTER-BNB-PERP-ONLY-2026-08-06` unless that product decision is explicitly reopened and approved.

P2.4 does **not** include P3 target-engine changes, P4 leverage research, P5 cycle-exit research or production authorization.

## P2.3 audited closure baseline

P2.3 closed in two implementation pieces:

1. PR #62 — core spot-vs-perp cost arithmetic;
2. PR #64 — full-project-audit correction that derives live depth/VWAP from Hyperliquid `l2Book`, makes L2 snapshots fetchable, freezes funding/basis units, fails closed on insufficient returned book depth and prevents maker execution from being inferred from taker VWAP.

Final P2.3 correction head:

```text
8501e9ad0a6622689a8331fee28fbda3b315c23b
```

Final evidence:

- Phase 0 baseline contract #78 / `31101519237`: SUCCESS;
- execution tests: SUCCESS;
- research integration: SUCCESS;
- PR handoff governance #98 / `31101516714`: SUCCESS.

P2.3 audited closure main commit:

```text
c2fa4ac79038d3ed800f5a167dd7703a8ef5946a
```

Full audit record:

```text
docs/FULL_PROJECT_AUDIT_2026-08-06.md
```

## Frozen router baseline

```text
BTC: verified spot candidate + perp fallback
ETH: verified UETH spot candidate + perp fallback
SOL: verified USOL spot candidate + perp fallback
BNB: PERP_ONLY_DEFAULT
```

The old Master Plan §6 BNB working-policy sentence is superseded by the later explicit BNB perp-only decision. This does not change the frozen four-asset long universe or Hyperliquid-first venue.

## Ordered forward program

```text
P1.1-P1.8 COMPLETE
P2.1 COMPLETE
P2.2 COMPLETE
P2.3 COMPLETE
P2.4 CURRENT / NEXT
P3   BLOCKED ON P2.4
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

Latest audit/correction PR #64 was:

```text
DRIFT_1
```

This was process/implementation-detail drift only; product/strategy drift was zero. A fresh P2.4 PR should be classified on its own facts and may be `DRIFT_0` if it follows the canonical plan without new deviation.

## Exact next action

After this post-merge normalization PR is green and merged, start **P2.4 Router decision** from then-current main on a fresh candidate branch. Close only the P2.4 router acceptance boundary before beginning P3.
