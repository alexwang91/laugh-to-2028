# BRRK Roadmap Audit — 2026-08-07

Status: **current program-wide audit / Phase-4 closeout complete**

This document reviews the repository against:

1. `docs/MASTER_PLAN_2026-08-05.md`;
2. `docs/IMPLEMENTATION_ROADMAP_2026-08-05.md`;
3. `docs/PROJECT_GOVERNANCE_2026-08-05.md`;
4. `config/decision_registry.json`;
5. merged PR / CI / immutable-result evidence through LEVERAGE-0041.

The goal is to distinguish:

- completed roadmap work;
- stopped/shadow research;
- historical deviations that were corrected;
- unresolved drift, if any;
- the unique forward dependency after Phase 4.

## 1. Executive conclusion

Current unresolved **product / strategy / production-authority drift: none identified**.

Current canonical state is aligned with the Master Plan:

- BRRK-0011 remains the directional core;
- long targets remain BTC/ETH/SOL/BNB;
- XRP remains feature-only;
- Hyperliquid remains the primary venue;
- daily boundary remains 00:00 UTC;
- defensive risk layer remains `[0,1]`;
- leverage was researched separately from the defensive selector;
- failed research lines were stopped rather than rescued on the same evidence;
- production authorization remains empty;
- master wallet / withdrawals / external transfers remain outside scope;
- FLAT and production transition human-control boundaries remain intact.

The repository did experience several historical implementation, evidence, documentation, and architecture deviations. They are not erased; they are listed below with their correction state.

Current product-state classification: `DRIFT_0`.

The Phase-4 closeout changes were `DRIFT_1` only in the sense that they repaired stale documentation / machine-readable registry state after the completed study. They did not introduce a new economic or production deviation.

## 2. Roadmap completion map

| Roadmap area | Current status | Evidence summary |
| --- | --- | --- |
| Phase 0 — canonical config / decision governance | COMPLETE / MERGED | canonical product decisions, registry, CI/governance spine |
| Phase 1 — execution truth / safety | COMPLETE / MERGED | P1.1–P1.8 implementation verified |
| Phase 2 — instrument / routing / cost | COMPLETE / MERGED | P2.1–P2.4 implementation verified |
| P3.1 data contract | COMPLETE / MERGED | canonical research/live input semantics; XRP feature-only correction closed |
| P3.2 target calculation API | COMPLETE / MERGED | frozen BRRK-0011 product-owned target engine + independent/golden parity |
| P3.3 rebalance / turnover control | COMPLETE / MERGED | explicit 5% aggregate L1 band + deviation measurement |
| P3.4 contribution handling | COMPLETE / MERGED | next-daily equity-change handling; no intraday risk increase |
| P4.1 defensive scaler | COMPLETE / MERGED | frozen corrected `[0,1]` layer |
| P4 architecture / cap1 / liquidation prerequisites | COMPLETE / MERGED | two-layer architecture, parity, frozen margin/liquidation evidence |
| LEVERAGE-0039 | STOPPED PRE-RUN | architecture conflict detected before economic result |
| LEVERAGE-0040 | COMPLETE / IMMUTABLE / NO_PROMOTION | first valid two-layer leverage study; no selected cap |
| LEVERAGE-0041 | COMPLETE / IMMUTABLE / NO_PROMOTION | independent spot-first/reserve/funding follow-on; no selected cap |
| P4.6 production leverage | NOT ENTERED | no promoted research candidate exists |
| Phase 5 cycle-top / exit | NEXT | not started |
| Phase 6 integrated shadow | NOT STARTED | blocked behind Phase 5 |
| Phase 7 limited-capital live long | NOT STARTED | requires Phase 6 evidence + explicit production approval |
| Phase 8 bear-short research | NOT STARTED | deliberately later than long/exit readiness |

## 3. Completed implementation chain

### Phase 0

The project established canonical product scope, decision status vocabulary, source-of-truth documents, PR evidence/governance rules, and explicit separation between research/candidate development and production/ACTIVE execution.

### Phase 1 — execution truth

P1.1–P1.8 were completed in order:

- deterministic order identity;
- persistent order ledger;
- fill-driven position truth;
- close-before-reverse safety;
- exchange precision / metadata formatting;
- post-submit reconciliation;
- restart recovery;
- independent emergency / kill / verified-FLAT controls.

No Phase-1 implementation is treated as production authorization.

### Phase 2 — instrument / routing / cost

P2.1–P2.4 were completed:

- canonical instrument registry;
- spot identity validation;
- matched spot/perp economic cost model with live L2 capacity evidence;
- deterministic route decision, logging/replay, reason codes and expected-vs-realized cost attribution.

BNB remains `PERP_ONLY_DEFAULT`.

### Phase 3 — daily BRRK pipeline

P3.1–P3.4 are complete:

- canonical Binance-spot daily signal data and Hyperliquid router evidence semantics;
- product-owned BRRK-0011 target calculation API;
- explicit rebalance / turnover control;
- next-daily contribution handling.

The machine-readable decision registry historically recorded P3.1 but omitted explicit P3.2/P3.3/P3.4 rows. That was a **registry/documentation gap only**; the implementations and merge/CI evidence already existed. PR #94 normalized those rows without changing runtime behavior.

### Phase 4 — leverage

The program correctly separated:

```text
BRRK relative direction
x defensive scaler [0,1]
x optional leverage multiplier
```

`LEVERAGE-0039` was stopped before execution when review found that extending the defensive selector itself above 1.0 could invert RISK_OFF semantics. The experiment ID was not reused.

`LEVERAGE-0040` then implemented the corrected two-layer study and completed exactly once. Result: immutable `NO_PROMOTION`.

`LEVERAGE-0041` was a new preregistered hypothesis, not a rescue of 0040. It tested a spot-first base plus perp overlay architecture, 25% explicit collateral reserve, funding-aware overlay reduction, a finer cap grid, stricter liquidation-distance evidence and broad-region selection. Result: immutable `NO_PROMOTION`.

This satisfies the roadmap rule prohibiting rescue of failed historical lines without a new registered hypothesis.

## 4. LEVERAGE-0041 final evidence

Immutable result commit:

`8ea784830cfffbf892a258cb329d437725d41982`

Summary SHA256:

`e41a5895263e7aa9206df9fa99fcbb71e5f937abc4746a567fbeb462cca88d17`

Selection:

```text
status                                  ONE_TIME_PREREGISTERED_STUDY_COMPLETE
selection.status                        NO_PROMOTION
selected_research_cap                   NONE
selected_operating_max_drawdown_budget  NONE
prospective_live_cap_if_authorized      NONE
production_authorized                   false
```

5 bps candidate summary:

| Cap | CAGR | MDD | Sharpe | Pre-broad pass | Final |
| ---: | ---: | ---: | ---: | --- | --- |
| 1.00 | 61.28% | -33.83% | 1.3005 | PASS comparator | comparator |
| 1.05 | 62.56% | -35.30% | 1.2935 | FAIL | FAIL |
| 1.10 | 62.84% | -36.59% | 1.2746 | FAIL | FAIL |
| 1.15 | 62.96% | -37.90% | 1.2544 | FAIL | FAIL |
| 1.20 | 64.90% | -39.16% | 1.2574 | FAIL | FAIL |
| 1.25 | 64.89% | -40.19% | 1.2387 | FAIL | FAIL |
| 1.30 | 66.28% | -40.93% | 1.2360 | FAIL | FAIL |

Liquidation-distance evidence, frozen requirement `>55%`:

| Cap | Minimum uniform adverse move | Gate |
| ---: | ---: | --- |
| 1.00 | 45.98% | FAIL |
| 1.05 | 42.52% | FAIL |
| 1.10 | 38.54% | FAIL |
| 1.15 | 35.19% | FAIL |
| 1.20 | 32.33% | FAIL |
| 1.25 | 29.86% | FAIL |
| 1.30 | 27.71% | FAIL |

The corrected architecture does not show the earlier 0040 zero-distance/already-liquidatable accounting pathology. Instead, it demonstrates that the tested explicit-reserve architecture still does not meet the deliberately conservative >55% liquidation-distance standard.

No candidate reaches P4.6.

## 5. Historical deviation audit

### A. Legacy execution / security backlog

Historical issue: several legacy execution and operational safety details survived the migration into the Master Plan.

Correction: PR #71 closed the registered residuals before P3.2, including alert preservation, leverage-clamp truth, cron authentication/error hygiene, removal of unregistered strong-beta runtime paths, and schedule alignment.

Disposition: **CORRECTED / CLOSED**.

### B. F27 measurement and EXPOSURE-SMOOTH authority

Historical issue: idle-cash measurement dropped the first realized-equity row; EXPOSURE-SMOOTH-0038 evidence needed an explicit non-promotion authority record.

Correction: PR #72 regenerated corrected evidence while preserving R1 as historical, and recorded 0038 as `SHADOW_ONLY / NOT PROMOTED`.

Disposition: **CORRECTED / CLOSED**.

### C. P3.1 XRP feature-input parity

Historical issue: the first P3.1 contract represented the four target assets but omitted XRP as a feature-only input actually consumed by frozen BRRK-0011 regime features.

Correction: PR #74 versioned the data contract, added XRP as feature-only, preserved BTC/ETH/SOL/BNB as the only targets/routes, and PR #75 restored/confirmed post-merge CI evidence.

Disposition: **CORRECTED / CLOSED**.

### D. P4 architecture / LEVERAGE-0039

Historical issue: the first leverage preregistration treated extension of the defensive selector above 1.0 as leverage, conflicting with the Master Plan two-layer architecture and potentially inverting RISK_OFF semantics.

This was the most material roadmap deviation discovered in the reviewed history (`DRIFT_2` at discovery).

Correction: it was found **before the first economic run**. LEVERAGE-0039 was permanently stopped with no result; new LEVERAGE-0040 was preregistered with the correct two-layer architecture.

Disposition: **CORRECTED BEFORE RESULT / CLOSED**.

### E. LEVERAGE-0040 run recovery chain

During the one-time 0040 run, several non-economic implementation edge cases were discovered: cross-equity handling, already-liquidatable starting-state handling, funding-window session alignment, and post-compute serialization/validator handling.

Each correction was separately recorded, no economic parameter was changed to obtain a pass, candidate metrics were not used for result-driven retuning, and the final result was validated/committed immutably.

Disposition: **AUDITED IMPLEMENTATION RECOVERY / CLOSED**.

### F. LEVERAGE-0041 governance / one-shot boundary

Process issue: the repository wording treated each research boundary as if a new owner prompt were mandatory even after the owner had explicitly authorized the continuous research workflow.

Correction: the standing research authorization was recorded before the 0041 run. The RUN_ONCE marker remained a technical one-shot integrity control; production P4.6 remained separate.

Disposition: **PROCESS SEMANTICS CLARIFIED / CLOSED**.

### G. Repository hygiene / stale authority documents

Historical issue: many remote branches and dated handoffs made recovery noisy; some docs described old phases as current.

Correction: PRs #91/#92 normalized branch/document authority and established reading precedence. PR #94 replaced stale 0041 pre-result README/CURRENT_STATE/NEXT_STEPS text, and PR #95 removed the remaining post-merge handoff wording from the canonical next-action documents.

Disposition: **CORRECTED / CLOSED**.

### H. Decision registry P3.2–P3.4 gap

Issue: P3.2, P3.3 and P3.4 were merged/verified, but explicit rows were absent from `decision_registry.json`.

Impact: machine-readable history was incomplete; runtime/economic implementation was not affected.

Correction: PR #94 added all three `IMPLEMENTATION_VERIFIED` rows and updated LEVERAGE-0041 from a preregistered research target to completed `REJECTED_STOPPED / NO_PROMOTION`.

Disposition: **CORRECTED / CLOSED**.

## 6. Research lines that must remain stopped or shadow-only

Do not reinterpret these as hidden backlog for immediate promotion:

- `PIT-ALPHA-0016-0018` — `REJECTED_STOPPED`;
- `TSMOM-ALPHA-0029` — `REJECTED_STOPPED`;
- `FUNDING-PNL-0003` all-perp default — `REJECTED_STOPPED`;
- carry economics lines — stopped where upstream economics failed;
- `ASYM-BETA-0024` — `SHADOW_ONLY`;
- `ROUTER-PNL-0005` — shadow/implementation evidence, not production authority;
- `EXPOSURE-SMOOTH-0038` — `SHADOW_ONLY / NOT PROMOTED`;
- `LEVERAGE-0039` — stopped pre-run;
- `LEVERAGE-0040` — immutable `NO_PROMOTION`;
- `LEVERAGE-0041` — immutable `NO_PROMOTION`.

## 7. Future roadmap

### Immediate: Phase 5

Start P5.1 from a fresh branch based on current `main`.

1. P5.1 Event taxonomy.
2. P5.2 Feature families.
3. P5.3 State model.
4. P5.4 Required behavior.
5. P5.5 Event-level validation.
6. P5.6 Integration.

Phase 5 is not allowed to rewrite BRRK relative ranking merely to improve an exit result.

### Then: Phase 6

Integrated shadow system using live market/account observations with zero signing/trading authority. Require target/data/router/reconciliation drift evidence before progression.

### Then: Phase 7

Limited-capital live long only after explicit user approval, frozen release, Agent/API-only credentials, no withdrawal automation, kill switch, startup reconciliation, monitoring, and required shadow evidence.

### Later: Phase 8

Bear-short research after long/exit readiness. Start with BTC/ETH/SOL/BNB; any broader Top-20 research needs explicit contemporaneous liquidity/perp/funding/market-structure gates. First short is human-gated.

## 8. Final audit verdict

```text
current canonical product drift        DRIFT_0
unresolved production authorization    NONE
production gross cap                   1.0
Phase 4 leverage outcome               FAIL_STOP / NO_PROMOTION
eligible P4.6 leverage candidate       NONE
unique forward roadmap dependency      PHASE 5 / P5.1 EVENT TAXONOMY
```

Do not reopen a stopped historical line merely because Phase 5 has not yet started. New economic hypotheses require new registered research IDs and normal evidence governance.
