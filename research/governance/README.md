# Program-Level Epistemic Governance v1 tooling

Canonical machine semantics live in `config/research_governance_v1.json`. The three registries remain separate authority planes from `config/decision_registry.json` and the Phase 6/7/8 authority contracts.

## Commands

```bash
python -m research.governance.validate
python -m research.governance.enforce_future --base <PR_BASE_SHA>
python -m research.governance.audit
python -m research.governance.audit --json
python -m unittest discover -s research/governance -p 'test_*.py'
```

`validate` exits non-zero for `ERROR` or `BLOCKING`. Legacy `UNKNOWN` provenance and open research-governance debt remain warnings rather than retroactively invalidating the historical repository.

`enforce_future` is the prospective diff gate. On pull requests it compares the exact PR base to `HEAD`, ignores governance/common infrastructure, and requires every changed formal `research/**` path to be owned by exactly one `PROGRAM_GOVERNED_V1` record. Future records must declare non-broad `governed_path_prefixes`; unregistered or ambiguously owned research paths fail closed. The future record must contain every frozen registration field, including an explicit `failure_reason` key. `failure_reason` may be `null` before a result exists, but the field cannot be silently omitted.

`audit` is deterministic and derives counts from the machine registries. It reports research/family/variant accounting, lineage state, dataset exposure, governance debt, edge admission and production-provenance status. The audit report is derived evidence, not a replacement source of authority.

## Future fail-closed boundary

`PROGRAM_GOVERNED_V1` records require the frozen PG1 fields, structured researcher-degrees-of-freedom accounting, explicit data-budget references, typed lineage semantics, governed path ownership and `production_authorized=false`. Result-released records also require a four-dimensional evidence scorecard:

- temporal novelty;
- statistical sufficiency;
- governance integrity;
- operational realism.

The validator rejects unregistered variants, invalid/circular lineage, false independent-replication claims after result exposure, invalid dataset references, released sealed data still claimed pristine, edge admission without incremental PASS and research/edge attempts to grant production authority. The prospective diff gate additionally rejects unregistered formal research paths, overbroad/reserved path claims and ambiguous path ownership.

Legacy records remain grandfathered as `RETROSPECTIVE_LEGACY`; the diff gate does not rewrite or retroactively fail unchanged historical research. Any post-boundary modification to a formal legacy research path is treated as a new research change and therefore cannot merge without prospective v1 coverage plus the repository's existing immutable-evidence/correction rules.

These controls govern research process only. They do not change BRRK economics or confer production authority.
