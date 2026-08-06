# BRRK Current State

Last updated: 2026-08-06
Status: authoritative cross-chat handoff snapshot

## Authoritative baseline

- P0.1 / P0.2: PASS / MERGED
- P1.1 through P1.8: PASS / MERGED for their canonical roadmap gates
- Phase 1 Account and execution truth: COMPLETE, with a narrow legacy-backlog alerting correction now being closed for F17
- P2.1 through P2.4: PASS / MERGED
- Phase 2 Hyperliquid instrument router: COMPLETE
- P3.1 Data contract PR #68: PASS / MERGED
- P3.1 post-merge handoff PR #69: MERGED
- Authoritative main before the current audit-correction candidate: `34165f8481b8c38f7f824b2f18f7592da731223b`
- Historical audit record: `docs/FULL_PROJECT_AUDIT_2026-08-06.md`
- Legacy backlog/roadmap bridge: `docs/BACKLOG_ROADMAP_CROSSWALK_2026-08-06.md`

## Current roadmap position

```text
P3.1 Data contract: PASS / MERGED
P3.2 Target calculation API: NEXT ROADMAP TASK
P3.3 Rebalance band / turnover controls: BLOCKED
P3.4 Weekly cash contribution handling: BLOCKED
P4+: BLOCKED
```

P3.2 remains the unique next roadmap implementation task. Before coding it, the repository is closing audit-discovered legacy backlog/handoff defects that predate the Master Plan. These corrections do not authorize or implement P3.2, P4 or production trading.

## Active audit-correction candidate

PR:

```text
#71 Audit correction: close legacy execution/security gaps before P3.2
```

Branch / base:

```text
audit/f19-f21-governance-corrections
base = 34165f8481b8c38f7f824b2f18f7592da731223b
```

Scope:

- F17 residual alerting gap: preserve best-effort operator notification when a strategy cycle raises, while re-raising the original failure;
- F19: distinguish a leverage-clamped unreachable target from a genuine below-minimum/no-trade state;
- F20: make `/api/cron` bearer-secret-only in shadow and trade, use constant-time comparison, remove spoofable User-Agent authorization, and redact external exception text;
- F21: remove the unregistered env-toggleable strong-beta path to 1.50 and its `HARD_BETA_CAP` / `ALLOW_STRONG_BETA` settings;
- F22 residual timing gap: move Vercel cron from 01:10 UTC to 00:05 UTC while preserving the canonical 00:00 UTC decision timestamp;
- add a durable backlog↔roadmap crosswalk and require fresh sessions/forward PRs to consult it.

## Candidate evidence

Initial PR head `e5fb8db0e130fb0c262d040af9441fc3543913cb` exposed eight compatibility failures in the full execution suite:

- four reversal tests still constructed removed `hard_beta_cap` / `allow_strong_beta` Settings fields;
- four service reconciliation tests returned plan stubs missing the new F19 reachability contract.

These were corrected on the same PR without restoring the removed runtime bypass.

Self-review also caught one F19 ordering defect before PR creation: a leverage-clamped target could have been suppressed by `inside_beta_band` even when the current position exceeded the reachable platform cap. Clamp reachability now takes precedence and the required reduction case is regression-tested.

Verified candidate head before this evidence writeback:

```text
1146b00c62e713537dad50c7e070d913dea05a6a
```

Evidence:

- PR handoff governance #115 / Actions `31115188630`: SUCCESS;
- Phase 0 baseline contract #92 / Actions `31115188583`: SUCCESS after an infrastructure-only first retry where runner `Set up job` failed before checkout;
- execution tests: SUCCESS;
- research integration contract: SUCCESS.

Current status:

```text
CANDIDATE IMPLEMENTATION EVIDENCE: GREEN
FINAL-HEAD CI AFTER EVIDENCE WRITEBACK: PENDING
MERGE: PENDING
PRODUCTION AUTHORIZATION: NO_CHANGE
```

Do not call the correction PASS/MERGED until the final evidence-writeback head is green and PR #71 is merged.

## P3.1 retained contract

Machine-readable authority:

```text
config/data_contract.json
contract_id = BRRK-DATA-CONTRACT-P3.1-2026-08-06
```

Canonical strategy-price source remains:

```text
Binance spot BTCUSDT / ETHUSDT / SOLUSDT / BNBUSDT
1d
explicit timeZone=0 UTC
decision boundary = 00:00:00 UTC
usable candle = close_time_ms < decision_timestamp_ms
```

Missing data remains fail-closed. Research and live adapters share one canonicalizer. P3.1 does not authorize target generation or production trading.

## Research / strategy boundaries retained

- BRRK-0011 remains the frozen canonical directional research target.
- `EXPOSURE-SMOOTH-0038` is a mechanism-validation result only and is **not promoted**; its governance record still needs explicit normalization so future sessions cannot miss that decision.
- ASYM-BETA-0024 remains shadow-only historical evidence, not production leverage authorization.
- stopped PIT-alpha, TSMOM and carry lines remain stopped on their tested evidence bases.
- F23 funding-filter redesign remains a separately registered-research boundary and must not be slipped into P3.2.
- P4 remains the dedicated >1 leverage study; the audit correction only removes an unregistered 1.50 runtime branch.

## Remaining evidence-normalization correction

After the execution/security audit correction closes, one narrow research/evidence normalization should be completed before P3.2 implementation begins:

1. record `EXPOSURE-SMOOTH-0038` in the authoritative research-history / decision layer as mechanism validated but not promoted;
2. repair F27 idle-cash-credit absolute CAGR measurement by preserving the first equity observation relative to the known $10,000 initial capital; retain old published values as superseded measurement evidence and state that the qualitative F27 conclusion is unchanged;
3. update stale P3.1 documentation labels/main references where needed.

This is evidence bookkeeping / measurement correction, not a new research hypothesis.

## Project drift audit

Current repository finding:

```text
DRIFT_1
```

Reason: legacy implementation/handoff defects survived the transition from the old review backlog into the canonical roadmap. No long-universe, venue, product objective, stopped-line, catastrophic-risk, human-approval, wallet/security boundary or production authorization has changed.

Closed PR #70 is explicitly invalid as forward evidence because it was authored from a parent 34 commits behind the canonical program. Do not revive or merge its stale roadmap rewrite. Isolated findings must be reimplemented from current main under normal governance.

## Production authorization

```text
NO_CHANGE
production_authorized_components = []
```

No audit correction authorizes live capital, >1 BRRK leverage, new assets, shorts, withdrawals, external transfers or production cutover.

## Exact next action

```text
final-head CI for PR #71 after evidence writeback
-> merge #71 only if final head is green
-> normalize merged handoff if needed
-> complete narrow 0038/F27 evidence-normalization correction from fresh main
-> rebuild a fresh P3.2 target-calculation branch from then-current main
-> implement frozen BRRK-0011 target API only
```
