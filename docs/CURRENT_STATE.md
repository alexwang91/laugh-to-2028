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
LEVERAGE-0039                  STOPPED PRE-RUN / NO RESULT
LEVERAGE-0040                  COMPLETE / IMMUTABLE / NO_PROMOTION
LEVERAGE-0041                  COMPLETE / IMMUTABLE / NO_PROMOTION
Phase 4 leverage research      FAIL_STOP / no eligible >1 candidate
P4.6 production leverage gate  NOT ENTERED / BLOCKED by no candidate
P5.1 event taxonomy            COMPLETE / MERGED / FROZEN
P5.2 feature families          COMPLETE / IMMUTABLE EVIDENCE / DESCRIPTIVE CLOSEOUT
P5.3 V1 state model            COMPLETE / IMMUTABLE / NO_PROMOTION / ARCHITECTURE_FAIL
P5.3 V2 architecture study     NEXT
P5.4 behavior mapping          BLOCKED / no eligible P5.3 classifier
P5.5-P5.6                      NOT STARTED
Phase 6 integrated shadow      NOT STARTED
Phase 7 limited live long      NOT STARTED / explicit approval required
Phase 8 bear-short research    NOT STARTED
production authorization       NONE
```

`production_authorized_components = []`

Current production gross cap remains `1.0`.

## Immutable upstream research

### Phase 4

`LEVERAGE-0040` and `LEVERAGE-0041` are immutable `NO_PROMOTION` studies. No >1 cap is eligible for P4.6.

### P5.1

Contract: `P5.1-EVENT-TAXONOMY-V1`  
Taxonomy blob SHA: `73d010666fbfd957ec15214a00883a90a8adba5a`

The 2021/2025 event taxonomy and four high-volatility non-top controls remain frozen. Only 2021 November is explicitly terminal.

### P5.2

Contract: `P5.2-FEATURE-FAMILIES-V1`  
Immutable result commit: `61d585afb64afbe3ead6422e7e62cde6c59fad40`  
Immutable summary SHA256: `3f6dc3c512d22ac8f71d43ed155f2602cd40d5caf3d617c0e130e170727e0627`

P5.2 remains descriptive only: 29 available features passed coverage, six requested data sources remain `DATA_SOURCE_PENDING`, and no final feature set or P5.3 threshold was selected.

## P5.3 V1 immutable result

State-model contract: `P5.3-STATE-MODEL-STRUCTURE-V1`  
Evidence contract: `P5.3-STATE-PATH-EVIDENCE-V1`  
Immutable result commit: `7703b3ffec906a9d2ea58b33ee7feea5cd2f0a89`  
Immutable summary SHA256: `a2e5ece89fec93a24e1a65e134a78824629b4b418e106294a6b0821fbd52608b`

RUN_ONCE completed successfully: frozen guards passed, all three profiles ran, immutable validation passed and result files were committed.

The result remains non-authorizing:

```text
profile_selected                 false
state_model_production_selected  false
selection.status                 STATE_PATH_EVIDENCE_ONLY
production_authorized            false
```

### V1 failure

All three profiles initialized on `2021-01-11` and first entered `FLAT` on `2021-02-23`.

```text
profile       classified days   FLAT days   FLAT fraction
EARLY         1874              1837        98.0256%
BALANCED      1874              1837        98.0256%
CONSERVATIVE  1874              1837        98.0256%
```

The first FLAT is a false hard-risk event inside the frozen `P5C-2021-JAN-FEB-HIGH-VOL` non-top control. In its `near_event` bucket (`2021-02-22 .. 2021-02-28`), every profile is FLAT for 6 of 7 classified days (`85.7143%`).

This is not missing-data/warm-up behavior. On `2021-02-23`:

```text
ordinary_inputs_complete   true
minimum_calibration_depth  57
exhaustion                 true
strong_exhaustion          true
damage                     true
strong_damage              true
raw_candidate_state        FLAT
```

Therefore no EARLY/BALANCED/CONSERVATIVE V1 profile is eligible for P5.4.

### Architecture problem exposed by V1

The immutable raw candidate recovered quickly after the false FLAT:

```text
2021-02-27  DE_RISK_2
2021-02-28  NORMAL_BULL
2021-03-01  NORMAL_BULL
2021-03-09  BTC_LEADERSHIP_MATURING
```

The final V1 state nevertheless remained permanently FLAT because V1 made the **market-state variable itself** absorbing.

V1 therefore conflated:

1. continuous market-state classification; and
2. the valid product/control requirement that actual re-risk after a zero-exposure action must be human-approved.

The human-approval boundary remains unchanged. The research architecture must separate it from the market-state history so later regimes remain observable.

Formal closeout: `docs/P5_3_STATE_PATH_CLOSEOUT.md`.

## V1 disposition

```text
P5.3-STATE-MODEL-STRUCTURE-V1  COMPLETE / IMMUTABLE / NO_PROMOTION
P5.3-STATE-PATH-EVIDENCE-V1    COMPLETE / IMMUTABLE
selected profile               NONE
P5.4 eligible profile          NONE
production authorization       NONE
```

Do not rerun or retune V1. Do not change V1 features, profile thresholds, event metrics or immutable result files after observing the failure.

## Next research hypothesis — P5.3 V2

P5.4 is blocked. The next research task is a **new P5.3 architecture contract**, not a V1 rescue.

The first V2 architecture-isolation hypothesis should separate:

```text
MARKET_STATE
  continues classifying recovery/deterioration after a market FLAT observation

RISK_PERMISSION_LOCK
  separate operational boundary; any future live re-risk after an actual zero-exposure action remains explicit-human-approved
```

To isolate architecture from signal retuning, the first V2 study should preserve V1:

- P5.1 taxonomy;
- P5.2 immutable feature inputs;
- evidence atoms;
- percentile normalization;
- EARLY/BALANCED/CONSERVATIVE percentile thresholds and persistence values.

The false raw FLAT in the non-top control remains evidence and must remain visible. V2 may make later market states observable; it must not rewrite the control event into a pass.

## Frozen product boundaries

- directional core: BRRK-0011;
- target/tradable assets: BTC / ETH / SOL / BNB;
- XRP feature-only;
- primary venue: Hyperliquid;
- daily decision boundary: 00:00 UTC;
- actual zero-exposure -> risk-on remains human-gated;
- no automated withdrawals/external transfers;
- P4.1 defensive scale `[0,1]` unchanged;
- production gross remains `1.0`;
- production authorization remains none.

## Exact next action

```text
CLOSE / CI-VERIFY / MERGE P5.3 V1 RESULT PR
VERIFY NEW MAIN
CREATE A FRESH P5.3 V2 ARCHITECTURE BRANCH
PREREGISTER MARKET_STATE VS RISK_PERMISSION_LOCK SEPARATION
KEEP V1 SIGNAL FEATURES / ATOMS / PROFILE THRESHOLDS UNCHANGED IN THE FIRST V2 ISOLATION STUDY
DO NOT START P5.4 UNTIL A P5.3 MARKET-STATE PATH IS USABLE
DO NOT PRODUCTION-AUTHORIZE ANYTHING
```
