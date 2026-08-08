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
| Phase 6 live-observation preactivation gate | **PREACTIVATION_BLOCKED_FAIL_CLOSED / GOVERNANCE V1** |
| Phase 6 durable evidence backend | **FROZEN / ACTIONS_ARTIFACT_V4 / 90D / NO CREDIT** |
| Phase 7 readiness gate | **IMPLEMENTED / MERGED #110 / LAUNCH BLOCKED** |
| Phase 7 program mode | **MONITOR_ONLY** |
| Phase 8 bear-short research | **BEAR-SHORT-0001 PREREGISTERED / TRIGGER ABSENT / NOT RUN / MERGED #111** |
| Phase 0–8 drift audit | **COMPLETE / PASS_FINAL_HEAD_VERIFIED / DRIFT_2 REMEDIATED** |
| Program-Level Epistemic Governance v1 | **PG0–PG6 COMPLETE / CI-ENFORCED / NO-DRIFT CLOSEOUT** |
| Stablecoin liquidity research | **STABLECOIN-LIQUIDITY-0001 / STAGE-1 FAIL_NO_INCREMENTAL_INFORMATION / TERMINAL STOP** |
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
- production gross cap remains `1.0`;
- no P5 cycle overlay was promoted;
- master-wallet private key, automated withdrawals and automated external transfers remain outside scope;
- credentials or `TRADING_MODE=trade` do not create production authority;
- actual zero-exposure → risk-on remains explicit-human-approved.

## Frozen research closeout

`LEVERAGE-0040` and `LEVERAGE-0041` remain immutable `NO_PROMOTION`. No >1 production leverage was selected or authorized.

`LEVERAGE-0040` immutable summary SHA256:

```text
3bb4dc46c61a5e9c7e049862575a89b2771830410ce4bc2bb25c83e469f52fc0
```

P5.5 immutable result commit and summary SHA256 remain:

```text
ae20890d87567c98e403e3558219d5de55daef67
ccbdc067f9f7f1277e6eecaa2f74f31f84e3a1882ccef418e097b2ea66bf6e71
```

No P5.5 profile/map combination passed the frozen validation stack, so P5.6 remains blocked and Phase 6 carries no cycle overlay.

`STABLECOIN-LIQUIDITY-0001` completed its single prospectively governed Stage-1 variant and terminated at `FAIL_NO_INCREMENTAL_INFORMATION / NO_PROMOTION`. It may not be rerun or rescued under the same research ID, creates no Edge Registry entry and changes no BRRK/Phase/production authority.

## Phase 6 / 7 / 8 authority

Phase 6 machine contract: `config/phase6_shadow_contract.json`.

```text
implementation/replay = PASS_SHADOW_ONLY_IMPLEMENTATION_REPLAY
sign orders           = false
submit orders         = false
production_authorized = false
minimum elapsed days  = 14
minimum decisions     = 10
```

Elapsed-time evidence cannot be replayed or backfilled. A repository audit found that the pre-existing `phase6-integrated-shadow.yml` is implementation/replay safety CI only: it has no scheduled future collector and no durable elapsed-evidence persistence. Therefore no automatic elapsed clock may be inferred from the Phase 6 PASS.

Governance v1 contains `research/governance/phase6_live_observation_gate.json` plus `phase6_live_observation_gate.py`. The gate is deliberately **not armed**. Schedule/duplicate-credit semantics are frozen, and the durable evidence backend is now separately frozen by `phase6_live_evidence_contract.json` / `phase6_live_evidence.py` to GitHub Actions Artifact v4 with 90-day retention, `overwrite=false`, immutable artifact identity outputs and a separately uploaded hash-bound receipt. The backend contract itself creates zero elapsed credit.

Two pre-arm dependencies remain: one explicit read-only observation account identity and current-position/account-equity valuation semantics for the permitted observation surfaces. The first eligible decision after a future arm remains the first canonical 00:00 UTC decision strictly after the arm commit timestamp; replay, rerun, duplicate timestamps and manual dispatch cannot create scheduled-decision credit.

Phase 7 machine contract: `config/phase7_launch_readiness.json`.

```text
current_program_state = MONITOR_ONLY
production_authorized = false
launch                 = BLOCKED
```

Human approval remains mandatory for `MONITOR_ONLY -> ACTIVE`, `FLAT -> LONG`, `FLAT -> SHORT` and the first short exposure of a new bear phase.

Phase 8 machine contract: `research/bear_short_0001/BEAR-SHORT-0001.json`.

```text
status                      = PREREGISTERED_TRIGGER_ABSENT_NOT_RUN
trigger_present             = false
short_ready                 = false
production_authorized       = false
first_real_short_authorized = false
```

## Program-Level Epistemic Governance v1

Governance v1 is prospective and extends the existing preregistration / RUN_ONCE / immutable-evidence / FAIL_STOP system rather than replacing it.

Frozen boundary:

```text
research_governance_version = 1
legacy_boundary_commit      = 896cbd123b7a0c38943815dd802f0f9dcd12e1c2
```

Authority is separated across:

- `config/decision_registry.json` — product/decision/production authority;
- `config/research_registry.json` — research families, experiments, typed lineage, trial/variant accounting and governance debt;
- `config/dataset_exposure_registry.json` — dataset slices and information-release/exposure events;
- `config/edge_registry.json` — admitted incremental-information edges only;
- existing Phase 6/7/8 contracts — phase/live authority.

The Dataset Exposure Registry is not globally empty: it now contains the prospectively recorded reconstructed-history Stablecoin validation slice/exposure. Legacy retrospective exposure remains intentionally unbackfilled where historical facts are unrecoverable. The Edge Registry remains empty because no feature has passed Governance-v1 incremental-information admission.

PG4 mapped 17 legacy records conservatively and records unrecoverable historical parameter trials, validation exposure, dataset exposure, lineage, researcher decisions and candidate universes as explicit Research Governance Debt. `UNKNOWN` remains UNKNOWN.

Future formal research is fail-closed: a changed formal `research/**` path must be covered by exactly one `PROGRAM_GOVERNED_V1` record in the same change, with frozen primary metric, stopping rule, variant budget, data-budget references, lineage semantics, researcher-degrees-of-freedom accounting and `production_authorized=false`.

Commands:

```bash
python -m research.governance.validate
python -m research.governance.enforce_future --base <PR_BASE_SHA>
python -m research.governance.phase6_live_evidence
python -m research.governance.phase6_live_observation_gate
python -m research.governance.audit
python -m research.governance.no_drift
```

`no_drift` compares the final repository against the pre-governance boundary, permits only governance/canonical-documentation changes, checks selected historical/economic git blobs for exact parity and re-validates strategy/authority invariants.

Canonical governance documentation:

- `docs/PROGRAM_GOVERNANCE_PG0_REPOSITORY_AUDIT_2026-08-08.md`;
- `docs/PROGRAM_GOVERNANCE_V1_SPEC_2026-08-08.md`;
- `docs/PROGRAM_GOVERNANCE_PG4_RETROSPECTIVE_MAPPING_2026-08-08.md`;
- `docs/PROGRAM_LEVEL_EPISTEMIC_GOVERNANCE_V1_FINAL_REPORT_2026-08-08.md`.

The framework **reduces research-process overfit**. It does not eliminate market nonstationarity, researcher historical knowledge, limited independent crypto regimes, dependence across observations, hidden qualitative choices or future structural breaks.

## Exact next dependency

Two Phase 6 live-observation operational semantics remain unresolved **before** any schedule or elapsed-evidence credit may be armed:

1. identify one explicit read-only observation account;
2. freeze how combined current positions and account equity are valued across the permitted observation surfaces, without changing P3.2/P3.3 economics;
3. then prospectively arm the collector in a separate change;
4. only the first 00:00 UTC decision strictly after that arm commit may begin scheduled-decision credit.

The durable create-only evidence backend/receipt identity and schedule/duplicate-credit rules are already frozen. Until the remaining two dependencies close, the Phase 6 live elapsed state remains `MEASUREMENT_INCONCLUSIVE_TIME_DEPENDENT`, with clock not armed. Do not backfill elapsed time and do not call replay/test artifacts live evidence.

After the Phase-6 collection path is truly armed, resume the original infrastructure plan: formal research lifecycle/state-machine enforcement, then Research Queue / trial-overlap accounting, before starting another result-bearing research family.

Phase 7 remains launch-blocked until its complete checklist and explicit owner approval exist. Phase 8 remains trigger-absent until the frozen confirmed-bear artifact exists.

## Source-of-truth order

1. `README.md`
2. `docs/CURRENT_STATE.md`
3. `docs/NEXT_STEPS.md`
4. `config/research_governance_v1.json`
5. `config/decision_registry.json`
6. `config/research_registry.json`
7. `config/dataset_exposure_registry.json`
8. `config/edge_registry.json`
9. `config/phase6_shadow_contract.json`
10. `config/phase7_launch_readiness.json`
11. `research/bear_short_0001/BEAR-SHORT-0001.json`
12. immutable research contracts/results and their hashes as evidence
