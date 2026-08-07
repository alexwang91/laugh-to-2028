# BRRK Next Steps

Last updated: 2026-08-07

## Current instruction

**P4.4 pre-result validation is resumed. Do not cross the LEVERAGE-0040 RUN_ONCE boundary automatically.**

The owner instruction authorizes the repository refresh and refreshed pre-result validation workflow only.

## Immediate state

```text
main                                  3690f64a6179a759a60d9759c214d59cf604869e
P4.4 refresh checkpoint               ee49ea6028b5c4426d03af81657663b7ede9d987
PR #90                                OPEN / DRAFT
LEVERAGE-0040 full study               NOT RUN
RUN_ONCE marker                        ABSENT
immutable leverage_0040 result         ABSENT
1.10 / 1.20 / 1.30 results             NOT OBSERVED
selected research cap                 NONE
operating drawdown budget             NONE
P4.5                                   BLOCKED
P4.6 production authorization         BLOCKED
P5                                     BLOCKED
production_authorized_components      []
```

Always re-read the current branch head and `main` before further mutations; the branch head will move as governance-only corrections are committed.

## Work allowed now

Only work required to close the **pre-result final-head gate** is in scope:

1. keep PR #90 on `p4-4/leverage-0040-one-time-study-v2` and DRAFT;
2. preserve current-main authority while retaining the preregistered P4.4 candidate implementation;
3. fix refresh/governance integration defects that do not change economics;
4. rerun all applicable pre-result CI/parity/governance checks on the final head;
5. verify corrected R1 real-data preflight exits before cap>1 evaluation and reports `cap>1 not evaluated`;
6. perform a final-head diff and project-drift audit;
7. re-confirm the marker/result are absent and production authorization remains empty.

The first refreshed governance run failed because `docs/CURRENT_STATE.md` was initially identical to `main`, so the forward-PR governance rule correctly detected that the current-state authority had not been updated in the PR diff. Correcting that documentation state is allowed and changes no economic semantics.

## Required final-head gates

At minimum, the refreshed candidate must obtain current evidence for:

- Phase 0 baseline contract;
- Research evidence normalization;
- P3.2 target research/live parity;
- committed historical golden validation;
- P4 cap=1 exact parity;
- P4 LEVERAGE-0040 pre-run prerequisites;
- P4.4 contract / corrected R1 real-data `--preflight-only`;
- PR handoff governance.

A historical green run on an older #90 head does not satisfy the final-head requirement.

No CI run means no CI PASS. A merge must never be used to infer pre-merge CI verification.

## Frozen pre-result semantics

The following must not change while fixing refresh or CI issues:

- BRRK-0011 directional model;
- defensive scale range `[0,1]`;
- candidate caps `1.00 / 1.10 / 1.20 / 1.30`;
- multiplier `1 + (candidate_cap - 1) * defensive_scale`;
- mandatory benchmark definitions;
- stress definitions and thresholds;
- selection gates;
- seed / HMM / scenario definitions;
- liquidation-model semantics;
- 5% L1 rebalance semantics;
- contribution handling;
- XRP feature-only status;
- production gross cap `1.0` before P4.6.

Do not modify economic parameters merely to make CI pass.

## One-time lifecycle boundary

### While result is absent

The only permitted economic-data path is:

`run_leverage_0040_once_r1.py --preflight-only`

It must terminate before cap>1 candidate construction/evaluation.

### If an immutable result eventually exists

The workflow must validate the existing result/digest/provenance only. It must not rerun LEVERAGE-0040 under the same experiment ID.

Any material economic change after a valid result requires a new experiment ID.

## Explicitly forbidden now

Until refreshed final-head gates and self-review are complete:

- do not create `RUN_ONCE_LEVERAGE_0040.marker`;
- do not run the 1.10 / 1.20 / 1.30 candidate suite;
- do not inspect or select cap>1 results;
- do not mark PR #90 ready;
- do not merge PR #90;
- do not start P4.5;
- do not authorize production leverage;
- do not reopen LEVERAGE-0039;
- do not promote EXPOSURE-SMOOTH-0038;
- do not introduce XRP targets, shorts, F23 redesign, P5 exits, or other unrelated research;
- do not retune BRRK or the P3.2 canonical target engine.

## Final-head self-review before any boundary decision

When all required gates are green, compare the candidate against then-current `main` and explicitly verify:

```text
RUN_ONCE marker absent
immutable result absent
no unexpected result files
no economic-parameter drift
no production-authorization drift
production_authorized_components = []
PR #90 still DRAFT
```

Also verify that refresh/governance commits only changed repository integration/current-state documentation and did not alter frozen study semantics.

## Stop point for the current resume instruction

The current instruction stops **before** RUN_ONCE.

If all pre-result gates become green, report that the one-time boundary is ready for a separate decision. Do not create the marker merely because validation succeeded.

## After a separately authorized one-time run

Only after an explicit decision to cross that boundary, the sequence remains:

```text
create exact RUN_ONCE marker once
-> dedicated workflow executes frozen LEVERAGE-0040
-> commit immutable result
-> validate digest / provenance
-> never rerun same experiment ID
-> apply preregistered P4.5 select / NO_PROMOTION rules
-> no post-result retuning
-> final-head governance
-> merge if appropriate
-> separate P4.6 production leverage authorization
```

Even a successful P4.5 research selection is not production authorization.
