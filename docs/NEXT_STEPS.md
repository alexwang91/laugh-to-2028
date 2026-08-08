# BRRK Next Steps

Last updated: 2026-08-08

## Current instruction

**P5.5 validation rules are frozen and the runner/validator are implemented. R2 aligns the economic end to the immutable P5.3 state-evidence end `2026-02-28` before any candidate economics. Run preflight CI, then one deterministic RUN_ONCE.**

## Immediate state

```text
Phase 0-3                              COMPLETE / MERGED
Phase 4 leverage research              FAIL_STOP
production gross cap                   1.0
production_authorized_components       []
P5.1 event taxonomy                    COMPLETE / FROZEN
P5.2 feature evidence                  COMPLETE / IMMUTABLE through 2026-02-28
P5.3 V1                               IMMUTABLE / ARCHITECTURE_FAIL
P5.3 V2                               IMMUTABLE EVIDENCE / ARCHITECTURE_PASS through 2026-02-28
P5.4 fixed candidates + pure mapping   COMPLETE / NO SELECTION
P5.5 validation contract               MERGED / FROZEN R1+R2
P5.5 runner/validator                  IMPLEMENTED / NOT RUN
P5.6 integration                       NOT STARTED
Phase 6-8                              NOT STARTED
```

## R2 common-coverage rule

P5.5 needs both frozen BRRK targets and frozen cycle state. BRRK prices/targets extend to `2026-08-02`, but immutable P5.2/P5.3 evidence ends `2026-02-28`.

The pre-result R2 correction therefore freezes:

```text
P5.5 economic window  2022-12-10 .. 2026-02-28
no MARKET_STATE forward-fill
no fabricated feature/state extension
no treating absent post-end state as a deliberate zero-risk signal
```

All candidate values, event gates, cost grid, robustness thresholds and selection rules are unchanged.

## P5.5 implementation

The runner:

- rebuilds authoritative frozen BRRK targets/prices through existing Phase-4 authority;
- applies the already-frozen P5.4 scalar mapping to each V2 MARKET_STATE profile;
- runs exactly 12 profile/map candidates at `5/10/20/50 bps`;
- uses the existing drifted-weight 5% L1 economic simulator;
- computes event behavior on the full 2021–2026 V2 state evidence without inventing 2021 BRRK returns;
- computes four start-date robustness slices and six event-held-out tests;
- builds frozen gate matrix and broad-policy adjacency;
- selects by highest 5-bps CAGR only among all-gate passers;
- fail-stops if none pass;
- never grants production or re-risk permission.

## Exact next step

```text
OPEN P5.5 IMPLEMENTATION PR
RUN FINAL PRE-RUN CI
IF GREEN -> COMMIT THE SINGLE RUN_ONCE MARKER
RUN / VALIDATE / COMMIT IMMUTABLE P5.5 RESULT
CLOSEOUT + MERGE
IF RESEARCH CANDIDATE EXISTS -> P5.6 INTEGRATE IT
IF NONE -> P5.6 BLOCKED / FAIL_STOP
CONTINUE TO PHASE 6 READINESS WITHOUT FAKING A MISSING P5.6 CANDIDATE
```
