# BRRK Next Steps

Last updated: 2026-08-07

## Current instruction

**P5.3 V1 is immutable `NO_PROMOTION / ARCHITECTURE_FAIL`. P5.3 V2 is now preregistered as an architecture-isolation study before any V2 state path. Validate and merge the V2 contract, then implement only the separation between continuous MARKET_STATE and human-gated RISK_PERMISSION_LOCK. Do not retune V1 signals or start P5.4.**

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
P5.3 V1 summary SHA256                 a2e5be8d605af5a2c8206235402fe3a66b08fd994eaa8a71e84cfb1e3cbfed8f
P5.3 V2 contract                       P5.3-MARKET-STATE-PERMISSION-SEPARATION-V2
P5.3 V2 architecture                   PREREGISTERED / FROZEN BEFORE V2 STATE PATHS
P5.3 V2 state paths                    NOT RUN
P5.4 behavior mapping                  BLOCKED PENDING V2 CLOSEOUT
```

## Why V2 exists

V1 produced a fully observed false raw FLAT on `2021-02-23` inside frozen `P5C-2021-JAN-FEB-HIGH-VOL`, a `HIGH_VOLATILITY_NON_TOP_CONTROL`. V1 then made the market-state variable absorbing, preventing useful evaluation of later regimes.

V2 does not erase the false trigger. It tests one architecture hypothesis only:

```text
MARKET_STATE
  should keep describing the market after a severe FLAT observation

RISK_PERMISSION_LOCK
  should remain a separate operational human-approval boundary
```

## Frozen V1 inheritance

The first V2 study must keep unchanged:

- P5.1 taxonomy, anchors and five evaluation buckets;
- immutable P5.2 feature panel;
- V1 runtime feature set;
- V1 evidence atoms;
- V1 raw candidate priority;
- causal percentile normalization;
- EARLY/BALANCED/CONSERVATIVE percentile thresholds;
- escalation persistence values;
- de-escalation clear-period values;
- missing-data fail-closed semantics.

Before V2 interpretation, normalized values, evidence atoms and raw candidates must exactly match immutable V1.

## Frozen profile values

| Profile | Moderate high/low | Strong high/low | Escalation | Clear |
| --- | --- | --- | ---: | ---: |
| EARLY | 0.65 / 0.35 | 0.80 / 0.20 | 2d | 5d |
| BALANCED | 0.70 / 0.30 | 0.85 / 0.15 | 3d | 5d |
| CONSERVATIVE | 0.75 / 0.25 | 0.90 / 0.10 | 3d | 7d |

## Single V2 architecture change

V1 ordinary de-escalation excluded `current_state == FLAT`. V2 removes only that exclusion for **MARKET_STATE**.

```text
raw FLAT
  -> immediate MARKET_STATE FLAT, unchanged from V1

MARKET_STATE FLAT + raw below FLAT for existing clear period
  -> DE_RISK_2

further recovery
  -> one severity step only after each new full clear period

raw returns FLAT before clear completes
  -> reset recovery counter, remain FLAT
```

No special post-FLAT threshold or new free parameter exists.

## RISK_PERMISSION_LOCK

Operational permission is separate:

```text
UNLOCKED
LOCKED_PENDING_HUMAN_APPROVAL
```

Rules:

- MARKET_STATE cannot unlock permission;
- automatic unlock is forbidden;
- explicit human approval is the only unlock authority;
- market recovery does not itself authorize a live risk increase.

Do not fabricate a V2 historical permission-lock path before P5.4 defines which market states actually map to zero exposure.

## V2 failure-preservation gate

V2 must reproduce the immutable V1 signal evidence, including:

```text
false raw FLAT date   2021-02-23
event                  P5C-2021-JAN-FEB-HIGH-VOL
class                  HIGH_VOLATILITY_NON_TOP_CONTROL
V1 near-event FLAT     6 / 7 days
```

If the raw FLAT disappears, V2 implementation has violated the preregistration.

## Required V2 evidence — later

After preregistration is merged and implementation parity is green, a separate controlled evidence run must report:

- full MARKET_STATE paths for all three profiles;
- exact V1 normalization/atom/raw-candidate parity;
- every MARKET_STATE FLAT episode and duration;
- first recovery date after each FLAT episode;
- every P5.1 event-bucket occupancy;
- second-wind behavior;
- non-top-control FLAT occupancy;
- terminal-event lead/near-event states;
- transitions/churn;
- direct V1-vs-V2 state-path delta;
- assertion that market recovery never changes operational permission.

## Architecture pass boundary

An architecture pass means only that:

- V1 raw/evidence parity is exact;
- the false FLAT remains visible;
- later market regimes remain classifiable instead of being permanently erased by an earlier FLAT;
- operational re-risk remains human-gated.

It does not accept signal quality, select a profile, select P5.4 gross behavior, or authorize production.

## P5.4 remains blocked

Do not define or test state-to-gross multipliers until V2 evidence is complete and reviewable. P5.4 cannot be used to compensate for V1/V2 classification defects.

## Frozen product boundaries

- BRRK-0011 relative ranking unchanged;
- BTC/ETH/SOL/BNB long universe unchanged;
- XRP feature-only;
- Hyperliquid primary venue;
- P4.1 defensive scaler `[0,1]` unchanged;
- production gross `1.0`;
- actual re-risk after implemented zero exposure remains human-gated;
- no withdrawal/external-transfer automation;
- no production authorization.

## Exact next step

```text
RUN FRESH V2 PREREG CONTRACT CI / GOVERNANCE
VERIFY IMMUTABLE V1 VALIDATOR STILL PASSES
VERIFY NO V2 RESULT EXISTS
IF GREEN, EXACT-HEAD MERGE V2 PREREGISTRATION
CREATE FRESH V2 IMPLEMENTATION BRANCH FROM NEW MAIN
IMPLEMENT ONLY NON-ABSORBING MARKET_STATE FLAT RECOVERY
PROVE EXACT V1 RAW / ATOM / NORMALIZATION PARITY
DO NOT RUN V2 HISTORICAL STATE PATHS UNTIL IMPLEMENTATION GATES ARE GREEN
DO NOT START P5.4
DO NOT PRODUCTION-AUTHORIZE ANYTHING
```
