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
| Phase 4 leverage research | **FAIL_STOP / LEVERAGE-0040 + 0041 IMMUTABLE / NO_PROMOTION** |
| P4.6 production leverage | **BLOCKED / NOT AUTHORIZED** |
| P5.1–P5.4 cycle research | **COMPLETE / FROZEN** |
| P5.5 joint validation | **COMPLETE / IMMUTABLE / NO_PROMOTION / FAIL_STOP** |
| P5.6 cycle integration | **BLOCKED / NO ELIGIBLE P5.5 CANDIDATE** |
| Phase 6 integrated shadow implementation/replay | **PASS / SHADOW ONLY / MERGED #109** |
| Phase 6 real elapsed evidence | **MEASUREMENT_INCONCLUSIVE_TIME_DEPENDENT** |
| Phase 7 limited-live readiness gate | **IMPLEMENTED / MERGED #110 / LAUNCH BLOCKED** |
| Phase 7 program mode | **MONITOR_ONLY** |
| Phase 8 bear-short research | **BEAR-SHORT-0001 PREREGISTERED / TRIGGER ABSENT / NOT RUN / MERGED #111** |
| Phase 0–8 drift audit | **COMPLETE / PASS_FINAL_HEAD_VERIFIED / DRIFT_2 REMEDIATED** |
| Production-authorized components | **none** |

```text
production_authorized_components = []
production gross cap             = 1.0
production launch authority      = NONE
first real short authority       = NONE
```

## Canonical product boundaries

- directional core: **BRRK-0011**;
- long target/tradable assets: **BTC / ETH / SOL / BNB**;
- XRP is **feature-only**;
- primary venue: **Hyperliquid**;
- canonical daily decision boundary: **00:00 UTC**;
- P4.1 defensive scale remains `[0,1]`;
- production gross cap remains `1.0`;
- no P5 cycle overlay was promoted;
- master-wallet private key, automated withdrawals and automated external transfers remain outside scope;
- credentials or `TRADING_MODE=trade` are execution plumbing, not production authority;
- actual zero-exposure → risk-on remains explicit-human-approved.

## Phase 4 closeout

`LEVERAGE-0040` and `LEVERAGE-0041` are immutable `NO_PROMOTION` studies. No >1 gross-cap candidate is eligible for P4.6 and no production leverage is authorized. Do not rerun or retune either experiment under the same ID.

`LEVERAGE-0040` immutable summary SHA256:

```text
3bb4dc46c61a5e9c7e049862575a89b2771830410ce4bc2bb25c83e469f52fc0
```

## Phase 5 closeout

P5.5 immutable result commit:

```text
ae20890d87567c98e403e3558219d5de55daef67
```

Summary SHA256:

```text
ccbdc067f9f7f1277e6eecaa2f74f31f84e3a1882ccef418e097b2ea66bf6e71
```

No profile / behavior-map combination passed the frozen event, economics, start-date, held-out and broad-policy gates. P5.6 is therefore `BLOCKED / NO ELIGIBLE CANDIDATE`; the canonical Phase 6 baseline carries **no cycle overlay**.

## Phase 6 — integrated shadow

Merged PR #109 at `1763d3c6f2c2d68f77f9e68b3cf9e252e4b799d4`.

Machine contract: `config/phase6_shadow_contract.json`.

Implementation/replay passed canonical P3.2 parity, committed golden vectors, reconciliation/audit checks and static zero-signer/zero-submit boundaries:

```text
implementation/replay = PASS_SHADOW_ONLY_IMPLEMENTATION_REPLAY
sign orders           = false
submit orders         = false
production_authorized = false
```

The real observation requirement is not backfilled by replay. Until at least 14 elapsed calendar days and at least 10 scheduled decisions satisfy the frozen contract, its state remains:

```text
MEASUREMENT_INCONCLUSIVE_TIME_DEPENDENT
```

## Phase 7 — launch readiness only

Readiness gate merged in PR #110. Machine contract: `config/phase7_launch_readiness.json`.

Current state:

```text
current_program_state = MONITOR_ONLY
production_authorized = false
launch                 = BLOCKED
```

At minimum, Phase 6 elapsed evidence, a frozen production release, operational/credential/monitoring evidence and explicit owner approval are required before launch. These transitions remain human-required:

```text
MONITOR_ONLY -> ACTIVE
FLAT -> LONG
FLAT -> SHORT
first short exposure of a new bear phase
```

## Phase 8 — bear-short research

`BEAR-SHORT-0001` was preregistered and merged in PR #111. Machine contract: `research/bear_short_0001/BEAR-SHORT-0001.json`.

There is no repository-valid `CONFIRMED_BEAR_TRANSITION_ARTIFACT`, therefore:

```text
status                      = PREREGISTERED_TRIGGER_ABSENT_NOT_RUN
trigger_present             = false
selection_status            = NONE_TRIGGER_ABSENT
short_ready                 = false
production_authorized       = false
first_real_short_authorized = false
```

Do not replace the missing trigger with a subjective current-market view and do not run trigger-dependent short economics under this experiment until the frozen trigger condition exists.

## Phase 0–8 drift audit

Machine contract: `config/phase0_8_drift_audit.json`. Evidence report: `docs/PHASE_0_8_DRIFT_AUDIT_2026-08-08.md`.

The audit found and remediated three drift classes without changing strategy economics:

1. legacy `TRADING_MODE=trade` could previously reach normal risk-increasing execution without the Phase 7 authority boundary;
2. legacy production-facing configuration/documentation still exposed `NORMAL_BETA_CAP=1.30`;
3. authoritative handoff docs lagged already-completed Phase 6/7/8 work.

Current invariants are:

```text
legacy normal-service new-risk authority = false
legacy production-facing beta cap        = 1.0
same-direction risk reduction            = preserved
emergency flatten                        = preserved
```

The audit closeout is `PASS_FINAL_HEAD_VERIFIED`. Audit success does **not** mean Phase 6 elapsed evidence passed, Phase 7 launch was approved, a bear transition was confirmed, or any real short was authorized.

## Exact next dependency

The next repository dependency is **real Phase 6 zero-authority elapsed-shadow evidence**, not another strategy implementation phase. Continue the frozen observation mechanism; do not manufacture elapsed time.

Phase 7 remains launch-blocked until its complete checklist and explicit owner approval exist. Phase 8 remains trigger-absent until the frozen confirmed-bear artifact exists.

## Source-of-truth order

1. `README.md`
2. `docs/CURRENT_STATE.md`
3. `docs/NEXT_STEPS.md`
4. `config/phase0_8_drift_audit.json`
5. `docs/ROADMAP_AUDIT_2026-08-07.md`
6. `docs/MASTER_PLAN_2026-08-05.md`
7. `docs/IMPLEMENTATION_ROADMAP_2026-08-05.md`
8. `config/decision_registry.json`
9. immutable `research/results/` and dated research documents as evidence
