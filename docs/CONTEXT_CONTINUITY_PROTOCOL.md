# BRRK Context Continuity Protocol

Status: **mandatory for all forward material work**

Purpose: make GitHub, not any single chat window, the persistent memory of the project. A fresh conversation must be able to recover the exact project state without relying on prior chat context.

## 1. Canonical reading order for a fresh conversation

Before proposing or implementing work, read in this order:

1. `docs/MASTER_PLAN_2026-08-05.md`
2. `docs/IMPLEMENTATION_ROADMAP_2026-08-05.md`
3. `docs/PROJECT_GOVERNANCE_2026-08-05.md`
4. `docs/CURRENT_STATE.md`
5. `docs/NEXT_STEPS.md`
6. the most recent merged PR(s) referenced by `CURRENT_STATE.md`
7. any task-specific code, tests and evidence needed for the next roadmap item

Then verify against live repository state:

- latest `main` commit;
- open PRs;
- open issues;
- active candidate branch, if any;
- CI/check status;
- whether `CURRENT_STATE.md` is stale or inconsistent.

If repository reality conflicts with `CURRENT_STATE.md`, repository reality wins and the first action is to correct `CURRENT_STATE.md` in the next PR.

## 2. Every material PR is a handoff checkpoint

Every material PR must make it possible for another assistant or a fresh chat to answer all of the following without reading the old conversation:

- What roadmap task was attempted?
- What was actually implemented?
- What evidence/tests were obtained?
- What failed or remains uncertain?
- Did the work deviate from the master plan or roadmap?
- If it deviated, was that deviation justified and formally recorded?
- What is the exact next unblocked task?
- What must not be reopened or retuned?
- What production behavior, if any, is authorized?

To enforce this, every material PR must update `docs/CURRENT_STATE.md`.

## 3. Mandatory project-drift audit

Each material PR must compare the completed work against:

- primary objective;
- current roadmap task and dependency order;
- long/short universe boundaries;
- venue boundary;
- risk philosophy and catastrophic limit;
- human approval boundaries;
- research-discipline rules;
- production/shadow separation;
- credential/security boundary;
- stopped/rejected research lines.

Use this drift classification:

```text
DRIFT_0 = no material deviation
DRIFT_1 = implementation-detail deviation; no product/research objective change
DRIFT_2 = roadmap sequencing or scope deviation that requires explicit justification
DRIFT_3 = master-plan assumption changed; master-plan update required before merge
DRIFT_4 = unauthorized production/risk/security boundary violation; merge prohibited
```

A PR with `DRIFT_2` or higher must explicitly explain why the deviation occurred and what document is updated to make the new path authoritative.

`DRIFT_3` requires a master-plan change in the same or a preceding approved PR.

`DRIFT_4` must not merge.

## 4. `docs/CURRENT_STATE.md` contract

`CURRENT_STATE.md` is a living handoff document, not historical prose. Keep it concise and current.

It must contain:

1. latest authoritative `main` state / last merged PR reference;
2. current roadmap phase and exact next task;
3. completed tasks since the master plan;
4. current evidence status;
5. current production authorization status;
6. open blockers / uncertainties;
7. explicit stopped or forbidden work that must not be accidentally reopened;
8. latest project drift assessment;
9. next-session resume instructions;
10. last-updated date and PR number.

Old details should move to PRs/evidence documents rather than accumulating indefinitely in `CURRENT_STATE.md`.

## 5. PR body contract

Every material PR body must include these headings:

```text
## Roadmap task
## Baseline reviewed
## What changed
## What did not change
## Evidence and tests
## Project drift audit
## Risks and unresolved items
## Production authorization
## CURRENT_STATE handoff
## Exact next step
```

The PR should be understandable on its own.

## 6. Development-loop rule

For each roadmap step:

```text
READ CURRENT STATE
-> verify repo reality
-> restate acceptance gate
-> implement only the next dependency
-> test / collect evidence
-> review against master plan
-> run project-drift audit
-> correct implementation or plan if needed
-> update CURRENT_STATE
-> open PR with full handoff
-> merge only when acceptance gate is closed
```

Do not batch unrelated roadmap phases merely to reduce the number of PRs.

## 7. New-chat bootstrap procedure

A new conversation should not ask the user to restate historical decisions already captured in GitHub.

The assistant should:

1. inspect the repository first;
2. read the canonical files above;
3. inspect the latest merged PR(s) referenced by `CURRENT_STATE.md`;
4. report the recovered project state, current drift level and next task;
5. continue directly unless a genuinely new user decision is required.

## 8. Recommended new-chat prompt

```text
Continue the BRRK / laugh-to-2028 project from GitHub repository:
https://github.com/alexwang91/laugh-to-2028

Do not rely on prior chat context and do not ask me to repeat decisions already recorded in the repository.

First recover the project state from GitHub. Read, in order:
1. docs/MASTER_PLAN_2026-08-05.md
2. docs/IMPLEMENTATION_ROADMAP_2026-08-05.md
3. docs/PROJECT_GOVERNANCE_2026-08-05.md
4. docs/CONTEXT_CONTINUITY_PROTOCOL.md
5. docs/CURRENT_STATE.md
6. docs/NEXT_STEPS.md
7. the latest merged PR(s) referenced by CURRENT_STATE.md

Then verify the actual repository state: latest main commit, open PRs/issues, CI status and any active candidate branch. If CURRENT_STATE conflicts with repository reality, correct the handoff state first.

Before doing new work, tell me briefly:
- what has been completed;
- current roadmap phase/task;
- latest evidence status;
- current project-drift level;
- exact next unblocked task;
- whether anything needs correction before proceeding.

Then continue the next authorized roadmap task directly.

For every material development PR, you must:
- state the roadmap task and acceptance criteria;
- explain what changed and what did not;
- provide tests/evidence;
- perform a project-drift audit against the master plan and roadmap;
- state unresolved risks;
- state production authorization explicitly;
- update docs/CURRENT_STATE.md;
- write the exact next step so another fresh conversation can continue without this chat.

Do not silently reopen stopped research lines, change strategy parameters to rescue historical results, skip roadmap dependencies, or change production/security boundaries without the required plan update.
```

## 9. Definition of successful handoff

A handoff is successful if a fresh assistant can recover the project in one repository-reading pass and continue the exact next task without needing hidden chat history.
