# Next Steps

> Read canonical sources in repository-defined order. GitHub actual state wins over stale prose.

## Current dependency

```text
Revalidate the corrected R1 pre-result LEVERAGE-0040 study head before the one-time RUN marker may be created.
```

Normalized main after PR #89:

`98396a5b510c5f0a717b954568921c1daef6edc8`

Current draft PR:

`#90 — p4-4/leverage-0040-one-time-study-v2`

Old v1 branch is **INVALID / ABANDONED / DO NOT MERGE / DO NOT REVIVE**.

## Frozen authority

```text
P4.1 defensive scaler       frozen 0 .. 1
LEVERAGE-0039              STOPPED_PRE_RUN / NO RESULT / DO NOT REUSE
LEVERAGE-0040              PREREGISTERED / MERGED / NOT RUN
cap=1 wiring/parity        PASS / MERGED
liquidation model          PASS / MERGED
>1 multiplier policy       FROZEN PRE-RESULT / MERGED
production gross cap       1.0 unchanged
production authorization   none
```

`production_authorized_components = []` remains unchanged.

## Corrected pre-result study implementation

Authority:

- `research/leverage_0040/LEVERAGE-0040-STUDY-IMPLEMENTATION-V1.json`
- `research/leverage_0040/study_core.py`
- `research/leverage_0040/run_leverage_0040_once.py` — execution library
- `research/leverage_0040/run_leverage_0040_once_r1.py` — authoritative corrected entrypoint
- `research/leverage_0040/validate_leverage_0040_result.py`

Initial preflight failed before cap>1 construction because the implementation tried to infer defensive scale from independently banded published V1/BRRK holdings. That is invalid. R1 now rebuilds raw V1 + BRRK scale from the frozen five-asset feature authority while targets remain four assets.

R1 also fixes the return-session boundary:

```text
first frozen BRRK decision: 2022-12-09
first evaluation session:   2022-12-10
```

Both changes are implementation corrections before any >1 observation; no cap/budget/stress/multiplier parameter changed.

## Corrected checkpoint evidence

Head:

`0b396de4d2bf10f06fee1403836331459b7bd696`

- P4.4 contract/preflight #7 / `31186348512`: **SUCCESS**, 24 pre-result tests, compile PASS, route artifact digest PASS, R1 real-data preflight PASS with `cap>1 not evaluated`;
- Phase 0 #157 / `31186348457`: **SUCCESS, 281 passed + 5/5 integration**;
- Research evidence #63 / `31186348431`: SUCCESS;
- P3.2 parity/golden #50 / `31186348474`: SUCCESS;
- P4 cap=1 #16 / `31186350411`: SUCCESS;
- P4 prerequisite #12 / `31186349388`: SUCCESS;
- governance #219 / `31186348416`: SUCCESS.

The current handoff commits produce a new head, so these runs are checkpoint evidence only. Final pre-result validation must repeat on the latest head.

## One-time marker remains blocked

Marker:

`research/leverage_0040/RUN_ONCE_LEVERAGE_0040.marker`

Expected SHA-256:

`f54cdf362f60cad19d6c429ac4e008047b45d2cb537a95c96e2bc6dac5ce733a`

Current state:

```text
RUN_ONCE MARKER:                ABSENT
LEVERAGE-0040 SEARCH RUN:       NO
1.10/1.20/1.30 RESULT:          NONE
RESULT SELECTED:                NO
OPERATING BUDGET FROZEN:        NO
PRODUCTION >1 RUNTIME:          NO
PRODUCTION AUTHORIZED:          NO_CHANGE
```

The marker may be created exactly once only after the latest pre-result head is fully green. The marker-triggered workflow then executes the already-frozen suite and commits immutable results. Result commits trigger only validation, not a second study run.

## Study semantics remain frozen

```text
caps                        1.00 / 1.10 / 1.20 / 1.30
multiplier                  1 + (cap-1) × defensive_scale
P3.3 economic L1 band       0.05
cost grid                   5 / 10 / 20 / 50 bps
operating MDD candidates    35% / 40% / 45% / 50%
catastrophe boundary        70%
bootstrap                   10,000 paired samples; 7/21/63 mean block days
```

Mandatory comparators/stresses, funding, routing, capacity, liquidation and broad-region rules remain exactly as preregistered/frozen. No post-result retuning is permitted.

## Project drift audit

```text
DRIFT_0
```

## Exact next action

```text
wait for latest #90 pre-result CI
-> same-PR fix only if a pre-result implementation defect appears
-> final pre-result head all green
-> update PR metadata / ready
-> create exact RUN_ONCE marker once
-> one-time immutable LEVERAGE-0040 study
-> validate committed result
-> make P4.5 select/fail decision without retuning
-> P4.6 remains separate production authorization gate
```
