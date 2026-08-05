# BRRK Project Governance — 2026-08-05

This document defines how research, implementation, review and production releases are controlled.

It is subordinate to `docs/MASTER_PLAN_2026-08-05.md` and is intended to prevent the repository from drifting back into disconnected experiments or live code changes without evidence.

---

## 1. Core principle

The repository has two different activities:

```text
RESEARCH / CANDIDATE DEVELOPMENT
PRODUCTION / ACTIVE EXECUTION
```

They must remain operationally distinct.

Research can move quickly. Production must move only through explicit gates.

---

## 2. Blue/green production model

At any time there may be:

```text
ACTIVE
CANDIDATE
```

### ACTIVE

The approved production release.

Rules:

- core strategy logic is immutable while the service runs;
- ordinary data updates and normal trading are allowed;
- no ad-hoc parameter edit to rescue current market behavior;
- emergency risk reduction is always allowed.

### CANDIDATE

The next version under research / implementation.

It may:

- use historical data;
- use live public market data;
- read the real account in shadow mode;
- produce hypothetical targets/orders;
- be modified until frozen for release.

It must not trade against the production account before explicit cutover approval.

---

## 3. Release cutover

A candidate becomes active only through a manual cutover.

Required sequence:

1. freeze candidate commit and configuration;
2. record release ID;
3. confirm required research/execution/shadow gates;
4. stop the old ACTIVE service;
5. cancel or reconcile outstanding orders as required;
6. snapshot actual account equity, positions, margin and open orders;
7. start the new release in reconciliation-first mode;
8. prohibit new risk until startup state matches the exchange;
9. enable ACTIVE trading only after reconciliation passes;
10. retain prior release for rollback.

No hot replacement of model logic in a running production process.

---

## 4. Human-control boundary

Within an already approved ACTIVE regime, normal model-driven trading is automatic.

Human approval is required for a new directional-risk cycle:

```text
FLAT -> LONG
FLAT -> SHORT
MONITOR_ONLY -> ACTIVE
first short exposure of a new bear phase
```

Automatic risk reduction never requires approval.

If the system determines that immediate risk reduction is required, it may:

- lower leverage;
- reduce exposure;
- cancel orders;
- close positions;
- enter FLAT.

---

## 5. Credential policy

Production uses a Hyperliquid trading Agent/API credential with only the permissions necessary to trade and read state.

The application must never require or persist the master wallet private key.

The application must not automate:

- withdrawals;
- transfers out;
- wallet security changes.

If any future implementation proposes these capabilities, it is outside the approved product boundary and requires a master-plan change before code work begins.

---

## 6. Research discipline

Every material new hypothesis should define:

- question;
- reason the hypothesis could work;
- canonical inputs;
- test window;
- out-of-sample/walk-forward design;
- costs;
- benchmark;
- success criteria;
- failure criteria.

When practical, preregister these before viewing final results.

### Historical failure policy

A failed strategy line remains failed on that sample.

Do not repeatedly modify:

- thresholds;
- assets;
- costs;
- holding periods;
- windows;
- leverage;

until the historical failure disappears.

A genuinely new hypothesis may be tested, but it must receive a new experiment ID and preserve the failed result.

---

## 7. Change classification

Every correction after review should be labeled as one of:

### BUG_FIX

The implementation contradicts the already-defined intended behavior.

A bug fix may correct the code without changing the hypothesis.

### MEASUREMENT_FIX

The metric, accounting, timestamp or comparison was incorrectly measured.

The old result remains preserved; the corrected result receives a new evidence record where needed.

### IMPLEMENTATION_HARDENING

No strategy economics change is intended. Examples:

- idempotency;
- retries;
- reconciliation;
- logging;
- authentication;
- order-state handling.

### NEW_HYPOTHESIS

A materially different economic idea. Requires a new research record.

### PARAMETER_CHANGE

A strategy parameter changes.

If the change is motivated by a failed historical result, treat it as a new registered experiment, not a silent fix.

---

## 8. Standard correction loop

All future tasks follow:

```text
PLAN
-> define acceptance criteria
-> IMPLEMENT
-> TEST
-> REVIEW
-> classify any failure
-> FIX or STOP
-> rerun required tests
-> record evidence
-> update roadmap status
```

Do not proceed to the dependent task while the predecessor remains ambiguous.

Possible final statuses:

```text
PASS_PRODUCTION_CANDIDATE
PASS_SHADOW_ONLY
FAIL_STOP
FAIL_FIX_IMPLEMENTATION
MEASUREMENT_INCONCLUSIVE
```

---

## 9. Pull-request expectations

A material PR should state:

1. roadmap task ID;
2. what behavior changes;
3. what behavior does not change;
4. tests/evidence;
5. risk implications;
6. production authorization status.

Suggested PR footer:

```text
Roadmap: P?.?
Change class: BUG_FIX | MEASUREMENT_FIX | IMPLEMENTATION_HARDENING | NEW_HYPOTHESIS | PARAMETER_CHANGE
Evidence status: ...
Production authorization: NO | SHADOW_ONLY | CANDIDATE
```

A merged PR does not automatically mean the feature is authorized for production trading.

---

## 10. Production release manifest

Every production release should archive:

- git commit SHA;
- config snapshot;
- strategy/model versions;
- data-source versions where relevant;
- approved leverage and risk caps;
- canonical asset/instrument registry;
- release timestamp;
- previous release ID;
- human approval record/reference;
- known limitations.

The running service should expose its release ID in logs and health/status output.

---

## 11. Audit-log requirements

For every official daily decision, persist enough information to reconstruct:

- input data timestamp;
- feature/model version;
- BRRK target weights;
- cycle state;
- target gross / leverage;
- router choice and reason;
- pre-trade account state;
- intended orders;
- actual orders and fills;
- post-trade account state;
- reconciliation result;
- exceptions / overrides.

For intraday emergency actions, additionally record the exact trigger and why the action was risk-reducing.

---

## 12. Model-state governance

The approved high-level states are:

```text
NORMAL_BULL
BTC_LEADERSHIP_MATURING
LATE_BULL_ROTATION
EXHAUSTION_WATCH
DE_RISK_1
DE_RISK_2
FLAT
MONITOR_ONLY
SHORT_READY
SHORT_ACTIVE
```

Not all states need to exist in the first production release. They become active only when the corresponding model is validated.

Until the cycle-exit program is approved, existing BRRK behavior should not pretend to generate those states.

---

## 13. Risk-limit governance

There are three distinct concepts:

### Catastrophic limit

User tolerance boundary:

```text
70% drawdown
```

It is not an optimizer target.

### Operating risk budget

Evidence-selected normal maximum risk. This may change only through a validated strategy/release change.

### Live deployment cap

An operational cap that may be stricter than research suggests.

Example:

```text
research supports gross 1.4
but live execution evidence authorizes only 1.1
```

In that case production remains at 1.1 until execution evidence justifies expansion.

---

## 14. Shadow governance

A candidate shadow process may read the same real account and market data as ACTIVE.

It must be technically incapable of signing production orders.

Shadow output should be comparable with ACTIVE by common decision timestamp.

A candidate does not graduate because its recent PnL is better. Graduation requires the predefined evidence gates.

---

## 15. Incident policy

An operational incident should first protect capital, then preserve evidence.

Priority:

```text
1. stop new risk
2. reconcile actual exchange state
3. reduce risk if necessary
4. preserve logs and external responses
5. diagnose
6. classify cause
7. fix in CANDIDATE
8. cut over only after validation
```

Do not debug a broken production strategy by live-editing it while it continues trading.

---

## 16. Plan changes

The master plan is not immutable forever, but changing it is a deliberate product decision.

A master-plan change is required when altering any of these foundational assumptions:

- long universe;
- primary venue;
- human approval boundaries;
- wallet/private-key boundary;
- recurring capital model;
- benchmark philosophy;
- catastrophic risk tolerance;
- production upgrade model;
- fixed-date versus state-based exit philosophy.

Routine implementation detail does not require changing the master plan.

---

## 17. Branch hygiene

Historical experiment branches are not a source of production truth. Main plus the current candidate PR should contain all authoritative documentation and code needed for continuation.

After a branch is merged and its unique evidence is archived on main, it should be deleted unless there is a specific reason to retain it.

The repository previously accumulated many historical remote branches. Their unique evidence was reviewed separately; future work should not recreate that accumulation pattern.

---

## 18. Current program status after this planning PR

Once the planning PR is merged:

```text
MASTER PLAN: established
ROADMAP: established
NEXT AUTHORIZED TASK: P0.1 / P0.2
PRODUCTION STRATEGY CHANGE: none from this planning PR
LIVE CAPITAL AUTHORIZATION: none from this planning PR
```

The first implementation PR after this plan should create the canonical product config and decision registry, then begin execution-state hardening.