# laugh-to-2028

一个面向长期生存、可审计研究和自动执行的加密资产系统项目。

**回测结果、研究结论、代码合并与生产授权是不同层级。这个仓库不构成收益承诺或投资建议。**

## 当前状态 — 2026-08-08

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
| P5.3 V2 architecture | **COMPLETE / IMMUTABLE EVIDENCE / ARCHITECTURE_PASS** |
| P5.3 selected profile | **NONE** |
| P5.4 behavior mapping | **NEXT / FIXED-CANDIDATE PREREGISTRATION** |
| P5.5 validation | **NOT STARTED** |
| P5.6 integration | **NOT STARTED** |
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

All three profiles first entered FLAT on `2021-02-23` inside frozen non-top control `P5C-2021-JAN-FEB-HIGH-VOL`. Because V1 made the research market-state variable absorbing, each profile then spent 1832 of 1869 classified days in FLAT (`98.0203%`). V1 is immutable `NO_PROMOTION / ARCHITECTURE_FAIL`.

Formal closeout: `docs/P5_3_STATE_PATH_CLOSEOUT.md`.

### P5.3 V2 — immutable architecture-isolation evidence

Architecture contract: `P5.3-MARKET-STATE-PERMISSION-SEPARATION-V2`  
Evidence contract: `P5.3-V2-MARKET-STATE-PATH-EVIDENCE-V1`  
Result commit: `e732b7ebe570236bf43084caecb6ea15f7edecb8`  
Summary SHA256: `05d5d68a59c8b13f1122d98ed75d03934defdc9d73c7dd92e038c92fd97d2e52`

V2 changed one architecture boundary only:

```text
MARKET_STATE
  continuous research classification across the full historical path

RISK_PERMISSION_LOCK
  separate operational permission; actual re-risk after implemented zero exposure remains human-gated
```

The V1 signal layer was not retuned. Immutable V2 evidence reports:

```text
architecture_pass                    true
raw_candidate_parity_fraction        1.0
atom_parity_fraction                 1.0
normalization_parity                 true
normalization_count_parity           true
pre_first_flat_state_parity_fraction 1.0
false_flat_reproduced                true
post_false_flat_nonflat_exists       true
later_events_observable              true
profile_selected                     false
p5_4_mapping_selected                false
risk_permission_unlock_authorized    false
production_authorized                false
```

The frozen false raw FLAT remains exactly visible on `2021-02-23`, but MARKET_STATE now recovers using the already-frozen clear-period mechanics:

| Profile | first FLAT episode | first non-FLAT | FLAT days / classified days |
| --- | --- | --- | ---: |
| EARLY | 2021-02-23 .. 2021-02-28 | 2021-03-01 | 6 / 1869 |
| BALANCED | 2021-02-23 .. 2021-02-28 | 2021-03-01 | 6 / 1869 |
| CONSERVATIVE | 2021-02-23 .. 2021-03-02 | 2021-03-03 | 8 / 1869 |

This fixes the **research architecture** defect: one early FLAT no longer erases every later event window.

It does **not** accept the inherited signal layer. The false FLAT remains negative evidence, no profile is selected, and P5.5 must charge false-positive duration and missed upside.

Examples from the now-observable state history reinforce that distinction:

- 2021 November terminal target-lead is `EXHAUSTION_WATCH` for all profiles rather than `DE_RISK_1+`;
- 2021 September non-top control produces substantial de-risk occupancy for EARLY;
- 2021 summer second-wind behavior varies materially by profile.

Formal V2 closeout: `docs/P5_3_V2_MARKET_STATE_CLOSEOUT.md`.

## P5.4 — next research dependency

The Implementation Roadmap defines P5.4 as **Required Behavior** and P5.5 as the owner of event/economic validation. V2 architecture evidence therefore unblocks P5.4 **research candidate definition only**.

P5.4 may preregister a small fixed family mapping MARKET_STATE to total gross-risk multipliers, subject to:

- all multipliers remain in `[0,1]`; Phase 4 authorized no >1 leverage;
- `NORMAL_BULL = 1.0`;
- mappings are monotone non-increasing with state severity;
- behavior scales total BRRK gross only and does not rewrite relative BTC/ETH/SOL/BNB ranking;
- `LATE_BULL_ROTATION` is not automatically treated as bearish/zero;
- an actual zero-exposure action remains human-gated for subsequent re-risk;
- no P5.4 winner is selected before P5.5;
- candidate values are frozen before P5.5 economic/event evaluation.

P5.5 must evaluate the Cartesian set of the three frozen P5.3 profiles × preregistered P5.4 behavior maps and may fail-stop if no robust candidate exists.

## Layer separation

```text
BRRK                 = which assets / relative weights
Cycle MARKET_STATE   = current market-risk classification
P5.4 behavior        = candidate total gross-risk response
Risk permission      = whether actual re-risk is operationally allowed
Router               = which instruments implement targets
Execution            = safe realization
```

## Phase 5 order from here

1. P5.1 taxonomy — **COMPLETE / FROZEN**.
2. P5.2 feature evidence — **COMPLETE / IMMUTABLE**.
3. P5.3 V1 — **COMPLETE / IMMUTABLE / ARCHITECTURE_FAIL**.
4. P5.3 V2 — **COMPLETE / IMMUTABLE EVIDENCE / ARCHITECTURE_PASS**.
5. P5.4 fixed behavior candidates — **NEXT / PREREGISTER BEFORE ECONOMIC TEST**.
6. P5.5 joint profile/mapping validation — later.
7. P5.6 integration — later.
8. Phase 6 shadow — later, zero trading authority.
9. Phase 7 limited-capital live — explicit production approval required.
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
