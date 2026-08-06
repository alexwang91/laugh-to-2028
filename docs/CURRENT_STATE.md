# BRRK Current State

Last updated: 2026-08-06
Status: authoritative cross-chat handoff snapshot

## Authoritative baseline

- P0.1 / P0.2: PASS / MERGED
- P1.1 through P1.8: PASS / MERGED
- Phase 1 Account and execution truth: COMPLETE
- P2.1 Canonical instrument registry: PASS / MERGED through PR #58
- P2.2 ETH/SOL spot validation + BNB perp-only policy: PASS / MERGED through PR #60
- P2.3 core cost-model PR #62: MERGED to main `e890aebc1764ab872b9446ab755fde793c48a77d`
- Full project audit: `docs/FULL_PROJECT_AUDIT_2026-08-06.md`
- Current correction branch: `p2-3/live-l2-measurement-correction`

## Current roadmap position

```text
P2.1 Canonical instrument registry: PASS / MERGED
P2.2 ETH / SOL spot validation + BNB perp-only policy: PASS / MERGED
P2.3 Spot vs perp cost model: CORRECTION REQUIRED / CURRENT
P2.4 Router decision: BLOCKED
P3+: BLOCKED
```

PR #63, which would have advanced the handoff to P2.4, was closed without merge after the audit found the P2.3 live-L2 measurement gap.

## Full-project audit result

The audit re-read the Master Plan, Roadmap, Governance, continuity protocol, canonical configs/registries, merged implementation PR chain and current code modules.

Result:

```text
PRODUCT / STRATEGY DRIFT: NONE
PRODUCTION AUTHORIZATION DRIFT: NONE
PROCESS / HANDOFF DRIFT: DRIFT_1
```

Completed P0, P1.1-P1.8, P2.1 and P2.2 remain valid and are not being redone. Their implementation PRs are merged and their decision-registry evidence remains present.

`DRIFT_1` records process/implementation-detail issues only:

1. many historical merged/research branches remain despite the Governance branch-hygiene preference;
2. one earlier BNB policy documentation commit was written directly to main before returning to the required branch/PR flow;
3. #63 was stopped before merge because the P2.3 predecessor was found incomplete.

No universe, venue, risk, security, human-approval, stopped-research or production boundary changed.

## P2.3 audit finding and correction

Merged PR #62 correctly implemented the cost arithmetic for BTC / ETH / SOL:

- configurable spot/perp fees;
- same-asset / equal-notional / equal-horizon comparison;
- spread + beyond-spread slippage accounting;
- signed funding by holding horizon;
- basis/premium evolution;
- custody/redemption friction input;
- capacity/VWAP diagnostic fields;
- no P2.4 route decision.

But #62 accepted live depth / VWAP as caller-supplied values. The Roadmap requires **live depth / VWAP**, so P2.3 is reopened only for this narrow measurement-completeness correction.

The correction now adds:

- Hyperliquid `l2Book` fetch support in the market layer;
- target-notional buy/sell VWAP from returned bid/ask levels;
- full spread and beyond-half-spread slippage derivation;
- displayed bid/ask USD depth and conservative two-sided depth;
- fail-closed behavior when the target cannot be filled from Hyperliquid's returned book levels instead of extrapolating unseen liquidity;
- explicit Hyperliquid funding decimal -> bps/hour conversion;
- explicit perp-vs-verified-spot basis conversion;
- tests that prevent VWAP/slippage double counting.

## Router product boundary

```text
BTC: spot candidate + perp fallback
ETH: verified UETH spot candidate + perp fallback
SOL: verified USOL spot candidate + perp fallback
BNB: PERP_ONLY_DEFAULT
```

`ROUTER-BNB-PERP-ONLY-2026-08-06` is authoritative. The older Master Plan §6 BNB working-policy sentence that says to choose spot/perp by availability/cost is superseded by this later explicit routing decision; it is not a change to the frozen BTC/ETH/SOL/BNB long universe or Hyperliquid-first venue.

## Production authorization

```text
NO_CHANGE
production_authorized_components = []
```

## Project drift audit

```text
DRIFT_1
```

Reason: process/handoff and P2.3 measurement-completeness correction only. Product/research objective drift is zero.

## Exact next action

```text
finish P2.3 live-L2 correction
-> authoritative candidate CI
-> self-review / same-PR fixes if needed
-> final-head CI
-> expected-head merge
-> post-merge normalization to P2.4
```

Do not begin P2.4 until this correction is merged and P2.3 is explicitly closed again.
