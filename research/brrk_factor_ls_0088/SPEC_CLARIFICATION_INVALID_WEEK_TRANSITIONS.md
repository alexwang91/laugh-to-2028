# BRRK Factor Long/Short 0088 — Prospective SPEC clarification

Research ID: `BRRK-FACTOR-LS-0088`
Applies prospectively before BUILD and before any controlled value read.
Controlled attempt remains `0/1`; controlled reads remain `0`; scientific engine calls remain `0/1`.

## Clarification scope

This clarification resolves only the pre-exposure portfolio-state ambiguity identified in Issue #437. It does not change the 0086 factor identities/signs, candidate count, universe, FWD5 horizon, Monday decision cadence, basket construction, costs, funding formula, inference, G0-G9 thresholds, or trial budget.

## Frozen invalid-week state transition

Process every scheduled Monday in calendar order, including Mondays that cannot produce an evaluated return observation.

A scheduled Monday is `UNSUPPORTED` if the implementation cannot truthfully form both (a) the target portfolio and (b) every required transition from the prior portfolio state using only decision-time information and the frozen source contract. Causes include fewer than 21 finite eligible assets, incomplete required funding support, or a missing/non-positive decision-time capacity denominator for any required trade.

When scheduled Monday `t` is `UNSUPPORTED`:

1. `t` contributes no scientific weekly return observation and no imputed price, funding, turnover, capacity, beta, or cost statistic.
2. The portfolio state becomes `ZERO` for the next admissible decision. The implementation must not carry a stale target across the unsupported gap.
3. If the immediately preceding otherwise-evaluable portfolio would require an unaccounted terminal transition at `t`, remove that preceding portfolio observation from the evaluated return series. This is a mechanical support rule determined without inspecting its realized return.
4. The next admissible scheduled Monday starts from zero weights and therefore pays full entry turnover `sum_i |w_i,t - 0|` under C0/C1/C2.
5. If any name with nonzero prior target weight lacks a finite positive decision-time trailing-30 median quote-volume denominator for the required transition, `t` is `UNSUPPORTED`. No stale denominator, future denominator, cross-sectional substitute, or imputation is allowed.
6. The existing end-of-sample exception remains unchanged: do not add a liquidation charge solely because controlled history ends.

The engine must apply the same rule regardless of the sign or magnitude of any portfolio return. Support status must be computable before the affected weekly return is admitted to scientific statistics.

## BUILD qualification obligations

Synthetic/nonhistorical qualification must cover at least:

- a missing-funding-support gap;
- a `<21` finite-asset gap;
- a previously held name with a missing or non-positive capacity denominator;
- removal of the preceding observation when an unsupported transition would otherwise be unaccounted;
- restart from zero with full entry turnover;
- consecutive unsupported Mondays;
- deterministic recovery at the next admissible Monday;
- proof that changing synthetic realized returns without changing support inputs cannot change which weeks are admitted.

BUILD must fail closed if implementation cannot represent these transitions exactly.

## Governance and stopping rule

This is a pre-exposure clarification, not a new portfolio candidate. It creates no additional trial and grants no lifecycle credit. Once merged, BUILD must implement this rule exactly. No later controlled result may be used to alter the rule.

## What did not change

- 0086 remains immutable `PASS_VALIDATED_FACTOR_ATLAS`; `MOM60_RAW=-1`, `RVOL20_RAW=-1`, `LIQ30_RAW=+1` remain fixed.
- 0088 remains attempt `0/1`, controlled reads `0`, engine `0/1`, with no scientific result.
- 0076 remains sealed at its Stage7 pre-marker read-boundary incident and is not replaced by 0088.
- 0085 remains immutable `INVALID_EXECUTION` with attempt `1/1` consumed.
- 0072/0073 remain paused; 0083 remains immutable FAIL.
- `workflow run 31381953131 / attempt 1`, CAPTURE-0001 sealed/no-retry, CAPTURE-0002 permanently claimed/no-refetch, and all other immutable anchors remain unchanged.
- Phase6 closeout, `CONTROLLED_RESEARCH_RUNNER_V1` qualification, and the prospective five-gate lifecycle remain unchanged.
- Production/signature/order/withdrawal/transfer authority remains false.
