# laugh-to-2028

一个面向长期生存、可审计研究和自动执行的加密资产系统项目。

**回测结果、研究结论、代码合并与生产授权是不同层级。这个仓库不构成收益承诺或投资建议。**

## 当前状态 — 2026-08-08

| 模块 | 状态 |
| --- | --- |
| Phase 0–3 | **COMPLETE / MERGED** |
| Phase 4 leverage research | **FAIL_STOP / LEVERAGE-0040 + 0041 IMMUTABLE / NO_PROMOTION** |
| P4.6 production leverage | **BLOCKED / NOT AUTHORIZED** |
| P5.1–P5.4 cycle research | **COMPLETE / FROZEN** |
| P5.5 joint validation | **COMPLETE / IMMUTABLE / NO_PROMOTION / FAIL_STOP** |
| P5.6 cycle integration | **BLOCKED / NO ELIGIBLE P5.5 CANDIDATE** |
| Phase 6 implementation/replay | **PASS / SHADOW ONLY / MERGED #109** |
| Phase 6 real elapsed evidence | **MEASUREMENT_INCONCLUSIVE_TIME_DEPENDENT / CLOCK NOT ARMED** |
| Phase 6 preactivation gate | **PREACTIVATION_BLOCKED_FAIL_CLOSED** |
| Phase 6 durable evidence backend | **FROZEN / ACTIONS_ARTIFACT_V4 / 90D / NO CREDIT / MERGED #133** |
| Phase 6 valuation contract | **PHASE6-LIVE-VALUATION-V1 / PR #134 CANDIDATE / STANDARD MODE ONLY** |
| Phase 6 pre-arm state | **3/4 FROZEN IN #134 CANDIDATE / ACCOUNT IDENTITY REMAINS** |
| Phase 7 readiness gate | **IMPLEMENTED / MERGED #110 / LAUNCH BLOCKED** |
| Phase 7 program mode | **MONITOR_ONLY** |
| Phase 8 bear-short research | **BEAR-SHORT-0001 PREREGISTERED / TRIGGER ABSENT / NOT RUN / MERGED #111** |
| Program-Level Epistemic Governance v1 | **PG0–PG6 COMPLETE / CI-ENFORCED / NO-DRIFT** |
| Stablecoin liquidity research | **STAGE-1 FAIL_NO_INCREMENTAL_INFORMATION / TERMINAL STOP** |
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
- P3.2 target engine: `P3.2-BRRK0011-V1`;
- P3.3 rebalance control: `P3.3-L1-BAND-V1`, aggregate L1 band `0.05`;
- production gross cap remains `1.0`;
- no P5 cycle overlay was promoted;
- no production leverage >1 was promoted;
- credentials or `TRADING_MODE=trade` do not create production authority;
- actual zero-exposure → risk-on remains explicit-human-approved;
- master-wallet private key, automated withdrawals and automated external transfers remain outside scope.

## Frozen research closeout

`LEVERAGE-0040` and `LEVERAGE-0041` remain immutable `NO_PROMOTION`. P5.5 remains immutable `NO_PROMOTION_FAIL_STOP` and P5.6 is ineligible.

`STABLECOIN-LIQUIDITY-0001` completed its single prospectively governed Stage-1 variant and terminated at `FAIL_NO_INCREMENTAL_INFORMATION / NO_PROMOTION`. It may not be rerun or rescued under the same research ID, creates no Edge Registry entry and changes no BRRK/Phase/production authority.

## Phase 6 live-observation boundary

```text
implementation/replay = PASS_SHADOW_ONLY_IMPLEMENTATION_REPLAY
sign orders           = false
submit orders         = false
production_authorized = false
minimum elapsed days  = 14
minimum decisions     = 10
minimum drills        = 1
```

Elapsed-time evidence cannot be replayed or backfilled. The existing integrated-shadow workflow is implementation/replay safety CI only; it does not itself accumulate the required real elapsed evidence.

The preactivation gate remains deliberately unarmed. The durable evidence backend is frozen to GitHub Actions Artifact v4 with 90-day retention, `overwrite=false`, immutable artifact identity outputs and a separately uploaded hash-bound receipt. That backend creates zero elapsed credit by itself.

PR #134 proposes `PHASE6-LIVE-VALUATION-V1`. It supports only explicit Hyperliquid Standard mode (`userAbstraction=disabled`) and maps verified UBTC/UETH/USOL spot holdings plus signed BTC/ETH/SOL/BNB perp notionals into the existing P3.3 position/equity inputs. Unsupported modes/assets fail closed; BNB remains perp-only.

Current candidate pre-arm dependency state:

```text
observation account identity          UNRESOLVED
current-position/equity valuation     FROZEN IN #134 CANDIDATE
durable create-only evidence backend  FROZEN / MERGED #133
schedule + duplicate-credit rule      FROZEN
collector_armed                       false
elapsed_evidence_credit_authorized    false
```

If #134 passes final CI and merges unchanged, only one external pre-arm dependency remains: one exact verified public read-only Hyperliquid master/subaccount address compatible with Standard mode. The address must not be invented or derived from a private key merely to close the gate.

A later arm change is separate. Its first eligible scheduled decision is the first canonical `00:00 UTC` decision strictly after the arm commit timestamp. Replay, rerun, duplicate timestamps and manual dispatch cannot create scheduled-decision credit.

## Phase 7 / 8 authority

Phase 7 remains `MONITOR_ONLY`, launch-blocked and `production_authorized=false`. Phase 8 remains trigger-absent/not-run with no short or first-real-short authority.

## Program-Level Epistemic Governance v1

```text
research_governance_version = 1
legacy_boundary_commit      = 896cbd123b7a0c38943815dd802f0f9dcd12e1c2
```

Authority remains separated across decision/research/dataset/edge registries and Phase 6/7/8 machine contracts. Future formal research is fail-closed and must be preregistered prospectively. Historical unknowns remain explicit governance debt.

## Exact next dependency

1. Finish PR #134 final-head CI/governance and expected-head merge.
2. Verify the new `main` and canonical no-drift invariants.
3. Freeze one exact public read-only Hyperliquid master/subaccount address.
4. Verify `userAbstraction=disabled` and compatibility with `PHASE6-LIVE-VALUATION-V1`.
5. Only when all 4/4 dependencies are frozen, create a separate prospective arm change.
6. Only genuine future scheduled decisions strictly after the arm commit may count toward Phase-6 elapsed evidence.

Until then Phase 6 remains `MEASUREMENT_INCONCLUSIVE_TIME_DEPENDENT`, Phase 7 remains `MONITOR_ONLY`, Phase 8 remains trigger-absent/not-run, and all production/signature/submission authority remains false.

After the Phase-6 collection path is genuinely operational, resume the infrastructure roadmap: formal research lifecycle/state-machine enforcement, then Research Queue / trial-overlap accounting.

## Source-of-truth order

1. `README.md`
2. `docs/CURRENT_STATE.md`
3. `docs/NEXT_STEPS.md`
4. governance/decision/research/dataset/edge registries
5. Phase 6/7/8 machine contracts
6. immutable research contracts/results and hashes