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
- P2.3 post-audit handoff: PASS / MERGED through PR #65
- Current main baseline for P2.4: `adea5af174aa3212128c95024f0047b54463af52`
- Full project audit: `docs/FULL_PROJECT_AUDIT_2026-08-06.md`
- Current candidate branch: `p2-4/router-decision`

## Current roadmap position

```text
P2.1 Canonical instrument registry: PASS / MERGED
P2.2 ETH / SOL spot validation + BNB perp-only policy: PASS / MERGED
P2.3 Spot vs perp cost model: PASS / MERGED
P2.4 Router decision: CANDIDATE IMPLEMENTED / CI PENDING / NOT MERGED
P3+: BLOCKED
```

P2.4 is the unique current task. Do not start P3 before the P2.4 evidence and merge loop closes.

## P2.4 candidate boundary

The router consumes an **economic exposure request** and returns an **implementation plan + deterministic reason code**. It does not decide BRRK weights, leverage level, cycle state or whether a bear program should exist.

Economic request fields are explicit and replayable:

- UTC decision timestamp;
- canonical BRRK asset;
- long/short direction;
- exposure role (`base` or `leverage_overlay`);
- economic notional;
- expected holding horizon;
- target revision.

The candidate consumes P2.1-P2.3 evidence rather than inventing identity or cost assumptions.

## Candidate routing policy

```text
BTC base long: verified spot candidate vs perp by P2.3 expected cost/capacity
ETH base long: verified UETH spot candidate vs perp by P2.3 expected cost/capacity
SOL base long: verified USOL spot candidate vs perp by P2.3 expected cost/capacity
BNB base long: PERP_ONLY_DEFAULT
short role: perp required by instrument type; this does not authorize a bear strategy
leverage_overlay role: perp required by instrument type; this does not select or authorize leverage
```

Spot runtime identity is resolved from Hyperliquid `spotMeta` using verified token identity plus dynamic token/pair indexes. API spot instrument identity is `@<spot_pair_index>`; UI display names are not treated as HyperCore asset IDs.

## Candidate reason-code contract

Registered reason codes include:

```text
SPOT_VERIFIED_LOWER_COST
SPOT_VERIFIED_COST_TIE
SPOT_ONLY_VIABLE_ROUTE
PERP_LOWER_COST
PERP_SPOT_UNVERIFIED
PERP_SPOT_COST_UNAVAILABLE
PERP_SPOT_LIQUIDITY_FAIL
PERP_PRODUCT_POLICY
PERP_REQUIRED_FOR_SHORT
PERP_REQUIRED_FOR_LEVERAGE_OVERLAY
NO_TRADE_LIQUIDITY_FAIL
NO_TRADE_COST_UNAVAILABLE
NO_TRADE_ZERO_EXPOSURE
```

The router fails closed when required route evidence is unavailable or capacity is insufficient rather than guessing an instrument.

## Reproducibility / logging candidate

- `RouterDecision.decision_id` is a deterministic hash of the request, policy, selected plan, recorded route candidates, runtime spot identity and fee schedule.
- `route_and_log()` appends canonical JSONL with fsync-backed persistence.
- `replay_logged_decision()` reconstructs the decision from the recorded assumptions and rejects a decision-id mismatch.
- `compare_expected_realized_cost()` provides the P2.4 boundary for later production attribution of expected versus realized implementation cost.
- The policy explicitly remains `IMPLEMENTATION_PLAN_ONLY_NO_PRODUCTION_AUTHORIZATION`.

## Candidate tests added

Controlled tests cover:

1. canonical BTC/ETH/SOL spot-candidate + BNB perp-only scope;
2. runtime `spotMeta` pair-index resolution and UI/HyperCore identity separation;
3. spot lower-cost selection;
4. perp lower-cost selection;
5. verified cost-tie policy;
6. BNB perp-only enforcement and rejection of spot inputs;
7. short forced-perp routing without bear-strategy authorization;
8. leverage-overlay forced-perp routing without leverage selection;
9. spot liquidity failure -> viable perp fallback;
10. both routes liquidity fail -> NO_TRADE;
11. missing spot cost / runtime identity reason codes;
12. no cost evidence -> fail-closed NO_TRADE;
13. zero economic exposure -> NO_TRADE;
14. runtime spot identity mismatch -> fail closed;
15. same-asset / same-notional / same-horizon observation contract;
16. deterministic decision ID and JSONL replay;
17. tamper detection during replay;
18. expected-versus-realized cost attribution;
19. `spotMeta` market-layer request/shape validation.

Authoritative GitHub Actions evidence is still pending. No implementation status may be upgraded until candidate CI passes.

## Self-review status

- Full P2.3 audit correction remains consumed unchanged.
- Runtime spot identity validation is called before a base-long spot route can be selected.
- BNB spot cannot be silently reopened by providing spot inputs.
- Short and leverage-overlay reason codes only select instrument type; they do not authorize the future P8 short program or P4 leverage level.
- Missing/insufficient cost or capacity evidence produces an explicit fallback or NO_TRADE result.
- P2.4 does not submit orders and does not modify the P1 execution path.

## Historical audit context

The latest full-project audit recorded `DRIFT_1` for historical process/implementation-detail issues only: branch-hygiene debt, one prior direct-main documentation incident, and the P2.3 live-L2 acceptance correction. PR #64 closed the P2.3 implementation gap before P2.4 began.

For the current P2.4 candidate itself, no new product, sequencing, research, risk, security or production deviation has been identified.

## Project drift audit — current P2.4 candidate

```text
DRIFT_0
```

The earlier audit `DRIFT_1` remains preserved as history; it is not reclassified away.

## Production authorization

```text
NO_CHANGE
production_authorized_components = []
```

No live capital, route, leverage, short, withdrawal/external transfer, strategy release or cutover is authorized by this candidate.

## Exact next action

```text
open P2.4 implementation PR
-> authoritative candidate CI
-> fix findings on the same PR
-> register P2.4 implementation evidence only after candidate CI passes
-> update CURRENT_STATE / PR evidence
-> final-head CI
-> expected-head merge
-> documentation-only post-merge normalization to P3.1
```
