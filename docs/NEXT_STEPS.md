# Next Steps

Status: **authoritative dependency order**
Last updated: 2026-08-07

## Owner pause

The current instruction is explicit:

> **Do not continue LEVERAGE-0040 now. Finish repository cleanup and normalization first.**

Therefore the active dependency is repository hygiene, not research execution.

## Current state

```text
Phase 0                    COMPLETE
Phase 1                    COMPLETE
Phase 2                    COMPLETE
Phase 3                    COMPLETE
P4 prerequisites           COMPLETE through cap1 / margin / liquidation / multiplier freeze
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

## Dependency 1 — finish repository hygiene

Complete the isolated housekeeping change based on normalized main after PR #89.

Required scope:

- reduce obsolete remote branch refs without deleting unreviewed unique work;
- replace stale root README with a current project map;
- rewrite `CURRENT_STATE.md` and this file to actual project state;
- add a documentation index;
- preserve historical research results/audits as evidence rather than current authority;
- record branch cleanup rules and retired branch SHAs;
- keep #90 visibly PAUSED / DRAFT;
- do not modify P4 economic parameters or run the study.

Repository branch audit result on 2026-08-07:

```text
remote branches before     96
pass 1 retired             81
pass 2 retired              1
pass 3 audited/retired     11
remaining during hygiene    3
```

The remaining set during the housekeeping PR is:

- `main`;
- `p4-4/leverage-0040-one-time-study-v2` — paused #90;
- `docs/repository-hygiene-2026-08-07` — temporary housekeeping branch.

The housekeeping branch itself should be retired after its merge is verified.

## Dependency 2 — keep P4.4 paused after hygiene merge

After repository hygiene is merged:

- do **not** automatically rebase, mark ready, create marker, or run #90;
- keep #90 draft and paused;
- treat its pre-hygiene green CI as historical evidence only because main has changed;
- no LEVERAGE-0040 result should appear merely because repository maintenance completed.

Allowed work while paused:

- documentation cleanup;
- branch/ref cleanup;
- security fixes;
- fail-closed correctness fixes that do not observe or optimize cap>1 results;
- archival/evidence normalization.

Forbidden while paused:

- create/change `RUN_ONCE_LEVERAGE_0040.marker`;
- manually dispatch the full LEVERAGE-0040 study;
- mark #90 ready for merge;
- merge #90;
- inspect or optimize 1.10/1.20/1.30 economic results;
- tune caps, budgets, stresses, multiplier policy, BRRK math, or promotion gates;
- authorize production gross >1.

## Dependency 3 — resume only on explicit owner instruction

When the owner explicitly says to resume P4.4, start from live GitHub state, not this historical SHA list.

Required resume sequence:

1. Re-fetch live `main`, PR #90 state, #90 head, workflows, marker path, and result path.
2. Confirm PR #90 is still the intended candidate and no unexpected result exists.
3. Refresh/rebase the paused candidate from then-current `main` without altering frozen economic semantics.
4. Re-run all applicable pre-result gates on the new final head:
   - Phase 0;
   - research evidence normalization;
   - P3.2 research/live parity + committed golden;
   - P4 cap=1 parity;
   - P4 pre-run prerequisite gate;
   - P4.4 study contract / R1 preflight-only;
   - PR handoff governance.
5. Require the corrected R1 preflight to exit before cap>1 candidate evaluation.
6. Re-confirm:
   - RUN_ONCE marker absent;
   - immutable result absent;
   - `production_authorized_components = []`.
7. Only then cross the exact one-time RUN_ONCE boundary.

## Dependency 4 — one-time LEVERAGE-0040 execution

When and only when resumed and pre-result gates are green:

```text
create exact marker once
→ dedicated workflow executes frozen suite once
→ commit immutable result
→ validate result digest/provenance
→ never rerun the study under the same experiment ID
```

No post-result retuning is allowed under `LEVERAGE-0040`.

If execution infrastructure fails before producing a valid result, classify the failure explicitly; do not silently rerun or modify economic semantics.

## Dependency 5 — P4.5 select/fail decision

After a valid immutable result exists, apply the preregistered selection rules exactly.

Possible outcomes:

- `NO_PROMOTION`; or
- a research promotion candidate within the frozen 1.10 / 1.20 / 1.30 set.

Neither outcome is production authorization.

Record the decision in:

- `config/decision_registry.json`;
- `docs/CURRENT_STATE.md`;
- this file;
- immutable result/evidence docs as required.

## Dependency 6 — P4.6 production gate

Production leverage authorization is a separate gate after P4.5.

It must not be inferred from:

- a successful backtest;
- a selected research cap;
- green CI;
- merged P4 code;
- acceptable liquidation-distance estimates.

Until an explicit production decision changes the registry:

```text
production_authorized_components = []
production gross cap = 1.0
```

## Dependency 7 — P5

Exit intelligence remains blocked until Phase 4 is formally resolved.

Do not pull P5 features into P4 leverage selection.

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
repository hygiene only
→ open/finish housekeeping PR
→ applicable final-head CI + governance
→ expected-head merge
→ verify new main
→ retire housekeeping branch
→ STOP
```

**No P4.4 research action follows automatically.**
