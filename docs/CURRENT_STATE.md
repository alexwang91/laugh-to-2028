# BRRK Current State

Last updated: 2026-08-06
Status: authoritative cross-chat handoff snapshot

## Authoritative baseline

- P0.1 / P0.2: PASS / MERGED
- P1.1 through P1.8: PASS / MERGED; Phase 1 COMPLETE
- P2.1 through P2.4: PASS / MERGED; Phase 2 COMPLETE
- P3.1 Data contract: PASS / MERGED
- Audit correction PR #71: PASS / MERGED
- Current authoritative `main`: `0f8a46d9aadb0374da40baf04762d10fa72c1eeb`
- Legacy backlog/roadmap bridge: `docs/BACKLOG_ROADMAP_CROSSWALK_2026-08-06.md`
- Historical stale-main PR #70: INVALID / CLOSED / DO NOT REVIVE

## Current roadmap position

```text
P3.1     PASS / MERGED
#72      ACTIVE PRE-P3.2 EVIDENCE-NORMALIZATION GATE
P3.2     UNIQUE NEXT ROADMAP IMPLEMENTATION AFTER #72
P3.3+    BLOCKED
```

P3.2 remains target calculation only. It must reproduce the frozen BRRK-0011 baseline and must not absorb F23 funding redesign, EXPOSURE-SMOOTH-0038 promotion, ASYM-BETA promotion, >1 leverage, cycle-exit logic, short logic, or production authorization.

## PR #72 — research/evidence normalization

PR: `#72 Audit normalization: repair F27 measurement and record EXPOSURE-SMOOTH-0038`

Branch:

```text
audit/research-evidence-normalization
base = 0f8a46d9aadb0374da40baf04762d10fa72c1eeb
```

### IMPLEMENTED

F27 measurement correction:

- original `research/results/idle_cash_credit_0027r1.json` is preserved as superseded historical measurement evidence;
- day-one return is reconstructed from the known `$10,000` base instead of being dropped by `pct_change().dropna()`;
- the script refuses to emit R2 unless BRRK-0011 raw CAGR reproduces the frozen calendar-span anchor `0.6516609785...`;
- corrected evidence is committed as `research/results/idle_cash_credit_0027r2.json`;
- no BRRK/V1 weights, parameters, regime fit, source convention, or strategy economics changed.

Corrected F27 R2 headline metrics:

| Metric | V1 baseline | BRRK-0011 core |
|---|---:|---:|
| mean idle cash | 20.5183% | 24.5700% |
| raw CAGR | 61.3127% | 65.1661% |
| credited CAGR | 62.6632% | 66.8068% |
| CAGR delta | +1.3505 pp | +1.6407 pp |
| raw Sharpe (rf=0) | 1.2950 | 1.3532 |
| credited Sharpe (rf=0) | 1.3138 | 1.3756 |
| raw excess Sharpe | 1.2724 | 1.3667 |
| credited excess Sharpe | 1.3029 | 1.4039 |
| raw MDD | -37.6349% | -33.7151% |
| credited MDD | -36.6003% | -33.5524% |

BRRK-vs-V1 rf=0 Sharpe gap moves from `+0.0581629` to `+0.0617832`, shift `+0.0036204`. Qualitative F27 conclusion is unchanged.

EXPOSURE-SMOOTH-0038 authority normalization:

- `research/results/exposure_smooth_0038/summary.json` now states `MECHANISM_VALIDATED_NOT_PROMOTED_BASELINE_UNCHANGED`;
- `docs/EXPOSURE_SMOOTH_0038_DECISION_2026-08-06.md` records the governance decision;
- `config/decision_registry.json` records `EXPOSURE-SMOOTH-0038` as non-promoted historical/shadow evidence;
- `docs/RESEARCH_HISTORY.md` records the result and the explicit prohibition on substituting 0038 into P3.2;
- frozen V1 and BRRK-0011 authority remain unchanged.

Stale handoff normalization:

- `docs/P3_1_DATA_CONTRACT.md` status is `PASS / MERGED — canonical P3.1 data contract`;
- `docs/CURRENT_STATE.md` reflects #71 merged and #72 as the active correction gate.

### TESTED

On PR head `8c347e12c3c938b16d70728fe83f11e8b66aa484`, Actions run `31118002035` (`Research evidence normalization`) completed successfully:

- canonical metric regression: **12 passed**;
- F27 R2 recomputation: **SUCCESS**;
- anchor check: BRRK-0011 raw CAGR **65.166098%**;
- exact R2 JSON printed and subsequently committed without hand-editing metric values.

The same head's `PR handoff governance` run `31118002045` failed before checkout at GitHub runner action-resolution setup with `Service Unavailable / Failed to resolve action download info`. This is infrastructure failure, not code/test failure, and does not count as a green governance gate.

### CI VERIFIED

```text
INTERMEDIATE EVIDENCE CI: VERIFIED GREEN
FINAL-HEAD CI AFTER EVIDENCE/AUTHORITY WRITEBACK: REQUIRED BEFORE MERGE
```

Do not merge #72 until the current final head has the required successful evidence/governance CI. If marketplace action resolution fails again before checkout, retry the failed governance job; do not lower the gate.

### MERGED

```text
NO — PR #72 remains unmerged until final-head gates pass.
```

### PRODUCTION AUTHORIZED

```text
NO_CHANGE
production_authorized_components = []
```

No live capital, leverage expansion, new asset, short, withdrawal, transfer, or cutover authorization is created by #72.

## Research / strategy boundaries retained

- `BRRK-0011` remains the frozen canonical directional research target; do not retune it on the current historical window.
- `EXPOSURE-SMOOTH-0038` is mechanism-valid evidence only: **NOT PROMOTED / BASELINE UNCHANGED**.
- `ASYM-BETA-0024` remains shadow-only evidence, not leverage authorization.
- stopped PIT-alpha, TSMOM and carry lines remain stopped.
- F23 funding-response redesign remains a separately registered research boundary and must not enter P3.2.
- P4 is the first phase allowed to research >1 gross exposure.

## Project drift audit

```text
DRIFT_1
```

Reason: #72 repairs measurement and authority/handoff bookkeeping inherited from pre-Master-Plan work. It does not change the product objective, universe, venue, research target, risk philosophy, human-approval boundary, credential/security boundary, stopped-line policy, or production authorization.

## Exact next action

```text
#72 current-head CI
-> retry infrastructure-only failed governance job if required
-> self-review current diff / confirm DRIFT_1
-> expected-head merge only after final-head gates are green
-> post-merge handoff normalization
-> create fresh P3.2 branch from then-current main
-> implement frozen BRRK-0011 Target calculation API only
-> build multi-date research/live golden parity
```
