# BRRK Next Steps

Last updated: 2026-08-07

## Current instruction

**P5.3 V1 state-path evidence is complete and immutable, but V1 is `NO_PROMOTION / ARCHITECTURE_FAIL`: every frozen profile entered FLAT in a non-top control on 2021-02-23 and the absorbing market-state rule then collapsed the rest of the historical path. Close/merge V1 evidence, then preregister a new P5.3 V2 architecture that separates continuous market-state classification from the existing human-gated re-risk permission boundary. Do not retune V1 signals.**

## Immediate state

```text
Phase 0-3                              COMPLETE / MERGED
LEVERAGE-0040 / 0041                   COMPLETE / IMMUTABLE / NO_PROMOTION
Phase 4 leverage research              FAIL_STOP
production gross cap                   1.0
production_authorized_components       []
P5.1 event taxonomy                    COMPLETE / MERGED / FROZEN
P5.2 feature evidence                  COMPLETE / IMMUTABLE / DESCRIPTIVE CLOSEOUT
P5.3 V1 state model                    COMPLETE / IMMUTABLE / NO_PROMOTION / ARCHITECTURE_FAIL
P5.3 V1 result commit                  7703b3ffec906a9d2ea58b33ee7feea5cd2f0a89
P5.3 V1 summary SHA256                 a2e5ece89fec93a24e1a65e134a78824629b4b418e106294a6b0821fbd52608b
P5.3 V2 architecture                   NEXT
P5.4 behavior mapping                  BLOCKED / no eligible P5.3 classifier
```

## P5.3 V1 result

All three profiles:

```text
initialization       2021-01-11
first FLAT           2021-02-23
classified days      1874
FLAT days            1837
FLAT fraction        98.0256%
```

The first FLAT occurs in the frozen `P5C-2021-JAN-FEB-HIGH-VOL` event, explicitly a `HIGH_VOLATILITY_NON_TOP_CONTROL`.

Near that control anchor (`-6..0d`), all three profiles are FLAT on 6/7 classified days (`85.7143%`).

The trigger is a fully observed frozen hard-risk signal, not a data defect:

```text
minimum calibration depth  57
exhaustion                  true
strong_exhaustion           true
damage                      true
strong_damage               true
raw candidate               FLAT
```

No profile can be selected from V1.

## Architecture diagnosis

The raw market candidate does **not** remain permanently bearish after the false FLAT:

```text
2021-02-27  DE_RISK_2
2021-02-28  NORMAL_BULL
2021-03-01  NORMAL_BULL
2021-03-09  BTC_LEADERSHIP_MATURING
```

V1 remains FLAT only because the market-state variable itself is absorbing.

This combines two distinct concerns:

```text
market classification
  what current market evidence says

operational permission
  whether a system may re-add risk after an actual zero-exposure action
```

The second concern remains human-gated by product policy. It should not erase later market-state evidence in historical research.

Formal result interpretation: `docs/P5_3_STATE_PATH_CLOSEOUT.md`.

## V1 frozen disposition

Do not:

- rerun `P5.3-STATE-PATH-EVIDENCE-V1`;
- alter V1 features / atoms / thresholds / profiles;
- move P5.1 events or buckets;
- edit the immutable result;
- pick a V1 profile after the fact;
- proceed to P5.4 using V1.

## P5.3 V2 — NEXT

Create a new architecture contract. The first V2 study is an **architecture-isolation** study, not a signal retune.

### Keep unchanged from V1

- P5.1 event taxonomy;
- immutable P5.2 feature panel;
- causal percentile formula/window/minimum;
- V1 runtime feature set;
- V1 evidence atoms;
- EARLY/BALANCED/CONSERVATIVE percentile thresholds;
- escalation/clear-period values;
- frozen P5.1 event reporting buckets.

### Change only the architecture layer

Separate:

```text
MARKET_STATE
  daily market classification; a FLAT market observation is severe but the classifier may later describe recovery under frozen clear/de-escalation rules

RISK_PERMISSION_LOCK
  separate control status; if an actual live system has reduced to zero exposure, re-risk remains explicit-human-approved
```

Historical research should continue calculating `MARKET_STATE` after a FLAT classification so later events remain observable. This does **not** grant an automated live re-entry permission.

### Required V2 evidence

At minimum report:

- market-state path for all three unchanged profiles;
- every raw/final market-state FLAT episode and duration;
- recovery date after each FLAT episode;
- control-event FLAT occupancy;
- second-wind state occupancy;
- terminal-event lead/near-event states;
- transitions/churn;
- comparison versus V1 showing exactly what changed because of layer separation;
- explicit operational permission-lock semantics kept outside the market-state classifier.

The 2021-02-23 non-top false FLAT must remain visible. V2 cannot declare it a non-event or change thresholds to remove it.

## P5.4 remains blocked

Do not map state to gross-risk multipliers until a usable P5.3 classifier exists. P5.4 behavior/economic mapping on V1 would merely monetize an already-rejected state architecture.

## Frozen product boundaries

- BRRK-0011 relative ranking unchanged;
- BTC/ETH/SOL/BNB long universe unchanged;
- XRP feature-only;
- Hyperliquid primary venue;
- P4.1 defensive scaler `[0,1]` unchanged;
- production gross `1.0`;
- actual re-risk after zero exposure remains human-gated;
- no withdrawal/external-transfer automation;
- no production authorization.

## Exact next step

```text
RUN FRESH POST-RESULT V1 CI / GOVERNANCE
IF GREEN, EXACT-HEAD MERGE P5.3 V1 CLOSEOUT
VERIFY NEW MAIN
CREATE FRESH P5.3 V2 ARCHITECTURE BRANCH
PREREGISTER MARKET_STATE / RISK_PERMISSION_LOCK SEPARATION
KEEP V1 SIGNAL RULES UNCHANGED
DO NOT START P5.4 UNTIL V2 STATE EVIDENCE IS REVIEWABLE
```
