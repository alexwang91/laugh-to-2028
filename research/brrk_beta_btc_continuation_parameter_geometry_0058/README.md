# BRRK-BETA-BTC-CONTINUATION-PARAMETER-GEOMETRY-0058

Status: **IMPLEMENTATION FROZEN ON BRANCH / SYNTHETIC CONTRACT TESTS ONLY / NOT RUN**

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
