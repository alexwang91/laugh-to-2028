# Next Steps

> Read canonical sources in repository-defined order. GitHub actual state wins over stale prose.

## Current authorized task

```text
P1.6 Post-submit reconciliation
```

P0.1, P0.2 and P1.1 through P1.5 are PASS / MERGED. P1.6 is the only authorized next implementation dependency.

Do not start P1.7, P1.8, P2, P3, P4, P5 or P8 early.

## P1.6 acceptance boundary

After every trading cycle:

- fetch open orders;
- fetch fills;
- fetch positions;
- fetch account equity/margin;
- compare with local ledger and target.

Acceptance criteria:

- unexplained differences block further risk-increasing orders;
- reduce-risk actions remain available.

P1.6 is reconciliation/hardening only. It does not include the complete P1.7 restart-recovery matrix or P1.8 emergency command paths.

## P1.5 closure baseline

P1.5 Precision / metadata is PASS / MERGED through PR #50.

Final implementation head:

```text
f62eb4edcf22aa47dccd521f119ddff688cbe289
```

Final evidence:

- Phase 0 baseline contract #36 / `31079063482`: SUCCESS;
- execution tests: SUCCESS;
- research integration: SUCCESS;
- PR handoff governance #46 / `31079063679`: SUCCESS;
- evidence-only governance #47 / `31079123985`: SUCCESS.

Squash/main commit:

```text
f23aa681e04ba0fdb37ff413270380e60036e9af
```

`EXEC-PRECISION-METADATA-P1.5 = IMPLEMENTATION_VERIFIED`.

P1.5 established metadata-driven `szDecimals` quantity formatting and BTC/ETH/SOL/BNB formatting tests without authorizing multi-asset production execution.

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
P1.6 CURRENT / NEXT
P1.7 BLOCKED ON P1.6
P1.8 BLOCKED
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

Start P1.6 from current main on a fresh candidate branch after this normalization PR merges. Follow the full implementation/test/self-review/PR/final-head-CI/merge loop.