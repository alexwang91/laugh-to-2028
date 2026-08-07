# BRRK Current State

Last updated: 2026-08-07
Status: authoritative cross-chat handoff snapshot

## Authoritative baseline

- P0/P1/P2: PASS / MERGED; Phases 0–2 complete.
- P3.1–P3.4: PASS / TESTED / CI VERIFIED / MERGED; **Phase 3 COMPLETE**.
- P4.1 corrected defensive scaler: PASS / MERGED; frozen strictly to `[0,1]`.
- `LEVERAGE-0039`: **STOPPED_PRE_RUN / NO_RESULT_EVER_PRODUCED / DO NOT REUSE**.
- `LEVERAGE-0040`: **PREREGISTERED / MERGED / NOT RUN**.
- Hyperliquid margin snapshot: CAPTURED / HASHED / MERGED.
- P4.3 two-layer composition + cap=1 historical parity: PASS / MERGED.
- P4.3 liquidation-distance model: PASS / MERGED by PR #88.
- P4.3 defensive-monotone multiplier policy: FROZEN PRE-RESULT / MERGED by PR #88.
- post-#88 normalization: PASS / MERGED by PR #89.

## Current main and candidate

Normalized main after PR #89:

`98396a5b510c5f0a717b954568921c1daef6edc8`

Current clean study branch:

`p4-4/leverage-0040-one-time-study-v2`

The earlier branch `p4-4/leverage-0040-one-time-study-v1` is **INVALID / ABANDONED / DO NOT MERGE / DO NOT REVIVE**. A tool-layer write-routing error created transient empty-file commits before any PR or result existed. The v2 branch was created from a clean tree; compare against main proves the transient file is absent from the v2 diff.

Current candidate state:

```text
P4.4 study implementation contract/core       IMPLEMENTED CANDIDATE / CI PENDING
P4.4 one-time runner                          IMPLEMENTED CANDIDATE / CI PENDING
P4.4 immutable-result validator               IMPLEMENTED CANDIDATE / CI PENDING
P4.4 contract + preflight workflow            IMPLEMENTED CANDIDATE / CI PENDING
P4.4 run-once workflow                        IMPLEMENTED CANDIDATE / NOT ARMED
P4.4 result-validation workflow               IMPLEMENTED CANDIDATE / NO RESULT
RUN_ONCE marker                               ABSENT
LEVERAGE-0040 1.10/1.20/1.30 evaluation      NOT RUN
P4.5 select/fail decision                     BLOCKED
P4.6 production gate                          BLOCKED
P5 exit intelligence                          BLOCKED
```

**SEARCH RUN: NO. RESULT SELECTED: NO. OPERATING BUDGET FROZEN: NO. PRODUCTION >1 AUTHORIZATION: NO.**

## Frozen architecture

```text
BRRK directional weights
× frozen defensive_scale in [0,1]
× leverage_multiplier
= final target economic exposure
```

Multiplier policy remains frozen before any >1 result:

```text
leverage_multiplier = 1 + (candidate_cap - 1) × frozen_defensive_scale
final_scale = defensive_scale + (candidate_cap - 1) × defensive_scale²
candidate caps = 1.00 / 1.10 / 1.20 / 1.30
```

No PnL-selected threshold, funding signal, raw-HMM retune, P5 input, 0038 input, short/XRP target input, or production authorization is allowed.

## Pre-result study implementation candidate

Machine contract:

`research/leverage_0040/LEVERAGE-0040-STUDY-IMPLEMENTATION-V1.json`

Pure mechanics:

`research/leverage_0040/study_core.py`

One-time runner:

`research/leverage_0040/run_leverage_0040_once.py`

Immutable-result validator:

`research/leverage_0040/validate_leverage_0040_result.py`

The implementation was frozen before any >1 historical observation and pins:

- published BRRK/V1 daily target artifacts and their blob SHAs;
- mechanical defensive-scale recovery from frozen V1/BRRK gross;
- P3.3 5% L1 economic-drift semantics;
- 5/10/20/50 bps transaction-cost grid;
- BTC verified spot base + perp overlay; ETH/SOL/BNB perp; all-perp stress panel;
- native Hyperliquid funding common window and adverse debit spikes 1x/2x/3x/5x;
- explicit cross-margin liquidation accounting using the frozen margin snapshot;
- P2 point-in-time capacity artifact and exact artifact SHA-256;
- preregistered historical, gap, volatility and degraded-fill stresses;
- operating-budget candidates 35/40/45/50%;
- 10,000-resample paired stationary-block bootstrap at 7/21/63 day mean blocks;
- broad neighboring-cap requirement;
- deterministic selection order and no post-result retuning.

The contract workflow includes a real-data `--preflight-only` mode that validates the frozen baseline/data/cap1/capacity inputs and returns before any cap>1 target is evaluated.

## One-time execution safety

Run marker:

`research/leverage_0040/RUN_ONCE_LEVERAGE_0040.marker`

Required exact marker SHA-256:

`f54cdf362f60cad19d6c429ac4e008047b45d2cb537a95c96e2bc6dac5ce733a`

The marker is currently **ABSENT**. The run-once workflow is path-triggered only by creation/change of that marker on the v2 branch. Result commits do not retrigger the study; they trigger only immutable-result validation.

The marker must not be created until the pre-study draft PR has passed all applicable contract/preflight, Phase 0, P3.2 parity/golden, P4 cap=1, prerequisite, research and governance gates on its final pre-result head.

## Pre-study self-review checkpoint

Before documentation changes, compare `d49ffe2b4b9ef39ba9ed5a1e3dbef157b8cb793e` versus normalized main showed:

```text
ahead 7 / behind 0
exactly 8 intended pre-result study files
README_NONEXISTENT absent from diff
no RUN_ONCE marker
no research/results/leverage_0040 result directory
```

The v2 bookkeeping update changes only the study-branch field and the two push-workflow branch references; economic semantics remain unchanged.

## Explicit boundaries

Still forbidden:

- merge/revive the abandoned v1 branch;
- create the RUN_ONCE marker before pre-study CI closes;
- run/reuse `LEVERAGE-0039`;
- alter 0040 caps, budgets, stress definitions, multiplier policy or study implementation after seeing >1 results;
- search above 1.30 under 0040;
- weaken the frozen 20% defensive tail gate;
- promote EXPOSURE-SMOOTH-0038;
- absorb F23 funding-response logic;
- shorts / XRP targets;
- P5 exit intelligence;
- production gross >1 or production leverage authorization.

## Production authorization

```text
NO_CHANGE
production_authorized_components = []
```

## Project drift audit

```text
DRIFT_0
```

The old v1 tool-routing incident is an implementation-process exception, not strategy drift; its tree is excluded from the current candidate and must never be merged.

## Exact next action

```text
open draft pre-study PR from v2
-> run contract synthetic tests + real preflight-only gate
-> Phase 0 + P3.2 parity/golden + P4 cap=1 + P4 prereq + research + governance
-> same-PR fixes if preflight fails; still no cap>1 observation
-> final pre-result head all green
-> only then create exact RUN_ONCE marker once
-> one-time workflow executes full frozen LEVERAGE-0040 suite and commits immutable result
-> immutable-result validation
-> update decision registry / CURRENT_STATE / NEXT_STEPS from result without retuning
-> final-head CI + governance
-> expected-head merge
-> post-merge normalization
```
