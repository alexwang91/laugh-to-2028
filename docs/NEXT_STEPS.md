# Next Steps

> Read canonical sources in repository-defined order. GitHub actual state wins over stale prose.

## Current authorized task

```text
P1.8 Kill and emergency paths
```

P0.1, P0.2 and P1.1 through P1.7 are PASS / MERGED. P1.8 is the only authorized next implementation dependency.

Do not start P2, P3, P4, P5, P6, P7 or P8 early.

## P1.8 acceptance boundary

Implement:

- cancel-all;
- reduce-only close;
- emergency FLAT;
- disable-new-risk switch.

Acceptance criteria:

- testnet / controlled test proves each path;
- emergency path does not depend on the normal target engine being healthy.

P1.8 is execution hardening only. It does not include P2 instrument routing, multi-asset production authorization, leverage expansion, strategy changes or live-capital approval.

## P1.7 closure baseline

P1.7 Restart recovery is PASS / MERGED through PR #54.

Final implementation head:

```text
56cc6d6a4547297dae93e33c390c26570c364bf6
```

Final evidence:

- Phase 0 baseline contract #46 / `31095951858`: SUCCESS;
- execution tests: SUCCESS;
- research integration: SUCCESS;
- PR handoff governance #60 / `31095951582`: SUCCESS.

Squash/main commit:

```text
03ee46bf234175bb54745de79b225711ecbc740b
```

`EXEC-RESTART-RECOVERY-P1.7 = IMPLEMENTATION_VERIFIED`.

P1.7 established safe and idempotent cold-start recovery for open orders, partial fills, unknown-submit results and stale local position state without blind resubmission.

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
P1.7 COMPLETE
P1.8 CURRENT / NEXT
P2   BLOCKED ON P1.8
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

After this normalization PR is green and merged, start **P1.8 Kill and emergency paths** from then-current main on a fresh candidate branch. Close the four emergency-command acceptance paths before beginning P2.
