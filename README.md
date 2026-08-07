# laugh-to-2028

一个面向长期生存、可审计研究和自动执行的加密资产系统项目。

**回测结果、研究结论、代码合并与生产授权是不同层级。这个仓库不构成收益承诺或投资建议。**

---

## 当前状态 — 2026-08-07

| 模块 | 状态 |
| --- | --- |
| Phase 0 — canonical config / governance | **COMPLETE / MERGED** |
| Phase 1 — execution truth & safety | **COMPLETE / MERGED** |
| Phase 2 — instrument / routing / cost evidence | **COMPLETE / MERGED** |
| Phase 3 — data → target → rebalance → contribution | **COMPLETE / MERGED** |
| P4.1 — defensive scaler `[0,1]` | **COMPLETE / MERGED** |
| P4.2 / P4.3 — leverage architecture / cap=1 parity / margin prerequisites | **COMPLETE / MERGED** |
| P4.4 — `LEVERAGE-0040` one-time study | **COMPLETE / IMMUTABLE RESULT** |
| P4.5 — leverage selection | **FAIL_STOP / NO_PROMOTION / MERGED** |
| `LEVERAGE-0041` — leverage architecture / sweet spot | **PREREGISTERED / NOT RUN** |
| P4.6 — production leverage authorization | **BLOCKED** |
| Phase 5 — exit intelligence | **NOT STARTED** |
| Production-authorized components | **none** |

`production_authorized_components = []`

Canonical merged base after PR #90:

`14dd9f2fb828d860b8552816814982dc4bd89b10`

Current production gross cap remains **1.0**.

### LEVERAGE-0040 immutable evidence

- immutable result commit: `bd256e77a9800556e97769858fbb3ba5054c4389`
- immutable summary SHA256: `3bb4dc46c61a5e9c7e049862575a89b2771830410ce4bc2bb25c83e469f52fc0`
- selection: `NO_PROMOTION`
- selected research cap: `null`
- selected operating drawdown budget: `null`
- production leverage authorization: **none**

At 5 bps execution cost:

| Gross cap | CAGR | Max drawdown | Sharpe | Frozen final gate |
| --- | ---: | ---: | ---: | --- |
| 1.00 | 65.31% | -33.53% | 1.3561 | comparator |
| 1.10 | 71.92% | -36.67% | 1.3548 | **FAIL** |
| 1.20 | 78.51% | -39.63% | 1.3550 | **FAIL** |
| 1.30 | 85.68% | -42.58% | 1.3618 | **FAIL** |

`LEVERAGE-0040` is closed. Do not retune, rescue, rerun or reuse its experiment ID.

---

## LEVERAGE-0041 — new preregistered sweet-spot study

The next experiment tests whether a different implementation architecture can safely realize the attractive leverage economics without relaxing the predecessor hard gates.

Frozen requested-cap grid:

```text
1.00 / 1.05 / 1.10 / 1.15 / 1.20 / 1.25 / 1.30
```

`1.20` is a focal design point only. It is not preselected.

Architecture:

`SPOT_FIRST_BASE_PLUS_PERP_OVERLAY_V1`

Core rules:

- 25% NAV explicit modeled cash collateral reserve;
- <=75% NAV spot financing;
- BTC / ETH / SOL base longs spot-first when verified P2.4 evidence permits;
- BNB remains perp-only;
- residual base exposure and all incremental leverage above cap=1 use perp;
- trailing 168h funding logic may only reduce the incremental overlay;
- liquidation distance must remain **>55%** for every promotable state;
- sweet spot must sit inside a contiguous all-pass region of at least three caps and have passing immediate lower/higher neighbors;
- objective is highest matched after-cost CAGR among all hard-gate PASS candidates, with lower cap preferred when CAGR is within 1.0 percentage point.

Preregistration is not RUN_ONCE authorization and is not production authorization.

---

## Frozen product / strategy boundaries

Unless a later approved decision explicitly changes them:

- canonical directional research target: **BRRK-0011**;
- target/tradable assets: **BTC / ETH / SOL / BNB**;
- XRP: **feature-only** where required by the frozen regime model;
- primary venue: **Hyperliquid**;
- cadence: **daily**, canonical boundary **00:00 UTC**;
- FLAT = zero directional exposure;
- FLAT → LONG / SHORT requires human approval;
- intraday automation may reduce risk but may not autonomously add directional exposure;
- bot uses trading Agent/API credentials only; master-wallet key and automated withdrawals/transfers remain outside scope;
- P4.1 defensive scaler remains `[0,1]`;
- production gross cap remains **1.0**;
- `production_authorized_components = []`.

---

## Source-of-truth reading order

1. [`README.md`](README.md)
2. [`docs/CURRENT_STATE.md`](docs/CURRENT_STATE.md)
3. [`docs/NEXT_STEPS.md`](docs/NEXT_STEPS.md)
4. [`docs/MASTER_PLAN_2026-08-05.md`](docs/MASTER_PLAN_2026-08-05.md)
5. [`docs/IMPLEMENTATION_ROADMAP_2026-08-05.md`](docs/IMPLEMENTATION_ROADMAP_2026-08-05.md)
6. [`config/decision_registry.json`](config/decision_registry.json)
7. [`docs/README.md`](docs/README.md)

LEVERAGE-0040 immutable evidence remains under `research/results/leverage_0040/`. LEVERAGE-0041 preregistration is under `research/leverage_0041/LEVERAGE-0041.json` and `docs/LEVERAGE_0041_PREREGISTRATION_2026-08-07.md`.
