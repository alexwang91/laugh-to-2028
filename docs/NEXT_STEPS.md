# Next Steps

> Read canonical sources in repository-defined order. GitHub actual state wins over stale prose.

## Current authorized task

```text
P1.7 Restart recovery
```

P0.1, P0.2 and P1.1 through P1.6 are PASS / MERGED. P1.7 is the only authorized next implementation dependency.

Do not start P1.8, P2, P3, P4, P5 or P8 early.

## P1.7 acceptance boundary

Required cold-restart cases:

- open order;
- partial fill;
- network timeout with unknown submit result;
- actual position differing from stale local state.

All cases must resolve safely and idempotently.

P1.7 must consume the durable CLOID/OID/fill truth from P1.2, actual-fill transition logic from P1.3, reversal safety from P1.4, metadata formatting from P1.5 and account-level risk gate from P1.6.

P1.7 does **not** include P1.8 cancel-all/emergency-FLAT commands or P2 instrument routing.

## P1.6 closure baseline

P1.6 Post-submit reconciliation is PASS / MERGED through PR #52.

Final implementation head:

```text
fd8ac395189bd6ce134eaeb5c1ae4bf1ac1a6ae5
```

Final evidence:

- Phase 0 baseline contract #40 / `31093119316`: SUCCESS;
- execution tests: SUCCESS;
- research integration: SUCCESS;
- PR handoff governance #51 / `31093117491`: SUCCESS;
- evidence-only governance #52 / `31093191350`: SUCCESS.

Squash/main commit:

```text
1a8addc6225446d287ab0465f0f9b555242b6739
```

`EXEC-POST-SUBMIT-RECON-P1.6 = IMPLEMENTATION_VERIFIED`.

P1.6 established that unexplained account/exchange/local differences block risk-increasing orders while same-direction reductions remain available when the durable ledger remains usable.

## Frozen product baseline

```text
Long universe: BTC / ETH / SOL / BNB
Primary venue: Hyperliquid
Initial capital: $2,000 cash/stablecoin
Recurring manual contribution: about $100/week
Daily boundary: 00:00 UTC
Intraday automation: risk reduction only
Leverage: model-determined
70% drawdown: catastrophic boundary only
FLAT: zero directional exposure
FLAT -> LONG/SHORT: human approval
First short in new bear phase: human approval
Bot credential: trading Agent/API only
No automated withdrawals/external transfers
Deployment: candidate/shadow + manual blue-green cutover
```

## Ordered forward program

```text
P1.1 COMPLETE
P1.2 COMPLETE
P1.3 COMPLETE
P1.4 COMPLETE
P1.5 COMPLETE
P1.6 COMPLETE
P1.7 CURRENT / NEXT
P1.8 BLOCKED ON P1.7
P2   BLOCKED
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

## Exact next action

After this normalization PR is green and merged, start P1.7 Restart recovery from then-current main on a fresh candidate branch and close its four-case evidence matrix before any P1.8 work.
