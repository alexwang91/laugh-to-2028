# BRRK Next Steps

Last updated: 2026-08-07

## Current instruction

**P5.3 R1+R2 structure is merged. The deterministic state engine and frozen state-path evidence contract are implemented but historical state paths have not been run. Run final pre-run CI using synthetic/unit evidence only; if green, execute `P5.3-STATE-PATH-EVIDENCE-V1` once under standing research authorization.**

## Immediate state

```text
Phase 0-3                              COMPLETE / MERGED
LEVERAGE-0040 / 0041                   COMPLETE / IMMUTABLE / NO_PROMOTION
Phase 4 leverage research              FAIL_STOP
production gross cap                   1.0
production_authorized_components       []
P5.1 event taxonomy                    COMPLETE / MERGED / FROZEN
P5.2 feature evidence                  COMPLETE / IMMUTABLE / DESCRIPTIVE CLOSEOUT
P5.3 structure                         COMPLETE / MERGED / R1+R2 FROZEN
P5.3 implementation                    IMPLEMENTED / FROZEN / PRE-RUN
P5.3 evidence contract                 P5.3-STATE-PATH-EVIDENCE-V1
P5.3 historical state paths            NOT RUN
P5.4-P5.6                              NOT STARTED
```

## Frozen P5.3 runtime contract

State severity order:

```text
NORMAL_BULL
BTC_LEADERSHIP_MATURING
LATE_BULL_ROTATION
EXHAUSTION_WATCH
DE_RISK_1
DE_RISK_2
FLAT
```

Evidence channels:

```text
REGIME_TEXTURE
LEADERSHIP_ROTATION
EXHAUSTION_TRANSITION
TREND_DAMAGE
```

Causal normalization:

```text
window          last up to 365 completed daily dates ending at t
minimum N       20 nonmissing observations per continuous feature
percentile      (average_rank(current) - 1) / (N - 1)
future data     forbidden
pre-init        DATA_INSUFFICIENT
```

Profiles:

```text
EARLY        moderate 65/35  strong 80/20  escalation 2d  clear 5d
BALANCED     moderate 70/30  strong 85/15  escalation 3d  clear 5d
CONSERVATIVE moderate 75/25  strong 90/10  escalation 3d  clear 7d
```

Core boundary:

```text
volatility alone            != top
ETH/BTC leadership alone    != bearish
raw RSI alone               != top
rotation without damage     -> LATE_BULL_ROTATION candidate
exhaustion without damage   -> EXHAUSTION_WATCH candidate
exhaustion + damage         -> de-risk candidate
strong exhaustion + damage  -> hard-risk / FLAT candidate
```

Hysteresis is exactly frozen by R2: continuously supported escalation, one-step de-escalation after each fresh clear period, missing-data hold, immediate fully-proven hard FLAT and absorbing FLAT.

## Frozen evidence-output contract

`P5.3-STATE-PATH-EVIDENCE-V1` binds to:

```text
state-model blob      400ec97f8a0e522c5776ce1f6a98fc6d7e069267
P5.2 summary SHA256   3f6dc3c512d22ac8f71d43ed155f2602cd40d5caf3d617c0e130e170727e0627
profiles              EARLY / BALANCED / CONSERVATIVE
```

Event reporting uses exactly the five frozen P5.1 buckets. No custom post-result lead/lag window may be introduced.

Required artifacts:

- causal normalized percentiles;
- normalization observation counts;
- daily profile state paths with raw candidate + evidence atoms;
- profile initialization/transition summary;
- event-bucket state occupancy;
- first occurrence of each state within each frozen bucket + signed anchor offset;
- immutable summary/digest.

The run may not select a profile, production state model or P5.4 gross mapping.

## Pre-run gate — NEXT

Fresh CI must prove without running historical state paths:

- P5.3 prereg tests remain green;
- synthetic state-engine tests pass;
- future data cannot affect prior percentile values;
- rotation alone cannot de-risk;
- exhaustion requires multiple subchannels;
- escalation uses minimum continuously supported severity;
- de-escalation moves only one step per fresh clear period;
- missing data cannot re-risk;
- FLAT is immediate on hard proof and absorbing;
- runner/validator compile;
- P5.1/P5.2 immutable dependencies match;
- P5.3 result is absent.

## After pre-run green

Standing research authorization already covers:

```text
COMMIT FROZEN RUN_ONCE MARKER
EXECUTE ALL THREE PROFILES ON IMMUTABLE P5.2 PANEL
VALIDATE / COMMIT IMMUTABLE P5.3 RESULT
```

No additional owner prompt is required for this research run.

If a non-research-definition implementation defect occurs before immutable result commit, use an audited recovery record without changing features, profiles, state rules or event metrics.

## After P5.3 result

Close P5.3 by reporting state behavior across terminal, second-wind, nonterminal and control events. Do **not** select a production state model. P5.4 may then define research gross-risk behavior; P5.5 owns robustness/economic selection.

## Frozen product boundaries

- BRRK-0011 relative ranking unchanged;
- BTC/ETH/SOL/BNB long universe unchanged;
- XRP feature-only;
- Hyperliquid primary venue;
- P4.1 defensive scaler `[0,1]` unchanged;
- production gross `1.0`;
- no withdrawal/external-transfer automation;
- no production authorization.

## Exact next step

```text
CREATE DRAFT P5.3 IMPLEMENTATION PR
RUN FRESH PRE-RUN CI / GOVERNANCE
IF GREEN, COMMIT RUN_ONCE MARKER WITHOUT ASKING AGAIN
RUN P5.3 STATE-PATH EVIDENCE ONCE
VALIDATE / COMMIT IMMUTABLE RESULT
UPDATE README / CURRENT_STATE / NEXT_STEPS
MERGE P5.3 CLOSEOUT BEFORE P5.4
```
