# Future controlled runner source-interface policy

Date: 2026-08-25

Scope: prospective research IDs 0086 and later only.

After the 0085 immutable `INVALID_EXECUTION`, the canonical controlled RUN path for future numeric research IDs is `ControlledResearchRunnerV1SourceQualified` from `research/governance/controlled_research_runner_v1_source_interface.py`.

Any future `run_controlled_once.py` that uses the public V1 controlled runner must use the source-qualified path. The governance unit test `test_future_controlled_runner_source_interface.py` enforces this rule before any future RUN can merge.

Each future controlled engine must implement metadata-only `validate_source_keys(source_keys)` and accept the exact frozen manifest filenames the runner will later expose as `EngineContext.sources` keys. The validator runs before marker creation, controlled reads, and scientific engine invocation.

This policy does not authorize a future controlled attempt. SPEC/BUILD/ARM/RUN/SEAL authorization rules remain unchanged.

## What did not change

- 0085 remains permanently sealed `INVALID_EXECUTION`; attempt 1/1 remains consumed.
- No 0085 rerun, rescue, recomputation, reinterpretation, source substitution, or replacement is authorized.
- 0070/0071/0083/0072/0073/0074/0075/0084 remain immutable.
- 0076 remains sealed at its Stage7 pre-marker incident with no replacement.
- `workflow run                         31381953131 / attempt 1` remains protected.
- CAPTURE-0001 remains sealed/no-retry.
- CAPTURE-0002 remains permanently claimed/no-refetch.
- Phase6 closeout remains unchanged.
- No production/signature/order/withdrawal/transfer authority is granted.
