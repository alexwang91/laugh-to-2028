# BRRK-EXHAUSTION-STATE-0044 — RESULT

Status: **PASS_TRIGGER_STAGE_ELIGIBLE / DEVELOPMENT ONLY / CLOSED**

0044 tested the preregistered low-dimensional exhaustion state on the exact researcher-exposed 0043 history. It did not define a trigger, simulate a portfolio, change BRRK targets, alter Phase 6, or grant any production/signing/order authority.

## Execution binding

The first workflow run (`31387906469`, run number 1) failed **before** the diagnostic step because the temporary workflow file itself was correctly rejected by the original no-drift regression. It created no artifact and is retained as a pre-result infrastructure failure, not a research result.

The unique valid result release was GitHub Actions run `31388103016`, run number 2, attempt 1, from head `9affc7572dd0feefb14fe41e2aea7904c3a132ba`, after proving that the only change from the fully green pre-result baseline `f6fd1fc3425fefdc6bd024fa032a065accab7c6e` was the temporary one-shot workflow. The original no-drift regression was also rerun against that exact green baseline before calculation.

```text
artifact id                     9062525981
artifact digest                 sha256:b109b610710b00904c924680a63305579f3f3c4c799d539906e0853629ddd378
full result SHA256              687ff49d8db8baf54a1cfafcf8863c848011800b6c74689ab0534796ac86ff29
artifact summary SHA256         96eeeb4627bc115c6b7752ddf903f290c34b62345512738a4030623e4c212ae0
result payload self-excl SHA256 1b0c3a87737f0d4cf48b20694fa614fc38fcc24732212544fab4ea5350b563c7
```

## Source reproduction gate

Before scoring, the runner reproduced the exact frozen 0043 taxonomy:

```text
candidate peaks                  16
10% panel                        12 TRUE / 4 CONTINUATION / 0 AMBIGUOUS
15% primary panel                 9 TRUE / 6 CONTINUATION / 1 AMBIGUOUS
20% severe panel                  7 TRUE / 6 CONTINUATION / 3 AMBIGUOUS
status                            MATCHED_0043_FROZEN_TAXONOMY
```

No observations after `2026-08-02` were used.

## Primary hard gates

All preregistered CORE4 gates passed:

```text
usable macro episodes                         7   PASS (>=4)
TRUE episodes                                 5   PASS (>=2)
CONTINUATION episodes                         4   PASS (>=2)
15% PRE14_7 CORE4 cross-episode AUC        0.750 PASS (>=0.70)
15% PRE14_7 CORE4 event-level AUC          0.778 PASS (>=0.68)
20% PRE14_7 CORE4 cross-episode AUC        0.750 PASS (>=0.75)
LOEO minimum cross-episode AUC              0.654 PASS (>=0.55)
LOEO median cross-episode AUC               0.739 PASS (>=0.68)
construction / causal / authority gate          PASS
```

The eight leave-one-episode-out influence AUCs were:

`0.750, 0.786, 0.654, 0.786, 0.727, 0.727, 0.885, 0.679`.

This means the PASS is not solely produced by one mechanically detected macro episode, although the evidence remains retrospective and researcher-exposed rather than independent OOS.

## State-axis evidence

Primary `-15%`, 7–14 days before the local peak, cross-episode AUC:

```text
CORE4                         0.750
S2 trend disagreement        0.744
S3 price structure           0.676
S4 volatility/downside       0.583
S1 momentum deceleration     0.565
S5 volume confirmation       0.500
```

Primary `-15%`, final week before the local peak:

```text
S2 trend disagreement        0.893
CORE4                         0.736
S3 price structure           0.681
S4 volatility/downside       0.569
S5 volume confirmation       0.528
S1 momentum deceleration     0.347
```

Severe `-20%`, 7–14 days before the peak:

```text
S2 trend disagreement        0.833
CORE4                         0.750
S3 price structure           0.731
S1 momentum deceleration     0.593
S4 volatility/downside       0.583
S5 volume confirmation       0.500
```

S2 is therefore the strongest exposed component in this frozen run. That observation may inform a **new** trigger-stage preregistration, but 0044 may not be retrospectively changed to select S2 alone or reweight CORE4.

## Volume confirmation — preserved negative evidence

The secondary CORE5 representation added S5 volume confirmation to the four primary axes. It made discrimination worse:

```text
PRE14_7 CORE4                 0.750
PRE14_7 CORE5                 0.676
CORE5 minus CORE4            -0.074

PRE7_0 CORE4                  0.736
PRE7_0 CORE5                  0.606
CORE5 minus CORE4            -0.130
```

S5 alone had primary PRE14_7 cross-episode AUC `0.500`. This negative evidence is retained. Volume/OBV features are not promoted into the core merely because they were an intuitively plausible research direction.

## Dimensionality

The five state axes have effective-rank participation ratio about `3.068`, materially lower than five but much cleaner than the 48-feature 0043 representation. S1 is nearly orthogonal to the other axes, while S2/S3/S4/S5 have moderate positive dependence.

## Interpretation and authority

0044 answers one narrow question: **a frozen low-dimensional exhaustion state retains useful 7–14 day discrimination after macro-episode dependence control.** It does not answer when to reduce risk or how much risk to remove.

A PASS therefore creates eligibility only for a separately preregistered trigger-stage study. Under 0044:

```text
trigger_defined                    false
portfolio_economics_executed       false
canonical_strategy_changed         false
phase6_observation_changed         false
production_authorized              false
signature_authorized               false
order_submission_authorized        false
same-ID rerun allowed              false
same-ID retuning allowed           false
```

`RUN_ONCE.marker` is permanent. No 0044 rescue, reweighting, feature pruning/addition, alternative episode rule, threshold search, persistence search, or gross mapping is permitted.
