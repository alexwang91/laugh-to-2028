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
P5.3 state-model structure     PREREGISTERED / FROZEN BEFORE STATE-PATH EVALUATION
P5.3 implementation/evidence   NOT RUN
P5.4-P5.6                      NOT STARTED
Phase 6 integrated shadow      NOT STARTED
Phase 7 limited live long      NOT STARTED / explicit approval required
Phase 8 bear-short research    NOT STARTED
production authorization       NONE
```

`production_authorized_components = []`

Current production gross cap remains `1.0`.

## Phase 4 immutable truth

`LEVERAGE-0040` and `LEVERAGE-0041` are complete immutable `NO_PROMOTION` studies. No research cap, operating drawdown budget or prospective P4.6 cap was selected. Do not rerun, rescue, retune, reinterpret or reuse either experiment ID.

LEVERAGE-0041 result commit:

`8ea784830cfffbf892a258cb329d437725d41982`

LEVERAGE-0041 immutable summary SHA256:

`e41a5895263e7aa9206df9fa99fcbb71e5f937abc4746a567fbeb462cca88d17`

## P5.1 immutable taxonomy truth

P5.1 merged in PR #97 on main `86497cdd663a89ca4d54c898b7acbac1cc07d836`.

Contract: `P5.1-EVENT-TAXONOMY-V1`.

Taxonomy blob SHA: `73d010666fbfd957ec15214a00883a90a8adba5a`.

Required 2021/2025 events and four high-volatility non-top controls are frozen. Only 2021 November is explicitly terminal in V1. Search windows, anchor rules and evaluation buckets may not be moved by P5.3.

## P5.2 immutable feature-evidence truth

Contract: `P5.2-FEATURE-FAMILIES-V1`.

Immutable result commit:

`61d585afb64afbe3ead6422e7e62cde6c59fad40`

Immutable summary SHA256:

`3f6dc3c512d22ac8f71d43ed155f2602cd40d5caf3d617c0e130e170727e0627`

```text
status                    ONE_TIME_FROZEN_FEATURE_EVIDENCE_COMPLETE
available features        29
coverage                   ALL PASS
resolved events            11
non-top controls           4
pending data sources       6
feature_set_selected       false
state_thresholds_selected  false
selection.status           DESCRIPTIVE_EVIDENCE_ONLY
production_authorized      false
```

Formal interpretation: `docs/P5_2_FEATURE_EVIDENCE_CLOSEOUT.md`.

Derived non-authorizing diagnostics: `research/analysis/p5_2_closeout/`.

P5.2 does not authorize a final feature set or thresholds. It provides evidence used to preregister P5.3.

## P5.3 frozen preregistration truth

Contract:

`P5.3-STATE-MODEL-STRUCTURE-V1`

Files:

```text
research/cycle_exit/p5_3_state_model_contract.json
docs/P5_3_STATE_MODEL_PREREG.md
execution/plan-b-bot/tests/test_p5_3_state_model_prereg.py
.github/workflows/p5-3-state-model-prereg.yml
```

Status:

`FROZEN_BEFORE_STATE_PATH_EVALUATION`

Target states:

```text
NORMAL_BULL
BTC_LEADERSHIP_MATURING
LATE_BULL_ROTATION
EXHAUSTION_WATCH
DE_RISK_1
DE_RISK_2
FLAT
```

### Frozen architecture

P5.3 uses four complementary evidence channels:

- `REGIME_TEXTURE` — volatility/high-level maturity context;
- `LEADERSHIP_ROTATION` — ETH/BTC-led rotation and breadth evidence;
- `EXHAUSTION_TRANSITION` — divergence, momentum failure and breadth transition;
- `TREND_DAMAGE` — KAMA/high-distance/20d/40d BTC damage.

The design explicitly enforces:

```text
volatility alone            != top
ETH/BTC leadership alone    != bearish
raw RSI alone               != top
rotation without damage     -> LATE_BULL_ROTATION candidate
exhaustion without damage   -> EXHAUSTION_WATCH candidate
exhaustion + damage         -> de-risk candidate
strong exhaustion + damage  -> hard-risk / FLAT candidate
```

### Causal normalization

Continuous runtime inputs use trailing empirical percentiles:

```text
lookback       365 completed daily observations
minimum        252 observations
future data    forbidden
current bar    allowed only after completion at 00:00 UTC decision boundary
missing data   fail closed / no automatic de-escalation or re-risk
```

P5.2 robust-z values are research diagnostics only and are **not** runtime inputs.

### Frozen sensitivity profiles

```text
EARLY        moderate 65/35  strong 80/20  escalation 2d  clear 5d
BALANCED     moderate 70/30  strong 85/15  escalation 3d  clear 5d
CONSERVATIVE moderate 75/25  strong 90/10  escalation 3d  clear 7d
```

All three profiles must be reported. They are preregistered sensitivity cases, not post-result tuning knobs.

### Transition boundary

- ordinary escalation requires profile-specific persistence;
- de-escalation requires a clear period and moves at most one state/day;
- hard strong-damage + strong-exhaustion may enter FLAT immediately;
- FLAT is absorbing inside P5.3;
- `FLAT -> risk-on` requires explicit human approval outside P5.3;
- intraday P5.3 risk addition is forbidden.

### Explicitly excluded pending data

P5.3 does not use or proxy the six P5.2 pending inputs:

- BTC dominance;
- broad-market breadth;
- historical funding;
- historical OI;
- historical basis/premium;
- liquidation proxy.

## P5.3 next evidence boundary

After prereg CI/governance is green and merged, implement the deterministic state engine against the immutable P5.2 feature panel and report all three frozen profiles.

Required outputs include:

- complete daily state paths;
- event-window occupancy;
- first-entry dates / lead-lag;
- state transition and churn counts;
- second-wind false-terminal / FLAT behavior;
- non-top-control conservative-state occupancy;
- missing-data behavior;
- profile sensitivity.

P5.3 may identify a research candidate for downstream P5.4/P5.5, but may not select production behavior or a production state model. P5.5 owns robustness selection after behavior/economic mapping exists.

## Roadmap audit status

All historical deviations identified by the 2026-08-07 program-wide audit have recorded CLOSED dispositions. Current canonical product/strategy/production drift: **DRIFT_0**.

## Frozen product boundaries

- directional core: BRRK-0011;
- target/tradable assets: BTC / ETH / SOL / BNB;
- XRP feature-only;
- primary venue: Hyperliquid;
- daily decision boundary: 00:00 UTC;
- FLAT = zero directional exposure;
- FLAT -> LONG / SHORT and MONITOR_ONLY -> ACTIVE require explicit human approval;
- first short of a new bear phase requires explicit human approval;
- intraday automation may reduce but not autonomously add directional exposure;
- master key, automated withdrawals and external transfers remain outside scope;
- P4.1 defensive scale stays `[0,1]`;
- production gross remains `1.0`.

## Exact next action

```text
RUN FRESH P5.3 PREREG CONTRACT CI + GOVERNANCE
IF GREEN, MERGE PREREGISTRATION
CREATE FRESH P5.3 IMPLEMENTATION BRANCH FROM NEW MAIN
IMPLEMENT EARLY / BALANCED / CONSERVATIVE EXACTLY AS FROZEN
DO NOT CHANGE FEATURES / PROFILES / STATE RULES AFTER STATE PATHS ARE OBSERVED
DO NOT SELECT P5.4 GROSS MULTIPLIERS
DO NOT PRODUCTION-AUTHORIZE ANYTHING
```
