# Phase 6 Address Binding Request

**Production authorization: NO_CHANGE**

This document requests only a PUBLIC READ-ONLY Hyperliquid
master/subaccount address for identity verification.

Do NOT provide:
- private keys
- seed phrases
- API private keys
- signing credentials

Providing a public address does not authorize signing,
order submission, transfer, withdrawal, production activation,
or live trading.

Status: `READINESS_ONLY / IDENTITY_UNBOUND / COLLECTOR_NOT_ARMED`

## 1. Exact input required in the future

The identity-binding step requires one **exact public Hyperliquid master or subaccount address**.

The address must:

- use the `0x` prefix followed by exactly 40 hexadecimal characters;
- identify the actual master/subaccount whose live state will be observed;
- not be an agent/API-wallet address;
- not be a vault address;
- return `userRole` equal to `user` or `subAccount`;
- return `userAbstraction` equal to `disabled`;
- preserve the Standard-account semantics frozen by `PHASE6-LIVE-VALUATION-V1`.

For a subaccount, the subaccount itself remains the observed identity. The returned master address is evidence only; the implementation must not silently substitute the master for the observed subaccount.

Agent wallets are rejected because Hyperliquid account-data queries must use the actual master/subaccount identity. Vaults are a different account surface. Unsupported abstraction modes are outside the frozen valuation contract. Silent substitution is prohibited because it would change the identity being measured after observation.

## 2. Public read-only self-check

Hyperliquid's official Info endpoint documentation defines public `POST https://api.hyperliquid.xyz/info` queries for account role and abstraction state:

Official API documentation:
`https://hyperliquid.gitbook.io/hyperliquid-docs/for-developers/api/info-endpoint`

Role query:

```json
{"type":"userRole","user":"<PUBLIC_ADDRESS>"}
```

Expected role:

```json
{"role":"user"}
```

or a `subAccount` role response.

Abstraction query:

```json
{"type":"userAbstraction","user":"<PUBLIC_ADDRESS>"}
```

Expected abstraction:

```json
"disabled"
```

These `/info` reads require no private key, wallet signature, API secret, signing credential, order authorization, transfer authority or withdrawal authority.

Hyperliquid's current account-abstraction documentation distinguishes Standard, Unified Account and Portfolio Margin modes. The frozen Phase-6 valuation contract accepts only Standard semantics represented by `userAbstraction=disabled`.

If the observed role or abstraction is any of the following, the V1 outcome is `BLOCKED_INCOMPATIBLE`:

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

That evidence establishes only:

- the probed identity had an acceptable role;
- it did **not** satisfy `PHASE6-LIVE-ACCOUNT-IDENTITY-V1`;
- no identity was bound;
- `identity_frozen` remained false;
- Phase 6 remained 3/4;
- no collector was armed;
- no schedule was configured;
- no elapsed evidence credit was created.

This document intentionally does not reproduce the probed public address. The historical address remains confined to its original evidence/discussion context.

## 4. Binding-success path

A future compatible binding follows this frozen sequence:

```text
valid explicit public master/subaccount identity
-> query userRole and userAbstraction
-> require userRole=user OR subAccount
-> require userAbstraction=disabled
-> persist non-secret provenance + raw response digests
-> freeze exact identity
-> Phase 6 dependencies = 4/4
-> STOP
-> separate prospective ARM change
-> collector armed
-> schedule configured
-> first eligible 00:00 UTC decision strictly after arm commit
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

The first eligible scheduled decision is the first canonical `00:00 UTC` decision **strictly after** the ARM commit timestamp.

The following create **no scheduled-decision credit**:

- historical backfill;
- historical replay;
- CI replay;
- workflow rerun;
- duplicate decision timestamp;
- manual dispatch.

A manual emergency drill may count only toward the emergency-drill requirement when it satisfies the frozen evidence rules; it does not become a scheduled decision.

### Theoretical earliest elapsed-time close

The elapsed clock starts at the **first eligible scheduled 00:00 UTC timestamp**, not at address submission, identity binding, dependency 4/4, PR opening, PR merge, or ARM commit time.

Therefore the time condition cannot pass until **14 full calendar days after that first eligible scheduled timestamp**. At least 10 genuine scheduled decisions and the other zero-error / drill gates must also be satisfied. No already-past time receives credit.

## 6. Explicit human gates that remain

Authoritative contracts and roadmap retain these human/owner boundaries:

1. **Identity owner action:** an explicit compatible public master/subaccount identity must be supplied; guessing, discovery from private material, and silent substitution are forbidden.
2. **ARM transition:** after identity binding reaches 4/4, work must stop for a separate prospective ARM change. Identity binding itself cannot arm the collector.
3. **Phase 7 launch approval:** the Phase-7 launch checklist requires explicit user approval before the limited-capital live long program can start.
4. **`MONITOR_ONLY -> ACTIVE`:** explicit human approval required.
5. **`FLAT -> LONG`:** explicit human approval required.
6. **`FLAT -> SHORT`:** explicit human approval required.
7. **First short exposure after a confirmed bear transition:** `SHORT_READY` is insufficient; the first short exposure of a new bear phase requires explicit user approval.

## 7. Boundary of this readiness document

This document does not:

- bind or re-probe any account;
- write a real account address to main;
- freeze an identity;
- arm the collector;
- configure the schedule;
- start or backfill the elapsed clock;
- authorize signing, orders, transfers, withdrawals, production activation or live trading.

The next compatible identity binding remains a separate future action.
