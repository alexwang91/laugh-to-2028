# laugh-to-2028

一个面向长期生存、可审计研究和自动执行的加密资产系统项目。

**回测结果、研究结论、代码合并与生产授权是不同层级。这个仓库不构成收益承诺或投资建议。**

## 当前状态 — 2026-08-07

| 模块 | 状态 |
| --- | --- |
| Phase 0–3 | **COMPLETE / MERGED** |
| P4.1 defensive scaler `[0,1]` | **COMPLETE / MERGED** |
| P4.2 / P4.3 architecture, parity, margin prerequisites | **COMPLETE / MERGED** |
| LEVERAGE-0040 | **COMPLETE / IMMUTABLE / NO_PROMOTION** |
| P4.5 closeout | **COMPLETE / MERGED** |
| LEVERAGE-0041 preregistration | **COMPLETE / MERGED** |
| LEVERAGE-0041 implementation | **PRE-RESULT / IN PROGRESS** |
| LEVERAGE-0041 research RUN_ONCE | **OWNER AUTHORIZED / PENDING GREEN PRE-RUN GATES** |
| P4.6 production leverage | **BLOCKED / SEPARATE AUTHORIZATION** |
| Production-authorized components | **none** |

`production_authorized_components = []`

Current production gross cap = **1.0**.

Implementation base main:

`baaa5776892411990734ef2121cf54a5dbbab047`

### LEVERAGE-0040 immutable evidence

- immutable result commit: `bd256e77a9800556e97769858fbb3ba5054c4389`
- summary SHA256: `3bb4dc46c61a5e9c7e049862575a89b2771830410ce4bc2bb25c83e469f52fc0`
- selection: `NO_PROMOTION`

Do not rerun or retune LEVERAGE-0040.

### LEVERAGE-0041

Frozen grid:

`1.00 / 1.05 / 1.10 / 1.15 / 1.20 / 1.25 / 1.30`

`1.20` is a focal design point only.

Architecture: `SPOT_FIRST_BASE_PLUS_PERP_OVERLAY_V1`

- requested target = frozen raw BRRK-0011 target × cap;
- 25% explicit cash/cross-margin reserve;
- <=75% NAV spot financing;
- BTC/ETH/SOL base longs spot-first under pinned route evidence;
- BNB perp-only;
- residual base + incremental exposure perp;
- funding reducer only decreases incremental overlay;
- modeled liquidation distance must be >55%;
- selected sweet spot must be interior to a contiguous >=3-cap all-PASS region.

The owner has authorized implementation, pre-run validation and the one-time LEVERAGE-0041 research run as one continuous research workflow. The RUN_ONCE marker is retained to enforce one execution and auditability, not to request permission again.

**This is not production authorization. P4.6 remains separate, and production gross remains 1.0.**

## Frozen product boundaries

- BRRK-0011 directional core;
- BTC / ETH / SOL / BNB targets; XRP feature-only;
- Hyperliquid primary venue;
- daily 00:00 UTC;
- FLAT = zero directional exposure;
- P4.1 defensive scale `[0,1]`;
- no autonomous production leverage expansion.

## Source-of-truth order

1. `README.md`
2. `docs/CURRENT_STATE.md`
3. `docs/NEXT_STEPS.md`
4. `docs/MASTER_PLAN_2026-08-05.md`
5. `docs/IMPLEMENTATION_ROADMAP_2026-08-05.md`
6. `config/decision_registry.json`

LEVERAGE-0040 immutable evidence is under `research/results/leverage_0040/`. LEVERAGE-0041 preregistration and implementation evidence are under `research/leverage_0041/`.
