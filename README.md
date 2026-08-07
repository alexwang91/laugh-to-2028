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
| P4.5 — leverage selection | **FAIL_STOP / NO_PROMOTION** |
| P4.6 — production leverage authorization | **BLOCKED / NO ELIGIBLE CANDIDATE** |
| Phase 5 — exit intelligence | **NOT STARTED** |
| Production-authorized components | **none** |

`production_authorized_components = []`

Active research/evidence PR:

- PR #90 — `P4.4 [DRAFT / RESULT: NO_PROMOTION]: immutable LEVERAGE-0040 study`
- branch: `p4-4/leverage-0040-one-time-study-v2`
- immutable result commit: `bd256e77a9800556e97769858fbb3ba5054c4389`
- immutable summary SHA256: `3bb4dc46c61a5e9c7e049862575a89b2771830410ce4bc2bb25c83e469f52fc0`
- selection: `NO_PROMOTION`
- selected research cap: `null`
- selected operating drawdown budget: `null`
- production leverage authorization: **none**

### LEVERAGE-0040 headline evidence

At 5 bps execution cost:

| Gross cap | CAGR | Max drawdown | Sharpe | Calmar | Frozen final gate |
| --- | ---: | ---: | ---: | ---: | --- |
| 1.00 | 65.31% | -33.53% | 1.3561 | 1.9477 | comparator |
| 1.10 | 71.92% | -36.67% | 1.3548 | 1.9616 | **FAIL** |
| 1.20 | 78.51% | -39.63% | 1.3550 | 1.9809 | **FAIL** |
| 1.30 | 85.68% | -42.58% | 1.3618 | 2.0122 | **FAIL** |

The study therefore does **not** authorize or select 1.10 / 1.20 / 1.30. The higher caps improved historical CAGR but did not satisfy all preregistered hard risk/implementation gates.

`LEVERAGE-0040` is closed. Do not retune its thresholds, implementation semantics or candidate set after observing the result, and do not reuse the experiment ID for a rescue study.

---

## Frozen product / strategy boundaries

Unless a later approved decision explicitly changes them:

- canonical directional research target: **BRRK-0011**;
- target/tradable assets: **BTC / ETH / SOL / BNB**;
- XRP: **feature-only** where required by the frozen regime model; never a target/routing asset;
- primary venue: **Hyperliquid**;
- cadence: **daily**, canonical boundary **00:00 UTC**;
- FLAT = zero directional exposure;
- FLAT → LONG / SHORT requires human approval;
- intraday automation may reduce risk but may not autonomously add directional exposure;
- bot uses trading Agent/API credentials only; master-wallet key and automated withdrawals/transfers remain outside scope;
- current production gross cap remains **1.0**;
- `production_authorized_components = []`.

---

## What the leverage result means

P4.5 follows the preregistered rule: leverage is not chosen from the highest in-sample CAGR alone. A candidate must survive the full robustness/risk suite.

For 1.10 and 1.20, the main vetoes were native Hyperliquid funding stress, liquidation-distance and synthetic-gap gates. 1.30 additionally failed the historical proxy catastrophe gate.

This does **not** establish that 1.20 is economically unattractive. It establishes that the specific `LEVERAGE-0040` implementation architecture did not earn promotion under its frozen gates.

A separate future study may investigate a better leverage implementation architecture and search for the highest **safely sustainable** gross exposure. The currently accepted planning direction treats **1.20 as an important focal design point**, not as a selected cap or production authorization. Any such study must receive a new experiment ID and be preregistered before results are observed.

---

## Source-of-truth reading order

1. [`README.md`](README.md)
2. [`docs/CURRENT_STATE.md`](docs/CURRENT_STATE.md)
3. [`docs/NEXT_STEPS.md`](docs/NEXT_STEPS.md)
4. [`docs/MASTER_PLAN_2026-08-05.md`](docs/MASTER_PLAN_2026-08-05.md)
5. [`docs/IMPLEMENTATION_ROADMAP_2026-08-05.md`](docs/IMPLEMENTATION_ROADMAP_2026-08-05.md)
6. [`config/decision_registry.json`](config/decision_registry.json)
7. [`docs/README.md`](docs/README.md)

Detailed immutable leverage evidence is under `research/results/leverage_0040/` and the P4.5 decision is recorded in `docs/LEVERAGE_0040_P4_5_DECISION_2026-08-07.md`.
