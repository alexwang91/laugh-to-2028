# Phase 6 Address Binding Request

**Production authorization: NO_CHANGE**

This document originally requested a PUBLIC READ-ONLY Hyperliquid master/subaccount identity. That request is fulfilled, the compatible identity is frozen, and the owner has subsequently authorized the separate Phase-6 ARM transition.

Do NOT provide:
- private keys
- seed phrases
- API private keys
- signing credentials

Neither identity binding nor Phase-6 ARM authorizes signing, order submission, transfer, withdrawal, production activation, or live trading.

Status: `FULFILLED / IDENTITY_BOUND / DEPENDENCIES_4_OF_4 / ARM_AUTHORIZED / FUTURE_ONLY_OBSERVATION`

## 1. Completed identity binding

The frozen identity is the explicit public Hyperliquid master account supplied by the owner and recorded in `research/governance/phase6_live_account_identity_contract.json`.

It satisfies:

```text
address format       0x + 40 hexadecimal characters
userRole             user
userAbstraction      disabled
identity_frozen      true
agent/API wallet     no
vault                no
```

The contract persists only the public address, non-secret provenance, parsed read-only responses, verification timestamp and SHA256 digests of the exact raw responses. No secret or signing material is stored.

Any future replacement identity remains a separate owner action and must satisfy the same fail-closed rules. A subaccount must be observed as itself; the implementation must not silently substitute its master account.

## 2. Public read-only identity checks

Hyperliquid's official Info endpoint supports public `POST https://api.hyperliquid.xyz/info` reads.

Role query:

```json
{"type":"userRole","user":"<PUBLIC_ADDRESS>"}
```

Accepted role is `user` or a valid `subAccount` response with master evidence.

Abstraction query:

```json
{"type":"userAbstraction","user":"<PUBLIC_ADDRESS>"}
```

Required value:

```json
"disabled"
```

The bound account passed these checks. `agent`, `vault`, `missing`, `default`, `unifiedAccount`, `portfolioMargin`, `dexAbstraction`, or any unsupported/absent value remains incompatible with Phase-6 V1.

## 3. Historical incompatible probe

Closed, unmerged PR #138 previously observed a different identity with `userRole=user` but `userAbstraction=default`. It created no binding, dependency credit, ARM authority or elapsed evidence. That historical address was not reused for the current binding.

## 4. Completed binding and ARM sequence

The project has now completed:

```text
explicit compatible public identity
-> userRole / userAbstraction verification
-> non-secret provenance + raw-response digests persisted
-> identity frozen
-> Phase 6 dependencies = 4/4
-> mandatory STOP
-> separate owner ARM authorization
-> real non-crediting external preflight
-> prospective ARM marker
-> future-only collector/schedule activation package
```

Real preflight workflow run `31316348226` passed with:

```text
account_equity_usd  53.788314
shadow_status       SHADOW_COMPUTED_NO_AUTHORITY
shadow_alerts       []
scheduled credit    false
```

The prospective ARM marker is:

```text
cbd58adb05187651ca72d67900a0ccbbd3e83b1e
```

Once the activation PR is merged to the default branch, the collector is scheduled daily at `00:00 UTC`. Pull-request preflight remains non-crediting.

Hard distinctions remain:

```text
ARM != HISTORICAL CREDIT
PR PREFLIGHT != SCHEDULED DECISION
WALL CLOCK != ACCEPTANCE WITHOUT DURABLE EVIDENCE
PHASE6 PASS != PHASE7 ACTIVE
```

## 5. Frozen Phase-6 acceptance gate

Authority: `research/governance/phase6_live_observation_gate.json`.

| Requirement | V1 threshold |
|---|---:|
| minimum elapsed calendar days | 14 |
| minimum scheduled decisions | 10 |
| minimum emergency drills | 1 |
| critical reconciliation errors | 0 |
| unexplained target drift | 0 |
| schedule failures | 0 |

The first eligible scheduled decision is the first genuine canonical `00:00 UTC` schedule event strictly after the ARM-marker commit timestamp and after the activation exists on `main`.

The ARM marker was created on 2026-08-09, so the rule-derived first eligible timestamp is `2026-08-10T00:00:00Z`; it counts only if the activation is already on `main` for that schedule and both required artifacts persist. Otherwise the next actual post-merge schedule is the first credit candidate. No missed timestamp may be backfilled.

The following create no scheduled-decision credit:

- historical backfill;
- historical replay;
- CI replay;
- pull-request preflight;
- workflow rerun;
- duplicate decision timestamp;
- manual dispatch.

A manual emergency drill may count only toward the drill requirement when it satisfies the frozen evidence contract; it never becomes a scheduled decision.

## 6. Evidence persistence

Each creditable scheduled observation requires:

1. raw public/read-only market, account and route bytes preserved before parsing;
2. input-provenance SHA256 and shadow-record SHA256;
3. a create-only GitHub Actions evidence artifact with 90-day retention and overwrite disabled;
4. a separate hash-bound receipt artifact created only after the evidence upload succeeds.

Failure of either required artifact upload means no credit.

## 7. Human gates that remain

The identity and Phase-6 ARM owner actions are complete for this zero-authority observation phase.

Separate explicit owner approval is still required for:

1. Phase-7 launch;
2. `MONITOR_ONLY -> ACTIVE`;
3. `FLAT -> LONG`;
4. `FLAT -> SHORT`;
5. first short exposure after a confirmed new bear phase.

One evidenced manual emergency drill is operationally required before Phase-6 closeout, but it grants no production authority.

## 8. Security / production boundary

Phase-6 observation does not:

- import or derive private keys;
- sign orders;
- submit orders;
- transfer or withdraw assets;
- activate production;
- change strategy mathematics or gross cap;
- authorize Phase 7.

Production remains `NO_CHANGE` with gross cap `1.0`, no authorized production components, and signing/order authority false.
