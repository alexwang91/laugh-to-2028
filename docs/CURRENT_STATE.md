# BRRK Current State

Last updated: 2026-08-07
Status: authoritative cross-chat handoff snapshot

## Authoritative baseline

- P0/P1/P2: PASS / MERGED; Phases 0–2 complete.
- P3.1–P3.4: PASS / TESTED / CI VERIFIED / MERGED; **Phase 3 COMPLETE**.
- P4.1 corrected defensive scaler: PASS / MERGED; frozen strictly to `[0,1]`.
- `LEVERAGE-0039`: **STOPPED_PRE_RUN / NO_RESULT_EVER_PRODUCED / DO NOT REUSE**.
- `LEVERAGE-0040`: **PREREGISTERED / MERGED / NOT RUN**.
- Hyperliquid margin snapshot, cap=1 parity, liquidation model and pre-result multiplier policy: PASS / MERGED.
- post-#88 normalization PR #89: PASS / MERGED.

Normalized main:

`98396a5b510c5f0a717b954568921c1daef6edc8`

Current clean candidate:

`p4-4/leverage-0040-one-time-study-v2`

PR #90 is the only active P4.4 candidate. Old v1 is **INVALID / ABANDONED / DO NOT MERGE / DO NOT REVIVE** and has no PR/result authority.

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

## Frozen architecture and study semantics

```text
BRRK directional weights
× frozen defensive_scale in [0,1]
× leverage_multiplier
= final target economic exposure

leverage_multiplier = 1 + (candidate_cap - 1) × frozen_defensive_scale
candidate caps = 1.00 / 1.10 / 1.20 / 1.30
```

The one-time study implementation is frozen in:

- `research/leverage_0040/LEVERAGE-0040-STUDY-IMPLEMENTATION-V1.json`
- `research/leverage_0040/study_core.py`
- `research/leverage_0040/run_leverage_0040_once.py` — execution library
- `research/leverage_0040/run_leverage_0040_once_r1.py` — authoritative corrected entrypoint
- `research/leverage_0040/validate_leverage_0040_result.py`

It preserves the preregistered cap grid, P3.3 5% economic L1 control, 5/10/20/50 bps costs, matched cap1 + frozen legacy comparators, BTC spot-base/perp-overlay routing, Hyperliquid funding spikes, standard cross-margin liquidation, pinned P2 capacity evidence, historical/gap/vol/degraded-fill stresses, 35/40/45/50% operating-budget candidates, 10,000 paired stationary-block bootstraps at 7/21/63-day mean blocks, broad neighboring-cap requirement and deterministic selection order.

## Pre-result corrections

Initial #90 `--preflight-only` correctly failed before any cap>1 construction because independently banded published V1/BRRK holdings cannot be divided to recover raw defensive scale. Same source review caught the one-day decision/session boundary.

Corrections, both before any >1 observation and with no economic parameter change:

```text
PREFLIGHT-RAW-TARGET-001
PREFLIGHT-SESSION-TIMING-002
```

R1 now uses frozen raw authority:

```text
feature universe: BTC / ETH / SOL / BNB / XRP
V1 raw target: build_benchmark_v1
features: build_features_no_dominance
BRRK scale: build_brrk0011_scale
raw BRRK target = raw V1 target × defensive scale
first decision: 2022-12-09
first evaluation session: 2022-12-10
```

XRP remains feature-only; tradable/target assets remain BTC/ETH/SOL/BNB. Published banded `daily_weights.csv` is legacy evidence only, never scale authority.

## Validated pre-result evidence

Corrected checkpoint `0b396de4d2bf10f06fee1403836331459b7bd696` passed all applicable gates, including Phase 0 **281 passed + 5/5 integration** and R1 preflight explicitly reporting `cap>1 not evaluated`.

Subsequent handoff head `0db6544af1793f48c30f9eb0b3cb98629bee58ba` also passed all seven applicable gates:

- P4.4 study contract/preflight `31186802141` (#10): **SUCCESS**;
- Phase 0 `31186802190` (#160): **SUCCESS**;
- Research evidence `31186802012` (#66): **SUCCESS**;
- P3.2 parity/golden `31186802121` (#53): **SUCCESS**;
- P4 cap=1 parity `31186802544` (#19): **SUCCESS**;
- P4 pre-run prerequisites `31186802021` (#15): **SUCCESS**;
- governance `31186802044` (#222): **SUCCESS**.

## Final pre-result CI lifecycle hardening

Before creating the one-time marker, one additional non-economic lifecycle issue was frozen:

- **pre-result state (`summary.json` absent):** the P4.4 contract workflow downloads the pinned P2 capacity artifact and runs R1 `--preflight-only`;
- **post-result state (`summary.json` present):** the same workflow runs only `validate_leverage_0040_result.py` against committed immutable evidence and does **not** redownload the capacity artifact or rerun the historical study.

This prevents later result/handoff/decision-registry commits from accidentally requiring a second LEVERAGE-0040 execution. The workflow path filter now includes `research/results/leverage_0040/**` and `config/decision_registry.json`, and a regression test locks both lifecycle branches.

This lifecycle hardening changes no cap, signal, cost, stress, budget, multiplier, benchmark or selection rule. Because it creates a new branch head, it must receive one final pre-result CI pass before the marker is created.

## One-time execution safety

Marker:

`research/leverage_0040/RUN_ONCE_LEVERAGE_0040.marker`

Required SHA-256:

`f54cdf362f60cad19d6c429ac4e008047b45d2cb537a95c96e2bc6dac5ce733a`

The marker remains **ABSENT**. Only its exact creation on the validated v2 branch may trigger the one-time workflow. Result commits trigger validation only.

## Explicit boundaries

Still forbidden:

- create the RUN_ONCE marker before the latest pre-result head is fully green and metadata/ready governance is green;
- rerun the study after immutable results exist;
- merge/revive abandoned v1;
- reuse LEVERAGE-0039;
- alter 0040 caps, multiplier policy, budgets, stress rules or study semantics after seeing cap>1 results;
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

R1 and CI-lifecycle fixes are fail-closed pre-result implementation corrections, not strategy retuning.

## Exact next action

```text
revalidate the latest pre-result #90 head after CI-lifecycle hardening
-> update PR evidence / mark ready
-> newest metadata/ready governance
-> create exact RUN_ONCE marker once
-> one-time workflow executes frozen 0040 suite and commits immutable result
-> immutable-result validation
-> record P4.5 select/fail decision without retuning
-> final-head CI/governance
-> expected-head merge
-> post-merge normalization
```
