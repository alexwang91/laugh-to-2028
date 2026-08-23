# 0075 Stage4 CI handoff

Research ID: `BRRK-CRYPTO-CROSS-SECTIONAL-FACTOR-ATLAS-0075`.

Stage3 PR #374 merged as `7b0ba828c75f9ecf8293b2e99a0531eac7954720` from exact head `8a333769ff22c26ee1cbdf689561b9e5bda23f13` after all standing CI succeeded.

This branch starts Stage4 IMPLEMENTATION only. It may encode the merged Stage3 contract and synthetic-only tests. It may not open controlled historical payloads, fetch scientific source-network data, consume the Stage8 attempt, create Stage8 markers, select signs/candidates from observed history, retune, rescue, rerun or recompute.

Current accounting: controlled attempt `0/1`; controlled historical/evidence reads `0`; scientific engine calls `0`; scientific source-network fetches `0`.

The immutable historical line `workflow run                         31381953131 / attempt 1` remains required unchanged in `docs/CURRENT_STATE.md`.

Fresh governance finding on 2026-08-23: the previous exact-head handoff run failed first because the PR body lacked the mandatory `## Evidence and tests` and `## Risks and unresolved items` headings. Those PR metadata sections are now repaired. The next known mechanical requirement remains synchronization of `docs/CURRENT_STATE.md` onto this Stage4 branch so that it appears in the forward PR diff. This note changes no frozen science and consumes no scientific budget.

Exact next work on this same Stage4 branch is to synchronize `docs/CURRENT_STATE.md` to Stage3 merge `7b0ba828c75f9ecf8293b2e99a0531eac7954720` / Stage4 #375 in progress while preserving every immutable anchor, then require fresh exact-head standing CI before any merge. Stage5 may not begin until Stage4 merges.
