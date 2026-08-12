# BRRK-BETA-BTC-CONTINUATION-PARAMETER-GEOMETRY-0058

Status: **CONTROLLED EXECUTION BOUNDARY FROZEN ON BRANCH / ZERO RESULT / NOT RUN**

This directory is the formal preregistration owner path for a DEVELOPMENT parameter-geometry study of a causal Beta-versus-BTC continuation mechanism.

Frozen before any 0058 economic output:

- immutable exposed daily BTC/ETH/SOL source through 2026-08-02;
- one 108-cell lattice: `L=20..240 by 20`, `kappa=0..2.0 by 0.25`;
- common 1,942-period evaluation window from 2021-04-08 through 2026-08-01;
- 5/10/20 bps executed-L1 costs;
- static BTC, static drifting 50/50 ETH/SOL Beta, and static 50% BTC + 25% ETH + 25% SOL benchmarks;
- central-difference gradient and symmetric Hessian spectral-norm geometry;
- `ln(1.05)` gradient and `ln(1.10)` curvature thresholds;
- 4-neighbor plateau support >=9 cells spanning >=3 L and >=3 kappa levels;
- cost-coherent plateau intersection across 5/10/20 bps;
- largest-support component then geometric medoid selection; historical argmax is descriptive only;
- selected representative 5 bps uplift >5% versus best static, strict stress dominance at 10/20 bps;
- four chronological blocks 486/486/485/485 requiring >=3 positive;
- moving-block bootstrap length 60, 10,000 reps, seed 1844716895, simultaneous one-sided 95% LCBs;
- complete lossless surface plus selected/benchmark daily NAV and drawdown paths persisted by the unique execution.

No 0058 parameter surface or portfolio economics has been run. Implementation-only is the next legal stage after this preregistration merges.

Canonical BRRK, Phase 6, production authorization, signing and order submission are unchanged.

## Implementation-only handoff

Preregistration merged at `e6d94b30c8bb4d126d6c234c30980d701a9ababc`. This stage adds a data-agnostic `engine.py` plus synthetic contract tests only. The engine accepts caller-supplied BTC/ETH/SOL DataFrames and contains no market loader, filesystem payload reader, network request or controlled-run entrypoint.

Synthetic Actions run `31640495960` passes 17 contract tests, including a complete 2,183-row frozen-calendar flat-price surface with 324 cell-cost summaries, 210 interior geometry rows and 1,942 selected-path rows. Synthetic output has zero scientific authority. Real 0058 market payload loading and historical parameter-surface economics remain forbidden.

Next legal stage after implementation merge is a separate controlled-execution boundary.

## Controlled-execution boundary handoff

Implementation merged at `e2a0f2fd564274e53d099811d54bcdb06d77fb07`. The controlled boundary freezes `RUN_INTERFACE.json`, `RESULT_SCHEMA.json`, staged `run_once.py`, `test_run_interface.py` and `CONTROLLED_EXECUTION_BOUNDARY.json`. No historical result or runtime marker exists.

The state machine is `preflight -> durable RUN_ATTEMPT.marker -> exactly one real 108-cell evaluation -> durable PRIMARY_RESULT.json + EXECUTION.json -> marker-only RUN_ONCE.marker`. Once the attempt marker is durable, same-ID recomputation, retuning and rescue are forbidden. Marker-only recovery is allowed only when attempt/result/execution already exist and verify while the final marker alone is missing.

The result schema requires all 324 candidate/cost surface rows and all 210 interior geometry rows, verifies central-difference gradient/Hessian values directly against persisted terminal wealth, enforces the frozen plateau/representative/path schema and preserves historical argmax as descriptive-only.

Synthetic/fault Actions run `31643240307` passed 17 immutable implementation contracts plus 13 controlled-run/schema contracts, governance validation, no-drift and the final zero-result guard. `REAL_0058_HISTORICAL_PAYLOAD_NOT_LOADED=true`, `REAL_0058_PARAMETER_SURFACE_ECONOMICS_NOT_EXECUTED=true`, `ACTUAL_HISTORICAL_VARIANTS_EVALUATED=0`.

After this boundary merges through standing governance, 0058 becomes technically eligible for its unique staged DEVELOPMENT historical execution. That execution is a separate irreversible action and is not part of this boundary.
