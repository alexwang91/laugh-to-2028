# P1.4 Candidate Handoff

Status: CANDIDATE / AWAITING PR CI / NOT MERGED

Roadmap task: P1.4 Reversal safety.

Acceptance gate:
- reduction and new-direction opening are distinct intents;
- reduce-only is used where applicable;
- failure during reversal cannot accidentally double directional risk.

Candidate behavior:
- reversal close is submitted as the distinct `reduce` intent using `market_close` / reduce-only semantics;
- the new-direction `increase` intent is not constructed/submitted until a fresh Hyperliquid `clearinghouseState` read proves the old-direction position is flat;
- partial old-direction remainder blocks the new-direction leg;
- unexpected cross-through into the opposite sign blocks the new-direction leg;
- malformed or failed fresh account-state reads block the new-direction leg;
- once flat is freshly verified, the opening leg persists `position_before_qty=0`, `reversal_flat_verified=true`, and the fresh-state tracking source.

Boundaries deliberately not claimed:
- P1.5 metadata-driven precision;
- P1.6 full account reconciliation;
- P1.7 complete restart recovery;
- P1.8 emergency paths;
- P2+ capabilities;
- production readiness.

Production authorization: NO_CHANGE. `production_authorized_components` remains empty.

Project drift: DRIFT_0.

Exact next step: PR -> authoritative CI -> fix P1.4 only on same PR -> final-head CI -> register implementation evidence -> merge -> normalize canonical CURRENT_STATE / NEXT_STEPS to P1.5. Do not start P1.5 before P1.4 merge.