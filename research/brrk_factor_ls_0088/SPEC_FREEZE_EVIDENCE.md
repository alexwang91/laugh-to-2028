# 0088 Factor L/S SPEC_FREEZE Evidence

Research ID: `BRRK-FACTOR-LS-0088`
Gate: `SPEC_FREEZE`

- Central owner-first registry insertion completed before `research/brrk_factor_ls_0088/` existed.
- Immutable upstream dependency is only sealed 0086 `PASS_VALIDATED_FACTOR_ATLAS`.
- Frozen factor signs are `MOM60_RAW=-1`, `RVOL20_RAW=-1`, `LIQ30_RAW=+1`; no factor reselection, sign reinterpretation, coefficient fitting, or subset search is allowed.
- 0088 is not a replacement, retry, continuation, rescue, or recomputation of 0076 and inherits zero lifecycle/attempt credit from it.
- SPEC freezes exactly one equal-weight signed-rank composite, one PIT universe, one Monday UTC-close cadence, one FWD5 horizon, one top/bottom-tercile portfolio, one funding convention, C0/C1/C2 cost panels, one beta/capacity/concentration rule set, one 8-week MBB inference configuration, and G0-G9 terminal gates.
- Controlled attempt remains `0/1`; controlled reads remain `0`; engine remains `0/1`; scientific values remain unexposed.
- BUILD is restricted to synthetic/nonhistorical fixtures. ARM is metadata/schema/identity-only and must use `ControlledResearchRunnerV1SourceQualified`.
- Any future RUN requires separate irreversible user authorization.
- Governance-core schema repair was mechanical only: objective type is the existing `PORTFOLIO_INTEGRATION` enum, 0086 ancestry is represented by `RESULT_INFORMED` plus `ref_research_id`, research IDs were removed from dataset-reference fields, and preregistration carries no result evidence. `python -m research.governance.validate` passed before the repair commit was pushed.

## What did not change

`workflow run                         31381953131 / attempt 1`, CAPTURE-0001 sealed/no-retry, CAPTURE-0002 permanently claimed/no-refetch, Phase6 closeout, 0076 sealed incident state, 0085 immutable INVALID_EXECUTION, 0086 immutable PASS, 0072/0073 paused, 0083 immutable FAIL, and all production/signature/order/withdrawal/transfer prohibitions remain unchanged.
