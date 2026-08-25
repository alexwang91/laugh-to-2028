# 0086 SPEC_FREEZE evidence

- Clean branch base: `e643a4fb1adb9c1adaa105cbb781b7bfb969252d`.
- Owner-first bootstrap workflow: `32872260945`.
- Owner-first bootstrap job: `97881866595` = `SUCCESS`.
- Central owner registry commit: `21da7d90b6f638638238f3d04f679424000c1d6e`.
- Governed `SPEC_FREEZE.md` was introduced only after that owner commit.
- SPEC handoff bootstrap workflow: `32872508364` = `SUCCESS`.
- First exact-head governance validation exposed one schema-only defect: the provisional objective type `FACTOR_ATLAS_VALIDATION` was not in the frozen governance enum.
- Governance enum source: `config/research_governance_v1.json`; Factor Atlas is classified under the existing allowed objective `ALPHA_DISCOVERY`.
- Objective-type schema-fix workflow: `32872904680`, job `97883926627` = `SUCCESS`; it changed only the registry objective classification and removed its temporary workflow.
- Frozen scientific question, factor family, universe, inference, cost, support, terminal gates, trial budget and stopping rule were unchanged by the schema alignment.
- Controlled attempt: `0/1`.
- Controlled historical value reads: `0`.
- Scientific engine calls: `0/1`.
- Production/signature/order/withdrawal/transfer authority: `false`.

## What did not change

`workflow run                         31381953131 / attempt 1` remains immutable. CAPTURE-0001 remains sealed/no-retry. CAPTURE-0002 remains permanently claimed/no-refetch. 0070/0071/0083/0072/0073/0074/0075/0076/0084/0085 remain immutable. This evidence file contains no controlled values and grants no RUN authority.
