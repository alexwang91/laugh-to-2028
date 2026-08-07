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
| P4 architecture / cap=1 / margin prerequisites | **COMPLETE / MERGED** |
| LEVERAGE-0040 | **COMPLETE / IMMUTABLE / NO_PROMOTION** |
| LEVERAGE-0041 | **COMPLETE / IMMUTABLE / NO_PROMOTION** |
| Phase 4 dynamic-leverage research line | **FAIL_STOP / NO ELIGIBLE >1 CANDIDATE** |
| P4.6 production leverage | **NOT ENTERED / BLOCKED — no promoted candidate** |
| Phase 5 cycle-top / exit intelligence | **NEXT** |
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

Every cap above 1.0 failed before the broad-region promotion stage. The preregistered liquidation-distance requirement was strictly `>55%`; measured minimum uniform-down distances fell from about `42.52%` at 1.05 to `27.71%` at 1.30. No >1 cap is eligible for P4.6.

Do not rerun, rescue, retune, reinterpret, or reuse `LEVERAGE-0040` or `LEVERAGE-0041` under the same experiment IDs.

## What has been completed

The current canonical implementation chain is:

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
```

Historical rejected or shadow research lines remain preserved as evidence; they are not silently promoted into BRRK or production.

A full task/deviation review is recorded in `docs/ROADMAP_AUDIT_2026-08-07.md`.

## Next roadmap work

The next forward program is **Phase 5 — cycle-top / late-bull / exit model**, which is a new research program rather than a retune of BRRK or either leverage study.

Order:

1. **P5.1 Event taxonomy** — label terminal-top, second-wind, and non-top high-volatility controls.
2. **P5.2 Feature families** — trend maturity, momentum exhaustion, leadership migration, breadth, leverage/speculation.
3. **P5.3 State model** — `NORMAL_BULL`, `BTC_LEADERSHIP_MATURING`, `LATE_BULL_ROTATION`, `EXHAUSTION_WATCH`, `DE_RISK_1`, `DE_RISK_2`, `FLAT`.
4. **P5.4 Required behavior** — allow late-bull rotation while reducing total gross as cycle hazard rises; hard-risk combinations may force FLAT.
5. **P5.5 Validation** — event-level / leave-one-event-out robustness, lead/lag, false-positive duration, missed upside, drawdown avoided, terminal wealth, second-wind behavior.
6. **P5.6 Integration** — cycle layer controls total directional risk; it does not rewrite BRRK relative ranking.
7. **Phase 6** — integrated live-data shadow system with zero signing/trading authority.
8. **Phase 7** — limited-capital live long only after explicit production approval and shadow/operational evidence.
9. **Phase 8** — bear-short research only after long/exit readiness; first short remains human-gated.

## Source-of-truth order

1. `README.md`
2. `docs/CURRENT_STATE.md`
3. `docs/NEXT_STEPS.md`
4. `docs/ROADMAP_AUDIT_2026-08-07.md`
5. `docs/MASTER_PLAN_2026-08-05.md`
6. `docs/IMPLEMENTATION_ROADMAP_2026-08-05.md`
7. `config/decision_registry.json`
8. dated audit/research/runbook documents as historical evidence

Immutable study outputs live under `research/results/`. The presence of a result file means evidence exists; it does not imply promotion or production authorization.
