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
- Current implementation PR: #66
- Current candidate branch: `p2-4/router-decision`

## Current roadmap position

```text
P2.1 Canonical instrument registry: PASS / MERGED
P2.2 ETH / SOL spot validation + BNB perp-only policy: PASS / MERGED
P2.3 Spot vs perp cost model: PASS / MERGED
P2.4 Router decision: IMPLEMENTATION VERIFIED ON CANDIDATE / FINAL-HEAD CI REQUIRED / NOT MERGED
P3+: BLOCKED
```

P2.4 is the unique current task. Do not start P3 before the P2.4 final-head evidence and merge loop closes.

## P2.4 implementation boundary

The router consumes an **economic exposure request** and returns an **implementation plan + deterministic reason code**. It does not decide BRRK weights, leverage level, cycle state or whether a bear program should exist.

Economic request fields are explicit and replayable:

- UTC decision timestamp;
- canonical BRRK asset;
- long/short direction;
- exposure role (`base` or `leverage_overlay`);
- economic notional;
- expected holding horizon;
- target revision.

The implementation consumes P2.1-P2.3 evidence rather than inventing identity or cost assumptions.

## Routing policy

```text
BTC base long: verified spot candidate vs perp by P2.3 expected cost/capacity
ETH base long: verified UETH spot candidate vs perp by P2.3 expected cost/capacity
SOL base long: verified USOL spot candidate vs perp by P2.3 expected cost/capacity
BNB base long: PERP_ONLY_DEFAULT
short role: perp required by instrument type; this does not authorize a bear strategy
leverage_overlay role: perp required by instrument type; this does not select or authorize leverage
```

Spot runtime identity is resolved from Hyperliquid `spotMeta` using verified token identity plus dynamic token/pair indexes. API spot instrument identity is `@<spot_pair_index>`; UI display names are not treated as HyperCore asset IDs.

## Reason-code contract

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

## Reproducibility / logging

- `RouterDecision.decision_id` is a deterministic hash of the request, policy, selected plan, recorded route candidates, runtime spot identity and fee schedule.
- `route_and_log()` appends canonical JSONL with fsync-backed persistence.
- `replay_logged_decision()` reconstructs the decision from recorded assumptions, verifies the deterministic decision ID, and now also requires the **entire canonical logged record** to match the replayed result; modified reason/plan/estimate/extra fields fail closed.
- `compare_expected_realized_cost()` provides the P2.4 boundary for later production attribution of expected versus realized implementation cost.
- Zero economic exposure short-circuits before market/cost observation validation and returns `NO_TRADE_ZERO_EXPOSURE`.
- The policy explicitly remains `IMPLEMENTATION_PLAN_ONLY_NO_PRODUCTION_AUTHORIZATION`.

`ROUTER-DECISION-P2.4 = IMPLEMENTATION_VERIFIED` is registered after successful candidate CI. This is engineering evidence only, not production authorization.

## Candidate CI evidence

Candidate head after self-review corrections:

```text
7110da7dbd425d4b49f51d01f3197ac6aa8e0c08
```

passed:

- `Phase 0 baseline contract` #82 / Actions `31105888002`: SUCCESS;
- execution tests: SUCCESS;
- research integration contract: SUCCESS;
- `PR handoff governance` #103 / Actions `31105888025`: SUCCESS.

The decision-registry and evidence writeback after this successful run changes the branch head, so **one final authoritative CI run is still required on the new exact head before merge**.

## Controlled test coverage

Tests cover:

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
13. zero economic exposure -> NO_TRADE without requiring market observations;
14. runtime spot identity mismatch -> fail closed;
15. same-asset / same-notional / same-horizon observation contract;
16. deterministic decision ID and JSONL replay;
17. policy/decision-ID tamper detection;
18. derived reason/plan/estimate/extra-field tamper detection through strict full-record replay;
19. expected-versus-realized cost attribution;
20. `spotMeta` market-layer request/shape validation.

## Self-review corrections

1. A partial file read initially made the runtime identity validation call appear absent. Full-function review confirmed `_validate_runtime_identity()` was already invoked before base-long spot selection, so no unnecessary code change was made.
2. Replay integrity was strengthened: decision-ID equality alone was insufficient to detect modifications to derived logged fields. Replay now requires full canonical-record equality.
3. Zero exposure is now handled before route-candidate construction so a zero target never requires or validates unnecessary market observations.
4. BNB spot inputs are explicitly rejected under the canonical perp-only decision.
5. Short and leverage-overlay reason codes only select instrument type; they do not authorize the future P8 short program or P4 leverage level.
6. Missing/insufficient cost or capacity evidence produces an explicit fallback or NO_TRADE result.
7. P2.4 does not submit orders and does not modify the P1 execution path.

## Historical audit context

The latest full-project audit recorded `DRIFT_1` for historical process/implementation-detail issues only: branch-hygiene debt, one prior direct-main documentation incident, and the P2.3 live-L2 acceptance correction. PR #64 closed the P2.3 implementation gap before P2.4 began.

For the current P2.4 implementation itself, no new product, sequencing, research, risk, security or production deviation has been identified.

## Project drift audit — current P2.4

```text
DRIFT_0
```

The earlier audit `DRIFT_1` remains preserved as history; it is not reclassified away.

## Production authorization

```text
NO_CHANGE
production_authorized_components = []
```

No live capital, route, leverage, short, withdrawal/external transfer, strategy release or cutover is authorized by P2.4 implementation verification.

## Exact next action

```text
final-head CI on PR #66
-> expected-head merge if and only if all checks pass
-> documentation-only post-merge normalization to P3.1 Data contract
```

Do not begin P3.1 until PR #66 is merged and the canonical handoff is normalized.
