# Next Steps

> Read canonical sources in repository-defined order. GitHub actual state wins over stale prose.

## Current authorized task

```text
P3.1 Data contract
```

P0.1, P0.2, P1.1-P1.8 and P2.1-P2.4 are PASS / MERGED. Phase 2 is COMPLETE.

Do not start P3.2, P3.3, P3.4, P4, P5, P6, P7 or P8 early.

## P3.1 acceptance boundary

Phase 3 goal: make the frozen BRRK directional core reproducible in live operation before adding new leverage or cycle-top intelligence.

P3.1 defines canonical sources and transformations for:

- daily close;
- missing data;
- corporate/token mapping changes where relevant;
- funding/basis inputs used by the router.

Acceptance criteria:

- UTC `00:00` daily boundary is identical in research and live;
- the same canonical historical input produces the same downstream target inputs/results.

P3.1 must define data semantics and deterministic transformations only. It must not implement P3.2 target-calculation API, P3.3 rebalance bands, P3.4 weekly cash-contribution handling, P4 leverage research or P5 cycle-exit research.

## Phase 2 closure baseline

P2.4 final implementation head:

```text
122124bf9d16f38fcb699f1d87d2750833d515d5
```

Final evidence:

- Phase 0 baseline contract #84 / Actions `31106165098`: SUCCESS;
- execution tests: SUCCESS;
- research integration contract: SUCCESS;
- PR handoff governance #105 / Actions `31106164750`: SUCCESS.

P2.4 implementation PR #66 squash-merged as:

```text
19b586c3ef08d02203d09c48b469063857d0a6b3
```

`ROUTER-DECISION-P2.4 = IMPLEMENTATION_VERIFIED`.

Phase 2 final routing boundary:

```text
BTC base long: verified spot candidate + perp fallback by cost/capacity
ETH base long: verified UETH spot candidate + perp fallback by cost/capacity
SOL base long: verified USOL spot candidate + perp fallback by cost/capacity
BNB base long: PERP_ONLY_DEFAULT
short instrument role: perp required, no bear-program authorization
leverage-overlay instrument role: perp required, no leverage-level authorization
```

Router outputs are deterministic/replayable, persistable as canonical JSONL and expose expected-versus-realized implementation-cost attribution. Production authorization remains separate.

## Full audit baseline

Full project audit:

```text
docs/FULL_PROJECT_AUDIT_2026-08-06.md
```

Historical audit `DRIFT_1` records process/implementation-detail history only. P2.4 itself closed `DRIFT_0`.

The authoritative BNB policy is:

```text
ROUTER-BNB-PERP-ONLY-2026-08-06
BNB = PERP_ONLY_DEFAULT
```

The P2.4 post-merge handoff synchronizes stale Master Plan wording with that already-approved policy; this is not a new routing decision.

## Ordered forward program

```text
P1.1-P1.8 COMPLETE
P2.1-P2.4 COMPLETE
P3.1 NEXT
P3.2 BLOCKED ON P3.1
P3.3 BLOCKED
P3.4 BLOCKED
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

P2.4 implementation:

```text
DRIFT_0
```

Post-merge Master Plan BNB wording synchronization should be recorded as documentation/authority reconciliation only; it does not create a new product, risk or production behavior.

## Exact next action

After the P2.4 post-merge handoff PR is green and merged, create a **fresh P3.1 Data contract branch from then-current main** and close only the P3.1 acceptance gate before beginning P3.2.
