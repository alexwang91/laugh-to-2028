# P5.3 V2 MARKET_STATE Architecture — Research Closeout

Status: **COMPLETE / IMMUTABLE EVIDENCE / ARCHITECTURE_PASS / NO PROFILE SELECTION**

This is research evidence only. It does not authorize production, live trading, re-risk after zero exposure, or any leverage increase.

## Immutable evidence

- Architecture contract: `P5.3-MARKET-STATE-PERMISSION-SEPARATION-V2`
- Evidence contract: `P5.3-V2-MARKET-STATE-PATH-EVIDENCE-V1`
- Result commit: `e732b7ebe570236bf43084caecb6ea15f7edecb8`
- Summary SHA256: `05d5d68a59c8b13f1122d98ed75d03934defdc9d73c7dd92e038c92fd97d2e52`

Immutable summary boundary:

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

## What V2 proved

V2 changed only the architecture layer: the research `MARKET_STATE` is no longer absorbing at `FLAT`. It did **not** change V1 feature inputs, percentiles, evidence atoms, raw-candidate priority, profile thresholds, persistence, clear periods, or the P5.1 event taxonomy.

All exact V1 signal-parity gates passed. The frozen `2021-02-23` false raw `FLAT` remains present.

The false-FLAT episode is now finite:

| Profile | FLAT start | FLAT end | duration | first non-FLAT |
| --- | --- | --- | ---: | --- |
| EARLY | 2021-02-23 | 2021-02-28 | 6d | 2021-03-01 |
| BALANCED | 2021-02-23 | 2021-02-28 | 6d | 2021-03-01 |
| CONSERVATIVE | 2021-02-23 | 2021-03-02 | 8d | 2021-03-03 |

Later frozen P5.1 event windows are therefore observable instead of being erased by an earlier absorbing FLAT.

## What V2 did not prove

Architecture pass is deliberately narrow. It does **not** prove:

- that the 2021-02-23 false FLAT is acceptable economically;
- that any profile is superior;
- that late-bull/exhaustion/de-risk states have optimal exposure multipliers;
- that turnover/cost/missed-upside trade-offs are acceptable;
- that any profile/mapping survives leave-one-event-out validation;
- that P5.4/P5.5 is production-ready;
- that market recovery can unlock operational risk.

The false-FLAT remains a real negative signal-quality observation and must be charged in P5.5 economic/robustness evaluation.

## Layer boundary preserved

```text
MARKET_STATE
  continuous research classification; can recover after FLAT

RISK_PERMISSION_LOCK
  operational authority; MARKET_STATE has no automatic unlock authority
```

Actual zero-exposure -> re-risk remains explicit-human-approved unless a later production governance decision says otherwise. P5.3 V2 grants no such authority.

## Disposition

```text
P5.3 V1                  COMPLETE / IMMUTABLE / NO_PROMOTION / ARCHITECTURE_FAIL
P5.3 V2 architecture     COMPLETE / IMMUTABLE EVIDENCE / ARCHITECTURE_PASS
selected P5.3 profile    NONE
selected P5.4 mapping    NONE
P5.4                     ELIGIBLE TO PREREGISTER FIXED BEHAVIOR CANDIDATES
production authorization NONE
```

P5.4 may now preregister fixed state-to-gross-risk behavior candidates. P5.4 must not select a winner. P5.5 must own joint profile/mapping robustness and economic selection using frozen event/cost/second-wind criteria.
