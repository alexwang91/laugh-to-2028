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
- P4.3 cap=1 parity, liquidation model and pre-result multiplier policy: PASS / MERGED.
- post-#88 normalization PR #89: PASS / MERGED.

Normalized main:

`98396a5b510c5f0a717b954568921c1daef6edc8`

Current clean candidate:

`p4-4/leverage-0040-one-time-study-v2`

PR:

`#90 — P4.4 [DRAFT]: freeze and preflight LEVERAGE-0040 one-time study`

Old `p4-4/leverage-0040-one-time-study-v1` remains **INVALID / ABANDONED / DO NOT MERGE / DO NOT REVIVE**. Its transient empty-file write never entered a PR, main or result artifact.

## Current safety state

```text
RUN_ONCE marker                         ABSENT
research/results/leverage_0040 summary ABSENT
1.10/1.20/1.30 candidate observation   NONE
result selected                        NO
operating budget frozen                NO
production >1 authorization            NO
production_authorized_components       []
```

## Frozen architecture

```text
BRRK directional weights
× frozen defensive_scale in [0,1]
× leverage_multiplier
= final target economic exposure

leverage_multiplier = 1 + (candidate_cap - 1) × frozen_defensive_scale
candidate caps = 1.00 / 1.10 / 1.20 / 1.30
```

No PnL-selected threshold, funding signal, raw-HMM retune, P5 input, EXPOSURE-SMOOTH-0038 input, short/XRP target input, or production authorization may enter P4.

## P4.4 pre-result study candidate

Primary machine contract:

`research/leverage_0040/LEVERAGE-0040-STUDY-IMPLEMENTATION-V1.json`

Pure study mechanics:

`research/leverage_0040/study_core.py`

Initial execution library:

`research/leverage_0040/run_leverage_0040_once.py`

Corrected authoritative entrypoint after preflight review:

`research/leverage_0040/run_leverage_0040_once_r1.py`

Immutable result validator:

`research/leverage_0040/validate_leverage_0040_result.py`

The frozen study semantics include P3.3 5% economic L1 control, 5/10/20/50 bps costs, matched cap1 + frozen legacy comparators, BTC spot-base/perp-overlay routing, native Hyperliquid funding spikes, all-perp stress, standard cross-margin liquidation, pinned P2 capacity evidence, historical/gap/vol/degraded-fill stresses, 35/40/45/50% operating-budget candidates, 10,000 paired stationary-block bootstraps at 7/21/63-day mean blocks, broad neighboring-cap requirement and deterministic selection order.

## Preflight correction — before any cap>1 observation

The first PR #90 contract run failed in `--preflight-only` **before any 1.10/1.20/1.30 candidate construction**.

Root cause:

- published `daily_weights.csv` contains independently 5%-banded V1 and BRRK holdings;
- therefore `gross(BRRK banded) / gross(V1 banded)` is not the raw defensive scale and may exceed 1 when the two independent band states differ;
- the initial implementation incorrectly treated those published banded holdings as a scale source.

Same pre-result review also caught session timing: the first frozen BRRK return session `2022-12-10` must use the `2022-12-09` decision target.

Corrections frozen in the same PR, with no economic parameter change and no cap>1 observation:

```text
PREFLIGHT-RAW-TARGET-001
PREFLIGHT-SESSION-TIMING-002
```

R1 now rebuilds the raw authority from frozen source:

```text
feature universe: BTC / ETH / SOL / BNB / XRP
V1 raw target: build_benchmark_v1
frozen feature model: build_features_no_dominance
BRRK scale: build_brrk0011_scale
corrected tail risk: research/risk_metric_fix/corrected_risk.py
raw BRRK target = raw V1 target × rebuilt defensive scale
published banded holdings are legacy evidence only, never scale authority
```

Target/tradable assets remain BTC/ETH/SOL/BNB; XRP remains feature-only.

## Successful corrected checkpoint

Corrected checkpoint head:

`0b396de4d2bf10f06fee1403836331459b7bd696`

Applicable CI:

- P4.4 study contract/preflight `31186348512` (#7): **SUCCESS**
  - pre-result mechanics/authority: **24 passed**
  - runner/validator compile: SUCCESS
  - pinned ROUTER-DATA-0004 artifact/hash: SUCCESS
  - R1 real-data `--preflight-only`: **SUCCESS**
  - explicit output: `cap>1 not evaluated`
  - trade-price frame SHA-256: `a2b9a3909dc681b94cbed1d1dacef88c27de1f261f9531ed1bc2b39462a770d8`
  - route capacity CSV SHA-256: `5493fa0740b62f853396f45cc64fe2cc212492decc20b9f9e9d801e44cd72aa6`
- Phase 0 `31186348457` (#157): **SUCCESS, 281 passed + 5/5 integration**
- Research evidence `31186348431` (#63): **SUCCESS**
- P3.2 parity/golden `31186348474` (#50): **SUCCESS**
- P4 cap=1 parity `31186350411` (#16): **SUCCESS**
- P4 pre-run prerequisites `31186349388` (#12): **SUCCESS**
- governance `31186348416` (#219): **SUCCESS**

This is a checkpoint only. The handoff commits create a new final pre-result head and must receive the same applicable gates before the one-time marker may be created.

## One-time execution safety

Marker path:

`research/leverage_0040/RUN_ONCE_LEVERAGE_0040.marker`

Required SHA-256:

`f54cdf362f60cad19d6c429ac4e008047b45d2cb537a95c96e2bc6dac5ce733a`

The marker remains **ABSENT**. The dedicated run-once workflow is triggered only by that exact marker on the clean v2 branch. Result commits do not retrigger the study; they trigger only immutable-result validation.

## Explicit boundaries

Still forbidden:

- create the RUN_ONCE marker before final pre-result CI is green;
- merge/revive abandoned v1;
- reuse LEVERAGE-0039;
- alter 0040 caps, multiplier policy, budgets, stress rules or study implementation after seeing cap>1 results;
- search above 1.30 under 0040;
- weaken frozen 20% defensive tail gate;
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

The R1 change is a pre-result implementation correction discovered by fail-closed preflight, not parameter retuning or strategy drift.

## Exact next action

```text
final pre-result head revalidation for #90
-> update PR evidence / ready only after all applicable gates green
-> create exact RUN_ONCE marker once
-> dedicated workflow executes frozen 0040 suite exactly once and commits immutable result
-> immutable-result validation
-> record P4.5 select/fail decision without retuning
-> final-head CI/governance
-> expected-head merge
-> post-merge normalization
```
