# Program-Level Epistemic Governance v1 — Canonical Semantics

Date: 2026-08-08  
Roadmap task: `PG1`  
Machine source: `config/research_governance_v1.json`

## Purpose

Program-Level Epistemic Governance v1 extends the repository's existing experiment-level preregistration, RUN_ONCE, immutable-evidence and fail-stop discipline. It adds program-level accounting for research-process overfit without replacing study-specific scientific contracts or decision/production authority.

The framework **reduces research-process overfit**. It does not eliminate nonstationarity, researcher historical knowledge, limited independent crypto regimes, hidden qualitative choices, dependence across observations or future structural breaks.

## Prospective boundary

```text
research_governance_version = 1
legacy_boundary_commit = 896cbd123b7a0c38943815dd802f0f9dcd12e1c2
```

That commit was the live canonical main verified immediately before PG0 began. No new strategy research occurred between the prepared handoff and the audit. PG0 itself changed governance documentation only, so it does not move the historical research boundary.

Research whose result-bearing historical work predates the boundary is mapped as:

```text
RETROSPECTIVE_LEGACY
```

New formal result-bearing research after the boundary must use:

```text
PROGRAM_GOVERNED_V1
```

Legacy records never pretend the v1 framework existed historically. Missing trial counts, exposure events, researcher decisions or lineage facts use `UNKNOWN` or `NOT_HISTORICALLY_RECORDED`.

## Authority planes

The v1 architecture deliberately separates authority:

| Plane | Canonical source | Owns |
| --- | --- | --- |
| Decision / Authorization | `config/decision_registry.json` | product decisions, implementation verification, stopped/rejected/shadow-only states, production authorization |
| Research | `config/research_registry.json` | families, hypotheses, experiments, typed lineage, objectives, trial accounting, evidence refs |
| Dataset Exposure | `config/dataset_exposure_registry.json` | slice identity, data budgets, releases, contamination and consumption |
| Edge | `config/edge_registry.json` | admitted incremental-information edges and allowed use |
| Phase authority | existing Phase 6/7/8 contracts | shadow/live/short authority boundaries |

The new registries may reference existing decisions, contracts and evidence but may not override them.

## Research hierarchy

```text
PROGRAM
-> RESEARCH_FAMILY
-> HYPOTHESIS
-> EXPERIMENT
-> EVIDENCE
-> DECISION
```

A different implementation or indicator name does not automatically create a new independent hypothesis. Related representations must share a research family when they consume the same underlying economic information.

## Research domains and objectives

Domains classify the information/problem area, including direction/regime, relative value, volatility/tail, derivatives crowding, liquidity/execution, portfolio integration, risk control, data quality, robustness, failure analysis and structural simplification. Reserved future domains such as options volatility, order flow, microstructure and cross-venue basis do not assert that an edge exists.

Every new formal experiment also declares an objective type. `ALPHA_DISCOVERY`, `MECHANISM_TEST`, `RISK_CONTROL`, `EXECUTION_IMPROVEMENT`, `STRUCTURAL_SIMPLIFICATION`, `DATA_QUALITY`, `ROBUSTNESS_AUDIT`, `FAILURE_ANALYSIS` and `PORTFOLIO_INTEGRATION` may require different success metrics. CAGR is not a universal objective.

## Typed lineage DAG

Lineage uses a DAG with typed relations:

```text
RESULT_INFORMED
PARAMETER_DESCENDANT
MECHANISM_FORK
NEW_TARGET_FORK
NEW_DATA_FORK
IMPLEMENTATION_FIX
MEASUREMENT_FIX
EXTERNAL_HYPOTHESIS
INDEPENDENT_REPLICATION
SUPERSEDES
```

Parents must exist and cycles are invalid. A result-informed descendant cannot claim complete independence from the result it consumed. Corrections remain distinct from new economic hypotheses.

A failed line does not become a new independent hypothesis because a lookback, threshold or weight changed. A fork after failure needs a material new mechanism, target, data source, market structure, execution assumption, regime event or external hypothesis provenance.

## Data budgets and exposure events

The canonical budgets are:

```text
DEVELOPMENT
VALIDATION
SEALED
TEMPORALLY_UNSEEN
```

Development supports repeated exploration and fitting. Its performance is not pristine OOS evidence. Validation is used for preregistered comparison and every release is logged. Sealed data remains unreleased until freeze; after release it is consumed and cannot be restored by renaming or repartitioning. Temporally unseen data is generated after the relevant research freeze.

Future Phase 6 elapsed observations enter `TEMPORALLY_UNSEEN` as zero-authority shadow evidence after governance v1 merges. This does not alter the Phase 6 requirement of 14 elapsed calendar days and 10 scheduled decisions and does not allow backfill.

A dataset slice is identified by source/version, assets, fields, resolution, time range, transformation and relevant PIT/publication semantics. Contamination therefore follows approximately:

```text
time x asset x field x source x transformation
```

A single `validation_peek_count` is only a derived count. The underlying facts are exposure events. Release types distinguish PASS/FAIL, primary metric, preregistered metric set, event summary, full table, equity curve and raw data.

## Researcher degrees of freedom

V1 separates final model complexity from research-process complexity. It records declared and actual parameter candidates, universes, horizons, rebalance variants, feature representations, special cases, researcher decisions, validation exposure and related-family trials when those facts are known.

Legacy omissions remain governance debt. The framework does not invent historical trial counts.

## Information families and Edge Registry

New indicator research starts with the underlying information family rather than an indicator zoo. Multiple price-trend or volatility representations are not independent simply because they use different names.

The Edge Registry never accepts a manually supplied `independent_edge=true`. It records the feature family, the existing information it must be incremental to, and an evidence status such as PASS/FAIL/UNKNOWN. It may initially be empty. BRRK features are not retroactively declared governance-v1 validated edges.

## Research funnel

New alpha/mechanism work should progress through:

```text
Stage 0 Hypothesis
Stage 1 Information Test
Stage 2 Robustness
Stage 3 Incremental Information
Stage 4 Portfolio Translation
Stage 5 Economics
Stage 6 Shadow
Stage 7 Elapsed Future Evidence
```

Before Stages 1–3 pass, research should avoid repeatedly using the final BRRK equity curve/CAGR/Sharpe as a general-purpose feature-selection surface.

A passing information edge does not enter BRRK directly. Portfolio integration is a separate preregistered experiment with allocation, sizing, interaction, cost and pass/fail rules frozen beforehand.

## Multiple testing and winner selection

Raw accounting is mandatory: registered experiments, family trials, variants, parameter candidates, validation exposures, result-informed descendants and failed ancestors.

DSR is applicability-gated. PBO, White Reality Check and Hansen SPA are `DEFERRED_NOT_APPLICABLE_TO_GENERIC_V1`; the framework does not add statistical methods merely for appearance.

Selected historical performance is interpreted in the context of the selection process and is not presented as an unbiased estimate of future expected performance.

## Evidence scorecard

Evidence is not collapsed to one absolute score. The canonical dimensions are:

```text
Temporal novelty
Statistical sufficiency
Governance integrity
Operational realism
```

If HIGH/MEDIUM/LOW/UNKNOWN confidence labels are later used, deterministic rules must derive them. No researcher may assign a confidence label after seeing the result and no label represents an invented probability.

Sample size claims must account for serial correlation, overlapping horizons, regime clustering, cross-asset correlation and shared macro shocks. Bar count and event count are not automatically independent sample counts.

## Production boundary

All new research defaults to:

```text
production_authorized = false
```

A research success means at most:

```text
ELIGIBLE_FOR_NEXT_RESEARCH_STAGE
```

It never authorizes live trading automatically. Decision/authorization authority remains separate.

Current authority is unchanged:

```text
production gross cap = 1.0
production_authorized_components = []
Phase 7 = MONITOR_ONLY
Phase 6 signing = false
Phase 6 submission = false
first real short authorized = false
```

## PG1 closeout

PG1 freezes semantics only. PG2 may now add the minimum machine-readable Research Registry, Dataset Exposure Registry and Edge Registry plus schemas. PG2 must not retrospectively fabricate legacy facts; detailed legacy mapping belongs to PG4.
