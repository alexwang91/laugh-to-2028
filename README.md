# laugh-to-2028

一个面向长期生存、可审计研究和自动执行的加密资产系统项目。

**回测结果、研究结论、代码合并与生产授权是不同层级。这个仓库不构成收益承诺或投资建议。**

## 当前状态 — 2026-08-08

```text
Phase 0-3                         COMPLETE / MERGED
Phase 4 leverage research         FAIL_STOP / NO_PROMOTION
P5.5                              COMPLETE / IMMUTABLE / NO_PROMOTION / FAIL_STOP
P5.6                              BLOCKED / NO ELIGIBLE CANDIDATE
Phase 6 implementation/replay     PASS_SHADOW_ONLY_IMPLEMENTATION_REPLAY / MERGED #109
Phase 6 live elapsed evidence     MEASUREMENT_INCONCLUSIVE_TIME_DEPENDENT / CLOCK NOT ARMED
Phase 6 evidence backend          FROZEN / MERGED #133
Phase 6 valuation contract        PHASE6-LIVE-VALUATION-V1 / PR #134 CANDIDATE
Phase 6 pre-arm state             3/4 FROZEN IN #134 CANDIDATE / ACCOUNT IDENTITY REMAINS
Phase 7                           MONITOR_ONLY / LAUNCH BLOCKED
Phase 8                           TRIGGER ABSENT / NOT RUN
Stablecoin Stage-1               FAIL_NO_INCREMENTAL_INFORMATION / TERMINAL STOP
production gross cap              1.0
production_authorized_components = []
first real short authority        NONE
```

## Canonical product boundaries

- directional core: **BRRK-0011**;
- long target/tradable assets: **BTC / ETH / SOL / BNB**;
- XRP is **feature-only**;
- primary venue: **Hyperliquid**;
- canonical decision boundary: **00:00 UTC**;
- P3.2 target engine: `P3.2-BRRK0011-V1`;
- P3.3 control: `P3.3-L1-BAND-V1`, aggregate L1 band `0.05`;
- BNB remains `PERP_ONLY_DEFAULT`;
- production gross cap remains `1.0`;
- no P5 cycle overlay or >1 production leverage was promoted;
- credentials do not create production authority;
- no automated withdrawal/external-transfer authority;
- no first real short authorization.

## Research closeout

`LEVERAGE-0040` and `LEVERAGE-0041` remain immutable `NO_PROMOTION`. P5.5 remains immutable `NO_PROMOTION_FAIL_STOP`.

`STABLECOIN-LIQUIDITY-0001` is terminal `FAIL_NO_INCREMENTAL_INFORMATION / NO_PROMOTION`; no same-ID rerun/rescue, Stage-2 eligibility, edge admission or portfolio integration exists.

## Phase 6 preactivation

The canonical Phase-6 shadow implementation is zero-authority and cannot sign or submit orders. Real elapsed evidence still requires >=14 elapsed days, >=10 genuine scheduled decisions, >=1 emergency drill and zero frozen quality failures.

The durable evidence backend is frozen to GitHub Actions Artifact v4 with 90-day retention, `overwrite=false`, immutable artifact identity and a hash-bound receipt; its existence creates zero elapsed credit.

PR #134 proposes `PHASE6-LIVE-VALUATION-V1`, limited to explicit Hyperliquid Standard mode:

```text
userAbstraction = disabled
```

It maps verified UBTC/UETH/USOL spot holdings plus signed BTC/ETH/SOL/BNB perp notionals into the existing P3.3 current-position/equity inputs. Unsupported modes/assets fail closed; BNB spot remains forbidden.

Candidate pre-arm state:

```text
observation account identity          UNRESOLVED
current-position/equity valuation     PR #134 CANDIDATE / TESTED
durable evidence backend              FROZEN / MERGED #133
schedule + duplicate-credit rule      FROZEN
collector_armed                       false
elapsed_evidence_credit_authorized    false
```

If #134 passes final CI and merges, only one pre-arm dependency remains: one exact verified **public read-only Hyperliquid master/subaccount address** compatible with Standard mode. Do not invent or derive the address from a private key.

## Exact next dependency

1. Run final #134 governance/no-drift/parity/Phase-6 safety CI.
2. Expected-head merge only if required checks are green.
3. Verify new `main` and canonical invariants.
4. Freeze one exact public read-only Hyperliquid master/subaccount address.
5. Verify `userAbstraction=disabled` and `PHASE6-LIVE-VALUATION-V1` compatibility.
6. Only at 4/4 dependencies create a separate prospective arm change.
7. First eligible credited decision = first `00:00 UTC` strictly after the arm commit.

Phase 7 remains `MONITOR_ONLY`; Phase 8 remains trigger-absent/not-run; all production/signature/submission authority remains false.

After genuine Phase-6 collection becomes operational, resume the infrastructure roadmap: formal research lifecycle/state-machine enforcement, then Research Queue / trial-overlap accounting.

## Source-of-truth order

1. `README.md`
2. `docs/CURRENT_STATE.md`
3. `docs/NEXT_STEPS.md`
4. governance / decision / research / dataset / edge registries
5. Phase 6/7/8 machine contracts
6. immutable research contracts/results