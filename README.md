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
Phase 6 valuation contract        PHASE6-LIVE-VALUATION-V1 / MERGED #134
Phase 6 identity-binding rules    PHASE6-LIVE-ACCOUNT-IDENTITY-V1 / CANDIDATE / ADDRESS UNBOUND
Phase 6 pre-arm state             3/4 FROZEN / ACCOUNT IDENTITY REMAINS UNRESOLVED
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
- no production/signature/submission/withdrawal/external-transfer authority;
- no first real short authorization.

## Research closeout

`LEVERAGE-0040` / `0041` remain immutable `NO_PROMOTION`. P5.5 remains immutable `NO_PROMOTION_FAIL_STOP`. `STABLECOIN-LIQUIDITY-0001` remains terminal `FAIL_NO_INCREMENTAL_INFORMATION / NO_PROMOTION`, with no same-ID rescue/rerun, Stage-2 eligibility, edge admission or portfolio integration.

## Phase 6 preactivation

The canonical Phase-6 shadow implementation is zero-authority. Real elapsed evidence still requires >=14 elapsed days, >=10 genuine scheduled decisions, >=1 emergency drill and zero frozen quality failures.

The durable evidence backend is frozen to GitHub Actions Artifact v4 with 90-day retention, `overwrite=false`, immutable artifact identity and a hash-bound receipt; its existence creates zero elapsed credit.

`PHASE6-LIVE-VALUATION-V1` merged in PR #134 and remains limited to explicit Hyperliquid Standard mode (`userAbstraction=disabled`). It maps verified UBTC/UETH/USOL spot holdings plus signed BTC/ETH/SOL/BNB perp notionals into the existing P3.3 current-position/equity inputs. Unsupported modes/assets fail closed; BNB spot remains forbidden.

The current identity-rule candidate `PHASE6-LIVE-ACCOUNT-IDENTITY-V1` freezes how a future public address may be bound, but does **not** bind an address now:

```text
account_address                     null
identity_frozen                     false
accepted userRole                   user / subAccount
rejected userRole                   agent / vault / missing
required userAbstraction            disabled
private-key discovery/derivation    forbidden
collector_armed                     false
elapsed_evidence_credit_authorized  false
```

A subaccount may be observed directly, but its returned master address must be preserved as evidence and must not silently replace the queried subaccount identity. Agent/API-wallet addresses are never valid observation identities.

Current pre-arm state remains:

```text
observation account identity          UNRESOLVED
current-position/equity valuation     FROZEN / MERGED #134
durable evidence backend              FROZEN / MERGED #133
schedule + duplicate-credit rule      FROZEN
collector_armed                       false
elapsed_evidence_credit_authorized    false
```

## Exact next dependency

After the identity-rule candidate passes final CI and merges, obtain one exact verified **public read-only Hyperliquid master/subaccount address**. Validate its `userRole` and require `userAbstraction=disabled`; persist non-secret provenance and raw-response digests before `identity_frozen` may become true.

Do not invent an address, use an agent/API wallet, or derive an address from a private key merely to close the gate. If the real account is incompatible, remain blocked rather than broadening the contract post-observation.

Even 4/4 dependencies do not arm the system automatically. A separate prospective arm change is required, and the first eligible credited decision remains the first `00:00 UTC` strictly after that arm commit.

Phase 7 remains `MONITOR_ONLY`; Phase 8 remains trigger-absent/not-run; all production/signature/submission authority remains false.

After genuine Phase-6 collection becomes operational, resume the infrastructure roadmap: formal research lifecycle/state-machine enforcement, then Research Queue / trial-overlap accounting.

## Source-of-truth order

1. `README.md`
2. `docs/CURRENT_STATE.md`
3. `docs/NEXT_STEPS.md`
4. governance / decision / research / dataset / edge registries
5. Phase 6/7/8 machine contracts
6. immutable research contracts/results