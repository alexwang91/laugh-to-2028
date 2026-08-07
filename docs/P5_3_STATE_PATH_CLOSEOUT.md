# P5.3 State-Path Evidence V1 — Research Closeout

Status: **COMPLETE / IMMUTABLE / NO_PROMOTION / ARCHITECTURE_FAIL**

This document records research evidence only. It does not authorize live trading, production deployment, leverage changes, or capital allocation.

## Immutable result

- State-model contract: `P5.3-STATE-MODEL-STRUCTURE-V1`
- Evidence contract: `P5.3-STATE-PATH-EVIDENCE-V1`
- Result commit: `7703b3ffec906a9d2ea58b33ee7feea5cd2f0a89`
- Summary SHA256: `a2e5ece89fec93a24e1a65e134a78824629b4b418e106294a6b0821fbd52608b`
- `profile_selected=false`
- `state_model_production_selected=false`
- `production_authorized=false`

## Main finding

All three frozen profiles entered `FLAT` on `2021-02-23` and, because V1 defined FLAT as absorbing, remained FLAT for almost the entire remaining sample.

| Profile | Initialization | First FLAT | Classified days | FLAT days | FLAT fraction |
| --- | --- | --- | ---: | ---: | ---: |
| EARLY | 2021-01-11 | 2021-02-23 | 1874 | 1837 | 98.0256% |
| BALANCED | 2021-01-11 | 2021-02-23 | 1874 | 1837 | 98.0256% |
| CONSERVATIVE | 2021-01-11 | 2021-02-23 | 1874 | 1837 | 98.0256% |

No profile is eligible for promotion to P5.4.

## False hard-risk event

`2021-02-23` lies inside the frozen `P5C-2021-JAN-FEB-HIGH-VOL` event, which P5.1 deliberately labels `HIGH_VOLATILITY_NON_TOP_CONTROL`.

In that control's `near_event` bucket (`2021-02-22 .. 2021-02-28`), every profile spends 6 of 7 classified days in FLAT: `0.857142857`.

The trigger is not caused by warm-up or missing data. On `2021-02-23` every profile has:

```text
ordinary_inputs_complete   true
minimum_calibration_depth  57
exhaustion                 true
strong_exhaustion          true
damage                     true
strong_damage              true
raw_candidate_state        FLAT
```

For example, the normalized evidence includes approximately:

```text
btc_kama_gap                         0.0552
btc_log_return_40d                   0.0190
btc_distance_from_90d_high           0.2321
btc_price_rsi_rank_divergence_20d    0.8532
btc_rsi14_failure_from_14d_max       0.8409
breadth_contraction_from_10d_max     0.8235
breadth_acceleration_10d             0.1250
```

The frozen hard-risk condition therefore genuinely fires in a nonterminal control window.

## Architecture issue exposed by the result

The immutable result also shows that the underlying raw market classification recovered quickly after the false FLAT:

```text
2021-02-27 raw candidate  DE_RISK_2
2021-02-28 raw candidate  NORMAL_BULL
2021-03-01 raw candidate  NORMAL_BULL
2021-03-09 raw candidate  BTC_LEADERSHIP_MATURING
```

However, the published V1 state remained FLAT because the research state variable itself was absorbing.

This demonstrates that V1 combined two concepts that should be studied separately:

1. a market-state classifier, which should continue describing later recovery or deterioration;
2. a separate operational permission boundary, where any future live re-entry after a zero-exposure state remains subject to explicit human approval.

The human-approval boundary is unchanged. The research problem is that making the market-state history absorbing prevents evaluation of later market regimes.

## Disposition

```text
P5.3-STATE-MODEL-STRUCTURE-V1  COMPLETE / IMMUTABLE / NO_PROMOTION
P5.3-STATE-PATH-EVIDENCE-V1    COMPLETE / IMMUTABLE
selected profile               NONE
P5.4 eligible profile          NONE
production authorization       NONE
```

V1 must not be rerun, retuned, or rewritten. In particular, do not alter V1 thresholds, profiles, event windows, or immutable outputs to remove the 2021-02-23 failure.

## Next research hypothesis

P5.4 remains blocked. The next step is a separately preregistered P5.3 V2 research architecture that separates continuous **market-state classification** from the existing human-gated operational permission boundary.

For the first V2 architecture-isolation study, keep V1 feature inputs, evidence atoms, percentile thresholds, and EARLY/BALANCED/CONSERVATIVE profile values unchanged. This allows the effect of the architecture separation to be measured without simultaneously tuning the signal rules.

The temporary false FLAT in the non-top control remains evidence that later robustness/economic validation must account for; it must not be hidden by the architecture change.

Production gross remains `1.0`; production authorization remains empty.
