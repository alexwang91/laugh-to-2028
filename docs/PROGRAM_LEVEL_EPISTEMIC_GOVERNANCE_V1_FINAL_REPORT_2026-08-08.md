# Program-Level Epistemic Governance v1 — Final Report

Date: 2026-08-08  
Scope: PG0–PG6  
Legacy boundary: `896cbd123b7a0c38943815dd802f0f9dcd12e1c2`  
Research governance version: `1`

## A. Existing State Audit

PG0 established that the repository already had substantial experiment-level discipline before Program-Level Epistemic Governance v1:

- committed preregistration contracts;
- RUN_ONCE markers/workflows;
- immutable result directories and SHA/hash references;
- result validators;
- negative-result preservation;
- FAIL_STOP / NO_PROMOTION / SHADOW_ONLY semantics;
- decision/production authority separated from research success;
- Phase 6 zero-authority shadow contracts;
- Phase 7 human-gated launch readiness;
- Phase 8 trigger-dependent short-research authority;
- Phase 0–8 drift auditing.

The missing layer was program-level epistemic accounting: research families, result-informed ancestry, variant/trial accounting, dataset-slice/exposure history, researcher degrees of freedom, research-governance debt and deterministic cross-program auditing.

PG0 therefore chose `extend, do not replace`. Existing scientific contracts, immutable evidence and production-authority sources remain authoritative in their original scopes.

## B. Architecture Added

Governance v1 adds the minimum sufficient institutional framework:

1. `config/research_governance_v1.json` — frozen governance/version/terminology/authority semantics.
2. `config/research_registry.json` — research families, experiments, typed lineage, trial/variant accounting, evidence refs and governance debt.
3. `config/dataset_exposure_registry.json` — stable dataset-slice identities and information-release/exposure events.
4. `config/edge_registry.json` — admitted incremental-information edges only; currently empty.
5. `research/governance/schemas/` — machine-readable registry contracts.
6. `research/governance/validate.py` — fail-closed registry/lineage/exposure/authority validation.
7. `research/governance/audit.py` — deterministic derived program audit.
8. `research/governance/enforce_future.py` — PR-diff gate requiring prospective v1 registration for changed formal research paths.
9. `research/governance/no_drift.py` — final boundary-to-HEAD no-drift regression.
10. `.github/workflows/research-governance.yml` — governance tests, validation, prospective enforcement, deterministic audit and no-drift CI.

No database, API server, dashboard, feature store, ML platform, automatic production promotion or single governance score was introduced.

## C. Files Changed

The governance program changes are intentionally confined to governance/configuration/documentation paths:

### Machine governance

- `config/research_governance_v1.json`
- `config/research_registry.json`
- `config/dataset_exposure_registry.json`
- `config/edge_registry.json`

### Governance tooling

- `research/governance/__init__.py`
- `research/governance/README.md`
- `research/governance/validate.py`
- `research/governance/audit.py`
- `research/governance/enforce_future.py`
- `research/governance/no_drift.py`
- `research/governance/schemas/*.json`
- `research/governance/test_*.py`
- `.github/workflows/research-governance.yml`

### Canonical / audit documentation

- `README.md`
- `docs/CURRENT_STATE.md`
- `docs/NEXT_STEPS.md`
- `docs/PROGRAM_GOVERNANCE_PG0_REPOSITORY_AUDIT_2026-08-08.md`
- `docs/PROGRAM_GOVERNANCE_V1_SPEC_2026-08-08.md`
- `docs/PROGRAM_GOVERNANCE_PG4_RETROSPECTIVE_MAPPING_2026-08-08.md`
- this final report.

The PG6 machine regression fails if a strategy, economic configuration, historical research contract/evidence path or other non-allowlisted file changed since the frozen legacy boundary.

## D. Canonical Sources of Truth

Authority remains deliberately split rather than duplicated:

| Fact class | Canonical source |
| --- | --- |
| governance version / vocabulary / authority-plane ownership | `config/research_governance_v1.json` |
| product decisions / stopped-rejected states / production authorization | `config/decision_registry.json` |
| detailed research-family / experiment / lineage / governance debt | `config/research_registry.json` |
| dataset slices / validation exposure / consumption | `config/dataset_exposure_registry.json` |
| admitted information edges | `config/edge_registry.json` |
| Phase 6 zero-authority shadow semantics | `config/phase6_shadow_contract.json` |
| Phase 7 launch authority | `config/phase7_launch_readiness.json` |
| Phase 8 bear-short research/run boundary | `research/bear_short_0001/BEAR-SHORT-0001.json` |
| current repository handoff | `docs/CURRENT_STATE.md` |
| next dependency | `docs/NEXT_STEPS.md` |
| derived program audit | `python -m research.governance.audit` |
| final strategy/governance drift proof | `python -m research.governance.no_drift` |

Derived reports do not override machine registries or original immutable evidence.

## E. Research Governance Model

### Research Family

A family groups experiments that consume substantially the same underlying information/economic idea. Different indicator names or experiment IDs do not create independent hypotheses by themselves.

### Research ID

A stable research ID identifies a formal experiment. Material new result-bearing work requires prospective registration rather than silently modifying a prior failed line.

### Preregistration

`PROGRAM_GOVERNED_V1` records must freeze the research family/domain, objective, question, hypothesis, economic mechanism, target, primary metric, data budgets, declared variant budget, stopping/pass/fail rules, follow-up boundaries, researcher degrees of freedom, lineage semantics and production relevance before result release.

### Typed Lineage DAG

Supported relations include:

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

References must exist; cycles are blocking. Result-informed descendants cannot simultaneously claim complete independent replication.

### Data Budget

```text
DEVELOPMENT
VALIDATION
SEALED
TEMPORALLY_UNSEEN
```

Development data permits repeated exploration. Validation releases are recorded. SEALED data is consumed when information is released and cannot be renamed back into pristine holdout status. `TEMPORALLY_UNSEEN` means genuinely future data generated after the relevant research freeze.

### Exposure Event

The exposure ledger records what information was actually released, not merely a scalar peek count. Release types range from PASS/FAIL-only to full tables, equity curves and raw data.

### Sealed Data

A released SEALED slice cannot remain `DATA_SEALED`; that transition is fail-closed.

### Researcher-Exposed History

Historical data already known to researchers may still support formal validation, but it cannot be represented as genuinely unknown future history by repartitioning the same dates.

### Temporally Unseen Data

This is the project’s most valuable prospective epistemic capital. Future Phase 6 elapsed observations enter this category as `ZERO_AUTHORITY_SHADOW` evidence, without backfill.

### Research Governance Debt

Legacy facts that cannot be reliably recovered are explicitly represented as debt instead of guessed.

### Edge Registry

An edge is an evidence conclusion, not a researcher declaration. Admission requires evidence of incremental information. The registry remains empty at governance-v1 closeout; BRRK and legacy features were not retroactively declared v1-validated edges.

### Program Audit

`python -m research.governance.audit` deterministically reports trial/family/variant accounting, lineage defects, exposure consumption, governance debt, edge state and production provenance. Legacy debt correctly yields WARNING rather than being hidden to manufacture a clean PASS.

## F. Retrospective Audit

PG4 conservatively maps 17 legacy research records, including:

- BRRK-0011;
- PIT / TSMOM / funding / carry lines;
- ASYM-BETA-0024;
- EXPOSURE-SMOOTH-0038;
- LEVERAGE-0039 / 0040 / 0041;
- P5.1–P5.5;
- BEAR-SHORT-0001.

Explicit contract-supported lineage was recovered where possible, for example:

```text
LEVERAGE-0040 --SUPERSEDES--> LEVERAGE-0039
LEVERAGE-0041 --RESULT_INFORMED / MECHANISM_FORK--> LEVERAGE-0040
P5.3 V2 --RESULT_INFORMED / MECHANISM_FORK--> P5.3 V1
P5.4 / P5.5 --RESULT_INFORMED--> frozen upstream P5 evidence
```

The mapping does not infer psychological ancestry from similarity alone.

Legacy data-exposure events were not fabricated. The Dataset Exposure Registry therefore remains empty at closeout because stable historical slice identity plus information-release/consumption history cannot be reconstructed reliably enough for truthful backfill.

## G. Anti-Overfit Coverage

### Same-history iterative redesign

Typed `RESULT_INFORMED` lineage, same-line fork rules and future path registration make later experiments visibly dependent on prior results rather than resetting them as nominally independent preregistrations.

### Hidden multiple testing

V1 requires raw accounting for family trials, variants, parameter candidates, validation exposures, result-informed descendants and failed ancestors.

### Validation resetting

SEALED data becomes consumed after release. A consumed slice cannot be relabeled pristine by changing a filename, split or experiment ID.

### Indicator zoo

Features must first be classified by underlying information family. Alternative representations do not automatically count as independent edges.

### Winner selection

Selected historical performance is explicitly interpreted in the context of family/variant/exposure counts. It is not treated as an unbiased estimate of future expected performance.

### False independence

Typed lineage and the `RESULT_INFORMED` versus `INDEPENDENT_REPLICATION` incompatibility prevent result-informed descendants from being represented as fully independent.

### Lineage loss

Stable IDs and explicit DAG edges preserve correction, mechanism-fork, supersession and result-informed relationships.

### Untracked parameter search

Future records freeze declared variant budgets and structured researcher-degrees-of-freedom accounting; evaluating more variants than declared is blocking.

These controls **reduce research-process overfit**. They do not eliminate it.

## H. Remaining Limitations

Governance v1 does not solve:

- market nonstationarity;
- limited independent crypto regimes;
- researcher knowledge of historical crashes, bear markets and peaks;
- serial correlation and overlapping horizons;
- regime clustering;
- cross-asset dependence and shared macro shocks;
- hidden qualitative choices outside committed artifacts;
- unknown historical local trials/views;
- future structural breaks.

Bar count or event count is not assumed to equal independent sample count.

DSR remains applicability-gated when Sharpe is a relevant selection metric and a defensible comparable trial universe exists. PBO, White Reality Check and Hansen SPA remain `DEFERRED_NOT_APPLICABLE_TO_GENERIC_V1`; v1 does not pretend generic multiple testing has been statistically solved by adding inappropriate tests.

## I. Tests

Governance v1 is covered by:

- unit tests for registry validation;
- schema contract checks;
- duplicate-ID validation;
- typed-lineage reference/cycle validation;
- false-independence validation;
- dataset/exposure and sealed-consumption validation;
- variant-budget validation;
- edge-admission validation;
- legacy compatibility / governance-debt warning behavior;
- deterministic audit tests;
- future-research path-ownership / diff enforcement tests;
- final no-drift allowlist tests;
- existing P3.2 research/live parity and committed golden-vector CI;
- existing Phase 0–8 drift audit;
- existing Phase 6 shadow safety/reconciliation gates;
- existing Phase 7 launch-readiness gates;
- existing Phase 8 trigger/short-authority gates;
- historical research contract/result validators.

The final governance workflow also runs `python -m research.governance.no_drift`, which checks the full legacy-boundary-to-HEAD changed-path set, explicit historical/economic git-blob parity and current machine authority semantics.

## J. Strategy Drift Check

Required conclusion:

```text
NO STRATEGY CHANGE
NO BNB CHANGE
NO PARAMETER CHANGE
NO COST CHANGE
NO PRODUCTION AUTHORITY CHANGE
NO HISTORICAL RESULT REINTERPRETATION
```

The final machine regression requires:

```text
directional core = BRRK-0011
long universe = BTC / ETH / SOL / BNB
XRP = feature-only
primary venue = Hyperliquid
daily decision boundary = 00:00 UTC
production gross cap = 1.0
production_authorized_components = []
Phase 6 signature_authorized = false
Phase 6 order_submission_authorized = false
Phase 6 minimum elapsed days = 14
Phase 6 minimum scheduled decisions = 10
Phase 7 = MONITOR_ONLY
Phase 7 production_authorized = false
Phase 8 = TRIGGER_ABSENT / NOT_RUN
first real short authorized = false
```

It also requires selected legacy economic/research contracts to have identical git blob SHAs at the governance boundary and final HEAD. The repository-wide changed-path allowlist rejects any non-governance strategy/evidence modification.

## K. Research Governance Debt

Six open debt classes remain explicit:

1. historical parameter/local trial counts unknown;
2. historical validation release/peek information unknown;
3. legacy dataset exposure/consumption ledger incomplete;
4. experiment lineage incomplete beyond committed evidence;
5. informal researcher decisions/discarded ideas unknown;
6. complete historical candidate/representation universe unknown.

This debt does not rewrite legacy results as invalid. It records irrecoverable uncertainty around their research-process independence and effective researcher degrees of freedom.

## L. Recommended Future Research Workflow

For any future idea:

```text
Idea
↓
Research Family
↓
Hypothesis / Mechanism
↓
Preregistration
↓
Information Test
↓
Robustness
↓
Incremental Information
↓
Freeze Edge Evidence
↓
Separate Portfolio Integration Experiment
↓
Shadow
↓
Elapsed Future Evidence
```

Operationally:

1. Create a stable `PROGRAM_GOVERNED_V1` research record before result-bearing work.
2. Declare the underlying information family, target and primary metric before seeing formal results.
3. Declare data budgets and stable slice identities.
4. Declare variant/parameter budgets and stopping rules.
5. Record all validation/sealed information releases as exposure events.
6. Preserve failed results and lineage; do not rescue the same failed idea with cosmetic parameter changes.
7. Require evidence of incremental information before Edge Registry admission.
8. Use a separate `PORTFOLIO_INTEGRATION` experiment before changing BRRK portfolio behavior.
9. Treat research PASS as `ELIGIBLE_FOR_NEXT_RESEARCH_STAGE`, never automatic production authorization.
10. Accumulate zero-authority shadow evidence and genuinely temporally unseen data before stronger claims.
11. Keep production authorization in the separate decision/phase authority plane with human gates intact.

## Closeout

Program-Level Epistemic Governance v1 is an institutional quantitative-research control layer. It records what the program tried, what information it consumed, how experiments relate and where historical uncertainty remains. It intentionally favors fewer experiments, fewer validation releases, explicit UNKNOWNs, retained failures and future evidence over repeated optimization on the same historical feedback surface.
