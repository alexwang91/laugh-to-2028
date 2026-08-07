# Next Steps

Status: **authoritative dependency order**
Last updated: 2026-08-07

## Current instruction

> **STOP. Do not continue LEVERAGE-0040 until the owner explicitly asks to resume it.**

Repository hygiene is complete. There is currently no automatic implementation or research dependency to execute.

## Current state

```text
Phase 0                    COMPLETE
Phase 1                    COMPLETE
Phase 2                    COMPLETE
Phase 3                    COMPLETE
P4 prerequisites           COMPLETE through cap1 / margin / liquidation / multiplier freeze
Repository hygiene         COMPLETE / MERGED (#91)
PR #90                     PAUSED / DRAFT / PRE-RESULT
LEVERAGE-0040              NOT RUN
RUN_ONCE marker            ABSENT
immutable result           ABSENT
P4.5 select/fail           BLOCKED
P4.6 production gate       BLOCKED
P5                         BLOCKED
production authorization   NONE
```

`production_authorized_components = []`

## Repository state after hygiene

PR #91 completed the repository cleanup and source-of-truth reset.

The hygiene audit reduced the remote branch inventory from 96 to the active maintenance/research set under explicit SHA/ancestry rules, retained historical evidence in merged docs/results, and established this documentation precedence:

1. root `README.md`;
2. `docs/CURRENT_STATE.md`;
3. this file;
4. `docs/MASTER_PLAN_2026-08-05.md`;
5. `docs/IMPLEMENTATION_ROADMAP_2026-08-05.md`;
6. `config/decision_registry.json`;
7. `docs/README.md` for evidence navigation.

The temporary normalization/housekeeping refs should be retired after their merges are verified. During the research pause the desired steady-state remote branch set is:

```text
main
p4-4/leverage-0040-one-time-study-v2   # PR #90, PAUSED / DRAFT
```

## While P4.4 is paused

Allowed maintenance:

- documentation/evidence cleanup;
- branch/ref hygiene;
- security fixes;
- fail-closed correctness fixes that do not observe or optimize cap>1 economics;
- dependency/security maintenance that does not alter frozen research semantics.

Forbidden without explicit owner resume:

- create/change `RUN_ONCE_LEVERAGE_0040.marker`;
- manually dispatch the full LEVERAGE-0040 study;
- mark #90 ready for merge;
- merge #90;
- inspect or optimize 1.10/1.20/1.30 economic results;
- tune caps, budgets, stresses, multiplier policy, BRRK math, or promotion gates;
- authorize production gross >1.

Pre-hygiene green CI on #90 remains evidence that the paused candidate was preflighted, but it is not current authorization because `main` has since changed.

## Resume procedure — only after explicit owner instruction

When the owner explicitly says to resume P4.4, start from live GitHub state rather than old SHAs.

Required sequence:

1. Re-fetch live `main`, PR #90 state/head, workflows, marker path, and immutable-result path.
2. Confirm #90 remains the intended candidate and no unexpected result exists.
3. Refresh/rebase the paused candidate from then-current `main` without changing frozen economic semantics.
4. Re-run all applicable pre-result gates:
   - Phase 0;
   - research evidence normalization;
   - P3.2 research/live parity + committed golden;
   - P4 cap=1 parity;
   - P4 pre-run prerequisite gate;
   - P4.4 study contract / corrected R1 preflight-only;
   - PR handoff governance.
5. Require R1 preflight to exit before cap>1 candidate evaluation.
6. Re-confirm:
   - RUN_ONCE marker absent;
   - immutable result absent;
   - `production_authorized_components = []`.
7. Only then reconsider crossing the one-time RUN_ONCE boundary.

## If P4.4 is later resumed

### One-time LEVERAGE-0040 execution

When and only when explicitly resumed and all new pre-result gates are green:

```text
create exact marker once
→ dedicated workflow executes frozen suite once
→ commit immutable result
→ validate result digest/provenance
→ never rerun the study under the same experiment ID
```

No post-result retuning is allowed under `LEVERAGE-0040`.

If infrastructure fails before a valid result is produced, classify that failure explicitly; do not silently rerun or modify economics.

### P4.5 select/fail

After a valid immutable result exists, apply the preregistered selection rules exactly.

Possible outcomes:

- `NO_PROMOTION`; or
- a research promotion candidate within 1.10 / 1.20 / 1.30.

Neither is production authorization.

### P4.6 production gate

Production leverage authorization is separate from research selection.

It must not be inferred from:

- successful backtests;
- selected research cap;
- green CI;
- merged P4 code;
- acceptable liquidation-distance estimates.

Until an explicit production decision changes the registry:

```text
production_authorized_components = []
production gross cap = 1.0
```

### P5

Exit intelligence remains blocked until Phase 4 is formally resolved. Do not pull P5 features into P4 leverage selection.

## Persistent prohibitions

- do not reuse `LEVERAGE-0039`;
- do not search above 1.30 under `LEVERAGE-0040`;
- do not weaken the frozen defensive risk gate after observing results;
- do not promote EXPOSURE-SMOOTH-0038 without its own decision path;
- do not absorb F23 funding-response logic into P4;
- do not introduce shorts or XRP target exposure through P4;
- do not conflate MERGED with PRODUCTION AUTHORIZED.

## Exact next action

```text
STOP
```

No P4.4 research action follows automatically from repository hygiene completion.
