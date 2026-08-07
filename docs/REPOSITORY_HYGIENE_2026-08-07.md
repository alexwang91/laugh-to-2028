# Repository Hygiene — 2026-08-07

Status: repository-organization record. This document does **not** change strategy, research results, or production authorization.

## Why this cleanup exists

By 2026-08-07 the repository had accumulated many short-lived implementation, handoff, audit, and research branches. The source-of-truth code was already on `main`, but remote branch count, stale README/current-state prose, and historical documents made it unnecessarily difficult to answer three basic questions:

1. What is actually merged and complete?
2. What problem is currently open?
3. What is the one next dependency?

This cleanup separates **current authority** from **historical evidence** and removes remote refs only when deletion is auditable.

## Baseline before cleanup

- normalized `main`: `98396a5b510c5f0a717b954568921c1daef6edc8` (PR #89)
- open research PR: #90, branch `p4-4/leverage-0040-one-time-study-v2`
- #90 is paused pre-result; no RUN_ONCE marker and no LEVERAGE-0040 result exist
- remote branches before cleanup: **96**

## Branch cleanup — pass 1

Run `31189904727` deleted **81** branches after re-fetching live state at execution time.

A branch qualified only when one of these rules was true:

1. it was the head of a merged PR in this repository **and** its current SHA still exactly matched the PR head SHA, proving that no post-merge commit would be discarded; or
2. it was one of two previously recorded explicit abandoned branches:
   - `p4-4/leverage-0040-one-time-study-v1` — INVALID / ABANDONED;
   - `p3-2/target-calculation-api-v2` — stale / no implementation.

Preserved unconditionally:

- `main`
- `p4-4/leverage-0040-one-time-study-v2`
- `docs/repository-hygiene-2026-08-07`

Result: **96 → 15 branches**.

## Branch cleanup — pass 2

Run `31190187270` tested every remaining historical branch against current `main` and deleted only a branch whose head commit was already an ancestor of `main` with no branch-only commit.

Deleted:

- `p3-2/target-calculation-api` @ `34165f8481b8c38f7f824b2f18f7592da731223b`

Result: **15 → 14 branches**.

## Branch cleanup — pass 3 audit

The remaining 11 historical branches had commits not reachable from current `main`, so they were not auto-deleted. Run `31190339024` audited their unique commits, PR relationship, and changed-file scope.

They are classified below. Their exact audited head SHA was recorded before deletion.

| Branch | Audited head | Classification / reason to retire |
| --- | --- | --- |
| `agent/asym-beta-0022-marginal-risk` | `1c29903d731d972f23d52022c4f76fe5b525cf55` | No PR; two branch-only commits add then remove the superseded preregistration; final unique file diff is empty. |
| `agent/funding-crossvenue-0002-overlap` | `86323e48baed6e7470f3e668d801ed27154b8509` | PR #6 merged. Canonical FUNDING-CROSSVENUE-0002 evidence is already used from `main` by later work; long-lived branch is no longer authority. |
| `agent/pit-disp-0015-validation` | `114a51802ba8a9f7f4b2e1051a316f661c7b6261` | PR #1 merged. Canonical PIT-DISP-0015 result artifacts are already part of the repository evidence used by later BRRK/P4 work. |
| `agent/tsmom-0029-first-mechanism` | `fdb146610f2da5f1514d17679294c9d69706941a` | PR #21 closed / not merged. Superseded by the later TSMOM-ALPHA-0029 line, which is registered REJECTED_STOPPED. |
| `claude/backlog-p1-p2` | `89f3dd190c4cb45cf4b231c93a2e061f912a859f` | PR #36 merged; branch-only tail is duplicate funding evidence and an obsolete summary layout, not a current authority. |
| `claude/plan-audit-2026-08-06` | `f8e49d1e7b80eb0e55b8d9a0837c85037be9d06e` | PR #70 explicitly INVALID / CLOSED / stale-main / DO NOT MERGE. |
| `p2-2/post-merge-handoff-v2` | `98f44778a5e3b2a090c2e1ed3c160ba56d94116a` | No PR; stale P2.2→P2.3 handoff prose. Later P2.3/P2.4 merged state supersedes it. |
| `p2-2/validate-spot-identities` | `147052b5ce4339cc6bedb2534d21ad5ca1043c0e` | PR #60 merged. Current main contains the canonical instrument/BNB policy lineage and later routing work. |
| `p2-3/post-merge-handoff` | `81da7da9da0f7b1fb58fb4b2703c035db966ce01` | PR #63 closed / not merged; stale handoff superseded by later P2.3 correction/normalization and P2.4. |
| `p2-3/spot-perp-cost-model` | `5ffda33bc8fb96e9d7ec50e9324709904f300bc2` | PR #62 merged; PR #64 later corrected live-L2 measurement and main contains the canonical P2.3/P2.4 path. |
| `research/tsmom-0027-pretest` | `754674e7f2f51032bfdc9e73865951fd0feb6eb8` | PR #20 closed / not merged; superseded by later TSMOM work and the final REJECTED_STOPPED decision. |

## Branch cleanup — pass 3 exact-SHA retirement

Run `31190668455`: **SUCCESS**.

The deletion step used an explicit branch→SHA allowlist built from the preceding audit. Before deleting any ref, it re-read the live branch set and required every branch to remain on the exact audited SHA. If any branch had moved, the run would have failed rather than deleting it.

All 11 audited historical refs were retired.

The workflow then required the remote branch set to be **exactly**:

```text
main
p4-4/leverage-0040-one-time-study-v2
docs/repository-hygiene-2026-08-07
```

Because the run succeeded, the verified branch count during hygiene is:

**96 → 3 remote branches**.

The temporary one-time branch-cleanup workflow was then removed from the housekeeping branch before the housekeeping PR is proposed. It is therefore not intended to enter `main`.

After the housekeeping PR itself is merged and verified, `docs/repository-hygiene-2026-08-07` should also be retired. The expected steady-state branch set during the owner-requested research pause is then:

```text
main
p4-4/leverage-0040-one-time-study-v2   # paused PR #90
```

These ref deletions retire historical/superseded branch names only. They do not delete merged commits, PR history, decision-registry records, or canonical evidence already persisted under `docs/` / `research/results/`.

## Documentation cleanup

The branch cleanup exposed a second problem: repository entry documents were materially stale.

The hygiene change therefore also:

- replaces the root README's old long-form research-status report with a current project map;
- rewrites `docs/CURRENT_STATE.md` as the single current snapshot;
- rewrites `docs/NEXT_STEPS.md` as the dependency order and explicit pause/resume rule;
- adds `docs/README.md` as the documentation/evidence index;
- keeps dated audit/research/runbook documents as evidence snapshots instead of deleting them.

Historical performance tables and experiment outputs remain under `research/results/`; they are not duplicated into the root README merely to make the front page look comprehensive.

## Documentation authority after cleanup

Use this reading order:

1. root `README.md` — project map and short current-status summary;
2. `docs/CURRENT_STATE.md` — single authoritative current snapshot;
3. `docs/NEXT_STEPS.md` — dependency order and explicit pause/resume rule;
4. `docs/MASTER_PLAN_2026-08-05.md` — frozen product/architecture intent;
5. `docs/IMPLEMENTATION_ROADMAP_2026-08-05.md` — phase definitions and acceptance criteria;
6. `config/decision_registry.json` — machine-readable accepted/rejected/shadow/production decisions;
7. `docs/README.md` — index into governance, implementation, audits, and historical evidence.

Dated audit/research documents remain evidence snapshots. They must not override `CURRENT_STATE.md` when they describe an older project state.

## Branch policy going forward

- `main` is the canonical merged source of truth.
- Keep at most one active implementation/research branch per current dependency unless a correction branch is explicitly required.
- A paused branch must be visibly labeled PAUSED in its PR and current-state handoff.
- Merged PR branches should be deleted promptly after merge verification.
- Abandoned branches should be deleted after their disposition and head SHA are recorded.
- Historical evidence belongs in merged `docs/` / `research/results/`, not in permanent remote feature branches.
- Never reuse an abandoned experiment ID or stale implementation branch.
- Branch deletion is a repository-hygiene action, not a mechanism for erasing failed or inconvenient research history.

## Current paused research boundary

PR #90 is explicitly labeled:

`P4.4 [PAUSED / DRAFT]: freeze and preflight LEVERAGE-0040 one-time study`

Repository maintenance must not automatically resume it.

After hygiene merges, #90 must remain paused until an explicit owner instruction. Any later resume must start by refreshing the candidate from then-current `main` and rerunning all applicable pre-result parity/CI/governance gates.

## What this cleanup does not change

- BRRK-0011 remains the frozen canonical directional research target.
- target/tradable long universe remains BTC/ETH/SOL/BNB; XRP remains feature-only where required by the frozen model.
- LEVERAGE-0040 remains preregistered and **NOT RUN**.
- no 1.10/1.20/1.30 result is created or observed by this cleanup.
- no operating drawdown budget is selected.
- no production gross >1 authorization is created.
- `production_authorized_components = []` remains unchanged.

## Project drift audit

`DRIFT_0`

This cleanup changes repository organization, current-status documentation and stale descriptive truth only. It does not alter frozen strategy formulas, research selection gates or production authorization.
