# BRRK Current State

Last updated: **2026-08-11**  
Authoritative repository: `alexwang91/laugh-to-2028`  
Authoritative baseline main: **`5d3e5b57c861b2a544db5da7456e78e17e818b12`**  
Latest merged research-design PR: **#174** — dynamic leadership router 0048 architecture  
Status of this document: **AUTHORITATIVE SNAPSHOT — replace stale cumulative handoff text with current program state**

> GitHub `main` remains the source of truth. This file is a compact operating snapshot, not a substitute for immutable preregistration, result, execution, recovery, artifact, or closeout files.

---

## 1. Executive state

```text
Phase 0-3                              COMPLETE / MERGED
Phase 4 leverage research             FAIL_STOP / NO_PROMOTION
P5.5                                   COMPLETE / IMMUTABLE / NO_PROMOTION / FAIL_STOP
F27 idle-cash measurement             R2 AUTHORITATIVE / R1 SUPERSEDED-PRESERVED
F7 metrics convergence                PARTIAL

Phase 6 ARM                            ACTIVE FUTURE-ONLY OBSERVATION
Phase 6 ARM marker                     cbd58adb05187651ca72d67900a0ccbbd3e83b1e
Phase 6 daily schedule                 00:00 UTC
Phase 6 genuine scheduled credit       1 / >=10
Phase 6 emergency drills               0 / >=1
Phase 6 elapsed requirement            NOT MET
Phase 6 live acceptance                MEASUREMENT_INCONCLUSIVE_TIME_DEPENDENT

BRRK opportunity-cost audit 0042       COMPLETE DIAGNOSTIC / NO PROMOTION AUTHORITY
BRRK-WINNER-0001                       PASS_ROBUSTNESS_STAGE_ELIGIBLE / DEVELOPMENT / CLOSED
BRRK-WINNER-ROBUSTNESS-0002            PASS_FUTURE_ONLY_VALIDATION_STAGE_ELIGIBLE / DEVELOPMENT / CLOSED
BRRK exhaustion event study 0043      COMPLETE DIAGNOSTIC / CLOSED
BRRK exhaustion state 0044            PASS_TRIGGER_STAGE_ELIGIBLE / CLOSED
BRRK exhaustion trigger 0045          FAIL_NO_DYNAMIC_GROSS_STAGE_ELIGIBILITY / CLOSED
BRRK exhaustion pulse 0046            FAIL_NO_FUTURE_ONLY_PULSE_VALIDATION_ELIGIBILITY / CLOSED
BRRK Beta handoff event study 0047    FAIL_NO_RECURRENT_DURABLE_HANDOFF_STRUCTURE / CLOSED
BRRK leadership rotation 0048         ARCHITECTURE FROZEN / NUMERICAL PREREG NOT FROZEN / NOT RUN

Phase 7                                MONITOR_ONLY / LAUNCH BLOCKED
Phase 8                                TRIGGER ABSENT / NOT RUN
Canonical BRRK-0011                    NO CHANGE
Production                             NO CHANGE
Signing                                NOT AUTHORIZED
Order submission                       NOT AUTHORIZED
```

The active research frontier is **0048 numerical-method design**. No 0048 historical measurement, dataset registration, model fit, runner, portfolio test, or candidate evaluation exists.

---

## 2. Current strategic thesis

The current research program no longer assumes a universal one-way sequence:

```text
BTC -> Beta
```

The architecture frozen in 0048 is a two-dimensional router:

1. **Leadership** decides which crypto asset should receive the risk budget.
2. **Exhaustion / market risk** decides how much Beta / crypto gross the portfolio should still tolerate.

Frozen qualitative leadership states:

```text
BTC_LEAD
ETH_LEAD
SOL_LEAD
NO_CLEAR_LEADER / TRANSITION
```

BTC, ETH and SOL must be treated as symmetric competitors with independent leadership clocks. Valid future state paths may include:

```text
BTC -> SOL -> BTC -> ETH
BTC -> ETH -> BTC
SOL -> BTC
BTC -> cash
```

The frozen economic principle is:

> **Concentrate during verified upside leadership; re-anchor to BTC when leadership quality or market risk deteriorates; use cash only for broader gross-risk reduction.**

Important separation:

```text
Leadership reversal  -> winner -> BTC       (return / stale-leader problem)
Exhaustion compression -> winner -> BTC     (risk-quality problem)
Broader risk failure -> BTC -> cash         (gross-risk problem)
```

These mechanisms must remain separately attributable in future studies.

Source: `research/governance/BRRK_LEADERSHIP_ROTATION_0048_ARCHITECTURE_FREEZE_2026-08-11.md`.

---

## 3. 0048 — current frontier, design only

Research object:

`BRRK-LEADERSHIP-ROTATION-0048`

Current status:

```text
architecture frozen                  true
numerical preregistration frozen     false
dataset registered                   false
runner / model implemented           false
historical measurement released      false
actual variants evaluated            0
portfolio allocation tested          false
portfolio economics executed         false
canonical strategy changed           false
Phase 6 changed                       false
production / signing / orders        false
```

### 3.1 Revised scientific question

0048 asks:

> Within an already-confirmed crypto uptrend, does leadership rotate among BTC, ETH and SOL in persistent, causally identifiable states, rather than reducing to a static ordering where the same high-Beta asset should simply always be held?

The required adversarial null is deliberately strong:

> **Static-Beta null:** if ETH/SOL are almost always superior once crypto is in an uptrend, dynamic BTC/winner rotation adds no information.

0048 must therefore demonstrate **alternation + persistence + causal identifiability**, not merely that SOL or ETH has the highest average historical return.

### 3.2 Required information layers

**Market / diffusion layer** may consider:

- canonical BTC absolute fast/slow trend;
- cross-asset breadth and diffusion;
- ETH/BTC and SOL/BTC broadening;
- participation / liquidity expansion;
- BTC Dominance only if a reproducible historical source is independently frozen.

**Asset leadership layer** must be symmetric and pairwise across BTC / ETH / SOL and may consider:

- absolute fast/slow trend;
- pairwise fast relative trend;
- pairwise slow relative trend;
- fast-minus-slow relative acceleration;
- leadership margin versus runner-up;
- participation / liquidity confirmation;
- market diffusion context.

BTC Dominance is a **market-diffusion variable only**, not a direct ETH/SOL winner selector. No price-only proxy may be relabeled as BTC Dominance.

### 3.3 Numerical items deliberately not frozen yet

The following must be solved in the next no-result design pass before preregistration:

1. exact forward leadership target;
2. exact primary horizon / path definition;
3. exact causal feature construction and normalization;
4. exact symmetric leadership representation;
5. exact `NO_CLEAR_LEADER` / confidence definition;
6. static-Beta / always-BTC / simple-momentum adversarial controls;
7. episode/block validation rule;
8. numerical PASS/FAIL gates;
9. candidate/model budget;
10. whether BTC Dominance has a reproducible source good enough for primary analysis.

No historical sweep is allowed to select these choices.

### 3.4 Revised research sequence

```text
0048  Leadership Rotation Information Stage
      prove BTC / ETH / SOL leadership alternates and is causally identifiable
      NO portfolio allocation test

0049  Winner Concentration Portfolio Economics
      only if 0048 passes
      compare existing 60% winner benchmark with a small preregistered aggressive family
      owner hypothesis: economically relevant winner region may be ~80%-100% of crypto risk budget

0050  Winner -> BTC Risk Re-anchor
      separate leadership-reversal route from exhaustion-compression route

0051  BTC -> Cash Gross Brake
      broader market-risk deterioration only
      correct investment-basis cash credit required

0052  Integrated Router
      leadership + BTC re-anchor + gross brake
      future-only validation required before canonical / production use
```

The numbering is a roadmap, not automatic eligibility.

---

## 4. 0047 — immutable negative result and what it changed

Research ID:

`BRRK-BETA-HANDOFF-EVENT-STUDY-0047`

Status:

`FAIL_NO_RECURRENT_DURABLE_HANDOFF_STRUCTURE / CLOSED`

Authoritative result:

```text
total BTC-positive episodes                 27
target-eligible BTC-positive episodes       27
primary durable handoff episodes            12
prevalence                                  12 / 27 = 44.4444%
ETH primary handoff causes                   3
SOL primary handoff causes                   9
only failed hard gate                        episode-level prevalence >= 0.50
```

Additional non-gating diagnostics that motivated the redesign:

```text
handoffs at state_age = 1                   8 / 12
handoff state-age median                    1
BTC/ETH pooled cross-correlation peak lag   0
BTC/SOL pooled cross-correlation peak lag   0
one-switch oracle positive uplift           17 / 27
oracle-positive without frozen durable label 7 episodes
```

Interpretation:

- 0047 **does not** prove rotation is absent.
- It rejects the frozen assumption that `BTC_TREND_FAST >= 0` is a clean leadership clock from which a recurrent later ETH/SOL handoff can be timed.
- It also rejects a universal fixed BTC-leading delay as the central model.
- The result is researcher-exposed DEVELOPMENT history, not independent OOS evidence.
- No same-ID rerun, retune, rescue, label relaxation, hazard-model continuation, or portfolio translation is allowed.

Evidence authority is the immutable 0047 result/recovery/closeout bundle under `research/brrk_beta_handoff_0047/`.

### 4.1 0047 evidence-recovery governance correction

During the 0048 architecture PR, standing CI exposed three closeout-governance defects:

1. three recovered evidence hash identities in closeout/docs/tests did not match the already-existing authoritative recovery evidence;
2. two standing lifecycle tests still enforced a pre-result `result files must not exist` rule after 0047 had become CLOSED;
3. a stale write-enabled temporary closeout workflow remained on `main`.

These were mechanically corrected without rerunning 0047 or changing any scientific result/gate/method.

Authoritative hash identities now remain separated correctly:

```text
PRIMARY_RESULT pre-serialization object
961ac99bd5a2d3d6556262b17411333bfbeead921616dccf120190ee1dd67c2a

PRIMARY_RESULT recovered raw JSON file
6c354b054bde2dfce12dbb1efe3809d59d371df02beddc613befe9373a17807d

PRIMARY_RESULT reparsed canonical JSON
35f0ee3934d45e19b5b652fa13b0cfa1f328aac51843ac9432e8cc94d20dd6b8

EXECUTION pre-serialization object
a87e37ae41e20d71e61dd52fb0b20009a5a6c6ffeeb6d0eb3d6faab568604665

RUN_ONCE marker object
9487c61867e9c2862d1d0a57396440382768c113596a280eff5fd0142c7efcc6
```

See `research/governance/BRRK_0047_CLOSEOUT_GOVERNANCE_CORRECTION_2026-08-11.md`.

---

## 5. Winner-concentration lineage — positive DEVELOPMENT evidence

### 5.1 Opportunity-cost audit 0042

The audit established that the strongest historical rigidity was portfolio construction rather than the defensive scaler:

```text
V1 CAGR                                 61.3150%
BRRK CAGR                               65.1702%
BRRK - V1 CAGR                          +3.8551 pp
V1 max drawdown                         -37.6349%
BRRK max drawdown                       -33.7151%
BRRK MDD improvement                    +3.9198 pp
BRRK top-20 V1 growth-day capture       ~100%
alt-active days                         590
BTC >= 50% of gross on alt-active days 70.1695%
```

Interpretation: existing BRRK remained structurally BTC-heavy even when alts were active.

### 5.2 BRRK-WINNER-0001

Status:

`PASS_ROBUSTNESS_STAGE_ELIGIBLE / DEVELOPMENT / CLOSED`

Frozen 40/60 single-alt candidate:

```text
canonical CAGR                 65.3057%
candidate CAGR                 69.6917%
CAGR delta                     +4.3860 pp
canonical MDD                  -33.5292%
candidate MDD                  -33.4499%
canonical Calmar               1.9477
candidate Calmar               2.0835
right-tail capture             103.5595%
turnover ratio                 1.1229x
```

### 5.3 BRRK-WINNER-ROBUSTNESS-0002

Status:

`PASS_FUTURE_ONLY_VALIDATION_STAGE_ELIGIBLE / DEVELOPMENT / CLOSED`

The exact 40/60 candidate survived the preregistered time/cost robustness panel, including 10/20 bps stress. Negative evidence is retained: temporal block T2 had candidate CAGR delta `-1.7365 pp`, although the aggregate 2/3 temporal gate passed.

This lineage motivates later testing of a more aggressive high-confidence winner region, but **does not prove** that 80%, 90% or 100% winner concentration is optimal.

No same-ID reallocation rescue/grid is allowed under 0001 or 0002.

---

## 6. Exhaustion lineage — information exists, trigger translations failed

### 6.1 BRRK-EXHAUSTION-EVENT-STUDY-0043

Status: complete DEVELOPMENT diagnostic / closed.

The historical event study found useful 7-14 day relative risk-ranking information. Primary `-15%` PRE14_7 AUCs included:

```text
EXHAUSTION_SCORE             0.7333
F7 disagreement              0.7556
F4 volatility/downside       0.7111
F1 momentum decay            0.6889
F2 price structure           0.6889
```

For severe `-20%` events, total PRE14_7 AUC was approximately `0.8571`.

0043 did **not** authorize an operational threshold or gross map.

### 6.2 BRRK-EXHAUSTION-STATE-0044

Status:

`PASS_TRIGGER_STAGE_ELIGIBLE / CLOSED`

Frozen CORE4 axes:

```text
S1 momentum deceleration
S2 trend disagreement
S3 price structure
S4 volatility / downside
CORE4 = equal mean(S1,S2,S3,S4)
```

Key frozen evidence:

```text
PRE14_7 CORE4 cross-episode AUC    0.750
PRE14_7 event AUC                  0.777777...
PRE7_0 cross-episode AUC           0.736111...
severe20 PRE14_7                   0.750
LOEO min / median / max            0.653846 / 0.738636 / 0.884615
```

Adding the volume axis as CORE5 worsened primary performance. 0044 therefore remains positive evidence for **continuous relative risk ranking**, not a portfolio trigger.

### 6.3 BRRK-EXHAUSTION-TRIGGER-0045

Status:

`FAIL_NO_DYNAMIC_GROSS_STAGE_ELIGIBILITY / CLOSED`

The frozen WATCH/RISK state machine was specific but too insensitive/sticky:

```text
primary TRUE PRE14_7 WATCH/RISK       3 / 9 = 33.3%   FAIL
primary CONT false WATCH/RISK         0 / 6           PASS
primary TRUE episode hit              2 / 5           FAIL
severe TRUE PRE14_7 WATCH/RISK        3 / 7           FAIL
qualifying PRE21_0 TRUE onsets        0               FAIL
WATCH + RISK full-history occupancy   34.38%
```

Interpretation: the particular absolute state-machine translation failed. This does **not** invalidate 0044 ranking information.

### 6.4 BRRK-EXHAUSTION-PULSE-0046

Status:

`FAIL_NO_FUTURE_ONLY_PULSE_VALIDATION_ELIGIBILITY / CLOSED`

The ARL365 transition-pulse translation solved some 0045 stickiness but became far too sparse:

```text
eligible detector sessions             1026
raw alarm sessions                     19
raw alarm occupancy                    1.85185%
raw alarm spells                       1
spell length                           19 days
transition pulses                      1
pulse date                             2026-06-03
TRUE PRE14_7 pulse hit                 0 / 9
TRUE episode PRE14_7                   0 / 5
severe TRUE PRE14_7                    0 / 7
qualifying TRUE PRE21_0 onsets         0
truncated ARL0                         365.0472
```

The one pulse did not land inside a frozen TRUE exhaustion lead window. 0046 is binding negative evidence for this pulse architecture, not evidence that continuous exhaustion information is useless.

---

## 7. Binding lesson from smooth gross control 0038

`EXPOSURE-SMOOTH-0038-CONTINUOUS-BETA` remains:

`MECHANISM_VALIDATED_NOT_PROMOTED_BASELINE_UNCHANGED`

Historical comparison:

```text
                         baseline        smooth
CAGR                     0.3638168       0.3413029
MDD                     -0.5971708      -0.4319886
vol                      0.48094         0.37696
Sharpe                   0.8881          0.96646
Calmar                   0.6092          0.79007
turnover               132.97          121.31
avg gross                 0.70303         0.59826
```

Binding interpretation:

> Lower volatility / shallower drawdown is not sufficient if bull-market upside and CAGR are sacrificed too heavily.

Future risk-control success must include **net CAGR and right-tail opportunity cost**, not only MDD/Sharpe.

---

## 8. Phase 6 — independent future-only observation

Phase 6 remains completely independent of the 0042-0048 research line.

Frozen ARM / acceptance:

```text
ARM commit                          cbd58adb05187651ca72d67900a0ccbbd3e83b1e
schedule                            daily 00:00 UTC
minimum elapsed calendar days       14
minimum genuine scheduled decisions 10
minimum emergency drills             1
critical reconciliation errors       0
unexplained target drift              0
schedule failures                     0
production_authorized              false
signature_authorized               false
order_submission_authorized        false
```

Repository accounting index currently records:

```text
genuine scheduled decisions          1 / >=10
emergency drills                     0 / >=1
distinct credited decision dates     1
critical reconciliation errors       0 observed
unexplained target drift              0 observed
schedule failures                     0 observed
elapsed requirement                  NOT MET
live acceptance                      MEASUREMENT_INCONCLUSIVE_TIME_DEPENDENT
```

The first credited genuine scheduled decision remains `2026-08-10T00:00:00Z`, backed by durable Actions evidence + separate hash-bound receipt. The repository-side ledger is an accounting index only and cannot create or backfill credit.

Manual dispatch, rerun, replay and duplicate timestamps remain non-crediting.

Source: `research/governance/phase6_observation_ledger.json` and frozen Phase-6 contracts.

---

## 9. Portfolio-economics conventions for later stages

These are not 0048 result rules, but remain binding for later portfolio studies.

### 9.1 P3.3 execution semantics

Use the repository's existing economic execution semantics from `research/leverage_0040/study_core.py`:

- decision on date `t` compares target with drifted current economic weights;
- execute target only when L1 gap reaches the frozen band;
- repository standard L1 band: `0.05`;
- primary transaction cost: `5 bps`;
- stress costs: `10 / 20 bps`;
- executed turnover = sum of absolute accepted-current weight changes;
- accepted weights earn the next session return;
- long-only unless a separately governed future study states otherwise.

### 9.2 Risk-free cash

New experiments must use investment-basis cash accounting from `research/common/risk_free.py` rather than the legacy discount-basis loader.

Both baseline idle cash and candidate idle cash must receive the same correct cash credit. Candidate-only cash credit is forbidden.

---

## 10. Governance invariants

All future formal research remains subject to the lifecycle:

```text
design
-> design merge
-> preregistration
-> prereg merge
-> implementation
-> one valid execution
-> immutable closeout
```

Non-negotiable rules:

- GitHub live `main` is the source of truth.
- Never invent SHA, run ID, artifact, file, result or authority.
- Preserve negative evidence.
- After one valid result, no same-ID rerun / retune / rescue.
- Result-informed continuation requires a new research ID.
- Random daily-row train/test splits are not acceptable where episode dependence matters.
- Researcher-exposed DEVELOPMENT history must not be described as independent OOS.
- A failed threshold/state/pulse translation must not be reinterpreted as absence of underlying ranking information.
- No result-bearing portfolio allocation may be smuggled into an information-stage study.
- Canonical strategy, Phase 6, production, signing and order authority remain unchanged unless separately and explicitly gated.

---

## 11. Exact permitted next research action

The only permitted next **0048 research** action is:

> **A no-result numerical-method design pass for 0048 preregistration.**

Before any historical 0048 run, that design pass must freeze:

1. forward leadership target and primary metric;
2. horizon / path semantics;
3. causal leadership feature construction;
4. symmetric BTC/ETH/SOL representation;
5. `NO_CLEAR_LEADER` confidence/margin rule;
6. always-BTC / always-ETH / always-SOL / simple relative-momentum / current-winner adversarial controls;
7. episode-preserving validation structure;
8. churn / persistence diagnostics;
9. numerical PASS/FAIL gates;
10. candidate/model budget;
11. BTC Dominance source decision or explicit exclusion from primary analysis.

Until that numerical design is explicitly approved and preregistered, **do not**:

- register an 0048 result dataset;
- implement an 0048 runner/model;
- run historical 0048 metrics;
- sweep horizons or thresholds;
- fit a classifier;
- test 80/90/100 winner allocation;
- run CAGR / Sharpe / MDD / Calmar economics;
- search CORE4-to-BTC rules;
- define BTC-to-cash gross mapping;
- change canonical BRRK or Phase 6.

---

## 12. Key source files

```text
0048 architecture
research/governance/BRRK_LEADERSHIP_ROTATION_0048_ARCHITECTURE_FREEZE_2026-08-11.md

0047 immutable closeout
research/brrk_beta_handoff_0047/CLOSEOUT.json
research/brrk_beta_handoff_0047/RESULT.md
research/brrk_beta_handoff_0047/EVIDENCE_RECOVERY.json

0047 governance correction note
research/governance/BRRK_0047_CLOSEOUT_GOVERNANCE_CORRECTION_2026-08-11.md

0046 immutable result
research/brrk_exhaustion_pulse_0046/RESULT.md

0045 immutable result
research/brrk_exhaustion_trigger_0045/RESULT.md

0044 state research
research/brrk_exhaustion_state_0044/

Winner lineage
research/brrk_winner_0001/
research/brrk_winner_robustness_0002/

Phase 6 accounting index
research/governance/phase6_observation_ledger.json

Risk-free accounting
research/common/risk_free.py

P3.3 economics
research/leverage_0040/study_core.py
```

---

## 13. Authority summary

```text
0048 historical result authority     none
0048 portfolio authority             none
0049 eligibility                     blocked pending 0048 PASS
0050 eligibility                     blocked
0051 eligibility                     blocked
0052 eligibility                     blocked
canonical BRRK change                false
Phase 6 research change              false
production authorization             false
signature authorization              false
order-submission authorization        false
```

**Current program frontier: design the 0048 numerical method correctly before touching history.**
