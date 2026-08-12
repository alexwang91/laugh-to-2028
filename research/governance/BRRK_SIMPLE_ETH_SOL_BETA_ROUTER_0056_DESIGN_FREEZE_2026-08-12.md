# BRRK-SIMPLE-ETH-SOL-BETA-ROUTER-0056 — DESIGN FREEZE

Date: 2026-08-12  
Status: **DESIGN FROZEN / NUMERICAL PREREG NOT YET FROZEN / NOT IMPLEMENTED / NOT RUN**

## 1. Research identity and non-negotiable interpretation

Research ID: `BRRK-SIMPLE-ETH-SOL-BETA-ROUTER-0056`  
Family: `BRRK_DYNAMIC_LEADERSHIP_ROUTER`  
Purpose: direct causal ETH/SOL Beta-sleeve portfolio economics.

0056 is a **new research ID**, not a rerun, rescue or retuning path for 0048, 0053, 0054 or 0055. The prior probability/readiness architecture is closed under those IDs. 0056 deliberately changes the scientific question from calibrated leadership prediction to a single fixed causal portfolio rule.

The economic objective is primary and binding:

> maximize causal net terminal wealth and net CAGR under a prospectively frozen full-history evaluation rule.

MDD, Sharpe, calibration quality and model elegance are not optimization objectives. MDD remains a diagnostic/tiebreaker only.

0056 is DEVELOPMENT research on researcher-exposed history. It is not independent OOS evidence and creates no production authority.

## 2. Why this new question is admissible

The following upstream evidence is already exposed and immutable:

- `BRRK-WINNER-0001`: winner concentration can have material historical economic value, but the winner is hindsight information and is not a causal router;
- `BRRK-WINNER-ROBUSTNESS-0002`: the winner-concentration economic effect survived the project's frozen 5/10/20 bps cost convention in DEVELOPMENT;
- `BRRK-LEADERSHIP-ROTATION-0048`: predictive leadership measurement was support-inconclusive and is permanently closed;
- `BRRK-LEADERSHIP-INTRADAY-SUPPORT-0053`: four-hour sampling did not solve the calendar-time support constraint under the strict equivalent clock;
- `BRRK-LEADERSHIP-4H-NATIVE-READINESS-0054`: the fixed seven-feature estimator did not establish training precision;
- `BRRK-LEADERSHIP-4H-STRUCTURAL-READINESS-0055`: the fixed 7D-to-3D structural representation also did not establish training precision.

0056 therefore does **not** continue repairing probability calibration, HAC readiness, burn-in selection or feature dimensionality. It asks whether a simple portfolio mechanism can directly produce superior net compounding.

The sole 60-day relative-momentum horizon is not selected from 0054/0055 outcomes. A 60-day SOL/ETH relative-momentum benchmark was already prospectively defined as baseline B3 in 0048. Using only its sign as the router decision boundary therefore does not constitute post-0055 lookback mining.

## 3. Frozen scientific question

> Does one fixed, simple, causal 60-day SOL/ETH relative-trend router improve net terminal wealth and net CAGR versus static ETH/SOL Beta holdings after realistic switching costs, without a probability model, hindsight winner label, BTC allocation or cash-timing layer?

This is a portfolio-control question, not a probability-estimation question.

## 4. Variant budget

Exactly one candidate variant is allowed.

```text
candidate variants                     1
lookback alternatives                  0
threshold alternatives                 0
model-family alternatives              0
parameter sweep                        FORBIDDEN
```

No 20d, 30d, 90d, 120d, EMA, MACD, RSI, CORE4, supervised model, neural model, regime ensemble or alternative threshold may be evaluated under 0056.

## 5. Frozen candidate signal

Let completed UTC daily close prices be `SOL_t` and `ETH_t`.

Define:

`z_t = log(SOL_t / ETH_t)`

and the sole signal:

`RM60_t = z_t - z_{t-60}`.

The target Beta asset is frozen as:

```text
RM60_t > 0     -> target SOL
RM60_t < 0     -> target ETH
RM60_t = 0     -> retain the prior router holding; no switch
```

For the first routable decision only, if `RM60_t = 0` and no prior router holding exists, the deterministic fallback is **ETH**. This fallback exists only to make exact-zero semantics complete and cannot be changed after result exposure.

No signal magnitude, probability, confidence bucket or threshold distance is used. Only the sign of the single frozen signal determines the target asset.

## 6. Causal timing and execution semantics

0056 uses completed UTC **daily** closes only.

At decision origin `t`:

1. observe completed closes through `t`;
2. compute `RM60_t` only from information available through `t`;
3. determine the target holding after close `t`;
4. apply that target only to the next close-to-close held return, `P_{t+1}/P_t - 1`.

No same-close return may be captured. No intraday or 4h information may be introduced.

The exact first and last evaluable origins will be mechanically bound in the numerical preregistration from the immutable daily dataset calendar. All candidate and benchmark arms must use the same evaluation window.

## 7. Portfolio semantics

The 0056 router is a fully invested Beta sleeve:

```text
allowed held assets                    ETH or SOL only
router gross exposure                  1.0
router cash allocation                 0 after initial entry
BTC allocation                         0
shorting                               forbidden
leverage                               forbidden
```

The router holds exactly one of ETH or SOL at 100% weight. It switches only when the frozen sign rule changes the target asset. There is no rebalance band and no discretionary persistence rule beyond the exact-zero retain rule.

0056 does not test BTC anchoring, Beta-to-BTC, BTC-to-cash, CORE4 dynamic gross, integrated routing or any production portfolio.

## 8. Frozen benchmarks

All benchmarks use the same starting NAV, common evaluation window and transaction-cost convention as the candidate.

### B0 — Static ETH

- initial portfolio is cash;
- make one initial 100% ETH entry;
- thereafter buy-and-hold ETH with no rebalancing.

### B1 — Static SOL

- initial portfolio is cash;
- make one initial 100% SOL entry;
- thereafter buy-and-hold SOL with no rebalancing.

### B2 — Static 50/50 ETH/SOL

- initial portfolio is cash;
- make one initial 50% ETH / 50% SOL allocation;
- thereafter buy-and-hold both assets with **no periodic rebalancing**.

No benchmark may receive a timing signal. The pointwise maximum of B0/B1/B2 is not an executable strategy; it is only the conservative comparison envelope for the primary hurdle.

No hindsight winner/oracle benchmark will be recomputed in 0056. Winner 0001 already supplies the exposed oracle-style economic motivation, and a new hindsight diagnostic has no decision authority here.

## 9. Transaction-cost convention

0056 inherits the project's existing executed-L1-turnover cost semantics.

For a trade boundary:

`cost_rate = cost_bps / 10000`

`transaction_cost = pre_trade_NAV * executed_L1_turnover * cost_rate`.

The frozen cost levels are:

```text
primary all-in cost proxy              5 bps per unit L1 turnover
stress level 1                         10 bps per unit L1 turnover
stress level 2                         20 bps per unit L1 turnover
```

For this portfolio family:

- cash -> any fully invested initial portfolio has total L1 turnover = 1;
- a full ETH -> SOL or SOL -> ETH router switch has total L1 turnover = 2;
- static benchmarks incur their initial-entry cost and then no further transaction cost because they are buy-and-hold;
- the static 50/50 benchmark has initial L1 turnover = 1 and no periodic rebalancing.

The later preregistration must freeze exact accounting order and NAV recursion before implementation, but it may not change these cost levels or the L1 charging definition.

## 10. Primary economic endpoints

Primary endpoints are:

1. **net terminal wealth `W_T`**;
2. **net CAGR** over the common evaluation window.

At the primary 5 bps cost level, the candidate must be compared against all three static benchmarks.

The primary economic hurdle is directionally fixed at design time:

`W_router,5bps > max(W_ETH,5bps, W_SOL,5bps, W_50_50,5bps)`.

Because all arms share the same start NAV and evaluation horizon, the same strict ordering must hold for net CAGR.

Merely beating one or two static benchmarks is not sufficient for a PASS classification.

## 11. Secondary diagnostics

Secondary diagnostics may explain the primary result but cannot replace it:

- maximum drawdown;
- total executed L1 turnover;
- router switch count;
- average and median holding duration;
- longest continuous underperformance interval versus the best frozen static comparator;
- fixed calendar-year or prospectively frozen chronological-block attribution;
- 10 bps and 20 bps cost sensitivity;
- dependence-aware paired uncertainty around the candidate-versus-static economic uplift.

No secondary diagnostic may be used post hoc to rescue a failure of the primary wealth hurdle.

## 12. Numerical preregistration boundary

This design freezes the mechanism and comparison family but intentionally does not invent data-informed inferential cutoffs.

The **next allowed stage**, only after this design is merged, is numerical/data preregistration. Before any implementation or 0056 economic result is computed, that preregistration must freeze at least:

- immutable daily dataset identity and payload SHA;
- exact common evaluation start/end origins;
- starting NAV and exact wealth recursion;
- precise cost debit ordering;
- benchmark accounting recursion;
- CAGR annualization convention;
- drawdown convention;
- fixed chronological concentration diagnostic and any hard gate;
- dependence-aware paired block/bootstrap method;
- exact block length;
- bootstrap repetitions and seed;
- exact PASS/FAIL machine classification strings;
- every robustness threshold required for PASS.

No threshold may be chosen after viewing 0056 economic output.

The already registered daily Binance Spot BTC/ETH/SOL slice is the intended reusable source for the preregistration:

```text
dataset id                              BINANCE_SPOT_BTC_ETH_SOL_1D_20200811_20260802
frequency                               1d UTC
common calendar                         2020-08-11 through 2026-08-02
rows                                    2183
payload SHA256                          d1cd28bc76f2cd8ee0486287fc50b49e5451355a3e75132a2de5b30c15af3193
contamination                           RESEARCHER_EXPOSED_HISTORY
independent OOS                         false
```

This design reference does not authorize execution and does not create a new dataset exposure event.

## 13. PASS / FAIL decision logic and stop rule

The exact numerical robustness gates will be frozen in the preregistration, but the research-direction decision is already constrained here.

### PASS eligibility

0056 may be classified as a PASS only if all of the following are true under the later frozen preregistration:

- at 5 bps, the router strictly beats **all three** static benchmarks in net terminal wealth / net CAGR;
- the 10/20 bps stress results satisfy the preregistered cost-survival requirement;
- the uplift satisfies the preregistered chronological concentration requirement rather than being accepted as an obvious single-era artifact;
- dependence-aware paired robustness satisfies its preregistered gate;
- all data-integrity and accounting checks pass.

A PASS creates only eligibility for a **new research ID** studying a fixed BTC anchor plus causal routed Beta, for example an architecture motivated by the previously exposed 40% BTC / 60% winner economic result. It does not authorize that allocation under 0056.

### FAIL / inconclusive consequence

If the frozen 0056 rule fails the preregistered economic decision, the ETH/SOL micro-timing line stops.

Under the same 0056 ID, do **not** open:

- 30d or 90d rescue lookbacks;
- MACD/EMA/RSI alternatives;
- magnitude thresholds;
- volatility filters;
- CORE4 overlays;
- ML/neural alternatives;
- dynamic leverage/gross variants;
- result-informed subperiod exclusions.

The next research budget then moves to a **new-ID Beta-to-BTC continuation-value problem**, potentially using CORE4 as context only if separately designed and preregistered. 0045/0046 may not be rescued.

Any result-informed continuation after 0056, positive or negative, requires a new research ID.

## 14. Explicit exclusions

0056 does not use or evaluate:

- winner labels or 14/28/56-day composite targets;
- probability forecasts;
- prevalence priors;
- ridge/logistic models;
- calibration or temperature scaling;
- AUC, NLL, Brier or balanced accuracy;
- estimator/HAC readiness gates from 0054/0055;
- four-hour data;
- BTC eligibility filters;
- BTC allocation;
- cash timing;
- CORE4 dynamic gross;
- oracle/hindsight exits;
- leverage or shorting;
- canonical BRRK modifications;
- live signing or order submission.

## 15. Development contamination and evidence status

0056 uses researcher-exposed historical data and therefore must remain labeled:

```text
stage                                   DEVELOPMENT
independent OOS                         false
production evidence                     false
```

A historical PASS would establish only that this exact causal router produced superior exposed-history economics under the frozen study. It would not by itself establish future predictive validity or production readiness.

## 16. Governance sequence

The only permitted stage order is:

```text
design freeze
-> design merge
-> numerical/data preregistration
-> prereg merge
-> implementation-only
-> implementation merge
-> controlled execution boundary
-> boundary merge
-> exactly one valid execution
-> immutable closeout
```

Before the controlled execution boundary merges, full-history 0056 economic execution is forbidden.

After durable run-attempt authority is consumed, the same ID may not recompute, retune, rescue, relax thresholds or change targets. Negative results must be preserved.

## 17. Production and canonical isolation

Nothing in 0056 design changes the live/canonical program:

```text
Canonical BRRK-0011                    NO CHANGE
Phase 6                                NO CHANGE
production gross cap                   1.0
production_authorized_components       []
production_authorized                  false
signature_authorized                   false
order_submission_authorized            false
```

0056 is research-only until a later, separately governed production authorization explicitly says otherwise.

## 18. Design-freeze completion criterion

This design stage is complete only when this document is merged to `main` through a formal design PR with no preregistration, implementation, workflow, result or run marker bundled into the same stage.

After that merge, the sole allowed 0056 continuation is the numerical/data preregistration described above.
