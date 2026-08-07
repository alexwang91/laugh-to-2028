# laugh-to-2028

一个面向长期生存、可审计研究和自动执行的加密资产系统项目。

**回测结果、研究结论、代码合并与生产授权是不同层级。这个仓库不构成收益承诺或投资建议。**

## 当前状态 — 2026-08-07

| 模块 | 状态 |
| --- | --- |
| Phase 0 — governance / canonical config | **COMPLETE / MERGED** |
| Phase 1 — execution truth & safety | **COMPLETE / MERGED** |
| Phase 2 — instrument / routing / cost | **COMPLETE / MERGED** |
| Phase 3 — data → target → rebalance → contribution | **COMPLETE / MERGED** |
| P4.1 defensive scaler `[0,1]` | **COMPLETE / MERGED** |
| LEVERAGE-0040 | **COMPLETE / IMMUTABLE / NO_PROMOTION** |
| LEVERAGE-0041 | **COMPLETE / IMMUTABLE / NO_PROMOTION** |
| Phase 4 leverage research | **FAIL_STOP / NO ELIGIBLE >1 CANDIDATE** |
| P4.6 production leverage | **NOT ENTERED / BLOCKED** |
| P5.1 cycle-top event taxonomy | **COMPLETE / MERGED / FROZEN** |
| P5.2 feature-family evidence | **COMPLETE / IMMUTABLE / DESCRIPTIVE CLOSEOUT** |
| P5.3 state model | **NEXT** |
| P5.4–P5.6 | **NOT STARTED** |
| Phase 6 integrated shadow | **NOT STARTED** |
| Phase 7 limited-capital live long | **NOT STARTED / EXPLICIT APPROVAL REQUIRED** |
| Phase 8 bear-short research | **NOT STARTED** |
| Production-authorized components | **none** |

`production_authorized_components = []`

Current production gross cap remains **1.0**.

## Canonical strategy / product boundaries

- directional core: **BRRK-0011**;
- long target/tradable assets: **BTC / ETH / SOL / BNB**;
- XRP is **feature-only**;
- primary venue: **Hyperliquid**;
- canonical daily decision boundary: **00:00 UTC**;
- FLAT means zero directional exposure;
- `FLAT -> LONG`, `FLAT -> SHORT`, `MONITOR_ONLY -> ACTIVE`, and the first short of a new bear phase require explicit human approval;
- intraday automation may reduce risk but may not autonomously add directional exposure;
- bot credentials are trading Agent/API credentials only;
- master-wallet private key, automated withdrawals, and automated external transfers remain outside scope;
- P4.1 defensive scale remains frozen in `[0,1]`;
- production gross remains **1.0** unless a future research candidate passes a separately authorized production gate.

## Phase 4 leverage closeout

### LEVERAGE-0040

- immutable result commit: `bd256e77a9800556e97769858fbb3ba5054c4389`;
- summary SHA256: `3bb4dc46c61a5e9c7e049862575a89b2771830410ce4bc2bb25c83e469f52fc0`;
- selection: `NO_PROMOTION`;
- selected research cap: none;
- selected operating DD budget: none.

### LEVERAGE-0041

- immutable result commit: `8ea784830cfffbf892a258cb329d437725d41982`;
- summary SHA256: `e41a5895263e7aa9206df9fa99fcbb71e5f937abc4746a567fbeb462cca88d17`;
- selection: `NO_PROMOTION`;
- selected research cap: none;
- selected operating DD budget: none;
- prospective P4.6 cap: none;
- production authorization: false.

At 5 bps execution cost:

| Gross cap | CAGR | Max drawdown | Sharpe | Final research pass |
| --- | ---: | ---: | ---: | --- |
| 1.00 | 61.28% | -33.83% | 1.3005 | comparator |
| 1.05 | 62.56% | -35.30% | 1.2935 | **FAIL** |
| 1.10 | 62.84% | -36.59% | 1.2746 | **FAIL** |
| 1.15 | 62.96% | -37.90% | 1.2544 | **FAIL** |
| 1.20 | 64.90% | -39.16% | 1.2574 | **FAIL** |
| 1.25 | 64.89% | -40.19% | 1.2387 | **FAIL** |
| 1.30 | 66.28% | -40.93% | 1.2360 | **FAIL** |

Every cap above 1.0 failed before the broad-region promotion stage. No >1 cap is eligible for P4.6. Do not rerun, rescue or reinterpret `LEVERAGE-0040` / `LEVERAGE-0041` under the same experiment IDs.

## Completed implementation chain

```text
Phase 0 governance/config
-> Phase 1 execution truth P1.1-P1.8
-> Phase 2 instrument/routing/cost P2.1-P2.4
-> Phase 3 P3.1 data contract
-> P3.2 canonical BRRK target API
-> P3.3 rebalance/turnover control
-> P3.4 contribution handling
-> P4 defensive baseline + leverage architecture/prerequisites
-> LEVERAGE-0039 STOPPED PRE-RUN
-> LEVERAGE-0040 COMPLETE / NO_PROMOTION
-> LEVERAGE-0041 COMPLETE / NO_PROMOTION
-> P5.1 EVENT TAXONOMY FROZEN
-> P5.2 IMMUTABLE FEATURE EVIDENCE / DESCRIPTIVE CLOSEOUT
```

Historical rejected or shadow research lines remain preserved as evidence; they are not silently promoted into BRRK or production.

A full task/deviation review is recorded in `docs/ROADMAP_AUDIT_2026-08-07.md`.

## Phase 5 cycle-top / exit program

### P5.1 — frozen event taxonomy

P5.1 is frozen in `research/cycle_exit/p5_1_event_taxonomy.json` and documented in `docs/P5_1_EVENT_TAXONOMY.md`.

It distinguishes before feature/model fitting:

- 2021 spring major top / May crash as nonterminal;
- 2021 summer second-wind transition;
- 2021 November terminal top / bear transition;
- 2025 June, August and October new-high/deleveraging phases;
- subsequent late-2025 deterioration without hardcoding it as a terminal top;
- multiple high-volatility non-top controls.

Calendar windows are frozen first and anchors are mechanically resolved from canonical BTCUSDT UTC daily closes. Later research may not move those windows/anchors to improve model results.

### P5.2 — immutable feature evidence

Contract: `P5.2-FEATURE-FAMILIES-V1`.

Immutable result commit:

`61d585afb64afbe3ead6422e7e62cde6c59fad40`

Immutable summary SHA256:

`3f6dc3c512d22ac8f71d43ed155f2602cd40d5caf3d617c0e130e170727e0627`

P5.2 evaluated **29 frozen causal features** across BTC trend maturity, momentum exhaustion, leadership migration and canonical breadth. All 29 passed the frozen coverage gate.

Six desired data families remain explicit `DATA_SOURCE_PENDING` rather than being replaced after seeing results:

- BTC dominance;
- broad-market breadth;
- comparable historical funding;
- historical open interest;
- basis/premium;
- liquidation history.

The result explicitly selected **no final feature set, no P5.3 thresholds and no production behavior**.

Formal interpretation: `docs/P5_2_FEATURE_EVIDENCE_CLOSEOUT.md`.

Derived non-authorizing diagnostics: `research/analysis/p5_2_closeout/`.

### What P5.2 says structurally

The evidence argues against a one-indicator “cycle top” score:

- realized-volatility state is powerful context but also appears in second-wind and nonterminal events, so it is not a terminal trigger by itself;
- ETH/BTC leadership is strong near terminal **and** second-wind/nonterminal structures, which requires a distinct `LATE_BULL_ROTATION` state rather than treating alt leadership as bearish;
- 20d price-versus-RSI rank divergence is the strongest 2021 terminal target-lead hypothesis, but there is only one explicit terminal event, so it cannot be promoted as a cross-cycle terminal rule;
- breadth acceleration describes transition shape but is not terminal-specific in the lead window;
- raw daily/4h RSI levels are not sufficient as standalone exit rules;
- distance from recent BTC highs contains useful second-wind versus top-like context;
- discrete breadth/consolidation features require categorical treatment where control MAD is zero.

### P5.3 — NEXT: multi-state cycle model

Target state vocabulary:

```text
NORMAL_BULL
BTC_LEADERSHIP_MATURING
LATE_BULL_ROTATION
EXHAUSTION_WATCH
DE_RISK_1
DE_RISK_2
FLAT
```

P5.3 must preregister state semantics and allowed evidence before numerical threshold fitting. It must preserve BRRK relative ranking and use the cycle layer only to decide **how much total directional risk** to take.

Key boundary:

```text
BRRK        = which assets / relative weights
Cycle layer = how much total directional risk
Router      = which instruments implement it
Execution   = how to reach actual target safely
```

ETH/BTC/alt rotation is not automatically bearish. A top/de-risk transition must depend on multi-family deterioration/exhaustion evidence, not on RSI, volatility or relative leadership alone.

### Remaining Phase 5 order

1. **P5.1 Event taxonomy — COMPLETE / FROZEN**.
2. **P5.2 Feature evidence — COMPLETE / IMMUTABLE / DESCRIPTIVE CLOSEOUT**.
3. **P5.3 State model — NEXT** — preregister multi-state structure, then fit/evaluate without retuning P5.1/P5.2.
4. **P5.4 Required behavior** — map accepted state semantics to total-risk behavior while preserving BRRK ranking.
5. **P5.5 Validation** — event-level / leave-one-event-out robustness, lead/lag, false-positive duration, missed upside, drawdown avoided, terminal wealth and second-wind behavior.
6. **P5.6 Integration** — cycle layer above BRRK as total-risk control only.
7. **Phase 6** — integrated live-data shadow system with zero signing/trading authority.
8. **Phase 7** — limited-capital live long only after explicit production approval and shadow/operational evidence.
9. **Phase 8** — bear-short research later; first short remains human-gated.

## Source-of-truth order

1. `README.md`
2. `docs/CURRENT_STATE.md`
3. `docs/NEXT_STEPS.md`
4. `docs/ROADMAP_AUDIT_2026-08-07.md`
5. `docs/MASTER_PLAN_2026-08-05.md`
6. `docs/IMPLEMENTATION_ROADMAP_2026-08-05.md`
7. `config/decision_registry.json`
8. dated audit/research/runbook documents as historical evidence

Immutable study outputs live under `research/results/`. The presence of a result means evidence exists; it does not imply promotion or production authorization.
