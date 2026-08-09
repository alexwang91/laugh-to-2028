# Phase 6 Address Binding Request

**Production authorization: NO_CHANGE**

This document originally requested only a PUBLIC READ-ONLY Hyperliquid master/subaccount address for identity verification. That request is now fulfilled by the explicit owner-supplied public master identity frozen in `research/governance/phase6_live_account_identity_contract.json`.

Do NOT provide:
- private keys
- seed phrases
- API private keys
- signing credentials

Providing or binding a public address does not authorize signing, order submission, transfer, withdrawal, production activation, or live trading.

Status: `FULFILLED / IDENTITY_BOUND / DEPENDENCIES_4_OF_4 / COLLECTOR_NOT_ARMED`

## 1. Completed identity input

The completed identity-binding step used one **exact public Hyperliquid master account address** supplied explicitly by the owner.

The bound identity satisfies the frozen requirements:

- `0x` prefix followed by exactly 40 hexadecimal characters;
- actual master account whose live state will be observed;
- not an agent/API-wallet address;
- not a vault address;
- `userRole = user`;
- `userAbstraction = disabled`;
- Standard-account semantics frozen by `PHASE6-LIVE-VALUATION-V1`.

The exact public address, non-secret provenance, parsed read-only responses, verification timestamp and raw-response SHA256 digests are persisted in `research/governance/phase6_live_account_identity_contract.json`.

For a future replacement with a subaccount, the subaccount itself would remain the observed identity. The returned master address would be evidence only; the implementation must not silently substitute the master for the observed subaccount.

Agent wallets remain rejected because Hyperliquid account-data queries must use the actual master/subaccount identity. Vaults are a different account surface. Unsupported abstraction modes remain outside the frozen valuation contract. Silent substitution remains prohibited because it would change the identity being measured after observation.

## 2. Public read-only self-check

Hyperliquid's official Info endpoint documentation defines public `POST https://api.hyperliquid.xyz/info` queries for account role and abstraction state:

Official API documentation:
`https://hyperliquid.gitbook.io/hyperliquid-docs/for-developers/api/info-endpoint`

Role query:

```json
{"type":"userRole","user":"<PUBLIC_ADDRESS>"}
```

Accepted role:

```json
{"role":"user"}
```

or a valid `subAccount` role response with master evidence.

Abstraction query:

```json
{"type":"userAbstraction","user":"<PUBLIC_ADDRESS>"}
```

Required abstraction:

```json
"disabled"
```

The completed owner-browser read-only checks returned `userRole=user` and `userAbstraction=disabled` for the bound identity.

These `/info` reads require no private key, wallet signature, API secret, signing credential, order authorization, transfer authority or withdrawal authority.

Hyperliquid's account-abstraction documentation distinguishes Standard, Unified Account and Portfolio Margin modes. The frozen Phase-6 valuation contract accepts only Standard semantics represented by `userAbstraction=disabled`.

If any future replacement identity observes any of the following, the V1 outcome remains `BLOCKED_INCOMPATIBLE`:

- `agent`;
- `vault`;
- `missing`;
- `default`;
- `unifiedAccount`;
- `portfolioMargin`;
- `dexAbstraction`;
- any other unsupported or absent value.

The contract must not be broadened after observing an incompatible account merely to make that account pass.

## 3. Reconciled historical probe evidence

A prior prospective read-only probe in closed, unmerged PR #138 demonstrated a valid `user` role but returned `userAbstraction="default"`.

That historical evidence established only:

- the probed identity had an acceptable role;
- it did **not** satisfy `PHASE6-LIVE-ACCOUNT-IDENTITY-V1`;
- no identity was bound from that probe;
- no dependency was credited;
- no elapsed clock started.

That historical address remains confined to its original evidence/discussion context and was not reused for the current binding.

## 4. Binding-success path — completed through the mandatory STOP

The frozen sequence is:

```text
valid explicit public master/subaccount identity
-> query userRole and userAbstraction
-> require userRole=user OR subAccount
-> require userAbstraction=disabled
-> persist non-secret provenance + raw response digests
-> freeze exact identity
-> Phase 6 dependencies = 4/4
-> STOP
```

The current repository state has completed exactly those steps and stops there.

The remaining future sequence is separate and not authorized by identity binding:

```text
separate prospective ARM change
-> collector armed
-> schedule configured
-> elapsed-evidence credit authorized
-> first eligible 00:00 UTC decision strictly after ARM commit
-> genuine future-only shadow evidence
-> Phase 6 closeout
-> Phase 7 launch eligibility assessment
```

Hard distinctions:

```text
4/4 != CLOCK STARTED
IDENTITY BOUND != ARM
ARM != HISTORICAL CREDIT
PHASE6 PASS != PHASE7 ACTIVE
```

Binding is therefore a readiness dependency, not production activation.

## 5. Frozen Phase 6 shadow acceptance gate

Authority: `research/governance/phase6_live_observation_gate.json`, gate `PHASE6-LIVE-OBSERVATION-PREACTIVATION-V1`.

The frozen requirements are:

| Requirement | V1 threshold |
|---|---:|
| minimum elapsed calendar days | 14 |
| minimum scheduled decisions | 10 |
| minimum emergency drills | 1 |
| critical reconciliation errors | 0 |
| unexplained target drift | 0 |
| schedule failures | 0 |

The first eligible scheduled decision is the first canonical `00:00 UTC` decision **strictly after** the future ARM commit timestamp.

The following create **no scheduled-decision credit**:

- historical backfill;
- historical replay;
- CI replay;
- workflow rerun;
- duplicate decision timestamp;
- manual dispatch.

A manual emergency drill may count only toward the emergency-drill requirement when it satisfies the frozen evidence rules; it does not become a scheduled decision.

### Theoretical earliest elapsed-time close

The elapsed clock starts at the **first eligible scheduled 00:00 UTC timestamp after ARM**, not at address submission, identity binding, dependency 4/4, PR opening or identity-binding PR merge.

Therefore no already-past time receives credit. After a separately authorized ARM, the time condition cannot pass until 14 full calendar days after the first eligible scheduled timestamp, with at least 10 genuine scheduled decisions and all other frozen gates satisfied.

## 6. Explicit human gates that remain

Authoritative contracts and roadmap retain these human/owner boundaries:

1. **ARM transition:** identity binding is complete, but a separate prospective ARM change is still required. Identity binding itself cannot arm the collector.
2. **Phase 7 launch approval:** the Phase-7 launch checklist requires explicit user approval before the limited-capital live long program can start.
3. **`MONITOR_ONLY -> ACTIVE`:** explicit human approval required.
4. **`FLAT -> LONG`:** explicit human approval required.
5. **`FLAT -> SHORT`:** explicit human approval required.
6. **First short exposure after a confirmed bear transition:** `SHORT_READY` is insufficient; the first short exposure of a new bear phase requires explicit user approval.

The identity-owner action is complete for the currently frozen public identity. Any future identity replacement would require a new explicit owner action.

## 7. Boundary of the completed binding

The identity binding does:

- freeze the exact owner-supplied public observation identity;
- persist non-secret provenance;
- persist the verified role/mode response data and raw-response SHA256 digests;
- complete the Phase-6 pre-arm dependencies to 4/4.

The identity binding does **not**:

- arm the collector;
- configure the schedule;
- start or backfill the elapsed clock;
- authorize signing, orders, transfers, withdrawals, production activation or live trading.

The exact next operational step is a separate future ARM decision.
