# Next Steps

> Read canonical sources in repository-defined order. GitHub actual state wins over stale prose.

## Current authorized task

```text
P2.4 Router decision
```

P0.1, P0.2, P1.1-P1.8 and P2.1-P2.3 are PASS / MERGED. P2.4 is the only authorized next implementation dependency.

Do not start P3, P4, P5, P6, P7 or P8 early.

## P2.4 acceptance boundary

The target engine requests economic exposure. Router returns an implementation plan and reason code.

Use:
- canonical instrument registry from P2.1/P2.2;
- P2.3 cost-model assumptions and live inputs;
- BNB `PERP_ONLY_DEFAULT` policy;
- perp for short exposure;
- perp for leverage-overlay exposure;
- no-trade fail-closed behavior when identity/liquidity evidence is insufficient.

Roadmap reason-code examples:

```text
SPOT_VERIFIED_LOWER_COST
PERP_SPOT_UNVERIFIED
PERP_REQUIRED_FOR_SHORT
PERP_REQUIRED_FOR_LEVERAGE_OVERLAY
NO_TRADE_LIQUIDITY_FAIL
```

Acceptance criteria:
- all routing decisions logged;
- research backtest can reproduce router assumptions.

P2.4 does not authorize production trading or change the BRRK target engine economics.

## P2.3 closure baseline

P2.3 Spot vs perp cost model is PASS / MERGED through PR #62.

Final implementation head:

```text
3a6dc02a560aa47be9a95e58942fe7814ae6c511
```

Final evidence:
- Phase 0 baseline contract #74 / `31100005137`: SUCCESS;
- execution tests: SUCCESS;
- research integration: SUCCESS;
- PR handoff governance #92 / `31100003917`: SUCCESS.

Squash/main commit:

```text
e890aebc1764ab872b9446ab755fde793c48a77d
```

`ROUTER-COST-MODEL-P2.3 = IMPLEMENTATION_VERIFIED`.

P2.3 established reproducible equal-exposure spot/perp cost comparison for BTC/ETH/SOL with configurable fees, spread/slippage, funding, basis, depth/VWAP diagnostics, custody friction and holding horizon. BNB remains excluded by its canonical perp-only policy.

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

```text
DRIFT_0
```

## Exact next action

After this normalization PR is green and merged, start **P2.4 Router decision** from then-current main on a fresh candidate branch. Do not begin P3 before P2.4 closes.
