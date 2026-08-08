# Program-Level Epistemic Governance v1 — Pre-Implementation Handoff

Date: 2026-08-08
Status: PREPARED / IMPLEMENTATION NOT STARTED

## 1. Purpose

The next repository program is a research-governance upgrade, not a strategy research program.

Goal:

> Extend the existing experiment-level discipline into program-level epistemic governance so the repository can account for research-process overfit, researcher degrees of freedom, lineage, repeated use of historical data, validation exposure, feature-family duplication and evidence provenance.

This handoff does **not** implement that governance. It freezes the starting point and execution boundaries for the next work session.

## 2. Canonical starting point

Prepared from canonical main:

```text
6fa1a412ea1b2d739ada8c2baee66ecd531bac81
```

That commit is the merged Phase 0–8 drift-audit closeout.

At preparation time:

```text
open pull requests = 0
production_authorized_components = []
production gross cap = 1.0
Phase 6 live elapsed evidence = MEASUREMENT_INCONCLUSIVE_TIME_DEPENDENT
Phase 7 mode = MONITOR_ONLY
Phase 8 = PREREGISTERED_TRIGGER_ABSENT_NOT_RUN
```

Historical phase/research branches are intentionally retained. Do not delete them as cleanup before the retrospective lineage/exposure audit; they may contain useful provenance about prior research decisions.

## 3. Existing governance to extend, not replace

The repository already has strong experiment-level controls, including:

- `config/decision_registry.json` for canonical decisions, stopped/rejected/shadow states and production-authority separation;
- preregistered experiment contracts with frozen questions, candidates, metrics, gates and stopping rules;
- one-time / RUN_ONCE study boundaries;
- immutable result artifacts and hashes;
- explicit FAIL_STOP / NO_PROMOTION preservation;
- Phase gates and human production-authorization boundaries;
- zero-authority Phase 6 shadow implementation;
- cross-phase drift-audit regression gates.

The program-level upgrade must reuse these mechanisms where they already provide the required authority or provenance. Do not build a parallel replacement governance system.

## 4. Program-level gaps to address

The next implementation should add the minimum sufficient machinery to answer questions that the current experiment-level system cannot reliably answer:

- how many related research trials/variants have been attempted across the program;
- which later hypotheses were informed by earlier results;
- which historical datasets/slices and result views were already exposed to the researcher;
- whether a validation/sealed slice is truly unconsumed or merely renamed/repartitioned;
- whether a feature is a new information family or another representation of an existing family;
- whether claimed incremental information was actually demonstrated;
- what research-governance debt remains unknown for legacy experiments;
- how much evidence is retrospective historical evidence versus truly elapsed future evidence.

## 5. Required design corrections relative to the initial proposal

The implementation should use the following refined semantics:

1. **Typed lineage DAG, not a single parent field.** Support relations such as RESULT_INFORMED, PARAMETER_DESCENDANT, MECHANISM_FORK, NEW_TARGET_FORK, NEW_DATA_FORK, IMPLEMENTATION_FIX, MEASUREMENT_FIX, EXTERNAL_HYPOTHESIS, INDEPENDENT_REPLICATION and SUPERSEDES.
2. **Exposure events, not only `validation_peek_count`.** A peek count should be derived from structured exposure events recording what information was released: PASS/FAIL, primary metric, predefined metric set, event summary, full table, equity curve or raw data.
3. **Dataset-slice identity, not only calendar labels.** Exposure identity must include source/version, assets, fields, resolution, date range and relevant transformation semantics so viewing BTC close does not automatically imply viewing historical OI.
4. **Research family accounting.** Different experiment IDs do not imply independent hypotheses. Related trials must share a family identity where appropriate.
5. **Independent edge is an evidence conclusion, not a manually asserted boolean.** Record feature family and incremental-evidence status against existing admitted edges.
6. **Evidence is multi-dimensional.** Do not treat one scalar evidence level as a total ordering. Track temporal novelty, statistical sufficiency, governance integrity and operational realism separately; a short live-shadow period is not automatically stronger than a rigorous sealed historical test.
7. **External hypothesis origin is provenance, not an automatic confidence bonus.**
8. **Multiple-testing statistics are applicability-gated.** Raw trial/variant/exposure accounting is mandatory; DSR/PBO/SPA/Reality Check are not universally mandatory and must not become statistical decoration.
9. **No single governance/complexity score.** Preserve a multidimensional scorecard.
10. **Separate authority planes.** Extend `decision_registry` for decisions/authorization, but do not overload it with every research trial or exposure event.

## 6. Recommended minimal architecture

The v1 implementation should aim for:

```text
Program Governance Specification v1
Research Registry
Typed Research Lineage DAG
Dataset / Validation Exposure Registry
Research Data Budget semantics
Preregistration schema extension
Program audit command + validator
CI governance gates for future research
Conservative retrospective legacy mapping
Research Governance Debt report
Edge Registry schema only
Derived audit/scorecard reports
```

Do not build a database, dashboard, API server, feature store, ML platform or complex blind-evaluation service unless later evidence shows it is necessary.

## 7. Legacy boundary

The new framework must be prospective.

Existing experiments must not be rewritten to pretend they were conducted under the new framework. Historical mappings must use a retrospective/legacy mode and preserve `UNKNOWN` where the true number of prior parameter trials, result views or researcher decisions is not historically recoverable.

At implementation start, re-read canonical `main`. If it still descends directly from the prepared audit-clean state without new strategy research, freeze an explicit `legacy_boundary_commit` and a `research_governance_version` in the new governance specification.

## 8. Strategy / production invariants

The governance upgrade must not change:

```text
BRRK-0011 strategy economics
BTC / ETH / SOL / BNB long universe
XRP feature-only role
P3 target outputs
P3.3 rebalance semantics
P4 results or leverage status
P5 results or cycle status
P8 trigger state
transaction-cost assumptions
production gross cap = 1.0
production_authorized_components = []
Phase 7 MONITOR_ONLY
first-real-short human gate
```

No historical failed/stopped/no-promotion/shadow-only result may be reinterpreted or rerun to obtain a different conclusion.

## 9. Phase 6 sequencing

Phase 6 implementation/replay remains passed. Real elapsed evidence remains unresolved because time cannot be backfilled.

Do not continue building new Phase 6 observation infrastructure before the program-governance v1 design is frozen. After governance v1 is merged, Phase 6 elapsed observations should be recorded as genuinely temporally unseen, zero-authority evidence under the new evidence/provenance model.

This is a sequencing change only. It does not weaken or alter the existing Phase 6 contract.

## 10. Recommended implementation sequence

```text
PG0  Repository governance audit / overlap map
PG1  Governance semantics + legacy boundary freeze
PG2  Machine-readable registries and schemas
PG3  Validator + deterministic program audit
PG4  Conservative retrospective legacy mapping
PG5  CI enforcement for future research
PG6  Handoff documentation + full no-strategy-drift regression
```

Use small reviewable PRs. Do not implement the entire framework as one giant refactor.

## 11. Final acceptance for the governance upgrade

The completed program must prove at minimum:

```text
NO STRATEGY CHANGE
NO UNIVERSE CHANGE
NO PARAMETER CHANGE
NO PRODUCTION AUTHORITY CHANGE
NO HISTORICAL RESULT REINTERPRETATION
NO IMMUTABLE EVIDENCE MUTATION
```

It must also demonstrate machine-auditable research IDs, family membership, typed lineage, exposure/validation consumption, stopping rules, primary metrics, governance versioning, legacy compatibility, deterministic audit output and fail-closed checks for future research.

## 12. Next action

Start a new work session from canonical `main` and execute **Program-Level Epistemic Governance v1** using this handoff plus the full execution prompt supplied by the owner.

Do not start Supertrend, funding/OI, relative-strength, new allocation, leverage or short research as part of this governance upgrade.
