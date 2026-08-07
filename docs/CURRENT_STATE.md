# BRRK Current State

Last updated: 2026-08-07
Status: **authoritative current-state handoff**

> GitHub `main` is the canonical live ref. Repository hygiene PR #91 merged as `d158e32095b4e235644a9b5c75f914449775a7dd`; this post-merge normalization only closes the handoff and does not advance research.

## Executive state

```text
Phase 0                         COMPLETE / MERGED
Phase 1                         COMPLETE / MERGED
Phase 2                         COMPLETE / MERGED
Phase 3                         COMPLETE / MERGED
P4.1 defensive scaler          COMPLETE / MERGED / frozen [0,1]
P4 architecture + cap1         COMPLETE / MERGED
P4 margin/liquidation prereqs  COMPLETE / MERGED
Repository hygiene             COMPLETE / MERGED (#91)
LEVERAGE-0040 implementation   PRE-RESULT CANDIDATE / PAUSED
LEVERAGE-0040 search           NOT RUN
P4.5 select/fail decision      BLOCKED
P4.6 production leverage gate  BLOCKED / separate authorization
P5 exit intelligence           BLOCKED / not started
production authorization       NONE
```

`production_authorized_components = []`

## Current owner instruction

**STOP. Do not continue LEVERAGE-0040 until the owner explicitly asks to resume it.**

PR #90 remains intentionally:

`P4.4 [PAUSED / DRAFT]: freeze and preflight LEVERAGE-0040 one-time study`

Research branch:

`p4-4/leverage-0040-one-time-study-v2`

Paused branch head at the time repository hygiene completed:

`d3f4c3f9407d253b36166940f650f6a9ed92957d`

Safety state:

```text
RUN_ONCE marker                         ABSENT
research/results/leverage_0040 summary ABSENT
1.10 / 1.20 / 1.30 result observation NONE
selected research cap                  NONE
operating drawdown budget              NONE
production gross >1 authorization      NONE
```

Pre-hygiene green CI on #90 is historical evidence, **not** permission to continue. `main` changed after #90's current head; a future resume must refresh/revalidate from live main first.

## Frozen architecture and product constraints

### Directional strategy

- canonical directional research target: **BRRK-0011**;
- target/tradable assets: **BTC / ETH / SOL / BNB**;
- XRP is **feature-only** where required by the frozen BRRK regime feature model;
- XRP is not a target, position, or routing asset;
- strategy cadence: daily;
- daily boundary: 00:00 UTC.

### Execution / safety

- primary venue: Hyperliquid;
- FLAT = zero exposure;
- FLAT → LONG / SHORT requires human approval;
- intraday automation may reduce risk, not autonomously add directional exposure;
- master wallet key and withdrawal authority are forbidden;
- merged / CI-verified does not imply production-authorized.

### P4 leverage boundary

P4.1 corrected defensive scale remains strictly `[0,1]`.

Frozen pre-result multiplier:

```text
leverage_multiplier = 1 + (candidate_cap - 1) × defensive_scale
candidate caps = 1.00 / 1.10 / 1.20 / 1.30
```

No candidate >1 has been observed under LEVERAGE-0040.

## What is complete

### P0 / governance baseline

Canonical product/config authority, decision registry, project-governance rules, CI baseline, and status taxonomy are merged.

Required distinction remains:

`IMPLEMENTED → TESTED → CI VERIFIED → MERGED → PRODUCTION AUTHORIZED`

### P1 / execution truth

Merged execution safety includes:

- deterministic order identity;
- persistent ledger;
- partial-fill correctness;
- reversal safety;
- precision metadata;
- post-submit reconciliation;
- restart recovery;
- kill / emergency paths.

### P2 / instrument and route evidence

Merged:

- canonical instrument registry;
- validated spot identity handling;
- evidence-scoped BNB perp-only policy;
- reproducible route-cost model;
- corrected live-L2 measurement;
- route decision logic and capacity evidence.

Route/depth evidence remains point-in-time execution evidence, not historical PIT liquidity.

### P3 / research-to-live target pipeline

**Phase 3 COMPLETE.**

- P3.1 canonical data contract;
- PR #74 correction restoring XRP feature-only strategy input parity;
- P3.2 canonical BRRK target engine;
- independent multi-date research/live parity;
- committed historical golden vectors;
- P3.3 5% L1 rebalance / turnover semantics;
- P3.4 contribution handling.

### P4 prerequisites completed

Merged before any >1 search result:

- corrected defensive scaler `[0,1]`;
- `LEVERAGE-0039` stopped pre-run / no result / do not reuse;
- `LEVERAGE-0040` preregistration;
- corrected two-layer leverage architecture;
- cap=1 historical parity;
- Hyperliquid margin snapshot / hash;
- standard cross-margin liquidation-distance model;
- defensive-monotone multiplier policy frozen pre-result.

### Repository hygiene completed

PR #91 normalized repository structure and entry documentation without advancing strategy research.

Verified cleanup history:

```text
remote branches before       96
pass 1 retired               81
pass 2 retired                1
pass 3 audited/retired       11
active refs during PR #91     3
```

The hygiene work also:

- replaced the stale root README;
- reset `CURRENT_STATE.md` and `NEXT_STEPS.md`;
- added `docs/README.md` as the documentation/evidence index;
- corrected stale P3.1 decision-registry prose to reflect XRP feature-only parity;
- removed all temporary cleanup/registry workflows before merge;
- preserved historical audits and `research/results/` evidence.

See `docs/REPOSITORY_HYGIENE_2026-08-07.md`.

## Important issues discovered and disposition

### GOV-HIST-0073 — manual merge evidence gap

PR #73 was manually merged without a recorded final-head green governance CI run.

Historical status remains:

```text
MERGED = YES
CI VERIFIED = NO / NOT RECORDED
```

Do not retroactively convert it to CI VERIFIED.

### DATA-PARITY-P3.1 — missing XRP feature-only input

The first P3.1 contract exposed only four price series, while frozen BRRK regime features also consume XRPUSDT.

PR #74 fixed the data contract to distinguish:

```text
target assets       BTC / ETH / SOL / BNB
feature-only assets XRP
strategy signal set BTC / ETH / SOL / BNB / XRP
```

PR #91 also corrected the stale registry description. No XRP target/routing authority was introduced.

### P4.4 PREFLIGHT-RAW-TARGET-001

Initial #90 `--preflight-only` incorrectly attempted:

`gross(BRRK banded holdings) / gross(V1 banded holdings)`

That is invalid because the two published holdings paths were independently subjected to a 5% band.

Correction: rebuild raw V1 + frozen BRRK-0011 scale from frozen source authority; published banded holdings are legacy evidence only.

### P4.4 PREFLIGHT-SESSION-TIMING-002

Correction: frozen decision `2022-12-09` maps to first evaluated return session `2022-12-10`.

Both corrections occurred before any cap>1 observation and changed no economic parameter.

### Repository sprawl / stale entry docs

Resolved by PR #91. Historical evidence was retained; obsolete remote refs were retired under auditable rules.

## Research decision summary

### Canonical / retained

- BRRK-0011 directional core;
- corrected defensive risk path;
- Phase 3 canonical live target pipeline.

### Shadow / diagnostic only

- EXPOSURE-SMOOTH-0038 — **SHADOW_ONLY / NOT PROMOTED**;
- PIT dispersion diagnostics — evidence only, not target authority.

### Rejected / stopped / superseded

- PIT dynamic-alpha promotion path;
- TSMOM promotion path;
- carry/funding-alpha stack as promoted standalone strategy;
- ASYM extra-exposure variants as promoted directional authority;
- LEVERAGE-0039 — stopped pre-run, no result, never reuse.

Historical evidence remains in `research/results/` and dated docs.

## Documentation authority

Read current state in this order:

1. root `README.md`;
2. `docs/CURRENT_STATE.md` — this file;
3. `docs/NEXT_STEPS.md`;
4. `docs/MASTER_PLAN_2026-08-05.md`;
5. `docs/IMPLEMENTATION_ROADMAP_2026-08-05.md`;
6. `config/decision_registry.json`;
7. `docs/README.md` for the evidence/document index.

A dated historical report is an evidence snapshot. It does not override this file.

## Project drift audit

```text
DRIFT_0
```

Repository hygiene and this post-merge normalization do not alter frozen strategy math or production authorization.

## Exact next action

```text
STOP
KEEP PR #90 PAUSED / DRAFT
DO NOT create RUN_ONCE marker
DO NOT merge #90
```

Only after an explicit owner instruction to resume:

```text
re-fetch live main / #90 / marker / result
→ refresh #90 from then-current main
→ repeat all applicable pre-result CI/parity/governance
→ verify marker/result still absent
→ only then reconsider crossing the one-time LEVERAGE-0040 execution boundary
```
