# 0088 Factor L/S SPEC clarification CI handoff

- Purpose: mechanically retrigger exact-head PR checks after completing the mandatory PR-body sections.
- Scientific semantics: unchanged from `SPEC_FREEZE.md` plus `SPEC_CLARIFICATION_INVALID_WEEK_TRANSITIONS.md`.
- Controlled attempt: `0/1`.
- Controlled reads: `0`.
- Scientific engine: `0/1`.
- Scientific values exposed: `false`.
- No historical result, source identity, factor sign, portfolio candidate, gate, threshold, common-runner contract, or production authority changes here.
- The first handoff check failed only because the PR body omitted `## What changed` and `## Risks and unresolved items`; those sections are now present.
- BUILD remains the next legal reversible gate after this clarification merges.

## What did not change

0086 remains immutable `PASS_VALIDATED_FACTOR_ATLAS`; 0085 remains immutable `INVALID_EXECUTION`; 0076 remains sealed; 0072/0073 remain paused; 0083 remains immutable FAIL; 0087 remains source-metadata blocked. Phase6 closeout, common-runner qualification, `workflow run                         31381953131 / attempt 1`, CAPTURE-0001 sealed/no-retry, and CAPTURE-0002 permanently claimed/no-refetch remain unchanged. Production/signature/order/withdrawal/transfer authority remains false.
