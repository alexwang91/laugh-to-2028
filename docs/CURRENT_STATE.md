# BRRK Current State

Last updated: 2026-08-08
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
P4.6 production leverage gate  BLOCKED
P5.1 event taxonomy            COMPLETE / MERGED / FROZEN
P5.2 feature families          COMPLETE / IMMUTABLE / DESCRIPTIVE CLOSEOUT
P5.3 V1 state model            COMPLETE / IMMUTABLE / NO_PROMOTION / ARCHITECTURE_FAIL
P5.3 V2 architecture           COMPLETE / IMMUTABLE EVIDENCE / ARCHITECTURE_PASS
P5.3 selected profile          NONE
P5.4 behavior mapping          NEXT / FIXED-CANDIDATE PREREGISTRATION
P5.5 validation                NOT STARTED
P5.6 integration               NOT STARTED
Phase 6 integrated shadow      NOT STARTED
Phase 7 limited live long      NOT STARTED / actual launch requires explicit approval
Phase 8 bear-short research    NOT STARTED
production authorization       NONE
```

`production_authorized_components = []`

Current production gross cap remains `1.0`.

## Immutable upstream research

### P5.1

Contract: `P5.1-EVENT-TAXONOMY-V1`  
Taxonomy blob SHA: `73d010666fbfd957ec15214a00883a90a8adba5a`

Events, anchors and five evaluation buckets remain frozen. Only 2021 November is explicitly terminal.

### P5.2

Contract: `P5.2-FEATURE-FAMILIES-V1`  
Result commit: `61d585afb64afbe3ead6422e7e62cde6c59fad40`  
Summary SHA256: `3f6dc3c512d22ac8f71d43ed155f2602cd40d5caf3d617c0e130e170727e0627`

P5.2 remains descriptive only. Six requested data families remain `DATA_SOURCE_PENDING`; favorable proxy substitution is forbidden.

## P5.3 V1 immutable negative result

Contract: `P5.3-STATE-MODEL-STRUCTURE-V1`  
Result commit: `7703b3ffec906a9d2ea58b33ee7feea5cd2f0a89`  
Summary SHA256: `a2e5be8d605af5a2c8206235402fe3a66b08fd994eaa8a71e84cfb1e3cbfed8f`

All profiles first entered `FLAT` on `2021-02-23` inside frozen `P5C-2021-JAN-FEB-HIGH-VOL`, a `HIGH_VOLATILITY_NON_TOP_CONTROL`. V1 made market state absorbing, producing a degenerate path. V1 is immutable and must not be rerun or retuned.

## P5.3 V2 architecture result

Architecture contract: `P5.3-MARKET-STATE-PERMISSION-SEPARATION-V2`  
Evidence contract: `P5.3-V2-MARKET-STATE-PATH-EVIDENCE-V1`  
Result commit: `e732b7ebe570236bf43084caecb6ea15f7edecb8`  
Summary SHA256: `05d5d68a59c8b13f1122d98ed75d03934defdc9d73c7dd92e038c92fd97d2e52`

V2 changed only architecture: continuous research `MARKET_STATE` is no longer absorbing at `FLAT`; operational `RISK_PERMISSION_LOCK` remains separate and human-gated.

Frozen parity/result boundary:

```text
architecture_pass                    true
raw_candidate_parity_fraction        1.0
atom_parity_fraction                 1.0
normalization_parity                 true
normalization_count_parity           true
pre_first_flat_state_parity_fraction 1.0
false_flat_reproduced                true
post_false_flat_nonflat_exists       true
later_events_observable              true
profile_selected                     false
p5_4_mapping_selected                false
risk_permission_unlock_authorized    false
production_authorized                false
```

The immutable false-FLAT remains visible but no longer erases the sample:

```text
EARLY         FLAT 2021-02-23..2021-02-28  -> non-FLAT 2021-03-01
BALANCED      FLAT 2021-02-23..2021-02-28  -> non-FLAT 2021-03-01
CONSERVATIVE  FLAT 2021-02-23..2021-03-02  -> non-FLAT 2021-03-03
```

Architecture pass does not select a profile and does not validate economics. Formal closeout: `docs/P5_3_V2_MARKET_STATE_CLOSEOUT.md`.

## P5.4 boundary

P5.4 is now eligible to preregister **fixed candidate state-to-gross-risk mappings**. It must not select a winner or alter BRRK relative asset ranking. Because Phase 4 produced no eligible >1 leverage candidate, every P5.4 gross-risk multiplier must remain in `[0,1]`.

P5.5 owns joint profile + behavior-map robustness/economic selection. The immutable 2021 false FLAT must be charged as missed-upside/false-positive evidence rather than hidden.

## Frozen product boundaries

- directional core: BRRK-0011;
- tradable long universe: BTC / ETH / SOL / BNB;
- XRP feature-only;
- primary venue: Hyperliquid;
- daily decision boundary: 00:00 UTC;
- P4.1 defensive scale `[0,1]` unchanged;
- production gross remains `1.0`;
- actual zero-exposure -> risk-on remains human-gated;
- no automated withdrawals/external transfers;
- no production authorization.

## Exact next action

```text
CLOSE / CI-VERIFY / MERGE P5.3 V2 RESULT PR
VERIFY NEW MAIN
PREREGISTER P5.4 FIXED STATE->GROSS-RISK CANDIDATE MAPS
DO NOT SELECT A P5.4 WINNER
IMPLEMENT CANDIDATE MAPPING MECHANICS
THEN P5.5 OWNS LEAVE-ONE-EVENT-OUT / COST / SECOND-WIND / TERMINAL-WEALTH VALIDATION
DO NOT PRODUCTION-AUTHORIZE ANYTHING
```
