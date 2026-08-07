# BRRK Current State

Last updated: 2026-08-07
Status: **authoritative current-state handoff**

> GitHub `main` is the canonical live ref. P4.4 has been explicitly resumed by the owner for **pre-result validation only**. This does not authorize the one-time LEVERAGE-0040 run, any cap>1 result observation, merge, or production deployment.

## Executive state

```text
Phase 0                         COMPLETE / MERGED
Phase 1                         COMPLETE / MERGED
Phase 2                         COMPLETE / MERGED
Phase 3                         COMPLETE / MERGED
P4.1 defensive scaler          COMPLETE / MERGED / frozen [0,1]
P4 architecture + cap1         COMPLETE / MERGED
P4 margin/liquidation prereqs  COMPLETE / MERGED
Repository hygiene             COMPLETE / MERGED (#91/#92 normalization)
LEVERAGE-0040 implementation   PRE-RESULT CANDIDATE / VALIDATION RESUMED
LEVERAGE-0040 search           NOT RUN
P4.5 select/fail decision      BLOCKED
P4.6 production leverage gate  BLOCKED / separate authorization
P5 exit intelligence           BLOCKED / not started
production authorization       NONE
```

`production_authorized_components = []`

## Current owner instruction

**Resume P4.4 pre-result validation only.**

PR #90 must remain **DRAFT** while refreshed final-head gates are being closed.

Until all refreshed pre-result gates are green and a final-head self-review is complete:

- do not create or modify `research/leverage_0040/RUN_ONCE_LEVERAGE_0040.marker`;
- do not execute the full LEVERAGE-0040 study;
- do not inspect 1.10 / 1.20 / 1.30 economic results;
- do not mark PR #90 ready;
- do not merge PR #90;
- do not change frozen economic semantics;
- do not authorize production gross >1.

## Live candidate and refresh state

Repository:

`alexwang91/laugh-to-2028`

Research PR / branch:

- PR #90;
- `p4-4/leverage-0040-one-time-study-v2`.

Canonical main used for this resume refresh:

`3690f64a6179a759a60d9759c214d59cf604869e`

Refresh integration checkpoint:

`ee49ea6028b5c4426d03af81657663b7ede9d987`

That refresh incorporates current `main` while preserving the pre-result P4.4 implementation. The only overlap with repository-normalization work was `docs/CURRENT_STATE.md` and `docs/NEXT_STEPS.md`; current authority was retained and is now updated to reflect the explicit resume instruction. No frozen research/economic parameter was changed by the refresh.

The branch head may move as governance-only corrections are committed; always re-read GitHub live state before any further mutation.

## Current safety state

```text
RUN_ONCE marker                         ABSENT
research/results/leverage_0040 summary ABSENT
1.10 / 1.20 / 1.30 result observation NONE
selected research cap                  NONE
operating drawdown budget              NONE
production gross >1 authorization      NONE
```

`production_authorized_components = []`

The first refreshed governance run exposed a documentation-state defect: the refresh initially retained `CURRENT_STATE.md` byte-for-byte from `main`, so the forward-PR governance contract correctly rejected the PR because the current-state authority was not updated in the PR diff. This is a governance/documentation correction only; it is not a research result and changes no economics.

## P4.4 one-time lifecycle

LEVERAGE-0040 remains a one-time experiment.

### Before an immutable result exists

Only the corrected R1 authority may run in:

`--preflight-only`

The preflight must exit before any cap>1 candidate evaluation. It must explicitly preserve:

`cap>1 not evaluated`

### After an immutable result exists

The workflow may only validate the immutable result, digest, and provenance. It must not rerun the study under the same experiment ID.

## Frozen architecture and product constraints

### Directional strategy

- canonical directional research target: **BRRK-0011**;
- target/tradable assets: **BTC / ETH / SOL / BNB**;
- XRP is **feature-only** where required by the frozen BRRK regime feature model;
- XRP is not a target, position, or routing asset;
- strategy cadence: daily;
- canonical decision boundary: 00:00 UTC.

### Execution / safety

- primary venue: Hyperliquid;
- FLAT = zero directional exposure;
- FLAT -> LONG / SHORT requires human approval;
- intraday automation may reduce risk but may not autonomously add directional exposure;
- bot credentials are trading Agent/API credentials only;
- master wallet private key, automated withdrawals, and automated external transfers are outside the approved boundary;
- MERGED / CI VERIFIED does not imply PRODUCTION AUTHORIZED.

### Leverage boundary

P4.1 corrected defensive scale remains strictly `[0,1]`.

Frozen post-defensive multiplier:

```text
leverage_multiplier = 1 + (candidate_cap - 1) * defensive_scale
candidate caps = 1.00 / 1.10 / 1.20 / 1.30
```

The multiplier must remain defensive-monotone. P4.4 may not alter BRRK-0011, the defensive selector, stress definitions, benchmarks, selection gates, seed, HMM logic, scenario definitions, liquidation semantics, or the preregistered candidate set to make validation pass.

Production gross cap remains `1.0` unless and until P4.6 separately authorizes otherwise.

`70% drawdown` remains catastrophic tolerance, not an operating drawdown budget. No operating drawdown budget is currently frozen.

## Completed foundations

### Phase 1

Execution safety is merged, including deterministic order identity, persistent ledger, partial-fill truth, reversal safety, reduce-only semantics, precision/metadata handling, post-submit reconciliation, restart recovery, kill/emergency paths, verified emergency FLAT, and disable-new-risk behavior.

### Phase 2

Instrument/routing work is merged, including the canonical Hyperliquid instrument registry, BTC/ETH/SOL identity validation, BNB `PERP_ONLY_DEFAULT`, route cost modeling, corrected live-L2 measurement, route decisions/logging, cost attribution, and capacity evidence.

Live depth remains point-in-time execution-capacity evidence, not historical PIT liquidity for every backtest date.

### Phase 3

Phase 3 is COMPLETE / MERGED. Target assets are BTC/ETH/SOL/BNB; XRP remains feature-only in the five-series strategy signal panel. Research/live canonical data parity, canonical target generation, committed historical golden vectors, 5% L1 rebalance semantics, and contribution handling are merged.

## Historical truth that must remain unchanged

### PR #73

```text
MERGED = YES
CI VERIFIED = NO / NOT RECORDED
```

Do not retroactively infer a final-head green governance run.

### EXPOSURE-SMOOTH-0038

`SHADOW_ONLY / NOT PROMOTED`

It is not the P3.2 canonical target and is not leverage authorization.

### LEVERAGE-0039

```text
STOPPED PRE-RUN
NO RESULT
DO NOT REUSE EXPERIMENT ID
```

### P4.4 preflight corrections

`PREFLIGHT-RAW-TARGET-001`: independently banded V1 and BRRK holdings cannot be divided to reconstruct raw defensive scale. Correct R1 authority rebuilds raw V1 plus frozen BRRK-0011 raw defensive scale from the frozen source.

`PREFLIGHT-SESSION-TIMING-002`: frozen decision `2022-12-09` maps to first evaluated return session `2022-12-10`.

Both corrections occurred before any cap>1 observation and were not result-driven retuning.

## Documentation authority

Read current state in this order:

1. root `README.md`;
2. `docs/CURRENT_STATE.md`;
3. `docs/NEXT_STEPS.md`;
4. `docs/MASTER_PLAN_2026-08-05.md`;
5. `docs/IMPLEMENTATION_ROADMAP_2026-08-05.md`;
6. `config/decision_registry.json`;
7. `docs/README.md` for evidence/document navigation.

Dated historical documents remain evidence snapshots and do not override current authority.

## Project drift audit

```text
DRIFT_0
```

The resume refresh and this governance correction change repository ancestry/current-state documentation only. Frozen strategy math, candidate caps, multiplier policy, risk/stress gates, and production authorization are unchanged.

## Exact next action

```text
COMPLETE REFRESHED FINAL-HEAD PRE-RESULT VALIDATION
KEEP PR #90 DRAFT
DO NOT CREATE RUN_ONCE
DO NOT EXECUTE 1.10 / 1.20 / 1.30
DO NOT MERGE
```

Required refreshed gates on the new final head:

1. Phase 0 baseline contract;
2. Research evidence normalization;
3. P3.2 research/live parity and committed golden validation;
4. P4 cap=1 exact parity;
5. P4 pre-run prerequisites;
6. P4.4 study contract plus corrected R1 real-data `--preflight-only`;
7. PR handoff governance.

After all applicable gates are green, perform a final-head diff/drift audit and re-confirm marker/result absence plus `production_authorized_components = []`.

Only then may the one-time RUN_ONCE boundary be **reconsidered**. It must not be crossed automatically by this resume instruction.
