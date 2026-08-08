# Program-Level Epistemic Governance v1 — PG0 Repository Governance Audit

Date: 2026-08-08  
Roadmap task: `PG0`  
Baseline reviewed: `896cbd123b7a0c38943815dd802f0f9dcd12e1c2`  
Status: `COMPLETE / AUDIT_ONLY / NO_IMPLEMENTATION`

## 1. Scope and invariants

PG0 audits the live repository before any Program-Level Epistemic Governance v1 schema or validator is introduced. It does not change research economics, strategy parameters, asset membership, transaction-cost assumptions, historical research outcomes or production authority.

Frozen invariants remain:

```text
directional core = BRRK-0011
long universe = BTC / ETH / SOL / BNB
XRP = feature-only
primary venue = Hyperliquid
daily decision boundary = 00:00 UTC
production gross cap = 1.0
production_authorized_components = []
Phase 7 mode = MONITOR_ONLY
Phase 6 signature_authorized = false
Phase 6 order_submission_authorized = false
first real short authorized = false
```

## 2. Existing experiment-level controls

### 2.1 Preregistration contracts

The repository already uses committed JSON research contracts to freeze material experiment semantics before result-bearing runs. Representative contracts include:

- `research/leverage_0040/LEVERAGE-0040.json`;
- `research/cycle_exit/p5_2_feature_contract.json`;
- `research/cycle_exit/p5_5_validation_contract.json`;
- `research/bear_short_0001/BEAR-SHORT-0001.json`.

Existing contracts already contain many primitives that governance v1 should reuse rather than duplicate:

- experiment/contract identity;
- registration timestamp and before-run status;
- research question/objective;
- frozen candidate sets or feature definitions;
- canonical data/evaluation windows;
- primary and secondary objective semantics where relevant;
- benchmark and cost assumptions;
- hard success/failure gates;
- stopping / one-run semantics;
- forbidden follow-up or rescue actions;
- upstream artifact/hash references;
- explicit `production_authorized = false` boundaries.

The field vocabulary is heterogeneous because the contracts evolved per study. Governance v1 should normalize program-level metadata around these records without rewriting the historical contracts.

### 2.2 RUN_ONCE lifecycle

RUN_ONCE is implemented through committed marker files plus GitHub Actions workflows tied to the relevant historical research branches. The LEVERAGE-0040 workflow demonstrates the pattern:

1. verify the immutable result directory does not already contain the final result;
2. verify expected marker SHA256 values;
3. execute the frozen deterministic runner;
4. execute a dedicated result validator;
5. commit the result directory once;
6. push the immutable evidence commit to the research branch.

P5 research contains the same family of one-time marker primitives, including P5.2 feature evidence, P5.3 state paths and P5.5 joint validation.

### 2.3 Immutable evidence and hash provenance

The repository already preserves result immutability through a combination of:

- dedicated result directories;
- summary SHA256 files / recorded summary hashes;
- exact upstream blob/commit/hash references inside later contracts;
- result validators;
- separate correction records instead of silently rewriting the original intended study history;
- authoritative current-state documentation that records frozen result hashes.

This mechanism is sufficient to reuse for governance-v1 evidence references. Governance v1 does not need a second artifact store.

### 2.4 Negative-result preservation and same-line rescue prohibition

`config/decision_registry.json` already preserves stopped, rejected, shadow-only and superseded decisions. Existing contracts and governance documentation explicitly prohibit retuning failed research on the same evidence base merely to remove a failure.

Examples preserved as negative/no-promotion evidence include:

- PIT line;
- TSMOM line;
- carry line;
- `EXPOSURE-SMOOTH-0038`;
- `LEVERAGE-0040`;
- `LEVERAGE-0041`;
- P5.5 joint validation;
- trigger-absent `BEAR-SHORT-0001`.

Governance v1 must reference these states. It must not reinterpret them.

### 2.5 Result validators and CI

The repository already uses study-specific validators and GitHub Actions to enforce frozen experiment rules. Existing CI covers, depending on the study:

- preregistration/contract structure;
- marker identity;
- result absence before one-time execution;
- deterministic result validation;
- baseline parity;
- immutable-result expectations;
- research-specific hard gates;
- strategy/integration parity;
- phase-gate and drift-audit checks.

The new program validator should therefore remain a thin program-level layer. It should validate registries, cross-record references, lineage/exposure semantics and production-provenance invariants rather than replace study-specific scientific validators.

## 3. Existing program-level controls

The repository already contains several program-level primitives, although they do not yet form a complete epistemic ledger.

### 3.1 Master-plan and roadmap authority

`docs/MASTER_PLAN_2026-08-05.md`, `docs/IMPLEMENTATION_ROADMAP_2026-08-05.md`, `docs/PROJECT_GOVERNANCE_2026-08-05.md`, `docs/CURRENT_STATE.md` and `docs/NEXT_STEPS.md` define program boundaries, dependency order, change classes, human approval boundaries and the no-rescue rule.

### 3.2 Decision / authorization registry

`config/decision_registry.json` is already the machine-readable source for product decisions, implementation verification, stopped/rejected lines, shadow-only status and production authorization.

Its authority should remain narrow. It should not be overloaded with every experiment variant, lineage edge or dataset exposure event.

### 3.3 Phase authority contracts

`config/phase6_shadow_contract.json` and `config/phase7_launch_readiness.json` already encode the separation between implementation evidence and live authority:

- Phase 6 can read state and compute hypothetical routing but cannot sign or submit orders;
- Phase 6 elapsed evidence cannot be backfilled by replay;
- Phase 7 remains `MONITOR_ONLY` and `production_authorized = false`;
- owner approval remains mandatory for risk-cycle transitions.

These contracts are existing authority-plane facts. Research governance must reference them, not restate them as a competing source of truth.

### 3.4 Cross-phase drift audit

`config/phase0_8_drift_audit.json` plus the Phase 0–8 audit documentation provide an existing program-wide regression primitive for detecting implementation/authority drift without retuning economics.

Governance v1 should add research-process drift checks alongside this mechanism while preserving its scope.

### 3.5 Partial family/taxonomy primitives

P5 already groups feature definitions into named feature families and separates descriptive feature evidence from later state/economic translation. This is a reusable conceptual primitive for the governance-v1 information-family taxonomy.

It is not yet a program-wide research-family registry and must not be treated as one retrospectively.

## 4. Overlap with proposed governance v1

The proposed framework overlaps existing infrastructure in the following areas:

| Proposed concept | Existing primitive | PG0 decision |
| --- | --- | --- |
| research ID | experiment/contract IDs | reuse IDs; add stable program registry references |
| preregistration | committed JSON study contracts | extend via governance metadata; do not replace contracts |
| stopping rule | contract `stopping_rule`, RUN_ONCE or frozen run authority | normalize for future records |
| immutable evidence | result dirs, SHA256, upstream blob/commit refs | reuse directly |
| negative results | decision registry + immutable summaries | reference, do not duplicate authority |
| feature family | P5 feature-family contract | reuse terminology where economically appropriate |
| production separation | decision registry + Phase 6/7 contracts | preserve as separate authority plane |
| correction semantics | BUG_FIX / MEASUREMENT_FIX / correction records | map to typed lineage relations |
| audit | Phase-specific validators + drift audit | add program research audit only |

## 5. Missing program-level controls

The live repository does not currently provide a single deterministic answer to the following questions across research lines:

1. Which research family does each experiment belong to?
2. How many related registered trials or evaluated variants belong to that family?
3. Which later research records were informed by earlier results?
4. Which relationships are parameter descendants, mechanism forks, measurement fixes, independent replications or supersessions?
5. Which exact dataset slices were used for development, validation, sealed evaluation or later future evidence?
6. Which information was released to the researcher from those slices, and when?
7. Which nominally sealed slices have already been consumed?
8. Which historical slices are already researcher-exposed regardless of a new train/test partition?
9. Which researcher degrees of freedom can be counted, and which are historically unrecoverable?
10. Which feature representations belong to an existing underlying information family?
11. Which information edges have actually passed incremental-information evidence?
12. What research-governance debt remains for legacy studies?
13. Does a governance-v1 record fail closed when required future fields are missing?
14. Can the repository produce a deterministic program audit from machine registries rather than manually copied summaries?

These are the gaps PG1–PG5 should address.

## 6. Duplicate-system risk

The largest architectural risk is creating a new registry that accidentally becomes a second authority source for facts already owned elsewhere.

PG0 therefore freezes these ownership rules for the next design stage:

- `config/decision_registry.json` remains the source for decision/production authority.
- Existing study contracts remain the historical source for their originally preregistered scientific/economic semantics.
- Existing immutable result directories/hashes remain the evidence artifacts.
- Phase 6/7 contracts remain the phase authority sources.
- Governance-v1 research/exposure registries may reference those facts by stable ID/path/hash but must not silently override them.
- An Edge Registry may only record admitted evidence conclusions; it may start empty.

## 7. Reusable infrastructure

PG1–PG5 should preferentially reuse:

- JSON machine contracts already used throughout `config/` and `research/`;
- Python 3.12 repository tooling and deterministic validators;
- stdlib-first JSON/hash/path validation where sufficient;
- existing GitHub Actions patterns;
- RUN_ONCE marker semantics for result-bearing research;
- immutable result directories and summary hashes;
- explicit production authorization booleans;
- stable experiment/decision IDs;
- existing change classes: `BUG_FIX`, `MEASUREMENT_FIX`, `IMPLEMENTATION_HARDENING`, `NEW_HYPOTHESIS`, `PARAMETER_CHANGE`;
- current-state handoff discipline;
- cross-phase drift regression.

A database, API server, dashboard, feature store or automatic promotion system is not justified for v1.

## 8. Historical provenance sources

Retrospective lineage may use repository evidence from:

- current-main research contracts;
- immutable result summaries and hashes;
- correction records;
- RUN_ONCE markers;
- study-specific validators/workflows;
- `config/decision_registry.json`;
- merged PR metadata and commit history;
- retained P4/P5 preregistration, implementation and one-time-study branches;
- current-state / next-step handoffs.

The retained branch set includes separate P4 leverage prereg/implementation/run-once branches and P5 event-taxonomy, feature-family, state-model, behavior and joint-validation branches. These are legitimate retrospective provenance inputs and must not be deleted before PG4 mapping is complete.

## 9. Information that cannot be reliably recovered

Repository evidence cannot prove every historical researcher action. Unless a committed artifact proves otherwise, legacy mapping must use `UNKNOWN` or `NOT_HISTORICALLY_RECORDED` for facts such as:

- uncommitted parameter variants tried locally;
- charts/tables viewed outside committed artifacts;
- exact historical validation peek count;
- the information content of every informal result view;
- uncommitted candidate universes;
- informal researcher decisions and discarded ideas;
- whether two historical ideas were psychologically independent when no repository lineage statement exists;
- complete pre-repository research history.

Repository inference may be labeled `INFERRED_FROM_REPOSITORY`; it may not be promoted to historical fact.

## 10. Recommended architecture after PG0

The minimum sufficient architecture is:

```text
config/research_governance_v1.json        canonical governance/version semantics
config/research_registry.json             research family / experiment / lineage / result metadata
config/dataset_exposure_registry.json     dataset-slice identity + exposure events
config/edge_registry.json                 admitted incremental-information edges only
research/governance/                      validator + deterministic audit + tests
.github/workflows/research-governance.yml future-research fail-closed CI
```

Schemas should live with the governance tooling or another existing repository-consistent location and should be simple JSON-compatible contracts. Derived audit reports should be generated from registries and not become new manually maintained authorities.

## 11. PG0 answers to required audit questions

1. **What authority does `decision_registry` hold?** Product decisions, implementation verification, stopped/rejected/superseded/shadow-only states and production-authorized components.
2. **What fields do prereg contracts already have?** Identity, time/status, question/objective, candidates/features, inputs/windows, benchmarks/costs, gates, stopping/run authority, forbidden actions, upstream provenance and production boundaries, with study-specific naming.
3. **How does immutable evidence/hash work?** Dedicated result directories, summary SHA256, blob/commit refs, validators and separate correction evidence.
4. **How does RUN_ONCE work?** Marker-triggered workflow, marker hash checks, result-absence guard, deterministic run, validator, one-time result commit.
5. **How are negative results retained?** Decision registry, immutable summaries, no-promotion/fail-stop current-state records and no-rescue rules.
6. **What does CI already enforce?** Study contracts, one-time execution, result validation, parity, phase gates and drift checks.
7. **What Phase 6/7/8 semantics already exist?** Zero-authority shadow, time-dependent future evidence, launch-blocked monitor-only state, human approval gates and trigger-absent bear research.
8. **What primitives can be extended?** JSON contracts, stable IDs, hashes, validators, workflows, change classes, feature-family vocabulary and current-state handoffs.
9. **Which branches/PRs aid retrospective lineage?** Retained P4/P5 preregistration/implementation/RUN_ONCE branches and their merged PR/commit records.
10. **What is permanently unrecoverable?** Uncommitted trials/views/decisions and any historical relationship not evidenced by repository artifacts.

## 12. PG0 acceptance

```text
PG0 repository audit                PASS
new governance implementation       NOT STARTED BY PG0
strategy economics changed          NO
asset universe changed              NO
BNB changed                         NO
transaction costs changed           NO
historical result reinterpreted     NO
production authority changed        NO
```

Exact next task: `PG1` freeze governance version, legacy boundary, canonical terminology, authority-plane ownership, dataset/exposure semantics and typed-lineage vocabulary.
