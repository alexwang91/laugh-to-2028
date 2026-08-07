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
P5.3 state-model structure     COMPLETE / MERGED / R1+R2 FROZEN
P5.3 implementation            IMPLEMENTED / FROZEN / PRE-RUN CI REQUIRED
P5.3 state-path evidence       NOT RUN
P5.4-P5.6                      NOT STARTED
Phase 6 integrated shadow      NOT STARTED
Phase 7 limited live long      NOT STARTED / explicit approval required
Phase 8 bear-short research    NOT STARTED
production authorization       NONE
```

`production_authorized_components = []`

Current production gross cap remains `1.0`.

## Immutable research dependencies

### Phase 4

`LEVERAGE-0040` and `LEVERAGE-0041` are complete immutable `NO_PROMOTION` studies. No >1 cap is eligible for P4.6. Production gross stays 1.0.

### P5.1

Contract: `P5.1-EVENT-TAXONOMY-V1`  
Taxonomy blob SHA: `73d010666fbfd957ec15214a00883a90a8adba5a`

Required 2021/2025 events and four high-volatility non-top controls are frozen. Only 2021 November is explicitly terminal. P5.3 may not move events, anchors or buckets.

### P5.2

Contract: `P5.2-FEATURE-FAMILIES-V1`  
Immutable result commit: `61d585afb64afbe3ead6422e7e62cde6c59fad40`  
Immutable summary SHA256: `3f6dc3c512d22ac8f71d43ed155f2602cd40d5caf3d617c0e130e170727e0627`

```text
available features        29
coverage                   ALL PASS
pending data sources       6
feature_set_selected       false
state_thresholds_selected  false
production_authorized      false
```

P5.2 robust-z values remain descriptive research diagnostics only and are not P5.3 runtime inputs.

## P5.3 frozen structure

State-model contract: `P5.3-STATE-MODEL-STRUCTURE-V1`.

Merged prereg main: `8533f8ce0519dfeade6ac33124d90a45a416122c`.

Both completeness corrections occurred before any state path:

- `P5.3-PREREG-COMPLETENESS-R1` — exact percentile mapping / causal early-history calibration;
- `P5.3-PREREG-COMPLETENESS-R2` — exact hysteresis mechanics / removal of dead runtime inputs.

State vocabulary / severity order:

```text
NORMAL_BULL
BTC_LEADERSHIP_MATURING
LATE_BULL_ROTATION
EXHAUSTION_WATCH
DE_RISK_1
DE_RISK_2
FLAT
```

Runtime evidence channels:

```text
REGIME_TEXTURE
LEADERSHIP_ROTATION
EXHAUSTION_TRANSITION
TREND_DAMAGE
```

Core semantic boundary:

```text
volatility alone            != top
ETH/BTC leadership alone    != bearish
raw RSI alone               != top
rotation without damage     -> LATE_BULL_ROTATION candidate
exhaustion without damage   -> EXHAUSTION_WATCH candidate
exhaustion + damage         -> de-risk candidate
strong exhaustion + damage  -> hard-risk / FLAT candidate
```

Causal normalization:

```text
window          last up to 365 completed daily dates ending at t
minimum N       20 nonmissing observations per continuous feature
percentile      (average_rank(current) - 1) / (N - 1)
future data     forbidden
pre-init        DATA_INSUFFICIENT
```

Frozen profiles:

```text
EARLY        65/35 moderate, 80/20 strong, escalation 2d, clear 5d
BALANCED     70/30 moderate, 85/15 strong, escalation 3d, clear 5d
CONSERVATIVE 75/25 moderate, 90/10 strong, escalation 3d, clear 7d
```

FLAT is absorbing inside P5.3; re-risk from FLAT requires explicit human approval outside the classifier.

## P5.3 implementation / evidence contract

Implementation files now exist on the P5.3 implementation branch:

```text
research/cycle_exit/p5_3_state_model.py
research/cycle_exit/run_p5_3_state_paths.py
research/cycle_exit/validate_p5_3_state_path_result.py
execution/plan-b-bot/tests/test_p5_3_state_model.py
```

Frozen evidence-output contract:

`P5.3-STATE-PATH-EVIDENCE-V1`

It binds to state-model blob:

`400ec97f8a0e522c5776ce1f6a98fc6d7e069267`

and P5.2 summary SHA256:

`3f6dc3c512d22ac8f71d43ed155f2602cd40d5caf3d617c0e130e170727e0627`

No historical P5.3 state path has been generated yet.

The evidence contract freezes event reporting to the existing five P5.1 buckets. It forbids adding a post-result custom lead/lag window. Required outputs include:

- normalized percentiles / normalization counts;
- daily state path, raw candidate and atom booleans for all three profiles;
- initialization/calibration diagnostics;
- event-bucket state occupancy;
- first state occurrence within each frozen bucket and anchor offset;
- profile transition/churn summary;
- second-wind/control conservative-state behavior through the same frozen occupancy table.

The result must remain:

```text
profile_selected                 false
state_model_production_selected  false
status                           STATE_PATH_EVIDENCE_ONLY
production authorization         NONE
```

## Frozen product boundaries

- directional core: BRRK-0011;
- target/tradable assets: BTC / ETH / SOL / BNB;
- XRP feature-only;
- primary venue: Hyperliquid;
- daily decision boundary: 00:00 UTC;
- FLAT = zero directional exposure;
- human approval remains required for risk-on transitions from FLAT/control states;
- no automated withdrawals/external transfers;
- P4.1 defensive scale `[0,1]` unchanged;
- production gross remains `1.0`.

## Exact next action

```text
RUN FRESH P5.3 IMPLEMENTATION / SYNTHETIC UNIT / GOVERNANCE CI
DO NOT COMPUTE HISTORICAL STATE PATHS DURING PREFLIGHT
IF ALL PRE-RUN GATES ARE GREEN, COMMIT THE FROZEN RUN_ONCE MARKER
EXECUTE P5.3-STATE-PATH-EVIDENCE-V1 ONCE
VALIDATE AND COMMIT IMMUTABLE RESULT
DO NOT RETUNE STATE RULES / PROFILES / EVENT METRICS AFTER RESULT
DO NOT SELECT P5.4 GROSS MULTIPLIERS
DO NOT PRODUCTION-AUTHORIZE ANYTHING
```
