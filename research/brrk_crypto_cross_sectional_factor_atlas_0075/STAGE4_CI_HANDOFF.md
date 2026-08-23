# 0075 Stage4 CI handoff

Research ID: `BRRK-CRYPTO-CROSS-SECTIONAL-FACTOR-ATLAS-0075`.

Stage3 PR #374 merged as `7b0ba828c75f9ecf8293b2e99a0531eac7954720` from exact head `8a333769ff22c26ee1cbdf689561b9e5bda23f13` after all standing CI succeeded.

This branch starts Stage4 IMPLEMENTATION only. It may encode the merged Stage3 contract and synthetic-only tests. It may not open controlled historical payloads, fetch scientific source-network data, consume the Stage8 attempt, create Stage8 markers, select signs/candidates from observed history, retune, rescue, rerun or recompute.

Current accounting: controlled attempt `0/1`; controlled historical/evidence reads `0`; scientific engine calls `0`; scientific source-network fetches `0`.

The immutable historical line `workflow run                         31381953131 / attempt 1` remains required unchanged in `docs/CURRENT_STATE.md`.

Governance repair on 2026-08-23: the earlier PR metadata failures were repaired, and `docs/CURRENT_STATE.md` is now synchronized on this same Stage4 branch to Stage3 merge `7b0ba828c75f9ecf8293b2e99a0531eac7954720` / Stage4 #375 in progress / formal completion `3/10` until Stage4 merge. The synchronization changes no frozen science and consumes no scientific budget.

Fresh exact-head CI must be terminal green before merge. In addition, Stage4 implementation review must remain consistent with Stage3 Section 11 synthetic obligations; any missing synthetic mechanics/fixtures must be completed on this branch without controlled-history access before Stage4 can earn lifecycle credit.

Exact next work on this same Stage4 branch is to read the fresh exact-head standing CI, resolve any implementation/qualification-coverage gap found against frozen Stage3 Section 11, and expected-head merge only after all mandatory checks succeed with head/base unchanged. Stage5 may not begin until Stage4 merges.
