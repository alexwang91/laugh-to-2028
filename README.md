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
| P5.3 V1 state model | **COMPLETE / IMMUTABLE / NO_PROMOTION / ARCHITECTURE_FAIL** |
| P5.3 V2 architecture | **NEXT** |
| P5.4 behavior mapping | **BLOCKED / NO ELIGIBLE P5.3 CLASSIFIER** |
| P5.5–P5.6 | **NOT STARTED** |
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
- actual zero-exposure -> risk-on transitions remain explicit-human-approved;
- intraday automation may reduce risk but may not autonomously add directional exposure;
- master-wallet private key, automated withdrawals, and automated external transfers remain outside scope;
- P4.1 defensive scale remains frozen in `[0,1]`;
- production gross remains **1.0**.

## Phase 4 leverage closeout

`LEVERAGE-0040` and `LEVERAGE-0041` are immutable `NO_PROMOTION` studies. No >1 gross-cap candidate is eligible for P4.6. Do not rerun or retune them under the same experiment IDs.

## Phase 5 cycle-top / exit program

### P5.1 — frozen event taxonomy

Contract: `P5.1-EVENT-TAXONOMY-V1`.

P5.1 freezes the required 2021/2025 event structure plus four high-volatility non-top controls before model fitting. Only 2021 November is explicitly terminal. Search windows, mechanical anchors and the five relative evaluation buckets remain immutable.

### P5.2 — immutable feature evidence

Contract: `P5.2-FEATURE-FAMILIES-V1`.

Immutable result commit:

`61d585afb64afbe3ead6422e7e62cde6c59fad40`

Immutable summary SHA256:

`3f6dc3c512d22ac8f71d43ed155f2602cd40d5caf3d617c0e130e170727e0627`

P5.2 evaluated 29 frozen causal features across BTC trend maturity, momentum exhaustion, leadership migration and canonical breadth. All 29 passed coverage. Six desired data families remain explicit `DATA_SOURCE_PENDING` rather than being replaced with favorable proxies:

- BTC dominance;
- broad-market breadth;
- comparable historical funding;
- historical open interest;
- basis/premium;
- liquidation history.

P5.2 selected no final feature set, no P5.3 threshold and no production behavior.

Formal closeout: `docs/P5_2_FEATURE_EVIDENCE_CLOSEOUT.md`.

### P5.3 V1 — immutable negative state-model evidence

State-model contract:

`P5.3-STATE-MODEL-STRUCTURE-V1`

State-path evidence contract:

`P5.3-STATE-PATH-EVIDENCE-V1`

Immutable result commit:

`7703b3ffec906a9d2ea58b33ee7feea5cd2f0a89`

Immutable summary SHA256:

`a2e5ece89fec93a24e1a65e134a78824629b4b418e106294a6b0821fbd52608b`

The one-time run and immutable validator both completed successfully. The result itself is a **research failure**:

| Profile | Init date | First FLAT | Classified days | FLAT days | FLAT fraction |
| --- | --- | --- | ---: | ---: | ---: |
| EARLY | 2021-01-11 | 2021-02-23 | 1874 | 1837 | 98.0256% |
| BALANCED | 2021-01-11 | 2021-02-23 | 1874 | 1837 | 98.0256% |
| CONSERVATIVE | 2021-01-11 | 2021-02-23 | 1874 | 1837 | 98.0256% |

All three profiles first enter FLAT inside the frozen `P5C-2021-JAN-FEB-HIGH-VOL` event, which is explicitly a **non-top control**. In that control's `near_event` bucket, all profiles are FLAT for 6/7 classified days (`85.7143%`).

This is not caused by missing data. On `2021-02-23` the inputs are complete, minimum calibration depth is 57, and the frozen rule simultaneously reports:

```text
exhaustion         true
strong_exhaustion  true
damage             true
strong_damage      true
raw candidate      FLAT
```

Therefore V1 has no profile eligible for P5.4.

Formal closeout: `docs/P5_3_STATE_PATH_CLOSEOUT.md`.

### Architecture problem exposed by V1

The raw market candidate recovered rapidly after the false FLAT:

```text
2021-02-27  DE_RISK_2
2021-02-28  NORMAL_BULL
2021-03-01  NORMAL_BULL
2021-03-09  BTC_LEADERSHIP_MATURING
```

The final V1 state nevertheless remains FLAT because V1 made the **market-state history itself absorbing**.

That conflates:

```text
MARKET_STATE
  what current market evidence says

RISK_PERMISSION_LOCK
  whether risk may actually be re-added after a zero-exposure action
```

The operational permission boundary is correctly human-gated. The research classifier should not lose all later market-state information merely because a prior severe state occurred.

### P5.3 V1 disposition

```text
P5.3-STATE-MODEL-STRUCTURE-V1  COMPLETE / IMMUTABLE / NO_PROMOTION
P5.3-STATE-PATH-EVIDENCE-V1    COMPLETE / IMMUTABLE
profile selected               NONE
P5.4 eligible profile          NONE
production authorization       NONE
```

V1 must not be rerun, retuned or rewritten after seeing the result.

### P5.3 V2 — NEXT

P5.4 is blocked. The next task is a **new P5.3 architecture study**, not a V1 rescue.

The first V2 study should change only the architecture separation:

```text
MARKET_STATE
  continues classifying market evidence after a FLAT observation and can later describe recovery under preregistered de-escalation rules

RISK_PERMISSION_LOCK
  separate operational state; any actual future re-risk after zero exposure remains explicit-human-approved
```

To isolate this architecture change, the first V2 study should keep unchanged:

- P5.1 taxonomy and buckets;
- P5.2 immutable feature panel;
- V1 runtime feature set;
- V1 evidence atoms;
- causal percentile normalization;
- EARLY/BALANCED/CONSERVATIVE percentile thresholds;
- V1 persistence/clear-period values.

The 2021-02-23 false raw FLAT remains evidence and must remain visible. V2 does not get to relabel the control or tune thresholds to remove it.

Only after a usable market-state history exists should P5.4 define research mappings from state to total directional risk. P5.5 then owns robustness/economic selection.

## Layer separation

```text
BRRK                 = which assets / relative weights
Cycle MARKET_STATE    = current market-risk classification
Risk permission       = whether re-risk is operationally allowed
Router                = which instruments implement targets
Execution             = safe realization
```

No Phase 5 research result currently authorizes production.

## Phase 5 order from here

1. P5.1 Event taxonomy — **COMPLETE / FROZEN**.
2. P5.2 Feature evidence — **COMPLETE / IMMUTABLE**.
3. P5.3 V1 — **COMPLETE / IMMUTABLE / NO_PROMOTION**.
4. P5.3 V2 architecture separation — **NEXT**.
5. P5.4 behavior mapping — **BLOCKED until usable P5.3 classifier**.
6. P5.5 validation — later.
7. P5.6 integration — later.
8. Phase 6 shadow — later, zero trading authority.
9. Phase 7 limited-capital live — only after explicit production approval.
10. Phase 8 bear-short — later; first short remains human-gated.

## Source-of-truth order

1. `README.md`
2. `docs/CURRENT_STATE.md`
3. `docs/NEXT_STEPS.md`
4. `docs/ROADMAP_AUDIT_2026-08-07.md`
5. `docs/MASTER_PLAN_2026-08-05.md`
6. `docs/IMPLEMENTATION_ROADMAP_2026-08-05.md`
7. `config/decision_registry.json`
8. immutable `research/results/` and dated research documents as evidence
