# P5.3 V2 — Market State / Risk Permission Architecture Preregistration

Status: **FROZEN BEFORE V2 STATE-PATH EVALUATION**  
Contract: `P5.3-MARKET-STATE-PERMISSION-SEPARATION-V2`  
Base main: `5b0cac61a45c13d28680e641dd434db4d9a6a2db`

## Objective

P5.3 V1 produced immutable negative evidence: every frozen profile generated a false hard `FLAT` on `2021-02-23` inside a frozen high-volatility non-top control. V1 then made the market-state variable itself absorbing, which erased the ability to evaluate later market regimes.

V2 is a **new architecture-isolation study**, not a V1 rescue. It separates:

```text
MARKET_STATE
  what the current frozen market evidence says

RISK_PERMISSION_LOCK
  whether an implemented system is operationally allowed to re-add directional risk
```

The V1 false raw FLAT remains evidence and must reproduce exactly. V2 changes no signal rule to make it disappear.

## Immutable dependencies

V2 is bound to:

- P5.1 taxonomy `P5.1-EVENT-TAXONOMY-V1`;
- P5.2 immutable feature evidence summary SHA256 `3f6dc3c512d22ac8f71d43ed155f2602cd40d5caf3d617c0e130e170727e0627`;
- V1 state-model contract blob `400ec97f8a0e522c5776ce1f6a98fc6d7e069267`;
- V1 state-path evidence contract blob `2c3f5a200c1c1a1ddad2d93ddd9f455e5a610efd`;
- V1 immutable result commit `7703b3ffec906a9d2ea58b33ee7feea5cd2f0a89`;
- V1 immutable summary SHA256 `a2e5be8d605af5a2c8206235402fe3a66b08fd994eaa8a71e84cfb1e3cbfed8f`.

V1 remains `COMPLETE / IMMUTABLE / NO_PROMOTION / ARCHITECTURE_FAIL` and is never modified or rerun.

## What stays exactly unchanged

The first V2 study preserves the complete V1 signal layer:

- runtime feature inputs;
- evidence atoms;
- raw candidate-state priority;
- causal trailing-percentile normalization;
- EARLY / BALANCED / CONSERVATIVE threshold values;
- escalation persistence values;
- de-escalation clear-period values;
- missing-data fail-closed semantics;
- P5.1 event anchors and five evaluation buckets.

Exact profiles remain:

| Profile | Moderate high/low | Strong high/low | Escalation | Clear |
| --- | --- | --- | ---: | ---: |
| EARLY | 0.65 / 0.35 | 0.80 / 0.20 | 2d | 5d |
| BALANCED | 0.70 / 0.30 | 0.85 / 0.15 | 3d | 5d |
| CONSERVATIVE | 0.75 / 0.25 | 0.90 / 0.10 | 3d | 7d |

Before any V2 historical result is valid, normalized feature values, evidence atoms and raw candidate states must exactly reproduce immutable V1.

## MARKET_STATE

The V2 market-state vocabulary and severity order remain identical to V1:

```text
NORMAL_BULL
BTC_LEADERSHIP_MATURING
LATE_BULL_ROTATION
EXHAUSTION_WATCH
DE_RISK_1
DE_RISK_2
FLAT
```

`FLAT` remains the most severe **market classification**, but it is no longer an absorbing market-state history.

All V1 transition mechanics remain unchanged except one architecture condition:

> V1 excluded `current_state == FLAT` from ordinary de-escalation. V2 removes only that exclusion for `MARKET_STATE`.

Therefore, when `MARKET_STATE=FLAT`:

1. raw `FLAT` continues to hold FLAT and resets any recovery counter;
2. if the fully evaluated raw candidate is below FLAT for the profile's existing `deescalation_clear_days`, MARKET_STATE moves exactly one severity step to `DE_RISK_2`;
3. counters reset after that transition;
4. every further lower state requires a fresh full clear period;
5. no profile gets a new recovery threshold or special post-FLAT parameter.

A fully evaluated raw `FLAT` still escalates immediately exactly as in V1. The false `2021-02-23` raw FLAT must therefore remain present.

## RISK_PERMISSION_LOCK

Operational re-risk permission is a separate layer:

```text
UNLOCKED
LOCKED_PENDING_HUMAN_APPROVAL
```

Rules:

- `MARKET_STATE` has **zero authority** to unlock risk permission;
- automatic unlock is forbidden;
- only explicit human approval may clear a lock;
- a later MARKET_STATE recovery does not authorize a live trade or risk increase.

P5.3 V2 does **not** fabricate a historical permission-lock time series. P5.4 has not yet defined which market states map to actual zero directional exposure, so a historical lock path would silently assume downstream behavior that does not exist yet.

When a later integration actually maps a state to zero exposure, that operational zero-exposure action must set/retain the human-gated lock according to product policy.

## Frozen V1 failure that V2 must preserve

The immutable V1 evidence includes:

```text
false raw FLAT date     2021-02-23
event                    P5C-2021-JAN-FEB-HIGH-VOL
event class              HIGH_VOLATILITY_NON_TOP_CONTROL
near-event V1 FLAT       6 / 7 days = 85.7143%
minimum calibration N    57
```

On the false-FLAT date V1 has complete inputs and simultaneously active exhaustion, strong exhaustion, damage and strong damage.

V2 may expose subsequent market recovery; it may not call the false FLAT a success, move the control window, or tune the signal layer to eliminate it.

## Required parity before V2 interpretation

V2 implementation/evidence must prove:

- exact normalized-feature parity versus immutable V1;
- exact evidence-atom parity versus immutable V1;
- exact raw-candidate-state parity versus immutable V1;
- final MARKET_STATE parity with V1 through the first FLAT date, inclusive;
- exact reproduction of the `2021-02-23` false raw FLAT.

Any parity failure is an implementation failure, not a new research result.

## Required V2 evidence

For all three frozen profiles report:

- full daily `MARKET_STATE` path;
- V1 parity report;
- every market-state FLAT episode, duration and recovery date;
- state occupancy in every frozen P5.1 event bucket;
- first state occurrence and signed anchor offset within each bucket;
- second-wind behavior;
- non-top-control FLAT occupancy;
- terminal-event lead / near-event states;
- transition and churn counts;
- direct V1-vs-V2 state-path difference attributable only to removal of market-state absorption;
- explicit assertion that market recovery never changes operational permission.

## Architecture evaluation boundary

An architecture pass requires:

- all V1 parity gates pass;
- the false `2021-02-23` raw FLAT remains visible;
- an earlier FLAT no longer structurally destroys all later MARKET_STATE evidence;
- later frozen event windows remain classifiable;
- market-state recovery never becomes automatic operational re-risk permission.

An architecture pass does **not** mean:

- the signal layer is accepted;
- a profile is selected;
- P5.4 gross behavior is selected;
- production is authorized.

P5.4 remains **BLOCKED** until V2 evidence is completed and reviewed.

## Forbidden

- edit or rerun immutable V1;
- move P5.1 events/anchors/buckets;
- modify P5.2 evidence;
- add/delete signal features;
- change evidence atoms or raw priority;
- change percentile normalization or thresholds;
- change any profile/persistence/clear-period value;
- hide or tune away the 2021-02-23 false raw FLAT;
- let MARKET_STATE recovery unlock operational risk;
- select P5.4 multipliers;
- authorize production.

## Completion boundary

This preregistration is complete when the machine contract, dedicated tests, CI and authoritative handoff are green and merged **before any V2 historical state-path evaluation**.

The next step after prereg merge is deterministic V2 implementation with exact V1 raw/evidence parity. Historical V2 state paths are not run in the preregistration PR.
