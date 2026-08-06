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
- P2.4 Router decision: PASS / MERGED through PR #66
- Phase 2 Hyperliquid instrument router: COMPLETE
- Current main after P2.4: `19b586c3ef08d02203d09c48b469063857d0a6b3`
- Full project audit: `docs/FULL_PROJECT_AUDIT_2026-08-06.md`

## Current roadmap position

```text
P2.1 Canonical instrument registry: PASS / MERGED
P2.2 ETH / SOL spot validation + BNB perp-only policy: PASS / MERGED
P2.3 Spot vs perp cost model: PASS / MERGED
P2.4 Router decision: PASS / MERGED
Phase 2: COMPLETE
P3.1 Data contract: NEXT
P3.2+: BLOCKED
P4+: BLOCKED
```

The unique next implementation task is **P3.1 Data contract**.

## P2.4 closure

P2.4 establishes a deterministic boundary from **economic exposure** to **implementation instrument plan + reason code**. It does not choose BRRK weights, leverage level, cycle state or whether a bear program exists.

Canonical routing behavior:

```text
BTC base long: verified spot candidate vs perp by P2.3 expected cost/capacity
ETH base long: verified UETH spot candidate vs perp by P2.3 expected cost/capacity
SOL base long: verified USOL spot candidate vs perp by P2.3 expected cost/capacity
BNB base long: PERP_ONLY_DEFAULT
short role: perp required by instrument type only; no bear-program authorization
leverage_overlay role: perp required by instrument type only; no leverage-level authorization
```

Spot runtime identity is resolved from Hyperliquid `spotMeta`; API identity uses dynamic `@<spot_pair_index>`. UI labels are not treated as HyperCore asset IDs.

Registered routing reasons include verified spot/perp cost outcomes, identity/cost/liquidity fallbacks, product-policy perp, forced-perp instrument roles, and fail-closed NO_TRADE states.

All router decisions can be persisted as canonical JSONL, replayed from recorded assumptions, and compared later against realized implementation cost. Replay verifies both the deterministic decision ID and full canonical-record equality so modified reason/plan/estimate/extra fields fail closed. Zero economic exposure short-circuits before market-observation validation.

`ROUTER-DECISION-P2.4 = IMPLEMENTATION_VERIFIED` is registered. This is engineering evidence only, not production authorization.

## P2.4 evidence

Candidate head after self-review corrections:

```text
7110da7dbd425d4b49f51d01f3197ac6aa8e0c08
```

passed:

- `Phase 0 baseline contract` #82 / Actions `31105888002`: SUCCESS;
- execution tests: SUCCESS;
- research integration contract: SUCCESS;
- `PR handoff governance` #103 / Actions `31105888025`: SUCCESS.

Final implementation head:

```text
122124bf9d16f38fcb699f1d87d2750833d515d5
```

passed:

- `Phase 0 baseline contract` #84 / Actions `31106165098`: SUCCESS;
- execution tests: SUCCESS;
- research integration contract: SUCCESS;
- `PR handoff governance` #105 / Actions `31106164750`: SUCCESS.

PR #66 squash-merged to main as:

```text
19b586c3ef08d02203d09c48b469063857d0a6b3
```

## P2.4 self-review corrections retained

1. Full-function review confirmed runtime spot identity validation occurs before base-long spot selection.
2. Replay integrity was strengthened from decision-ID-only verification to full canonical-record equality.
3. Zero exposure was moved ahead of route-candidate construction so a zero target requires no unnecessary market evidence.
4. BNB spot inputs are explicitly rejected rather than silently reopening the perp-only product policy.
5. Short and leverage-overlay routing only select instrument type; they do not authorize P8 short logic or P4 leverage.
6. Missing/insufficient identity, cost or capacity evidence produces explicit fallback or NO_TRADE rather than a guessed route.

## Full-project audit / drift history

The full audit recorded historical `DRIFT_1` for process/implementation-detail history only:

1. historical merged/research branches remain despite branch-hygiene preference;
2. one earlier BNB policy documentation commit was written directly to main before returning to branch/PR flow;
3. PR #63 was closed without merge when the P2.3 live-L2 acceptance gap was discovered.

PR #64 closed the P2.3 implementation gap before P2.4 began.

P2.4 itself closed as:

```text
DRIFT_0
```

No long-universe, venue, risk, human-approval, security, stopped-research or production boundary changed.

## Router product boundary

```text
BTC: verified spot candidate + perp fallback
ETH: verified UETH spot candidate + perp fallback
SOL: verified USOL spot candidate + perp fallback
BNB: PERP_ONLY_DEFAULT
```

`ROUTER-BNB-PERP-ONLY-2026-08-06` is authoritative. The Master Plan instrument-policy prose is being synchronized in the P2.4 post-merge handoff so fresh conversations do not encounter stale BNB routing text before reading the decision registry.

## Production authorization

```text
NO_CHANGE
production_authorized_components = []
```

No live capital, production route, leverage, short, withdrawal/external transfer, strategy release or cutover is authorized.

## Unique next task: P3.1 Data contract

Phase 3 goal: make the frozen BRRK directional core reproducible in live operation before adding leverage or cycle-exit intelligence.

P3.1 must define canonical sources and transformations for:

- daily close;
- missing data;
- corporate/token mapping changes where relevant;
- funding/basis inputs used by the router.

Acceptance criteria:

- the UTC `00:00` daily boundary is identical in research and live;
- the same canonical historical input produces the same downstream target inputs/results.

P3.1 is a **data-contract** task only. Do not implement P3.2 target calculation API, P3.3 turnover controls, P3.4 contribution handling, P4 leverage, P5 cycle-exit, P6 shadow, P7 live or P8 bear research inside the P3.1 PR.

## Exact next action

```text
finish and merge P2.4 post-merge handoff
-> from then-current main create a fresh P3.1/data-contract candidate branch
-> implement P3.1 only
-> tests / self-review / drift audit / PR / CI / expected-head merge
```
