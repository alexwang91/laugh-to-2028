# BRRK Current State

Last updated: 2026-08-06
Status: authoritative cross-chat handoff snapshot

## Authoritative baseline

- P0.1 / P0.2: PASS / MERGED
- P1.1 through P1.8: PASS / MERGED for their canonical roadmap gates
- Phase 1 Account and execution truth: COMPLETE
- P2.1 through P2.4: PASS / MERGED
- Phase 2 Hyperliquid instrument router: COMPLETE
- P3.1 Data contract PR #68: PASS / MERGED
- P3.1 post-merge handoff PR #69: MERGED
- Audit correction PR #71: PASS / MERGED
- Current main after #71: `0f8a46d9aadb0374da40baf04762d10fa72c1eeb`
- Historical audit record: `docs/FULL_PROJECT_AUDIT_2026-08-06.md`
- Legacy backlog/roadmap bridge: `docs/BACKLOG_ROADMAP_CROSSWALK_2026-08-06.md`

## Audit correction #71 closure

#71 closed residual pre-Master-Plan execution/security acceptance gaps without changing strategy economics:

- F17: unexpected strategy-cycle execution failure now preserves best-effort operator notification while re-raising the original error;
- F19: leverage-clamped requested targets are explicitly separated from reachable targets and cannot be mislabeled as ordinary below-minimum/no-op states;
- F20: `/api/cron` requires bearer `CRON_SECRET` in shadow and trade, uses constant-time comparison, removes spoofable User-Agent authorization, and redacts external exception text;
- F21: unregistered `ALLOW_STRONG_BETA` / `HARD_BETA_CAP` and the runtime path to 1.50 were removed; P4 remains the authority for >1 leverage research;
- F22 residual timing: Vercel cron moved from 01:10 UTC to 00:05 UTC while the canonical strategy decision boundary remains 00:00 UTC;
- legacy backlog ↔ roadmap crosswalk is now part of the continuity protocol.

Final #71 head before merge:

```text
020b4b6e78ec762481497cd4c7eaedd0f4a496a3
```

Final evidence:

- Phase 0 baseline contract #93 / Actions `31115747347`: SUCCESS;
- execution tests: SUCCESS;
- research integration contract: SUCCESS;
- PR handoff governance #117 / Actions `31115876962`: SUCCESS.

#71 squash-merged as:

```text
0f8a46d9aadb0374da40baf04762d10fa72c1eeb
```

Production authorization remained unchanged.

## Current roadmap position

```text
P3.1 Data contract: PASS / MERGED
RESEARCH/EVIDENCE NORMALIZATION: ACTIVE CORRECTION GATE
P3.2 Target calculation API: NEXT ROADMAP TASK AFTER CORRECTION GATE
P3.3 Rebalance band / turnover controls: BLOCKED
P3.4 Weekly cash contribution handling: BLOCKED
P4+: BLOCKED
```

P3.2 remains the unique next roadmap implementation. The active correction is evidence/handoff normalization only; it does not introduce a new strategy hypothesis or change P3.2's economic baseline.

## Active research/evidence normalization candidate

Branch:

```text
audit/research-evidence-normalization
```

Base:

```text
0f8a46d9aadb0374da40baf04762d10fa72c1eeb
```

Scope:

1. F27 measurement fix:
   - preserve the original `idle_cash_credit_0027r1.json` as superseded evidence;
   - reconstruct day-one returns from the known $10,000 starting capital instead of `pct_change().dropna()`;
   - emit a separate R2 measurement and verify that the raw BRRK CAGR reproduces the frozen calendar-span anchor `0.6516609785`;
   - restate all affected metrics, not just CAGR;
   - qualitative F27 decision is expected to remain unchanged and must be checked from regenerated evidence.
2. `EXPOSURE-SMOOTH-0038` governance normalization:
   - explicitly record mechanism validation;
   - explicitly record **NOT PROMOTED / BASELINE UNCHANGED**;
   - prevent a fresh session from rerunning or silently substituting 0038 into V1/BRRK authority.
3. stale documentation normalization:
   - P3.1 data-contract status must no longer say candidate;
   - current-main / historical-audit wording must remain distinguishable from current roadmap state.

A dedicated research evidence CI recomputes F27 R2 from committed equity/weights and the canonical risk-free loader instead of hand-editing metrics.

Current evidence status:

```text
IMPLEMENTATION IN PROGRESS
R2 RECOMPUTATION: PENDING PR CI
MERGE: PENDING
PRODUCTION AUTHORIZATION: NO_CHANGE
```

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
- `EXPOSURE-SMOOTH-0038` is a mechanism-validation result only and is **not promoted**; V1 and BRRK-0011 authority remain unchanged.
- ASYM-BETA-0024 remains shadow-only historical evidence, not production leverage authorization.
- stopped PIT-alpha, TSMOM and carry lines remain stopped on their tested evidence bases.
- F23 funding-filter redesign remains a separately registered-research boundary and must not be slipped into P3.2.
- P4 remains the dedicated >1 leverage study.

## Project drift audit

Current audit finding:

```text
DRIFT_1
```

The remaining work is measurement/bookkeeping normalization from the pre-Master-Plan research history. No product objective, universe, venue, risk philosophy, stopped-line rule, human-approval boundary, credential boundary or production authorization changes.

Closed PR #70 remains explicitly invalid as forward evidence because it was authored from a parent 34 commits behind the canonical program. Do not revive or merge its stale roadmap rewrite.

## Production authorization

```text
NO_CHANGE
production_authorized_components = []
```

No correction authorizes live capital, leverage expansion, new assets, shorts, withdrawals, transfers or production cutover.

## Exact next action

```text
open research/evidence normalization PR
-> run F27 R2 recomputation + regression tests
-> write regenerated evidence and 0038 authority record
-> self-review / drift audit / final-head CI
-> merge
-> post-merge handoff normalization if needed
-> rebuild fresh P3.2 branch from then-current main
-> implement frozen BRRK-0011 target API only
```
