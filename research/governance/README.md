# Program-Level Epistemic Governance v1 tooling

Canonical machine semantics live in `config/research_governance_v1.json`. The three registries remain separate authority planes from `config/decision_registry.json` and the Phase 6/7/8 authority contracts.

## Commands

```bash
python -m research.governance.validate
python -m research.governance.audit
python -m research.governance.audit --json
python -m unittest research.governance.test_governance
```

`validate` exits non-zero for `ERROR` or `BLOCKING`. Legacy `UNKNOWN` provenance and open research-governance debt remain warnings rather than retroactively invalidating the historical repository.

`audit` is deterministic and derives counts from the machine registries. It reports research/family/variant accounting, lineage state, dataset exposure, governance debt, edge admission and production-provenance status. The audit report is derived evidence, not a replacement source of authority.

## Future fail-closed boundary

`PROGRAM_GOVERNED_V1` records require the frozen PG1 fields, structured researcher-degrees-of-freedom accounting and `production_authorized=false`. Result-released records also require a four-dimensional evidence scorecard:

- temporal novelty;
- statistical sufficiency;
- governance integrity;
- operational realism.

The validator rejects unregistered variants, invalid/circular lineage, false independent-replication claims after result exposure, invalid dataset references, released sealed data still claimed pristine, edge admission without incremental PASS and research/edge attempts to grant production authority.

PG5 will connect these validators to diff-aware CI for new formal research. PG3 itself does not change any strategy or production authority.
