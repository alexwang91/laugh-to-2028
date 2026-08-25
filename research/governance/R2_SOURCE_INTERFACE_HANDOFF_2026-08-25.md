# R2 source-interface handoff receipt

Date: 2026-08-25

This governance-only receipt binds the prospective 0086+ source-qualified-runner guard in PR #421 to the live terminal state recorded in `docs/CURRENT_STATE.md`.

- 0085 is permanently sealed `INVALID_EXECUTION / CLOSED TO SAME-ID RERUN`; attempt 1/1 is consumed.
- The unique 0085 run completed 201 controlled reads and exactly one scientific engine invocation after durable marker creation. No PASS/FAIL/INCONCLUSIVE scientific result is admissible.
- PR #420 requalified the prospective source-key interface with metadata-only validation and 20 consecutive synthetic full lifecycles.
- Future numeric controlled IDs 0086+ must use `ControlledResearchRunnerV1SourceQualified` when they use the public V1 controlled runner.
- This receipt authorizes no controlled scientific attempt and changes no frozen science, historical state, source identity, attempt budget, or production authority.

## What did not change

0076 remains sealed at its Stage7 pre-marker incident. 0072/0073 Carry remain paused/closed. 0083 remains immutable FAIL. `workflow run                         31381953131 / attempt 1`, CAPTURE-0001 sealed/no-retry, CAPTURE-0002 permanently claimed/no-refetch, Phase6 closeout, and all other immutable research states remain unchanged.
