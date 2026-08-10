# BRRK-EXHAUSTION-TRIGGER-0045 — RESULT

Status: **FAIL_NO_DYNAMIC_GROSS_STAGE_ELIGIBILITY / DEVELOPMENT ONLY / CLOSED**

0045 tested exactly one preregistered causal HEALTHY / DECELERATION / WATCH / RISK / RECOVERY state machine on the exact researcher-exposed 0044/0043 history. It did not define portfolio gross, run portfolio economics, alter canonical BRRK-0011, modify Phase 6, or grant any production/signing/order authority.

## Execution binding

The first one-shot workflow (`31390711467`, run number 1, head `ca59056fa8944ab413829507b4bf4a3397f68596`) failed **before** the diagnostic step because a static contract test used the over-broad forbidden substring `gross_map`, which also matched the declaration key `gross_mapping_defined=false`. The diagnostic was skipped and no artifact was created. The workflow was removed, only the test expression was corrected, and a new full pre-result baseline was required.

The fully green pre-result baseline was `669942a4bef3f32894f616b9b28e5001d81e82b9`. It passed governance/no-drift, P3.2 parity, Phase 6 shadow safety and live-observation preflight, drift audit, handoff and standing contracts.

The unique valid result release was Actions run `31391109057`, run number 2, attempt 1, head `f9d4fba80bd07b8a5c67c5c3928f9081332809c7`. Before calculation it proved the only difference from the green baseline was the temporary one-shot workflow, reconfirmed the frozen preregistration/runner contracts and registry, and reran original no-drift on the exact green baseline.

```text
artifact id                          9063704951
artifact digest                      sha256:0f8cd31ca3905d798194387622456fc8e59cb786376e57a6c135bdb2867c9c04
full result SHA256                   06714848cbb8c812a655700c29362487fc9e77ef2638f57547c7340ee10a2682
artifact summary SHA256              5530a4e922d2219a012e0914f43d1f328ee92ee45724a582189176d37d05ab59
result payload self-excl SHA256      38d8a8d7cd2d7ff58d0c29354f384b04ed3d9860cd7b97da10fa62d293ca66c5
```

## Source reproduction

The runner reproduced the exact frozen 0043 taxonomy before trigger evaluation:

```text
candidate peaks                  16
10% panel                        12 TRUE / 4 CONTINUATION / 0 AMBIGUOUS
15% primary panel                 9 TRUE / 6 CONTINUATION / 1 AMBIGUOUS
20% severe panel                  7 TRUE / 6 CONTINUATION / 3 AMBIGUOUS
status                            MATCHED_0043_FROZEN_TAXONOMY
parent 0044                       PASS_TRIGGER_STAGE_ELIGIBLE
```

No observations after `2026-08-02` were used.

## Frozen hard-gate result

The first state machine is highly specific but insufficiently sensitive:

```text
episode diversity                                  PASS
primary TRUE PRE14_7 WATCH/RISK      3 / 9 = 33.3% FAIL  (need >=50%)
primary CONT PRE14_0 false WATCH/RISK 0 / 6 = 0.0% PASS  (need <=34%)
primary TRUE episode hit             2 / 5 = 40.0% FAIL  (need >=60%)
primary CONT episode false            0 / 5 = 0.0% PASS  (need <=50%)
severe TRUE PRE14_7 WATCH/RISK       3 / 7 = 42.9% FAIL  (need >=57%)
severe TRUE PRE7_POST3 RISK          2 / 7 = 28.6% FAIL  (need >=57%)
primary CONT PRE14_POST3 RISK         0 / 6 = 0.0% PASS  (need <=17%)
qualifying PRE21_0 TRUE onsets                    0 FAIL  (need >=4)
premature-clear gate                    no denominator FAIL
construction / zero-authority                         PASS
```

Final classification:

```text
FAIL_NO_DYNAMIC_GROSS_STAGE_ELIGIBILITY
```

## Which genuine exhaustion events were captured

Primary TRUE events with WATCH/RISK in PRE14_7:

- `2024-06-05`
- `2024-07-21`
- `2025-10-08`

The machine did **not** produce a PRE14_7 WATCH/RISK hit for important genuine exhaustion events including `2023-12-25`, `2024-03-31`, `2024-12-17`, and `2025-01-18`.

For the user-important October-2025 region, `2025-10-08` was caught in PRE14_7 WATCH/RISK, but it did not escalate to RISK in PRE7_POST3. Thus even one of the strongest desired examples did not satisfy the frozen near-peak RISK-confirmation objective.

## Zero false-top events does not mean a sparse trigger

All six primary continuation / false-top events had zero PRE14_0 WATCH/RISK false triggers, and all six had zero PRE14_POST3 RISK false triggers. This is positive specificity evidence, but it must not be interpreted as a globally rare risk state.

Daily state occupancy across 1,332 sessions was:

```text
HEALTHY        630 sessions   47.30%
DECELERATION   228 sessions   17.12%
WATCH          217 sessions   16.29%
RISK           241 sessions   18.09%
RECOVERY        16 sessions    1.20%
WATCH + RISK                  34.38%
non-HEALTHY                   52.70%
```

The frozen state machine therefore spends about one-third of the entire history in WATCH/RISK even though the six mechanically defined continuation-event windows happen not to overlap those states. Mapping these states directly to reduced portfolio gross would consequently risk substantial opportunity cost and is not authorized.

## Transition-onset failure and hysteresis interpretation

The primary TRUE PRE21_0 onset count was `0`. This is not because no TRUE event was ever in WATCH/RISK: three were hit in PRE14_7. Rather, for those captured events the machine was already in WATCH/RISK before the frozen PRE21_0 window, so no new transition from below WATCH occurred inside the requested one-to-three-week lead window.

This is important negative evidence. The first state machine behaves more like a persistent risk-regime label than a precise one-to-two-week action trigger. Its slow-recovery hysteresis may help specificity, but in this frozen form it is too sticky to satisfy the requested timing semantics. Because no qualifying onsets existed, the preregistered premature-clear denominator was zero; that hard gate therefore fails rather than being treated as a free PASS.

## Governance interpretation

0044 remains a valid closed PASS showing that exhaustion **ranking/state information exists**. 0045 separately shows that this particular absolute percentile/persistence/hysteresis translation does **not** turn that information into an acceptable operational trigger.

No same-ID rescue is allowed. Specifically, 0045 may not now:

- lower WATCH/RISK percentiles;
- shorten or alter persistence;
- widen the onset window;
- change recovery hysteresis;
- use S2 alone;
- reweight CORE4;
- reintroduce S5 volume, breadth or correlation;
- try a threshold grid;
- run gross/portfolio economics.

A different trigger architecture would require a new result-informed research ID and a fresh preregistration. The preregistered dynamic-gross stage is **not eligible** from 0045.

```text
dynamic_gross_stage_eligible       false
gross_mapping_defined              false
portfolio_economics_executed       false
canonical_strategy_changed         false
phase6_observation_changed         false
production_authorized              false
signature_authorized               false
order_submission_authorized        false
same-ID rerun allowed              false
same-ID retuning allowed           false
```
