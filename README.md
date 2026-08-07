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
| LEVERAGE-0040 / 0041 | **COMPLETE / IMMUTABLE / NO_PROMOTION** |
| Phase 4 leverage research | **FAIL_STOP / NO ELIGIBLE >1 CANDIDATE** |
| P4.6 production leverage | **NOT ENTERED / BLOCKED** |
| P5.1 cycle-top event taxonomy | **COMPLETE / MERGED / FROZEN** |
| P5.2 feature-family evidence | **COMPLETE / IMMUTABLE / DESCRIPTIVE CLOSEOUT** |
| P5.3 V1 state model | **COMPLETE / IMMUTABLE / NO_PROMOTION / ARCHITECTURE_FAIL** |
| P5.3 V2 architecture | **PREREGISTERED / FROZEN BEFORE V2 STATE PATHS** |
| P5.4 behavior mapping | **BLOCKED PENDING V2 CLOSEOUT** |
| P5.5–P5.6 | **NOT STARTED** |
| Phase 6 integrated shadow | **NOT STARTED** |
| Phase 7 limited-capital live long | **NOT STARTED / EXPLICIT APPROVAL REQUIRED** |
| Phase 8 bear-short research | **NOT STARTED** |
| Production-authorized components | **none** |

`production_authorized_components = []`

Current production gross cap remains **1.0**.

## Canonical product boundaries

- directional core: **BRRK-0011**;
- long target/tradable assets: **BTC / ETH / SOL / BNB**;
- XRP is **feature-only**;
- primary venue: **Hyperliquid**;
- canonical daily decision boundary: **00:00 UTC**;
- actual zero-exposure -> risk-on remains explicit-human-approved;
- intraday automation may reduce but may not autonomously add directional exposure;
- master-wallet private key, automated withdrawals and external transfers remain outside scope;
- P4.1 defensive scale stays `[0,1]`;
- production gross remains `1.0`.

## Phase 4 closeout

`LEVERAGE-0040` and `LEVERAGE-0041` are immutable `NO_PROMOTION` studies. No >1 gross-cap candidate is eligible for P4.6. Do not rerun or retune them under the same experiment IDs.

## Phase 5 cycle-top / exit program

### P5.1 — frozen taxonomy

Contract: `P5.1-EVENT-TAXONOMY-V1`.

The 2021/2025 event taxonomy, four high-volatility non-top controls, anchors and five relative evaluation buckets are frozen. Only 2021 November is explicitly terminal.

### P5.2 — immutable feature evidence

Contract: `P5.2-FEATURE-FAMILIES-V1`  
Result commit: `61d585afb64afbe3ead6422e7e62cde6c59fad40`  
Summary SHA256: `3f6dc3c512d22ac8f71d43ed155f2602cd40d5caf3d617c0e130e170727e0627`

P5.2 evaluated 29 frozen causal features. Six requested data families remain explicit `DATA_SOURCE_PENDING`; no final feature set, P5.3 threshold or production behavior was selected.

### P5.3 V1 — immutable negative evidence

State-model contract: `P5.3-STATE-MODEL-STRUCTURE-V1`  
Evidence contract: `P5.3-STATE-PATH-EVIDENCE-V1`  
Result commit: `7703b3ffec906a9d2ea58b33ee7feea5cd2f0a89`  
Summary SHA256: `a2e5be8d605af5a2c8206235402fe3a66b08fd994eaa8a71e84cfb1e3cbfed8f`

All three profiles first entered FLAT on `2021-02-23` inside frozen non-top control `P5C-2021-JAN-FEB-HIGH-VOL`. Because V1 made the market-state variable absorbing, each profile then spent 1832 of 1869 classified days in FLAT (`98.0203%`). V1 is therefore `NO_PROMOTION / ARCHITECTURE_FAIL`; no profile is eligible for P5.4.

Formal closeout: `docs/P5_3_STATE_PATH_CLOSEOUT.md`.

## P5.3 V2 — frozen architecture-isolation preregistration

Contract: `P5.3-MARKET-STATE-PERMISSION-SEPARATION-V2`  
Documentation: `docs/P5_3_V2_ARCHITECTURE_PREREG.md`  
Base main: `5b0cac61a45c13d28680e641dd434db4d9a6a2db`

V2 is **not** a V1 signal rescue. It changes one architecture boundary only:

```text
MARKET_STATE
  continuous market classification across the full historical path

RISK_PERMISSION_LOCK
  separate operational permission; actual re-risk after implemented zero exposure remains human-gated
```

### Frozen signal inheritance

The first V2 study keeps V1 exactly unchanged for:

- runtime feature inputs;
- evidence atoms and raw candidate priority;
- causal percentile normalization;
- EARLY / BALANCED / CONSERVATIVE thresholds;
- escalation persistence and de-escalation clear periods;
- P5.1 event anchors and buckets.

Before V2 interpretation, normalized values, evidence atoms and raw candidates must exactly match immutable V1.

### Single architecture delta

V1 allowed ordinary de-escalation only when the current state was not FLAT. V2 removes **only that exclusion for `MARKET_STATE`**.

`MARKET_STATE=FLAT` remains the highest severity and raw FLAT still enters immediately. But if the fully evaluated raw candidate stays below FLAT for the existing profile clear period, MARKET_STATE moves exactly one step to `DE_RISK_2`; each later lower step needs a fresh clear period.

No recovery threshold is added and no existing threshold changes.

### Permission boundary remains stricter than market classification

`RISK_PERMISSION_LOCK` is frozen as:

```text
UNLOCKED
LOCKED_PENDING_HUMAN_APPROVAL
```

MARKET_STATE has zero authority to unlock it. Automatic unlock is forbidden. Only explicit human approval may clear an operational lock.

P5.3 V2 does not fabricate a historical permission-lock path because P5.4 has not yet defined which market states map to actual zero directional exposure.

### V1 failure must reproduce

V2 must preserve the `2021-02-23` false raw FLAT in `P5C-2021-JAN-FEB-HIGH-VOL`. It may make later market regimes observable; it may not relabel the control or tune signals to erase the false trigger.

### V2 evaluation boundary

Architecture pass requires exact V1 raw/evidence parity, preservation of the false FLAT, later event windows remaining classifiable, and no market-state recovery being treated as operational re-risk authorization.

Architecture pass does **not** select a profile, accept signal quality, select P5.4 behavior, or authorize production. P5.4 remains blocked until V2 evidence closeout.

## Layer separation

```text
BRRK                 = which assets / relative weights
Cycle MARKET_STATE   = current market-risk classification
Risk permission      = whether re-risk is operationally allowed
Router               = which instruments implement targets
Execution            = safe realization
```

## Phase 5 order from here

1. P5.1 taxonomy — **COMPLETE / FROZEN**.
2. P5.2 feature evidence — **COMPLETE / IMMUTABLE**.
3. P5.3 V1 — **COMPLETE / IMMUTABLE / NO_PROMOTION**.
4. P5.3 V2 architecture prereg — **FROZEN BEFORE V2 STATE PATHS**.
5. P5.3 V2 implementation/evidence — **NEXT AFTER PREREG MERGE**.
6. P5.4 behavior mapping — **BLOCKED until V2 closeout**.
7. P5.5 validation — later.
8. P5.6 integration — later.
9. Phase 6 shadow — later, zero trading authority.
10. Phase 7 limited-capital live — explicit production approval required.
11. Phase 8 bear-short — later; first short remains human-gated.

## Source-of-truth order

1. `README.md`
2. `docs/CURRENT_STATE.md`
3. `docs/NEXT_STEPS.md`
4. `docs/ROADMAP_AUDIT_2026-08-07.md`
5. `docs/MASTER_PLAN_2026-08-05.md`
6. `docs/IMPLEMENTATION_ROADMAP_2026-08-05.md`
7. `config/decision_registry.json`
8. immutable `research/results/` and dated research documents as evidence
