# Next Steps

> Read canonical sources in repository-defined order. GitHub actual state wins over stale prose.

## Current authorized task

```text
P2.1 Canonical instrument registry
```

P0.1, P0.2 and P1.1 through P1.8 are PASS / MERGED. Phase 1 Account and execution truth is complete. P2.1 is the only authorized next implementation dependency.

Do not start P2.2, P2.3, P2.4, P3, P4, P5, P6, P7 or P8 early.

## P2.1 acceptance boundary

For BTC, ETH, SOL and BNB record:

- spot token identity;
- perp identity;
- decimals / tick size;
- custody/redemption facts where relevant;
- liquidity metrics;
- availability state.

BTC spot identity already has prior evidence and should be imported rather than rediscovered.

P2.1 does **not** include UETH/USOL/BNB validation experiments, route cost modeling, route decisions, strategy changes or production authorization.

## P1.8 closure baseline

P1.8 Kill and emergency paths is PASS / MERGED through PR #56.

Final implementation head:

```text
3d1715dafda8edc5d8a37d1de7a2a2de56b0e587
```

Final evidence:

- Phase 0 baseline contract #50 / `31096925400`: SUCCESS;
- execution tests: SUCCESS;
- research integration: SUCCESS;
- PR handoff governance #64 / `31096925378`: SUCCESS.

Squash/main commit:

```text
765fc53dfcb3699ffc1de530717349cf926b42ed
```

`EXEC-KILL-EMERGENCY-P1.8 = IMPLEMENTATION_VERIFIED`.

P1.8 established direct target-engine-independent cancel-all, reduce-only close, verified emergency FLAT and durable disable-new-risk controls, while preserving risk-reduction availability.

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
P1.1-P1.8 COMPLETE
P2.1 CURRENT / NEXT
P2.2 BLOCKED ON P2.1
P2.3 BLOCKED
P2.4 BLOCKED
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

After this normalization PR is green and merged, start **P2.1 Canonical instrument registry** from then-current main on a fresh candidate branch. Close only the registry acceptance boundary before beginning P2.2.
