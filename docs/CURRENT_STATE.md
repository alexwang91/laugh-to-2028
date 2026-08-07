# BRRK Current State

Last updated: 2026-08-07
Status: **authoritative current-state handoff**

## Executive state

```text
Phase 0                         COMPLETE / MERGED
Phase 1                         COMPLETE / MERGED
Phase 2                         COMPLETE / MERGED
Phase 3                         COMPLETE / MERGED
P4.1 defensive scaler          COMPLETE / MERGED / frozen [0,1]
LEVERAGE-0040 / 0041           COMPLETE / IMMUTABLE / NO_PROMOTION
Phase 4 leverage research      FAIL_STOP / no eligible >1 candidate
P4.6 production leverage gate  NOT ENTERED / BLOCKED
P5.1 event taxonomy            COMPLETE / MERGED / FROZEN
P5.2 feature families          COMPLETE / IMMUTABLE EVIDENCE / DESCRIPTIVE CLOSEOUT
P5.3 V1 state model            COMPLETE / IMMUTABLE / NO_PROMOTION / ARCHITECTURE_FAIL
P5.3 V2 architecture           PREREGISTERED / FROZEN BEFORE V2 STATE PATHS
P5.3 V2 implementation         NOT STARTED
P5.4 behavior mapping          BLOCKED PENDING V2 CLOSEOUT
P5.5-P5.6                      NOT STARTED
Phase 6 integrated shadow      NOT STARTED
Phase 7 limited live long      NOT STARTED / explicit approval required
Phase 8 bear-short research    NOT STARTED
production authorization       NONE
```

`production_authorized_components = []`

Current production gross cap remains `1.0`.

## Immutable upstream truth

### P5.1

Contract: `P5.1-EVENT-TAXONOMY-V1`  
Taxonomy blob SHA: `73d010666fbfd957ec15214a00883a90a8adba5a`

Events, anchors and five evaluation buckets remain frozen. Only 2021 November is explicitly terminal.

### P5.2

Contract: `P5.2-FEATURE-FAMILIES-V1`  
Immutable result commit: `61d585afb64afbe3ead6422e7e62cde6c59fad40`  
Immutable summary SHA256: `3f6dc3c512d22ac8f71d43ed155f2602cd40d5caf3d617c0e130e170727e0627`

P5.2 remains descriptive only. Six desired data families remain `DATA_SOURCE_PENDING`; no favorable proxy substitution is allowed.

## P5.3 V1 immutable negative result

State-model contract: `P5.3-STATE-MODEL-STRUCTURE-V1`  
Evidence contract: `P5.3-STATE-PATH-EVIDENCE-V1`  
Result commit: `7703b3ffec906a9d2ea58b33ee7feea5cd2f0a89`  
Summary SHA256: `a2e5be8d605af5a2c8206235402fe3a66b08fd994eaa8a71e84cfb1e3cbfed8f`

All EARLY/BALANCED/CONSERVATIVE profiles initialized on `2021-01-17`, first entered FLAT on `2021-02-23`, and then spent 1832 of 1869 classified days in FLAT because V1 made the market-state variable absorbing.

The first FLAT lies inside frozen `HIGH_VOLATILITY_NON_TOP_CONTROL` event `P5C-2021-JAN-FEB-HIGH-VOL`. The raw trigger is fully observed and must remain part of the evidence.

V1 disposition:

```text
P5.3 V1                  COMPLETE / IMMUTABLE / NO_PROMOTION / ARCHITECTURE_FAIL
selected profile         NONE
P5.4 eligible profile    NONE
production authorization NONE
```

V1 must not be rerun, retuned or rewritten.

## P5.3 V2 frozen preregistration

Contract: `P5.3-MARKET-STATE-PERMISSION-SEPARATION-V2`  
Documentation: `docs/P5_3_V2_ARCHITECTURE_PREREG.md`  
Base main: `5b0cac61a45c13d28680e641dd434db4d9a6a2db`  
Status: `FROZEN_BEFORE_V2_STATE_PATH_EVALUATION`

V2 is an architecture-isolation study only.

### Layer separation

```text
MARKET_STATE
  continuous research classification of market evidence

RISK_PERMISSION_LOCK
  operational authority controlling whether actual directional risk may be re-added
```

`MARKET_STATE` states/severity remain exactly V1:

```text
NORMAL_BULL
BTC_LEADERSHIP_MATURING
LATE_BULL_ROTATION
EXHAUSTION_WATCH
DE_RISK_1
DE_RISK_2
FLAT
```

`RISK_PERMISSION_LOCK` semantics are:

```text
UNLOCKED
LOCKED_PENDING_HUMAN_APPROVAL
```

MARKET_STATE has zero authority to unlock operational risk. Automatic unlock is forbidden; only explicit human approval may clear a lock.

P5.3 V2 does not simulate a historical permission-lock path because P5.4 has not defined which MARKET_STATE values map to actual zero exposure.

### Exact signal inheritance from V1

The first V2 study changes none of the following:

- runtime feature inputs;
- evidence atoms;
- raw candidate priority;
- causal percentile normalization;
- EARLY / BALANCED / CONSERVATIVE threshold values;
- escalation persistence values;
- de-escalation clear-period values;
- P5.1 events/anchors/buckets.

V2 implementation must prove exact normalized-feature, evidence-atom and raw-candidate parity versus immutable V1 before any V2 result is interpretable.

### Single architecture delta

V1 excluded `current_state == FLAT` from ordinary de-escalation. V2 removes only that exclusion for **MARKET_STATE**.

Therefore:

- fully evaluated raw FLAT still moves MARKET_STATE immediately to FLAT;
- FLAT remains the highest market severity;
- FLAT is not absorbing in the research MARKET_STATE path;
- if raw candidate stays below FLAT for the existing profile `deescalation_clear_days`, MARKET_STATE moves exactly one step to `DE_RISK_2`;
- every further lower state requires a fresh full clear period;
- any raw FLAT before clear completion resets the recovery counter;
- MARKET_STATE recovery has no effect on RISK_PERMISSION_LOCK.

No new recovery threshold or special parameter exists.

### Frozen V1 failure must remain visible

V2 must exactly reproduce the `2021-02-23` false raw FLAT in `P5C-2021-JAN-FEB-HIGH-VOL` before any architecture interpretation is valid.

It may expose subsequent recovery; it may not:

- change the event/control label;
- move the window/anchor;
- change a signal threshold;
- remove a feature/atom;
- call the false trigger a pass.

### Architecture evaluation boundary

V2 architecture can pass only if:

- all V1 raw/evidence/normalization parity gates pass;
- the false FLAT remains present;
- an earlier FLAT no longer structurally erases all later MARKET_STATE evidence;
- later frozen event windows remain classifiable;
- no market recovery unlocks operational risk.

Architecture pass is not signal acceptance, profile selection, P5.4 selection or production authorization.

P5.4 remains `BLOCKED` until V2 evidence closeout.

## Frozen product boundaries

- BRRK-0011 relative ranking unchanged;
- BTC/ETH/SOL/BNB target universe unchanged;
- XRP feature-only;
- Hyperliquid primary venue;
- P4.1 defensive scaler `[0,1]` unchanged;
- production gross `1.0`;
- actual zero-exposure -> risk-on remains human-gated;
- no automated withdrawals/external transfers;
- production authorization remains none.

## Exact next action

```text
RUN FRESH P5.3 V2 PREREG CI / GOVERNANCE
DO NOT RUN V2 HISTORICAL STATE PATHS IN THE PREREG PR
IF GREEN, MERGE THE V2 PREREGISTRATION
VERIFY NEW MAIN
CREATE A FRESH V2 IMPLEMENTATION BRANCH
IMPLEMENT ONLY THE FROZEN MARKET_STATE FLAT-DEESCALATION ARCHITECTURE DELTA
PROVE EXACT V1 NORMALIZATION / ATOM / RAW-CANDIDATE PARITY
THEN PREPARE A SEPARATE CONTROLLED V2 EVIDENCE RUN
DO NOT START P5.4 OR AUTHORIZE PRODUCTION
```
