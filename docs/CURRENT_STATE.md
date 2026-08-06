# BRRK Current State

Last updated: 2026-08-06
Status: authoritative cross-chat handoff snapshot

## Authoritative baseline

- P0.1 / P0.2: PASS / MERGED
- P1.1 through P1.8: PASS / MERGED
- Phase 1 Account and execution truth: COMPLETE
- P2.1 Canonical instrument registry: PASS / MERGED through PR #58
- P2.2 ETH/SOL spot validation + BNB perp-only policy: PASS / MERGED through PR #60
- P2.3 core cost arithmetic: PASS / MERGED through PR #62
- P2.3 live-L2 measurement correction: PASS / MERGED through PR #64
- P2.3 audited closure main commit: `c2fa4ac79038d3ed800f5a167dd7703a8ef5946a`
- Full project audit: `docs/FULL_PROJECT_AUDIT_2026-08-06.md`

## Current roadmap position

```text
P2.1 Canonical instrument registry: PASS / MERGED
P2.2 ETH / SOL spot validation + BNB perp-only policy: PASS / MERGED
P2.3 Spot vs perp cost model: PASS / MERGED
P2.4 Router decision: NEXT
P3+: BLOCKED
```

The unique next implementation task is **P2.4 Router decision**.

## Full-project audit result

The audit re-read the Master Plan, Roadmap, Governance, continuity protocol, canonical configs/registries, merged implementation chain and current code modules before allowing P2.4 to proceed.

Result:

```text
PRODUCT / STRATEGY DRIFT: NONE
PRODUCTION AUTHORIZATION DRIFT: NONE
LATEST AUDIT / CORRECTION PR: DRIFT_1
```

`DRIFT_1` refers only to process/implementation-detail history and the P2.3 acceptance correction:

1. historical merged/research branches remain despite the Governance branch-hygiene preference;
2. one earlier BNB policy documentation commit was written directly to main before returning to the required branch/PR flow;
3. PR #63 was closed without merge when the audit found that #62 had not yet derived live L2 depth/VWAP canonically.

PR #64 closed the P2.3 measurement gap before P2.4 was authorized. No universe, venue, risk, security, human-approval, stopped-research or production boundary changed. A new P2.4 PR should be classified on its own facts; absent a new deviation it may return to `DRIFT_0`.

## P2.3 audited closure

P2.3 now provides, for BTC / ETH / SOL:

- configurable maker/taker fee inputs;
- same-asset, equal-notional, equal-horizon comparison;
- canonical Hyperliquid `l2Book` fetch support;
- target-notional buy/sell VWAP from returned book levels;
- full spread and beyond-half-spread taker slippage derivation;
- displayed bid/ask USD depth and conservative two-sided depth;
- fail-closed capacity handling when target quantity exceeds returned book depth;
- explicit funding decimal -> bps/hour conversion and horizon accumulation;
- explicit perp-vs-verified-spot basis conversion;
- spot custody/redemption friction input;
- VWAP diagnostic separation from charged slippage to prevent double counting;
- taker-only L2-derived observations; maker queue/fill economics require separate explicit assumptions.

P2.3 remains a cost/measurement layer only; it does not authorize a route.

Final correction head:

```text
8501e9ad0a6622689a8331fee28fbda3b315c23b
```

passed:

- `Phase 0 baseline contract` #78 / Actions `31101519237`: SUCCESS;
- execution tests: SUCCESS;
- research integration contract: SUCCESS;
- `PR handoff governance` #98 / Actions `31101516714`: SUCCESS.

PR #64 squash-merged to main as:

```text
c2fa4ac79038d3ed800f5a167dd7703a8ef5946a
```

## Router product boundary

```text
BTC: verified spot candidate + perp fallback
ETH: verified UETH spot candidate + perp fallback
SOL: verified USOL spot candidate + perp fallback
BNB: PERP_ONLY_DEFAULT
```

`ROUTER-BNB-PERP-ONLY-2026-08-06` is authoritative. The older Master Plan §6 BNB working-policy sentence is superseded by this later explicit routing decision; the frozen BTC/ETH/SOL/BNB long universe and Hyperliquid-first venue remain unchanged.

## Current unique next task: P2.4 Router decision

The target engine requests **economic exposure**. The router must return an **implementation plan + deterministic reason code**.

Roadmap examples include:

```text
SPOT_VERIFIED_LOWER_COST
PERP_SPOT_UNVERIFIED
PERP_REQUIRED_FOR_SHORT
PERP_REQUIRED_FOR_LEVERAGE_OVERLAY
NO_TRADE_LIQUIDITY_FAIL
```

Acceptance criteria:

- every routing decision is logged;
- research/backtest can reproduce the router assumptions;
- production can compare expected versus realized implementation cost;
- BNB remains `PERP_ONLY_DEFAULT` unless its product decision is explicitly reopened;
- P2.4 must consume P2.1-P2.3 evidence rather than inventing new identity/cost assumptions.

## Production authorization

```text
NO_CHANGE
production_authorized_components = []
```

No live capital, leverage expansion, production route, short, withdrawal/external transfer or cutover is authorized by P2.3 closure.

## Exact next action

```text
P2.4 Router decision
```

Start from current main after this post-merge normalization is merged, on a fresh candidate branch. Do not begin P3 before P2.4 closes.
