# Next Steps

> Read canonical sources in repository-defined order. GitHub actual state wins over stale prose.

## Current authorized task

```text
P2.2 UETH / USOL / BNB validation
```

P0.1, P0.2 and P1.1 through P1.8 are PASS / MERGED. Phase 1 is complete. P2.1 Canonical instrument registry is PASS / MERGED. P2.2 is the only authorized next implementation dependency.

Do not start P2.3, P2.4, P3, P4, P5, P6, P7 or P8 early.

## P2.2 acceptance boundary

Verify official identity and actual implementation constraints for UETH / USOL / BNB spot candidates.

Acceptance criteria:

- no PnL study can substitute for token-identity evidence;
- unavailable or ambiguous spot assets are explicitly marked;
- any perp-only fallback remains an implementation status, not a routing decision;
- token/pair IDs, canonical naming and custody/redemption constraints must be evidenced rather than inferred.

P2.2 does **not** include route cost modeling (P2.3), route decisions (P2.4), strategy changes or production authorization.

## P2.1 closure baseline

P2.1 Canonical instrument registry is PASS / MERGED through PR #58.

Final implementation head:

```text
85ab49f0c29fad58f3dbc5d327fdaa581811fe58
```

Final evidence:

- Phase 0 baseline contract #54 / `31097667694`: SUCCESS;
- execution tests: SUCCESS;
- research integration: SUCCESS;
- PR handoff governance #69 / `31097667779`: SUCCESS.

Squash/main commit:

```text
67ac0e2e9f85a35a4c987d28f7ddfb9a95f76f48
```

`ROUTER-INSTRUMENT-REGISTRY-P2.1 = IMPLEMENTATION_VERIFIED`.

P2.1 established a canonical registry with BTC prior spot evidence imported, while ETH/SOL/BNB remain explicitly non-routable pending P2.2.

## Ordered forward program

```text
P1.1-P1.8 COMPLETE
P2.1 COMPLETE
P2.2 CURRENT / NEXT
P2.3 BLOCKED ON P2.2
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

After this normalization PR is green and merged, start **P2.2 UETH / USOL / BNB validation** from then-current main on a fresh candidate branch. Close only the identity/implementation-constraint evidence boundary before beginning P2.3.
