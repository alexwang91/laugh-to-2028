# BRRK Current State

Last updated: 2026-08-14

Authoritative repository: `alexwang91/laugh-to-2028`.
Merged implementation: `981a38dc2a7f02094d19c5de44e39afc10942510`.
Active branch: `research/0063-boundary-v1`.
The pre-0063 long-form handoff remains preserved by Git history at blob `dcc655864caf0a62a5123b38700047b77920e546`.

## Required closed-research anchors

BRRK-EXHAUSTION-EVENT-STUDY-0043 — complete diagnostic
workflow run                         31381953131 / attempt 1
7–14 day exhaustion-ranking signal appears feasible
ID 0043 is closed against result-informed pruning, reweighting, threshold rescue

## Research state

0062 = `FAIL_NO_SIGNAL_ATLAS_FAMILY_INFORMATION / CLOSED`; same-ID rerun/retune/rescue forbidden.
0063 = `CONTROLLED BOUNDARY FROZEN / NOT RUN`.
Research ID = `BRRK-IDLE-CASH-SWEEP-ROBUSTNESS-0063`.
Frozen DTB3 raw SHA256 = `4d8aee67dbd528ce38ff8482e9bb02dd5ccf2c6cd461f606fe90007151ab6879`.
Primary conservative cell = 50% realization / 10 bps.
Frozen stress cells = 16.
MBB = L60 / 4000 reps / seed 630063 / aligned non-circular moving blocks.
Implementation engine blob = `94dec1f3071ce80b859c9558556cdb4f1ffd26c8`.
Controlled runner blob = `9ce6b2d486a9dab994d9d905c1db1a63334c8de2`.
Historical execution attempt budget = 1.
Historical 0063 candidate economics = NOT COMPUTED.
Actual historical variants evaluated = 0.
RUN_ATTEMPT.marker = ABSENT.
PRIMARY_RESULT.json = ABSENT.
EXECUTION.json = ABSENT.
RUN_ONCE.marker = ABSENT.

## Exactly-once boundary

Preflight checks Git blob identities and zero-result state only; it does not open historical CSV content or call the scientific engine.
After boundary merge, the authorized execution must durably persist RUN_ATTEMPT.marker before opening any frozen historical input. Equity, weights and DTB3 may each be read once; all 16 stress cells are evaluated inside at most one scientific engine call. Same-ID rerun, recomputation, retune and rescue are forbidden after marker persistence.

## No-drift authority

production gross cap = 1.0
production_authorized_components = []
production_authorized = false
signature_authorized = false
order_submission_authorized = false

Canonical BRRK-0011 = NO CHANGE.
Phase 6 = NO CHANGE.

## Exact next step

Run a zero-result boundary preflight and standing CI. After the controlled boundary merges, execute exactly one governed historical attempt: persist the attempt marker first, read each frozen input once, call the frozen engine at most once, persist result/evidence/execution, then finalize from persisted hashes without any market re-read or remeasurement.
