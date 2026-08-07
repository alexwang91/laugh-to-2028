# laugh-to-2028

一个面向长期生存、可审计研究和自动执行的加密资产系统项目。

这个仓库同时包含：

- 方向性研究与历史证据；
- 交易执行与订单安全；
- 现货 / 永续路由与成本模型；
- 数据契约、目标权重、再平衡和资金流处理；
- 杠杆研究的预注册、风险约束和生产授权边界。

**它不是收益承诺，也不是投资建议。回测、研究通过、代码合并和生产授权是四个不同层级。**

---

## 当前状态 — 2026-08-07

| 模块 | 状态 |
| --- | --- |
| Phase 0 — canonical config / governance baseline | **COMPLETE / MERGED** |
| Phase 1 — execution truth & safety | **COMPLETE / MERGED** |
| Phase 2 — instrument / routing / execution-cost evidence | **COMPLETE / MERGED** |
| Phase 3 — data → target → rebalance → contribution pipeline | **COMPLETE / MERGED** |
| P4.1 — corrected defensive scaler `[0,1]` | **COMPLETE / MERGED** |
| P4.2 / P4.3 — leverage architecture, cap=1 parity, margin/liquidation prerequisites | **COMPLETE / MERGED** |
| Repository hygiene / documentation normalization | **COMPLETE / MERGED — PR #91** |
| P4.4 — `LEVERAGE-0040` one-time study | **PAUSED / DRAFT / NOT RUN** |
| P4.5 — select/fail leverage decision | **BLOCKED on P4.4 result** |
| P4.6 — production leverage authorization | **BLOCKED / SEPARATE GATE** |
| Phase 5 — exit intelligence | **NOT STARTED / BLOCKED** |
| Production-authorized components | **none** |

Active research PR:

- **#90 — `P4.4 [PAUSED / DRAFT]: freeze and preflight LEVERAGE-0040 one-time study`**
- branch: `p4-4/leverage-0040-one-time-study-v2`
- RUN_ONCE marker: **ABSENT**
- immutable `LEVERAGE-0040` result: **ABSENT**
- 1.10 / 1.20 / 1.30 candidate observation: **NONE**

The pause is intentional. Repository hygiene was completed by PR #91; **that completion does not automatically resume research**.

---

## Frozen product / strategy boundaries

Unless a later approved decision explicitly changes them, these are the current constraints:

- directional target assets: **BTC / ETH / SOL / BNB**;
- XRP: **feature-only** where required by the frozen BRRK regime model; never a target/routing asset;
- primary venue: **Hyperliquid**;
- strategy cadence: **daily**;
- canonical daily boundary: **00:00 UTC**;
- intraday automation: **risk reduction only**;
- FLAT means **zero exposure**;
- FLAT → LONG / SHORT requires human approval;
- master-wallet key / withdrawal authority is forbidden;
- production gross >1 remains forbidden;
- `production_authorized_components = []`.

Canonical directional research target remains **BRRK-0011**.

---

## What has been completed

### Phase 0 — canonical truth and governance

Established machine-readable product/config authority, decision registry, handoff/governance rules, CI baseline, and a strict distinction between:

`IMPLEMENTED → TESTED → CI VERIFIED → MERGED → PRODUCTION AUTHORIZED`

A merged component is **not** automatically production-authorized.

### Phase 1 — execution correctness

Completed the execution-integrity chain, including:

- deterministic order identity;
- persistent order ledger;
- partial-fill correctness;
- reversal safety;
- precision / exchange metadata handling;
- post-submit reconciliation;
- restart recovery;
- kill / emergency paths.

The execution layer is built to fail closed rather than silently infer exchange state.

### Phase 2 — instrument and routing evidence

Completed:

- canonical instrument registry;
- validated spot identities;
- BNB perp-only default under the verified evidence set;
- reproducible spot-vs-perp cost model;
- live L2 measurement correction;
- route decision logic and point-in-time capacity evidence.

Important: route/depth snapshots are execution evidence, **not historical point-in-time liquidity for every backtest date**.

### Phase 3 — canonical strategy pipeline

Completed and merged:

1. **P3.1 data contract**
   - target assets BTC/ETH/SOL/BNB;
   - XRP restored as frozen feature-only input after parity review;
   - common-history / missing-data checks fail closed.
2. **P3.2 target calculation API**
   - canonical live target engine separated from the old generic model module;
   - independent research/live multi-date parity;
   - committed historical golden vectors.
3. **P3.3 rebalance / turnover controls**
   - 5% L1 economic rebalance semantics.
4. **P3.4 contribution handling**
   - contributions handled without silently changing strategy authority.

Phase 3 is the first complete research-to-live target pipeline.

### Phase 4 prerequisites completed so far

Completed before any >1 production authorization:

- corrected P4.1 defensive scaler strictly bounded to `[0,1]`;
- `LEVERAGE-0039` stopped **before run** and must not be reused;
- new `LEVERAGE-0040` preregistration;
- corrected two-layer leverage architecture;
- cap=1 historical parity;
- Hyperliquid margin snapshot / hash;
- standard cross-margin liquidation-distance model;
- frozen pre-result multiplier policy:

```text
leverage_multiplier = 1 + (candidate_cap - 1) × defensive_scale
candidate caps = 1.00 / 1.10 / 1.20 / 1.30
```

No >1 candidate has yet been executed under `LEVERAGE-0040`.

### Repository hygiene

PR #91 completed a repository-wide cleanup without changing strategy economics:

- remote branch inventory reduced from **96** to the active maintenance/research set, with every retired unique branch audited before deletion;
- stale root README replaced with this current project map;
- `CURRENT_STATE.md` and `NEXT_STEPS.md` reset to actual project state;
- `docs/README.md` added as the documentation/evidence index;
- P3.1 registry prose aligned with merged XRP feature-only parity correction;
- temporary cleanup workflows removed before merge;
- historical research results and dated audits retained as evidence.

See `docs/REPOSITORY_HYGIENE_2026-08-07.md`.

---

## Research decisions that matter now

### Accepted / canonical

- **BRRK-0011** — frozen directional research target.
- corrected defensive risk measurement / scaler — accepted for P4 base layer.
- Phase 3 live target/rebalance pipeline — merged and parity-tested.

### Shadow / diagnostic only

- **EXPOSURE-SMOOTH-0038** — mechanism validated, but **NOT PROMOTED**; registry remains shadow-only.
- PIT dispersion work — useful broad-risk evidence, not a replacement production target authority.

### Rejected / stopped / superseded

The repository has tested several alternatives that did not earn promotion, including:

- PIT dynamic-alpha variants;
- TSMOM line;
- carry / funding-alpha stack as a standalone promotion path;
- ASYM extra-exposure variants as a promoted directional mechanism;
- `LEVERAGE-0039` — stopped pre-run and invalid for reuse.

Historical result files remain under `research/results/`. Their existence does not mean the strategy was promoted.

---

## Problems found during implementation

The project preserves corrections instead of hiding them.

### 1. Documentation and branch sprawl

Before the 2026-08-07 hygiene pass:

- remote branches: **96**;
- README and handoff docs described older project stages;
- many merged/abandoned branches remained visible and competed with `main` as apparent authority.

PR #91 normalized the repository and documented a branch-retirement policy. Historical evidence remains available even when obsolete remote refs are removed.

### 2. PR #73 governance evidence gap

PR #73 was manually merged. Its merge is real, but a final-head green governance run was not recorded before that merge.

Therefore its status must remain:

- MERGED: **YES**
- CI VERIFIED: **NO / NOT RECORDED**

Later work must not retroactively rewrite this history.

### 3. P3.1 feature-input parity defect

The first P3.1 contract exposed only four target assets, but frozen BRRK regime features also require XRPUSDT as a feature-only price input.

PR #74 corrected this without adding XRP to targets or routing. PR #91 later corrected the stale descriptive row in `decision_registry.json` so machine-readable prose now matches that merged fact.

### 4. P4.4 preflight wiring defects

Before any cap>1 result was observed, fail-closed preflight found:

- `PREFLIGHT-RAW-TARGET-001` — independently banded V1/BRRK holdings cannot be divided to recover raw defensive scale;
- `PREFLIGHT-SESSION-TIMING-002` — first BRRK decision `2022-12-09` must map to first evaluation return session `2022-12-10`.

The corrected R1 preflight rebuilds raw V1/BRRK authority from frozen source and explicitly exits before cap>1 evaluation.

These were implementation corrections, **not result-driven parameter tuning**.

---

## What happens next

**Current action: STOP. Research remains paused.**

Repository hygiene is complete. There is deliberately no automatic next implementation/research action.

Only after an explicit resume instruction:

```text
re-fetch live main / #90 / marker / result state
→ refresh #90 from then-current main
→ rerun all applicable pre-result CI / parity / governance
→ re-confirm marker and immutable result are still absent
→ only then reconsider the one-time RUN_ONCE boundary
→ if executed, validate immutable LEVERAGE-0040 result
→ P4.5 select/fail decision with no post-result retuning
→ P4.6 separate production-authorization gate
```

P5 remains blocked until the leverage phase is resolved through its proper gates.

---

## Source-of-truth reading order

Do **not** infer current state from an arbitrary dated report. Read in this order:

1. [`README.md`](README.md) — short project map;
2. [`docs/CURRENT_STATE.md`](docs/CURRENT_STATE.md) — authoritative current snapshot;
3. [`docs/NEXT_STEPS.md`](docs/NEXT_STEPS.md) — unique dependency order / pause rule;
4. [`docs/MASTER_PLAN_2026-08-05.md`](docs/MASTER_PLAN_2026-08-05.md) — frozen architecture/product intent;
5. [`docs/IMPLEMENTATION_ROADMAP_2026-08-05.md`](docs/IMPLEMENTATION_ROADMAP_2026-08-05.md) — phase definitions and acceptance criteria;
6. [`config/decision_registry.json`](config/decision_registry.json) — machine-readable decisions;
7. [`docs/README.md`](docs/README.md) — documentation/evidence index.

If a dated historical document conflicts with `CURRENT_STATE.md`, the dated document is an evidence snapshot, not current authority.

---

## Repository map

```text
config/                 canonical product / instrument / decision configuration
execution/              live execution package and tests
research/               research implementations and preregistrations
research/results/       persisted research evidence and immutable outputs
docs/                   governance, architecture, phase docs, audits, handoffs
.github/workflows/       CI / evidence / governance workflows
```

Detailed historical metrics are intentionally kept in `research/results/` rather than duplicated into the root README.

---

## Production status

Current production authorization:

```text
production_authorized_components = []
```

No research result, merged PR, successful backtest, or green CI run should be interpreted as permission to deploy capital unless the explicit production gate changes that registry state.
